# PyGraphDB Benchmarks Overview

## Insert Dump (edges/sec)


Every datascience project starts by importing the data.
Let's see how long it will take to load an adjacency list into each DB.
But before comparing DBs, let's see what our SSD is capable of by simply parsing the list (2 or 3 column CSV).
This will be our baseline for estimating the time required to build the indexes in each DB.

|                   | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | Result |
| :---------------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----: |
| Parsing in Python |    490,068.94     |       564,322.69        |       617,139.11       |                  |   ?    |
| SQLiteMem         |     73,992.93     |        74,524.73        |       71,887.72        |                  |   ?    |

|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----: |
| SQLite     |     68,527.88     |        57,372.50        |       44,137.56        |                  |   ?    |
| MySQL      |     22,045.07     |        23,981.46        |       14,636.07        |                  |   ?    |
| PostgreSQL |     7,951.17      |        7,174.14         |        7,230.86        |                  |   ?    |
| MongoDB    |     8,863.45      |        14,832.76        |       14,199.87        |                  |   ?    |
| Neo4J      |      455.21       |                         |                        |                  |   ?    |


Most DBs provide some form functionality for faster bulk imports, but not all of them where used in benchmarks for various reasons.

* Neo4J supports CSV imports, but it requires duplicating the imported file and constantly crashes (due to Java heap management issues).
* PostgreSQL and MySQL dialects of SQL have special functions for importing CSVs, but their functionality is very limited and performance gains aren't substantial. A better approach is to use unindexed table of incoming edges and later submit it into the main store once the data is absorbed.
* MongoDB provides a command line tool, but it wasn't used to limit the number of binary dependencies and simlify configuration.


|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----: |
| GraphBPlus |    204,365.92     |       207,143.17        |       113,372.62       |                  |   ?    |
| GraphLSM   |    119,314.66     |       534,250.90        |       135,714.61       |                  |   ?    |

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
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----: |
| SQLite     |      709.98       |         629.05          |                        |                  |   ?    |
| MySQL      |     1,067.25      |         757.05          |                        |                  |   ?    |
| PostgreSQL |      977.48       |         495.16          |                        |                  |   ?    |
| MongoDB    |     3,396.74      |        2,503.34         |                        |                  |   ?    |
| GraphBPlus |     1,339.74      |                         |                        |                  |   ?    |
| GraphLSM   |     46,640.69     |        3,206.06         |                        |                  |   ?    |

### Retrieve Undirected Edge

Given a pair of nodes - find any edge that connects them.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----: |
| SQLite     |      716.45       |         542.24          |                        |                  |   ?    |
| MySQL      |     1,067.58      |         574.87          |                        |                  |   ?    |
| PostgreSQL |      995.94       |         416.59          |                        |                  |   ?    |
| MongoDB    |     3,535.67      |        2,251.54         |                        |                  |   ?    |
| GraphBPlus |     1,354.79      |                         |                        |                  |   ?    |
| GraphLSM   |     56,837.62     |        24,030.62        |                        |                  |   ?    |

### Retrieve Connected Edges

Find all edges that contain a specific node in any role.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----: |
| SQLite     |      721.73       |          21.34          |                        |                  |   ?    |
| MySQL      |      990.07       |          1.11           |                        |                  |   ?    |
| PostgreSQL |      985.84       |          22.84          |                        |                  |   ?    |
| MongoDB    |     3,025.62      |          98.67          |                        |                  |   ?    |
| GraphBPlus |     13,168.71     |                         |                        |                  |   ?    |
| GraphLSM   |     12,193.76     |          44.52          |                        |                  |   ?    |

### Retrieve Outgoing Edges

Find all directed edges that start in a specific node.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----: |
| SQLite     |      700.62       |          23.13          |                        |                  |   ?    |
| MySQL      |      892.62       |          0.05           |                        |                  |   ?    |
| PostgreSQL |     1,014.53      |          22.36          |                        |                  |   ?    |
| MongoDB    |     3,060.09      |          98.29          |                        |                  |   ?    |
| GraphBPlus |     1,356.34      |                         |                        |                  |   ?    |
| GraphLSM   |     12,330.82     |          40.29          |                        |                  |   ?    |

### Retrieve Ingoing Edges

Find all directed edges that end in a specific node.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----: |
| SQLite     |      458.22       |          4.41           |                        |                  |   ?    |
| MySQL      |     1,077.03      |          95.31          |                        |                  |   ?    |
| PostgreSQL |     1,084.54      |         394.82          |                        |                  |   ?    |
| MongoDB    |     3,002.81      |        1,441.00         |                        |                  |   ?    |
| GraphBPlus |     1,336.23      |                         |                        |                  |   ?    |
| GraphLSM   |     13,955.82     |          51.82          |                        |                  |   ?    |

### Retrieve Friends

Get IDs of all nodes that share an edge with a given node.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----: |
| SQLite     |      746.50       |          21.15          |                        |                  |   ?    |
| MySQL      |     1,014.85      |          1.08           |                        |                  |   ?    |
| PostgreSQL |      927.42       |          22.34          |                        |                  |   ?    |
| MongoDB    |     3,005.61      |          92.26          |                        |                  |   ?    |
| GraphBPlus |     18,836.18     |                         |                        |                  |   ?    |
| GraphLSM   |     13,046.63     |          46.64          |                        |                  |   ?    |

