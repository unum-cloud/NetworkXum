
import setuptools
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

__version__ = '0.3.0'

setup(
    name='PyWrappedDBs',
    version=__version__,
    author='Ashot Vardanian',
    author_email='ashvardanian@gmail.com',
    url='https://github.com/ashvardanian/PyWrappedDBs',
    description='''
    A set of database wrappers with OOP-like interfaces.
    Graph structures are backed by SQLite, MySQL, PostgreSQL, MongoDB and Neo4J and compatiable with NetworkX. 
    Document collections are backed by SQLite, MySQL, PostgreSQL, MongoDB and Lucene.
    ''',
    long_description=long_description,
    packages=['PyWrappedGraph', 'PyWrappedTexts', 'PyWrappedHelpers'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
