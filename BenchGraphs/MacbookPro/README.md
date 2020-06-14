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

* [Neo4J](https://neo4j.com) was designed specifically for graphs storage, but crashes consistently, so it was removed from comparison.
* [SQLite](https://www.sqlite.org), [MySQL](https://www.mysql.com), [PostgreSQL](https://www.postgresql.org) and other SQL DBs are the foundations of modern entrprise IT infrastructure.
* [MongoDB](https://www.sqlite.org/index.html) is a new NoSQL database currently values at aound $10 Bln.
* [GraphDB](https://unum.xyz) is our in-house solution.

Databases were configured to use 512 Mb of RAM for cache and 4 cores for query execution.

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
* [Human Brain Network](http://networkrepository.com/bn-human-Jung2015-M87102575.php).
    * Size: 4 Gb.
    * Edges: 87'273'967.
    * Average Degree: 186.

## Sequential Writes: Import CSV (edges/sec)

Every datascience project starts by importing the data.
Let's see how long it will take to load an adjacency list into each DB.
But before comparing DBs, let's see what our SSD is capable of by simply parsing the list (2 or 3 column CSV).
This will be our baseline for estimating the time required to build the indexes in each DB.

|                   | Patent Citations | Mouse Genes | Human Brain |
| :---------------- | :--------------: | :---------: | :---------: |
| Parsing in Python |    596,891.71    | 523,663.71  | 431,661.95  |
| SQLiteMem         |    71,887.72     |             |             |

Most DBs provide some form functionality for faster bulk imports, but not all of them where used in benchmarks for various reasons.

* Neo4J supports CSV imports, but it requires duplicating the imported file and constantly crashes (due to Java heap management issues).
* PostgreSQL and MySQL dialects of SQL have special functions for importing CSVs, but their functionality is very limited and performance gains aren't substantial. A better approach is to use unindexed table of incoming edges and later submit it into the main store once the data is absorbed. That's how we implemented it.
* MongoDB provides a command line tool, but it wasn't used to limit the number of binary dependencies and simplify configuration.

|            | Patent Citations | Mouse Genes | Human Brain | Good in Human Brain |
| :--------- | :--------------: | :---------: | :---------: | :-----------------: |
| SQLite     |    44,137.56     |  49,059.01  |  38,185.49  |    :thumbsdown:     |
| MySQL      |    14,636.07     |  18,370.53  |  12,185.34  |    :thumbsdown:     |
| PostgreSQL |     7,230.86     |  7,361.18   |  7,428.68   |    :thumbsdown:     |
| MongoDB    |    14,199.87     |  15,448.18  |  15,171.61  |    :thumbsdown:     |
| GraphDB    |    198,482.00    | 401,714.33  | 134,482.94  |    :thumbsdown:     |
| MGraphDB   |    285,056.99    | 875,710.22  | 549,628.79  |     :thumbsup:      |

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

|            | Patent Citations | Mouse Genes | Human Brain | Good in Human Brain |
| :--------- | :--------------: | :---------: | :---------: | :-----------------: |
| SQLite     |      565.20      |   569.89    |    0.04     |    :thumbsdown:     |
| MySQL      |      791.43      |   627.89    |   560.39    |    :thumbsdown:     |
| PostgreSQL |      310.87      |   485.25    |   569.41    |    :thumbsdown:     |
| MongoDB    |     1,550.38     |   567.44    |   174.32    |    :thumbsdown:     |
| GraphDB    |    22,528.48     |  51,553.01  |  37,496.58  |     :thumbsup:      |
| MGraphDB   |     7,937.44     |  18,170.31  |  7,024.40   |    :thumbsdown:     |

### Random Reads: Find Directed Edge

Input: 2 vertex identifiers (order is important).<br/>
Output: edge that connects them in given direction.<br/>
Metric: number of such edges returned per second.<br/>

|            | Patent Citations | Mouse Genes | Human Brain | Good in Human Brain |
| :--------- | :--------------: | :---------: | :---------: | :-----------------: |
| SQLite     |      487.21      |   462.52    |    0.03     |    :thumbsdown:     |
| MySQL      |      649.42      |   534.80    |   622.63    |    :thumbsdown:     |
| PostgreSQL |      689.94      |   345.37    |   488.56    |    :thumbsdown:     |
| MongoDB    |     1,373.88     |   317.53    |   162.91    |    :thumbsdown:     |
| GraphDB    |    10,874.39     |  48,047.33  |  19,324.58  |     :thumbsup:      |
| MGraphDB   |     3,797.41     |  8,211.14   |  3,816.05   |    :thumbsdown:     |

### Random Reads: Find Connected Edges

Input: 1 vertex identifier.<br/>
Output: all edges attached to it.<br/>
Metric: number of such edges returned per second.<br/>

|            | Patent Citations | Mouse Genes | Human Brain | Good in Human Brain |
| :--------- | :--------------: | :---------: | :---------: | :-----------------: |
| SQLite     |      381.21      |    40.21    |    31.85    |    :thumbsdown:     |
| MySQL      |      857.91      |    33.90    |    85.09    |    :thumbsdown:     |
| PostgreSQL |      894.25      |    44.62    |    28.20    |    :thumbsdown:     |
| MongoDB    |     2,441.84     |   129.69    |    67.33    |    :thumbsdown:     |
| GraphDB    |     8,652.50     |   821.97    |  2,243.16   |     :thumbsup:      |
| MGraphDB   |     4,062.32     |   103.42    |   315.89    |    :thumbsdown:     |

### Random Reads: Find Ingoing Edges

Input: 1 vertex identifier.<br/>
Output: all edges incoming into it.<br/>
Metric: number of such edges returned per second.<br/>

|            | Patent Citations | Mouse Genes | Human Brain |         Good in Human Brain          |
| :--------- | :--------------: | :---------: | :---------: | :----------------------------------: |
| SQLite     |       0.13       |    95.55    |    0.02     |             :thumbsdown:             |
| MySQL      |      791.89      |    66.36    |   128.18    |             :thumbsdown:             |
| PostgreSQL |      443.79      |   100.68    |    25.47    |             :thumbsdown:             |
| MongoDB    |     1,558.45     |   305.64    |    78.23    |             :thumbsdown:             |
| GraphDB    |    12,722.08     |  1,587.38   |  4,186.25   | :strawberry::strawberry::strawberry: |
| MGraphDB   |     3,610.75     |    97.86    |   316.31    |             :thumbsdown:             |

### Random Reads: Find Friends

Input: 1 vertex identifier.<br/>
Output: the identifiers of all unique vertexes that share an edge with the input.<br/>
Metric: number of neighbor identiefiers returned per second.<br/>

|            | Patent Citations | Mouse Genes | Human Brain | Good in Human Brain |
| :--------- | :--------------: | :---------: | :---------: | :-----------------: |
| SQLite     |      651.92      |    43.30    |    35.33    |    :thumbsdown:     |
| MySQL      |      837.92      |    33.89    |    75.76    |    :thumbsdown:     |
| PostgreSQL |      882.00      |    43.20    |    29.18    |    :thumbsdown:     |
| MongoDB    |     2,334.31     |   127.35    |    69.23    |    :thumbsdown:     |
| GraphDB    |    12,929.29     |  1,793.26   |  4,794.98   |     :thumbsup:      |
| MGraphDB   |    17,288.37     |  1,944.81   |  4,971.51   |     :thumbsup:      |

### Random Reads: Count Friends

Input: 1 vertex identifier.<br/>
Output: the total number of attached edges and their accumulated weight.<br/>
Metric: number queries per second.<br/>

|            | Patent Citations | Mouse Genes | Human Brain |      Good in Human Brain       |
| :--------- | :--------------: | :---------: | :---------: | :----------------------------: |
| SQLite     |      692.86      |   283.86    |    51.63    |          :thumbsdown:          |
| MySQL      |      862.79      |    7.10     |    64.27    |          :thumbsdown:          |
| PostgreSQL |      966.32      |   188.98    |    41.42    |          :thumbsdown:          |
| MongoDB    |     1,873.56     |   200.26    |    80.04    |          :thumbsdown:          |
| GraphDB    |    13,694.29     |  1,734.97   |  5,055.78   | :underage::underage::underage: |
| MGraphDB   |     4,361.97     |   113.43    |   344.57    |          :thumbsdown:          |

### Random Reads: Count Followers

Input: 1 vertex identifier.<br/>
Output: the total number of incoming edges and their accumulated weight.<br/>
Metric: number queries per second.<br/>

|            | Patent Citations | Mouse Genes | Human Brain |      Good in Human Brain       |
| :--------- | :--------------: | :---------: | :---------: | :----------------------------: |
| SQLite     |       0.37       |   685.33    |    0.02     |          :thumbsdown:          |
| MySQL      |      998.98      |   134.48    |   211.11    |          :thumbsdown:          |
| PostgreSQL |      982.84      |   731.73    |    47.05    |          :thumbsdown:          |
| MongoDB    |     2,170.54     |   574.66    |    90.98    |          :thumbsdown:          |
| GraphDB    |    14,298.05     |  4,192.80   |  9,389.60   | :underage::underage::underage: |
| MGraphDB   |     4,383.93     |   106.43    |   338.74    |          :thumbsdown:          |

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

|            | Patent Citations | Mouse Genes | Human Brain | Good in Human Brain |
| :--------- | :--------------: | :---------: | :---------: | :-----------------: |
| SQLite     |      372.24      |   446.27    |   338.95    |    :thumbsdown:     |
| MySQL      |      373.24      |   406.16    |   348.81    |    :thumbsdown:     |
| PostgreSQL |      547.85      |   702.21    |   521.75    |    :thumbsdown:     |
| MongoDB    |     2,516.66     |  2,483.28   |   851.42    |    :thumbsdown:     |
| GraphDB    |     3,362.11     |  4,093.78   |  4,199.33   |     :thumbsup:      |
| MGraphDB   |     3,798.41     |  4,146.34   |  4,008.92   |     :thumbsup:      |

### Random Writes: Upsert Edges Batch

Input: 500 new edges.<br/>
Output: 500 success/failure indicators.<br/>
Metric: number inserted edges per second.<br/>

|            | Patent Citations | Mouse Genes | Human Brain | Good in Human Brain |
| :--------- | :--------------: | :---------: | :---------: | :-----------------: |
| SQLite     |     1,177.27     |  1,140.73   |  1,133.51   |    :thumbsdown:     |
| MySQL      |      849.62      |   856.45    |   828.88    |    :thumbsdown:     |
| PostgreSQL |      995.12      |   965.59    |   930.99    |    :thumbsdown:     |
| MongoDB    |     6,482.28     |  6,439.03   |  1,446.09   |    :thumbsdown:     |
| GraphDB    |    11,073.18     |  9,408.31   |  11,381.79  |     :thumbsup:      |
| MGraphDB   |    11,421.12     |  13,136.74  |  12,279.58  |     :thumbsup:      |

### Random Writes: Remove Edge

Input: 1 existing edge.<br/>
Output: success/failure indicator.<br/>
Metric: number removed edges per second.<br/>

|            | Patent Citations | Mouse Genes | Human Brain | Good in Human Brain |
| :--------- | :--------------: | :---------: | :---------: | :-----------------: |
| SQLite     |      469.26      |   596.98    |   424.58    |    :thumbsdown:     |
| MySQL      |      885.60      |   726.17    |   824.31    |    :thumbsdown:     |
| PostgreSQL |      897.67      |  1,061.85   |   917.14    |    :thumbsdown:     |
| MongoDB    |      572.77      |   359.21    |    76.02    |    :thumbsdown:     |
| GraphDB    |     3,189.15     |  4,254.52   |  4,014.76   |     :thumbsup:      |
| MGraphDB   |     3,153.38     |  4,103.24   |  3,339.86   |     :thumbsup:      |

### Random Writes: Remove Edges Batch

Input: 500 existing edges.<br/>
Output: 500 success/failure indicators.<br/>
Metric: number removed edges per second.<br/>

|            | Patent Citations | Mouse Genes | Human Brain | Good in Human Brain |
| :--------- | :--------------: | :---------: | :---------: | :-----------------: |
| SQLite     |      643.42      |   630.82    |   645.67    |    :thumbsdown:     |
| MySQL      |      739.35      |   732.53    |   744.90    |    :thumbsdown:     |
| PostgreSQL |     1,254.80     |  1,419.80   |  1,247.01   |    :thumbsdown:     |
| MongoDB    |     1,215.18     |   590.56    |    84.37    |    :thumbsdown:     |
| GraphDB    |    10,530.37     |  9,744.00   |  11,756.17  |     :thumbsup:      |
| MGraphDB   |    11,524.81     |  13,074.22  |  12,387.68  |     :thumbsup:      |

