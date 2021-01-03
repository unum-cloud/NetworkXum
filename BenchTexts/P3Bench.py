import os
from time import time

from pystats2md.stats_file import StatsFile
from pystats2md.micro_bench import MicroBench

from PyStorageGraph.BaseAPI import BaseAPI

from P0Config import P0Config
from P3TasksSampler import P3TasksSampler
from PyStorageHelpers import *


class P3Bench(object):
    """
        Benchmarks groups of operations in following order:
        2. Edge lookups and simple queries.
        3. A few complex analytical queries.
        4. Modifications: removing and restoring same objects.
        5. Clearing all the data (if needed).
    """

    def __init__(self, max_seconds_per_query=30):
        self.conf = P0Config.shared()
        self.max_seconds_per_query = max_seconds_per_query
        self.tasks = P3TasksSampler()
        allow_big_csv_fields()

    def run(self, repeat_existing=False):
        self.repeat_existing = repeat_existing
        for dataset in self.conf.datasets:
            dataset_path = self.conf.normalize_path(dataset['path'])
            self.tasks.sample_file(dataset_path)

            for db in self.conf.databases:
                self.tdb = self.conf.make_db(database=db, dataset=dataset)
                self.database = db
                self.dataset = dataset
                self.bench_buffered_graph()
                self.conf.default_stats_file.dump_to_file()

    def bench_buffered_graph(self):
        if self.tdb is None:
            return
        if self.tdb.count_texts() == 0:
            return
        print('- Benchmarking: {} @ {}'.format(
            self.dataset['name'],
            self.database['name']
        ))

        # Queries returning single object.
        self.bench_task(
            name='Random Reads: Lookup Doc by ID',
            func=self.get
        )

        # Queries returning collections.
        self.bench_task(
            name='Random Reads: Find up to 10,000 Docs containing a Short Word',
            func=lambda: self.find_substrings(
                max_matches=10000, queries=self.tasks.short_words_to_search)
        )
        self.bench_task(
            name='Random Reads: Find up to 20 Docs containing a Short Word',
            func=lambda: self.find_substrings(
                max_matches=20, queries=self.tasks.short_words_to_search)
        )
        self.bench_task(
            name='Random Reads: Find up to 20 Docs with Short Phrases',
            func=lambda: self.find_substrings(
                max_matches=20, queries=self.tasks.short_phrases_to_search)
        )
        self.bench_task(
            name='Random Reads: Find up to 20 Docs containing a Long Word',
            func=lambda: self.find_substrings(
                max_matches=20, queries=self.tasks.long_words_to_search)
        )
        self.bench_task(
            name='Random Reads: Find up to 20 Docs with Long Phrases',
            func=lambda: self.find_substrings(
                max_matches=20, queries=self.tasks.long_phrases_to_search)
        )
        # for regex_template in self.tasks.regexs_to_search:
        #     name = 'Random Reads: Find up to 20 RegEx Matches ({})'.format(
        #         regex_template['Name'])
        #     regexs = regex_template['Tasks']
        #     self.bench_task(
        #         name=name,
        #         func=lambda: self.find_regex(
        #             regexs=regexs, max_matches=20)
        #     )

        # Reversable write operations.
        self.bench_task(
            name='Random Writes: Remove Doc',
            func=self.remove_text
        )
        self.bench_task(
            name='Random Writes: Upsert Doc',
            func=self.upsert_text
        )
        self.bench_task(
            name='Random Writes: Remove Docs Batch',
            func=self.remove_texts
        )
        self.bench_task(
            name='Random Writes: Upsert Docs Batch',
            func=self.upsert_texts
        )

    def bench_task(self, name, func):
        dataset_name = self.dataset['name']
        db_name = self.database['name']
        print(f'--- {db_name}: {name} @ {dataset_name}')
        counter = MicroBench(
            benchmark_name=name,
            func=func,
            database=db_name,
            dataset=dataset_name,
            source=self.conf.default_stats_file,
            device_name=self.conf.device_name,
            limit_iterations=1,
            limit_seconds=None,
            limit_operations=None,
        )

        if not self.repeat_existing:
            if self.conf.default_stats_file.contains(counter):
                print('--- Skipping!')
                return
        print('---- Running!')
        counter.run()
        if counter.count_operations == 0:
            print('---- Didn\'t measure!')
            return
        print('---- Importing new stats!')

    # ---
    # Operations
    # ---

    def get(self) -> int:
        cnt = 0
        cnt_found = 0
        t0 = time()
        for doc_id in self.tasks.doc_ids_to_query:
            match = self.tdb.get(doc_id)
            cnt += 1
            cnt_found += 0 if (match is None) else 1
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        print(f'---- {cnt} ops: {cnt_found} ID matches')
        return cnt

    def find_substrings(self, max_matches: int, queries: list) -> int:
        cnt = 0
        cnt_found = 0
        t0 = time()
        for q in queries:
            doc_ids = self.tdb.find_substring(query=q, max_matches=max_matches)
            cnt += 1
            cnt_found += len(doc_ids)
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        print(f'---- {cnt} ops: {cnt_found} matches found')
        return cnt

    def find_regex(self, regexs, max_matches: int = None) -> int:
        cnt = 0
        cnt_found = 0
        t0 = time()
        for regex in regexs:
            doc_ids = self.tdb.find_regex(
                query=regex, max_matches=max_matches)
            cnt += 1
            cnt_found += len(doc_ids)
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        print(f'---- {cnt} ops: {cnt_found} matches found')
        return cnt

    def remove_text(self) -> int:
        cnt = 0
        for doc in self.tasks.docs_to_change_by_one:
            self.tdb.remove(doc._id)
            cnt += 1
        return cnt

    def upsert_text(self) -> int:
        cnt = 0
        for doc in self.tasks.docs_to_change_by_one:
            self.tdb.add(doc)
            cnt += 1
        return cnt

    def remove_texts(self) -> int:
        cnt = 0
        for docs in self.tasks.docs_to_change_batched:
            self.tdb.remove(list([doc._id for doc in docs]))
            cnt += len(docs)
        return cnt

    def upsert_texts(self) -> int:
        cnt = 0
        for docs in self.tasks.docs_to_change_batched:
            self.tdb.add(docs)
            cnt += len(docs)
        return cnt


if __name__ == "__main__":
    c = P0Config(device_name='MacbookPro')
    try:
        P3Bench().run()
    finally:
        c.default_stats_file.dump_to_file()
