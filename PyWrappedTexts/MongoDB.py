from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence

import pymongo
from pymongo import MongoClient
from pymongo import UpdateOne, DeleteOne

from PyWrappedTexts.BaseAPI import BaseAPI
from PyWrappedHelpers import *


class MongoDB(BaseAPI):
    """
        MongoDB until v2.6 had 1'000 element limit for the batch size.
        It was later pushed to 100'000, but there isn't much improvement 
        beyond this point and not every document is small enough to fit 
        in RAM with such batch sizes.
        https://stackoverflow.com/q/51250036/2766161
        https://docs.mongodb.com/manual/reference/limits/#Write-Command-Batch-Limit-Size
    """
    __max_batch_size__ = 10000
    __is_concurrent__ = True

# region Metadata

    def __init__(self, url='mongodb://localhost:27017/texts', **kwargs):
        BaseAPI.__init__(self, **kwargs)
        _, db_name = extract_database_name(url)
        self.db = MongoClient(url)
        self.docs_collection = self.db[db_name]['docs']
        self.create_indexes()

    def count_texts(self) -> int:
        return self.docs_collection.count_documents(filter={})

# region Random Reads

    def find_with_id(self, query: int) -> Optional[Text]:
        return self.docs_collection.find_one(filter={
            '_id': query
        })

    def find_with_substring(
        self,
        query: str,
        field: str = 'content',
        max_matches: int = None,
    ) -> Sequence[TextMatch]:
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
        field: str = 'content',
        max_matches: int = None,
    ) -> Sequence[TextMatch]:

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

# region Random Writes

    def upsert_text(self, doc: Text) -> bool:
        doc = self.validate_text(doc)
        result = self.docs_collection.update_one(
            filter={'_id': doc['_id'], },
            update={'$set': doc, },
            upsert=True,
        )
        return (result.modified_count >= 1) or (result.upserted_id is not None)

    def remove_text(self, doc: Text) -> bool:
        doc = self.validate_text(doc)
        result = self.docs_collection.delete_one(filter={'_id': doc['_id'], })
        return result.deleted_count >= 1

    def upsert_texts(self, docs: Sequence[Text]) -> int:
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

        docs = map(self.validate_text, docs)
        ops = list(map(make_upsert, docs))
        try:
            result = self.docs_collection.bulk_write(
                requests=ops, ordered=False)
            return result.bulk_api_result['nUpserted'] + result.bulk_api_result['nInserted']
        except pymongo.errors.BulkWriteError as bwe:
            print(bwe)
            print(bwe.details['writeErrors'])
            return 0

    def insert_texts(self, docs: Sequence[Text]) -> int:
        docs = map(self.validate_text, docs)
        result = self.docs_collection.insert_many(
            documents=docs, ordered=False)
        return len(result.inserted_ids)

    def remove_texts(self, docs: Sequence[Text]) -> int:
        def make_upsert(doc):
            return DeleteOne(
                filter={'_id': doc['_id'], },
            )

        docs = map(self.validate_text, docs)
        ops = list(map(make_upsert, docs))
        try:
            result = self.docs_collection.bulk_write(
                requests=ops, ordered=False)
            return result.bulk_api_result['nUpserted'] + result.bulk_api_result['nInserted']
        except pymongo.errors.BulkWriteError as bwe:
            print(bwe)
            print(bwe.details['writeErrors'])
            return 0

# region Bulk

    def clear(self):
        self.docs_collection.drop()
        self.create_indexes()

    def import_texts_from_csv(self, filepath: str) -> int:
        # Current version of MongoDB driver is incapable of chunking the iterable input,
        # so it loads everything into RAM forcing the OS to allocate GBs of swap pages.
        # https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.insert_many
        # def produce_validated():
        #     for doc in yield_texts_from_sectioned_csv(filepath):
        #         yield self.validate_text(doc)
        # result = self.docs_collection.insert_many(
        #     documents=produce_validated(),
        #     ordered=False,
        # )
        # return len(result.inserted_ids)
        allow_big_csv_fields()
        cnt_success = 0
        for files_chunk in chunks(yield_texts_from_sectioned_csv(filepath), type(self).__max_batch_size__):
            try:
                cnt_success += self.insert_texts(files_chunk)
            except:
                pass
        return cnt_success

# region Helpers

    def validate_text(self, doc: Text) -> dict:
        if isinstance(doc, (str, int)):
            return {'_id': doc}
        if isinstance(doc, Text):
            return doc.to_dict()
        if isinstance(doc, dict):
            return doc
        return doc.__dict__

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


# region Testing

if __name__ == '__main__':
    sample_file = 'Datasets/TextTest/nanoformulations.txt'
    db = MongoDB(url='mongodb://localhost:27017/SingleTextTest')
    db.clear()
    assert db.count_texts() == 0
    assert db.upsert_text(Text.from_file(sample_file))
    assert db.count_texts() == 1
    assert db.find_with_substring('Atripla-trimethyl')
    assert db.find_with_regex('Atripla-trimeth[a-z]{2}')
    # assert db.remove_text(Text.from_file(sample_file))
    # assert db.count_texts() == 0
