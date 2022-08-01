#!/usr/bin/env python
# -*- coding:utf-8 -*-

from setuptools import setup, find_packages

if __name__ == "__main__":
    setup(
        name="j2generator",
        version="0.0.1",
        author="stfujnkk",
        description="A general file generator using jinja2 syntax",
        license="MIT",
        packages=find_packages(),
        install_requires=[
            'Jinja2>=3.0.0',
            'setuptools>=16.0.0'
        ],
    )
