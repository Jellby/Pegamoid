#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import re

with open("README.md", "r") as f:
    # Remove screenshots
    long_description = re.sub('Screenshots\n-*\n*(<.*> *\n*)*', '', f.read())

setup(name='Pegamoid',
      version='2.2.1',
      description='Orbital viewer for OpenMolcas',
      author=u'Ignacio Fdez. Galván',
      author_email='jellby@yahoo.com',
      url='https://gitlab.com/Jellby/Pegamoid',
      license='GPL v3.0',
      scripts=['pegamoid.py'],
      install_requires=['numpy (>=1.9.0)', 'h5py', 'VTK (>=8.1.0)', 'qtpy', 'future (>=0.15.2);python_version<"3.0"' ],
      long_description=long_description,
      long_description_content_type="text/markdown",
      classifiers=[
          'Development Status :: 5 - Production/Stable',
          'Intended Audience :: Science/Research',
          'Environment :: X11 Applications :: Qt',
          'Topic :: Scientific/Engineering :: Chemistry',
          'Topic :: Scientific/Engineering :: Visualization',
          'Topic :: Multimedia :: Graphics :: 3D Rendering',
      ],
     )
