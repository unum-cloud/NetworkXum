from PyWrappedTexts.BaseAPI import BaseAPI
from PyWrappedHelpers import *

from P0Config import P0Config


class P1Test(object):
    """
        Test basic operations over a tiny graph.
        Use this ONLY for empty databases, as it will 
        clear the data before and after execution!
    """

    def __init__(self):
        self.conf = P0Config.shared()
        self.docs = [
            Text(1, 'the big brown fox'),
            Text(2, 'as.the.day;passes'),
            Text(3, 'along the:way'),
        ]

    def run(self):
        for db in self.conf.databases:
            t = self.conf.make_db(
                database=db,
                dataset=self.conf.test_dataset,
            )
            self.run_one(t)

    def run_one(self, t):
        if t is None:
            return

        print(f'-- Starting testing of: {class_name(t)}')

        print(f'--- Cleaning')
        t.clear()
        self.validate_empty(t)

        print(f'--- Single Operations')
        for doc in self.docs:
            assert t.upsert_text(doc)
        self.validate_contents(t)
        for doc in self.docs:
            assert t.remove_text(doc._id)
        self.validate_empty(t)

        print(f'--- Batch Operations')
        t.upsert_texts(self.docs)
        self.validate_contents(t)
        t.remove_texts([doc._id for doc in self.docs])
        self.validate_empty(t)

        print(f'--- Bulk Insert')
        t.import_texts_from_csv(self.conf.test_dataset['path'], column=3)
        self.validate_contents(t)
        t.clear()
        self.validate_empty(t)

        print(f'--- Passed All!')

    def validate_empty(self, t):
        assert t.count_texts() == 0, \
            f'count_texts() must be =0: {t.count_texts()}'

    def validate_contents(self, t):
        for d in self.docs:
            assert t.find_with_id(d._id).content == d.content, \
                f'No document: {d}'

        assert t.count_texts() == 3, \
            f'count_texts: {t.count_texts()}'
        assert {match._id for match in t.find_with_substring('big', max_matches=100)} == {1}, \
            f'find_with_substring: {t.find_with_substring("big", max_matches=100)}'
        assert {match._id for match in t.find_with_regex('big', max_matches=100)} == {1}, \
            f'find_with_regex: {t.find_with_regex("big", max_matches=100)}'


if __name__ == "__main__":
    P1Test().run()
