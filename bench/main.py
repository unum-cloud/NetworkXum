import time
from typing import List
from copy import copy
import json
import platform
import os

from pygraphdb.edge import Edge
from pygraphdb.graph_base import GraphBase
from pygraphdb.plain_sql import PlainSQL, SQLite, SQLiteMem, MySQL, PostgreSQL
from pygraphdb.mongo_db import MongoDB
from pygraphdb.neo4j import Neo4j
from pygraphdb.helpers import *

from pystats.file import StatsFile

from full_test import FullTest
from full_bench import FullBench
from tasks_sampler import TasksSampler


print('Welcome to GraphDB benchmarks!')
print('- Reading settings')
sampling_ratio = float(os.getenv('SAMPLING_RATIO', '0.01'))
sample_from_real_data = os.getenv('SAMPLE_FROM_REAL_DATA', '1') == '1'
count_nodes = int(os.getenv('COUNT_NODES', '0'))
count_edges = int(os.getenv('COUNT_EDGES', '0'))
count_finds = int(os.getenv('COUNT_FINDS', '10000'))
count_analytics = int(os.getenv('COUNT_ANALYTICS', '1000'))
count_changes = int(os.getenv('COUNT_CHANGES', '10000'))
file_path = os.getenv('URI_FILE',
                      '/Users/av/Datasets/graph-orkut/orkut.edges')

sqlite_mem_url = os.getenv(
    'URI_SQLITE', 'sqlite:///:memory:')
sqlite_url = os.getenv(
    'URI_SQLITE', 'sqlite:////Users/av/sqlite/orkut/temp.db')
mysql_url = os.getenv(
    'URI_MYSQL', 'mysql://root:temptemp@0.0.0.0:3306/orkut/')
pgsql_url = os.getenv(
    'URI_PGSQL', 'postgres://root:temptemp@0.0.0.0:5432/orkut/')
neo4j_url = os.getenv('URI_NEO4J', 'bolt://0.0.0.0:7687/orkut/')
mongo_url = os.getenv('URI_MONGO', 'mongodb://0.0.0.0:27017/orkut')
hyperrocks_url = os.getenv(
    'URI_HYPER_ROCKS', '/Users/av/rocksdb/orkut/')

dataset_name = os.path.basename(file_path)
report_path = 'artifacts/stats_mew.md'


if __name__ == "__main__":
    # Preprocessing
    stats = StatsFile()
    tasks = TasksSampler()
    print('- Sampling tasks!')
    tasks.sample_from_distribution(2783196)

    # Wrappers selection.
    gs = list()
    if len(hyperrocks_url):
        from embedded_graph_py import HyperRocks
        gs.append(lambda: HyperRocks(hyperrocks_url))
    if len(sqlite_url):
        gs.append(lambda: SQLite(url=sqlite_url))
    # if len(sqlite_mem_url):
    #     gs.append(lambda: SQLiteMem(url=sqlite_mem_url))
    # if len(mysql_url):
    #     gs.append(lambda: MySQL(url=mysql_url))
    # if len(pgsql_url):
    #     gs.append(lambda: PostgreSQL(url=pgsql_url))
    # if len(neo4j_url):
    #     gs.append(lambda: Neo4j(url=neo4j_url))
    # if len(mongo_db):
    #     gs.append(lambda: MongoDB(url=mongo_db))

    # Analysis
    for g_connector in gs:
        print('New adapter!')
        g = g_connector()
        print('Starting tests!')
        FullTest(graph=g).run()
        print('Starting bench!')
        FullBench(
            graph=g,
            stats=stats,
            tasks=tasks,
            dataset_path=file_path,
        ).run(
            repeat_existing=False,
            remove_all_afterwards=False,
        )
        stats.dump_to_file()
    # Postprocessing: Reporting
    # StatsExporter()
