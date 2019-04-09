"""Setup configuration."""
import setuptools

with open("README.md", "r") as fh:
    LONG = fh.read()

setuptools.setup(
    name="ovoenergy",
    version="0.1.2",
    author="Timmo",
    author_email="contact@timmo.xyz",
    description="",
    long_description=LONG,
    long_description_content_type="text/markdown",
    install_requires=[
        'requests==2.21.0'
    ],
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
