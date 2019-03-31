"""Setup configuration."""
import setuptools

with open("README.md", "r") as fh:
    LONG = fh.read()

with open('requirements.txt') as f:
    REQ = f.read().splitlines()

setuptools.setup(
    name="ovoenergy",
    version="0.1.0",
    author="Timmo",
    author_email="contact@timmo.xyz",
    description="",
    long_description=LONG,
    long_description_content_type="text/markdown",
    install_requires=REQ,
    entry_points={
        'console_scripts': [
            'ovoenergy = ovoenergy.cli:cli'
        ]
    },
    url="https://github.com/timmo001/ovoenergy",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    )
)
