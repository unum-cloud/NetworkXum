from pygraphdb.graph_base import GraphBase
from benchmarks.stats import Stats
from benchmarks.tasks import Tasks


class GraphBenchmark(object):

    def __init__(self, graph: GraphBase, stats: Stats, tasks: Tasks):
        self.graph = graph
        self.stats = stats
        self.tasks = tasks

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
            counter = StatsCounter().handle(f)
            class_name = str(type(self.graph))
            self.stats.insert(class_name, operation_name, counter)
            return

        # Bulk write operations.
        # micro('bulk-load', self.db.port_file(file_pat)
        # micro('bulk-index', self.db.eate_index)
        # This operation will alter the state of database,
        # changing the results on future runs.
        # micro('remove-v', self.find_e_directed)

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
        micro('remove-e', self.remove_e)
        micro('insert-e', self.insert_e)

    # ---
    # Operations
    # ---

    def find_e_directed(self) -> int:
        # Try both existing and potentially missing edges
        half = len(edges_to_query) / 2
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
        for e in self.tasks.edges_to_remove:
            self.graph.delete(e)
            cnt += 1
        return cnt

    def insert_e(self) -> int:
        cnt = 0
        for e in self.tasks.edges_to_insert:
            self.graph.insert(e)
            cnt += 1
        return cnt
