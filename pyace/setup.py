import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyace", # Replace with your own username
    version="0.0.1",
    author="Jasper Landa",
    author_email="jasper.landa@virtualsciences.nl",
    description="IBM ACE test utility package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://repo.virtualsciences.nl/jlanda/eindopdracht-2020",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)