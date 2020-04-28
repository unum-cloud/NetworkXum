import os
from typing import Optional
import importlib

from pystats2md.stats_file import StatsFile

from pygraphdb.table_sqlite import SQLite, SQLiteMem
from pygraphdb.table_mysql import MySQL
from pygraphdb.table_postgres import PostgreSQL
from pygraphdb.docs_mongo import MongoDB
from pygraphdb.graph_neo4j import Neo4J

try:
    # pylint: disable=undefined-variable
    importlib.reload(unumdb_python)
except NameError:
    import unumdb_python
from unumdb_python import SQLiteCpp
from unumdb_python import RocksMonolith
from unumdb_python import RocksChunked
from unumdb_python import STLOrderedMap
from unumdb_python import STLUnorderedMap
from unumdb_python import TSLHopscotch
from unumdb_python import TSLRobin


count_nodes = int(os.getenv('COUNT_NODES', '0'))
count_edges = int(os.getenv('COUNT_EDGES', '0'))
count_finds = int(os.getenv('COUNT_FINDS', '5000'))
count_analytics = int(os.getenv('COUNT_ANALYTICS', '300'))
count_changes = int(os.getenv('COUNT_CHANGES', '5000'))
device_name = os.getenv('DEVICE_NAME', 'Unknown Device')

report_path = 'bench/stats_macbookpro19/README.md'
stats_path = 'bench/stats_macbookpro19/stats.json'
stats = StatsFile(stats_path)

_datasets = [
    # Path, Number of Nodes, Number of Edges

    # Test graph.
    ('/Users/av/Code/PyGraphDB/datasets/graph-test/all.csv', 8, 10),

    # Average degree: ~8.
    # http://networkrepository.com/fb-pages-company.php
    # ('/Users/av/Datasets/graph-communities/all.csv', 0, 52310),

    # Average degree 90.
    # http://networkrepository.com/rec-eachmovie.php
    # ('/Users/av/Datasets/graph-eachmovie-ratings/all.csv', 0, 2811716),

    # Patent Citation Network. 77 Mb.
    # Average degree: 8.
    # http://networkrepository.com/cit-patent.php
    # ('/Users/av/Datasets/graph-patent-citations/all.csv', 0, 16518947),

    # Mouse gene regulatory network derived
    # from analyzing gene expression profiles. 162 Mb.
    # Third column is the edge weights.
    # Average degree: 670.
    # http://networkrepository.com/bio-mouse-gene.php
    ('/Users/av/Datasets/graph-mouse-gene/all.csv', 0, 14506199),

    # Human Brain Network. 227 Mb.
    # Average degree: 186.
    # http://networkrepository.com/bn-human-Jung2015-M87102575.php
    # ('/Users/av/Datasets/graph-human-brain/all.csv', 0, 87273967),
]
dataset_test = _datasets[0][0]
datasets = [x[0] for x in _datasets[1:]]

wrapper_types = [
    # SQLiteMem,
    # SQLite,
    # MongoDB,
    # MySQL,
    # PostgreSQL,
    RocksChunked,
    # RocksMonolith,
    # SQLiteCpp,
    # Neo4J,
]

_wrappers = [
    # Type, Environment Variable, Default Value
    (RocksChunked, 'URI_UNUMDB_RC', '/Users/av/DBs/unumdb.RocksChunked/<dataset>'),
    (RocksMonolith, 'URI_UNUMDB_RM', '/Users/av/DBs/unumdb.RocksMonolith/<dataset>'),
    (SQLiteCpp, 'URI_UNUMDB_SQLITE', '/Users/av/DBs/unumdb.SQLiteCpp/<dataset>.db3'),

    (SQLiteMem, 'URI_SQLITE_MEM', 'sqlite:///:memory:'),
    (SQLite, 'URI_SQLITE', 'sqlite:////Users/av/DBs/sqlite/<dataset>.db3'),
    (MySQL, 'URI_MYSQL', 'mysql://av:temptemp@0.0.0.0:3306/<dataset>'),
    (PostgreSQL, 'URI_PGSQL', 'postgres://av:temptemp@0.0.0.0:5432/<dataset>'),
    (Neo4J, 'URI_NEO4J', 'bolt://neo4j:temptemp@localhost:7687/<dataset>'),
    # (Neo4J, 'URI_NEO4J', 'bolt://localhost:7687/<dataset>'),
    # To startup:
    # mongod --dbpath=/Users/av/DBs/mongo/ --directoryperdb --wiredTigerCacheSizeGB=2 --wiredTigerDirectoryForIndexes &!
    (MongoDB, 'URI_MONGO', 'mongodb://0.0.0.0:27017/<dataset>'),
]


def dataset_number_of_edges(dataset_path: str) -> int:
    for d in _datasets:
        if d[0] != dataset_path:
            continue
        return d[2]
    return 0


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
