=================
cargo-lite v0.3.0
=================

``cargo-lite`` is an interim package manager for Rust that is sloppily
designed and implemented, intended to have something that "just works" until
there is a package manager that works reliably and well. This isn't intended
to grow into a production-quality package manager.

What does it do? It fetches dependencies and builds them. It can fetch from
git, hg, or local directories. It doesn't do any handling of versions etc. It
will rebuild when dependencies change, as well as when rustc's version
changes.

Installation
------------

Install using distutils::

    git clone https://github.com/cmr/cargo-lite.git
    cd cargo-lite
    sudo python setup.py install

Getting Help
------------

You can find me on ``irc.mozilla.org`` as ``cmr``. Look for me
``#rust-gamedev``.

=========================
How To Use ``cargo-lite``
=========================

First, you need a ``cargo-lite.conf`` in the top-level directory of your
repository. In it you will list your dependencies. You do this with a nested
list::

    deps = [
        ["--git", "http://github.com/bjz/gl-rs.git"]
    ,   ["--git", "http://github.com/bjz/glfw-rs.git"]
    ]

This specifies two dependencies: gl-rs_ and glfw-rs_. It specifies that they
should be cloned with ``git``. ``cargo-lite install`` will read their
top-level ``cargo-lite.conf``, install all of their dependencies, and then
build them, copying their build artifacts into the package depository
(currently hardcoded as ``~/.rust``). To build your own crate, you need an
additional section in the ``cargo-lite.conf``::

    [build]
    crate_root = "src/main.rs"

This tells ``cargo-lite`` to run ``rustc`` on ``src/main.rs``. It will pass
it the proper ``-L`` to link to its dependencies. You can add an additional
directive to the build section to add flags::

    [build]
    crate_root = "src/main.rs"
    rustc_args = ["-C", "prefer-dynamic"]

And that's it, for simple crates! You can use ``cargo-lite build`` to build
your crate. It will output the build artifacts in the same place as running
``rustc src/main.rs`` would. For building a library, you need to do::

    [build]
    crate_root = "src/lib.rs"
    crate_type = "library"

For more complex projects, ``cargo-lite`` accepts the following directives::

    subpackages = ["src/foo", "src/examples"]
    [build]
    build_cmd = "./build.sh"

``cargo-lite.py`` will first recurse into the subpackages, installing those,
and will then run the ``build_cmd`` with the system's shell. Two environment
variables will be added, which the ``build_cmd`` is expected to respect:
``CARGO_OUT_DIR``, which is where artifacts that to be installed must be
copied to, and ``CARGO_RUSTFLAGS``, which should be passed to rustc for all
artifacts that are copied into ``CARGO_OUT_DIR``. The ``CARGO_RUSTFLAGS`` will
include things like ``-L /path/where/cargo-lite/libs/are/stored`` and
optimization options.

.. _toml: https://github.com/mojombo/toml
.. _gl-rs: https://github.com/bjz/gl-rs
.. _glfw-rs: https://github.com/bjz/glfw-rs
.. _sh: http://amoffat.github.io/sh/index.html

===========================
``cargo-lite.conf`` details
===========================

Top-level attributes
--------------------

``subpackages``
    A list of directories, relative to the directory this ``cargo-lite.conf``
    is in, to recurse into and install. Note that subpackages installed
    *unconditionally*, and cannot fetch their source from a remote source.
    They provide a way to structure a single repository that has multiple
    crates in it. Subpackages are processed in order, and before any build
    instructions in ``build`` are executed.

``build`` section
------------------

The ``build`` section describes how to build a package. If there are defined
subpackages, this is optional. Otherwise, it is required. It has the following
sub-attributes:

``crate_root``
    A string. If specified, ``rustc`` will be invoked on this file, using the
    correct arguments (given the ``crate_type`` and ``rustc_args``).
``crate_type``
    A string. Either "binary" or "library". Specifies whether the crate is to
    be built as a library or executable binary. Optional, the default is
    "binary".
``rustc_args``
    A list of strings. If specified, these arguments will be passed on to
    ``rustc`` when ``crate_root`` is specified, or joined with a single space
    and exported in the ``CARGO_RUSTFLAGS`` environment variable if
    ``build_cmd`` is specified.
``hash_files``
    A list of strings. If specified, any files matching any of these globs
    will be hashed as part of determining whether a package should be rebuilt
    or not. By default, only ``*.rs`` is considered. Do note that this is, by
    nature, a quadratic algorithm. Take care not to specify many globs, and
    specifying the most common globs first. Since, on every build, every
    file in every dependency is hashed,

    Only ``mtime`` is hashed, to try and keep time down. Due to the crate
    model, fine-grained dependency tracking isn't particularly useful.

At least one of ``crate_root`` and ``build_cmd`` must be specified. If both
are specified, the ``build_cmd`` is run first, allowing for custom code
generation. If neither is specified, processing will halt, and an error will
be printed.

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
- rebuild deps when they change (generate make files? see https://gist.github.com/csherratt/8627881)

non-goals
---------

- versioning of dependencies
- build system beyond simply running rustc or a single shell command
- rustc integration beyond what is already present (no hooking into libsyntax
  etc)
- rust rewrite, or a rewrite into any other language

