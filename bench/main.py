import time
from typing import List
from copy import copy
import json
import platform
import os

from pygraphdb.edge import Edge
from pygraphdb.graph_base import GraphBase
from pygraphdb.plain_sql import PlainSQL
from pygraphdb.mongo_db import MongoDB
from pygraphdb.neo4j import Neo4j
from helpers.shared import *

from benchmarks.tests import FullTest
from benchmarks.benchmark import FullBenchmark
from benchmarks.stats import Stats
from benchmarks.tasks import Tasks


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

if __name__ == "__main__":
    # Preprocessing
    stats = Stats()
    tasks = Tasks()
    tasks.sample_from_file(file_path, sampling_ratio)
    gs = [
        PlainSQL(url='sqlite:///:memory:'),
        PlainSQL(url='sqlite:////Users/av/sqlite/pygraphdb.db'),
        PlainSQL(url='mysql://root:temptemp@0.0.0.0:3306/mysql'),
        PlainSQL(url='postgres://root:temptemp@0.0.0.0:5432'),
        Neo4j(
            url='bolt://0.0.0.0:7687/pygraphdb',
            enterprise_edition=False,
        ),
        MongoDB(
            url='mongodb://0.0.0.0:27017/',
            db_name='pygraphdb',
            collection_name='tests',
        ),
    ]
    # Analysis
    for g in gs:
        try:
            FullTest(graph=g).run()
            FullBenchmark(graph=g, stats=stats, tasks=tasks).run()
        except Exception as e:
            print(f'Failed for {g}: {str(e)}')
    # Postprocessing
    stats.dump_to_file()
