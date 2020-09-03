# Benchmarking DBs on Graph Workloads with PyWrappedDBs

The intention of benchmarks was to see, how well various DBs can handle graph workloads.
If you are not familiar with graphs, its just a mathematical term to describe relations between different points.
The only thing you need to know from terminology is that `point=node=vertex` and `edge=relation`.

Some DBs were originally designed for faster queries over complex graphs, but it doesnt mean they are good at it.
Feel free to replicate and share the results!

## Stages

The application is split into multiple stages, each with it's own file, so you can each stage separately as a script.

* [P1Test.py](P1Test.py) - Validates if connections can be established, basic operations work as intended and dump file paths are accessible.
* [P2Import.py](P2Import.py) - Bulk-loads data into DBs for future analysis. Files must be CSVs with a header row: `first,second,weight`.
* [P3Bench.py](P3Bench.py) - Benchmarks simple `GET`, `PUT` for single nodes/edges and batches of them.
* [P4Print.py](P4Print.py) - Exports stats about each type of operations from `stats.json` into a single `stats.md` report.

## Setup

Testing and benchmarking was done on 16" 2019 MacBook Pro. The simplest approach is to test using Docker Compose to start sandboxed DB instances, but [it comes with sacrifices on other platforms.](https://github.com/docker/for-mac/issues/1592). In case you are running this on the mac - call `run_mac.sh`, otherwise - `run_textker.sh`.

Docker engine can't talk to Apple File System directly, and the `osxfs` [intermediate layer is a lot slower than native storage](https://docs.docker.com/docker-for-mac/osxfs/#performance-issues-solutions-and-roadmap). With a classical block-based file system, the access latency is typically under 10μs (microseconds). With `osxfs`, latency is presently around 130μs for most operations (or 13× slower). Throughput for bulk operations doesn't exceed 250 MB/s, while the drive is capable of 3 GB/s (or 12× slower). Even in operations with huge batch sizes the performance was at least 4 times lower than native storage.

## Environment Variables

```sh
URI_FILE="~/Downloads/archieve.edges" # Can be a local CSV file or archeive.
URI_MONGODB="mongodb://localhost:27017" # Clear to disable Mongo benchmarks.
URI_POSTGRESQL="postgres://localhost:5432" # Clear to disable Postgres benchmarks.
URI_MYSQL="mysql://localhost:3306" # Clear to disable MySQL benchmarks.
URI_SQLITE="/var/lib/sqlite/" # Clear to disable SQLite benchmarks.
URI_SQLITE_RAM="sqlite:///:memory:"  # Clear to disable in-memory SQLite benchmarks.
```

## Benchmarking the Benchmark

If you want to improve the benchmarks and make sure no time is wasted on needless operations use `pyinstrument`. The app is too complex to validate it with `cProfile` and the stats tables are impossible to navigate.

```sh
python -m pyinstrument P2Import.py
```
