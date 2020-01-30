#!/usr/bin/env python

# distutils does not support "python setup.py develop"
#from distutils.core import setup
from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()


install_requires = [
    "argparse",
    "psycopg2",
]

tests_require = [
    "coverage",
    "nose",
    "pep8",
    "pylint",
]

setup(
    name = "moruslib",
    version = "0.1",
    description = "Mulberry Demo Library Functions",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    packages = [
        "morus",
        "morus.aws",
        "morus.flask",
        "morus.setuptools",
        "morus.test",
    ],
    license = "PRIVATE",
    setup_requires = ["nose>=1.0", "pip>=1.7.2"],
    test_suite = "nose.collector",
    install_requires = install_requires,
    tests_require = tests_require,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
)

