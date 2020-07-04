# PyWrappedDBs

A library (and set of benchmarks) of DB wrappers, which hide their unique interfaces behind simple-to-use purpose-specific wrappers for:

* Graphs (Networks),
* Textual Documents,
* Time Series.

The intention of this project was to find the best storage layer for [Unum](https://unum.xyz) neuro-symbolic AI models, so we compared all kinds of DBs: SQL & NoSQL, distributed & single-node, embedded databases & full scale servers. This library was tested with following backends: 

* [MongoDB](#mongodb) - modern (yet mature) distributed document DB with good performance in most workloads,
* [ElasticSearch](#elasticsearch) - extremely popular text-indexing software, 
* [Neo4J](#neo4j) - disturbingly slow and unstable DB positioned as the go-to Graph database, 
* [SQLite3](#sqlite3) - ubiquitous compact relation DB with basic `SQL` support, 
* [PostgreSQL](#postgresql) - most feature-rich open-source relational DB,
* [MySQL](#mysql) - the most commonly-used relational DB.

## Project Structure

* [PyWrappedGraph](PyWrappedGraph) - Python wrappers for Graph (Network) datastructures backed by persistent DBs.
* [BenchGraphs](BenchGraphs) - benchmarking tools and performance results for [PyWrappedGraph](PyWrappedGraph).
* [PyWrappedDocs](PyWrappedDocs) - Python wrappers for search-able containers of strings backed by persistent DBs.
* [BenchDocs](BenchDocs) - benchmarking tools and performance results for [PyWrappedDocs](PyWrappedDocs).

## Performance Considerations

After months-long analysis on different datasets and hardware - we decided to write a new high-performance database from scratch ([UnumDB](https://unum.xyz/db)). Below are some of the bottlenecks we have identified in most modern DBs. If you decide to write your own, those are the points to consider. 

|                           |          Common Solutions          |            What we use in UnumDB            |               **Result**                |
| :------------------------ | :--------------------------------: | :-----------------------------------------: | :-------------------------------------: |
| Data layout               |        Row-wise or columnar        |          Optimal for each datatype          |            Less random jumps            |
| Compression               |  Generic, but slow (Snappy, zlib)  | Newly invented algorithms for each datatype |         Writes/reads less data          |
| Query language            | SQL-like with big parsing overhead |           Simple Python-interface           |   Lower latency for simple operations   |
| Inter-node communications |               TCP/IP               |    DMA or Infiniband RDMA (in a cluster)    | Faster data exchange across the cluster |
| Data exchange format      |         Plain text or JSON         |                   Binary                    |        Avoids serialization step        |

Or just use [UnumDB](https://unum.xyz/db).

## Implementation Details & Included DBs

### MongoDB

* A distributed document storage. 
* Internally uses the `BSON` binary format.
* Very popular open-source project backed by the publicly traded `$MDB` enterprise.
* Provides bindings for most programming languages (including `pymongo` for Python).

### ElasticSearch

### SQLite3

* Embedded tabular SQL database with an extreme level of adoption.
* They provide a nice C API, but we use SQL for queries to make results comparable to PostgreSQL and MySQL. 
* We use SQLAlchemy library for Object-Relational-Mapping in Python, which is by far the most common Python ORM tool.
* SQlite is a single file databse, which makes it very easy configure for every workload. We overwrite the page size, Write-Ahead-Log format and concurrency settings for higher performance.

### PostgreSQL

* One of the most common open-source SQL databases.

### MySQL

* One of the most common open-source SQL databases.

### Neo4J

* The best known graph database with >10 year history.
* Instead of SQL uses CYPHER DSL for queries, which are transmitted over the BOLT API.
* There are some compatiability issues between API versions 3.5 and 4.
* Some of the essential indexing capabilities are not availiable in the free version.
* In our experience, extremely unstable and doesn't scale beyond tiny datasets.

## TODO

- [x] Benchmark on small graphs.
- [x] Benchmark on mid size graphs.
- [x] Session management in SQL and Neo4J.
- [x] Make benchmarks easier to read and control execution time.
- [ ] Add multithreaded benchmarks.
- [ ] ArangoDB wrapper.
- [ ] Mixed Read/Write benchmarks.
- [ ] NetworkX analytical wrapper and benchmarks.
- [ ] Time Series benchmarks.
