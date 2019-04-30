#!/usr/bin/env python
# -*- coding: utf-8 -*-
import io
import re
from setuptools import setup
from collections import OrderedDict

with io.open('README.md', 'rt', encoding='utf8') as f:
    readme = f.read()

with io.open('rtconfig/__init__.py', 'rt', encoding='utf8') as f:
    version = re.search(r'__version__ = \'(.*?)\'', f.read()).group(1)

setup(
    name='rtconfig',
    version=version,
    url='https://github.com/dwdw520533/rtconfig',
    project_urls=OrderedDict((
        ('Code', 'https://github.com/dwdw520533/rtconfig'),
    )),
    license='BSD',
    author='Dongwei',
    description='A simple Python async framework for building web applications. ',
    long_description=readme,
    long_description_content_type="text/markdown",
    packages=[
        'rtconfig',
    ],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    python_requires='>=3.5',
    install_requires=[
        'bson',
        'attrs',
        'blinker',
        'click',
        'uvloop',
        'multidict',
        'itsdangerous',
        'httptools',
        'websockets',
        'gunicorn',
        'aiofiles',
        'jinja2'
    ],
    extras_require={
        'dotenv': ['python-dotenv'],
        'docs': [
            'sphinx',
            'pallets-sphinx-themes',
            'sphinxcontrib-log-cabinet',
        ]
    },
    classifiers=[
        'Development Status :: 1 - Planning',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    entry_points={
        'console_scripts': [
            'rtc = rtconfig.cli:main',
        ],
    },
)