### Retrieve Friends of Friends

Get IDs of all nodes that share an edge with neighbors of a given node.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----: |
| SQLite     |      259.96       |          0.08           |                        |                  |   ?    |
| MySQL      |      246.68       |          0.07           |                        |                  |   ?    |
| PostgreSQL |      225.07       |          0.07           |                        |                  |   ?    |
| MongoDB    |      923.24       |          0.23           |                        |                  |   ?    |
| GraphBPlus |      704.90       |                         |                        |                  |   ?    |
| GraphLSM   |      917.64       |          0.03           |                        |                  |   ?    |

### Count Friends

Count the number of edges containing a specific node and their total weight.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----: |
| SQLite     |      710.82       |         414.33          |                        |                  |   ?    |
| MySQL      |     1,061.34      |          1.70           |                        |                  |   ?    |
| PostgreSQL |      948.69       |         337.51          |                        |                  |   ?    |
| MongoDB    |     2,084.99      |         170.88          |                        |                  |   ?    |
| GraphBPlus |     17,210.93     |                         |                        |                  |   ?    |
| GraphLSM   |     15,158.66     |          46.79          |                        |                  |   ?    |

### Count Followers

Count the number of edges ending in a specific node and their total weight.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----: |
| SQLite     |      458.87       |          4.35           |                        |                  |   ?    |
| MySQL      |      937.50       |         533.00          |                        |                  |   ?    |
| PostgreSQL |      976.35       |         791.99          |                        |                  |   ?    |
| MongoDB    |     2,403.35      |        1,499.58         |                        |                  |   ?    |
| GraphBPlus |     1,270.27      |                         |                        |                  |   ?    |
| GraphLSM   |     14,473.62     |          47.20          |                        |                  |   ?    |

### Count Following

Count the number of edges starting in a specific node and their total weight.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----: |
| SQLite     |      714.43       |         485.17          |                        |                  |   ?    |
| MySQL      |      427.94       |          0.05           |                        |                  |   ?    |
| PostgreSQL |      980.47       |         383.07          |                        |                  |   ?    |
| MongoDB    |     2,258.81      |         182.71          |                        |                  |   ?    |
| GraphBPlus |     1,249.34      |                         |                        |                  |   ?    |
| GraphLSM   |     14,279.97     |          45.58          |                        |                  |   ?    |

## Write Operations


We don't benchmark edge insertions as those operations are uncommon in graph workloads.
Instead of that we benchmark **upserts** = inserts or updates.
Batch operations have different sizes for different DBs depending on memory consumption
and other limitations of each DB.
Concurrency is tested only in systems that explicitly support it.

### Upsert Edge

|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----: |
| SQLite     |      449.77       |         435.48          |                        |                  |   ?    |
| MySQL      |      674.22       |         607.03          |                        |                  |   ?    |
| PostgreSQL |      763.39       |         631.47          |                        |                  |   ?    |
| MongoDB    |     3,347.44      |        3,064.88         |                        |                  |   ?    |
| GraphBPlus |     1,750.36      |                         |                        |                  |   ?    |
| GraphLSM   |     13,345.08     |        3,925.93         |                        |                  |   ?    |

### Upsert Edges Batch

|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----: |
| SQLite     |     1,410.86      |        1,146.63         |                        |                  |   ?    |
| MySQL      |     1,055.15      |        1,014.81         |                        |                  |   ?    |
| PostgreSQL |     1,037.72      |         936.90          |                        |                  |   ?    |
| MongoDB    |     14,350.05     |        11,351.20        |                        |                  |   ?    |
| GraphBPlus |     18,428.76     |                         |                        |                  |   ?    |
| GraphLSM   |     78,205.83     |        5,753.74         |                        |                  |   ?    |

### Remove Edge

|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----: |
| SQLite     |      687.63       |         585.89          |                        |                  |   ?    |
| MySQL      |      980.79       |         643.81          |                        |                  |   ?    |
| PostgreSQL |     1,448.48      |        1,093.10         |                        |                  |   ?    |
| MongoDB    |     3,159.98      |        1,310.84         |                        |                  |   ?    |
| GraphBPlus |     1,762.28      |                         |                        |                  |   ?    |
| GraphLSM   |     9,766.94      |        4,210.60         |                        |                  |   ?    |

### Remove Edges Batch

|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | Result |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----: |
| SQLite     |      634.35       |         640.65          |                        |                  |   ?    |
| MySQL      |     1,000.71      |         926.02          |                        |                  |   ?    |
| PostgreSQL |     1,458.10      |        1,287.87         |                        |                  |   ?    |
| MongoDB    |     2,970.35      |        1,677.48         |                        |                  |   ?    |
| GraphBPlus |     1,758.83      |                         |                        |                  |   ?    |
| GraphLSM   |     77,003.51     |        5,476.70         |                        |                  |   ?    |

## Device


* CPU: 8 cores, 16 threads @ 2300.00Mhz.
* RAM: 16.00 Gb
* Disk: 931.55 Gb
* OS: Darwin

