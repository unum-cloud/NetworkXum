# PyGraphDB Benchmarks Overview

## Sequential Writes: Import CSV (edges/sec)


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

|               | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :------------ | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite        |     68,527.88     |        57,372.50        |       44,137.56        |    49,059.01     | :thumbsdown: |
| MySQL         |     22,045.07     |        23,981.46        |       14,636.07        |    18,370.53     | :thumbsdown: |
| PostgreSQL    |     7,951.17      |        7,174.14         |        7,230.86        |     7,361.18     | :thumbsdown: |
| MongoDB       |     8,863.45      |        14,832.76        |       14,199.87        |    15,448.18     | :thumbsdown: |
| Neo4J         |      455.21       |                         |                        |                  |      ?       |
| SQLiteCpp     |    204,365.92     |       207,143.17        |       113,372.62       |    177,345.69    |  :thumbsup:  |
| RocksMonolith |    119,314.66     |       534,250.90        |       135,714.61       |    429,779.53    |  :thumbsup:  |

## Read Queries


Following are simple lookup operations.
Their speed translates into the execution time of analytical queries like:

* Shortest Path Calculation,
* Clustering Analysis,
* Pattern Matching.

As we are running on a local machine and within the same filesystem,
the networking bandwidth and latency between server and client applications
can't be a bottleneck.

### Random Reads: Find Directed Edge

Given nodes A and B - find any directed edge that goes from A to B.
|               | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :------------ | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite        |      709.98       |         629.05          |         487.21         |      462.52      |              |
| MySQL         |     1,067.25      |         757.05          |         649.42         |      534.80      |              |
| PostgreSQL    |      977.48       |         495.16          |         689.94         |      345.37      |              |
| MongoDB       |     3,396.74      |        2,503.34         |        1,373.88        |      317.53      |  :thumbsup:  |
| SQLiteCpp     |     1,339.74      |          4.28           |          0.55          |       0.81       | :thumbsdown: |
| RocksMonolith |     20,917.97     |        1,509.78         |        1,378.05        |     1,259.01     |  :thumbsup:  |

### Random Reads: Find Any Relation

Given a pair of nodes - find any edge that connects them.
|               | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :------------ | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite        |      716.45       |         542.24          |         565.20         |      569.89      | :thumbsdown: |
| MySQL         |     1,067.58      |         574.87          |         791.43         |      627.89      | :thumbsdown: |
| PostgreSQL    |      995.94       |         416.59          |         310.87         |      485.25      | :thumbsdown: |
| MongoDB       |     3,535.67      |        2,251.54         |        1,550.38        |      567.44      | :thumbsdown: |
| SQLiteCpp     |     1,354.79      |          4.29           |          0.73          |       0.82       | :thumbsdown: |
| RocksMonolith |     37,151.93     |        13,107.86        |       25,168.34        |    27,644.30     |  :thumbsup:  |

### Random Reads: Find Connected Edges

Find all edges that contain a specific node in any role.
|               | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :------------ | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite        |      721.73       |          21.34          |         381.21         |      40.21       | :thumbsdown: |
| MySQL         |      990.07       |          1.11           |         857.91         |      33.90       | :thumbsdown: |
| PostgreSQL    |      985.84       |          22.84          |         894.25         |      44.62       | :thumbsdown: |
| MongoDB       |     3,025.62      |          98.67          |        2,441.84        |      129.69      | :thumbsdown: |
| SQLiteCpp     |     13,168.71     |         132.49          |        1,425.63        |      139.12      | :thumbsdown: |
| RocksMonolith |     14,706.89     |          83.39          |        6,757.22        |      137.18      |  :thumbsup:  |

### Random Reads: Find Outgoing Edges

Find all directed edges that start in a specific node.
|               | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :------------ | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite        |      700.62       |          23.13          |         479.46         |       0.71       | :thumbsdown: |
| MySQL         |      892.62       |          0.05           |         711.94         |      56.49       |              |
| PostgreSQL    |     1,014.53      |          22.36          |         721.53         |      75.24       |              |
| MongoDB       |     3,060.09      |          98.29          |        1,585.57        |      180.67      |  :thumbsup:  |
| SQLiteCpp     |     1,356.34      |          4.16           |          0.73          |       0.82       | :thumbsdown: |
| RocksMonolith |     14,965.90     |          74.38          |         511.97         |      61.14       | :thumbsdown: |

