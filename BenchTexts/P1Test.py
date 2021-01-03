from PyStorageTexts.BaseAPI import BaseAPI
from PyStorageHelpers import *

from P0Config import P0Config


class P1Test(object):
    """
        Test basic operations over a tiny graph.
        Use this ONLY for empty databases, as it will 
        clear the data before and after execution!
    """

    def __init__(self):
        self.conf = P0Config.shared()
        self.texts = [
            Text(1, 'the big brown fox'),
            Text(2, 'as.the.day;passes'),
            Text(3, 'along the:way'),
        ]

    def run(self):
        for db in self.conf.databases:
            tdb = self.conf.make_db(
                database=db,
                dataset=self.conf.test_dataset,
            )
            self.run_one(tdb)

    def run_one(self, tdb):
        if tdb is None:
            return

        print(f'-- Starting testing of: {class_name(tdb)}')

        print(f'--- Cleaning')
        tdb.clear()
        self.validate_empty(tdb)

        print(f'--- Single Operations')
        for text in self.texts:
            assert tdb.add(text)
        self.validate_contents(tdb)
        for text in self.texts:
            assert tdb.remove(text._id)
        self.validate_empty(tdb)

        print(f'--- Batch Operations')
        tdb.add(self.texts)
        self.validate_contents(tdb)
        tdb.remove([text._id for text in self.texts])
        self.validate_empty(tdb)

        print(f'--- Bulk Insert')
        import_texts(tdb, self.conf.test_dataset['path'], column=3)
        self.validate_contents(tdb)
        tdb.clear()
        self.validate_empty(tdb)

        print(f'--- Passed All!')

    def validate_empty(self, tdb):
        assert tdb.count_texts() == 0, \
            f'count_texts() must be =0: {tdb.count_texts()}'

    def validate_contents(self, tdb):
        for d in self.texts:
            assert tdb.get(d._id).content == d.content, \
                f'No textument: {d}'

        assert tdb.count_texts() == 3, \
            f'count_texts: {tdb.count_texts()}'
        assert {match._id for match in tdb.find_substring('big', max_matches=100)} == {1}, \
            f'find_substring: {tdb.find_substring("big", max_matches=100)}'
        assert {match._id for match in tdb.find_regex('big', max_matches=100)} == {1}, \
            f'find_regex: {tdb.find_regex("big", max_matches=100)}'


if __name__ == "__main__":
    P1Test().run()
