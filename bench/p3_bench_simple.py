import os
from time import time

from pystats2md.stats_file import StatsFile
from pystats2md.micro_bench import MicroBench

from pygraphdb.base_graph import GraphBase

import config
from tasks_sampler import TasksSampler


class SimpleBenchmark(object):
    """
        Benchmarks groups of operations in following order:
        2. Edge lookups and simple queries.
        3. A few complex analytical queries.
        4. Modifications: removing and restoring same objects.
        5. Clearing all the data (if needed).
    """

    def __init__(self, max_seconds_per_query=120):
        self.max_seconds_per_query = max_seconds_per_query

    def run(self, repeat_existing=True):
        self.repeat_existing = repeat_existing
        for dataset_path in config.datasets:
            self.dataset_path = dataset_path
            self.tasks = TasksSampler()
            self.tasks.count_finds = config.count_finds
            self.tasks.count_analytics = config.count_analytics
            self.tasks.count_changes = config.count_changes
            self.tasks.sample_reservoir(dataset_path)

            for graph_type in config.wrapper_types:
                url = config.database_url(graph_type, dataset_path)
                if url is None:
                    continue
                g = graph_type(url=url)
                if (g.count_edges() == 0) and (not graph_type.__in_memory__):
                    continue

                dataset_name = config.dataset_name(dataset_path)
                wrapper_name = config.wrapper_name(g)
                print(f'-- Benchmarking: {dataset_name} @ {wrapper_name}')
                self.graph = g
                self.run_one()
                self.graph = None
                config.stats.dump_to_file()

            self.tasks = None
            self.dataset_path = None

    def run_one(self, remove_all_afterwards=False):
        if type(self.graph).__in_memory__:
            self.one('Sequential Writes: Import CSV',
                     self.import_bulk)

        # Queries returning single object.
        self.one('Random Reads: Find Directed Edge',
                 self.find_e_directed)
        self.one('Random Reads: Find Any Relation',
                 self.find_e_undirected)

        # # Queries returning collections.
        # self.one('Random Reads: Find Outgoing Edges',
        #          self.find_es_from)
        self.one('Random Reads: Find Ingoing Edges',
                 self.find_es_to)
        self.one('Random Reads: Find Connected Edges',
                 self.find_es_related)
        self.one('Random Reads: Find Friends',
                 self.find_vs_related)
        # self.one('Random Reads: Find Friends of Friends',
        #          self.find_vs_related_related)

        # Queries returning stats.
        self.one('Random Reads: Count Friends',
                 self.count_v_related)
        self.one('Random Reads: Count Followers',
                 self.count_v_followers)
        # self.one('Random Reads: Count Following',
        #          self.count_v_following)

        # Reversable write operations.
        self.one('Random Writes: Remove Edge',
                 self.remove_e)  # Single edge removals
        self.one('Random Writes: Upsert Edge',
                 self.upsert_e)  # Single edge inserts
        self.one('Random Writes: Remove Edges Batch',
                 self.remove_es)  # Batched edge removals
        self.one('Random Writes: Upsert Edges Batch',
                 self.upsert_es)  # Batched edge inserts

        if remove_all_afterwards:
            self.one('Random Writes: Remove Vertex',
                     self.remove_v)
            self.one('Sequential Writes: Remove All',
                     self.remove_bulk)

    def one(self, benchmark_name, f):
        dataset_name = config.dataset_name(self.dataset_path)
        wrapper_name = config.wrapper_name(self.graph)
        print(f'--- {wrapper_name}: {benchmark_name} @ {dataset_name}')
        counter = MicroBench(
            benchmark_name=benchmark_name,
            func=f,
            database=wrapper_name,
            dataset=dataset_name,
            source=config.stats,
            device_name='MacbookPro',
            limit_iterations=1,
            limit_seconds=None,
            limit_operations=None,
        )

        if not self.repeat_existing:
            if config.stats.contains(counter):
                print('--- Skipping!')
                return
        print(f'---- Running!')
        counter.run()
        if counter.count_operations == 0:
            print(f'---- Didnt measure!')
            return
        print(f'---- Importing new stats!')

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
            match = self.graph.edge_directed(e['v1'], e['v2'])
            cnt += 1
            cnt_found += 0 if (match is None) else 1
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        t0 = time()
        for e in self.tasks.edges_to_query[half:]:
            match = self.graph.edge_directed(e['v2'], e['v1'])
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
            match = self.graph.edge_directed(e['v1'], e['v2'])
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
            es = self.graph.edges_related(v)
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
            es = self.graph.edges_from(v)
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
            es = self.graph.edges_to(v)
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
            vs = self.graph.nodes_related(v)
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
            self.graph.count_related(v)
            cnt += 1
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        return cnt

    def count_v_followers(self) -> int:
        cnt = 0
        t0 = time()
        for v in self.tasks.nodes_to_query:
            self.graph.count_followers(v)
            cnt += 1
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        return cnt

    def count_v_following(self) -> int:
        cnt = 0
        t0 = time()
        for v in self.tasks.nodes_to_query:
            self.graph.count_following(v)
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
            vs = self.graph.nodes_related_to_related(v)
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
            self.graph.remove_edge(e)
            cnt += 1
        return cnt

    def upsert_e(self) -> int:
        cnt = 0
        for e in self.tasks.edges_to_change_by_one:
            self.graph.upsert_edge(e)
            cnt += 1
        return cnt

    def remove_es(self) -> int:
        cnt = 0
        for es in self.tasks.edges_to_change_batched:
            self.graph.remove_edges(es)
            cnt += len(es)
        return cnt

    def upsert_es(self) -> int:
        cnt = 0
        for es in self.tasks.edges_to_change_batched:
            self.graph.upsert_edges(es)
            cnt += len(es)
        return cnt

    def remove_v(self) -> int:
        cnt = 0
        for v in self.tasks.nodes_to_change_by_one:
            self.graph.remove_node(v)
            cnt += 1
        return cnt

    def remove_bulk(self) -> int:
        c = self.graph.count_edges()
        self.graph.remove_all()
        return c - self.graph.count_edges()

    def import_bulk(self) -> int:
        self.graph.insert_adjacency_list(self.dataset_path)
        return self.graph.count_edges()


if __name__ == "__main__":
    try:
        SimpleBenchmark().run()
    finally:
        config.stats.dump_to_file()
