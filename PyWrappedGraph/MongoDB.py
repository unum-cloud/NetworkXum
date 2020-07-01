from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence

# Properties of every entry are: 'from_id', 'to_id', 'weight'
# There are indexes by all keys.
import pymongo
from pymongo import MongoClient
from pymongo import UpdateOne

from PyWrappedGraph.BaseAPI import BaseAPI
from PyWrappedHelpers.Algorithms import *


class MongoDB(BaseAPI):
    __max_batch_size__ = 1000
    __is_concurrent__ = True
    __edge_type__ = dict

    def __init__(self, url='mongodb://localhost:27017/graph', **kwargs):
        BaseAPI.__init__(self, **kwargs)
        _, db_name = extract_database_name(url)
        self.db = MongoClient(url)
        self.edges = self.db[db_name]['edges']
        self.nodes = self.db[db_name]['nodes']
        self.create_index()

    def create_index(self, background=False):
        self.edges.create_index('v1', background=background, sparse=True)
        self.edges.create_index('v2', background=background, sparse=True)
        self.edges.create_index('directed', background=background, sparse=True)

    # Relatives

    def edge_directed(self, v1: int, v2: int) -> Optional[object]:
        result = self.edges.find_one(filter={
            'v1': v1,
            'v2': v2,
            'directed': True,
        })
        return result

    def edge_undirected(self, v1: int, v2: int) -> Optional[object]:
        result = self.edges.find_one(filter={
            '$or': [{
                'v1': v1,
                'v2': v2,
            }, {
                'v1': v2,
                'v2': v1,
            }],
        })
        return result

    def edges_from(self, v: int) -> List[object]:
        result = self.edges.find(filter={'v1': v, 'directed': True})
        return list(result)

    def edges_to(self, v: int) -> List[object]:
        result = self.edges.find(filter={'v2': v, 'directed': True})
        return list(result)

    def edges_related(self, v: int) -> List[object]:
        result = self.edges.find(filter={
            '$or': [{
                'v1': v,
            }, {
                'v2': v,
            }],
        })
        return list(result)

    # Wider range of neighbors

    def nodes_related_to_group(self, vs: Sequence[int]) -> Set[int]:
        vs = list(vs)
        result = self.edges.find(filter={
            '$or': [{
                'v1': {'$in': vs},
            }, {
                'v2': {'$in': vs},
            }],
        }, projection={
            'v1': 1,
            'v2': 1,
        })
        vs_unique = set()
        for e in result:
            vs_unique.add(e['v1'])
            vs_unique.add(e['v2'])
        return vs_unique.difference(set(vs))

    # Metadata

    def count_nodes(self) -> int:
        froms = set(self.edges.distinct('v1'))
        tos = set(self.edges.distinct('v2'))
        attributed = set(self.nodes.distinct('_id'))
        return len(froms.union(tos).union(attributed))

    def count_edges(self) -> int:
        return self.edges.count_documents(filter={})

    def count_related(self, v: int) -> (int, float):
        result = self.edges.aggregate(pipeline=[
            {
                '$match': {
                    '$or': [
                        {'v1': v},
                        {'v2': v}
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
                    'v2': v,
                    'directed': True
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
                    'v1': v,
                    'directed': True
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

    def validate_edge(self, e: object) -> object:
        if not isinstance(e, dict):
            e = e.__dict__
        return super().validate_edge(e)

    def upsert_edge(self, e: object) -> bool:
        e = self.validate_edge(e)
        if e is None:
            return False
        if '_id' in e:
            result = self.edges.update_one(
                filter={'_id': e['_id'], },
                update={'$set': e, },
                upsert=True,
            )
        else:
            result = self.edges.update_one(
                filter={
                    'v1': e['v1'],
                    'v2': e['v2'],
                },
                update={'$set': e, },
                upsert=True,
            )
        return result.modified_count >= 1

    def remove_edge(self, e: object) -> bool:
        result = self.edges.delete_one(filter={
            'v1': e['v1'],
            'v2': e['v2'],
            'directed': e['directed'],
        })
        return result.deleted_count >= 1

    def remove_node(self, v: int) -> int:
        result = self.edges.delete_many(filter={
            '$or': [
                {'v1': v},
                {'v2': v},
            ]
        })
        return result.deleted_count >= 1

    def remove_all(self):
        self.edges.drop()

    def upsert_edges(self, es: List[object]) -> int:
        """Supports up to 1000 operations"""
        es = map_compact(self.validate_edge, es)
        es = remove_duplicate_edges(es)
        es = list(es)
        if len(es) == 0:
            return 0

        def make_upsert(e):
            filters = {}
            if '_id' in e:
                filters['_id'] = e['_id']
            else:
                filters['v1'] = e['v1']
                filters['v2'] = e['v2']
                filters['directed'] = e['directed']

            return UpdateOne(
                filter=filters,
                update={
                    '$set': e
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

    def insert_edges(self, es: List[object]) -> int:
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
