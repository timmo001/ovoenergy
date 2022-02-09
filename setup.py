"""Setup configuration."""
import setuptools

with open("README.md", "r") as fh:
    LONG = fh.read()

setuptools.setup(
    name="ovoenergy",
    version="1.2.0",
    author="Timmo",
    author_email="contact@timmo.xyz",
    description="Get energy data from OVO's API",
    license="MIT",
    long_description=LONG,
    long_description_content_type="text/markdown",
    install_requires=["aiohttp>=3.7.3", "click>=7.1.2"],
    entry_points={"console_scripts": ["ovoenergy = ovoenergy.cli:cli"]},
    url="https://github.com/timmo001/ovoenergy",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
