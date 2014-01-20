#!/usr/bin/env python2
# Copyright 2014 The Rust Project Developers. See LICENSE for more details.
"""Naval Fate.

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
from plumbum.cmd import git, hg, rustc
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
        print "entering {}".format(newPath)
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
        git["clone", path, dest]()
    elif hg:
        hg["clone", path, dest]()
    return dest


def build(args, conf):
    print "build in {}".format(os.getcwd())
    if 'build' in conf:
        b = conf['build']
        if 'crate_file' in b:
            crate_root = os.path.abspath(b['crate_file'])
            status, names, stderr = rustc.run(args=("--crate-file-name", crate_root))
            if status != 0:
                sys.stdout.write("--crate-file-name failed, status {}, stderr:\n".format(status))
                sys.stdout.write(stderr)
                sys.stdout.write("\nstdout:\n")
                sys.stdout.write(names)
                sys.exit(1)

            if all([os.path.exists(os.path.join(libdir(), x)) for x in names.split('\n') if x != ""]):
                print "wow they're all there!"

            print "crate root is {}".format(crate_root)
            args = b.get('rustc_args', [])
            args.append(crate_root)
            status, stdout, stderr = rustc.run(*args)
            if status != 0:
                sys.stdout.write("building {} with rustc failed with status {}, stderr:\n".format(crate_root, status))
                sys.stdout.write(stderr)
                sys.stdout.write("\nstdout:\n")
                sys.stdout.write(stdout)
                sys.exit(1)
            for fname in filter(lambda x: x != "", names.split('\n')):
                shutil.copy(os.path.join(os.path.dirname(crate_root), fname), libdir())

        elif 'build_cmd' in b:
            sys.stdout.write("arbitrary build commands not yet supported\n")
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
        print dep
        install(docopt(__doc__, version=VERSION, argv=dep))

    with cd(path):
        build(args, conf)

    print conf
    print path


if __name__ == '__main__':
    print sys.argv
    arguments = docopt(__doc__, version=VERSION)
    print arguments
    print
    if arguments['install']:
        install(arguments)
