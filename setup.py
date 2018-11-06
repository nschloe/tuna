# -*- coding: utf-8 -*-
#
import codecs
import os

from setuptools import setup, find_packages

# https://packaging.python.org/single_source_version/
base_dir = os.path.abspath(os.path.dirname(__file__))
about = {}
with open(os.path.join(base_dir, "tuna", "__about__.py"), "rb") as f:
    exec(f.read(), about)


def read(fname):
    with codecs.open(os.path.join(base_dir, fname), encoding="utf-8") as f:
        return f.read()


setup(
    name="tuna",
    version=about["__version__"],
    author=about["__author__"],
    author_email=about["__author_email__"],
    packages=find_packages(),
    description="Visualize Python profiles in the browser",
    long_description=read("README.md"),
    long_description_content_type="text/markdown",
    url="https://github.com/nschloe/tuna",
    license=about["__license__"],
    platforms="any",
    install_requires=["pipdate >=0.3.0, <0.4.0"],
    classifiers=[
        about["__status__"],
        about["__license__"],
        "Intended Audience :: Developers",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: User Interfaces",
    ],
    entry_points={"console_scripts": ["tuna = tuna.cli:main"]},
    package_data={
        "tuna": [
            "web/*.html",
            "web/static/*.js",
            "web/static/*.css",
            "web/static/favicon256.png",
        ]
    },
)
