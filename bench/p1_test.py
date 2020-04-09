from pygraphdb.graph_base import GraphBase
from pygraphdb.edge import Edge
from pygraphdb.helpers import export_edges_into_graph_parallel

import config


class Tester(object):
    """
    Test basic operations over a tiny graph.
    Use this ONLY for empty databases!
    """

    def __init__(self):
        self.edges = [
            Edge(1, 2, weight=4).__dict__,
            Edge(2, 3, weight=20).__dict__,
            Edge(3, 4, weight=10).__dict__,
            Edge(4, 5, weight=3).__dict__,
            Edge(5, 3, weight=2).__dict__,
            Edge(4, 1, weight=5).__dict__,
            Edge(8, 6, weight=4).__dict__,
            Edge(8, 7, weight=2).__dict__,
            Edge(6, 1, weight=3).__dict__,
            Edge(7, 1, weight=2).__dict__,
        ]

    def run(self):
        for graph_type in config.wrapper_types:
            file_path = config.dataset_test
            url = config.database_url(graph_type, file_path)
            if url is None:
                continue
            g = graph_type(url)
            self.run_one(g)

    def run_one(self, g):
        print(f'-- Starting testing of: {config.wrapper_name(g)}')

        print(f'--- Cleaning')
        g.remove_all()
        self.validate_empty_edges(g)
        self.validate_empty_nodes(g)

        print(f'--- Single Operations')
        for e in self.edges:
            g.insert_edge(e)
        self.validate_contents(g)
        for e in self.edges:
            g.remove_edge(e)
        self.validate_empty_edges(g)

        print(f'--- Batch Operations')
        g.insert_edges(self.edges)
        self.validate_contents(g)
        g.remove_edges(self.edges)
        self.validate_empty_edges(g)

        print(f'--- Bulk Operations')
        g.insert_dump(config.dataset_test)
        self.validate_contents(g)
        g.remove_all()
        self.validate_empty_edges(g)
        self.validate_empty_nodes(g)

        # print(f'--- Parallel Bulk Operations')
        # export_edges_into_graph_parallel(config.dataset_test, g)
        # self.validate_contents(g)
        print(f'--- Passed All!')

    def validate_empty_edges(self, g):
        assert g.count_edges() == 0, \
            f'count_edges must be =0: {g.count_edges()}'

    def validate_empty_nodes(self, g):
        assert g.count_nodes() == 0, \
            f'count_nodes must be =0: {g.count_nodes()}'

    def validate_contents(self, g):
        for e in self.edges:
            assert g.find_edge(e['v_from'], e['v_to']), \
                f'No directed edge: {e}'
            assert g.find_edge_or_inv(e['v_from'], e['v_to']), \
                f'No undirected edge: {e}'

        assert g.count_edges() == 10, \
            f'count_edges: {g.count_edges()}'
        assert g.count_nodes() == 8, \
            f'count_nodes: {g.count_nodes()}'
        assert g.count_followers(1) == (3, 10.0), \
            f'count_followers: {g.count_followers(1)}'
        assert g.count_following(1) == (1, 4.0), \
            f'count_following: {g.count_following(1)}'
        assert g.count_related(1) == (4, 14.0), \
            f'count_related: {g.count_related(1)}'
        assert set(g.nodes_related(1)) == {2, 4, 6, 7}, \
            f'nodes_related: {g.nodes_related(1)}'
        assert set(g.nodes_related_to_related(8)) == {1}, \
            f'nodes_related_to_related: {g.nodes_related_to_related(8)}'
        assert g.count_followers(5) == (1, 3.0), \
            f'count_followers: {g.count_followers(5)}'
        assert g.count_following(5) == (1, 2.0), \
            f'count_following: {g.count_following(5)}'
        # assert g.shortest_path(4, 3) == ([4, 5, 3], 5.0), \
        #     f'shortest_path: {g.shortest_path(4, 3)}'


if __name__ == "__main__":
    Tester().run()
