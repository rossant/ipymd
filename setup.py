"""
ipymd
"""
from setuptools import setup

setup(
    name='ipymd',
    version='0.0.1.dev',
    packages=['ipymd'],
    entry_points={
        'console_scripts': [
            'ipymd=ipymd.scripts:main',
            ]
        }
    )
