from datetime import datetime
import os

from pygraphdb.helpers import StatsCounter

import config


class BulkImporter(object):
    """
    Performs multithreaded bulk import into DB.
    Saves stats.
    """

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
                file_size = os.path.getsize(dataset_path) / (2 ** 20)
                expected_edges = config.dataset_number_of_edges(dataset_path)
                print(f'-- Bulk importing: {dataset_name} -> {wrapper_name}')
                print(f'--- started at:', datetime.now().strftime('%H:%M:%S'))
                print(f'--- file size (Mb):', file_size)

                def import_one() -> int:
                    g.insert_adjacency_list(dataset_path)
                    return g.count_edges()

                counter = StatsCounter()
                counter.handle(import_one)
                config.stats.insert(
                    wrapper_class=wrapper_name,
                    operation_name='Insert Dump',
                    dataset=dataset_name,
                    stats=counter,
                )
                secs_elapsed = (counter.time_elapsed / 1000)
                print(f'--- edges:', counter.count_operations)
                print(f'--- edges/second:', counter.ops_per_sec())
                print(f'--- Mb/second:', file_size / secs_elapsed)
                config.stats.dump_to_file()


if __name__ == "__main__":
    try:
        BulkImporter().run()
    finally:
        config.stats.dump_to_file()
