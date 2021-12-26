import os

from setuptools import find_packages, setup

with open('README.md') as f:
    long_description = f.read()

setup(
    name='wsgi-tools',
    version='0.4.0',
    url='https://github.com/rpkak/wsgi-tools',
    license='Apache 2.0',
    author='rpkak',
    description='A collection of WSGI packages.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    packages=find_packages(),
    classifiers=[
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet'
    ]
)
