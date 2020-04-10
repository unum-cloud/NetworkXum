import os

from pygraphdb.graph_base import GraphBase
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

    def run(self):
        for dataset_path in config.datasets:
            self.tasks = TasksSampler()
            max_wanted_edges = max(
                config.count_finds, config.count_analytics, config.count_changes)
            self.tasks.sample_from_file_cpp(dataset_path, max_wanted_edges)

            for graph_type in config.wrapper_types:
                url = config.database_url(graph_type, dataset_path)
                if url is None:
                    continue
                g = graph_type(url)
                if (g.count_nodes() != 0):
                    continue

                dataset_name = config.dataset_name(dataset_path)
                wrapper_name = config.wrapper_name(g)
                print(f'-- Benchmarking: {dataset_name} @ {wrapper_name}')
                self.run_one(g)

    def run_one(self, g, remove_all_afterwards=False):
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
        self.one('Insert Edge', self.insert_e)  # Single edge inserts
        self.one('Remove Edges Batch', self.remove_es)  # Batched edge removals
        self.one('Insert Edges Batch', self.insert_es)  # Batched edge inserts

        if remove_all_afterwards:
            self.one('Remove Vertex', self.remove_v)
            self.one('Remove All', self.remove_bulk)

    def one(operation_name, f):
        counter = StatsCounter()
        dataset_name = os.path.basename(self.dataset_path)
        class_name = self.graph.__class__.__name__
        print(f'--- {class_name}: {operation_name} @ {dataset_name}')
        if not repeat_existing:
            old_results = self.stats.find(
                class_name,
                operation_name,
                dataset_name
            )
            if old_results is not None:
                print('--- Skipping!')
                return
        counter.handle(f)
        print(f'---- Importing new stats!')
        self.stats.insert(
            class_name,
            operation_name,
            dataset_name,
            counter
        )

    # ---
    # Operations
    # ---

    def find_e_directed(self) -> int:
        # Try both existing and potentially missing edges
        half = int(len(self.tasks.edges_to_query) / 2)
        cnt = 0
        cnt_found = 0
        for e in self.tasks.edges_to_query[:half]:
            match = self.graph.find_edge(e['v_from'], e['v_to'])
            cnt += 1
            cnt_found += 0 if (match is None) else 1
        for e in self.tasks.edges_to_query[half:]:
            match = self.graph.find_edge(e['v_to'], e['v_from'])
            cnt += 1
            cnt_found += 0 if (match is None) else 1
        print(f'---- {cnt} ops: {cnt_found} directed matches')
        return cnt

    def find_e_undirected(self) -> int:
        cnt = 0
        cnt_found = 0
        for e in self.tasks.edges_to_query:
            match = self.graph.find_edge(e['v_from'], e['v_to'])
            cnt += 1
            cnt_found += 0 if (match is None) else 1
        print(f'---- {cnt} ops: {cnt_found} undirected matches')
        return cnt

    def find_es_related(self) -> int:
        cnt = 0
        cnt_found = 0
        for v in self.tasks.nodes_to_query:
            es = self.graph.edges_related(v)
            cnt += 1
            cnt_found += len(es)
        print(f'---- {cnt} ops: {cnt_found} edges found')
        return cnt

    def find_es_from(self) -> int:
        cnt = 0
        cnt_found = 0
        for v in self.tasks.nodes_to_query:
            es = self.graph.edges_from(v)
            cnt += 1
            cnt_found += len(es)
        print(f'---- {cnt} ops: {cnt_found} edges found')
        return cnt

    def find_es_to(self) -> int:
        cnt = 0
        cnt_found = 0
        for v in self.tasks.nodes_to_query:
            es = self.graph.edges_to(v)
            cnt += 1
            cnt_found += len(es)
        print(f'---- {cnt} ops: {cnt_found} edges found')
        return cnt

    def find_vs_related(self) -> int:
        cnt = 0
        cnt_found = 0
        for v in self.tasks.nodes_to_query:
            vs = self.graph.nodes_related(v)
            cnt += 1
            cnt_found += len(vs)
        print(f'---- {cnt} ops: {cnt_found} related nodes')
        return cnt

    def count_v_related(self) -> int:
        cnt = 0
        for v in self.tasks.nodes_to_query:
            self.graph.count_related(v)
            cnt += 1
        return cnt

    def count_v_followers(self) -> int:
        cnt = 0
        for v in self.tasks.nodes_to_query:
            self.graph.count_followers(v)
            cnt += 1
        return cnt

    def count_v_following(self) -> int:
        cnt = 0
        for v in self.tasks.nodes_to_query:
            self.graph.count_following(v)
            cnt += 1
        return cnt

    def find_vs_related_related(self) -> int:
        cnt = 0
        for v in self.tasks.nodes_to_analyze:
            self.graph.nodes_related_to_related(v)
            cnt += 1
        return cnt

    def remove_e(self) -> int:
        cnt = 0
        for e in self.tasks.edges_to_change_by_one:
            self.graph.remove_edge(e)
            cnt += 1
        return cnt

    def insert_e(self) -> int:
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

    def insert_es(self) -> int:
        cnt = 0
        for es in self.tasks.edges_to_change_batched:
            self.graph.upsert_edges(es)
            cnt += len(es)
        return cnt

    def upsert_adjacency_list(self) -> int:
        self.graph.upsert_adjacency_list(self.dataset_path)
        return self.graph.count_edges()

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
    SimpleBenchmark().run()
    config.stats.dump_to_file()
