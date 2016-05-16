#! /usr/bin/env python

#from ez_setup import use_setuptools
#use_setuptools()

from setuptools import setup, find_packages, Extension
from setuptools.command.install import install
from setuptools.command.develop import develop

from distutils.extension import Extension

import sys

ext_modules = [
    Extension('landlab.components.flexure.cfuncs',
              ['landlab/components/flexure/cfuncs.pyx']),
    Extension('landlab.components.flow_routing.cfuncs',
              ['landlab/components/flow_routing/cfuncs.pyx']),
    Extension('landlab.components.stream_power.cfuncs',
              ['landlab/components/stream_power/cfuncs.pyx']),
    Extension('landlab.grid.structured_quad.cfuncs',
              ['landlab/grid/structured_quad/cfuncs.pyx']),
    Extension('landlab.grid.structured_quad.c_faces',
              ['landlab/grid/structured_quad/c_faces.pyx']),
]

import numpy as np

# from landlab import __version__
__version__ = '1.0.0beta'


import os

#cython_pathspec = os.path.join('landlab', 'components','**','*.pyx')
#ext_modules = cythonize(cython_pathspec)


setup(name='landlab',
      version=__version__,
      author='Eric Hutton',
      author_email='eric.hutton@colorado.edu',
      url='https://github.com/landlab',
      description='Plugin-based component modeling tool.',
      long_description=open('README.rst').read(),
      install_requires=['scipy>=0.12',
                        'nose>=1.3',
                        'matplotlib',
                        'six',
                        'pyyaml',
                       ],
      #                  'Cython>=0.22'],
      setup_requires=['cython'],
      classifiers=[
          'Intended Audience :: Science/Research',
          'License :: OSI Approved :: MIT License',
          'Operating System :: OS Independent',
          'Programming Language :: Cython',
          'Programming Language :: Python :: 2.6',
          'Programming Language :: Python :: 2.7',
          'Programming Language :: Python :: Implementation :: CPython',
          'Topic :: Scientific/Engineering :: Physics'
      ],
      packages=find_packages(),
      package_data={'': ['tests/*txt', 'data/*asc', 'data/*nc',
                         'preciptest.in']},
      test_suite='nose.collector',
      entry_points={
          'console_scripts': [
              'landlab=landlab.cmd.landlab:main',
          ]
      },
      include_dirs = [np.get_include()],
      ext_modules = ext_modules,
     )
