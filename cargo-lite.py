#!/usr/bin/env python2
# Copyright 2014 The Rust Project Developers. See LICENSE for more details.
"""cargo-lite, a dirt simple Rust package manager

Usage:
  cargo-lite.py install [--git | --hg | --local] <path> [<package>]
  cargo-lite.py build
  cargo-lite.py --version

Options:
  -h --help     Show this screen.
  --git         Fetch source using git (inferred if <package> ends in .git)
  --hg          Fetch source using hg (never inferred)
  --version     Show version.

"""

import sys
import os
import shutil

from docopt import docopt
from sh import git, hg, rustc
import sh
import toml

VERSION = 'cargo-lite.py 0.1.0'


def expand(path):
    return os.path.expandvars(os.path.expanduser(path))


def repodir():
    return expand("~/.rust")


def libdir():
    dr = expand(os.path.join(repodir(), "lib"))
    if not os.path.exists(dr):
        os.makedirs(dr)
    return dr


def from_pkgdir(path):
    path = os.path.join(path, "cargo-lite.conf")
    if not os.path.exists(path):
        raise Exception("no cargo-lite.conf in {}".format(path))
    return toml.loads(open(path).read())


class cd:
    """Context manager for changing the current working directory, creating if necessary"""
    def __init__(self, newPath):
        newPath = os.path.abspath(os.path.expandvars(os.path.expanduser(newPath)))
        self.newPath = newPath
        if not os.path.exists(newPath):
            os.makedirs(newPath)

    def __enter__(self):
        self.savedPath = os.getcwd()
        os.chdir(self.newPath)

    def __exit__(self, etype, value, traceback):
        os.chdir(self.savedPath)


def fetch(args):
    "Fetch a package's source, returning the path to it"

    path = args['<path>']

    local = args['--local']
    use_git = args['--git']
    use_hg = args['--hg']

    if not use_hg and not use_git and not local:
        if path.endswith('.git'):
            use_git = True
        else:
            sys.stderr.write("error: neither --git nor --hg given, and can't infer from package path\n")
            os.exit(1)

    pkg = args['<package>']
    if pkg is None:
        pkg, ext = os.path.splitext(os.path.basename(path))

    dest = os.path.join(expand(repodir()), pkg)
    if os.path.exists(dest):
        print "Already found fetched copy of {}, skipping".format(pkg)
        return dest

    if local:
        shutil.copytree(expand(path), dest)
    elif git:
        git.clone(path, dest)
    elif hg:
        hg.clone(path, dest)
    return dest


def build(args, conf):
    if 'subpackages' in conf:
        s = conf['subpackages']
        sys.stderr.write("TODO: subpackages NYI")
        sys.exit(1)

    if 'build' in conf:
        b = conf['build']
        if 'crate_file' in b:
            crate_root = os.path.abspath(b['crate_file'])
            output = rustc("--crate-file-name", crate_root, _iter=True)
            if output.exit_code != 0:
                sys.stderr.write("--crate-file-name failed, status {}, stderr:\n".format(output.exit_code))
                sys.stderr.write(str(output))
                sys.exit(1)

            names = list(output)

            if all([os.path.exists(os.path.join(libdir(), x)) for x in names if x != ""]):
                print "all artifacts present, not rebuilding (TODO: add way to rebuild)"
                return

            args = b.get('rustc_args', [])
            args.append(crate_root)
            output = rustc(*args)
            status, stdout, stderr = rustc(*args)

            if status != 0:
                sys.stderr.write("building {} with rustc failed with status {}, stderr:\n".format(crate_root, status))
                sys.stderr.write(stderr)
                sys.stderr.write("\nstdout:\n")
                sys.stderr.write(stdout)
                sys.exit(1)
            for fname in filter(lambda x: x != '', names.split('\n')):
                shutil.copy(os.path.join(os.path.dirname(crate_root), fname), libdir())

        elif 'build_cmd' in b:
            out = sh.Command(b["build_cmd"])()
            if not out.startswith("cargo-lite: "):
                raise Exception("malformed output in build_cmd's stdout")
            if out.startswith("cargo-lite: artifacts"):
                for artifact in filter(lambda x: x != "", out.split("\n")[1:]):
                    shutil.copy(artifact, libdir())
            elif out.startswith("carg-lite: crate_file="):
                args = dict(args)
                del args["build"]["build_cmd"]
                args["build"]["crate_root"] = out.replace("cargo-lite: crate_root=", "")
                install(args)
            else:
                sys.stderr.write(str(out))
                sys.stderr.write("unrecognized directive in build_cmd output\n")
                sys.exit(1)
        else:
            raise Exception("unrecognized build information in cargo-lite.conf")
    else:
        raise Exception("no build information in cargo-lite.conf!")


def install(args):
    path = fetch(args)
    conf = from_pkgdir(path)
    for dep in conf.get('deps', []):
        # whee prepend!
        dep.insert(0, 'install')
        install(docopt(__doc__, version=VERSION, argv=dep))

    with cd(path):
        build(args, conf)

if __name__ == '__main__':
    arguments = docopt(__doc__, version=VERSION)
    if arguments['install']:
        install(arguments)
    else:
        sys.stderr.write("non-install commands not yet supported\n")
        sys.exit(1)
