from PyWrappedDocs.BaseAPI import BaseAPI
from PyWrappedHelpers.Text import Text
from PyWrappedHelpers.Algorithms import *

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
        t.remove_all()
        self.validate_empty(t)

        print(f'--- Single Operations')
        for doc in self.docs:
            assert t.upsert_doc(doc)
        self.validate_contents(t)
        for doc in self.docs:
            assert t.remove_doc(doc._id)
        self.validate_empty(t)

        print(f'--- Batch Operations')
        t.upsert_docs(self.docs)
        self.validate_contents(t)
        t.remove_docs([doc._id for doc in self.docs])
        self.validate_empty(t)

        print(f'--- Bulk Insert')
        t.import_docs_from_csv(self.conf.test_dataset['path'], column=3)
        self.validate_contents(t)
        t.remove_all()
        self.validate_empty(t)

        print(f'--- Passed All!')

    def validate_empty(self, t):
        assert t.count_docs() == 0, \
            f'count_docs() must be =0: {t.count_docs()}'

    def validate_contents(self, t):
        for d in self.docs:
            assert t.find_with_id(d._id).content == d.content, \
                f'No document: {d}'

        assert t.count_docs() == 3, \
            f'count_docs: {t.count_docs()}'
        assert {match._id for match in t.find_with_substring('big', max_matches=100)} == {1}, \
            f'find_with_substring: {t.find_with_substring("big", max_matches=100)}'
        assert {match._id for match in t.find_with_regex('big', max_matches=100)} == {1}, \
            f'find_with_regex: {t.find_with_regex("big", max_matches=100)}'


if __name__ == "__main__":
    P1Test().run()
