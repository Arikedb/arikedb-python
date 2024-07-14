#!/usr/bin/python3
from setuptools import find_packages, setup

with open('arikedb/__init__.py', 'r') as f:
    version = list(
        filter(lambda line: "__version__ =" in line, f.readlines())
    )[0].split("\"")[1]

setup(
    name="arikedb",
    version=version,
    description="Arikedb Python Client Library",
    long_description="Welcome to the ArikeDB Rust library! "
                     "This library provides an interface to interact "
                     "with the Arike Database, an advanced real-time "
                     "database solution. This documentation "
                     "will guide you through the process of setting "
                     "up and using the library effectively.",
    long_description_content_type="text/markdown",
    author="Alejandro Alfonso",
    author_email="alejandroalfonso1994@gmail.com",
    license="MIT",
    url="https://github.com/alejandroalfonsoyero/arikedb-python",
    packages=find_packages(exclude=['tests', 'demo']),
    include_package_data=True,
    install_requires=[r.strip() for r in open("requirements.txt").readlines()]
)
