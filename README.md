# PyWrappedDBs

A library (and benchmark) of graph-like adaptors for conventional persistent storage engines. <br/>
Supports both SQL and NoSQL backends, embedded databases and full scale servers. <br/>
Was benchmarked with MongoDB, Neo4J, *ArangoDB*, SQLite, PostgreSQL and MySQL backends. <br/>
Implements the same [interface](adapters/base.py) for every one of those backends.

## Project Structure

* [pygraphdb](pygraphdb) - contains Pythonic wrappers for DBs.
* [bench](bench) - contains benchmark programs and results for different hardware.
* [bench/stats_*/stats.json](bench/MacbookPro/stats.json) - contains machine-readable results of previous benchmarks.
* [bench/stats_*/stats.md](bench/MacbookPro/stats.md) - contains human-readable results of previous benchmarks.

## Implementation Details & Included DBs

### MongoDB

* A distributed document storage. Fast growing project, but performance isnt the primary objective.
* Each edge is a separate BSON document with 2 separate indexes for source and target nodes.
* Each dataset is stored in it's own database within MongoDB instance. MongoDB is configured to put them in separate directories.
* We connect to it using `pymongo` bindings.

### Neo4J

* A graph database. Best known product in its segment.
* All datasets are stored in the same database (but with different labels), as Neo4J doesnt provide and easy way to switch between collections.
* The implementation isn't properly optimized due to compatiability issues between API versions 3.5 and 4, constant crashes and limited community edition.
* We were not able to index properties of edges, as its a paid feature.
* We connect to it over BOLT API and encode requests manually into CYPHER query DSL.

### SQLite3

* Embedded tabular SQL database with extreme level of adoption.
* They provide a nice C API, but we use SQL for queries to make results comparable to PostgreSQL and MySQL. We use SQLAlchemy library for Object-Relational-Mapping in Python, which is by far the most common tool for that.
* We also include in-memory variant of SQLite for comparison purposes. If you wish to see how other DBs perform in-memory, just mount them on RAM drive.
* SQlite is a single file databse, which makes it very easy configure for every workload. We cutomize the page size, Write-Ahead-Log format and concurrency settings for higher performance.
* As in other SQL databases we store 3 tables of data (`table_nodes`, `table_edges` and `new_edges` for bulk imports), but no relations between them to make queries less complex. However, the main properties of each edge (`v1`, `v2`, `directed`) are indexed which must easily compensate the lack of direct connection between tables.

### PostgreSQL

* One of the most common open-source SQL databases.
* Data layout that we use is the same as for SQLite3, but with less configuration.
* Each dataset is stored in it's own database within Postregres instance.

### MySQL

* One of the most common open-source SQL databases.
* Data layout that we use is the same as for SQLite3, but with less configuration.
* Each dataset is stored in it's own database within MySQL instance.

### UnumDB

* Our in-house closed-source solution for storing graphs.
* The binaries aren't included, now we can only share some benchmarks.

## TODO

- [x] Benchmark on small graphs.
- [x] Benchmark on mid size graphs.
- [x] Session management in SQL and Neo4J.
- [ ] Make benchmarks easier to read and control execution time.
- [ ] Add multithreaded benchmarks.
- [ ] ArangoDB wrapper.
- [ ] Mixed Read/Write benchmarks.
- [ ] NetworkX analytical wrapper and benchmarks.
- [ ] Compare to CompressedGraphLSM.
