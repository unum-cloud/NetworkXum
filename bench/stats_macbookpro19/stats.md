# PyGraphDB Benchmarks Overview

## Insert Dump (edges/sec)


Every datascience project starts by importing the data.
Let's see how long it will take to load an adjacency list into each DB.
But before comparing DBs, let's see what our SSD is capable of by simply parsing the list (2 or 3 column CSV).
This will be our baseline for estimating the time required to build the indexes in each DB.

|                   | graph-communities | graph-eachmovie-ratings | graph-patent-citations |    Result    |
| :---------------- | :---------------: | :---------------------: | :--------------------: | :----------: |
| Parsing in Python |    490,068.94     |       564,322.69        |       617,139.11       |  :thumbsup:  |
| SQLiteMem         |     73,992.93     |        74,524.73        |       71,887.72        | :thumbsdown: |

|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----------: |
| SQLite     |     68,527.88     |        57,372.50        |       44,137.56        |  :thumbsup:  |
| MySQL      |     22,045.07     |        23,981.46        |       14,636.07        | :thumbsdown: |
| PostgreSQL |     7,951.17      |        7,174.14         |        7,230.86        | :thumbsdown: |
| MongoDB    |     8,863.45      |        14,832.76        |       14,199.87        | :thumbsdown: |
| Neo4J      |      455.21       |                         |                        |      ?       |


Most DBs provide some form functionality for faster bulk imports, but not all of them where used in benchmarks for various reasons.

* Neo4J supports CSV imports, but it requires duplicating the imported file and constantly crashes (due to Java heap management issues).
* PostgreSQL and MySQL dialects of SQL have special functions for importing CSVs, but their functionality is very limited and performance gains aren't substantial. A better approach is to use unindexed table of incoming edges and later submit it into the main store once the data is absorbed.
* MongoDB provides a command line tool, but it wasn't used to limit the number of binary dependencies and simlify configuration.


|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----------: |
| GraphBPlus |    204,365.92     |       207,143.17        |       113,372.62       | :thumbsdown: |
| GraphLSM   |    119,314.66     |       534,250.90        |       135,714.61       |  :thumbsup:  |

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
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----------: |
| SQLite     |      709.98       |         629.05          |         487.21         | :thumbsdown: |
| MySQL      |     1,067.25      |         757.05          |         649.42         |              |
| PostgreSQL |      977.48       |         495.16          |         689.94         |              |
| MongoDB    |     3,396.74      |        2,503.34         |        1,373.88        |  :thumbsup:  |
| GraphBPlus |     1,339.74      |          4.28           |          0.55          | :thumbsdown: |
| GraphLSM   |     46,640.69     |        3,206.06         |        1,502.16        |  :thumbsup:  |

### Retrieve Undirected Edge

Given a pair of nodes - find any edge that connects them.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----------: |
| SQLite     |      716.45       |         542.24          |         565.20         | :thumbsdown: |
| MySQL      |     1,067.58      |         574.87          |         791.43         | :thumbsdown: |
| PostgreSQL |      995.94       |         416.59          |         310.87         | :thumbsdown: |
| MongoDB    |     3,535.67      |        2,251.54         |        1,550.38        | :thumbsdown: |
| GraphBPlus |     1,354.79      |          4.29           |          0.73          | :thumbsdown: |
| GraphLSM   |     56,837.62     |        24,030.62        |       42,074.31        |  :thumbsup:  |

### Retrieve Connected Edges

Find all edges that contain a specific node in any role.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----------: |
| SQLite     |      721.73       |          21.34          |         381.21         | :thumbsdown: |
| MySQL      |      990.07       |          1.11           |         857.91         | :thumbsdown: |
| PostgreSQL |      985.84       |          22.84          |         894.25         | :thumbsdown: |
| MongoDB    |     3,025.62      |          98.67          |        2,441.84        | :thumbsdown: |
| GraphBPlus |     13,168.71     |         132.49          |        1,425.63        | :thumbsdown: |
| GraphLSM   |     12,193.76     |          44.52          |        6,569.00        |  :thumbsup:  |

