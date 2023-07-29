#!/usr/bin/env python

import io
import os.path
import re

from setuptools import find_packages, setup

HERE = os.path.dirname(__file__)

# Extract version
SOURCE_FILE = os.path.join(HERE, 'barely_json', '__init__.py')
version = None
with io.open(SOURCE_FILE, 'r', encoding='utf-8') as f:
    for line in f:
        s = line.strip()
        m = re.match(r"""__version__\s*=\s*['"](.*)['"]""", line)
        if m:
            version = m.groups()[0]
if not version:
    raise RuntimeError('Could not extract version from "%s".' % SOURCE_FILE)

# Extract requirements
REQUIREMENTS_FILE = os.path.join(HERE, 'requirements.txt')
with io.open(REQUIREMENTS_FILE, 'r', encoding='utf-8') as f:
    requirements = f.readlines()

long_description = """
A lot of data is encoded in a format that is similar to JSON but not quite valid JSON. This module tries to be as forgiving as possible while parsing such data.
""".strip()

setup(
    name='barely_json',
    description='Parse invalid, malformed and barely JSON-esque data',
    long_description=long_description,
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
