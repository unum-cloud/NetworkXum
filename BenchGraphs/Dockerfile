FROM continuumio/miniconda3:latest

# Flexible document stores:
RUN conda install -c anaconda pymongo

# SQL abstraction layers for Postgres, MySQL and SQLite:
RUN conda install -c conda-forge sqlalchemy
RUN conda install -c conda-forge psycopg2 
RUN conda install -c conda-forge mysqlclient 

# SQLite bindings are already in the standard library:
# https://docs.python.org/2/library/sqlite3.html
RUN conda install -c conda-forge sqlite

# Actual graph databases.
RUN conda install -c conda-forge py2neo 
RUN conda install -c moustik pyarango

COPY . /graphdb
WORKDIR /graphdb

CMD python3 main.py
