from typing import List, Optional, Dict, Generator, Set, Tuple, Sequence

import pymongo
from pymongo import MongoClient
from pymongo import UpdateOne, DeleteOne

from PyStorageTexts.BaseAPI import BaseAPI
from PyStorageHelpers import *


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
        self.texts_collection = self.db[db_name]['texts']
        self.create_indexes()

    def count_texts(self) -> int:
        return self.texts_collection.count_documents(filter={})

# region Random Reads

    def get(self, query: int) -> Optional[Text]:
        result = self.texts_collection.find_one(filter={
            '_id': query
        })
        if result:
            return Text(**result)
        return None

    def find_substring(
        self,
        query: str,
        case_sensitive: bool = True,
        max_matches: Optional[int] = None,
        include_text=True,
    ) -> Sequence[TextMatch]:
        """
            CAUTION: Seems like MongoDB doesn't support text search limited 
            to a specific field, so it's inapplicable to more complex cases.
        """
        # https://docs.mongodb.com/manual/reference/operator/query/text/
        # https://docs.mongodb.com/manual/core/index-text/
        # https://docs.mongodb.com/manual/reference/text-search-languages/#text-search-languages
        proj = ['_id', 'content'] if include_text else ['_id']
        dicts = self.texts_collection.find(filter={
            '$text': {
                '$search': f'\"{query}\"',
                '$caseSensitive': case_sensitive,
                '$diacriticSensitive': False,
            },
        }, projection=proj)
        if max_matches:
            dicts = dicts.limit(max_matches)
        return list(map(self.parse_match, dicts))

    def find_regex(
        self,
        query: str,
        case_sensitive: bool = True,
        max_matches: Optional[int] = None,
        include_text=True,
    ) -> Sequence[TextMatch]:

        # https://docs.mongodb.com/manual/reference/operator/query/regex/
        proj = ['_id', 'content'] if include_text else ['_id']
        opts = 'm' if case_sensitive else 'mi'
        dicts = self.texts_collection.find(filter={
            'content': {
                '$regex': query,
                '$options': opts,
            },
        }, projection=proj)
        if max_matches:
            dicts = dicts.limit(max_matches)
        return list(map(self.parse_match, dicts))

# region Random Writes

    def add(self, obj: Text, upsert=True) -> int:
        """
            Supports up to 1000 updates per batch.
            https://api.mongodb.com/python/current/examples/bulk.html#ordered-bulk-write-operations
        """
        target = self.texts_collection
        if isinstance(obj, Text):
            if upsert:
                result = target.update_one(
                    filter={'_id': obj._id, },
                    update={'$set': obj.__dict__, },
                    upsert=True,
                )
                return (result.modified_count >= 1) or (result.upserted_id is not None)
            else:
                return target.insert_one(obj.__dict__).acknowledged
        elif is_sequence_of(obj, Text):
            if upsert:
                def make_upsert(o):
                    return UpdateOne(
                        filter={'_id': o._id, },
                        update={'$set': o.__dict__, },
                        upsert=True,
                    )
                ops = list(map(make_upsert, obj))
                try:
                    result = target.bulk_write(
                        requests=ops, ordered=False)
                    cnt_old = result.bulk_api_result['nUpserted']
                    cnt_new = result.bulk_api_result['nInserted']
                    return cnt_new + cnt_old
                except pymongo.errors.BulkWriteError as bwe:
                    print(bwe)
                    print(bwe.details['writeErrors'])
                    return 0
            else:
                obj = [o.__dict__ for o in obj]
                result = target.insert_many(obj, ordered=False)
                return len(result.inserted_ids)

        return super().add(obj, upsert=upsert)

    def remove(self, obj) -> int:
        target = self.texts_collection
        if isinstance(obj, int):
            return target.delete_one(filter={'_id': obj}).deleted_count >= 1
        elif is_sequence_of(obj, int):
            return target.delete_many(filter={'_id': {'$in': obj}}).deleted_count

        return super().remove(obj)


# region Bulk Reads

    @property
    def texts(self) -> Sequence[Text]:
        return [Text(**as_dict) for as_dict in self.texts_collection.find()]

# region Bulk Writes

    def clear(self):
        self.texts_collection.drop()
        self.create_indexes()

    def add_stream(self, stream, upsert=False) -> int:
        # Current version of MongoDB driver is incapable of chunking the iterable input,
        # so it loads everything into RAM forcing the OS to allocate GBs of swap pages.
        # https://api.mongodb.com/python/current/api/pymongo/collection.html#pymongo.collection.Collection.insert_many
        return super().add_stream(stream, upsert=upsert)

# region Helpers

    def create_indexes(self):
        for field in self.indexed_fields:
            self.create_index(field)
        # As MongoDB can't search in a specific index,
        # we can create a generic index for all fields.
        # self.create_index_for_all_strings()

    def create_index(self, field: str, background=False):
        self.texts_collection.create_index(
            [(field, pymongo.TEXT)],
            background=background,
        )

    def create_index_for_all_strings(self, background=False):
        # https://docs.mongodb.com/manual/core/index-text/#wildcard-text-indexes
        self.texts_collection.create_index(
            {'$**': 'text'},
            background=background,
        )

    def parse_match(self, dict_) -> TextMatch:
        return TextMatch(_id=dict_['_id'], content=dict_.get('content', ''), rating=1)


# region Testing

if __name__ == '__main__':
    sample_file = 'Datasets/TextTest/nanoformulations.txt'
    db = MongoDB(url='mongodb://localhost:27017/SingleTextTest')
    db.clear()
    assert db.count_texts() == 0
    assert db.add(Text.from_file(sample_file))
    assert db.count_texts() == 1
    assert db.find_substring('Atripla-trimethyl')
    assert db.find_regex('Atripla-trimeth[a-z]{2}')
    # assert db.remove(Text.from_file(sample_file))
    # assert db.count_texts() == 0
