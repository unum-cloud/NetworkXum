# NetworkXum

NetworkXum is [NetworkX](https://github.com/networkx/networkx)-like interface for large persistent graphs stored inside DBMS. This lets you upscale from Megabyte-Gigabyte graphs to Terabyte-Petabyte graphs (that won't fit into RAM), without changing your code. We provide wrappers for following DBs:

* [MongoDB](#mongodb) - modern (yet mature) distributed document DB with good performance in most workloads
* [Neo4J](#neo4j) - disturbingly slow and unstable DBMS positioned as the go-to Graph database,
* [SQLite3](#sqlite3) - ubiquitous compact relational DBMS with basic `SQL` support,
* [PostgreSQL](#postgresql) - most feature-rich open-source relational DB,
* [MySQL](#mysql) - the most commonly-used relational DB.

## Project Structure

* [networkxum](networkxum) - Python wrappers for Graph (Network) datastructures backed by persistent DBs.
* [benchmarks](benchmarks) - benchmarking tools and performance results.
* [assets](assets) - tiny datasets for testing purposes.
* [regexum](PyStorageTexts) - Python wrappers for search-able containers backed by persistent DBs.
* [benchmarks](benchmarks) - benchmarking tools and performance results.
* [assets](assets) - tiny datasets for testing purposes.

## Implementation Details & Included DBs

Some common databases have licences that prohibit sharing of benchmark results, so they were excluded from comparisons.

|     Name      |       Purpose       | Implementation Language | Lines of Code (in `/src/`) |
| :-----------: | :-----------------: | :---------------------: | :------------------------: |
|    MongoDB    |      Documents      |           C++           |         3'900'000          |
|    Postgre    |       Tables        |            C            |         1'300'000          |
|     Neo4J     |       Graphs        |          Java           |          800'000           |
| ElasticSearch |        Text         |          Java           |          730'000           |
|     Unum      | Graphs, Table, Text |           C++           |           80'000           |

### MongoDB

* A distributed ACID document store.
* Internally uses the `BSON` binary format.
* Very popular open-source project backed by the `$MDB` [publicly traded company](https://finance.yahoo.com/quote/MDB).
* Provides bindings for most programming languages (including [PyMongo](https://pymongo.readthedocs.io) for Python).

### ElasticSearch

* Java-based document store built on top of Lucene text index.
* Widely considered high-performance solutions due to the lack of competition.
* Lucene was ported to multiple languages including projects like: [CLucene](http://clucene.sourceforge.net) and [LucenePlusPlus](https://github.com/luceneplusplus/LucenePlusPlus).
* Very popular open-source project backed by the `$ESTC` [publicly traded company](https://finance.yahoo.com/quote/ESTC).

### SQLite3

* Embedded tabular single-file SQL database with an extreme level of adoption.
* Provides a more direct C API in addition to the SQL interface. 
* We use SQLAlchemy for Object-Relational-Mapping, which is by far the most common Python ORM tool.
* We overwrite the page size, Write-Ahead-Log format and concurrency settings for higher performance.

### Postgre, MySQL and other SQLs

* Most common open-source SQL databases.
* Work well in single-node environment, but scale poorly out of the box.
* Mostly store search indexes in a form of a [B-Tree](https://ieftimov.com/post/postgresql-indexes-btree/). They generally provide good read performance, but are slow to update.

### Neo4J

* The best known graph database with over 10 year of history.
* Instead of SQL provides [Cyper DSL](https://neo4j.com/developer/cypher-query-language/) for queries, which are transmitted using [Bolt protocol](https://en.wikipedia.org/wiki/Bolt_(network_protocol)).
* Some of the essential indexing capabilities are not availiable in the free version.
* There are some compatiability issues between API versions 3.5 and 4.
* In our experience, Neo4J is extremely unstable and doesn't scale beyond tiny datasets. Generally crashes due to Java VM heap management issues.

## TODO

* [x] Benchmark on small & mid graphs.
* [x] Session management in SQL and Neo4J.
* [x] Duration constraints for benchmarks.
* [ ] Mixed Multithreaded Read/Write benchmarks.
