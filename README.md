# PYthon + OpenCL + workER = pycler

A set of libraries and their benchmarks, that harness the power of GPUs via OpenCL, but pack it into simple Python lib.

## Project Structure

We implement the most essential operations as stream*processing operations on GPU.

* Encryption/Hashing.
  * MD5.
  * AES.
* Compression.
  * bz2.
  * gzip.
* Graph Analysis.
  * PageRank & Personalized PR.
  * Linearized Belief Propagation.
  * Graphical non*linear neural nets.
  * Node embeddings.
* Probabilistic tasks.
  * Percentile estimation.
  * HyperLogLog counters.
* Machine learning.
  * Stream dimesnion reduction.
  * Stream clustering.
  * Locality Sensitive hashing.
  
We provide a C API and binding for Apache Arrow datatypes to be automatically pushed onto GPU.
