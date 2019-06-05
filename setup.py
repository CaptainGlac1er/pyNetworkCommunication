import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="py-network-communication",
    version="0.1.0.dev1",
    author="GlacierByte",
    description="Socket Message Communicator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CaptainGlac1er/pyNetworkCommunication",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Topic :: System :: Operating System",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
    ],
)
