# PyGraphDB Benchmarks Overview

## Insert Dump (edges/sec)


Every datascience project starts by importing the data.
Let's see how long it will take to load an adjacency list into each DB.
But before comparing DBs, let's see what our SSD is capable of by simply parsing the list (2 or 3 column CSV).
This will be our baseline for estimating the time required to build the indexes in each DB.

|                   | graph-communities | graph-eachmovie-ratings | patent-citations | Result |
| :---------------- | :---------------: | :---------------------: | :--------------: | :----: |
| Parsing in Python |    490,068.94     |       564,322.69        |                  |   ?    |

|            | graph-communities | graph-eachmovie-ratings | patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------: | :----: |
| SQLiteMem  |     73,992.93     |        74,524.73        |                  |   ?    |
| SQLite     |     68,527.88     |        57,372.50        |                  |   ?    |
| MySQL      |     22,045.07     |        23,981.46        |                  |   ?    |
| PostgreSQL |     7,951.17      |        7,174.14         |                  |   ?    |
| MongoDB    |     8,863.45      |        14,832.76        |                  |   ?    |
| Neo4j      |      455.21       |                         |                  |   ?    |


Most DBs provide some form functionality for faster bulk imports, but not all of them where used in benchmarks for various reasons.

* Neo4J supports CSV imports, but it requires duplicating the imported file and constantly crashes (due to Java heap management issues).
* PostgreSQL and MySQL dialects of SQL have special functions for importing CSVs, but their functionality is very limited and performance gains aren't substantial. A better approach is to use unindexed table of incoming edges and later submit it into the main store once the data is absorbed.
* MongoDB provides a command line tool, but it wasn't used to limit the number of binary dependencies and simlify configuration.


|            | graph-communities | graph-eachmovie-ratings | patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------: | :----: |
| GraphLSM   |    119,314.66     |       534,250.90        |                  |   ?    |
| GraphBPlus |    204,365.92     |       207,143.17        |                  |   ?    |

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
|            | graph-communities | graph-eachmovie-ratings | patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------: | :----: |
| SQLiteMem  |                   |                         |                  |   ?    |
| SQLite     |      656.64       |         420.76          |                  |   ?    |
| MySQL      |     1,072.92      |                         |                  |   ?    |
| PostgreSQL |      840.35       |                         |                  |   ?    |
| MongoDB    |     2,655.66      |                         |                  |   ?    |
| Neo4j      |                   |                         |                  |   ?    |
| GraphLSM   |     46,640.69     |        3,206.06         |                  |   ?    |
| GraphBPlus |     1,339.74      |                         |                  |   ?    |

### Retrieve Undirected Edge

Given a pair of nodes - find any edge that connects them.
|            | graph-communities | graph-eachmovie-ratings | patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------: | :----: |
| SQLiteMem  |                   |                         |                  |   ?    |
| SQLite     |      682.46       |         382.87          |                  |   ?    |
| MySQL      |      973.20       |                         |                  |   ?    |
| PostgreSQL |      890.59       |                         |                  |   ?    |
| MongoDB    |     3,080.53      |                         |                  |   ?    |
| Neo4j      |                   |                         |                  |   ?    |
| GraphLSM   |     56,837.62     |        24,030.62        |                  |   ?    |
| GraphBPlus |     1,354.79      |                         |                  |   ?    |

### Retrieve Connected Edges

Find all directed edges that contain a specific node in any role.
|            | graph-communities | graph-eachmovie-ratings | patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------: | :----: |
| SQLiteMem  |                   |                         |                  |   ?    |
| SQLite     |      716.92       |          18.50          |                  |   ?    |
| MySQL      |      643.70       |                         |                  |   ?    |
| PostgreSQL |      910.70       |                         |                  |   ?    |
| MongoDB    |     2,682.58      |                         |                  |   ?    |
| Neo4j      |                   |                         |                  |   ?    |
| GraphLSM   |     12,193.76     |          44.52          |                  |   ?    |
| GraphBPlus |     13,168.71     |                         |                  |   ?    |

### Retrieve Outgoing Edges

Find all directed edges that start in a specific node.
|            | graph-communities | graph-eachmovie-ratings | patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------: | :----: |
| SQLiteMem  |                   |                         |                  |   ?    |
| SQLite     |      711.15       |          17.62          |                  |   ?    |
| MySQL      |      740.72       |                         |                  |   ?    |
| PostgreSQL |      910.29       |                         |                  |   ?    |
| MongoDB    |     2,876.23      |                         |                  |   ?    |
| Neo4j      |                   |                         |                  |   ?    |
| GraphLSM   |     12,330.82     |          40.29          |                  |   ?    |
| GraphBPlus |     1,356.34      |                         |                  |   ?    |

### Retrieve Friends

Get IDs of all nodes that share an edge with a given node.
|            | graph-communities | graph-eachmovie-ratings | patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------: | :----: |
| SQLiteMem  |                   |                         |                  |   ?    |
| SQLite     |      673.63       |          17.83          |                  |   ?    |
| MySQL      |      531.39       |                         |                  |   ?    |
| PostgreSQL |      908.78       |                         |                  |   ?    |
| MongoDB    |     3,109.96      |                         |                  |   ?    |
| Neo4j      |                   |                         |                  |   ?    |
| GraphLSM   |     13,046.63     |          46.64          |                  |   ?    |
| GraphBPlus |     18,836.18     |                         |                  |   ?    |

