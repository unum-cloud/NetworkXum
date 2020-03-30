# PyGraphDB

A library (and benchmark) of graph-like adaptors for conventional persistent storage engines. <br/>
Supports both SQL and NoSQL backends, embedded databases and full scale servers. <br/>
Was benchmarked with MongoDB, RocksDB, ArangoDB, SQLite, PostgreSQL and MySQL backends. <br/>
Implements the same [interface](adapters/base.py) for every one of those backends.

## Project Structure

* [pygraphdb](pygraphdb) - contains Pythonic wrappers for DBs.
* [artifacts/stats.json](artifacts/stats.json) - contains machine-readable results of previous benchmarks.
* [artifacts/stats.md](artifacts/stats.md) - contains human-readable results of previous benchmarks.
* [bench/Dockerfile](bench/Dockerfile) - contains Docker image of benchmark application.
* [bench/docker-compose.yml](bench/docker-compose.yml) - instantiates that image for selected datasets and alse spins up infrastructure for testing. Comment out the second part of it if you don't want to create new DB containers.

## Environment Variables

```sh
URI_FILE="~/Downloads/archieve.edges" # Can be a local CSV file or archeive.
URI_MONGO_DB="mongodb://localhost:27017" # Clear to disable Mongo benchmarks.
URI_POSTGRES="postgres://localhost:5432" # Clear to disable Postgres benchmarks.
URI_MY_SQL="mysql://localhost:3306" # Clear to disable MySQL benchmarks.
URI_ROCKS_DB="/var/lib/rocksdb/" # Clear to disable RocksDB benchmarks.
URI_SQLITE="/var/lib/sqlite/" # Clear to disable SQLite benchmarks.
URI_SQLITE_MEM="sqlite:///:memory:"  # Clear to disable in-memory SQLite benchmarks.
```

Remaining can be found listed in the [Dockerfile](Dockerfile).

## Datasets

This application accepts data in a shape of adjacency list. <br/>
The Docker image will download the file from `${FILE_URL}` and unpack it if it's an archeive. <br/>
Here are some relatively big graphs you can use for benchmarks:

* Orkut social network. 2Gb. `|V|`=3M, `|E|`=117M. [Source](http://networkrepository.com/orkut.php).
* Sina Weibo social network. 2Gb. `|V|`=21M, `|E|`=261M. [Source](http://networkrepository.com/soc-sinaweibo.php).
* Twitter social network. 6Gb. `|V|`=58M, `|E|`=265M. [Source](http://networkrepository.com/soc-twitter.php).
* Friendster social network. 9Gb. `|V|`=65M, `|E|`=1.8B. [Source](http://networkrepository.com/soc-friendster.php).
* ClueWeb 2009 network. 40Gb. `|V|`=1.7B, `|E|`=7.8B. [Source](http://networkrepository.com/web-ClueWeb09.php).

## Related notes

* Alternative Graph Storage Approaches
* Untouched datasets
* PyCler Graph DBs benchmark
