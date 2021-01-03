from datetime import datetime
import os
import importlib

from pystats2md.micro_bench import MicroBench
from pystats2md.helpers import metric2str, bytes2str

from PyStorageHelpers import *
from P0Config import P0Config


class P2Import(object):
    """
        Performs bulk import into DB.
        Saves stats.
    """

    def __init__(self):
        self.conf = P0Config.shared()

    def run(self):
        for dataset in self.conf.datasets:
            for db in self.conf.databases:
                tdb = self.conf.make_db(database=db, dataset=dataset)
                self.import_texts(tdb=tdb, database=db, dataset=dataset)

    def import_texts(self, tdb, database: dict, dataset: dict):
        if tdb is None:
            return

        db_name = database['name']
        dataset_name = dataset['name']
        if (tdb.count_texts() != 0):
            print(f'-- Skipping: {dataset_name} -> {db_name}')
            return

        dataset_path = self.conf.normalize_path(dataset['path'])
        file_size = os.path.getsize(dataset_path)
        print(f'-- Bulk importing: {dataset_name} -> {db_name}')
        print(f'--- started at:', datetime.now().strftime('%H:%M:%S'))
        print(f'--- file size:', bytes2str(file_size))

        def import_one() -> int:
            import_texts(tdb, dataset_path)
            return tdb.count_texts()

        counter = MicroBench(
            benchmark_name='Sequential Writes: Import CSV',
            func=import_one,
            database=db_name,
            dataset=dataset_name,
            source=self.conf.default_stats_file,
            device_name=self.conf.device_name,
        )
        counter.run_if_missing()

        print(f'--- docs:', metric2str(counter.count_operations))
        print(f'--- docs/second:', metric2str(counter.ops_per_sec()))
        print(f'--- bytes/second:', bytes2str(file_size / counter.time_elapsed))
        print(f'--- finished at:', datetime.now().strftime('%H:%M:%S'))
        self.conf.default_stats_file.dump_to_file()


if __name__ == "__main__":
    c = P0Config(device_name='MacbookPro')
    try:
        P2Import().run()
    finally:
        c.default_stats_file.dump_to_file()
