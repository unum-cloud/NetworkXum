from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence

# Properties of every entry are: 'from_id', 'to_id', 'weight'
# There are indexes by all keys.
import pymongo
from pymongo import MongoClient
from pymongo import UpdateOne

from PyWrappedGraph.BaseAPI import BaseAPI
from PyWrappedHelpers.Algorithms import *


class MongoDB(BaseAPI):
    """
        MongoDB until second.6 had 1'000 element limit for the batch size.
        It was later pushed to 100'000, but there isn't much improvement 
        beyond this point and not every document is small enough to fit 
        in RAM with such batch sizes.
        https://stackoverflow.com/q/51250036/2766161
        https://docs.mongodb.com/manual/reference/limits/#Write-Command-Batch-Limit-Size
    """
    __max_batch_size__ = 10000
    __is_concurrent__ = True
    __edge_type__ = Edge

    def __init__(self, url='mongodb://localhost:27017/graph', **kwargs):
        BaseAPI.__init__(self, **kwargs)
        _, db_name = extract_database_name(url)
        self.db = MongoClient(url)
        self.edges = self.db[db_name]['edges']
        self.nodes = self.db[db_name]['nodes']
        self.create_index()

    def create_index(self, background=False):
        self.edges.create_index('first', background=background, sparse=True)
        self.edges.create_index('second', background=background, sparse=True)
        self.edges.create_index(
            'is_directed', background=background, sparse=True)

    # Relatives

    def edge_directed(self, first: int, second: int) -> Optional[Edge]:
        result = self.edges.find_one(filter={
            'first': first,
            'second': second,
            'is_directed': True,
        })
        return self.validate_edge(result)

    def edge_undirected(self, first: int, second: int) -> Optional[Edge]:
        result = self.edges.find_one(filter={
            '$or': [{
                'first': first,
                'second': second,
            }, {
                'first': second,
                'second': first,
            }],
        })
        return self.validate_edge(result)

    def edges_from(self, v: int) -> List[Edge]:
        result = self.edges.find(filter={'first': v, 'is_directed': True})
        return list(map_compact(self.validate_edge, result))

    def edges_to(self, v: int) -> List[Edge]:
        result = self.edges.find(filter={'second': v, 'is_directed': True})
        return list(map_compact(self.validate_edge, result))

    def edges_related(self, v: int) -> List[Edge]:
        result = self.edges.find(filter={
            '$or': [{
                'first': v,
            }, {
                'second': v,
            }],
        })
        return list(map_compact(self.validate_edge, result))

    # Wider range of neighbors

    def nodes_related_to_group(self, vs: Sequence[int]) -> Set[int]:
        vs = list(vs)
        result = self.edges.find(filter={
            '$or': [{
                'first': {'$in': vs},
            }, {
                'second': {'$in': vs},
            }],
        }, projection={
            'first': 1,
            'second': 1,
        })
        vs_unique = set()
        for e in map_compact(self.validate_edge, result):
            vs_unique.add(e.first)
            vs_unique.add(e.second)
        return vs_unique.difference(set(vs))

    # Metadata

    def count_nodes(self) -> int:
        froms = set(self.edges.distinct('first'))
        tos = set(self.edges.distinct('second'))
        attributed = set(self.nodes.distinct('_id'))
        return len(froms.union(tos).union(attributed))

    def count_edges(self) -> int:
        return self.edges.count_documents(filter={})

    def count_related(self, v: int) -> (int, float):
        result = self.edges.aggregate(pipeline=[
            {
                '$match': {
                    '$or': [
                        {'first': v},
                        {'second': v}
                    ],
                }
            },
            {
                '$group': {
                    '_id': None,
                    'count': {'$sum': 1},
                    'weight': {'$sum': '$weight'},
                }
            }
        ])
        result = list(result)
        if len(result) == 0:
            return 0, 0
        return result[0]['count'], result[0]['weight']

    def count_followers(self, v: int) -> (int, float):
        result = self.edges.aggregate(pipeline=[
            {
                '$match': {
                    'second': v,
                    'is_directed': True
                }
            },
            {
                '$group': {
                    '_id': None,
                    'count': {'$sum': 1},
                    'weight': {'$sum': '$weight'},
                }
            }
        ])
        result = list(result)
        if len(result) == 0:
            return 0, 0
        return result[0]['count'], result[0]['weight']

    def count_following(self, v: int) -> (int, float):
        result = self.edges.aggregate(pipeline=[
            {
                '$match': {
                    'first': v,
                    'is_directed': True
                }
            },
            {
                '$group': {
                    '_id': None,
                    'count': {'$sum': 1},
                    'weight': {'$sum': '$weight'},
                }
            }
        ])
        result = list(result)
        if len(result) == 0:
            return 0, 0
        return result[0]['count'], result[0]['weight']

    def biggest_edge_id(self) -> int:
        result = self.edges.find(
            {},
            sort=[('_id', pymongo.DESCENDING)],
        ).limit(1)
        result = list(result)
        if len(result) == 0:
            return 0
        return int(result[0]['_id'])

    # Modifications

    def upsert_edge(self, e: Edge) -> bool:
        e = self.validate_edge(e)
        if e is None:
            return False
        if e._id < 0:
            result = self.edges.update_one(
                filter={
                    'first': e.first,
                    'second': e.second,
                },
                update={'$set': e.__dict__, },
                upsert=True,
            )
        else:
            result = self.edges.update_one(
                filter={'_id': e._id, },
                update={'$set': e.__dict__, },
                upsert=True,
            )
        return result.modified_count >= 1

    def remove_edge(self, e: Edge) -> bool:
        result = self.edges.delete_one(filter={
            'first': e.first,
            'second': e.second,
            'is_directed': e.is_directed,
        })
        return result.deleted_count >= 1

    def remove_node(self, v: int) -> int:
        result = self.edges.delete_many(filter={
            '$or': [
                {'first': v},
                {'second': v},
            ]
        })
        return result.deleted_count >= 1

    def remove_all(self):
        self.edges.drop()

    def upsert_edges(self, es: List[Edge]) -> int:
        """Supports up to 1000 operations"""
        es = map_compact(self.validate_edge, es)
        es = remove_duplicate_edges(es)
        es = list(es)
        if len(es) == 0:
            return 0

        def make_upsert(e):
            filters = {}
            if e._id < 0:
                filters['first'] = e.first
                filters['second'] = e.second
                filters['is_directed'] = e.is_directed
            else:
                filters['_id'] = e._id

            return UpdateOne(
                filter=filters,
                update={
                    '$set': e.__dict__
                },
                upsert=True,
            )
        ops = list(map(make_upsert, es))
        try:
            result = self.edges.bulk_write(requests=ops, ordered=False)
            return result.bulk_api_result['nUpserted'] + result.bulk_api_result['nInserted']
        except pymongo.errors.BulkWriteError as bwe:
            print(bwe)
            print(bwe.details['writeErrors'])
            return 0

    def insert_edges(self, es: List[Edge]) -> int:
        try:
            es = map_compact(self.validate_edge, es)
            es = remove_duplicate_edges(es)
            result = self.edges.insert_many(es, ordered=False)
            return len(result.inserted_ids)
        except pymongo.errors.BulkWriteError as bwe:
            print(bwe)
            print(bwe.details['writeErrors'])
            return 0

    # def upsert_adjacency_list(self, filepath: str) -> int:
    #     return export_edges_into_graph(filepath, self)
