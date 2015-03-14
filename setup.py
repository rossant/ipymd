"""
ipymd
"""
from setuptools import setup

setup(
    name='ipymd',
    version='0.1.0-dev',
    packages=['ipymd',
              'ipymd.core',
              'ipymd.ext',
              'ipymd.formats',
              'ipymd.lib',
              'ipymd.utils',
              ],
    entry_points={
        'console_scripts': [
            'ipymd=ipymd.core.scripts:main',
            ]
        }
    )
