cargo-lite
==========

``cargo-lite`` is an interim package manager for Rust that is sloppily
designed and implemented, intended to have something that "just works" until
we get a proper package manager. It depends on plumbum, docopt, and toml. This
isn't intended to grow into a production-quality package manager.

example
=======

Slap a ``cargo-lite.conf`` in your repository! See the help, too. The config
files are toml_. There's an example in this repo. It has some useful comments.
Read it.


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

- some sort of setup.py?
- ``cargo-lite.py build`` (install deps in cwd, build crate file with proper
  -L)
- handle package config files betterly
- store rustc version lib built with
- support repo containing multiple packages
- document what the hell this thing expects
- configurable repodir + libdir
- per-project repos.

non-goals
---------

- versioning
- build system
- rustc integration
- rust rewrite

.. _toml: https://github.com/mojombo/toml
