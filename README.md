# PyStorage

A library (and a set of benchmarks) of DB wrappers, which hide their unique interfaces behind simple-to-use purpose-specific wrappers for:

* Graphs (Networks) - modeled after NetworkX interface,
* Textual Documents - modeled after ElasticSearch interface.

The intention of this project was to find the best storage layer for [Unum](https://unum.xyz) neuro-symbolic AI models, so we compared all kinds of DBs: SQL & NoSQL, distributed & single-node, embedded databases & full scale servers. This library was tested with following backends: 

* [MongoDB](#mongodb) - modern (yet mature) distributed document DB with good performance in most workloads,
* [ElasticSearch](#elasticsearch) - extremely popular text-indexing software, 
* [Neo4J](#neo4j) - disturbingly slow and unstable DB positioned as the go-to Graph database, 
* [SQLite3](#sqlite3) - ubiquitous compact relation DB with basic `SQL` support, 
* [PostgreSQL](#postgresql) - most feature-rich open-source relational DB,
* [MySQL](#mysql) - the most commonly-used relational DB.

## Project Structure

* [PyWrappedGraph](PyWrappedGraph) - Python wrappers for Graph (Network) datastructures backed by persistent DBs.
* [PyStoragehs](BenPyStorage - benchmarking tools and performance results for [PyWrappedGraph](PyWrappedGraph).
* [PyWrappedTexts](PyWrappedTexts) - Python wrappers for search-able containersPyStoragegs backPyStoragesistent DBs.
* [PyStorages](BencPyStorage benchmarking tools and performance results for [PyWrappedTexts](PyWrappedTexts).
PyStoragePyStorage
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

## Performance Considerations

After months-long analysis on different datasets and hardware - we decided to write a new high-performance database from scratch ([UnumDB](https://unum.xyz/db)). Below are some of the bottlenecks we have identified in most modern DBs. If you decide to write your own, those are the points to consider. 

|                           |            Common Solutions             |            What we use in UnumDB            |                **Result**                | Device |
| :------------------------ | :-------------------------------------: | :-----------------------------------------: | :--------------------------------------: | :----: |
| Data layout               |          Row-wise or columnar           |          Optimal for each datatype          |         Less random jumps on SSD         |   💾    |
| Compression               |    Generic, but slow (Snappy, zlib)     | Newly invented algorithms for each datatype |   Writes/reads less bytes to/from SSD    |   💾    |
| Integrated Analytics      |     Integrating 3rd party libraries     |           Co-designed algorithms            | Optimal use of search indexes & metadata |   🧠    |
| Computations              |               Sequential                |              SIMD-Accelerated               |   Processing more bytes per CPU cycle    |   🧠    |
| Query language            |   SQL-like with big parsing overhead    |           Simple Python-interface           |   Lower latency for simple operations    |   🧠    |
| Memory management         |      Garbage collecting languages       |       Modern C++ with smart pointers        |     Reusing RAM & avoiding GC stalls     |   🐏    |
| In-Memory copies          | 1+ per read/write + DB cache + OS cache |      1 per write + DB cache + OS cache      |     Fitting more data-points in RAM      |   🐏    |
| Parallelism               |            Multi-processing             |        Asynchronous multi-threading         |     Faster sharing between CPU cores     |   🧠    |
| Inter-node communications |                 TCP/IP                  |    DMA or Infiniband RDMA (in a cluster)    |      Faster sharing between servers      |   📡    |
| Data exchange format      |           Plain text or JSON            |                   Binary                    |     No serialization overhead on CPU     |   🧠    |

Or just use [UnumDB](https://unum.xyz/db), it's free. **Currently you can expect 5x-100x better DB performance across the board**. We are on track to implement a lot more optimizations than listed above. If you decide to switch to a more mature DB later on - you will only have to change 1 line in your code.

## TODO

* [x] Benchmark on small & mid graphs.
* [x] Session management in SQL and Neo4J.
* [x] Durration constraints for benchmarks.
* [ ] Mixed Multithreaded Read/Write benchmarks.
* [ ] Time Series benchmarks.
