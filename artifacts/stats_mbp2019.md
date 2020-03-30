# PyGraphDB Benchmark

Following tests compare the performance of various databases in classical graph operations.
Many DBs werent opptimizied for such use case, but still perform better than actual Graph DBs.
Following results are **specific to `fb-pages-company.edges` dataset and device** described below.
## Device

* CPU: 8 cores, 16 threads @ 2300.00Mhz.
* RAM: 16.00 Gb
* Disk: 931.55 Gb

## Simple Queries (ops/sec)

|  | Retrieve Directed Edge | Retrieve Undirected Edge | Retrieve Connected Edges | Retrieve Ingoing Edges | Retrieve Outgoing Edges | Result |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| SQLite | 1,278.22 | 1,086.93 | 1,170.30 |  | 1,419.41 | :thumbsup: |
| MySQL | 590.90 | 614.91 | 529.53 |  | 590.84 |  |
| PostgreSQL | 326.20 | 305.19 | 294.70 |  | 297.26 | :thumbsdown: |
| Neo4j | 82.60 | 78.16 | 75.39 |  | 76.95 | :thumbsdown: |
| MongoDB | 56.42 | 80.91 | 35.83 |  | 43.52 | :thumbsdown: |

## Complex Queries (ops/sec)

|  | Count Friends | Count Followers | Count Following | Retrieve Friends | Retrieve Friends of Friends | Result |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| SQLite | 1,453.94 | 1,627.44 |  | 1,226.09 | 150.47 | :thumbsup: |
| MySQL | 395.65 | 491.11 |  | 526.66 | 88.44 |  |
| PostgreSQL | 318.92 | 364.03 |  | 293.02 | 79.87 |  |
| Neo4j | 97.41 | 110.55 |  | 111.86 | 49.45 | :thumbsdown: |
| MongoDB | 35.10 | 43.75 |  | 35.00 | 15.32 | :thumbsdown: |

## Insertions (ops/sec)

|  | Insert Edge | Insert Edges Batch | Import Dump | Result |
| :--- | :---: | :---: | :---: | :---: |
| SQLite | 509.00 | 7,177.28 | 12,767.77 | :thumbsup: |
| MySQL | 145.84 | 6,202.72 | 8,832.01 | :thumbsdown: |
| PostgreSQL | 171.15 | 1,064.31 | 988.96 | :thumbsdown: |
| Neo4j | 217.57 | 166.53 | 97.99 |  |
| MongoDB | 41.36 | 7,492.13 | 8,549.08 | :thumbsdown: |

## Removals (ops/sec)

|  | Remove Edge | Remove Edges Batch | Remove Vertex | Remove All | Result |
| :--- | :---: | :---: | :---: | :---: | :---: |
| SQLite | 839.24 | 712.66 | 380.43 | 1,827,424.38 | :thumbsup: |
| MySQL | 210.02 | 203.29 | 164.41 | 77,234.82 | :thumbsdown: |
| PostgreSQL | 192.96 | 220.20 | 199.21 | 647,486.53 | :thumbsdown: |
| Neo4j | 230.51 | 167.82 | 2,358,087.96 | 4,626.08 | :thumbsdown: |
| MongoDB | 82.31 | 42.54 | 34.25 | 657,475.43 | :thumbsdown: |

