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
                self.g = self.conf.make_db(database=db, dataset=dataset)
                self.database = db
                self.dataset = dataset
                self.bench_buffered_graph()
                self.conf.default_stats_file.dump_to_file()

    def bench_buffered_graph(self, remove_all_afterwards=False):
        if self.g is None:
            return
        is_in_ram = bool(type(self.g).__in_memory__)
        if (self.g.count_edges() == 0) and (not is_in_ram):
            return
        print('- Benchmarking: {} @ {}'.format(
            self.dataset['name'],
            self.database['name']
        ))

        if is_in_ram:
            self.bench_task(
                name='Sequential Writes: Import CSV',
                func=self.import_bulk
            )

        # Queries returning single object.
        self.bench_task(
            name='Random Reads: Find Directed Edge',
            func=self.find_e_directed
        )
        self.bench_task(
            name='Random Reads: Find Any Relation',
            func=self.find_e_undirected
        )

        # Queries returning collections.
        self.bench_task(
            name='Random Reads: Find Ingoing Edges',
            func=self.find_es_to
        )
        self.bench_task(
            name='Random Reads: Find Connected Edges',
            func=self.find_es_related
        )
        self.bench_task(
            name='Random Reads: Find Friends',
            func=self.find_vs_related
        )

        # Queries returning stats.
        self.bench_task(
            name='Random Reads: Count Friends',
            func=self.count_v_related
        )
        self.bench_task(
            name='Random Reads: Count Followers',
            func=self.count_v_followers
        )

        # Reversable write operations.
        self.bench_task(
            name='Random Writes: Remove Edge',
            func=self.remove_e
        )
        self.bench_task(
            name='Random Writes: Upsert Edge',
            func=self.upsert_e
        )
        self.bench_task(
            name='Random Writes: Remove Edges Batch',
            func=self.remove_es
        )
        self.bench_task(
            name='Random Writes: Upsert Edges Batch',
            func=self.upsert_es
        )

        if remove_all_afterwards:
            self.bench_task(
                name='Random Writes: Remove Vertex',
                func=self.remove_v
            )
            self.bench_task(
                name='Sequential Writes: Remove All',
                func=self.remove_bulk
            )

    def bench_task(self, name, func):
        dataset_name = self.dataset['name']
        db_name = self.database['name']
        print(f'--- {db_name}: {name} @ {dataset_name}')
        counter = MicroBench(
            benchmark_name=name,
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

    def find_e_directed(self) -> int:
        # Try both existing and potentially missing edges
        half = int(len(self.tasks.edges_to_query) / 2)
        cnt = 0
        cnt_found = 0
        t0 = time()
        for e in self.tasks.edges_to_query[:half]:
            match = self.g.edge_directed(e.first, e.second)
            cnt += 1
            cnt_found += 0 if (match is None) else 1
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        t0 = time()
        for e in self.tasks.edges_to_query[half:]:
            match = self.g.edge_directed(e.second, e.first)
            cnt += 1
            cnt_found += 0 if (match is None) else 1
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        print(f'---- {cnt} ops: {cnt_found} directed matches')
        return cnt

    def find_e_undirected(self) -> int:
        cnt = 0
        cnt_found = 0
        t0 = time()
        for e in self.tasks.edges_to_query:
            match = self.g.edge_directed(e.first, e.second)
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
            es = self.g.edges_related(v)
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
            es = self.g.edges_from(v)
            cnt += 1
            cnt_found += len(es)
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        print(f'---- {cnt} ops: {cnt_found} edges found')
        return cnt

    def find_es_to(self) -> int:
        cnt = 0
        cnt_found = 0
        t0 = time()
        for v in self.tasks.nodes_to_query:
            es = self.g.edges_to(v)
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
            vs = self.g.nodes_related(v)
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
            self.g.count_related(v)
            cnt += 1
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        return cnt

    def count_v_followers(self) -> int:
        cnt = 0
        t0 = time()
        for v in self.tasks.nodes_to_query:
            self.g.count_followers(v)
            cnt += 1
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        return cnt

    def count_v_following(self) -> int:
        cnt = 0
        t0 = time()
        for v in self.tasks.nodes_to_query:
            self.g.count_following(v)
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
            vs = self.g.nodes_related_to_related(v)
            cnt += 1
            cnt_found += len(vs)
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        print(f'---- {cnt} ops: {cnt_found} related to related nodes')
        return cnt

    def remove_e(self) -> int:
        cnt = 0
        for e in self.tasks.edges_to_change_by_one:
            self.g.remove_edge(e)
            cnt += 1
        return cnt

    def upsert_e(self) -> int:
        cnt = 0
        for e in self.tasks.edges_to_change_by_one:
            self.g.upsert_edge(e)
            cnt += 1
        return cnt

    def remove_es(self) -> int:
        cnt = 0
        for es in self.tasks.edges_to_change_batched:
            self.g.remove_edges(es)
            cnt += len(es)
        return cnt

    def upsert_es(self) -> int:
        cnt = 0
        for es in self.tasks.edges_to_change_batched:
            self.g.upsert_edges(es)
            cnt += len(es)
        return cnt

    def remove_v(self) -> int:
        cnt = 0
        for v in self.tasks.nodes_to_change_by_one:
            self.g.remove_node(v)
            cnt += 1
        return cnt

    def remove_bulk(self) -> int:
        c = self.g.count_edges()
        self.g.remove_all()
        return c - self.g.count_edges()

    def import_bulk(self) -> int:
        self.g.insert_adjacency_list(self.dataset_path)
        return self.g.count_edges()


if __name__ == "__main__":
    c = P0Config(device_name='MacbookPro')
    try:
        P3Bench().run()
    finally:
        c.default_stats_file.dump_to_file()