### Random Reads: Find Ingoing Edges

Find all directed edges that end in a specific node.
|               | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :------------ | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite        |      458.22       |          4.41           |          0.13          |      95.55       | :thumbsdown: |
| MySQL         |     1,077.03      |          95.31          |         791.89         |      66.36       | :thumbsdown: |
| PostgreSQL    |     1,084.54      |         394.82          |         443.79         |      100.68      | :thumbsdown: |
| MongoDB       |     3,002.81      |        1,441.00         |        1,558.45        |      305.64      | :thumbsdown: |
| SQLiteCpp     |     1,336.23      |          4.15           |          0.71          |       0.70       | :thumbsdown: |
| RocksMonolith |     16,972.30     |         117.07          |        7,013.42        |      148.18      |  :thumbsup:  |

### Random Reads: Find Friends

Get IDs of all nodes that share an edge with a given node.
|               | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :------------ | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite        |      746.50       |          21.15          |         651.92         |      43.30       | :thumbsdown: |
| MySQL         |     1,014.85      |          1.08           |         837.92         |      33.89       | :thumbsdown: |
| PostgreSQL    |      927.42       |          22.34          |         882.00         |      43.20       | :thumbsdown: |
| MongoDB       |     3,005.61      |          92.26          |        2,334.31        |      127.35      | :thumbsdown: |
| SQLiteCpp     |     18,836.18     |         551.95          |        8,555.51        |      343.85      |  :thumbsup:  |
| RocksMonolith |     17,263.29     |         104.68          |        7,182.86        |      153.27      |  :thumbsup:  |

### Random Reads: Find Friends of Friends

Get IDs of all nodes that share an edge with neighbors of a given node.
|               | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :------------ | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite        |      259.96       |          0.08           |         39.75          |       0.02       | :thumbsdown: |
| MySQL         |      246.68       |          0.07           |         35.08          |       0.03       | :thumbsdown: |
| PostgreSQL    |      225.07       |          0.07           |         34.86          |       0.03       | :thumbsdown: |
| MongoDB       |      923.24       |          0.23           |         69.23          |       0.09       |              |
| SQLiteCpp     |      704.90       |          0.02           |         98.10          |       0.16       |              |
| RocksMonolith |      491.87       |          0.42           |         132.73         |       0.10       |  :thumbsup:  |

### Random Reads: Count Friends

Count the number of edges containing a specific node and their total weight.
|               | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :------------ | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite        |      710.82       |         414.33          |         692.86         |      283.86      | :thumbsdown: |
| MySQL         |     1,061.34      |          1.70           |         862.79         |       7.10       | :thumbsdown: |
| PostgreSQL    |      948.69       |         337.51          |         966.32         |      188.98      | :thumbsdown: |
| MongoDB       |     2,084.99      |         170.88          |        1,873.56        |      200.26      | :thumbsdown: |
| SQLiteCpp     |     17,210.93     |         567.82          |        8,494.86        |      382.25      |  :thumbsup:  |
| RocksMonolith |     27,874.63     |         286.21          |        2,134.54        |      108.58      | :thumbsdown: |

### Random Reads: Count Followers

Count the number of edges ending in a specific node and their total weight.
|               | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :------------ | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite        |      458.87       |          4.35           |          0.37          |      685.33      | :thumbsdown: |
| MySQL         |      937.50       |         533.00          |         998.98         |      134.48      | :thumbsdown: |
| PostgreSQL    |      976.35       |         791.99          |         982.84         |      731.73      | :thumbsdown: |
| MongoDB       |     2,403.35      |        1,499.58         |        2,170.54        |      574.66      | :thumbsdown: |
| SQLiteCpp     |     1,270.27      |          4.15           |          0.71          |       0.79       | :thumbsdown: |
| RocksMonolith |     22,410.55     |         296.45          |        6,977.28        |      139.76      |  :thumbsup:  |

### Random Reads: Count Following

