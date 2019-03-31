"""Setup configuration."""
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

with open('requirements.txt') as f:
    install_requires = f.read().splitlines()

setuptools.setup(
    name="ovoenergy",
    version="0.1.0",
    author="Timmo",
    author_email="contact@timmo.xyz",
    description="",
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=install_requires,
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
