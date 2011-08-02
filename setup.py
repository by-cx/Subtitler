#!/usr/bin/python

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "subtitler",
    version = "0.1",
    author = "Adam Strauch",
    author_email = "cx@initd.cz",
    description = ("Tool for searching subtitles by hash or typed query."),
    license = "BSD",
    keywords = "subtitle",
    url = "",
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    long_description=read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=[
        'argparse'
        ],
    entry_points="""
    [console_scripts]
    subtitler = subtitler.subtitler:main
    """
)