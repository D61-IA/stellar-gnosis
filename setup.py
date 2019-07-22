# -*- coding: utf-8 -*-
#
# Copyright 2018 Data61, CSIRO
#
import setuptools

DESCRIPTION = "Gnosis web application for paper management and collaboration."
URL = "https://github.com/stellargraph/stellar-gnosis"

setuptools.setup(
    name="gnosis",
    version="0.3.1b",
    author="Pantelis Elinas, Data61, CSIRO",
    author_email="pantelis.elinas@data61.csiro.au",
    url=URL,
    long_description=DESCRIPTION,
    long_description_content_type="text/markdown",
    python_requires='>3.5.0, <3.7.0',
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
)
