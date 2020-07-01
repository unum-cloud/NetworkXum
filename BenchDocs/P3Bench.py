import os
from time import time

from pystats2md.stats_file import StatsFile
from pystats2md.micro_bench import MicroBench

from PyWrappedGraph.BaseAPI import BaseAPI

from P0Config import P0Config
from P3TasksSampler import P3TasksSampler


class P3Bench(object):
    """
        Benchmarks groups of operations in following order:
        2. Edge lookups and simple queries.
        3. A few complex analytical queries.
        4. Modifications: removing and restoring same objects.
        5. Clearing all the data (if needed).
    """

    def __init__(self, max_seconds_per_query=60):
        self.conf = P0Config.shared()
        self.max_seconds_per_query = max_seconds_per_query
        self.tasks = P3TasksSampler()

    def run(self, repeat_existing=True):
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
        if self.tdb.count_docs() == 0:
            return
        print('- Benchmarking: {} @ {}'.format(
            self.dataset['name'],
            self.db['name']
        ))

        self.doc_ids_to_query = []
        self.substrings_to_query = []
        self.regexs_to_query = []
        self.docs_to_change_by_one = []
        self.docs_to_change_batched = [[]]

        # Queries returning single object.
        self.bench_task(
            name='Random Reads: Retreive Doc by ID',
            func=self.find_with_id
        )

        # Queries returning collections.
        self.bench_task(
            name='Random Reads: Find Docs with Substring',
            func=self.find_with_substring
        )
        # self.bench_task(
        #     name='Random Reads: Find Docs with RegEx',
        #     func=self.find_with_regex
        # )

        # Reversable write operations.
        self.bench_task(
            name='Random Writes: Remove Doc',
            func=self.remove_doc
        )
        self.bench_task(
            name='Random Writes: Upsert Doc',
            func=self.upsert_doc
        )
        self.bench_task(
            name='Random Writes: Remove Docs Batch',
            func=self.remove_docs
        )
        self.bench_task(
            name='Random Writes: Upsert Docs Batch',
            func=self.upsert_docs
        )

    def bench_task(self, name, func):
        dataset_name = self.dataset['name']
        db_name = self.db['name']
        print(f'--- {db_name}: {name} @ {dataset_name}')
        counter = MicroBench(
            name=name,
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

    def find_with_id(self) -> int:
        cnt = 0
        cnt_found = 0
        t0 = time()
        for doc_id in self.tasks.doc_ids_to_query:
            match = self.tdb.find_with_id(doc_id)
            cnt += 1
            cnt_found += 0 if (match is None) else 1
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        print(f'---- {cnt} ops: {cnt_found} ID matches')
        return cnt

    def find_with_substring(self) -> int:
        cnt = 0
        cnt_found = 0
        t0 = time()
        for word in self.tasks.substrings_to_query:
            doc_ids = self.tdb.find_with_substring(word)
            cnt += 1
            cnt_found += len(doc_ids)
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        print(f'---- {cnt} ops: {cnt_found} matches found')
        return cnt

    def find_with_regex(self) -> int:
        cnt = 0
        cnt_found = 0
        t0 = time()
        for regex in self.tasks.regexs_to_query:
            doc_ids = self.tdb.find_with_regex(regex)
            cnt += 1
            cnt_found += len(doc_ids)
            dt = time() - t0
            if dt > self.max_seconds_per_query:
                break
        print(f'---- {cnt} ops: {cnt_found} matches found')
        return cnt

    def remove_doc(self) -> int:
        cnt = 0
        for doc in self.tasks.docs_to_change_by_one:
            self.tdb.remove_edge(doc)
            cnt += 1
        return cnt

    def upsert_doc(self) -> int:
        cnt = 0
        for doc in self.tasks.docs_to_change_by_one:
            self.tdb.upsert_edge(doc)
            cnt += 1
        return cnt

    def remove_docs(self) -> int:
        cnt = 0
        for docs in self.tasks.docs_to_change_batched:
            self.tdb.remove_edges(docs)
            cnt += len(docs)
        return cnt

    def upsert_docs(self) -> int:
        cnt = 0
        for docs in self.tasks.docs_to_change_batched:
            self.tdb.upsert_edges(docs)
            cnt += len(docs)
        return cnt


if __name__ == "__main__":
    try:
        P3Bench().run()
    finally:
        P0Config.shared().default_stats_file.dump_to_file()
