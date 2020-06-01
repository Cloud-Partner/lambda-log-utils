from setuptools import find_packages, setup

setup(
    name="lambda-log-utils",
    version="0.1",
    install_requires=[
        "aws-lambda-powertools==0.8.1"
    ],
    extras_require={
        "develop": [
            "pytest",
            "pytest-mock"
        ]
    },
    packages=find_packages(exclude=['tests*'])
)
