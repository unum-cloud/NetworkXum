from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence

# Properties of every entry are: 'from_id', 'to_id', 'weight'
# There are indexes by all keys.
from pymongo import MongoClient
from pymongo import UpdateOne

from pygraphdb.edge import Edge
from pygraphdb.graph_base import GraphBase
from helpers.shared import chunks, yield_edges_from


class MongoDB(GraphBase):

    def __init__(self, url, db_name, collection_name):
        super().__init__()
        self.db = MongoClient(url)
        self.table = self.db[db_name][collection_name]
        self.create_index()

    def create_index(self, background=False):
        self.table.create_index('v_from', background=background, sparse=True)
        self.table.create_index('v_to', background=background, sparse=True)

    # Relatives

    def edge_directed(self, v_from: int, v_to: int) -> Optional[object]:
        result = self.table.find_one(filter={
            'v_from': v_from,
            'v_to': v_to,
        })
        return result

    def edge_undirected(self, v1: int, v2: int) -> Optional[object]:
        result = self.table.find_one(filter={
            '$or': [{
                'v_from': v1,
                'v_to': v2,
            }, {
                'v_from': v2,
                'v_to': v1,
            }],
        })
        return result

    def edges_from(self, v: int) -> List[object]:
        result = self.table.find(filter={'v_from': v})
        return list(result)

    def edges_to(self, v: int) -> List[object]:
        result = self.table.find(filter={'v_to': v})
        return list(result)

    def edges_related(self, v: int) -> List[object]:
        result = self.table.find(filter={
            '$or': [{
                'v_from': v,
            }, {
                'v_to': v,
            }],
        })
        return list(result)

    # Wider range of neighbours

    def vertexes_related_to_group(self, vs: Sequence[int]) -> Set[int]:
        vs = list(vs)
        result = self.table.find(filter={
            '$or': [{
                'v_from': {'$in': vs},
            }, {
                'v_to': {'$in': vs},
            }],
        }, projection={
            'v_from': 1,
            'v_to': 1,
        })
        vs_unique = set()
        for e in result:
            vs_unique.add(e['v_from'])
            vs_unique.add(e['v_to'])
        return vs_unique.difference(set(vs))

    # Metadata

    def count_vertexes(self) -> int:
        froms = set(self.table.distinct('v_from'))
        tos = set(self.table.distinct('v_to'))
        return len(froms.union(tos))

    def count_edges(self) -> int:
        return self.table.count_documents(filter={})

    def count_related(self, v: int) -> (int, float):
        result = self.table.aggregate(pipeline=[
            {
                '$match': {
                    '$or': [
                        {'v_from': v},
                        {'v_to': v}
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
        result = self.table.aggregate(pipeline=[
            {
                '$match': {'v_to': v}
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
        result = self.table.aggregate(pipeline=[
            {
                '$match': {'v_from': v}
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

    # Modifications

    def insert(self, e: Edge) -> bool:
        result = self.table.update_one(
            filter={
                'v_from': e['v_from'],
                'v_to': e['v_to'],
            },
            update={
                '$set': e.__dict__,
            },
            upsert=True,
        )
        return result.modified_count >= 1

    def delete(self, e: object) -> bool:
        result = self.table.delete_one(filter={
            'v_from': e['v_from'],
            'v_to': e['v_to'],
        })
        return result.deleted_count >= 1

    def delete_many(self, es: List[object]) -> int:
        pass

    def insert_many(self, es: List[object]) -> int:
        """Supports up to 1000 operations"""
        ops = list()
        for e in es:
            op = UpdateOne(
                filter={
                    'v_from': e['v_from'],
                    'v_to': e['v_to'],
                },
                update=e.__dict__,
                upsert=True,
            )
            ops.append(op)
        result = table.bulk_write(requests=ops, ordered=False)
        return int(result.bulk_api_result['upserted'])

    def import_file(self, filepath: str):
        for es in chunks(yield_edges_from(filepath), 1000):
            self.insert_many(list(es))
