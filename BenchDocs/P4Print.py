import platform
import glob

import psutil
from pystats2md.stats_file import StatsFile
from pystats2md.stats_subset import StatsSubset
from pystats2md.report import Report

from P0Config import P0Config
from PyWrappedHelpers.Config import unumdb_purpose


class P4Print():

    def __init__(self):
        self.conf = P0Config.shared()

    def run(self) -> str:

        device_name = self.conf.device_name
        ins = StatsFile(filename=None)
        stats_paths = [f for f in glob.glob(
            f'BenchDocs/{device_name}/**/*.json', recursive=True)]
        for stats_path in stats_paths:
            ins.append(StatsFile(filename=stats_path))

        out = Report()
        dbs = [
            'MongoDB', 'ElasticSearch', 'UnumDB.Graph'
        ]  # ins.subset().unique('database')
        dataset_names = [
            'COVID-19', 'EnglishWiki',
        ]  # ins.subset().unique('dataset')
        dataset_for_comparison = 'HumanBrain'

        # Intro.
        out.add('# How well can different DBs handle texts?')
        out.add()

        out.add('## Setup')
        out.add('### Databases')
        out.add(unumdb_purpose)
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
        Let's see how long it will take to load every dataset into each DB.
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
        * ElasticSearch: .
        * Unum: 1.5 Gb total volume. Extra 3.8 Gb of space were (optionally) used requested to slighly accelerate the import time. All of that space was reclaimed. A total of 5.3 was written to disk.
        ''')

        # Read Queries.
        out.add('## Read Queries')

        read_ops = [
            ('Random Reads: Find a Word',
             '''
             Input: 1 randomly selected word.<br/>
             Output: all documents containing it.<br/>
             Metric: number of such queries returned per second.<br/>
             '''),
            ('Random Reads: Find a Substring',
             '''
             Input: a combination of randomly selected words.<br/>
             Output: all documents containing it.<br/>
             Metric: number of such queries returned per second.<br/>
             '''),
            ('Random Reads: Find a RegEx',
             '''
             Input: a regular expression.<br/>
             Output: all documents containing it.<br/>
             Metric: number of such queries returned per second.<br/>
             '''),
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
        We primarily benchmark **upserts** = inserts or updates.
        Batch operations have different sizes for different DBs depending 
        on memory consumption and other limitations of each DB.
        ''')

        write_ops = [
            ('Random Writes: Upsert a Document',
             '''
             Input: 1 new document.<br/>
             Output: success/failure indicator.<br/>
             Metric: number inserted docs per second.<br/>
             '''),

            ('Random Writes: Upsert a Batch of Documents',
             '''
             Input: 500 new docs.<br/>
             Output: 500 success/failure indicators.<br/>
             Metric: number inserted docs per second.<br/>
             '''),

            ('Random Writes: Remove a Document',
             '''
             Input: 1 existing document.<br/>
             Output: success/failure indicator.<br/>
             Metric: number removed docs per second.<br/>
             '''),

            ('Random Writes: Remove a Batch of Documents',
             '''
             Input: 500 existing docs.<br/>
             Output: 500 success/failure indicators.<br/>
             Metric: number removed docs per second.<br/>
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

        out.print_to(f'BenchDocs/{device_name}/README.md')


if __name__ == "__main__":
    P0Config(device_name='MacbookPro').run()
    P4Print().run()
