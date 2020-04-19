# PyGraphDB Benchmarks Overview

## Insert Dump (edges/sec)


Every datascience project starts by importing the data.
Let's see how long it will take to load an adjacency list into each DB.
But before comparing DBs, let's see what our SSD is capable of by simply parsing the list (2 or 3 column CSV).
This will be our baseline for estimating the time required to build the indexes in each DB.

|                   | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :---------------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| Parsing in Python |    490,068.94     |       564,322.69        |       617,139.11       |    565,048.86    |  :thumbsup:  |
| SQLiteMem         |     73,992.93     |        74,524.73        |       71,887.72        |                  | :thumbsdown: |


Most DBs provide some form functionality for faster bulk imports, but not all of them where used in benchmarks for various reasons.

* Neo4J supports CSV imports, but it requires duplicating the imported file and constantly crashes (due to Java heap management issues).
* PostgreSQL and MySQL dialects of SQL have special functions for importing CSVs, but their functionality is very limited and performance gains aren't substantial. A better approach is to use unindexed table of incoming edges and later submit it into the main store once the data is absorbed.
* MongoDB provides a command line tool, but it wasn't used to limit the number of binary dependencies and simlify configuration.

|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite     |     68,527.88     |        57,372.50        |       44,137.56        |    49,059.01     | :thumbsdown: |
| MySQL      |     22,045.07     |        23,981.46        |       14,636.07        |    18,370.53     | :thumbsdown: |
| PostgreSQL |     7,951.17      |        7,174.14         |        7,230.86        |     7,361.18     | :thumbsdown: |
| MongoDB    |     8,863.45      |        14,832.76        |       14,199.87        |    15,448.18     | :thumbsdown: |
| Neo4J      |      455.21       |                         |                        |                  |      ?       |
| SQLiteCpp  |    204,365.92     |       207,143.17        |       113,372.62       |    177,345.69    |  :thumbsup:  |
| GraphLSM   |    119,314.66     |       534,250.90        |       135,714.61       |    429,779.53    |  :thumbsup:  |

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
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite     |      709.98       |         629.05          |         487.21         |                  |              |
| MySQL      |     1,067.25      |         757.05          |         649.42         |                  |              |
| PostgreSQL |      977.48       |         495.16          |         689.94         |                  |              |
| MongoDB    |     3,396.74      |        2,503.34         |        1,373.88        |                  |  :thumbsup:  |
| SQLiteCpp  |     1,339.74      |          4.28           |          0.55          |                  | :thumbsdown: |
| GraphLSM   |     20,917.97     |        1,509.78         |        1,378.05        |     1,259.01     |  :thumbsup:  |

### Retrieve Undirected Edge

Given a pair of nodes - find any edge that connects them.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite     |      716.45       |         542.24          |         565.20         |                  | :thumbsdown: |
| MySQL      |     1,067.58      |         574.87          |         791.43         |                  | :thumbsdown: |
| PostgreSQL |      995.94       |         416.59          |         310.87         |                  | :thumbsdown: |
| MongoDB    |     3,535.67      |        2,251.54         |        1,550.38        |                  | :thumbsdown: |
| SQLiteCpp  |     1,354.79      |          4.29           |          0.73          |                  | :thumbsdown: |
| GraphLSM   |     37,151.93     |        13,107.86        |       25,168.34        |    27,644.30     |  :thumbsup:  |

### Retrieve Connected Edges

Find all edges that contain a specific node in any role.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite     |      721.73       |          21.34          |         381.21         |                  | :thumbsdown: |
| MySQL      |      990.07       |          1.11           |         857.91         |                  | :thumbsdown: |
| PostgreSQL |      985.84       |          22.84          |         894.25         |                  | :thumbsdown: |
| MongoDB    |     3,025.62      |          98.67          |        2,441.84        |                  | :thumbsdown: |
| SQLiteCpp  |     13,168.71     |         132.49          |        1,425.63        |                  | :thumbsdown: |
| GraphLSM   |     14,706.89     |          83.39          |        6,757.22        |      137.18      |  :thumbsup:  |

