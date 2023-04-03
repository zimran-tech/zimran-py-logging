from os import environ

from setuptools import find_namespace_packages, setup

with open('README.md', 'r', encoding='utf-8') as file:
    long_description = file.read()

setup(
    name='zimran-logging',
    version=environ['GITHUB_REF_NAME'],
    description='Loguru, Sentry based logging for backend services',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_namespace_packages(include=['zimran.*']),
    install_requires=['loguru', 'sentry-sdk[fastapi]'],
    python_requires='>=3.10',
    zip_file=False,
)