### Retrieve Outgoing Edges

Find all directed edges that start in a specific node.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----------: |
| SQLite     |      700.62       |          23.13          |         479.46         | :thumbsdown: |
| MySQL      |      892.62       |          0.05           |         711.94         |              |
| PostgreSQL |     1,014.53      |          22.36          |         721.53         |              |
| MongoDB    |     3,060.09      |          98.29          |        1,585.57        |  :thumbsup:  |
| GraphBPlus |     1,356.34      |          4.16           |          0.73          | :thumbsdown: |
| GraphLSM   |     12,330.82     |          40.29          |         462.34         | :thumbsdown: |

### Retrieve Ingoing Edges

Find all directed edges that end in a specific node.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----------: |
| SQLite     |      458.22       |          4.41           |          0.13          | :thumbsdown: |
| MySQL      |     1,077.03      |          95.31          |         791.89         | :thumbsdown: |
| PostgreSQL |     1,084.54      |         394.82          |         443.79         | :thumbsdown: |
| MongoDB    |     3,002.81      |        1,441.00         |        1,558.45        | :thumbsdown: |
| GraphBPlus |     1,336.23      |          4.15           |          0.71          | :thumbsdown: |
| GraphLSM   |     13,955.82     |          51.82          |        6,747.75        |  :thumbsup:  |

### Retrieve Friends

Get IDs of all nodes that share an edge with a given node.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----------: |
| SQLite     |      746.50       |          21.15          |         651.92         | :thumbsdown: |
| MySQL      |     1,014.85      |          1.08           |         837.92         | :thumbsdown: |
| PostgreSQL |      927.42       |          22.34          |         882.00         | :thumbsdown: |
| MongoDB    |     3,005.61      |          92.26          |        2,334.31        | :thumbsdown: |
| GraphBPlus |     18,836.18     |         551.95          |        8,555.51        |  :thumbsup:  |
| GraphLSM   |     13,046.63     |          46.64          |        7,189.17        |  :thumbsup:  |

### Retrieve Friends of Friends

Get IDs of all nodes that share an edge with neighbors of a given node.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----------: |
| SQLite     |      259.96       |          0.08           |         39.75          | :thumbsdown: |
| MySQL      |      246.68       |          0.07           |         35.08          | :thumbsdown: |
| PostgreSQL |      225.07       |          0.07           |         34.86          | :thumbsdown: |
| MongoDB    |      923.24       |          0.23           |         69.23          |              |
| GraphBPlus |      704.90       |          0.02           |         98.10          |  :thumbsup:  |
| GraphLSM   |      917.64       |          0.03           |         42.87          | :thumbsdown: |

### Count Friends

Count the number of edges containing a specific node and their total weight.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----------: |
| SQLite     |      710.82       |         414.33          |         692.86         | :thumbsdown: |
| MySQL      |     1,061.34      |          1.70           |         862.79         | :thumbsdown: |
| PostgreSQL |      948.69       |         337.51          |         966.32         | :thumbsdown: |
| MongoDB    |     2,084.99      |         170.88          |        1,873.56        | :thumbsdown: |
| GraphBPlus |     17,210.93     |         567.82          |        8,494.86        |  :thumbsup:  |
| GraphLSM   |     15,158.66     |          46.79          |        6,462.96        |  :thumbsup:  |

### Count Followers

Count the number of edges ending in a specific node and their total weight.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----------: |
| SQLite     |      458.87       |          4.35           |          0.37          | :thumbsdown: |
| MySQL      |      937.50       |         533.00          |         998.98         | :thumbsdown: |
| PostgreSQL |      976.35       |         791.99          |         982.84         | :thumbsdown: |
| MongoDB    |     2,403.35      |        1,499.58         |        2,170.54        | :thumbsdown: |
| GraphBPlus |     1,270.27      |          4.15           |          0.71          | :thumbsdown: |
| GraphLSM   |     14,473.62     |          47.20          |        7,167.55        |  :thumbsup:  |

