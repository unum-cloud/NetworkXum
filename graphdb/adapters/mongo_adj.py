# Properties of every entry are: 'from_id', 'to_id', 'weight'
# There are indexes by all keys.
from pymongo import MongoClient
from pymongo import UpdateOne

from shared import *


class GraphMongoAdjacency(GraphBase):

    def __init__(self, url, db_name, collection_name):
        super().__init__()
        self.db = MongoClient(url)
        self.table = self.db[db_name][collection_name]

    def create_index(self, background=False):
        self.table.create_index('from', background=background, sparse=True)
        self.table.create_index('to', background=background, sparse=True)

    def insert(self, e: object) -> bool:
        result = self.table.update_one(
            filter={
                'from': e['from'],
                'to': e['to'],
            },
            update=e,
            upsert=True,
        )
        return result.modified_count >= 1

    def delete(self, e: object) -> bool:
        result = self.table.delete_one(filter={
            'from': e['from'],
            'to': e['to'],
        })
        return result.deleted_count >= 1

    def edge_directed(self, v_from, v_to) -> Optional[object]:
        result = self.table.find_one(filter={
            'from': v_from,
            'to': v_to,
        })
        return result

    def edge_undirected(self, v1, v2) -> Optional[object]:
        result = self.table.find_one(filter={
            '$or': [{
                'from': v1,
                'to': v2,
            }, {
                'from': v2,
                'to': v1,
            }],
        })
        return result

    # Relatives

    def edges_from(self, v: int) -> List[object]:
        result = self.table.find(filter={'from': v})
        return list(result)

    def edges_to(self, v: int) -> List[object]:
        result = self.table.find(filter={'to': v})
        return list(result)

    def edges_friends(self, v: int) -> List[object]:
        result = self.table.find(filter={
            '$or': [{
                'from': v,
            }, {
                'to': v,
            }],
        })
        return list(result)

    def vertexes_friends(self, v: int) -> Set[int]:
        vs_unique = set()
        for e in self.edges_friends(v):
            vs_unique.insert(e['from'])
            vs_unique.insert(e['to'])
        vs_unique.remove(v)
        return vs_unique

    # Wider range of neighbours

    def vertexes_friends_of_friends(self, v: int) -> Set[int]:
        pass

    def vertexes_friends_of_group(self, vs) -> Set[int]:
        pass

    # Metadata

    def count_degree(self, v: int) -> (int, float):
        result = self.table.aggregate(pipeline=[
            {
                '$match': {
                    '$or': [
                        {'from': v},
                        {'to': v}
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
        return result['count'], result['weight']

    def count_followers(self, v: int) -> (int, float):
        result = self.table.aggregate(pipeline=[
            {
                '$match': {'to': v}
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
        return result['count'], result['weight']

    def count_following(self, v: int) -> (int, float):
        result = self.table.aggregate(pipeline=[
            {
                '$match': {'from': v}
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
        return result['count'], result['weight']

    # Bulk methods

    def insert_many(self, es: List[object]) -> int:
        '''Supports up to 1000 operations'''
        ops = list()
        for e in es:
            op = UpdateOne(
                filter={
                    'from': e['from'],
                    'to': e['to'],
                },
                update=e,
                upsert=True,
            )
            ops.append(op)
        result = table.bulk_write(requests=ops, ordered=False)
        return int(result.bulk_api_result['upserted'])

    def import_file(self, filepath: str):
        for es in chunks(yield_edges_from(filepath), 1000):
            self.insert_many(list(es))
