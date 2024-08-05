#!/usr/bin/env python

from distutils.core import setup

setup(
    name="GitHubRepositoryManipulation",
    version="1.0",
    description="Utilities to manipulate a set of GitHub repositories",
    author="IBEX group",
    author_email="",
    url="",
    scripts=["scripts/change_repos.py"],
    install_requires=["github3.py", "pytz"],
    packages=["repository_manipulator"],
)
