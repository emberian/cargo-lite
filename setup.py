#!/usr/bin/env python

import platform
from setuptools import setup

sh = 'sh'

if platform.system() == 'Windows':
    sh = 'pbs'

setup(name='cargo-lite',
      version='1.1.5',
      description='Rust package manager',
      author='Corey Richardson',
      author_email='corey@octayn.net',
      url='http://github.com/cmr/cargo-lite',
      scripts=['cargo-lite'],
      install_requires=['docopt ', 'toml', sh, 'pyblake2', 'colorama']
      )
