# Benchmarking DBs on Textual Workloads with PyStorageDBs

The intention of benchmarks was to see, how well various DBs can handle textual workloads, such as: substring search and RegEx pattern matching.
Most DBs have text indexing capabilities, but the performance and space consumption differs a lot.
Feel free to replicate and share the results!

## Stages

The application is split into multiple stages, each with it's own file, so you can each stage separately as a script.

* [P1Test.py](P1Test.py) - Validates if connections can be established, basic operations work as intended and dump file paths are accessible.
* [P2Import.py](P2Import.py) - Bulk-loads data into DBs for future analysis. Files must be CSVs with a header row: `article_id,article_title,section_title,section_text`.
* [P3Bench.py](P3Bench.py) - Benchmarks simple search queries and indexing capabilies for single documents and batches of them.
* [P4Print.py](P4Print.py) - Exports stats about each type of operations from `stats.json` into a single `stats.md` report.
