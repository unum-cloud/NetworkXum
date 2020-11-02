# How well can different DBs handle texts?


## Setup


### Databases


At [Unum](https://unum.xyz) we develop a neuro-symbolic AI, which means combining discrete structural representations of data and semi-continuous neural representations.
The common misconception is that CPU/GPU power is the bottleneck for designing AGI, but we would argue that it's the storage layer (unless you want to train on the same data over and over again).

* CPU ⇌ RAM bandwidth ([DDR4](https://en.wikipedia.org/wiki/DDR4_SDRAM)): ~100 GB/s.
* GPU ⇌ VRAM bandwidth ([HBM2](https://en.wikipedia.org/wiki/High_Bandwidth_Memory)): ~1,000 GB/s.
* GPU ⇌ GPU bandwidth ([NVLink](https://en.wikipedia.org/wiki/NVLink)): ~300 GB/s.
* CPU ⇌ GPU bandwidth ([PCI-E Gen3 x16](https://en.wikipedia.org/wiki/PCI_Express)): ~15 GB/s (60 GB/s by 2022).
* CPU ⇌ SSD bandwidth ([NVMe over PCI-E Gen3 x4](https://en.wikipedia.org/wiki/NVM_Express)): ~2 GB/s (6 GB/s by 2022).

As we can see, the theoretical throughput between storage (SSD) and CPU is by far the biggest bottleneck.
2 GB/s isn't scary, but **most databases can hardly saturate 10% of that capacity (or 200 MB/s)** due to [read-amplification](http://smalldatum.blogspot.com/2015/11/read-write-space-amplification-pick-2_23.html) or random jumps.
That's why it's crucial for us to store the data in the most capable database!


### Device


* CPU:
    * Model: `Intel(R) Core(TM) i9-9880H CPU @ 2.30GHz`.
    * Cores: 8 (16 threads @ 2.3 Ghz).
* RAM Space: 16.0 GB.
* Disk Space: 931.5 GB.
* OS Family: Darwin.
* Python Version: 3.7.7.


### Datasets


* [Covid19](https://www.kaggle.com/allen-institute-for-ai/CORD-19-research-challenge) Scientific Papers.
  * Articles: 45,941.
  * Sections: 1,604,649.
  * Size: 1,7 GB.
* [PoliticalTweetsIndia](https://www.kaggle.com/iamyoginth/facthub) Posts.
  * Tweets: 12,488,143.
  * Size: 2,3 GB.
* [OldNewspapers](https://www.kaggle.com/alvations/old-newspapers) Articles in different languages.
  * Articles: 16,806,041.
  * Size: 2,3 GB.
* [EnglishWikipedia](https://www.kaggle.com/jkkphys/english-wikipedia-articles-20170820-sqlite) Dump from 2017.
  * Articles: 4,902,648.
  * Sections: 23,046,187.
  * Size: 18,2 GB.


## Sequential Writes: Import CSV (docs/sec)


Every datascience project starts by importing the data.
Let's see how long it will take to load every dataset into each DB.


|               | Covid19 | PoliticalTweetsIndia | EnglishWikipedia | Mean Gains |
| :------------ | :-----: | :------------------: | :--------------: | :--------: |
| MongoDB       |  42.98  |       3,339.69       |                  |     1x     |
| ElasticSearch | 210.14  |       6,649.18       |     1,152.83     | **1.58x**  |

|               |     Covid19      | PoliticalTweetsIndia | EnglishWikipedia |
| :------------ | :--------------: | :------------------: | :--------------: |
| MongoDB       | 17 mins, 49 secs |   49 mins, 54 secs   |                  |
| ElasticSearch | 3 mins, 39 secs  |   25 mins, 4 secs    | 1 hours, 10 mins |

Those benchmarks only tell half of the story. 
We should not only consider performance, but also the used disk space and the affect on the hardware lifetime, as SSDs don't last too long.
Unum has not only the highest performance, but also the most compact representation.
MongoDB generally performs well across different benchmarks, but it failed to import the English Wikipedia in 10 hours.
I suspect a bug in the implementation of the text index, as some batch import operations took over 10 mins for a modest batch size of 10,000 docs.


|               | Covid19 | PoliticalTweetsIndia | EnglishWikipedia |
| :------------ | :-----: | :------------------: | :--------------: |
| MongoDB       | 1,9 GB  |        3,2 GB        | Expected 60,7 GB |
| ElasticSearch | 2,5 GB  |        2,9 GB        |     33,5 GB      |
| Unum.TextDB   |    1    |          1           |        1         |

MongoDB is one of the best products on the DB market, but I suspect they have a bug in their text indexing capabilities. Some of the batch insertions were hanging for ~10 mins and only 15% of the largest dataset were imported after ~7 hours!

## Read Queries


Regular Expressions are the most computational intesive operations in textual database.
If the pattern is complex, even the most advanced DBs may not be able to utilize the pre-constructed search index.
As a result they will be forced to run a full-scan against all documents stored in the DB.
It means having at least 2 bottlenecks:

1. If you are scanning all the data in the DB you are limited by the sequential read performance of the SSD (accounting for the read amplification dependant on the data locality).
2. The speed of your RegEx engine.

The (1.) point is pretty clear, but the (2.) is much more complex. Most DBs use the [PCRE/PCRE2](http://www.pcre.org) C library which was first released back in 1997 with a major upgrade in 2015.<br/>
Implementing full RegEx support is complex, especially if you want to beat C code in performance, so most programming languages and libraries just wrap PCRE.<br/>
That said, the performance is still laughable. It varies a lot between different different queries, but [can be orders of magniture slower](https://rust-leipzig.github.io/regex/2017/03/28/comparison-of-regex-engines/) than [Intel Hyperscan](https://software.intel.com/content/www/us/en/develop/articles/introduction-to-hyperscan.html) State-of-theArt library.<br/>
Most (if not all) of those libraries use the classical **DFA-based algorithm with `~O(n)` worst case time complexity for search** (assuming the automata is already constructed).<br/>
As always, we are not limiting ourselves to using existing algorithms, we design our own. In `Unum.ReGex` we have developed an algorithm with worst-case-complexity harder than the DFA approach, but the average complexity is also `~O(n)`.<br/>
However, **the constant multiplier in our case is much lower, so the new algorithm ends-up beating the classical solutions from Intel, Google** and other companies at least in some cases. <br/>
On our test bench the timings are:

*   Intel Hyperscan on 1 Intel Core: 4 GB/s consistent performance.
*   Unum.RegEx on 1 Intel Core: up to 3 GB/s.
*   Unum.RegEx on 1 Intel Core (after text preprocessing): **up to 15 GB/s**.
*   Unum.RegEx on Titan V GPU: ? GB/s.
*   Unum.RegEx on Titan V GPU (after text preprocessing): ? GB/s.

The best part is that it can use statistics and cleverly organizind search indexes to vastly reduce the number of documents to be scanned.
To our knowledge, no modern piece of software has such level of **mutually-benefitial communication between the storage layer and the application layer**.
<br/><br/>
The results below speak for themselves, but before we go further I would like to note, that comparing randomly generated RegEx queries makes little sense, as such results wouldn't translate into real-world benefits for potential users. 
There are not too many universally used RegEx patterns, so the DBs can use the cache to fetch previously computed results.
Such benchmarks are not representative as well, so I took the most common RegEx patterns (dates, numbers, IP addresses, E-mail addresses, XML tags...) and concatentated them with randomly sampled words from each of the datasets.
That way we are still getting results similar to real-world queries, but avoid cache hits.


### Random Reads: Lookup Doc by ID


Input: 1 document identifier.<br/>
Output: text content.<br/>
Metric: number of such queries returned per second.<br/>


|               | Covid19  | PoliticalTweetsIndia | EnglishWikipedia | Mean Gains |
| :------------ | :------: | :------------------: | :--------------: | :--------: |
| MongoDB       | 2,457.27 |       1,588.46       |     2,270.19     |     1x     |
| ElasticSearch |  519.67  |        617.50        |      629.71      |   0.28x    |

### Random Reads: Find up to 10,000 Docs containing a Word


Input: 1 randomly selected word.<br/>
Output: up to 10,000 documents IDs containing it.<br/>
Metric: number of such queries returned per second.<br/>


|               | Covid19 | PoliticalTweetsIndia | EnglishWikipedia | Mean Gains |
| :------------ | :-----: | :------------------: | :--------------: | :--------: |
| MongoDB       |  0.13   |         2.41         |       0.20       |     1x     |
| ElasticSearch |  0.69   |         0.48         |       0.33       |   0.54x    |

### Random Reads: Find up to 20 Docs containing a Word


Input: 1 randomly selected word.<br/>
Output: up to 20 documents IDs containing it.<br/>
Metric: number of such queries returned per second.<br/>


|               | Covid19 | PoliticalTweetsIndia | EnglishWikipedia | Mean Gains |
| :------------ | :-----: | :------------------: | :--------------: | :--------: |
| MongoDB       |  4.25   |        113.38        |       0.82       |     1x     |
| ElasticSearch | 234.04  |        169.76        |      72.17       | **4.02x**  |

### Random Reads: Find up to 20 Docs with Bigram


Input: a combination of randomly selected words.<br/>
Output: all documents IDs containing it.<br/>
Metric: number of such queries returned per second.<br/>


|               | Covid19 | PoliticalTweetsIndia | EnglishWikipedia | Mean Gains  |
| :------------ | :-----: | :------------------: | :--------------: | :---------: |
| MongoDB       |  0.09   |         0.49         |       0.02       |     1x      |
| ElasticSearch | 241.92  |        88.08         |      32.02       | **606.10x** |

## Write Operations


We primarily benchmark **upserts** = inserts or updates.
Batch operations have different sizes for different DBs depending 
on memory consumption and other limitations of each DB.


### Random Writes: Upsert Doc


Input: 1 new document.<br/>
Output: success/failure indicator.<br/>
Metric: number inserted docs per second.<br/>


|               | Covid19 | PoliticalTweetsIndia | EnglishWikipedia | Mean Gains |
| :------------ | :-----: | :------------------: | :--------------: | :--------: |
| MongoDB       |  30.00  |        509.45        |      22.22       |     1x     |
| ElasticSearch |  13.28  |        14.16         |      14.05       |   0.07x    |

### Random Writes: Upsert Docs Batch


Input: 500 new docs.<br/>
Output: 500 success/failure indicators.<br/>
Metric: number inserted docs per second.<br/>


|               | Covid19 | PoliticalTweetsIndia | EnglishWikipedia | Mean Gains |
| :------------ | :-----: | :------------------: | :--------------: | :--------: |
| MongoDB       |  31.09  |       1,672.29       |      21.40       |     1x     |
| ElasticSearch |  23.15  |        20.88         |      26.40       |   0.04x    |

### Random Writes: Remove Doc


Input: 1 existing document.<br/>
Output: success/failure indicator.<br/>
Metric: number removed docs per second.<br/>


|               | Covid19 | PoliticalTweetsIndia | EnglishWikipedia | Mean Gains |
| :------------ | :-----: | :------------------: | :--------------: | :--------: |
| MongoDB       |  21.08  |        221.75        |      58.35       |     1x     |
| ElasticSearch |  13.63  |        12.67         |      11.76       |   0.13x    |

### Random Writes: Remove Docs Batch


Input: 500 existing docs.<br/>
Output: 500 success/failure indicators.<br/>
Metric: number removed docs per second.<br/>


|               | Covid19 | PoliticalTweetsIndia | EnglishWikipedia | Mean Gains |
| :------------ | :-----: | :------------------: | :--------------: | :--------: |
| MongoDB       |  32.48  |       1,772.88       |      21.08       |     1x     |
| ElasticSearch |  25.97  |        20.58         |      26.07       |   0.04x    |

