from setuptools import setup, find_packages

with open("README.md") as f:
    long_description = f.read()

setup(
    name="reference_implementation",
    version="0.0.1",
    description="Decentralized Privacy Preserving Proximity Tracing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/DP-3T/reference_implementation",
    author="Mathias Payer",
    author_email="mathias.payer@nebelwelt.net",
    py_modules=["LowCostDP3T"],
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
    ],
    keywords="DP3T",
    python_requires=">=3",
    install_requires=["pycryptodomex"],
)
