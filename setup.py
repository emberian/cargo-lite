#!/usr/bin/env python

from distutils.core import setup

setup(name='cargo-lite',
      version='0.1.0',
      description='Rust package manager',
      author='Corey Richardson',
      author_email='corey@octayn.net',
      url='http://github.com/cmr/cargo-lite',
      scripts=['cargo-lite.py'],
      requires=['docopt', 'toml', 'sh'],
      )