### Retrieve Outgoing Edges

Find all directed edges that start in a specific node.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite     |      700.62       |          23.13          |         479.46         |                  | :thumbsdown: |
| MySQL      |      892.62       |          0.05           |         711.94         |                  |              |
| PostgreSQL |     1,014.53      |          22.36          |         721.53         |                  |              |
| MongoDB    |     3,060.09      |          98.29          |        1,585.57        |                  |  :thumbsup:  |
| SQLiteCpp  |     1,356.34      |          4.16           |          0.73          |                  | :thumbsdown: |
| GraphLSM   |     14,965.90     |          74.38          |         511.97         |      61.14       | :thumbsdown: |

### Retrieve Ingoing Edges

Find all directed edges that end in a specific node.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite     |      458.22       |          4.41           |          0.13          |                  | :thumbsdown: |
| MySQL      |     1,077.03      |          95.31          |         791.89         |                  | :thumbsdown: |
| PostgreSQL |     1,084.54      |         394.82          |         443.79         |                  | :thumbsdown: |
| MongoDB    |     3,002.81      |        1,441.00         |        1,558.45        |                  | :thumbsdown: |
| SQLiteCpp  |     1,336.23      |          4.15           |          0.71          |                  | :thumbsdown: |
| GraphLSM   |     16,972.30     |         117.07          |        7,013.42        |      148.18      |  :thumbsup:  |

### Retrieve Friends

Get IDs of all nodes that share an edge with a given node.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite     |      746.50       |          21.15          |         651.92         |                  | :thumbsdown: |
| MySQL      |     1,014.85      |          1.08           |         837.92         |                  | :thumbsdown: |
| PostgreSQL |      927.42       |          22.34          |         882.00         |                  | :thumbsdown: |
| MongoDB    |     3,005.61      |          92.26          |        2,334.31        |                  | :thumbsdown: |
| SQLiteCpp  |     18,836.18     |         551.95          |        8,555.51        |                  |  :thumbsup:  |
| GraphLSM   |     17,263.29     |         104.68          |        7,182.86        |      153.27      |  :thumbsup:  |

### Retrieve Friends of Friends

Get IDs of all nodes that share an edge with neighbors of a given node.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite     |      259.96       |          0.08           |         39.75          |                  | :thumbsdown: |
| MySQL      |      246.68       |          0.07           |         35.08          |                  | :thumbsdown: |
| PostgreSQL |      225.07       |          0.07           |         34.86          |                  | :thumbsdown: |
| MongoDB    |      923.24       |          0.23           |         69.23          |                  |              |
| SQLiteCpp  |      704.90       |          0.02           |         98.10          |                  |  :thumbsup:  |
| GraphLSM   |     1,146.33      |          0.06           |         50.37          |       0.04       | :thumbsdown: |

### Count Friends

Count the number of edges containing a specific node and their total weight.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite     |      710.82       |         414.33          |         692.86         |                  | :thumbsdown: |
| MySQL      |     1,061.34      |          1.70           |         862.79         |                  | :thumbsdown: |
| PostgreSQL |      948.69       |         337.51          |         966.32         |                  | :thumbsdown: |
| MongoDB    |     2,084.99      |         170.88          |        1,873.56        |                  | :thumbsdown: |
| SQLiteCpp  |     17,210.93     |         567.82          |        8,494.86        |                  |  :thumbsup:  |
| GraphLSM   |     18,818.82     |         109.71          |        8,420.20        |      149.83      |  :thumbsup:  |

### Count Followers

Count the number of edges ending in a specific node and their total weight.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite     |      458.87       |          4.35           |          0.37          |                  | :thumbsdown: |
| MySQL      |      937.50       |         533.00          |         998.98         |                  | :thumbsdown: |
| PostgreSQL |      976.35       |         791.99          |         982.84         |                  | :thumbsdown: |
| MongoDB    |     2,403.35      |        1,499.58         |        2,170.54        |                  | :thumbsdown: |
| SQLiteCpp  |     1,270.27      |          4.15           |          0.71          |                  | :thumbsdown: |
| GraphLSM   |     18,869.42     |         115.69          |        8,322.66        |      149.44      |  :thumbsup:  |

