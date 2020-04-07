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
mongo_url = os.getenv('URI_MONGO', 'mongodb://localhost:27017')
file_path = os.getenv('URI_FILE',
                      '/Users/av/Datasets/graph-communities/fb-pages-company.edges')

dataset_name = os.path.basename(file_path)
report_path = 'artifacts/stats_mew.md'
compare_to_ram = True
compare_to_cpp = True

if compare_to_cpp:
    from embedded_graph_py import HyperRocks

if __name__ == "__main__":
    # Preprocessing
    stats = StatsFile()
    tasks = TasksSampler()
    tasks.sample_from_file(file_path, sampling_ratio)
    # Wrappers selection.
    gs = list()
    if compare_to_cpp:
        gs.extend([
            HyperRocks('/Users/av/rocksdb/fb-pages-company/temp.db'),
        ])
    if compare_to_ram:
        gs.extend([
            SQLiteMem(url='sqlite:///:memory:'),
        ])
    gs.extend([
        SQLite(url='sqlite:////Users/av/sqlite/fb-pages-company/temp.db'),
        MySQL(url='mysql://root:temptemp@0.0.0.0:3306/fb-pages-company/'),
        PostgreSQL(url='postgres://root:temptemp@0.0.0.0:5432/fb-pages-company/'),
        Neo4j(url='bolt://0.0.0.0:7687/fb-pages-company/'),
        MongoDB(url='mongodb://0.0.0.0:27017/fb-pages-company'),
    ])
    # Analysis
    for g in gs:
        FullTest(graph=g).run()
        FullBench(
            graph=g,
            stats=stats,
            tasks=tasks,
            dataset=dataset_name,
        ).run(
            repeat_existing=True,
            remove_all_afterwards=False,
        )
        # try:
        # except Exception as e:
        #     print(f'Failed for {g}: {str(e)}')
        stats.dump_to_file()
    # Postprocessing: Reporting
    # StatsExporter()
