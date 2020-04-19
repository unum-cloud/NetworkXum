import os
from time import time

from pygraphdb.base_graph import GraphBase
from pygraphdb.helpers import StatsCounter
from pystats.file import StatsFile

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

    def __init__(self, max_seconds_per_query=15):
        self.max_seconds_per_query = max_seconds_per_query

    def run(self, repeat_existing=False):
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
                g = graph_type(url)
                if (g.count_edges() == 0):
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
        # Queries returning single object.
        self.one('Retrieve Directed Edge', self.find_e_directed)
        self.one('Retrieve Undirected Edge', self.find_e_undirected)

        # Queries returning collections.
        self.one('Retrieve Outgoing Edges', self.find_es_from)
        self.one('Retrieve Ingoing Edges', self.find_es_to)
        self.one('Retrieve Connected Edges', self.find_es_related)
        self.one('Retrieve Friends', self.find_vs_related)
        self.one('Retrieve Friends of Friends', self.find_vs_related_related)

        # Queries returning stats.
        self.one('Count Friends', self.count_v_related)
        self.one('Count Followers', self.count_v_followers)
        self.one('Count Following', self.count_v_following)

        # Reversable write operations.
        self.one('Remove Edge', self.remove_e)  # Single edge removals
        self.one('Upsert Edge', self.upsert_e)  # Single edge inserts
        self.one('Remove Edges Batch', self.remove_es)  # Batched edge removals
        self.one('Upsert Edges Batch', self.upsert_es)  # Batched edge inserts

        if remove_all_afterwards:
            self.one('Remove Vertex', self.remove_v)
            self.one('Remove All', self.remove_bulk)

    def one(self, operation_name, f):
        counter = StatsCounter()
        dataset_name = config.dataset_name(self.dataset_path)
        wrapper_name = config.wrapper_name(self.graph)
        print(f'--- {wrapper_name}: {operation_name} @ {dataset_name}')
        if not self.repeat_existing:
            if config.stats.find_index(
                wrapper_class=wrapper_name,
                operation_name=operation_name,
                dataset=dataset_name,
            ) is not None:
                print('--- Skipping!')
                return
        counter.handle(f)
        if counter.count_operations == 0:
            print(f'---- Didnt measure!')
            return
        print(f'---- Importing new stats!')
        config.stats.upsert(
            wrapper_class=wrapper_name,
            operation_name=operation_name,
            dataset=dataset_name,
            stats=counter,
        )

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


if __name__ == "__main__":
    try:
        SimpleBenchmark().run()
    finally:
        config.stats.dump_to_file()