### Count Following

Count the number of edges starting in a specific node and their total weight.
|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----------: |
| SQLite     |      714.43       |         485.17          |         715.09         | :thumbsdown: |
| MySQL      |      427.94       |          0.05           |        1,044.02        | :thumbsdown: |
| PostgreSQL |      980.47       |         383.07          |         980.77         | :thumbsdown: |
| MongoDB    |     2,258.81      |         182.71          |        2,221.77        | :thumbsdown: |
| GraphBPlus |     1,249.34      |          4.24           |          0.72          | :thumbsdown: |
| GraphLSM   |     14,279.97     |          45.58          |        7,169.65        |  :thumbsup:  |

## Write Operations


We don't benchmark edge insertions as those operations are uncommon in graph workloads.
Instead of that we benchmark **upserts** = inserts or updates.
Batch operations have different sizes for different DBs depending on memory consumption
and other limitations of each DB.
Concurrency is tested only in systems that explicitly support it.

### Upsert Edge

|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----------: |
| SQLite     |      449.77       |         435.48          |         372.24         | :thumbsdown: |
| MySQL      |      674.22       |         607.03          |         373.24         | :thumbsdown: |
| PostgreSQL |      763.39       |         631.47          |         547.85         | :thumbsdown: |
| MongoDB    |     3,347.44      |        3,064.88         |        2,516.66        | :thumbsdown: |
| GraphBPlus |     1,750.36      |        1,528.97         |        1,246.90        | :thumbsdown: |
| GraphLSM   |     13,345.08     |        3,925.93         |        9,312.31        |  :thumbsup:  |

### Upsert Edges Batch

|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----------: |
| SQLite     |     1,410.86      |        1,146.63         |        1,177.27        | :thumbsdown: |
| MySQL      |     1,055.15      |        1,014.81         |         849.62         | :thumbsdown: |
| PostgreSQL |     1,037.72      |         936.90          |         995.12         | :thumbsdown: |
| MongoDB    |     14,350.05     |        11,351.20        |        6,482.28        | :thumbsdown: |
| GraphBPlus |     18,428.76     |        4,515.64         |        4,415.95        | :thumbsdown: |
| GraphLSM   |     78,205.83     |        5,753.74         |       68,336.96        |  :thumbsup:  |

### Remove Edge

|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----------: |
| SQLite     |      687.63       |         585.89          |         469.26         | :thumbsdown: |
| MySQL      |      980.79       |         643.81          |         885.60         | :thumbsdown: |
| PostgreSQL |     1,448.48      |        1,093.10         |         897.67         | :thumbsdown: |
| MongoDB    |     3,159.98      |        1,310.84         |         572.77         | :thumbsdown: |
| GraphBPlus |     1,762.28      |        1,371.72         |         956.39         | :thumbsdown: |
| GraphLSM   |     9,766.94      |        4,210.60         |        3,334.01        |  :thumbsup:  |

### Remove Edges Batch

|            | graph-communities | graph-eachmovie-ratings | graph-patent-citations |    Result    |
| :--------- | :---------------: | :---------------------: | :--------------------: | :----------: |
| SQLite     |      634.35       |         640.65          |         643.42         | :thumbsdown: |
| MySQL      |     1,000.71      |         926.02          |         739.35         | :thumbsdown: |
| PostgreSQL |     1,458.10      |        1,287.87         |        1,254.80        | :thumbsdown: |
| MongoDB    |     2,970.35      |        1,677.48         |        1,215.18        | :thumbsdown: |
| GraphBPlus |     1,758.83      |        1,808.20         |        1,791.25        | :thumbsdown: |
| GraphLSM   |     77,003.51     |        5,476.70         |       70,875.59        |  :thumbsup:  |

## Device


* CPU: 8 cores, 16 threads @ 2300.00Mhz.
* RAM: 16.00 Gb
* Disk: 931.55 Gb
* OS: Darwin

