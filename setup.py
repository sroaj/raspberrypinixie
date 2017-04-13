# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


with open('README.md') as f:
    readme = f.read()

with open('LICENSE') as f:
    license = f.read()

setup(
    name='raspberrypinixie',
    version='1.0.0',
    description='Raspberry Pi Nixie Tube Driver library',
    long_description=readme,
    author='Sroaj Sosothikul',
    url='https://github.com/sroaj/raspberrypinixie',
    license=license,
    packages=find_packages(exclude=('tests', 'docs', 'samples', 'ext'))
)
