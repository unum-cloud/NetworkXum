
import setuptools
from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

__version__ = '0.1.0'

setup(
    name='pygraphdb',
    version=__version__,
    author='Ashot Vardanian',
    author_email='ashvardanian@gmail.com',
    url='https://github.com/ashvardanian/PyGraphDB',
    description='''
    A generic persistent Graph structure compatiable with NetworkX. 
    It can store big graphs in SQLite, MySQL, Postgres, MongoDB or Neo4j database.
    ''',
    long_description=long_description,
    packages=['pygraphdb', 'pystats'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
