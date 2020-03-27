
from adapters.base import GraphBase
from adapters.sql import *
from adapters.mongo_adj import *


def validate(wrap):
    edges = [
        {'v_from': 1, 'v_to': 2, 'weight': 4},
        {'v_from': 2, 'v_to': 3, 'weight': 20},
        {'v_from': 3, 'v_to': 4, 'weight': 10},
        {'v_from': 4, 'v_to': 5, 'weight': 3},
        {'v_from': 5, 'v_to': 3, 'weight': 2},
        {'v_from': 4, 'v_to': 1, 'weight': 5},
        {'v_from': 8, 'v_to': 6, 'weight': 4},
        {'v_from': 8, 'v_to': 7, 'weight': 2},
        {'v_from': 6, 'v_to': 1, 'weight': 3},
        {'v_from': 7, 'v_to': 1, 'weight': 2},
    ]
    es_last = 0
    vs_last = 0
    for e in edges:
        wrap.insert(e)
        assert wrap.find_directed(
            e['v_from'], e['v_to']), f'No directed edge: {e}'
        assert wrap.find_undirected(
            e['v_from'], e['v_to']), f'No undirected edge: {e}'
        es_count = wrap.count_edges()
        assert es_count >= es_last, 'Didnt update number of edges'
        es_last = es_count
        vs_count = wrap.count_vertexes()
        assert vs_count >= vs_last, 'Problems in counting nodes'
        vs_last = vs_count

    assert vs_last == 8, 'Wrong number of nodes!'
    assert es_last == 10, 'Wrong number of edges!'
    assert wrap.count_followers(1) == (3, 10.0)
    assert wrap.count_following(1) == (1, 4.0)
    assert wrap.count_related(1) == (4, 14.0)
    assert wrap.vertexes_related(1) == {2, 4, 6, 7}
    assert wrap.vertexes_related_to_related(8) == {1, 6, 7}
    assert wrap.count_followers(5) == (1, 3.0)
    assert wrap.count_following(5) == (1, 2.0)


if __name__ == "__main__":
    for g in [
        GraphSQL(),
        GraphMongoAdjacency(
            url='mongodb://localhost:27017',
            db_name='graphdb',
            collection_name='tests',
        ),
    ]:
        validate(g)
