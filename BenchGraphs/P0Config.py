import os
from typing import Optional
import importlib

from pystats2md.stats_file import StatsFile

from PyWrappedGraph.SQLite import SQLite, SQLiteMem
from PyWrappedGraph.MySQL import MySQL
from PyWrappedGraph.PostgreSQL import PostgreSQL
from PyWrappedGraph.MongoDB import MongoDB
from PyWrappedGraph.Neo4J import Neo4J


count_nodes = int(os.getenv('COUNT_NODES', '0'))
count_edges = int(os.getenv('COUNT_EDGES', '0'))
count_finds = int(os.getenv('COUNT_FINDS', '20000'))
count_analytics = int(os.getenv('COUNT_ANALYTICS', '300'))
count_changes = int(os.getenv('COUNT_CHANGES', '10000'))
device_name = os.getenv('DEVICE_NAME', 'UnknownDevice')

datasets = json.load_from('BenchGraphs/P0ConfigDatasets.json')
wrappers = json.load_from('BenchGraphs/P0ConfigDBs.json')
report_path = 'BenchGraphs/MacbookPro/README.md'
stats_path = 'BenchGraphs/MacbookPro/stats_pygraphdb.json'
stats = StatsFile(stats_path)

dataset_test = {
    "name": "Test",
    "path": "Datasets/graph-test/edges.csv",
    "nodes": 8,
    "edges": 10,
    "size_mb": 1,
}

wrapper_types = [
    SQLite,
    MongoDB,
    PostgreSQL,
    MySQL,
    Neo4J,
]

try:
    # pylint: disable=undefined-variable
    importlib.reload(PyUnumDB)
    from PyUnumDB import GraphDB
    wrapper_types.append(GraphDB)
except NameError:
    try:
        import PyUnumDB
        from PyUnumDB import GraphDB
        wrapper_types.append(GraphDB)
    except:
        pass


def dataset_number_of_edges(dataset_path: str) -> int:
    for d in _datasets:
        if d[0] != dataset_path:
            continue
        return d[2]
    return 0


def dataset_name(dataset_path: str) -> str:
    for d in _datasets:
        if d[0] != dataset_path:
            continue
        return d[3]
    return 0


def wrapper_name(cls: type) -> Optional[str]:
    for w in _wrappers:
        if w[0] != cls:
            continue
        return w[2]
    # If no name was found - generate one.
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
        url = url.replace('${DATASET_NAME}', name)
        return url
    return None
