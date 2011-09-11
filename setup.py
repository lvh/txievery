#!/usr/bin/env python
from setuptools import find_packages, setup

setup(name='txievery',
      version='0',
      description='Library for dealing with Paypal using Twisted',
      url='https://github.com/lvh/txievery',

      author='Laurens Van Houtven',
      author_email='_@lvh.cc',

      packages=find_packages(),

      install_requires=['twisted'],

      license='ISC',
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Framework :: Twisted",
        "License :: OSI Approved :: ISC License (ISCL)",
        ])
