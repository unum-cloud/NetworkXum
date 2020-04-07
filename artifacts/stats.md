## Simple Search Queries

|            | Retrieve Ingoing Edges | Retrieve Connected Edges | Retrieve Directed Edge | Retrieve Outgoing Edges | Retrieve Undirected Edge | Result       |
| ---------- | ---------------------- | ------------------------ | ---------------------- | ----------------------- | ------------------------ | ------------ |
| PostgreSQL | 295.73                 | 294.70                   | 326.20                 | 297.26                  | 305.19                   | :thumbsdown: |
| SQLiteMem  | 2091.74                | 1579.95                  | 1895.73                | 1931.75                 | 1789.21                  | :thumbsup:   |
| SQLite     | 2028.63                | 1170.30                  | 1278.22                | 1419.41                 | 1086.93                  |              |
| MongoDB    | 46.67                  | 35.83                    | 56.42                  | 43.52                   | 80.91                    | :thumbsdown: |
| MySQL      | 638.75                 | 529.53                   | 590.90                 | 590.84                  | 614.91                   | :thumbsdown: |
| Neo4j      | 77.79                  | 75.39                    | 82.60                  | 76.95                   | 78.16                    | :thumbsdown: |

## Complex Search Queries

|            | Count Followers | Retrieve Friends of Friends | Retrieve Friends | Count Friends | Count Followers | Result       |
| ---------- | --------------- | --------------------------- | ---------------- | ------------- | --------------- | ------------ |
| PostgreSQL | 362.58          | 79.87                       | 293.02           | 318.92        | 364.03          |              |
| SQLiteMem  | 1696.61         | 154.77                      | 1484.09          | 1476.50       | 1729.20         | :thumbsup:   |
| SQLite     | 1642.76         | 150.47                      | 1226.09          | 1453.94       | 1627.44         | :thumbsup:   |
| MongoDB    | 45.62           | 15.32                       | 35.00            | 35.10         | 43.75           | :thumbsdown: |
| MySQL      | 491.51          | 88.44                       | 526.66           | 395.65        | 491.11          |              |
| Neo4j      | 103.57          | 49.45                       | 111.86           | 97.41         | 110.55          | :thumbsdown: |

## Insertions

|            | Insert Edge | Insert Edges Batch | Import Dump | Result       |
| ---------- | ----------- | ------------------ | ----------- | ------------ |
| PostgreSQL | 171.15      | 1064.31            | 988.96      | :thumbsdown: |
| SQLiteMem  | 1291.70     | 16273.28           | 16777.03    | :thumbsup:   |
| SQLite     | 509.00      | 7177.28            | 12767.77    |              |
| MongoDB    | 41.36       | 7492.13            | 8549.08     | :thumbsdown: |
| MySQL      | 145.84      | 6202.72            | 8832.01     | :thumbsdown: |
| Neo4j      | 217.57      | 166.53             | 97.99       | :thumbsdown: |

## Removals

|            | Remove All | Remove Vertex | Remove Edge | Remove Edges Batch | Result       |
| ---------- | ---------- | ------------- | ----------- | ------------------ | ------------ |
| PostgreSQL | 647486.53  | 199.21        | 192.96      | 220.20             | :thumbsdown: |
| SQLiteMem  | 9565520.52 | 1858.00       | 2842.31     | 2804.89            | :thumbsup:   |
| SQLite     | 1827424.38 | 380.43        | 839.24      | 712.66             | :thumbsdown: |
| MongoDB    | 657475.43  | 34.25         | 82.31       | 42.54              | :thumbsdown: |
| MySQL      | 77234.82   | 164.41        | 210.02      | 203.29             | :thumbsdown: |
| Neo4j      | 4626.08    | 2358087.96    | 230.51      | 167.82             | :thumbsdown: |

