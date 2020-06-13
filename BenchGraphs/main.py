import config
from p1_test import Tester
from p2_import import BulkImporter
from p3_bench_simple import SimpleBenchmark
from p4_bench_networkx import NetworkXBenchmark
# from p5_export_stats_operation import StatsExporter
# from p6_export_stats_dataset import StatsExporter


if __name__ == "__main__":
    try:
        print('Welcome to PyWrappedDBs Benchmark!')
        print('- Testing DBs!')
        Tester().run()
        print('- Importing datasets!')
        BulkImporter().run()
        # print('- Benchmarking simple queries!')
        # SimpleBenchmark().run()
        # print('- Benchmarking complex algorithms!')
        # NetworkXBenchmark().run()
        # print('- Exporting stats!')
        # StatsExporter().run()
    finally:
        config.stats.dump_to_file()
