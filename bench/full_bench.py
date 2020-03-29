from pygraphdb.graph_base import GraphBase
from bench.stats_file import StatsFile
from bench.tasks_sampler import TasksSampler
from helpers.shared import StatsCounter


class FullBench(object):

    def __init__(
        self,
        graph: GraphBase,
        stats: StatsFile,
        tasks: TasksSampler,
        datasource: str,
        repeat_existing=False,
    ):
        self.graph = graph
        self.stats = stats
        self.tasks = tasks
        self.datasource = datasource
        self.repeat_existing = repeat_existing

    def run(self):
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
            counter.handle(f)
            class_name = self.graph.__class__.__name__
            if not self.repeat_existing:
                if self.stats.find(class_name, operation_name) is not None:
                print(f'Reusing stats {class_name}, {operation_name}')
                return
            print(f'Importing stats {class_name}, {operation_name}: {counter}')
            self.stats.insert(class_name, operation_name, counter)
            return

        # Bulk write operations.
        micro('insert-bulk', lambda: self.graph.insert_dump(self.datasource))

        # Queries returning single object.
        micro('find-e-directed', self.find_e_directed)
        micro('find-e-undirected', self.find_e_undirected)

        # Queries returning collections.
        micro('find-es-from', self.find_es_from)
        micro('find-es-to', self.find_es_to)
        micro('find-es-related', self.find_es_related)
        micro('find-vs-related', self.find_vs_related)
        micro('find-vs-related-related', self.find_vs_related_related)

        # Queries returning stats.
        micro('count-v-related', self.count_v_related)
        micro('count-v-followers', self.count_v_followers)
        micro('count-v-following', self.count_v_following)

        # Write operations.
        micro('remove-e', self.remove_e)  # Single edge removals
        micro('insert-e', self.insert_e)  # Single edge inserts
        micro('remove-es', self.remove_es)  # Batched edge removals
        micro('insert-es', self.insert_es)  # Batched edge inserts
        micro('remove-v', self.remove_v)  # Single node removals

        # Cleaning
        micro('remove-bulk', lambda: self.graph.remove_all())

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

    def remove_v(self) -> int:
        cnt = 0
        for v in self.tasks.nodes_to_change_by_one:
            self.graph.remove_vertex(v)
            cnt += 1
        return cnt
