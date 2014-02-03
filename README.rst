=================
cargo-lite v0.1.0
=================

``cargo-lite`` is an interim package manager for Rust that is sloppily
designed and implemented, intended to have something that "just works" until
there is a package manager that works reliably and well. It depends on sh_,
docopt, and toml. This isn't intended to grow into a production-quality
package manager.

What does it do? It fetches dependencies and builds them. Eventually it will
be able to update deps by fetching from hg/git, and also when rustc version
changes. That's it. That's all it does. No fancy configurable package script
(a la rustpkg), no fancy only-rebuild-what-is-necessary, no handling of cyclic
dependencies, etc.

Installation
------------

Install using distutils::

    git clone https://github.com/cmr/cargo-lite.git
    cd cargo-lite
    sudo python setup.py install

That should pull in the dependencies for you. Otherwise, copy
``cargo-lite`` into a directory in your PATH and make sure you have the
deps installed.

Getting Help
------------

You can find me on irc.mozilla.org as ``cmr``. It's probably best to ask for
help in ``#rust-gamedev``, since that's mostly what has spurred me to work on
this project.

=========================
How To Use ``cargo-lite``
=========================

First, you need a ``cargo-lite.conf`` in the top-level directory of your
repository. In it you will list your dependencies. You do this with a nested
list::

    deps = [
        ["--git", "http://github.com/bjz/gl-rs.git"]
    ,   ["--git", "http://github.com/bjz/glfw-rs.git"] # bjz so amaze?
    ]

This specifies two dependencies: gl-rs_ and glfw-rs_. It specifies that they
should be cloned with ``git``. ``cargo-lite install`` will read their
top-level ``cargo-lite.conf``, install all of their dependencies, and then
build them, copying their build artifacts into the package depository
(currently hardcoded as ``~/.rust``). To build your own crate, you need an
additional section in the ``cargo-lite.conf``::

    [build]
    crate_file = "src/main.rs"

This tells ``cargo-lite`` to run ``rustc`` on ``src/main.rs``. It will pass
it the proper ``-L`` to link to its dependencies. You can add an additional
directive to the build section to add flags::

    [build]
    crate_file = "src/main.rs"
    rustc_args = ["-Z", "prefer-dynamic"]

And that's it, for simple crates! You can use ``cargo-lite build`` to build
your crate. It will output the build artifacts in the same place as running
``rustc src/main.rs`` would. For more complex projects, ``cargo-lite``
accepts the following directives::

    subpackages = ["src/foo", "src/examples"]
    [build]
    build_cmd = "./build.sh"

``cargo-lite`` will first recurse into the subpackages, installing those,
and will then run the ``build_cmd`` with the system's shell. The ``build_cmd``
is expected to print one of two things::

    cargo-lite: artifacts
    libfoo-hash.rlib
    libbar-hash.so

    # or

    cargo-lite: crate_root="src/main.rs",rustc_args=[...]

For the first case, the listed artifacts will be copied into the depository.
.. note:: the paths printed should be relative to the *repository root*.
In the second, ``cargo-lite`` will run ``rustc`` on the given crate file
with the given args as if it were from a ``cargo-lite.conf``.

.. _toml: https://github.com/mojombo/toml
.. _gl-rs: https://github.com/bjz/gl-rs
.. _glfw-rs: https://github.com/bjz/glfw-rs
.. _sh: http://amoffat.github.io/sh/index.html


===
FAQ
===

why python?
-----------

Because it's simple and easy to write incorrect software that works (ie, this)

wow this sucks
--------------

Yup! I don't handle versioning, intelligent rebuilding, or anything of that
sort. Pull requests accepted. Its design revolves around "I want to release
this today".

todo
----

- store rustc version lib built with
- configurable repodir + libdir
- per-project repos (like rustpkg's workspaces)
- rebuild deps when they change (generate make files? see https://gist.github.com/csherratt/8627881)

non-goals
---------

- versioning of dependencies
- build system beyond simply running rustc or a single shell command
- rustc integration beyond what is already present (no hooking into libsyntax
  etc)
- rust rewrite, or a rewrite into any other language

