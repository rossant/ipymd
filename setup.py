#!/usr/bin/env python

from setuptools import setup, find_packages


__version__ = '0.1.0-dev'

classes = """
    Development Status :: 3 - ALpha
    License :: OSI Approved :: BSD License
    Environment :: Console
    Framework :: IPython
    Intended Audience :: Developers
    Natural Language :: English
    Operating System :: Unix
    Operating System :: POSIX
    Operating System :: MacOS :: MacOS X
    Programming Language :: Python
    Programming Language :: Python :: 2
    Programming Language :: Python :: 2.7
    Programming Language :: Python :: 3
    Programming Language :: Python :: 3.3
    Programming Language :: Python :: 3.4
    Topic :: Software Development :: Libraries
    Topic :: Text Processing :: Markup

"""
classifiers = [s.strip() for s in classes.split('\n') if s]

description = ('Use the IPython notebook as an interactive Markdown editor')

with open('README.md') as f:
    long_description = f.read()

setup(name='ipymd',
      version=__version__,
      license='BSD',
      description=description,
      long_description=long_description,
      author='Cyrille Rossant',
      author_email='',
      maintainer='Cyrille Rossant',
      maintainer_email='',
      url='https://github.com/rossant/ipymd',
      classifiers=classifiers,
      packages=find_packages(),
      entry_points={'console_scripts': ['ipymd=ipymd.core.scripts:main']},
      install_requires=['ipython[notebook] >= 3.0'],
      extras_require={'test': ['pytest', 'flake8', 'coverage', 'pytest-cov']})
