import os
from typing import Optional

from pystats.file import StatsFile
from pygraphdb.plain_sql import SQLite, SQLiteMem, MySQL, PostgreSQL
from pygraphdb.mongo_db import MongoDB
from pygraphdb.neo4j import Neo4j
from embedded_graph_py import HyperRocks


count_nodes = int(os.getenv('COUNT_NODES', '0'))
count_edges = int(os.getenv('COUNT_EDGES', '0'))
count_finds = int(os.getenv('COUNT_FINDS', '10000'))
count_analytics = int(os.getenv('COUNT_ANALYTICS', '1000'))
count_changes = int(os.getenv('COUNT_CHANGES', '10000'))
device_name = os.getenv('DEVICE_NAME', 'Unknown Device')

report_path = 'artifacts/stats.md'
stats_path = 'artifacts/stats.json'
stats = StatsFile(stats_path)

dataset_test = '/Users/av/Code/PyGraphDB/artifacts/graph-test/all.csv'
datasets = [
    '/Users/av/Datasets/graph-communities/all.csv',
    '/Users/av/Datasets/graph-patent-citations/all.csv',
    # '/Users/av/Datasets/graph-mouse-gene/all.csv',
    # '/Users/av/Datasets/graph-human-brain/all.csv',
]

wrapper_types = [SQLiteMem, SQLite,
                 MySQL, PostgreSQL, Neo4j, MongoDB, HyperRocks]
_wrappers = [
    (HyperRocks, 'URI_HYPER_ROCKS', '/Users/av/rocksdb/<dataset>/'),
    (SQLiteMem, 'URI_SQLITE', 'sqlite:///:memory:'),
    (SQLite, 'URI_SQLITE', 'sqlite:////Users/av/sqlite/<dataset>/graph.db'),
    (MySQL, 'URI_MYSQL', 'mysql://root:temptemp@0.0.0.0:3306/<dataset>/'),
    (PostgreSQL, 'URI_PGSQL', 'postgres://root:temptemp@0.0.0.0:5432/<dataset>/'),
    (Neo4j, 'URI_NEO4J', 'bolt://0.0.0.0:7687/<dataset>'),
    (MongoDB, 'URI_MONGO', 'mongodb://0.0.0.0:27017/<dataset>'),
]


def dataset_name(dataset_path: str) -> str:
    parts = dataset_path.split('/')
    if len(parts) > 1:
        return parts[-2]
    return dataset_path


def wrapper_name(cls: type) -> str:
    if isinstance(cls, type):
        return cls.__name__
    else:
        return cls.__class__.__name__


def database_url(cls: type, dataset_path: str) -> Optional[str]:
    name = dataset_name(dataset_path)
    for w in _wrappers:
        if w[0] != cls:
            continue
        url = os.getenv(w[1], w[2])
        url = url.replace('<dataset>', name)
        return url
    return None
