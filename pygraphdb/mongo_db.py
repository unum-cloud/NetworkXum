from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence
from urllib.parse import urlparse

# Properties of every entry are: 'from_id', 'to_id', 'weight'
# There are indexes by all keys.
from pymongo import MongoClient
from pymongo import UpdateOne

from pygraphdb.edge import Edge
from pygraphdb.graph_base import GraphBase


class MongoDB(GraphBase):

    def __init__(self, url, db_name=None):
        super().__init__()
        # Extract database name and collection name if nothing was provided.
        if (db_name is None):
            url_parts = urlparse(url).path
            url_parts = url_parts.split('/')
            url_parts = [v for v in url_parts if (v != '/' and v != '')]
            if len(url_parts) >= 1:
                db_name = url_parts[0]
            else:
                db_name = 'graph'
            if len(url_parts) > 1:
                print('Will avoid remaining url parts:', url_parts[2:])
        self.db = MongoClient(url)
        self.edges = self.db[db_name]['edges']
        self.nodes = self.db[db_name]['nodes']
        self.create_index()

    def create_index(self, background=False):
        self.edges.create_index('v_from', background=background, sparse=True)
        self.edges.create_index('v_to', background=background, sparse=True)

    # Relatives

    def find_edge(self, v_from: int, v_to: int) -> Optional[object]:
        result = self.edges.find_one(filter={
            'v_from': v_from,
            'v_to': v_to,
        })
        return result

    def find_edge_or_inv(self, v1: int, v2: int) -> Optional[object]:
        result = self.edges.find_one(filter={
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
        result = self.edges.find(filter={'v_from': v})
        return list(result)

    def edges_to(self, v: int) -> List[object]:
        result = self.edges.find(filter={'v_to': v})
        return list(result)

    def edges_related(self, v: int) -> List[object]:
        result = self.edges.find(filter={
            '$or': [{
                'v_from': v,
            }, {
                'v_to': v,
            }],
        })
        return list(result)

    # Wider range of neighbors

    def nodes_related_to_group(self, vs: Sequence[int]) -> Set[int]:
        vs = list(vs)
        result = self.edges.find(filter={
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

    def count_nodes(self) -> int:
        froms = set(self.edges.distinct('v_from'))
        tos = set(self.edges.distinct('v_to'))
        attributed = set(self.nodes.distinct('_id'))
        return len(froms.union(tos).union(attributed))

    def count_edges(self) -> int:
        return self.edges.count_documents(filter={})

    def count_related(self, v: int) -> (int, float):
        result = self.edges.aggregate(pipeline=[
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
        result = self.edges.aggregate(pipeline=[
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
        result = self.edges.aggregate(pipeline=[
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

    def insert_edge(self, e: Edge) -> bool:
        if not isinstance(e, dict):
            e = e.__dict__
        result = self.edges.update_one(
            filter={
                'v_from': e['v_from'],
                'v_to': e['v_to'],
            },
            update={
                '$set': e,
            },
            upsert=True,
        )
        return result.modified_count >= 1

    def remove_edge(self, e: object) -> bool:
        result = self.edges.delete_one(filter={
            'v_from': e['v_from'],
            'v_to': e['v_to'],
        })
        return result.deleted_count >= 1

    def remove_node(self, v: int) -> int:
        result = self.edges.delete_many(filter={
            '$or': [
                {'v_from': v},
                {'v_to': v},
            ]
        })
        return result.deleted_count >= 1

    def remove_all(self):
        self.edges.drop()

    def insert_edges(self, es: List[object]) -> int:
        """Supports up to 1000 operations"""
        ops = list()
        for e in es:
            if not isinstance(e, dict):
                e = e.__dict__
            op = UpdateOne(
                filter={
                    '_id': e['_id'],
                    'v_from': e['v_from'],
                    'v_to': e['v_to'],
                },
                update={
                    '$set': e
                },
                upsert=True,
            )
            ops.append(op)
        result = self.edges.bulk_write(requests=ops, ordered=False)
        return len(result.bulk_api_result['upserted'])
