#!/usr/bin/env python

from setuptools import setup

setup(name='cargo-lite',
      version='1.1.3',
      description='Rust package manager',
      author='Corey Richardson',
      author_email='corey@octayn.net',
      url='http://github.com/cmr/cargo-lite',
      scripts=['cargo-lite'],
      install_requires=['docopt ', 'toml', 'sh', 'pyblake2', 'colorama']
      )
