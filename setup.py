#!/usr/bin/python

import os
from setuptools import setup, find_packages

def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

setup(
    name = "subtitler",
    version = "0.2.1",
    author = "Adam Strauch",
    author_email = "cx@initd.cz",
    description = ("Tool/library for searching subtitles by hash or typed query."),
    license = "BSD",
    keywords = "subtitle subtitles",
    url = "https://github.com/creckx/Subtitler",
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    long_description="Subtitler is a small tool for downloading subtitles from OpenSubtitles.org, contains simple library for theirs XML-RPC API.",#read('README'),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
    install_requires=[
        
        ],
    entry_points="""
    [console_scripts]
    subtitler = subtitler.subtitler:main
    """
)
