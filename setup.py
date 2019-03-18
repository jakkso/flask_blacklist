"""Project setup."""

from setuptools import find_packages, setup

with open("README.md") as file:
    long_description = file.read()

setup(
    name="flask_blacklist",
    version="0.0.1",
    packages=find_packages(),
    url="https://github.com/jakkso/flask_blacklist",
    license="MIT License",
    author="Alexander Potts",
    author_email="alexander@jakkso.com",
    description="Token blacklist flask extension",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Framework :: Flask",
    ],
)