### Retrieve Friends of Friends

Get IDs of all nodes that share an edge with neighbors of a given node.
|            | graph-communities | graph-eachmovie-ratings | patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------: | :----: |
| SQLiteMem  |                   |                         |                  |   ?    |
| SQLite     |      226.19       |          0.08           |                  |   ?    |
| MySQL      |      165.94       |                         |                  |   ?    |
| PostgreSQL |      175.87       |                         |                  |   ?    |
| MongoDB    |     1,430.51      |                         |                  |   ?    |
| Neo4j      |                   |                         |                  |   ?    |
| GraphLSM   |      917.64       |          0.03           |                  |   ?    |
| GraphBPlus |      704.90       |                         |                  |   ?    |

### Count Friends

Count the number of edges containing a specific node and their total weight.
|            | graph-communities | graph-eachmovie-ratings | patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------: | :----: |
| SQLiteMem  |                   |                         |                  |   ?    |
| SQLite     |      623.74       |         483.06          |                  |   ?    |
| MySQL      |      842.55       |                         |                  |   ?    |
| PostgreSQL |      748.09       |                         |                  |   ?    |
| MongoDB    |     2,087.07      |                         |                  |   ?    |
| Neo4j      |                   |                         |                  |   ?    |
| GraphLSM   |     15,158.66     |          46.79          |                  |   ?    |
| GraphBPlus |     17,210.93     |                         |                  |   ?    |

### Count Followers

Count the number of edges ending in a specific node and their total weight.
|            | graph-communities | graph-eachmovie-ratings | patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------: | :----: |
| SQLiteMem  |                   |                         |                  |   ?    |
| SQLite     |      468.51       |          4.45           |                  |   ?    |
| MySQL      |     1,062.65      |                         |                  |   ?    |
| PostgreSQL |      778.25       |                         |                  |   ?    |
| MongoDB    |     2,172.86      |                         |                  |   ?    |
| Neo4j      |                   |                         |                  |   ?    |
| GraphLSM   |     14,473.62     |          47.20          |                  |   ?    |
| GraphBPlus |     1,270.27      |                         |                  |   ?    |

## Write Operations


We don't benchmark edge insertions as those operations are uncommon in graph workloads.
Instead of that we benchmark **upserts** = inserts or updates.
Batch operations have different sizes for different DBs depending on memory consumption
and other limitations of each DB.
Concurrency is tested only in systems that explicitly support it.

### Upsert Edge

|            | graph-communities | graph-eachmovie-ratings | patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------: | :----: |
| SQLiteMem  |                   |                         |                  |   ?    |
| SQLite     |      386.17       |         454.83          |                  |   ?    |
| MySQL      |      615.32       |                         |                  |   ?    |
| PostgreSQL |      666.96       |                         |                  |   ?    |
| MongoDB    |     3,178.74      |                         |                  |   ?    |
| Neo4j      |                   |                         |                  |   ?    |
| GraphLSM   |     13,345.08     |        3,925.93         |                  |   ?    |
| GraphBPlus |     1,750.36      |                         |                  |   ?    |

### Upsert Edges Batch

|            | graph-communities | graph-eachmovie-ratings | patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------: | :----: |
| SQLiteMem  |                   |                         |                  |   ?    |
| SQLite     |     1,395.34      |        1,088.85         |                  |   ?    |
| MySQL      |      890.93       |                         |                  |   ?    |
| PostgreSQL |      950.84       |                         |                  |   ?    |
| MongoDB    |     13,729.85     |                         |                  |   ?    |
| Neo4j      |                   |                         |                  |   ?    |
| GraphLSM   |     78,205.83     |        5,753.74         |                  |   ?    |
| GraphBPlus |     18,428.76     |                         |                  |   ?    |

### Remove Edge

|            | graph-communities | graph-eachmovie-ratings | patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------: | :----: |
| SQLiteMem  |                   |                         |                  |   ?    |
| SQLite     |      613.05       |         565.12          |                  |   ?    |
| MySQL      |     1,045.80      |                         |                  |   ?    |
| PostgreSQL |     1,320.79      |                         |                  |   ?    |
| MongoDB    |     3,366.41      |                         |                  |   ?    |
| Neo4j      |                   |                         |                  |   ?    |
| GraphLSM   |     9,766.94      |        4,210.60         |                  |   ?    |
| GraphBPlus |     1,762.28      |                         |                  |   ?    |

### Remove Edges Batch

|            | graph-communities | graph-eachmovie-ratings | patent-citations | Result |
| :--------- | :---------------: | :---------------------: | :--------------: | :----: |
| SQLiteMem  |                   |                         |                  |   ?    |
| SQLite     |      631.44       |         619.41          |                  |   ?    |
| MySQL      |      919.22       |                         |                  |   ?    |
| PostgreSQL |     1,307.67      |                         |                  |   ?    |
| MongoDB    |     2,834.11      |                         |                  |   ?    |
| Neo4j      |                   |                         |                  |   ?    |
| GraphLSM   |     77,003.51     |        5,476.70         |                  |   ?    |
| GraphBPlus |     1,758.83      |                         |                  |   ?    |

## Device


* CPU: 8 cores, 16 threads @ 2300.00Mhz.
* RAM: 16.00 Gb
* Disk: 931.55 Gb
* OS: Darwin

