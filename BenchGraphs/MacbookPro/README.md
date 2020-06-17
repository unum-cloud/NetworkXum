# How well can different DBs handle graphs (networks)?


At [Unum](https://unum.xyz) we develop a neuro-symbolic AI, which means combining discrete structural representations of data and semi-continuous neural representations.
The common misconception is that CPU/GPU power is the bottleneck for designing AGI, but we would argue that it's the storage layer.

* CPU ⇌ RAM bandwidth: ~100 GB/s.
* GPU ⇌ VRAM bandwidth: ~1,000 GB/s.
* CPU ⇌ GPU bandwidth: ~15 GB/s.
* GPU ⇌ GPU bandwidth: ~300 GB/s.
* CPU ⇌ SSD bandwidth: ~2 GB/s.

As we can see, the theoretical throughput between storage (SSD) and CPU is by far the biggest bottleneck.
2 GB/s doesn't sound very scary, but the problem is that **most databases can hardly saturate 10%% of that capacity (or 200 MB/s)!**
When it comes to random (opposed to sequential) read operations the performance drops further to <1%% of channel capacity.
That's why it's crucial for us to store the data in the most capable database!


## Setup


### Databases


* [SQLite](https://www.sqlite.org) is the most minimalistic SQL database. 
* [MySQL](https://www.mysql.com) is the most widely used Open-Source DB in the world. 
* [PostgreSQL](https://www.postgresql.org) is the 2nd most popular Open-Source DB.
* [MongoDB](https://www.sqlite.org/index.html) is the most popular NoSQL database. `$MDB` is values at aound $10 Bln.
* [Neo4J](https://neo4j.com) was designed specifically for graphs storage, but crashes consistently, so it was removed from comparison.
* [GraphDB](https://unum.xyz) is our in-house solution.

Databases were configured to use 512 Mb of RAM for cache and 4 cores for query execution.
Links: [The Most Popular Open Source Databases 2020](https://www.percona.com/blog/2020/04/22/the-state-of-the-open-source-database-industry-in-2020-part-three/).


### Device


* CPU: 8 cores, 16 threads @ 2300.00 Mhz.
* RAM: 16.00 Gb
* Disk: 931.55 Gb
* OS: Darwin


### Datasets


* [Patent Citation Network](http://networkrepository.com/cit-patent.php).
    * Size: 77 Mb.
    * Edges: 16,518,947.
    * Average Degree: 8.
* [Mouse Gene Regulatory Network](http://networkrepository.com/bio-mouse-gene.php).
    * Size: 300 Mb.
    * Edges: 14,506,199.
    * Average Degree: 670.
* [HumanBrain Network](http://networkrepository.com/bn-human-Jung2015-M87102575.php).
    * Size: 4 Gb.
    * Edges: 87'273'967.
    * Average Degree: 186.


## Sequential Writes: Import CSV (edges/sec)


Every datascience project starts by importing the data.
Let's see how long it will take to load an adjacency list into each DB.
But before comparing DBs, let's see what our SSD is capable of by simply parsing the list (2 or 3 column CSV).
This will be our baseline for estimating the time required to build the indexes in each DB.


|                   | PatentCitations | MouseGenes | HumanBrain |
| :---------------- | :-------------: | :--------: | :--------: |
| Parsing in Python |   606,288.73    | 532,980.66 | 465,800.36 |

Most DBs provide some form functionality for faster bulk imports, but not all of them where used in benchmarks for various reasons.

* Neo4J supports CSV imports, but it requires duplicating the imported file and constantly crashes (due to Java heap management issues).
* PostgreSQL and MySQL dialects of SQL have special functions for importing CSVs, but their functionality is very limited and performance gains aren't substantial. A better approach is to use unindexed table of incoming edges and later submit it into the main store once the data is absorbed. That's how we implemented it.
* MongoDB provides a command line tool, but it wasn't used to limit the number of binary dependencies and simplify configuration.


|            | PatentCitations | MouseGenes | HumanBrain | Gains in HumanBrain |
| :--------- | :-------------: | :--------: | :--------: | :-----------------: |
| PostgreSQL |    7,522.24     |  7,306.20  |  7,469.46  |         1x          |
| MySQL      |    14,698.93    | 18,549.58  | 12,144.30  |        1.63x        |
| SQLite     |    50,057.93    | 43,819.69  | 34,728.02  |        4.65x        |
| MongoDB    |    15,135.22    | 14,759.00  | 15,125.21  |        2.02x        |
| GraphDB    |   213,415.62    | 633,552.81 | 414,012.72 |       55.43x        |

The benchmarks were repeated dozens of times. 
These numbers translate into following import duration for each dataset.


|            | PatentCitations  |    MouseGenes    |    HumanBrain    |
| :--------- | :--------------: | :--------------: | :--------------: |
| PostgreSQL | 36 mins, 36 secs | 33 mins, 5 secs  | 3 hours, 14 mins |
| MySQL      | 18 mins, 44 secs | 13 mins, 2 secs  | 1 hours, 59 mins |
| SQLite     | 5 mins, 30 secs  | 5 mins, 31 secs  | 41 mins, 53 secs |
| MongoDB    | 18 mins, 11 secs | 16 mins, 23 secs | 1 hours, 36 mins |
| GraphDB    | 1 mins, 17 secs  | 0 mins, 23 secs  | 3 mins, 31 secs  |

Those benchmarks only tell half of the story. 
We should not only consider performance, but also the used disk space and the affect on the hardware lifetime, as SSDs don't last too long.
Unum has not only the highest performance, but also the most compact representation. For the `HumanBrain` graph results are:

* MongoDB: 1,1 Gb for data + 2,5 Gb for indexes = 3,6 Gb. Wrote ~25 Gb to disk.
* MySQL: 8.5 Gb for data + 6.4 Gb for indexes = 14.9 Gb. Wrote ~300 Gb to disk.
* PostgreSQL: 6 Gb for data + 9 Gb for indexes = 15 Gb. Wrote ~25 Gb to disk. Furthermore, after flushing the changes, it didn't reclaim 8 Gb of space from the temporary table.
* Unum: 1.5 Gb total volume. Extra 3.8 Gb of space were (optionally) used requested to slighly accelerate the import time. All of that space was reclaimed. A total of 5.3 was written to disk.


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


Input: 2 vertex identifiers.<br/>
Output: edge that connects them.<br/>
Metric: number of such edges returned per second.<br/>


|            | PatentCitations | MouseGenes | HumanBrain | Gains in HumanBrain |
| :--------- | :-------------: | :--------: | :--------: | :-----------------: |
| PostgreSQL |     795.55      |   358.33   |   533.47   |         1x          |
| MySQL      |     659.80      |   778.07   |   503.36   |        0.94x        |
| SQLite     |     295.62      |   389.14   |   51.15    |        0.10x        |
| MongoDB    |     990.73      |   980.28   |   136.46   |        0.26x        |
| GraphDB    |    19,947.87    | 60,166.34  | 36,392.62  |       68.22x        |

### Random Reads: Find Directed Edge


Input: 2 vertex identifiers (order is important).<br/>
Output: edge that connects them in given direction.<br/>
Metric: number of such edges returned per second.<br/>


|            | PatentCitations | MouseGenes | HumanBrain | Gains in HumanBrain |
| :--------- | :-------------: | :--------: | :--------: | :-----------------: |
| PostgreSQL |     686.19      |   381.83   |   459.56   |         1x          |
| MySQL      |     672.81      |   616.83   |   547.84   |        1.19x        |
| SQLite     |     282.41      |   375.69   |   47.57    |        0.10x        |
| MongoDB    |    1,002.83     |   734.23   |   145.53   |        0.32x        |
| GraphDB    |    9,879.49     | 55,039.13  | 17,609.57  |       38.32x        |

### Random Reads: Find Connected Edges


Input: 1 vertex identifier.<br/>
Output: all edges attached to it.<br/>
Metric: number of such edges returned per second.<br/>


|            | PatentCitations | MouseGenes | HumanBrain | Gains in HumanBrain |
| :--------- | :-------------: | :--------: | :--------: | :-----------------: |
| PostgreSQL |     328.63      |    8.08    |   24.17    |         1x          |
| MySQL      |     540.34      |   35.92    |   90.80    |        3.76x        |
| SQLite     |     312.83      |   17.94    |   28.93    |        1.20x        |
| MongoDB    |     779.87      |   128.89   |   58.69    |        2.43x        |
| GraphDB    |    13,079.72    |   448.47   |  1,265.66  |       52.36x        |

### Random Reads: Find Ingoing Edges


Input: 1 vertex identifier.<br/>
Output: all edges incoming into it.<br/>
Metric: number of such edges returned per second.<br/>


|            | PatentCitations | MouseGenes | HumanBrain | Gains in HumanBrain |
| :--------- | :-------------: | :--------: | :--------: | :-----------------: |
| PostgreSQL |     365.96      |   74.56    |   24.36    |         1x          |
| MySQL      |     760.76      |   80.79    |   132.62   |        5.44x        |
| SQLite     |     281.01      |   84.61    |   30.81    |        1.26x        |
| MongoDB    |    1,225.93     |   373.95   |   67.70    |        2.78x        |
| GraphDB    |    14,139.46    |  1,682.84  |  4,313.47  |       177.04x       |

### Random Reads: Find Friends


Input: 1 vertex identifier.<br/>
Output: the identifiers of all unique vertexes that share an edge with the input.<br/>
Metric: number of neighbor identiefiers returned per second.<br/>


|            | PatentCitations | MouseGenes | HumanBrain | Gains in HumanBrain |
| :--------- | :-------------: | :--------: | :--------: | :-----------------: |
| PostgreSQL |     314.14      |   10.39    |   24.50    |         1x          |
| MySQL      |     505.74      |   34.54    |   83.49    |        3.41x        |
| SQLite     |     301.06      |   39.58    |   28.94    |        1.18x        |
| MongoDB    |     986.09      |   137.81   |   59.64    |        2.43x        |
| GraphDB    |    17,127.20    |  1,970.54  |  4,942.23  |       201.70x       |

### Random Reads: Count Friends


Input: 1 vertex identifier.<br/>
Output: the total number of attached edges and their accumulated weight.<br/>
Metric: number queries per second.<br/>


|            | PatentCitations | MouseGenes | HumanBrain | Gains in HumanBrain |
| :--------- | :-------------: | :--------: | :--------: | :-----------------: |
| PostgreSQL |     330.16      |   73.70    |   30.44    |         1x          |
| MySQL      |     616.57      |    7.83    |   51.40    |        1.69x        |
| SQLite     |     324.47      |   195.61   |   39.07    |        1.28x        |
| MongoDB    |     912.83      |   218.61   |   67.06    |        2.20x        |
| GraphDB    |    15,867.33    |   605.78   |  1,859.41  |       61.09x        |

### Random Reads: Count Followers


Input: 1 vertex identifier.<br/>
Output: the total number of incoming edges and their accumulated weight.<br/>
Metric: number queries per second.<br/>


|            | PatentCitations | MouseGenes | HumanBrain | Gains in HumanBrain |
| :--------- | :-------------: | :--------: | :--------: | :-----------------: |
| PostgreSQL |     362.16      |   578.65   |   33.78    |         1x          |
| MySQL      |     821.91      |   132.29   |   214.55   |        6.35x        |
| SQLite     |     360.58      |   646.95   |   40.73    |        1.21x        |
| MongoDB    |    1,241.53     |   601.68   |   77.26    |        2.29x        |
| GraphDB    |    16,800.24    |  4,275.98  |  9,572.43  |       283.34x       |

## Write Operations


We don't benchmark edge insertions as those operations are uncommon in graph workloads.
Instead of that we benchmark **upserts** = inserts or updates.
Batch operations have different sizes for different DBs depending on memory consumption
and other limitations of each DB.
Concurrency is tested only in systems that explicitly support it.


### Random Writes: Upsert Edge


Input: 1 new edge.<br/>
Output: success/failure indicator.<br/>
Metric: number inserted edges per second.<br/>


|            | PatentCitations | MouseGenes | HumanBrain | Gains in HumanBrain |
| :--------- | :-------------: | :--------: | :--------: | :-----------------: |
| PostgreSQL |     421.67      |   491.60   |   454.61   |         1x          |
| MySQL      |     396.75      |   407.14   |   309.22   |        0.68x        |
| SQLite     |     347.70      |   364.13   |   278.15   |        0.61x        |
| MongoDB    |    1,524.28     |  2,064.84  |   845.99   |        1.86x        |
| GraphDB    |    4,065.29     |  4,164.98  |  3,938.13  |        8.66x        |

### Random Writes: Upsert Edges Batch


Input: 500 new edges.<br/>
Output: 500 success/failure indicators.<br/>
Metric: number inserted edges per second.<br/>


|            | PatentCitations | MouseGenes | HumanBrain | Gains in HumanBrain |
| :--------- | :-------------: | :--------: | :--------: | :-----------------: |
| PostgreSQL |     567.80      |   819.02   |   746.89   |         1x          |
| MySQL      |     812.79      |   795.84   |   786.82   |        1.05x        |
| SQLite     |    1,073.77     |  1,115.09  |  1,004.13  |        1.34x        |
| MongoDB    |    4,192.98     |  5,427.22  |  1,639.07  |        2.19x        |
| GraphDB    |    11,190.59    | 11,032.29  | 10,223.71  |       13.69x        |

### Random Writes: Remove Edge


Input: 1 existing edge.<br/>
Output: success/failure indicator.<br/>
Metric: number removed edges per second.<br/>


|            | PatentCitations | MouseGenes | HumanBrain | Gains in HumanBrain |
| :--------- | :-------------: | :--------: | :--------: | :-----------------: |
| PostgreSQL |     862.59      |   996.31   |   855.55   |         1x          |
| MySQL      |     822.14      |   732.72   |   745.51   |        0.87x        |
| SQLite     |     422.41      |   444.84   |   382.08   |        0.45x        |
| MongoDB    |     525.93      |   297.69   |   71.89    |        0.08x        |
| GraphDB    |    3,552.51     |  4,230.23  |  3,947.07  |        4.61x        |

### Random Writes: Remove Edges Batch


Input: 500 existing edges.<br/>
Output: 500 success/failure indicators.<br/>
Metric: number removed edges per second.<br/>


|            | PatentCitations | MouseGenes | HumanBrain | Gains in HumanBrain |
| :--------- | :-------------: | :--------: | :--------: | :-----------------: |
| PostgreSQL |    1,243.77     |  1,312.31  |  1,282.17  |         1x          |
| MySQL      |     689.72      |   641.08   |   649.54   |        0.51x        |
| SQLite     |     605.12      |   615.77   |   595.16   |        0.46x        |
| MongoDB    |     916.13      |   436.58   |   82.23    |        0.06x        |
| GraphDB    |    11,185.17    | 11,124.88  | 10,176.45  |        7.94x        |

