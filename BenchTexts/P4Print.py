import re
import glob

from pystats2md.stats_file import StatsFile
from pystats2md.stats_subset import StatsSubset
from pystats2md.stats_table import StatsTable
from pystats2md.report import Report

from P0Config import P0Config
from P3TasksSampler import P3TasksSampler
from PyStorageHelpers import *


class P4Print():

    def __init__(self):
        self.conf = P0Config.shared()

    def run(self) -> str:

        device_name = self.conf.device_name
        ins = StatsFile(filename=None)
        stats_paths = [f for f in glob.glob(
            f'BenchTexts/{device_name}/**/*.json', recursive=True)]
        for stats_path in stats_paths:
            ins.append(StatsFile(filename=stats_path))

        out = Report()
        dbs = [
            'MongoDB', 'ElasticSearch',
            'UnumDB',
        ]  # ins.subset().unique('database')
        dataset_names = [
            'Covid19',
            'PoliticalTweetsIndia',
            # 'EnglishWikipedia',
        ]  # ins.subset().unique('dataset')
        dataset_for_comparison = 'Covid19'

        # Intro.
        out.add('# How well can different DBs handle texts?')
        # out.add()

        out.add('## Setup')
        out.add('### Databases')
        out.add(unumdb_purpose)
        out.add('### Device')
        out.add_current_device_specs()
        out.add('### Datasets')
        out.add('''
        * [Covid19](https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge) Scientific Papers.
            * Documents: 45,941.
            * Sections: 1,604,649.
            * Size: 1,7 GB.
        * [PoliticalTweetsIndia](https://www.kaggle.com/iamyoginth/facthub) Posts.
            * Documents: 12,488,144.
            * Sections: 12,488,144.
            * Size: 2,3 GB.
        * [EnglishWikipedia](https://www.kaggle.com/jkkphys/english-wikipedia-articles-20170820-sqlite) Dump from 2017.
            * Documents: 4,902,648.
            * Sections: 23,046,187.
            * Size: 18,2 GB.
        ''')

        # Sequential Writes: Import CSV
        out.add('## Sequential Writes: Import CSV (docs/sec)')
        out.add('''
        Every datascience project starts by importing the data.
        Let's see how long it will take to load every dataset into each DB.
        ''')

        out.add(ins.filtered(
            device_name=device_name,
            benchmark_name='Sequential Writes: Import CSV',
        ).table(
            row_name_property='database',
            col_name_property='dataset',
            cell_content_property='operations_per_second',
            row_names=dbs,
            col_names=dataset_names,
        ).add_gains())

        out.add(ins.filtered(
            device_name=device_name,
            benchmark_name='Sequential Writes: Import CSV',
        ).table(
            row_name_property='database',
            col_name_property='dataset',
            cell_content_property='time_elapsed',
            row_names=dbs,
            col_names=dataset_names,
        ).printable_seconds())

        out.add('''
        Those benchmarks only tell half of the story. 
        We should not only consider performance, but also the used disk space and the affect on the hardware lifetime, as SSDs don't last too long.
        Unum has not only the highest performance, but also the most compact representation.
        MongoDB generally performs well across different benchmarks, but it failed to import the English Wikipedia in 10 hours.
        I suspect a bug in the implementation of the text index, as some batch import operations took over 10 mins for a modest batch size of 10,000 docs.
        ''')
        out.add(StatsTable(header_row=[
            'Covid19', 'PoliticalTweetsIndia', 'EnglishWikipedia',
        ], header_col=[
            'MongoDB', 'ElasticSearch', 'UnumDB',
        ], content=[
            ['1,9 GB', '3,2 GB', 'Expected 60,7 GB'],
            ['2,5 GB', '2,9 GB', '33,5 GB'],
            ['1', '1', '1'],
        ]))

        out.add(
            StatsSubset(ins).filtered(
                device_name=device_name,
                benchmark_name='Sequential Writes: Import CSV',
            ).table(
                cell_content_property='write_bytes',
                row_name_property='database',
                col_name_property='dataset',
                col_names=dataset_names,
                row_names=dbs,
            ).plot(
                title='Import Overhead - Total Bytes Written',
                print_height=True,
                print_rows_names=True,
                print_cols_names=True,
            )
        )

        # Read Queries.
        out.add('## Read Queries')
        out.add('''
        Regular Expressions are the most computational intesive operations in textual database.
        If the pattern is complex, even the most advanced DBs may not be able to utilize the pre-constructed search index.
        As a result they will be forced to run a full-scan against all documents stored in the DB.
        It means having at least 2 bottlenecks:

        1. If you are scanning all the data in the DB you are limited by the sequential read performance of the SSD (accounting for the read amplification dependant on the data locality).
        2. The speed of your RegEx engine.

        The (1.) point is pretty clear, but the (2.) is much more complex. Most DBs use the [PCRE/PCRE2](http://www.pcre.org) C library which was first released back in 1997 with a major upgrade in 2015.
        Implementing full RegEx support is complex, especially if you want to beat C code in performance, so most programming languages and libraries just wrap PCRE.
        That said, the performance is still laughable. It varies a lot between different different queries, but [can be orders of magniture slower](https://rust-leipzig.github.io/regex/2017/03/28/comparison-of-regex-engines/) than [Intel Hyperscan](https://software.intel.com/content/www/us/en/develop/articles/introduction-to-hyperscan.html) State-of-theArt library.
        Most (if not all) of those libraries use the classical DFA-based algorithm with `~O(n)` worst case time complexity for search (assuming the automata is already constructed).
        As always, we are not limiting ourselves to using existing algorithms, we design our own. In `Unum.ReGex` we have developed an algorithm with worst-case-complexity harder than the DFA approach, but the average complexity is also `~O(n)`.
        However, the constant multiplier in our case is much lower, so the new algorithm ends-up beating the classical solutions from Intel, Google and other companies at least in some cases. 
        On our test bench the timings are:

        *   `std::regex` on 1 Intel Core: varies between 1 MB/s and 300 MB/s.
        *   PCRE2 on 1 Intel Core: .
        *   Intel Hyperscan on 1 Intel Core: 4 GB/s consistent performance.
        *   Unum.RegEx on 1 Intel Core: up to 3 GB/s.
        *   Unum.RegEx on 1 Intel Core (after text preprocessing): up to 15 GB/s.
        *   Unum.RegEx on Titan V GPU: ? GB/s.
        *   Unum.RegEx on Titan V GPU (after text preprocessing): ? GB/s.

        The best part is that it can use statistics and cleverly organizind search indexes to vastly reduce the number of documents to be scanned.
        To our knowledge, no modern piece of software has such level of mutually-benefitial communication between the storage layer and the application layer.
        The results below speak for themselves, but before we go further I would like to note, that comparing randomly generated RegEx queries makes little sense, as such results wouldn't translate into real-world benefits for potential users.
        There are not too many universally used RegEx patterns, so the DBs can use the cache to fetch previously computed results.
        Such benchmarks are not representative as well, so I took the most common RegEx patterns (dates, numbers, IP addresses, E-mail addresses, XML tags...) and concatentated them with randomly sampled words from each of the datasets.
        That way we are still getting results similar to real-world queries, but avoid cache hits.
        ''')

        read_ops = [
            ('Random Reads: Lookup Doc by ID',
             '''
             Input: 1 document identifier.<br/>
             Output: text content.<br/>
             Metric: number of queries per second.<br/>
             '''),
            ('Random Reads: Find up to 10,000 Docs containing a Short Word',
             '''
             Input: 1 randomly selected word (under 9 letters).<br/>
             Output: up to 10,000 documents IDs containing it.<br/>
             Metric: number of queries per second.<br/>
             '''),
            ('Random Reads: Find up to 20 Docs containing a Short Word',
             '''
             Input: 1 randomly selected word (under 9 letters).<br/>
             Output: up to 20 documents IDs containing it.<br/>
             Metric: number of queries per second.<br/>
             '''),
            ('Random Reads: Find up to 20 Docs with Short Phrases',
             '''
             Input: a combination of randomly selected short words (under 9 letters).<br/>
             Output: up to 20 documents IDs containing it.<br/>
             Metric: number of queries per second.<br/>
             '''),
            ('Random Reads: Find up to 20 Docs containing a Long Word',
             '''
             Input: 1 randomly selected word (over 9 letters).<br/>
             Output: up to 20 documents IDs containing it.<br/>
             Metric: number of queries per second.<br/>
             '''),
            ('Random Reads: Find up to 20 Docs with Long Phrases',
             '''
             Input: a combination of randomly selected short words (over 9 letters).<br/>
             Output: up to 20 documents IDs containing it.<br/>
             Metric: number of queries per second.<br/>
             '''), ]
        # for regex_template in P3TasksSampler.__regex_templates__:
        #     read_op = 'Random Reads: Find a RegEx ({})'.format(
        #         regex_template['Name'])
        #     description = '''
        #         Input: a regular expression: `{}`.<br/>
        #         Output: all documents IDs containing it.<br/>
        #         Metric: number of queries per second.<br/>
        #         Match Example: `{}`.<br/>
        #     '''.format(regex_template['Template'], regex_template['Example'])
        #     read_ops.append([read_ops, description])

        for read_op, description in read_ops:

            out.add(f'### {read_op}')
            out.add(description)
            out.add(ins.filtered(
                device_name=device_name,
                benchmark_name=read_op,
            ).table(
                row_name_property='database',
                col_name_property='dataset',
                cell_content_property='operations_per_second',
                row_names=dbs,
                col_names=dataset_names
            ).add_gains())

        # Add a chart showing the number of total read bytes during random read operations.
        out.add(
            StatsSubset(ins).filtered(
                device_name=device_name,
                benchmark_name=re.compile('Random Reads: Find.*'),
            ).table(
                cell_content_property='read_bytes',
                row_name_property='database',
                col_name_property='benchmark_name',
                row_names=dbs,
            ).plot(
                title='Read Amplification - Read Bytes Per Benchmark',
                print_height=True,
                print_rows_names=True,
                print_cols_names=True,
            )
        )

        # Write Operations.
        out.add('## Write Operations')
        out.add('''
        We primarily benchmark **upserts** = inserts or updates.
        Batch operations have different sizes for different DBs depending 
        on memory consumption and other limitations of each DB.
        ''')

        write_ops = [
            ('Random Writes: Upsert Doc',
             '''
             Input: 1 new document.<br/>
             Output: success/failure indicator.<br/>
             Metric: number inserted docs per second.<br/>
             '''),

            ('Random Writes: Upsert Docs Batch',
             '''
             Input: 500 new docs.<br/>
             Output: 500 success/failure indicators.<br/>
             Metric: number inserted docs per second.<br/>
             '''),

            ('Random Writes: Remove Doc',
             '''
             Input: 1 existing document.<br/>
             Output: success/failure indicator.<br/>
             Metric: number removed docs per second.<br/>
             '''),

            ('Random Writes: Remove Docs Batch',
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
            ).table(
                row_name_property='database',
                col_name_property='dataset',
                cell_content_property='operations_per_second',
                row_names=dbs,
                col_names=dataset_names
            ).add_gains())

        # Add a chart showing the number of total read and written bytes during write operations.
        out.add(
            StatsSubset(ins).filtered(
                device_name=device_name,
                benchmark_name=re.compile('Random Writes.*'),
            ).table(
                cell_content_property='write_bytes',
                row_name_property='database',
                col_name_property='benchmark_name',
                row_names=dbs,
            ).plot(
                title='Write Amplification - Written Bytes Per Benchmark',
                print_height=True,
                print_rows_names=True,
                print_cols_names=True,
            )
        )

        out.print_to(f'BenchTexts/{device_name}/README.md')


if __name__ == "__main__":
    P0Config(device_name='MacbookPro').run()
    P4Print().run()
