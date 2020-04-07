from pygraphdb.graph_base import GraphBase
from pygraphdb.edge import Edge


class FullTest(object):

    def __init__(self, graph: GraphBase):
        self.graph = graph

    def run(self):
        g = self.graph

        # Clear the DB before run.
        g.remove_all()
        assert g.count_nodes() == 0, \
            f'count_nodes before initialization: {g.count_nodes()}'
        assert g.count_edges() == 0, \
            f'count_edges before initialization: {g.count_edges()}'

        # Fill the DB.
        edges = [
            Edge(1, 2, weight=4),
            Edge(2, 3, weight=20),
            Edge(3, 4, weight=10),
            Edge(4, 5, weight=3),
            Edge(5, 3, weight=2),
            Edge(4, 1, weight=5),
            Edge(8, 6, weight=4),
            Edge(8, 7, weight=2),
            Edge(6, 1, weight=3),
            Edge(7, 1, weight=2),
        ]
        es_last = 0
        vs_last = 0
        for e in edges:
            g.insert_edge(e.__dict__)
            assert g.find_edge(e['v_from'], e['v_to']), \
                f'No directed edge: {e}'
            assert g.find_edge_or_inv(e['v_from'], e['v_to']), \
                f'No undirected edge: {e}'
            # Make sure the size of the DB isn't getting smaller.
            # It may remain unchanged for persistent stores.
            es_count = g.count_edges()
            assert es_count >= es_last, 'Didnt update number of edges'
            es_last = es_count
            vs_count = g.count_nodes()
            assert vs_count >= vs_last, 'Problems in counting nodes'
            vs_last = vs_count
        # Validate the queries.
        assert g.count_nodes() == 8, \
            f'count_nodes: {g.count_nodes()}'
        assert g.count_edges() == 10, \
            f'count_edges: {g.count_edges()}'
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
        # Remove elements one by one.
        for e in edges:
            g.remove_edge(e)
        # Bulk load data again.
        g.insert_dump('artifacts/test.csv')
        assert g.count_nodes() == 8, \
            f'count_nodes after dump imports: {g.count_nodes()}'
        assert g.count_edges() == 10, \
            f'count_edges after dump imports: {g.count_edges()}'
        # Clear all the data at once.
        g.remove_all()
        assert g.count_nodes() == 0, \
            f'count_nodes after remove_alling: {g.count_nodes()}'
        assert g.count_edges() == 0, \
            f'count_edges after remove_alling: {g.count_edges()}'
