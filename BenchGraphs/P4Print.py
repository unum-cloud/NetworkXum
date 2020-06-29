import platform
import glob

import psutil
from pystats2md.stats_file import StatsFile
from pystats2md.stats_subset import StatsSubset
from pystats2md.report import Report

from P0Config import P0Config


class P4Print():

    def __init__(self):
        self.conf = P0Config.shared()

    def run(self) -> str:

        device_name = self.conf.device_name
        ins = StatsFile(filename=None)
        stats_paths = [f for f in glob.glob(
            f'BenchGraphs/{device_name}/**/*.json', recursive=True)]
        for stats_path in stats_paths:
            ins.append(StatsFile(filename=stats_path))

        out = Report()
        dbs = ['PostgreSQL', 'MySQL', 'SQLite', 'MongoDB',
               'UnumDB.Graph']  # ins.subset().unique('database')
        dataset_names = ['PatentCitations', 'MouseGenes',
                         'HumanBrain']  # ins.subset().unique('dataset')
        dataset_for_comparison = 'HumanBrain'

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
        2 GB/s doesn't sound very scary, but the problem is that **most databases can hardly saturate 10% of that capacity (or 200 MB/s)!**
        When it comes to random (opposed to sequential) read operations the performance drops further to <1% of channel capacity.
        That's why it's crucial for us to store the data in the most capable database!
        ''')

        out.add('## Setup')
        out.add('### Databases')
        out.add('''
        * [SQLite](https://www.sqlite.org) is the most minimalistic SQL database. 
        * [MySQL](https://www.mysql.com) is the most widely used Open-Source DB in the world. 
        * [PostgreSQL](https://www.postgresql.org) is the 2nd most popular Open-Source DB.
        * [MongoDB](https://www.sqlite.org/index.html) is the most popular NoSQL database. `$MDB` is values at aound $10 Bln.
        * [Neo4J](https://neo4j.com) was designed specifically for graphs storage, but crashes consistently, so it was removed from comparison.
        * [UnumDB.Graph](https://unum.xyz/db) is our in-house solution.

        Databases were configured to use 512 Mb of RAM for cache and 4 cores for query execution.
        Links: [The Most Popular Open Source Databases 2020](https://www.percona.com/blog/2020/04/22/the-state-of-the-open-source-database-industry-in-2020-part-three/).
        ''')
        out.add('### Device')
        out.add_current_device_specs()
        out.add('### Datasets')
        out.add('''
        * [Patent Citation Network](http://networkrepository.com/cit-patent.php).
            * Size: 272 Mb.
            * Edges: 16,518,947.
            * Average Degree: 8.
        * [Mouse Gene Regulatory Network](http://networkrepository.com/bio-mouse-gene.php).
            * Size: 295 Mb.
            * Edges: 14,506,199.
            * Average Degree: 670.
        * [HumanBrain Network](http://networkrepository.com/bn-human-Jung2015-M87102575.php).
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
            row_names=['Parsing in Python'],
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
            row_names=dbs,
            col_names=dataset_names,
        ).add_gains())

        out.add('''
        The benchmarks were repeated dozens of times. 
        These numbers translate into following import duration for each dataset.
        ''')

        out.add(ins.filtered(
            device_name=device_name,
            benchmark_name='Sequential Writes: Import CSV',
        ).to_table(
            row_name_property='database',
            col_name_property='dataset',
            cell_content_property='time_elapsed',
            row_names=dbs,
            col_names=dataset_names,
        ).printable_seconds())

        out.add('''
        Those benchmarks only tell half of the story. 
        We should not only consider performance, but also the used disk space and the affect on the hardware lifetime, as SSDs don't last too long.
        Unum has not only the highest performance, but also the most compact representation. For the `HumanBrain` graph results are:

        * MongoDB: 1,1 Gb for data + 2,5 Gb for indexes = 3,6 Gb. Wrote ~25 Gb to disk.
        * MySQL: 8.5 Gb for data + 6.4 Gb for indexes = 14.9 Gb. Wrote ~300 Gb to disk.
        * PostgreSQL: 6 Gb for data + 9 Gb for indexes = 15 Gb. Wrote ~25 Gb to disk. Furthermore, after flushing the changes, it didn't reclaim 8 Gb of space from the temporary table.
        * Unum: 1.5 Gb total volume. Extra 3.8 Gb of space were (optionally) used requested to slighly accelerate the import time. All of that space was reclaimed. A total of 5.3 was written to disk.
        ''')

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
             Input: 2 vertex identifiers.<br/>
             Output: edge that connects them.<br/>
             Metric: number of such edges returned per second.<br/>
             '''),
            ('Random Reads: Find Directed Edge',
             '''
             Input: 2 vertex identifiers (order is important).<br/>
             Output: edge that connects them in given direction.<br/>
             Metric: number of such edges returned per second.<br/>
             '''),
            ('Random Reads: Find Connected Edges',
             '''
             Input: 1 vertex identifier.<br/>
             Output: all edges attached to it.<br/>
             Metric: number of such edges returned per second.<br/>
             '''),
            ('Random Reads: Find Ingoing Edges',
             '''
             Input: 1 vertex identifier.<br/>
             Output: all edges incoming into it.<br/>
             Metric: number of such edges returned per second.<br/>
             '''),
            ('Random Reads: Find Friends',
             '''
             Input: 1 vertex identifier.<br/>
             Output: the identifiers of all unique vertexes that share an edge with the input.<br/>
             Metric: number of neighbor identiefiers returned per second.<br/>
             '''),
            ('Random Reads: Count Friends',
             '''
             Input: 1 vertex identifier.<br/>
             Output: the total number of attached edges and their accumulated weight.<br/>
             Metric: number queries per second.<br/>
             '''),
            ('Random Reads: Count Followers',
             '''
             Input: 1 vertex identifier.<br/>
             Output: the total number of incoming edges and their accumulated weight.<br/>
             Metric: number queries per second.<br/>
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
                row_names=dbs,
                col_names=dataset_names
            ).add_gains())

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
             Input: 1 new edge.<br/>
             Output: success/failure indicator.<br/>
             Metric: number inserted edges per second.<br/>
             '''),

            ('Random Writes: Upsert Edges Batch',
             '''
             Input: 500 new edges.<br/>
             Output: 500 success/failure indicators.<br/>
             Metric: number inserted edges per second.<br/>
             '''),

            ('Random Writes: Remove Edge',
             '''
             Input: 1 existing edge.<br/>
             Output: success/failure indicator.<br/>
             Metric: number removed edges per second.<br/>
             '''),

            ('Random Writes: Remove Edges Batch',
             '''
             Input: 500 existing edges.<br/>
             Output: 500 success/failure indicators.<br/>
             Metric: number removed edges per second.<br/>
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
                row_names=dbs,
                col_names=dataset_names
            ).add_gains())

        out.print_to(f'BenchGraphs/{device_name}/README.md')


if __name__ == "__main__":
    P0Config(device_name='MacbookPro').run()
    P4Print().run()
