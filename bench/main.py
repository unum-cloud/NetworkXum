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


from 1_test import FullTest
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
device_name = os.getenv('DEVICE_NAME', 'Unknown Device')
report_path = 'artifacts/stats_mew.md'

datasets = [
    '/Users/av/Code/PyGraphDB/artifacts/graph-test/all.edges'
    '/Users/av/Datasets/graph-communities/all.edges',
    '/Users/av/Datasets/graph-patent-citations/all.edges',
    '/Users/av/Datasets/graph-mouse-gene/all.edges',
    '/Users/av/Datasets/graph-human-brain/all.edges',
]
test_dataset = datasets[0]

wrappers = [
    (HyperRocks, 'URI_HYPER_ROCKS', '/Users/av/rocksdb/<dataset>/'),
    (SQLiteMem, 'URI_SQLITE', 'sqlite:///:memory:'),
    (SQLite, 'URI_SQLITE', 'sqlite:////Users/av/sqlite/<dataset>/graph.db'),
    (MySQL, 'URI_MYSQL', 'mysql://root:temptemp@0.0.0.0:3306/<dataset>/'),
    (PostgreSQL, 'URI_PGSQL', 'postgres://root:temptemp@0.0.0.0:5432/<dataset>/'),
    (Neo4j, 'URI_NEO4J', 'bolt://0.0.0.0:7687/<dataset>'),
    (MongoDB, 'URI_MONGO', 'mongodb://0.0.0.0:27017/<dataset>'),
]

if __name__ == "__main__":
    # Preprocessing
    stats = StatsFile()

    for dataset in datasets:
        dataset_name = split(dataset, '/')[-2]
        print('- Sampling tasks!')
        tasks = TasksSampler()
        tasks.sample_from_real_data(dataset)

        for wrapper in wrappers:
            wrapper_class = wrapper[0]
            wrapper_url: str = os.getenv(wrapper[1], wrapper[2])
            if '<dataset>' in wrapper_url:
                wrapper_url.replace('<dataset>', dataset_name)

            print(f'- Establising connection: {wrapper_url}')
            g = wrapper_class(url=wrapper_url)

            if dataset == test_dataset:
                print(f'- Running tests')
                FullTest(graph=g).run()

            if g.count_edges() == 0:
                print(f'- Importing data')
                BulkImport(
                    graph=g,
                    dataset_path=dataset,
                    stats=stats
                ).run()

            print(f'- Simple benchmarks')
            FullBenchmark(
                graph=g,
                stats=stats,
                tasks=tasks,
            ).run(repeat_existing=False)

            print(f'- NetworkX benchmarks')
            NetworkxBenchmark(
                graph=g,
                stats=stats,
                tasks=tasks,
            ).run(repeat_existing=False)

            stats.dump_to_file()

    # Postprocessing.
    StatsExporter().run()
