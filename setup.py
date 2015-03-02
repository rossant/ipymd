"""
ipymd
"""
from setuptools import setup

setup(
    name='ipymd',
    version='0.1.0-dev',
    packages=['ipymd',
              'ipymd.formats',
              ],
    entry_points={
        'console_scripts': [
            'ipymd=ipymd.scripts:main',
            ]
        }
    )