### Count Following

Count the number of edges starting in a specific node and their total weight.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite     |      714.43       |         485.17          |         715.09         |                  | :thumbsdown: |
| MySQL      |      427.94       |          0.05           |        1,044.02        |                  | :thumbsdown: |
| PostgreSQL |      980.47       |         383.07          |         980.77         |                  | :thumbsdown: |
| MongoDB    |     2,258.81      |         182.71          |        2,221.77        |                  | :thumbsdown: |
| SQLiteCpp  |     1,249.34      |          4.24           |          0.72          |                  | :thumbsdown: |
| GraphLSM   |     18,858.31     |         118.31          |        8,463.39        |      151.24      |  :thumbsup:  |

## Write Operations


We don't benchmark edge insertions as those operations are uncommon in graph workloads.
Instead of that we benchmark **upserts** = inserts or updates.
Batch operations have different sizes for different DBs depending on memory consumption
and other limitations of each DB.
Concurrency is tested only in systems that explicitly support it.

### Upsert Edge

|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite     |      449.77       |         435.48          |         372.24         |                  | :thumbsdown: |
| MySQL      |      674.22       |         607.03          |         373.24         |                  | :thumbsdown: |
| PostgreSQL |      763.39       |         631.47          |         547.85         |                  | :thumbsdown: |
| MongoDB    |     3,347.44      |        3,064.88         |        2,516.66        |                  | :thumbsdown: |
| SQLiteCpp  |     1,750.36      |        1,528.97         |        1,246.90        |                  | :thumbsdown: |
| GraphLSM   |     13,777.14     |        3,999.12         |        9,570.64        |     6,048.25     |  :thumbsup:  |

### Upsert Edges Batch

|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite     |     1,410.86      |        1,146.63         |        1,177.27        |                  | :thumbsdown: |
| MySQL      |     1,055.15      |        1,014.81         |         849.62         |                  | :thumbsdown: |
| PostgreSQL |     1,037.72      |         936.90          |         995.12         |                  | :thumbsdown: |
| MongoDB    |     14,350.05     |        11,351.20        |        6,482.28        |                  | :thumbsdown: |
| SQLiteCpp  |     18,428.76     |        4,515.64         |        4,415.95        |                  | :thumbsdown: |
| GraphLSM   |     79,122.58     |        6,552.02         |       69,060.91        |    15,601.93     |  :thumbsup:  |

### Remove Edge

|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite     |      687.63       |         585.89          |         469.26         |                  | :thumbsdown: |
| MySQL      |      980.79       |         643.81          |         885.60         |                  | :thumbsdown: |
| PostgreSQL |     1,448.48      |        1,093.10         |         897.67         |                  | :thumbsdown: |
| MongoDB    |     3,159.98      |        1,310.84         |         572.77         |                  | :thumbsdown: |
| SQLiteCpp  |     1,762.28      |        1,371.72         |         956.39         |                  | :thumbsdown: |
| GraphLSM   |     10,819.78     |        4,115.75         |        3,220.58        |     3,882.20     |  :thumbsup:  |

### Remove Edges Batch

|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite     |      634.35       |         640.65          |         643.42         |                  | :thumbsdown: |
| MySQL      |     1,000.71      |         926.02          |         739.35         |                  | :thumbsdown: |
| PostgreSQL |     1,458.10      |        1,287.87         |        1,254.80        |                  | :thumbsdown: |
| MongoDB    |     2,970.35      |        1,677.48         |        1,215.18        |                  | :thumbsdown: |
| SQLiteCpp  |     1,758.83      |        1,808.20         |        1,791.25        |                  | :thumbsdown: |
| GraphLSM   |     80,724.27     |        6,613.06         |       70,085.89        |    12,865.58     |  :thumbsup:  |

## Device


* CPU: 8 cores, 16 threads @ 2300.00Mhz.
* RAM: 16.00 Gb
* Disk: 931.55 Gb
* OS: Darwin

