# PyGraphDB Benchmarks Overview

## Insert Dump (edges/sec)

Every datascience project starts by importing the data.
Let's see how long it will take to load an adjacency list into each DB.
But before comparing DBs, let's see what our SSD is capable of by simply parsing the list (2 or 3 column CSV).
This will be our baseline for estimating the time required to build the indexes in each DB.

|                   | graph-communities | graph-eachmovie-ratings | graph-patent-citations |   Result   |
| :---------------- | :---------------: | :---------------------: | :--------------------: | :--------: |
| Parsing in Python |    490,068.94     |       564,322.69        |       617,139.11       | :thumbsup: |

|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----------: |
| SQLiteMem  |     73,992.93     |        74,524.73        |       71,887.72        |  :thumbsup:  |
| SQLite     |     68,527.88     |        57,372.50        |       44,137.56        |              |
| MySQL      |     22,045.07     |        23,981.46        |       14,636.07        | :thumbsdown: |
| PostgreSQL |     7,951.17      |        7,174.14         |        7,230.86        | :thumbsdown: |
| MongoDB    |     8,863.45      |        14,832.76        |       14,199.87        | :thumbsdown: |
| Neo4j      |     17,279.18     |                         |                        |      ?       |

Most DBs provide some form functionality for faster bulk imports, but not all of them where used in benchmarks for various reasons.

* Neo4J supports CSV imports, but it requires duplicating the imported file and constantly crashes (due to Java heap management issues).
* PostgreSQL and MySQL dialects of SQL have special functions for importing CSVs, but their functionality is very limited and performance gains aren't substantial. A better approach is to use unindexed table of incoming edges and later submit it into the main store once the data is absorbed.
* MongoDB provides a command line tool, but it wasn't used to limit the number of binary dependencies and simlify configuration.

|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----------: |
| GraphLSM   |    119,314.66     |       490,707.11        |       135,714.61       |  :thumbsup:  |
| GraphBPlus |    204,365.92     |       207,143.17        |       113,372.62       | :thumbsdown: |

## Read Queries

Following are simple lookup operations.
Their speed translates into the execution time of analytical queries like:

* Shortest Path Calculation,
* Clustering Analysis,
* Pattern Matching.

As we are running on a local machine and within the same filesystem,
the networking bandwidth and latency between server and client applications
can't be a bottleneck.

### Retrieve Directed Edge

Given nodes A and B - find any directed edge that goes from A to B.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----: |
| SQLiteMem  |                   |                         |                        |   ?    |
| SQLite     |                   |                         |                        |   ?    |
| MySQL      |                   |                         |                        |   ?    |
| PostgreSQL |                   |                         |                        |   ?    |
| MongoDB    |                   |                         |                        |   ?    |
| Neo4j      |                   |                         |                        |   ?    |
| GraphLSM   |                   |                         |                        |   ?    |
| GraphBPlus |                   |                         |                        |   ?    |

### Retrieve Undirected Edge

Given a pair of nodes - find any edge that connects them.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----: |
| SQLiteMem  |                   |                         |                        |   ?    |
| SQLite     |                   |                         |                        |   ?    |
| MySQL      |                   |                         |                        |   ?    |
| PostgreSQL |                   |                         |                        |   ?    |
| MongoDB    |                   |                         |                        |   ?    |
| Neo4j      |                   |                         |                        |   ?    |
| GraphLSM   |                   |                         |                        |   ?    |
| GraphBPlus |                   |                         |                        |   ?    |

### Retrieve Connected Edges

Find all directed edges that contain a specific node in any role.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----: |
| SQLiteMem  |                   |                         |                        |   ?    |
| SQLite     |                   |                         |                        |   ?    |
| MySQL      |                   |                         |                        |   ?    |
| PostgreSQL |                   |                         |                        |   ?    |
| MongoDB    |                   |                         |                        |   ?    |
| Neo4j      |                   |                         |                        |   ?    |
| GraphLSM   |                   |                         |                        |   ?    |
| GraphBPlus |                   |                         |                        |   ?    |

### Retrieve Outgoing Edges

Find all directed edges that start in a specific node.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----: |
| SQLiteMem  |                   |                         |                        |   ?    |
| SQLite     |                   |                         |                        |   ?    |
| MySQL      |                   |                         |                        |   ?    |
| PostgreSQL |                   |                         |                        |   ?    |
| MongoDB    |                   |                         |                        |   ?    |
| Neo4j      |                   |                         |                        |   ?    |
| GraphLSM   |                   |                         |                        |   ?    |
| GraphBPlus |                   |                         |                        |   ?    |

