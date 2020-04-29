import platform

import psutil
from pystats2md.stats_file import StatsFile
from pystats2md.stats_subset import StatsSubset
from pystats2md.report import Report

import config


class StatsExporterPerOperation():

    def run(
        self,
        device_name='MacbookPro',
    ) -> str:

        ins = config.stats
        out = Report()
        dbs_pygraph = [
            'SQLite',
            'MySQL',
            'PostgreSQL',
            'MongoDB',
            # 'Neo4J',
            # 'ArangoDB',
        ]
        dbs_unum = [
            'PontDBchunk',
            'PontDBmono',
            # 'SQLiteCpp',
        ]
        dbs_mem = [
            'SQLiteMem',
            'PontDBstlo',
            'PontDBstlu',
            'PontDBtslh',
            'PontDBtslr',
        ]
        dataset_names = [
            'graph-communities',
            'graph-eachmovie-ratings',
            'graph-patent-citations',
            'graph-mouse-gene',
            'graph-human-brain',
        ]
        dataset_for_comparison = dataset_names[2]

        # Intro.
        out.add('# PyGraphDB Benchmarks Overview')

        # Sequential Writes: Import CSV
        out.add('## Sequential Writes: Import CSV (edges/sec)')
        out.add('''
            Every datascience project starts by importing the data.
            Let's see how long it will take to load an adjacency list into each DB.
            But before comparing DBs, let's see what our SSD is capable of by simply parsing the list (2 or 3 column CSV).
            This will be our baseline for estimating the time required to build the indexes in each DB.
            ''')

        out.add(ins.filtered(
            device_name=device_name,
            benchmark_name='Sequential Writes: Import CSV',
        ).to_table(
            row_name_property='database',
            col_name_property='dataset',
            cell_content_property='operations_per_second',
            row_names=['Parsing in Python', 'SQLiteMem'],
            col_names=dataset_names,
        ).add_emoji(dataset_for_comparison))

        out.add('''
            Most DBs provide some form functionality for faster bulk imports, but not all of them where used in benchmarks for various reasons.

            * Neo4J supports CSV imports, but it requires duplicating the imported file and constantly crashes (due to Java heap management issues).
            * PostgreSQL and MySQL dialects of SQL have special functions for importing CSVs, but their functionality is very limited and performance gains aren't substantial. A better approach is to use unindexed table of incoming edges and later submit it into the main store once the data is absorbed.
            * MongoDB provides a command line tool, but it wasn't used to limit the number of binary dependencies and simlify configuration.
        ''')

        out.add(ins.filtered(
            device_name=device_name,
            benchmark_name='Sequential Writes: Import CSV',
        ).to_table(
            row_name_property='database',
            col_name_property='dataset',
            cell_content_property='operations_per_second',
            row_names=[*dbs_pygraph, 'Neo4J', *dbs_unum],
            col_names=dataset_names,
        ).add_emoji(dataset_for_comparison))

        # Read Queries.
        out.add('## Read Queries')
        out.add('''
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
            ('Random Reads: Find Any Relation',
             'Given a pair of nodes - find any edge that connects them.'),
            ('Random Reads: Find Directed Edge',
             'Given nodes A and B - find any directed edge that goes from A to B.'),
            ('Random Reads: Find Connected Edges',
             'Find all edges that contain a specific node in any role.'),
            ('Random Reads: Find Ingoing Edges',
             'Find all directed edges that end in a specific node.'),
            ('Random Reads: Find Friends',
             'Get IDs of all nodes that share an edge with a given node.'),
            ('Random Reads: Count Friends',
             'Count the number of edges containing a specific node and their total weight.'),
            ('Random Reads: Count Followers',
             'Count the number of edges ending in a specific node and their total weight.'),

            # These are essentially the same.
            # ('Random Reads: Find Outgoing Edges',
            #  'Find all directed edges that start in a specific node.'),
            # ('Random Reads: Find Friends of Friends',
            #  'Get IDs of all nodes that share an edge with neighbors of a given node.'),
            # ('Random Reads: Count Following',
            #  'Count the number of edges starting in a specific node and their total weight.'),
        ]
        for read_op, description in read_ops:

            out.add(f'### {read_op}')
            out.add(description)
            out.add(ins.filtered(
                device_name=device_name,
                benchmark_name=read_op,
            ).to_table(
                row_name_property='database',
                col_name_property='dataset',
                cell_content_property='operations_per_second',
                row_names=[*dbs_pygraph, *dbs_unum],
                col_names=dataset_names
            ).add_emoji(dataset_for_comparison))

        # Write Operations.
        out.add('## Write Operations')
        out.add('''
        We don't benchmark edge insertions as those operations are uncommon in graph workloads.
        Instead of that we benchmark **upserts** = inserts or updates.
        Batch operations have different sizes for different DBs depending on memory consumption 
        and other limitations of each DB.
        Concurrency is tested only in systems that explicitly support it.
        ''')

        write_ops = [
            'Random Writes: Upsert Edge',
            # 'Random Writes: Upsert Edge Concurrent',
            'Random Writes: Upsert Edges Batch',
            'Random Writes: Remove Edge',
            # 'Random Writes: Remove Edge Concurrent',
            'Random Writes: Remove Edges Batch',
        ]
        for write_op in write_ops:
            out.add(f'### {write_op}')
            out.add(ins.filtered(
                device_name=device_name,
                benchmark_name=write_op,
            ).to_table(
                row_name_property='database',
                col_name_property='dataset',
                cell_content_property='operations_per_second',
                row_names=[*dbs_pygraph, *dbs_unum],
                col_names=dataset_names
            ).add_emoji(dataset_for_comparison))

        # Configuration Details
        out.add('## Device')
        cores = psutil.cpu_count(logical=False)
        threads = psutil.cpu_count(logical=True)
        frequency = psutil.cpu_freq().min
        ram_gbs = psutil.virtual_memory().total / (2 ** 30)
        disk_gbs = psutil.disk_usage('/').total / (2 ** 30)
        out.add(f'''
            * CPU: {cores} cores, {threads} threads @ {frequency:.2f}Mhz.
            * RAM: {ram_gbs:.2f} Gb
            * Disk: {disk_gbs:.2f} Gb
            * OS: {platform.system()}
            ''')

        out.print_to(config.report_path)


if __name__ == "__main__":
    StatsExporterPerOperation().run()
