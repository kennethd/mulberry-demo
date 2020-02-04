#!/usr/bin/env python
import logging
import os

# distutils does not support "python setup.py develop"
#from distutils.core import setup
from setuptools import setup

import morus
from morus.setuptools.commands import COMMANDS, NoseTestCommand


log = logging.getLogger("setup")
log.setLevel(logging.DEBUG)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
log.addHandler(console_handler)


LIBS_DIR = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


class MulberryDemoNoseTestCommand(NoseTestCommand):
    """meta-setup command for running moruslib & pplansvc tests simultaneously

    Note: this wouldn't be required in non-demo context where moruslib is
    packaged properly
    """
    nose_opts = NoseTestCommand.nose_opts + [
        "--cover-package=morus",
        "--cover-package=pplans",
        "./setup.py",  # for doctests defined here
        "./pplans",
    ] + morus.__spec__.submodule_search_locations
COMMANDS["test"] = MulberryDemoNoseTestCommand


with open("README.md", "r") as fh:
    long_description = fh.read()


# this is just a hack for demo purposes, to avoid setting up & registering pypi server
def local_pkg(pkgname):
    """helper to create dependency link for dependency on local disk

    for demo purposes only; in lieu of having private PyPi or git server

    >>> pkg = "mylib"
    >>> path = local_pkg(pkg)
    >>> path == os.path.sep.join([LIBS_DIR, pkg])
    True
    """
    return os.path.sep.join([LIBS_DIR, pkgname])


dependency_links = [
    local_pkg("moruslib"),
]

setup_requires = [
    "moruslib", # requires dependency_link above
]

install_requires = [
    "Flask",
    "moruslib", # requires dependency_link above
    #"psycopg2",
    #"redis",
    #"simplejson",
    "SQLAlchemy",
    "urllib3",
]

tests_require = [
    "coverage",
    "nose",
    "pep8",
    "pylint",
    "requests",
]

setup(
    name = "pplansvc",
    version = "0.1",
    description = "Mulberry Payment Plans Service",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    packages = ["pplans", "pplans.flask", "pplans.test"],
    license = "Proprietary",
    author = "Kenneth Dombrowski",
    author_email = "kdombrowski@gmail.com",
    setup_requires = setup_requires,
    install_requires = install_requires,
    tests_require = tests_require,
    dependency_links = dependency_links,
    cmdclass = COMMANDS,
    classifiers=[
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.7",
    ],
)

