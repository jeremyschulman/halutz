#!/usr/bin/env python
# -*- coding: utf-8 -*-
import re

from setuptools import setup, find_packages
import halutz


def read(fname):
    with open(fname) as fp:
        content = fp.read()
    return content

setup(
    name='halutz',
    version=halutz.__version__,
    description=('Python client for Swagger/OpenAPI'),
    # long_description=read('README.rst'),
    author='Jeremy Schulman',
    author_email='nwkautomaniac@gmail.com',
    url='https://github.com/jeremyschulman/halutz',
    packages=['halutz'],
    include_package_data=True,
    license='MIT',
    zip_safe=False,
    install_requires=[
        'requests',
        'six',
        'first',
        'inflection',
        'bravado',
        'python_jsonschema_objects'
    ],
    # keywords=('serialization', 'rest', 'json', 'api', 'marshal',
    #           'marshalling', 'deserialization', 'validation', 'schema',
    #           'marshmallow'),
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        # 'Programming Language :: Python :: 3',
        # 'Programming Language :: Python :: 3.3',
        # 'Programming Language :: Python :: 3.4',
        # 'Programming Language :: Python :: 3.5',
        # 'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
    ]
)
