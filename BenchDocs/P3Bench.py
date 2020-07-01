import os
from time import time

from pystats2md.stats_file import StatsFile
from pystats2md.micro_bench import MicroBench

from PyWrappedGraph.BaseAPI import BaseAPI

from P0Config import P0Config
from P3TasksSampler import P3TasksSampler


class P3Bench(object):
    """
        Benchmarks groups of operations in following order:
        2. Edge lookups and simple queries.
        3. A few complex analytical queries.
        4. Modifications: removing and restoring same objects.
        5. Clearing all the data (if needed).
    """

    def __init__(self, max_seconds_per_query=60):
        self.conf = P0Config.shared()
        self.max_seconds_per_query = max_seconds_per_query
        self.tasks = P3TasksSampler()

    def run(self, repeat_existing=True):
        self.repeat_existing = repeat_existing
        for dataset in self.conf.datasets:
            dataset_path = self.conf.normalize_path(dataset['path'])
            self.tasks.sample_file(dataset_path)

            for db in self.conf.databases:
                self.tdb = self.conf.make_db(database=db, dataset=dataset)
                self.database = db
                self.dataset = dataset
                self.bench_buffered_graph()
                self.conf.default_stats_file.dump_to_file()

    def bench_buffered_graph(self):
        if self.tdb is None:
            return
        if self.tdb.count_docs() == 0:
            return
        print('- Benchmarking: {} @ {}'.format(
            self.dataset['name'],
            self.db['name']
        ))

        self.doc_ids_to_query = []
        self.substrings_to_query = []
        self.regexs_to_query = []
        self.docs_to_change_by_one = []
        self.docs_to_change_batched = [[]]

        # Queries returning single object.
        self.bench_task(
            name='Random Reads: Retreive Doc by ID',
            func=self.retreive_doc_by_id
        )

        # Queries returning collections.
        self.bench_task(
            name='Random Reads: Find Docs with Substring',
            func=self.find_docs_with_substring
        )
        self.bench_task(
            name='Random Reads: Find Docs with RegEx',
            func=self.find_docs_with_regex
        )

        # Reversable write operations.
        self.bench_task(
            name='Random Writes: Remove Doc',
            func=self.remove_doc
        )
        self.bench_task(
            name='Random Writes: Upsert Doc',
            func=self.upsert_doc
        )
        self.bench_task(
            name='Random Writes: Remove Docs Batch',
            func=self.remove_docs
        )
        self.bench_task(
            name='Random Writes: Upsert Docs Batch',
            func=self.upsert_docs
        )

    def bench_task(self, name, func):
        dataset_name = self.dataset['name']
        db_name = self.db['name']
        print(f'--- {db_name}: {name} @ {dataset_name}')
        counter = MicroBench(
            name=name,
            func=func,
            database=db_name,
            dataset=dataset_name,
            source=self.conf.default_stats_file,
            device_name=self.conf.device_name,
            limit_iterations=1,
            limit_seconds=None,
            limit_operations=None,
        )

        if not self.repeat_existing:
            if self.conf.default_stats_file.contains(counter):
                print('--- Skipping!')
                return
        print('---- Running!')
        counter.run()
        if counter.count_operations == 0:
            print('---- Didn\'t measure!')
            return
        print('---- Importing new stats!')

    # ---
    # Operations
    # ---

    def retreive_doc_by_id(self) -> int:
        cnt = 0
        cnt_found = 0
        t0 = time()
        for e in self.tasks.edges_to_query:
            match = self.tdb.edge_directed(e['v1'], e['v2'])
            cnt += 1
            cnt_found += 0 if (match is None) else 1
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        print(f'---- {cnt} ops: {cnt_found} undirected matches')
        return cnt

    def find_es_related(self) -> int:
        cnt = 0
        cnt_found = 0
        t0 = time()
        for v in self.tasks.nodes_to_query:
            es = self.tdb.edges_related(v)
            cnt += 1
            cnt_found += len(es)
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        print(f'---- {cnt} ops: {cnt_found} edges found')
        return cnt

    def find_es_from(self) -> int:
        cnt = 0
        cnt_found = 0
        t0 = time()
        for v in self.tasks.nodes_to_query:
            es = self.tdb.edges_from(v)
            cnt += 1
            cnt_found += len(es)
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        print(f'---- {cnt} ops: {cnt_found} edges found')
        return cnt

    def find_docs_with_regex(self) -> int:
        cnt = 0
        cnt_found = 0
        t0 = time()
        for v in self.tasks.nodes_to_query:
            es = self.tdb.edges_to(v)
            cnt += 1
            cnt_found += len(es)
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        print(f'---- {cnt} ops: {cnt_found} edges found')
        return cnt

    def find_vs_related(self) -> int:
        cnt = 0
        cnt_found = 0
        t0 = time()
        for v in self.tasks.nodes_to_query:
            vs = self.tdb.nodes_related(v)
            cnt += 1
            cnt_found += len(vs)
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        print(f'---- {cnt} ops: {cnt_found} related nodes')
        return cnt

    def count_v_related(self) -> int:
        cnt = 0
        t0 = time()
        for v in self.tasks.nodes_to_query:
            self.tdb.count_related(v)
            cnt += 1
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        return cnt

    def count_v_followers(self) -> int:
        cnt = 0
        t0 = time()
        for v in self.tasks.nodes_to_query:
            self.tdb.count_followers(v)
            cnt += 1
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        return cnt

    def count_v_following(self) -> int:
        cnt = 0
        t0 = time()
        for v in self.tasks.nodes_to_query:
            self.tdb.count_following(v)
            cnt += 1
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        return cnt

    def find_vs_related_related(self) -> int:
        cnt = 0
        cnt_found = 0
        t0 = time()
        for v in self.tasks.nodes_to_analyze:
            vs = self.tdb.nodes_related_to_related(v)
            cnt += 1
            cnt_found += len(vs)
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        print(f'---- {cnt} ops: {cnt_found} related to related nodes')
        return cnt

    def remove_doc(self) -> int:
        cnt = 0
        for e in self.tasks.edges_to_change_by_one:
            self.tdb.remove_edge(e)
            cnt += 1
        return cnt

    def upsert_doc(self) -> int:
        cnt = 0
        for e in self.tasks.edges_to_change_by_one:
            self.tdb.upsert_edge(e)
            cnt += 1
        return cnt

    def remove_docs(self) -> int:
        cnt = 0
        for es in self.tasks.edges_to_change_batched:
            self.tdb.remove_edges(es)
            cnt += len(es)
        return cnt

    def upsert_docs(self) -> int:
        cnt = 0
        for es in self.tasks.edges_to_change_batched:
            self.tdb.upsert_edges(es)
            cnt += len(es)
        return cnt

    def remove_v(self) -> int:
        cnt = 0
        for v in self.tasks.nodes_to_change_by_one:
            self.tdb.remove_node(v)
            cnt += 1
        return cnt

    def remove_bulk(self) -> int:
        c = self.tdb.count_edges()
        self.tdb.remove_all()
        return c - self.tdb.count_edges()

    def import_bulk(self) -> int:
        self.tdb.insert_adjacency_list(self.dataset_path)
        return self.tdb.count_edges()


if __name__ == "__main__":
    try:
        P3Bench().run()
    finally:
        P0Config.shared().default_stats_file.dump_to_file()
