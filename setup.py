#!/usr/bin/env python

from setuptools import setup
from pip.req.req_file import parse_requirements
from pip.download import PipSession

import halutz


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
    install_requires=[
        item.name
        for item in parse_requirements(
            'requirements.txt',
            session=PipSession())],
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
