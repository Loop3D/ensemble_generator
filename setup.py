import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ensemble_generator",
    version="0.0.1",
    author="Mark Lindsay",
    author_email="mark.lindsay@uwa.edu.au",
    description="A package to generate stochastic model suite inputs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Loop3D/ensemble_generator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
