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
    packages=find_packages(exclude=('tests', 'docs', 'samples', 'ext')),
    classifiers=(
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.2',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ),
)