### Retrieve Friends

Get IDs of all nodes that share an edge with a given node.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----: |
| SQLiteMem  |                   |                         |                        |   ?    |
| SQLite     |                   |                         |                        |   ?    |
| MySQL      |                   |                         |                        |   ?    |
| PostgreSQL |                   |                         |                        |   ?    |
| MongoDB    |                   |                         |                        |   ?    |
| Neo4j      |                   |                         |                        |   ?    |
| GraphLSM   |                   |                         |                        |   ?    |
| GraphBPlus |                   |                         |                        |   ?    |

### Retrieve Friends of Friends

Get IDs of all nodes that share an edge with neighbors of a given node.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----: |
| SQLiteMem  |                   |                         |                        |   ?    |
| SQLite     |                   |                         |                        |   ?    |
| MySQL      |                   |                         |                        |   ?    |
| PostgreSQL |                   |                         |                        |   ?    |
| MongoDB    |                   |                         |                        |   ?    |
| Neo4j      |                   |                         |                        |   ?    |
| GraphLSM   |                   |                         |                        |   ?    |
| GraphBPlus |                   |                         |                        |   ?    |

### Count Friends

Count the number of edges containing a specific node and their total weight.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----: |
| SQLiteMem  |                   |                         |                        |   ?    |
| SQLite     |                   |                         |                        |   ?    |
| MySQL      |                   |                         |                        |   ?    |
| PostgreSQL |                   |                         |                        |   ?    |
| MongoDB    |                   |                         |                        |   ?    |
| Neo4j      |                   |                         |                        |   ?    |
| GraphLSM   |                   |                         |                        |   ?    |
| GraphBPlus |                   |                         |                        |   ?    |

### Count Followers

Count the number of edges ending in a specific node and their total weight.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----: |
| SQLiteMem  |                   |                         |                        |   ?    |
| SQLite     |                   |                         |                        |   ?    |
| MySQL      |                   |                         |                        |   ?    |
| PostgreSQL |                   |                         |                        |   ?    |
| MongoDB    |                   |                         |                        |   ?    |
| Neo4j      |                   |                         |                        |   ?    |
| GraphLSM   |                   |                         |                        |   ?    |
| GraphBPlus |                   |                         |                        |   ?    |

## Write Operations

We don't benchmark edge insertions as those operations are uncommon in graph workloads.
Instead of that we benchmark **upserts** = inserts or updates.
Batch operations have different sizes for different DBs depending on memory consumption
and other limitations of each DB.
Concurrency is tested only in systems that explicitly support it.

### Upsert Edge

|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----: |
| SQLiteMem  |                   |                         |                        |   ?    |
| SQLite     |                   |                         |                        |   ?    |
| MySQL      |                   |                         |                        |   ?    |
| PostgreSQL |                   |                         |                        |   ?    |
| MongoDB    |                   |                         |                        |   ?    |
| Neo4j      |                   |                         |                        |   ?    |
| GraphLSM   |                   |                         |                        |   ?    |
| GraphBPlus |                   |                         |                        |   ?    |

### Upsert Edges Batch

|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----: |
| SQLiteMem  |                   |                         |                        |   ?    |
| SQLite     |                   |                         |                        |   ?    |
| MySQL      |                   |                         |                        |   ?    |
| PostgreSQL |                   |                         |                        |   ?    |
| MongoDB    |                   |                         |                        |   ?    |
| Neo4j      |                   |                         |                        |   ?    |
| GraphLSM   |                   |                         |                        |   ?    |
| GraphBPlus |                   |                         |                        |   ?    |

### Remove Edge

|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----: |
| SQLiteMem  |                   |                         |                        |   ?    |
| SQLite     |                   |                         |                        |   ?    |
| MySQL      |                   |                         |                        |   ?    |
| PostgreSQL |                   |                         |                        |   ?    |
| MongoDB    |                   |                         |                        |   ?    |
| Neo4j      |                   |                         |                        |   ?    |
| GraphLSM   |                   |                         |                        |   ?    |
| GraphBPlus |                   |                         |                        |   ?    |

### Remove Edges Batch

|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----: |
| SQLiteMem  |                   |                         |                        |   ?    |
| SQLite     |                   |                         |                        |   ?    |
| MySQL      |                   |                         |                        |   ?    |
| PostgreSQL |                   |                         |                        |   ?    |
| MongoDB    |                   |                         |                        |   ?    |
| Neo4j      |                   |                         |                        |   ?    |
| GraphLSM   |                   |                         |                        |   ?    |
| GraphBPlus |                   |                         |                        |   ?    |

