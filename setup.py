#!/usr/bin/env python

import os.path
import re

from setuptools import find_packages, setup

HERE = os.path.dirname(__file__)

# Extract version
SOURCE_FILE = os.path.join(HERE, 'barely_json', '__init__.py')
version = None
with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
    for line in f:
        s = line.strip()
        m = re.match(r"""__version__\s*=\s*['"](.*)['"]""", line)
        if m:
            version = m.groups()[0]
if not version:
    raise RuntimeError('Could not extract version from "%s".' % SOURCE_FILE)

# Extract requirements
REQUIREMENTS_FILE = os.path.join(HERE, 'requirements.txt')
with open(REQUIREMENTS_FILE, 'r') as f:
    requirements = f.readlines()

README_FILE = os.path.join(HERE, 'README.md')
with open(README_FILE, 'r') as f:
    long_description =f.read()

setup(
    name='barely_json',
    description='Parse invalid, malformed and barely JSON-esque data',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/torfsen/barely_json',
    version=version,
    license='MIT',
    keywords=['json'],
    classifiers=[
        # Reference: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],

    author='Florian Brucker',
    author_email='mail@florianbrucker.de',

    packages=find_packages(),
    install_requires=requirements,
)
