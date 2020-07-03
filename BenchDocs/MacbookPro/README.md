# How well can different DBs handle texts?


## Setup


### Databases


At [Unum](https://unum.xyz) we develop a neuro-symbolic AI, which means combining discrete structural representations of data and semi-continuous neural representations.
The common misconception is that CPU/GPU power is the bottleneck for designing AGI, but we would argue that it's the storage layer (unless you want to train on the same data over and over again).

* CPU ⇌ RAM bandwidth (DDR4): ~100 GB/s.
* GPU ⇌ VRAM bandwidth (HBM2): ~1,000 GB/s.
* CPU ⇌ GPU bandwidth (PCI-E Gen3 x16): ~15 GB/s.
* GPU ⇌ GPU bandwidth (NVLink): ~300 GB/s.
* CPU ⇌ SSD bandwidth (NVMe): ~2 GB/s.

As we can see, the theoretical throughput between storage (SSD) and CPU is by far the biggest bottleneck.
2 GB/s doesn't sound very scary, but the problem is that **most databases can hardly saturate 10% of that capacity (or 200 MB/s)!**
When it comes to random (opposed to sequential) read operations the performance drops further to <1% of channel capacity.
That's why it's crucial for us to store the data in the most capable database!


### Device


* CPU: 8 cores, 16 threads @ 2300.00 Mhz.
* RAM: 16.00 GB
* Disk: 931.55 GB
* OS: Darwin


### Datasets


* [Patent Citation Network](http://networkrepository.com/cit-patent.php).
    * Size: 272 MB.
    * Edges: 16,518,947.
    * Average Degree: 8.
* [Mouse Gene Regulatory Network](http://networkrepository.com/bio-mouse-gene.php).
    * Size: 295 MB.
    * Edges: 14,506,199.
    * Average Degree: 670.
* [HumanBrain Network](http://networkrepository.com/bn-human-Jung2015-M87102575.php).
    * Size: 4 GB.
    * Edges: 87'273'967.
    * Average Degree: 186.


## Sequential Writes: Import CSV (edges/sec)


Every datascience project starts by importing the data.
Let's see how long it will take to load every dataset into each DB.


|               | Covid19 |
| :------------ | :-----: |
| MongoDB       |  40.13  |
| ElasticSearch |  21.87  |

|               |     Covid19     |
| :------------ | :-------------: |
| MongoDB       | 19 mins, 5 secs |
| ElasticSearch | 35 mins, 1 secs |

Those benchmarks only tell half of the story. 
We should not only consider performance, but also the used disk space and the affect on the hardware lifetime, as SSDs don't last too long.
Unum has not only the highest performance, but also the most compact representation. For the `HumanBrain` graph results are:

* MongoDB: 1,1 GB for data + 2,5 GB for indexes = 3,6 GB. Wrote ~25 GB to disk.
* ElasticSearch: .
* Unum: 1.5 GB total volume. Extra 3.8 GB of space were (optionally) used requested to slighly accelerate the import time. All of that space was reclaimed. A total of 5.3 was written to disk.


## Read Queries


### Random Reads: Lookup Doc by ID


Input: 1 document identifier.<br/>
Output: text content.<br/>
Metric: number of such queries returned per second.<br/>


|               | Covid19  |
| :------------ | :------: |
| MongoDB       | 2,652.10 |
| ElasticSearch |  447.98  |

### Random Reads: Find All Docs with Substring


Input: 1 randomly selected word.<br/>
Output: all documents IDs containing it.<br/>
Metric: number of such queries returned per second.<br/>


|               | Covid19  |
| :------------ | :------: |
| MongoDB       |   0.15   |
| ElasticSearch | 1,192.92 |

### Random Reads: Find 20 Docs with Substring


Input: 1 randomly selected word.<br/>
Output: up to 20 documents IDs containing it.<br/>
Metric: number of such queries returned per second.<br/>


|               | Covid19  |
| :------------ | :------: |
| MongoDB       |   0.17   |
| ElasticSearch | 1,838.35 |

### Random Reads: Find All Docs with Bigram


Input: a combination of randomly selected words.<br/>
Output: all documents containing it.<br/>
Metric: number of such queries returned per second.<br/>


|               | Covid19  |
| :------------ | :------: |
| MongoDB       |   0.10   |
| ElasticSearch | 1,876.19 |

### Random Reads: Find a RegEx


Input: a regular expression.<br/>
Output: all documents containing it.<br/>
Metric: number of such queries returned per second.<br/>


|               | Covid19 |
| :------------ | :-----: |
| MongoDB       |         |
| ElasticSearch |         |

## Write Operations


We primarily benchmark **upserts** = inserts or updates.
Batch operations have different sizes for different DBs depending 
on memory consumption and other limitations of each DB.


### Random Writes: Upsert Doc


Input: 1 new document.<br/>
Output: success/failure indicator.<br/>
Metric: number inserted docs per second.<br/>


|               | Covid19 |
| :------------ | :-----: |
| MongoDB       |  27.42  |
| ElasticSearch |  13.28  |

### Random Writes: Upsert Docs Batch


Input: 500 new docs.<br/>
Output: 500 success/failure indicators.<br/>
Metric: number inserted docs per second.<br/>


|               | Covid19 |
| :------------ | :-----: |
| MongoDB       |  29.36  |
| ElasticSearch |  23.15  |

### Random Writes: Remove Doc


Input: 1 existing document.<br/>
Output: success/failure indicator.<br/>
Metric: number removed docs per second.<br/>


|               | Covid19 |
| :------------ | :-----: |
| MongoDB       |  27.24  |
| ElasticSearch |  13.63  |

### Random Writes: Remove Docs Batch


Input: 500 existing docs.<br/>
Output: 500 success/failure indicators.<br/>
Metric: number removed docs per second.<br/>


|               | Covid19 |
| :------------ | :-----: |
| MongoDB       |  30.85  |
| ElasticSearch |  25.97  |

