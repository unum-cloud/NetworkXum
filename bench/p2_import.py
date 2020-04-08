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
                print(f'-- Bulk importing: {dataset_name} -> {wrapper_name}')

                def import_one() -> int:
                    g.insert_dump(dataset_path)
                    return g.count_edges()

                counter = StatsCounter()
                counter.handle(import_one)
                config.stats.insert(
                    wrapper_class=wrapper_name,
                    operation_name='Insert Dump',
                    dataset=dataset_name,
                    stats=counter,
                )


if __name__ == "__main__":
    BulkImporter().run()
    config.stats.dump_to_file()
