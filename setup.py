#!/usr/bin/env python

from setuptools import setup

import halutz


def requirements(filepath):
    return [line.strip() for line in open(filepath).readlines()]


setup(
    name='halutz',
    packages=['halutz'],
    version=halutz.__version__,
    description=("Halutz is a python library for Swagger, "
                 "inspired by working with network engineers getting started with Python."),
    # TODO long_description=read('README.rst'),
    author='Jeremy Schulman',
    author_email='nwkautomaniac@gmail.com',
    url='https://github.com/jeremyschulman/halutz',
    include_package_data=True,
    license='MIT',
    zip_safe=False,
    install_requires=requirements('requirements.txt'),
    keywords=('serialization', 'rest', 'json', 'api', 'marshal',
              'marshalling', 'deserialization', 'validation', 'schema',
              'jsonschema', 'swagger', 'openapi', 'networking', 'automation'),
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.6'
    ]
)
