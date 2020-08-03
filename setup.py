import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name="finnews",
    version="0.1.1",
    author="Shrivu Shankar",
    author_email="shrivu1122@gmail.com",
    description="A suite of market/financial news webscrapers.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sshh12/Financial-News-Indexing",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
