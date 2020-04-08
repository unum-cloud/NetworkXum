
from p1_test import Tester
from p2_import import BulkImporter
from p4_bench_simple import SimpleBenchmark
from p5_bench_networkx import NetworkXBenchmark
# from p6_export_stats_dataset import StatsExporter


if __name__ == "__main__":
    print('Welcome to PyGraphDB Benchmark!')
    print('- Testing DBs!')
    Tester().run()
    print('- Importing datasets!')
    BulkImporter().run()
    print('- Benchmarking simple queries!')
    SimpleBenchmark().run()
    print('- Benchmarking complex algorithms!')
    NetworkXBenchmark().run()
    # print('- Exporting stats!')
    # StatsExporter().run()
