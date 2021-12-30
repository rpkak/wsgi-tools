from setuptools import find_packages, setup

from wsgi_tools import __version__

with open('README.md') as f:
    long_description = f.read()

with open('docs-requirements.txt') as f:
    docs_requirements = f.readlines()

setup(
    name='wsgi-tools',
    version=__version__,
    url='http://wsgi-tools.rtfd.io/',
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
    ],
    extras_require={
        'docs': docs_requirements
    }
)
