
class StatsExporter(object):

    def __init__(
        self,
        benchmarks_path: str,
        report_path: str,
    ):
        pass

    def short_for_dataset(
        self,
        dataset_name: str,
        device_name: str,
    ) -> str:

        out = StatsExporter()

        cores = psutil.cpu_count(logical=False)
        threads = psutil.cpu_count(logical=True)
        frequency = psutil.cpu_freq().min
        ram_gbs = psutil.virtual_memory().total / (2 ** 30)
        disk_gbs = psutil.disk_usage('/').total / (2 ** 30)
        persistent_dbs = [
            'SQLite',
            'MySQL',
            'PostgreSQL',
            'Neo4j',
            'MongoDB',
            'HyperRocks',
            'SQLiteMem',
        ]

        out.\
            add_title(f'PyGraphDB Benchmark').\
            add_text(f'Following tests compare the performance of various databases in classical graph operations.').\
            add_text(f'Many DBs werent opptimizied for such use case, but still perform better than actual Graph DBs.').\
            add_text(f'Following results are **specific to `{dataset_name}` dataset and device** described below.\n')\

        out.\
            add_title(f'Device').\
            add_text(f'* CPU: {cores} cores, {threads} threads @ {frequency:.2f}Mhz.').\
            add_text(f'* RAM: {ram_gbs:.2f} Gb').\
            add_text(f'* Disk: {disk_gbs:.2f} Gb').\
            add_text('')

        out.\
            add_title('Simple Queries (ops/sec)').\
            reload_stats('artifacts/stats.json').\
            filter_stats(dataset=dataset_name).\
            correlate(
                'operation', 'database', 'operations_per_second',
                allowed_rows=persistent_dbs,
                allowed_cols=[
                    'Retrieve Directed Edge',
                    'Retrieve Undirected Edge',
                    'Retrieve Connected Edges',
                    'Retrieve Ingoing Edges',
                    'Retrieve Outgoing Edges',
                ]
            ).\
            compare_by('Retrieve Directed Edge').\
            add_last_table()

        out.\
            add_title('Complex Queries (ops/sec)').\
            reload_stats('artifacts/stats.json').\
            filter_stats(dataset=dataset_name).\
            correlate(
                'operation', 'database', 'operations_per_second',
                allowed_rows=persistent_dbs,
                allowed_cols=[
                    'Count Friends',
                    'Count Followers',
                    'Count Following',
                    'Retrieve Friends',
                    'Retrieve Friends of Friends',
                ]
            ).\
            compare_by('Retrieve Friends of Friends').\
            add_last_table()

        out.\
            add_title('Insertions (ops/sec)').\
            reload_stats('artifacts/stats.json').\
            filter_stats(dataset=dataset_name).\
            correlate(
                'operation', 'database', 'operations_per_second',
                allowed_rows=persistent_dbs,
                allowed_cols=[
                    'Insert Edge',
                    'Insert Edges Batch',
                    'Insert Dump',
                ]
            ).\
            compare_by('Insert Edge').\
            add_last_table()

        out.\
            add_title('Removals (ops/sec)').\
            reload_stats('artifacts/stats.json').\
            filter_stats(dataset=dataset_name).\
            correlate(
                'operation', 'database', 'operations_per_second',
                allowed_rows=persistent_dbs,
                allowed_cols=[
                    'Remove Edge',
                    'Remove Edges Batch',
                    'Remove Vertex',
                    'Remove All',
                ]
            ).\
            compare_by('Remove Edge').\
            add_last_table()

        out.export_to('artifacts/stats_mbp2019.md', overwrite=True)

    def long_for_each_operation(
        self,
    ):
        pass
