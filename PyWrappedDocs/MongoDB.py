from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence

import pymongo
from pymongo import MongoClient
from pymongo import UpdateOne

from PyWrappedDocs.BaseAPI import BaseAPI
from PyWrappedGraph.Algorithms import *


class MongoDB(BaseAPI):
    __max_batch_size__ = 1000
    __is_concurrent__ = True
    __edge_type__ = dict

    def __init__(self, url='mongodb://localhost:27017/graph', **kwargs):
        BaseAPI.__init__(self, **kwargs)
        db_name = extract_database_name(url)
        self.db = MongoClient(url)
        self.docs_collection = self.db[db_name]['docs']
        for field in self.indexed_fields:
            self.create_index(field)

    def create_index(self, field:str, background=False):
        self.docs_collection.create_index({field: 'text'}, background=background, sparse=True)

    def create_index_for_all_strings(self, background=False):
        self.docs_collection.create_index({'$**': 'text'}, background=background, sparse=True)

    def count_docs(self) -> int:
        return self.docs_collection.count_documents(filter={})

    def remove_all(self):
        self.docs_collection.drop()

    def find_substring(self, field: str, query: str) -> Sequence[object]:
        # https://docs.mongodb.com/manual/reference/operator/query/text/
        # https://docs.mongodb.com/manual/core/index-text/
        # https://docs.mongodb.com/manual/reference/text-search-languages/#text-search-languages
        return self.docs_collection.find(filter={
            field: {
                '$text': {
                    '$search': query,
                    '$language': 'en',
                    '$caseSensitive': True,
                    '$diacriticSensitive': False,
                }
            },
        })

    def find_regex(self, field: str, query: str) -> Sequence[object]:
        # https://docs.mongodb.com/manual/reference/operator/query/regex/
        return self.docs_collection.find(filter={
            field: {
                '$regex': query,
                '$options': 'm',
            },
        })

    def upsert_doc(self, doc: object) -> bool:
        result = self.docs_collection.update_one(
            filter={'_id': doc['_id'], },
            update={'$set': doc, },
            upsert=True,
        )
        return result.modified_count >= 1

    def remove_doc(self, doc: object) -> bool:
        result = self.docs_collection.delete_one(filter={'_id': doc['_id'], })
        return result.deleted_count >= 1

    def upsert_docs(self, docs: List[object]) -> int:
        """Supports up to 1000 updates per batch"""
        docs = list(docs)
        if len(docs) == 0:
            return 0

        def make_upsert(doc):
            return UpdateOne(
                filter={'_id': doc['_id'], },
                update={'$set': doc, },
                upsert=True,
            )
        ops = list(map(make_upsert, docs))
        try:
            result = self.docs_collection.bulk_write(requests=ops, ordered=False)
            return len(result.bulk_api_result['upserted'])
        except pymongo.errors.BulkWriteError as bwe:
            print(bwe)
            print(bwe.details['writeErrors'])
            return 0
