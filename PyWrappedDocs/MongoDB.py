from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence

import pymongo
from pymongo import MongoClient
from pymongo import UpdateOne, DeleteOne

from PyWrappedDocs.BaseAPI import BaseAPI
from PyWrappedHelpers.Algorithms import *
from PyWrappedHelpers.TextFile import TextFile


class MongoDB(BaseAPI):
    __max_batch_size__ = 1000
    __is_concurrent__ = True

    def __init__(self, url='mongodb://localhost:27017/texts', **kwargs):
        BaseAPI.__init__(self, **kwargs)
        _, db_name = extract_database_name(url)
        self.db = MongoClient(url)
        self.docs_collection = self.db[db_name]['docs']
        self.create_indexes()

    def create_indexes(self):
        for field in self.indexed_fields:
            self.create_index(field)
        # As MongoDB can't search in a specific index,
        # we can create a generic index for all fields.
        # self.create_index_for_all_strings()

    def create_index(self, field: str, background=False):
        self.docs_collection.create_index(
            [(field, pymongo.TEXT)],
            background=background,
        )

    def create_index_for_all_strings(self, background=False):
        # https://docs.mongodb.com/manual/core/index-text/#wildcard-text-indexes
        self.docs_collection.create_index(
            {'$**': 'text'},
            background=background,
        )

    def count_docs(self) -> int:
        return self.docs_collection.count_documents(filter={})

    def remove_all(self):
        self.docs_collection.drop()
        self.create_indexes()

    def find_with_id(self, query: str) -> object:
        return self.docs_collection.find_one(filter={
            '_id': query if isinstance(query, (str, int)) else query['_id'],
        })

    def find_with_substring(
        self,
        query: str,
        field: str = 'plain',
        max_matches: int = None,
    ) -> Sequence[str]:
        """
            CAUTION: Seems like MongoDB doesn't support text search limited 
            to a specific field, so it's inapplicable to more complex cases.
        """
        # https://docs.mongodb.com/manual/reference/operator/query/text/
        # https://docs.mongodb.com/manual/core/index-text/
        # https://docs.mongodb.com/manual/reference/text-search-languages/#text-search-languages
        dicts = self.docs_collection.find(filter={
            '$text': {
                '$search': f'\"{query}\"',
                '$caseSensitive': True,
                '$diacriticSensitive': False,
            },
        }, projection=['_id'])
        if max_matches is not None:
            dicts = dicts.limit(max_matches)
        return [d['_id'] for d in dicts]

    def find_with_regex(
        self,
        query: str,
        field: str = 'plain',
        max_matches: int = None,
    ) -> Sequence[str]:

        # https://docs.mongodb.com/manual/reference/operator/query/regex/
        dicts = self.docs_collection.find(filter={
            field: {
                '$regex': query,
                '$options': 'm',
            },
        }, projection=['_id'])
        if max_matches is not None:
            dicts = dicts.limit(max_matches)
        return [d['_id'] for d in dicts]

    def validate_doc(self, doc: object) -> dict:
        if isinstance(doc, dict):
            return doc
        if isinstance(doc, TextFile):
            return doc.to_dict()
        return doc.__dict__

    def upsert_doc(self, doc: object) -> bool:
        doc = self.validate_doc(doc)
        result = self.docs_collection.update_one(
            filter={'_id': doc['_id'], },
            update={'$set': doc, },
            upsert=True,
        )
        return (result.modified_count >= 1) or (result.upserted_id is not None)

    def remove_doc(self, doc: object) -> bool:
        doc = self.validate_doc(doc)
        result = self.docs_collection.delete_one(filter={'_id': doc['_id'], })
        return result.deleted_count >= 1

    def upsert_docs(self, docs: List[object]) -> int:
        """
            Supports up to 1000 updates per batch.
            https://api.mongodb.com/python/current/examples/bulk.html#ordered-bulk-write-operations
        """
        def make_upsert(doc):
            return UpdateOne(
                filter={'_id': doc['_id'], },
                update={'$set': doc, },
                upsert=True,
            )

        docs = map(self.validate_doc, docs)
        ops = list(map(make_upsert, docs))
        try:
            result = self.docs_collection.bulk_write(
                requests=ops, ordered=False)
            return result.bulk_api_result['nUpserted'] + result.bulk_api_result['nInserted']
        except pymongo.errors.BulkWriteError as bwe:
            print(bwe)
            print(bwe.details['writeErrors'])
            return 0

    def remove_docs(self, docs: List[object]) -> int:
        """
            Supports up to 1000 updates per batch.
            https://api.mongodb.com/python/current/examples/bulk.html#ordered-bulk-write-operations
        """
        def make_upsert(doc):
            return DeleteOne(
                filter={'_id': doc['_id'], },
            )

        docs = map(self.validate_doc, docs)
        ops = list(map(make_upsert, docs))
        try:
            result = self.docs_collection.bulk_write(
                requests=ops, ordered=False)
            return result.bulk_api_result['nUpserted'] + result.bulk_api_result['nInserted']
        except pymongo.errors.BulkWriteError as bwe:
            print(bwe)
            print(bwe.details['writeErrors'])
            return 0


if __name__ == '__main__':
    sample_file = 'Datasets/TextTest/nanoformulations.txt'
    db = MongoDB(url='mongodb://localhost:27017/SingleTextTest')
    db.remove_all()
    assert db.count_docs() == 0
    assert db.upsert_doc(TextFile(sample_file).to_dict())
    assert db.count_docs() == 1
    assert db.find_with_substring('Atripla-trimethyl')
    assert db.find_with_regex('Atripla-trimeth[a-z]{2}')
    # assert db.remove_doc(TextFile(sample_file).to_dict())
    # assert db.count_docs() == 0
