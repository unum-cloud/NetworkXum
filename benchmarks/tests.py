
from pygraphdb.edge import Edge
from pygraphdb.graph_base import GraphBase
from pygraphdb.plain_sql import PlainSQL
from pygraphdb.mongo_db import MongoDB
from pygraphdb.neo4j import Neo4j


def validate(wrap):
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
    # Fill the DB.
    es_last = 0
    vs_last = 0
    for e in edges:
        wrap.insert(e)
        assert wrap.edge_directed(e['v_from'], e['v_to']), \
            f'No directed edge: {e}'
        assert wrap.edge_undirected(e['v_from'], e['v_to']), \
            f'No undirected edge: {e}'
        # Make sure the size of the DB isn't getting smaller.
        # It may remain unchanged for persistent stores.
        es_count = wrap.count_edges()
        assert es_count >= es_last, 'Didnt update number of edges'
        es_last = es_count
        vs_count = wrap.count_vertexes()
        assert vs_count >= vs_last, 'Problems in counting nodes'
        vs_last = vs_count
    # Validate the queries.
    assert vs_last == 8, \
        f'count_nodes: {vs_last}'
    assert es_last == 10, \
        f'count_edges: {es_last}'
    assert wrap.count_followers(1) == (3, 10.0), \
        f'count_followers: {wrap.count_followers(1)}'
    assert wrap.count_following(1) == (1, 4.0), \
        f'count_following: {wrap.count_following(1)}'
    assert wrap.count_related(1) == (4, 14.0), \
        f'count_related: {wrap.count_related(1)}'
    assert wrap.vertexes_related(1) == {2, 4, 6, 7}, \
        f'vertexes_related: {wrap.vertexes_related(1)}'
    assert wrap.vertexes_related_to_related(8) == {1}, \
        f'vertexes_related_to_related: {wrap.vertexes_related_to_related(8)}'
    assert wrap.count_followers(5) == (1, 3.0), \
        f'count_followers: {wrap.count_followers(5)}'
    assert wrap.count_following(5) == (1, 2.0), \
        f'count_following: {wrap.count_following(5)}'
    # Clear the DB.


if __name__ == "__main__":
    for g in [
        PlainSQL(url='mysql://root:temptemp@0.0.0.0:3306/mysql'),
        PlainSQL(),
        PlainSQL(url='postgres://root:temptemp@0.0.0.0:5432'),
        Neo4j(url='bolt://0.0.0.0:7687', enterprise_edition=False),
        MongoDB(
            url='mongodb://0.0.0.0:27017',
            db_name='graphdb',
            collection_name='tests',
        ),
    ]:
        try:
            validate(g)
        except Exception as e:
            print(f'Failed for {g}: {str(e)}')