Count the number of edges starting in a specific node and their total weight.
|               | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :------------ | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite        |      714.43       |         485.17          |         715.09         |       0.93       | :thumbsdown: |
| MySQL         |      427.94       |          0.05           |        1,044.02        |      106.65      | :thumbsdown: |
| PostgreSQL    |      980.47       |         383.07          |         980.77         |      229.59      | :thumbsdown: |
| MongoDB       |     2,258.81      |         182.71          |        2,221.77        |      304.79      | :thumbsdown: |
| SQLiteCpp     |     1,249.34      |          4.24           |          0.72          |       0.80       | :thumbsdown: |
| RocksMonolith |     26,658.37     |         253.00          |        7,160.12        |      153.99      |  :thumbsup:  |

## Write Operations


We don't benchmark edge insertions as those operations are uncommon in graph workloads.
Instead of that we benchmark **upserts** = inserts or updates.
Batch operations have different sizes for different DBs depending on memory consumption
and other limitations of each DB.
Concurrency is tested only in systems that explicitly support it.

### Random Writes: Upsert Edge

|               | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :------------ | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite        |      449.77       |         435.48          |         372.24         |      446.27      | :thumbsdown: |
| MySQL         |      674.22       |         607.03          |         373.24         |      406.16      | :thumbsdown: |
| PostgreSQL    |      763.39       |         631.47          |         547.85         |      702.21      | :thumbsdown: |
| MongoDB       |     3,347.44      |        3,064.88         |        2,516.66        |     2,483.28     | :thumbsdown: |
| SQLiteCpp     |     1,750.36      |        1,528.97         |        1,246.90        |     1,761.80     | :thumbsdown: |
| RocksMonolith |     13,777.14     |        3,999.12         |        9,570.64        |     6,048.25     |  :thumbsup:  |

### Random Writes: Upsert Edges Batch

|               | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :------------ | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite        |     1,410.86      |        1,146.63         |        1,177.27        |     1,140.73     | :thumbsdown: |
| MySQL         |     1,055.15      |        1,014.81         |         849.62         |      856.45      | :thumbsdown: |
| PostgreSQL    |     1,037.72      |         936.90          |         995.12         |      965.59      | :thumbsdown: |
| MongoDB       |     14,350.05     |        11,351.20        |        6,482.28        |     6,439.03     | :thumbsdown: |
| SQLiteCpp     |     18,428.76     |        4,515.64         |        4,415.95        |     4,106.50     | :thumbsdown: |
| RocksMonolith |     79,122.58     |        6,552.02         |       69,060.91        |    15,601.93     |  :thumbsup:  |

### Random Writes: Remove Edge

|               | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :------------ | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite        |      687.63       |         585.89          |         469.26         |      596.98      | :thumbsdown: |
| MySQL         |      980.79       |         643.81          |         885.60         |      726.17      | :thumbsdown: |
| PostgreSQL    |     1,448.48      |        1,093.10         |         897.67         |     1,061.85     | :thumbsdown: |
| MongoDB       |     3,159.98      |        1,310.84         |         572.77         |      359.21      | :thumbsdown: |
| SQLiteCpp     |     1,762.28      |        1,371.72         |         956.39         |     1,478.62     | :thumbsdown: |
| RocksMonolith |     10,819.78     |        4,115.75         |        3,220.58        |     3,882.20     |  :thumbsup:  |

### Random Writes: Remove Edges Batch

|               | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene |    Result    |
| :------------ | :---------------: | :---------------------: | :--------------------: | :--------------: | :----------: |
| SQLite        |      634.35       |         640.65          |         643.42         |      630.82      | :thumbsdown: |
| MySQL         |     1,000.71      |         926.02          |         739.35         |      732.53      | :thumbsdown: |
| PostgreSQL    |     1,458.10      |        1,287.87         |        1,254.80        |     1,419.80     | :thumbsdown: |
| MongoDB       |     2,970.35      |        1,677.48         |        1,215.18        |      590.56      | :thumbsdown: |
| SQLiteCpp     |     1,758.83      |        1,808.20         |        1,791.25        |     1,956.87     | :thumbsdown: |
| RocksMonolith |     80,724.27     |        6,613.06         |       70,085.89        |    12,865.58     |  :thumbsup:  |

## Device


* CPU: 8 cores, 16 threads @ 2300.00Mhz.
* RAM: 16.00 Gb
* Disk: 931.55 Gb
* OS: Darwin

