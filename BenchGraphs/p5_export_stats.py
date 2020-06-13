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

        ins = StatsFile(filename=None)
        for path in [
            'BenchGraphs/MacbookPro/stats_pygraphdb.json',
            'BenchGraphs/MacbookPro/stats_unumdb.json'
        ]:
            ins.append(StatsFile(filename=path))

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
            'GraphDB',
            # 'SQLiteCpp',
        ]
        dbs_mem = [
            'SQLiteMem',
            # 'STLOrderedMap',
            # 'STLUnorderedMap',
            # 'TSLHopscotch',
            # 'TSLRobin',
        ]
        dataset_names = [
            # 'graph-communities',
            # 'graph-eachmovie-ratings',
            'graph-patent-citations',
            'graph-mouse-gene',
            'graph-human-brain',
        ]
        dataset_for_comparison = 'graph-human-brain'

        # Intro.
        out.add('# How well can different DBs handle graphs (networks)?')
        out.add('''
        At [Unum](https://unum.xyz) we develop a neuro-symbolic AI, which means combining discrete structural representations of data and semi-continuous neural representations.
        The common misconception is that CPU/GPU power is the bottleneck for designing AGI, but we would argue that it's the storage layer.

        * CPU ⇌ RAM bandwidth: ~100 GB/s.
        * GPU ⇌ VRAM bandwidth: ~1,000 GB/s.
        * CPU ⇌ GPU bandwidth: ~15 GB/s.
        * GPU ⇌ GPU bandwidth: ~300 GB/s.
        * CPU ⇌ SSD bandwidth: ~2 GB/s.

        As we can see, the theoretical throughput between storage (SSD) and CPU is by far the biggest bottleneck.
        2 GB/s doesn't sound very scary, but the problem is that **most databases can hardly saturate 10%% of that capacity (or 200 MB/s)!**
        When it comes to random (opposed to sequential) read operations the performance drops further to <1%% of channel capacity.
        That's why it's crucial for us to store the data in the most capable database!
        ''')

        out.add('## Setup')
        out.add('### Databases')
        out.add('''
        * [Neo4J](https://neo4j.com) was designed specifically for graphs storage, but crashes consistently, so it was removed from comparison.
        * [SQLite](https://www.sqlite.org), [MySQL](https://www.mysql.com), [PostgreSQL](https://www.postgresql.org) and other SQL DBs are the foundations of modern entrprise IT infrastructure.
        * [MongoDB](https://www.sqlite.org/index.html) is a new NoSQL database currently values at aound $10 Bln.
        * [GraphDB](https://unum.xyz) is our in-house solution.

        Databases were configured to use 512 Mb of RAM for cache and 4 cores for query execution.
        ''')
        out.add('### Device')
        out.add_current_device_specs()
        out.add('### Datasets')
        out.add('''
        * [Patent Citation Network](http://networkrepository.com/cit-patent.php).
            * Size: 77 Mb.
            * Edges: 16,518,947.
            * Average Degree: 8.
        * [Mouse Gene Regulatory Network](http://networkrepository.com/bio-mouse-gene.php).
            * Size: 300 Mb.
            * Edges: 14,506,199.
            * Average Degree: 670.
        * [Human Brain Network](http://networkrepository.com/bn-human-Jung2015-M87102575.php).
            * Size: 4 Gb.
            * Edges: 87'273'967.
            * Average Degree: 186.
        ''')

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
        ))

        out.add('''
        Most DBs provide some form functionality for faster bulk imports, but not all of them where used in benchmarks for various reasons.

        * Neo4J supports CSV imports, but it requires duplicating the imported file and constantly crashes (due to Java heap management issues).
        * PostgreSQL and MySQL dialects of SQL have special functions for importing CSVs, but their functionality is very limited and performance gains aren't substantial. A better approach is to use unindexed table of incoming edges and later submit it into the main store once the data is absorbed. That's how we implemented it.
        * MongoDB provides a command line tool, but it wasn't used to limit the number of binary dependencies and simplify configuration.
        ''')

        out.add(ins.filtered(
            device_name=device_name,
            benchmark_name='Sequential Writes: Import CSV',
        ).to_table(
            row_name_property='database',
            col_name_property='dataset',
            cell_content_property='operations_per_second',
            row_names=[*dbs_pygraph, *dbs_unum],
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
             '''
             Input: 2 vertex identifiers.
             Output: edge that connects them.
             Metric: number of such edges returned per second.
             '''),
            ('Random Reads: Find Directed Edge',
             '''
             Input: 2 vertex identifiers (order is important).
             Output: edge that connects them in given direction.
             Metric: number of such edges returned per second.
             '''),
            ('Random Reads: Find Connected Edges',
             '''
             Input: 1 vertex identifier.
             Output: all edges attached to it.
             Metric: number of such edges returned per second.
             '''),
            ('Random Reads: Find Ingoing Edges',
             '''
             Input: 1 vertex identifier.
             Output: all edges incoming into it.
             Metric: number of such edges returned per second.
             '''),
            ('Random Reads: Find Friends',
             '''
             Input: 1 vertex identifier.
             Output: the identifiers of all unique vertexes that share an edge with the input.
             Metric: number of neighbor identiefiers returned per second.
             '''),
            ('Random Reads: Count Friends',
             '''
             Input: 1 vertex identifier.
             Output: the total number of attached edges and their accumulated weight.
             Metric: number queries per second.
             '''),
            ('Random Reads: Count Followers',
             '''
             Input: 1 vertex identifier.
             Output: the total number of incoming edges and their accumulated weight.
             Metric: number queries per second.
             ''')
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
            ('Random Writes: Upsert Edge',
             '''
             Input: 1 new edge.
             Output: success/failure indicator.
             Metric: number inserted edges per second.
             '''),

            ('Random Writes: Upsert Edges Batch',
             '''
             Input: 500 new edges.
             Output: 500 success/failure indicators.
             Metric: number inserted edges per second.
             '''),

            ('Random Writes: Remove Edge',
             '''
             Input: 1 existing edge.
             Output: success/failure indicator.
             Metric: number removed edges per second.
             '''),

            ('Random Writes: Remove Edges Batch',
             '''
             Input: 500 existing edges.
             Output: 500 success/failure indicators.
             Metric: number removed edges per second.
             '''),
        ]
        for write_op, description in write_ops:
            out.add(f'### {write_op}')
            out.add(description)
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

        out.print_to(config.report_path)


if __name__ == "__main__":
    StatsExporterPerOperation().run()
