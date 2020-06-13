# PyWrappedDBs Benchmarks Overview

## Sequential Writes: Import CSV (edges/sec)


Every datascience project starts by importing the data.
Let's see how long it will take to load an adjacency list into each DB.
But before comparing DBs, let's see what our SSD is capable of by simply parsing the list (2 or 3 column CSV).
This will be our baseline for estimating the time required to build the indexes in each DB.

|  | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | graph-human-brain | Good in graph-human-brain |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| Parsing in Python | 602,084.89 | 538,175.26 | 622,782.99 | 546,260.93 | 443,102.25 |  |
| SQLiteMem | 73,992.93 | 74,524.73 | 71,887.72 |  |  |  |


Most DBs provide some form functionality for faster bulk imports, but not all of them where used in benchmarks for various reasons.

* Neo4J supports CSV imports, but it requires duplicating the imported file and constantly crashes (due to Java heap management issues).
* PostgreSQL and MySQL dialects of SQL have special functions for importing CSVs, but their functionality is very limited and performance gains aren't substantial. A better approach is to use unindexed table of incoming edges and later submit it into the main store once the data is absorbed.
* MongoDB provides a command line tool, but it wasn't used to limit the number of binary dependencies and simlify configuration.

|  | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | graph-human-brain | Good in graph-human-brain |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| SQLite | 59,371.14 | 57,372.50 | 44,137.56 | 49,059.01 | 38,185.49 | :thumbsdown: |
| MySQL | 22,045.07 | 23,981.46 | 14,636.07 | 18,370.53 | 12,185.34 | :thumbsdown: |
| PostgreSQL | 7,951.17 | 7,174.14 | 7,230.86 | 7,361.18 | 7,428.68 | :thumbsdown: |
| MongoDB | 8,863.45 | 14,832.76 | 14,199.87 | 15,448.18 | 15,171.61 | :thumbsdown: |
| Neo4J | 455.21 |  |  |  |  |  |
| GraphDB | 240,559.64 | 639,939.85 | 285,056.99 | 875,710.22 | 549,628.79 | :underage::underage::underage: |

## Read Queries


Following are simple lookup operations.
Their speed translates into the execution time of analytical queries like:

* Shortest Path Calculation,
* Clustering Analysis,
* Pattern Matching.

As we are running on a local machine and within the same filesystem,
the networking bandwidth and latency between server and client applications
can't be a bottleneck.

### Random Reads: Find Any Relation

Given a pair of nodes - find any edge that connects them.
|  | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | graph-human-brain | Good in graph-human-brain |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| SQLite | 580.09 | 542.24 | 565.20 | 569.89 | 0.04 | :thumbsdown: |
| MySQL | 1,067.58 | 574.87 | 791.43 | 627.89 | 560.39 | :thumbsdown: |
| PostgreSQL | 995.94 | 416.59 | 310.87 | 485.25 | 569.41 | :thumbsdown: |
| MongoDB | 3,535.67 | 2,251.54 | 1,550.38 | 567.44 | 174.32 | :thumbsdown: |
| GraphDB | 138,077.72 | 21,347.36 | 7,937.44 | 18,170.31 | 7,024.40 | :fire::fire::fire: |

### Random Reads: Find Directed Edge

Given nodes A and B - find any directed edge that goes from A to B.
|  | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | graph-human-brain | Good in graph-human-brain |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| SQLite | 534.89 | 629.05 | 487.21 | 462.52 | 0.03 | :thumbsdown: |
| MySQL | 1,067.25 | 757.05 | 649.42 | 534.80 | 622.63 | :thumbsdown: |
| PostgreSQL | 977.48 | 495.16 | 689.94 | 345.37 | 488.56 | :thumbsdown: |
| MongoDB | 3,396.74 | 2,503.34 | 1,373.88 | 317.53 | 162.91 | :thumbsdown: |
| GraphDB | 120,605.34 | 14,641.39 | 3,797.41 | 8,211.14 | 3,816.05 | :thumbsup: |

### Random Reads: Find Connected Edges

Find all edges that contain a specific node in any role.
|  | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | graph-human-brain | Good in graph-human-brain |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| SQLite | 734.92 | 21.34 | 381.21 | 40.21 | 31.85 | :thumbsdown: |
| MySQL | 990.07 | 1.11 | 857.91 | 33.90 | 85.09 | :thumbsdown: |
| PostgreSQL | 985.84 | 22.84 | 894.25 | 44.62 | 28.20 | :thumbsdown: |
| MongoDB | 3,025.62 | 98.67 | 2,441.84 | 129.69 | 67.33 | :thumbsdown: |
| GraphDB | 33,315.84 | 665.69 | 4,062.32 | 103.42 | 315.89 | :thumbsup: |

### Random Reads: Find Ingoing Edges

Find all directed edges that end in a specific node.
|  | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | graph-human-brain | Good in graph-human-brain |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| SQLite | 502.81 | 4.41 | 0.13 | 95.55 | 0.02 | :thumbsdown: |
| MySQL | 1,077.03 | 95.31 | 791.89 | 66.36 | 128.18 |  |
| PostgreSQL | 1,084.54 | 394.82 | 443.79 | 100.68 | 25.47 | :thumbsdown: |
| MongoDB | 3,002.81 | 1,441.00 | 1,558.45 | 305.64 | 78.23 | :thumbsdown: |
| GraphDB | 36,843.80 | 448.60 | 3,610.75 | 97.86 | 316.31 | :thumbsup: |

### Random Reads: Find Friends

