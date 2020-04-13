# PyGraphDB Benchmark

The purpose of those benchmarks is to compare conventional SQL and modern NoSQL databases in graph operations. The application is split into multiple stages, each with it's own file, so you can each stage separately as a script.

* [p1_test.py](p1_test.py) - Validates if connections can be established, basic operations work as intended and dump file paths are accessible.
* [p2_import.py](p2_import.py) - Bulk-loads data into DBs for future analysis. Files must be CSVs with a header row: `v1,v2,weight`.
* [p3_bench_simple.py](p3_bench_simple.py) - Benchmarks simple `GET`, `PUT` for single nodes/edges and batches of them.
* [p4_bench_networkx.py](p4_bench_networkx.py) - Select graph algorithms applied to persistent data.
* [p5_export_stats_operation.py](p5_export_stats_operation.py) - Exports stats about each type of operations from `artifacts/stats.json` into a single report.
* [p6_export_stats_dataset.py](p6_export_stats_dataset.py) - Exports all stats related to same dataset from `artifacts/stats.json` into a single report.

## Results

The results are presented in [artifacts folder](https://github.com/ashvardanian/PyGraphDB/artifacts).

## Setup

Testing and benchmarking was done on 16" 2019 MacBook Pro. The simplest approach is to test using Docker Compose to start sandboxed DB instances, but [it comes with sacrifices on other platforms.](https://github.com/docker/for-mac/issues/1592). In case you are running this on the mac - call `run_mac.sh`, otherwise - `run_docker.sh`.
