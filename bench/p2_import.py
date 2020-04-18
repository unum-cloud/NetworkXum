from datetime import datetime
import os
import importlib

from pygraphdb.helpers import StatsCounter

import config


class BulkImporter(object):
    """
    Performs multithreaded bulk import into DB.
    Saves stats.
    """

    def printable_bytes(self, size, decimal_places=3):
        for unit in ['B', 'KiB', 'MiB', 'GiB', 'TiB']:
            if size < 1024.0:
                break
            size /= 1024.0
        return f"{size:.{decimal_places}f}{unit}"

    def printable_count(self, size, decimal_places=3):
        for unit in ['', 'K', 'M', 'G', 'T']:
            if size < 1000.0:
                break
            size /= 1000.0
        return f"{size:.{decimal_places}f}{unit}"

    def run(self):
        for graph_type in config.wrapper_types:
            for dataset_path in config.datasets:
                url = config.database_url(graph_type, dataset_path)
                if url is None:
                    continue

                g = graph_type(url)
                dataset_name = config.dataset_name(dataset_path)
                wrapper_name = config.wrapper_name(g)

                if (g.count_edges() != 0):
                    print(f'-- Skipping: {dataset_name} -> {wrapper_name}')
                    continue
                file_size = os.path.getsize(dataset_path)
                expected_edges = config.dataset_number_of_edges(dataset_path)
                print(f'-- Bulk importing: {dataset_name} -> {wrapper_name}')
                print(f'--- started at:', datetime.now().strftime('%H:%M:%S'))
                print(f'--- file size:', self.printable_bytes(file_size))

                def import_one() -> int:
                    g.insert_adjacency_list(dataset_path)
                    return g.count_edges()

                counter = StatsCounter()
                counter.handle(import_one)
                config.stats.upsert(
                    wrapper_class=wrapper_name,
                    operation_name='Insert Dump',
                    dataset=dataset_name,
                    stats=counter,
                )
                print(f'--- edges:', self.printable_count(counter.count_operations))
                print(f'--- edges/second:',
                      self.printable_count(counter.ops_per_sec()))
                print(f'--- bytes/second:',
                      self.printable_bytes(file_size / counter.time_elapsed))
                config.stats.dump_to_file()


if __name__ == "__main__":
    try:
        BulkImporter().run()
    finally:
        config.stats.dump_to_file()
