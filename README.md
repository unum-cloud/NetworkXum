# NetworkXternal

![NetworkXternal thumbnail](https://github.com/ashvardanian/ashvardanian/raw/master/repositories/NetworkXternal.jpg?raw=true)

NetworkXternal is [NetworkX](https://github.com/networkx/networkx)-like interface for external memory graphs persisted in various databases.
This lets you upscale from Megabyte-Gigabyte graphs to Terabyte-Petabyte graphs (that won't fit into RAM), without changing your code.
It's not a silver bullet, as it comes with a performance penalty, but it can be a good place to start.

The library was designed to be compatible with the following databases:

- [MongoDB](#mongodb) - modern (yet mature) distributed document DB,
- [Neo4J](#neo4j) - disturbingly slow and unstable DBMS positioned as the go-to Graph database,
- [SQLite3](#sqlite3) - ubiquitous compact relational DBMS with basic `SQL` support,
- [PostgreSQL](#postgresql) - most feature-rich open-source relational DB,
- [MySQL](#mysql) - the most commonly-used relational DB.

## Project Structure

- [networkxternal](networkxternal) - `Graph`-like DBMS client wrappers.
- [benchmarks](benchmarks) - benchmarking tools and performance results.
- [assets](assets) - toy datasets for testing purposes.

### Compared DBs

Some common databases have licenses that prohibit sharing of benchmark results, so they were excluded from comparisons.

| Name     |             Purpose | Implementation | Code Length in `/src/**` |
| :------- | ------------------: | -------------: | -----------------------: |
| MongoDB  |           Documents |            C++ |          3'900'000 lines |
| Postgres |              Tables |              C |          1'300'000 lines |
| Neo4J    |              Graphs |           Java |            800'000 lines |
| UStore   | Graphs, Table, Text |            C++ |             80'000 lines |

#### MongoDB

- A distributed ACID document store.
- Internally uses the `BSON` binary format.
- Very popular open-source project backed by the `$MDB` [publicly traded company](https://finance.yahoo.com/quote/MDB).
- Provides bindings for most programming languages (including [PyMongo](https://pymongo.readthedocs.io) for Python).

#### SQLite3

- Embedded tabular single-file SQL database with an extreme level of adoption.
- Provides a more direct C API in addition to the SQL interface. 
- We use SQLAlchemy for Object-Relational-Mapping, which is by far the most common Python ORM tool.
- We overwrite the page size, Write-Ahead-Log format and concurrency settings for higher performance.

#### Postgres, MySQL & other SQLs

- Most common open-source SQL databases.
- Work well in single-node environment, but scale poorly out of the box.
- Mostly store search indexes in a form of a [B-Tree](https://ieftimov.com/post/postgresql-indexes-btree/). They generally provide good read performance, but are slow to update.

#### Neo4J

- The best known graph database with over 10 year of history.
- Instead of SQL provides [Cypher DSL](https://neo4j.com/developer/cypher-query-language/) for queries, which are transmitted using [Bolt protocol](https://en.wikipedia.org/wiki/Bolt_(network_protocol)).
- Some of the essential indexing capabilities are not available in the free version.
- There are some compatibility issues between API versions 3.5 and 4.
- In our experience, Neo4J is extremely unstable and doesn't scale beyond tiny datasets. Generally crashes due to Java VM heap management issues.

## TODO

- [x] Benchmark on small & mid graphs.
- [x] Session management in SQL and Neo4J.
- [x] Duration constraints for benchmarks.
- [ ] Testing suite.
- [ ] Refactor benchmarks and include MemGraph.
- [ ] Mixed multithreaded Read/Write benchmarks in GIL-less Python 3.13.


## Building

```sh
uv build # To build the project
uv venv  # To create a development environment
uv run ruff check
```
