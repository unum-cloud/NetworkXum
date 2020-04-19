import platform

import psutil
from pystats.exporter import StatsExporter

import config


class StatsExporterPerOperation():

    def run(
        self,
        device_name: str = None,
    ) -> str:

        out = StatsExporter()
        dbs_pygraph = [
            'SQLiteMem',
            'SQLite',
            'MySQL',
            'PostgreSQL',
            'MongoDB',
            'Neo4j',
            # 'ArangoDB',
        ]
        dbs_unum = [
            'GraphLSM',
            'GraphBPlus',
            # 'GraphGigaHash',
            # 'GraphTeraHash',
        ]
        # dataset_names = [config.dataset_name(p) for p in config.datasets]
        dataset_names = [
            'graph-communities',
            'graph-eachmovie-ratings',
            'patent-citations',
        ]

        # Intro.
        out.add_text('# PyGraphDB Benchmarks Overview')

        # Insert Dump
        out.add_text('## Insert Dump (edges/sec)')
        out.add_text('''
            Every datascience project starts by importing the data.
            Let's see how long it will take to load an adjacency list into each DB.
            But before comparing DBs, let's see what our SSD is capable of by simply parsing the list (2 or 3 column CSV).
            This will be our baseline for estimating the time required to build the indexes in each DB.
            ''')

        out.\
            reload_stats(config.stats_path).\
            filter_stats(device=device_name).\
            filter_stats(operation='Insert Dump').\
            correlate(
                field_row='database',
                field_col='dataset',
                field_cell='operations_per_second',
                allowed_rows=['Parsing in Python'],
                allowed_cols=dataset_names,
            ).\
            compare_by(dataset_names[-1]).\
            add_last_table()

        out.\
            reload_stats(config.stats_path).\
            filter_stats(device=device_name).\
            filter_stats(operation='Insert Dump').\
            correlate(
                field_row='database',
                field_col='dataset',
                field_cell='operations_per_second',
                allowed_rows=dbs_pygraph,
                allowed_cols=dataset_names,
            ).\
            compare_by(dataset_names[-1]).\
            add_last_table()

        out.add_text('''
            Most DBs provide some form functionality for faster bulk imports, but not all of them where used in benchmarks for various reasons.

            * Neo4J supports CSV imports, but it requires duplicating the imported file and constantly crashes (due to Java heap management issues).
            * PostgreSQL and MySQL dialects of SQL have special functions for importing CSVs, but their functionality is very limited and performance gains aren't substantial. A better approach is to use unindexed table of incoming edges and later submit it into the main store once the data is absorbed.
            * MongoDB provides a command line tool, but it wasn't used to limit the number of binary dependencies and simlify configuration.

        ''')

        out.\
            reload_stats(config.stats_path).\
            filter_stats(device=device_name).\
            filter_stats(operation='Insert Dump').\
            correlate(
                field_row='database',
                field_col='dataset',
                field_cell='operations_per_second',
                allowed_rows=dbs_unum,
                allowed_cols=dataset_names,
            ).\
            compare_by(dataset_names[-1]).\
            add_last_table()

        # Read Queries.
        out.add_text('## Read Queries')
        out.add_text('''
            Following are simple lookup operations.
            Their speed translates into the execution time of analytical queries like:

            * Shortest Path Calculation,
            * Clustering Analysis,
            * Pattern Matching.

            As we are running on a local machine and within the same filesystem,
            the networking bandwidth and latency between server and client applications
            can't be a bottleneck.
        ''')

        read_ops = [
            ('Retrieve Directed Edge',
             'Given nodes A and B - find any directed edge that goes from A to B.'),
            ('Retrieve Undirected Edge',
             'Given a pair of nodes - find any edge that connects them.'),
            ('Retrieve Connected Edges',
             'Find all directed edges that contain a specific node in any role.'),
            ('Retrieve Outgoing Edges',
             'Find all directed edges that start in a specific node.'),
            # ('Retrieve Ingoing Edges', 'Find all directed edges that end in a specific node.'),
            ('Retrieve Friends',
             'Get IDs of all nodes that share an edge with a given node.'),
            ('Retrieve Friends of Friends',
             'Get IDs of all nodes that share an edge with neighbors of a given node.'),
            ('Count Friends', 'Count the number of edges containing a specific node and their total weight.'),
            ('Count Followers', 'Count the number of edges ending in a specific node and their total weight.'),
            # ('Count Following', 'Count the number of edges starting in a specific node and their total weight.'),
        ]
        for read_op, description in read_ops:
            out.\
                add_text(f'### {read_op}').\
                add_text(description).\
                reload_stats(config.stats_path).\
                filter_stats(device=device_name).\
                filter_stats(operation=read_op).\
                correlate(
                    field_row='database',
                    field_col='dataset',
                    field_cell='operations_per_second',
                    allowed_rows=[*dbs_pygraph, *dbs_unum],
                    allowed_cols=dataset_names
                ).\
                compare_by(dataset_names[-1]).\
                add_last_table()

        # Write Operations.
        out.add_text('## Write Operations')
        out.add_text('''
        We don't benchmark edge insertions as those operations are uncommon in graph workloads.
        Instead of that we benchmark **upserts** = inserts or updates.
        Batch operations have different sizes for different DBs depending on memory consumption 
        and other limitations of each DB.
        Concurrency is tested only in systems that explicitly support it.
        ''')

        write_ops = [
            'Upsert Edge',
            # 'Upsert Edge Concurrent',
            'Upsert Edges Batch',
            'Remove Edge',
            # 'Remove Edge Concurrent',
            'Remove Edges Batch',
        ]
        for write_op in write_ops:
            out.\
                add_text(f'### {write_op}').\
                reload_stats(config.stats_path).\
                filter_stats(device=device_name).\
                filter_stats(operation=write_op).\
                correlate(
                    field_row='database',
                    field_col='dataset',
                    field_cell='operations_per_second',
                    allowed_rows=[*dbs_pygraph, *dbs_unum],
                    allowed_cols=dataset_names
                ).\
                compare_by(dataset_names[-1]).\
                add_last_table()

        # Configuration Details
        out.add_text('## Device')
        cores = psutil.cpu_count(logical=False)
        threads = psutil.cpu_count(logical=True)
        frequency = psutil.cpu_freq().min
        ram_gbs = psutil.virtual_memory().total / (2 ** 30)
        disk_gbs = psutil.disk_usage('/').total / (2 ** 30)
        out.add_text(f'''
            * CPU: {cores} cores, {threads} threads @ {frequency:.2f}Mhz.
            * RAM: {ram_gbs:.2f} Gb
            * Disk: {disk_gbs:.2f} Gb
            * OS: {platform.system()}
            ''')

        out.export_to(config.report_path, overwrite=True)


if __name__ == "__main__":
    StatsExporterPerOperation().run()
