import os

from pygraphdb.graph_base import GraphBase
from pystats.file import StatsFile
from bench.tasks_sampler import TasksSampler
from pygraphdb.helpers import StatsCounter


class FullBench(object):
    """

    """

    def __init__(
        self,
        graph: GraphBase,
        stats: StatsFile,
        tasks: TasksSampler,
        dataset: str,
    ):
        self.graph = graph
        self.stats = stats
        self.tasks = tasks
        self.dataset = dataset

    def run(
        self,
        repeat_existing=False,
        clear_afterwards=False,
    ):
        # Benchmark groups in self.tasks.chronological order:
        # --
        # - bulk load
        # - index construction
        # --
        # - lookups
        # - analytics
        # --
        # - edge removals
        # - edge inserts
        # - optional node removals
        # --
        def micro(operation_name, f):
            counter = StatsCounter()
            dataset_name = os.path.basename(self.dataset)
            class_name = self.graph.__class__.__name__
            print(f'-- {class_name}: {operation_name} @ {dataset_name}')
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
            print(f'--- Importing new stats!')
            self.stats.insert(
                class_name,
                operation_name,
                dataset_name,
                counter
            )

        if self.graph.count_edges() == 0:
            micro('Import Dump', self.insert_bulk)

        # Queries returning single object.
        micro('Retrieve Directed Edge', self.find_e_directed)
        micro('Retrieve Undirected Edge', self.find_e_undirected)

        # Queries returning collections.
        micro('Retrieve Outgoing Edges', self.find_es_from)
        micro('Retrieve Incoming Edges', self.find_es_to)
        micro('Retrieve Connected Edges', self.find_es_related)
        micro('Retrieve Friends', self.find_vs_related)
        micro('Retrieve Friends of Friends', self.find_vs_related_related)

        # Queries returning stats.
        micro('Count Friends', self.count_v_related)
        micro('Count Followers', self.count_v_followers)
        micro('Count Following', self.count_v_following)

        # Reversable write operations.
        micro('Remove Edge', self.remove_e)  # Single edge removals
        micro('Insert Edge', self.insert_e)  # Single edge inserts
        micro('Remove Edges Batch', self.remove_es)  # Batched edge removals
        micro('Insert Edges Batch', self.insert_es)  # Batched edge inserts

        if clear_afterwards:
            micro('Remove Vertex', self.remove_v)
            micro('Remove All', self.remove_bulk)

    # ---
    # Operations
    # ---

    def find_e_directed(self) -> int:
        # Try both existing and potentially missing edges
        half = int(len(self.tasks.edges_to_query) / 2)
        cnt = 0
        for e in self.tasks.edges_to_query[:half]:
            e = self.graph.edge_directed(e['v_from'], e['v_to'])
            cnt += 1
        for e in self.tasks.edges_to_query[half:]:
            e = self.graph.edge_directed(e['v_to'], e['v_from'])
            cnt += 1
        return cnt

    def find_e_undirected(self) -> int:
        cnt = 0
        for e in self.tasks.edges_to_query:
            self.graph.edge_directed(e['v_from'], e['v_to'])
            cnt += 1
        return cnt

    def find_es_related(self) -> int:
        cnt = 0
        for v in self.tasks.nodes_to_query:
            self.graph.edges_related(v)
            cnt += 1
        return cnt

    def find_es_from(self) -> int:
        cnt = 0
        for v in self.tasks.nodes_to_query:
            self.graph.edges_from(v)
            cnt += 1
        return cnt

    def find_es_to(self) -> int:
        cnt = 0
        for v in self.tasks.nodes_to_query:
            self.graph.edges_to(v)
            cnt += 1
        return cnt

    def find_vs_related(self) -> int:
        cnt = 0
        for v in self.tasks.nodes_to_query:
            self.graph.vertexes_related(v)
            cnt += 1
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
            self.graph.vertexes_related_to_related(v)
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
            self.graph.insert_edge(e)
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
            self.graph.insert_edges(es)
            cnt += len(es)
        return cnt

    def insert_bulk(self) -> int:
        self.graph.insert_dump(self.dataset)
        return self.graph.count_edges()

    def remove_v(self) -> int:
        cnt = 0
        for v in self.tasks.nodes_to_change_by_one:
            self.graph.remove_vertex(v)
            cnt += 1
        return cnt

    def remove_bulk(self) -> int:
        c = self.graph.count_edges()
        self.graph.remove_all()
        return c - self.graph.count_edges()