Get IDs of all nodes that share an edge with a given node.
|  | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | graph-human-brain | Good in graph-human-brain |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| SQLite | 724.49 | 21.15 | 651.92 | 43.30 | 35.33 | :thumbsdown: |
| MySQL | 1,014.85 | 1.08 | 837.92 | 33.89 | 75.76 | :thumbsdown: |
| PostgreSQL | 927.42 | 22.34 | 882.00 | 43.20 | 29.18 | :thumbsdown: |
| MongoDB | 3,005.61 | 92.26 | 2,334.31 | 127.35 | 69.23 | :thumbsdown: |
| GraphDB | 35,139.36 | 6,674.89 | 17,288.37 | 1,944.81 | 4,971.51 | :underage::underage::underage: |

### Random Reads: Count Friends

Count the number of edges containing a specific node and their total weight.
|  | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | graph-human-brain | Good in graph-human-brain |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| SQLite | 667.42 | 414.33 | 692.86 | 283.86 | 51.63 | :thumbsdown: |
| MySQL | 1,061.34 | 1.70 | 862.79 | 7.10 | 64.27 | :thumbsdown: |
| PostgreSQL | 948.69 | 337.51 | 966.32 | 188.98 | 41.42 | :thumbsdown: |
| MongoDB | 2,084.99 | 170.88 | 1,873.56 | 200.26 | 80.04 | :thumbsdown: |
| GraphDB | 33,509.33 | 789.88 | 4,361.97 | 113.43 | 344.57 | :thumbsup: |

### Random Reads: Count Followers

Count the number of edges ending in a specific node and their total weight.
|  | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | graph-human-brain | Good in graph-human-brain |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| SQLite | 439.27 | 4.35 | 0.37 | 685.33 | 0.02 | :thumbsdown: |
| MySQL | 937.50 | 533.00 | 998.98 | 134.48 | 211.11 |  |
| PostgreSQL | 976.35 | 791.99 | 982.84 | 731.73 | 47.05 | :thumbsdown: |
| MongoDB | 2,403.35 | 1,499.58 | 2,170.54 | 574.66 | 90.98 | :thumbsdown: |
| GraphDB | 29,832.71 | 445.31 | 4,383.93 | 106.43 | 338.74 | :thumbsup: |

## Write Operations


We don't benchmark edge insertions as those operations are uncommon in graph workloads.
Instead of that we benchmark **upserts** = inserts or updates.
Batch operations have different sizes for different DBs depending on memory consumption
and other limitations of each DB.
Concurrency is tested only in systems that explicitly support it.

### Random Writes: Upsert Edge

|  | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | graph-human-brain | Good in graph-human-brain |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| SQLite | 445.50 | 435.48 | 372.24 | 446.27 | 338.95 | :thumbsdown: |
| MySQL | 674.22 | 607.03 | 373.24 | 406.16 | 348.81 | :thumbsdown: |
| PostgreSQL | 763.39 | 631.47 | 547.85 | 702.21 | 521.75 | :thumbsdown: |
| MongoDB | 3,347.44 | 3,064.88 | 2,516.66 | 2,483.28 | 851.42 | :thumbsdown: |
| GraphDB | 5,426.79 | 4,636.66 | 3,798.41 | 4,146.34 | 4,008.92 | :thumbsup: |

### Random Writes: Upsert Edges Batch

|  | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | graph-human-brain | Good in graph-human-brain |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| SQLite | 1,360.65 | 1,146.63 | 1,177.27 | 1,140.73 | 1,133.51 | :thumbsdown: |
| MySQL | 1,055.15 | 1,014.81 | 849.62 | 856.45 | 828.88 | :thumbsdown: |
| PostgreSQL | 1,037.72 | 936.90 | 995.12 | 965.59 | 930.99 | :thumbsdown: |
| MongoDB | 14,350.05 | 11,351.20 | 6,482.28 | 6,439.03 | 1,446.09 | :thumbsdown: |
| GraphDB | 49,064.79 | 16,929.90 | 11,421.12 | 13,136.74 | 12,279.58 | :thumbsup: |

### Random Writes: Remove Edge

|  | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | graph-human-brain | Good in graph-human-brain |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| SQLite | 621.68 | 585.89 | 469.26 | 596.98 | 424.58 | :thumbsdown: |
| MySQL | 980.79 | 643.81 | 885.60 | 726.17 | 824.31 | :thumbsdown: |
| PostgreSQL | 1,448.48 | 1,093.10 | 897.67 | 1,061.85 | 917.14 | :thumbsdown: |
| MongoDB | 3,159.98 | 1,310.84 | 572.77 | 359.21 | 76.02 | :thumbsdown: |
| GraphDB | 6,614.31 | 4,384.99 | 3,153.38 | 4,103.24 | 3,339.86 | :thumbsup: |

### Random Writes: Remove Edges Batch

|  | graph-communities | graph-eachmovie-ratings | graph-patent-citations | graph-mouse-gene | graph-human-brain | Good in graph-human-brain |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| SQLite | 646.02 | 640.65 | 643.42 | 630.82 | 645.67 | :thumbsdown: |
| MySQL | 1,000.71 | 926.02 | 739.35 | 732.53 | 744.90 | :thumbsdown: |
| PostgreSQL | 1,458.10 | 1,287.87 | 1,254.80 | 1,419.80 | 1,247.01 | :thumbsdown: |
| MongoDB | 2,970.35 | 1,677.48 | 1,215.18 | 590.56 | 84.37 | :thumbsdown: |
| GraphDB | 41,944.00 | 16,977.09 | 11,524.81 | 13,074.22 | 12,387.68 | :thumbsup: |

## Device


* CPU: 8 cores, 16 threads @ 2300.00Mhz.
* RAM: 16.00 Gb
* Disk: 931.55 Gb
* OS: Darwin

