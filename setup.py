#!/usr/bin/env python
from setuptools import setup
from setuptools.command.test import test as TestCommand

from morus.setuptools.commands import NoseTestCommand


class MulberryDemoNoseTestCommand(NoseTestCommand):
    """meta-setup command for running moruslib & pplansvc tests simultaneously

    this wouldn't be required in non-demo context where moruslib is packaged"""
    nose_opts = NoseTestCommand.nose_opts + [
        "--cover-package=morus",
        "--cover-package=pplans",
        "./moruslib/",
        "./pplansvc/"
    ]


COMMANDS = {
    "test": MulberryDemoNoseTestCommand,
}


with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name = "mulberry-demo",
    version = "0.1",
    description = "Mulberry Demo Meta Package",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    cmdclass = COMMANDS,
)

