from PyWrappedGraph.BaseAPI import BaseAPI
from PyWrappedHelpers.TextFile import TextFile
from PyWrappedHelpers.Algorithms import export_edges_into_graph_parallel, class_name

from P0Config import P0Config


class P1Test(object):
    """
        Test basic operations over a tiny graph.
        Use this ONLY for empty databases, as it will 
        clear the data before and after execution!
    """

    def __init__(self):
        self.conf = P0Config.shared()
        self.docs = [
            TextFile('1', 'the big brown fox').__dict__,
            TextFile('2', 'as.the.day;passes').__dict__,
            TextFile('3', 'along the:way').__dict__,
        ]

    def run(self):
        for db in self.conf.databases:
            g = self.conf.make_db(
                database=db, dataset=self.conf.test_dataset)
            if g is None:
                continue
            self.run_one(g)

    def run_one(self, g):
        print(f'-- Starting testing of: {class_name(g)}')

        print(f'--- Cleaning')
        g.remove_all()
        self.validate_empty(g)

        print(f'--- Single Operations')
        for e in self.edges:
            g.upsert_edge(e)
        self.validate_contents(g)
        for e in self.edges:
            g.remove_edge(e)
        self.validate_empty(g)

        print(f'--- Batch Operations')
        g.upsert_edges(self.edges)
        self.validate_contents(g)
        g.remove_edges(self.edges)
        self.validate_empty(g)

        # print(f'--- Bulk Insert')
        # g.insert_adjacency_list(self.conf.test_dataset['path'])
        # self.validate_contents(g)
        # g.remove_all()
        # self.validate_empty(g)

        print(f'--- Passed All!')

    def validate_empty(self, g):
        assert g.count_docs() == 0, \
            f'count_docs() must be =0: {g.count_docs()}'

    def validate_contents(self, g):
        for e in self.edges:
            assert g.edge_directed(e['v1'], e['v2']), \
                f'No directed edge: {e}'
            assert g.edge_undirected(e['v1'], e['v2']), \
                f'No undirected edge: {e}'

        assert g.count_docs() == 10, \
            f'count_docs: {g.count_docs()}'
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


if __name__ == "__main__":
    P1Test().run()
