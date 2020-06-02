from setuptools import find_packages, setup

setup(
    name="lambda_utils",
    version="0.1",
    install_requires=[
        "aws-lambda-powertools==0.8.1"
    ],
    packages=find_packages(exclude=['tests*'])
)
