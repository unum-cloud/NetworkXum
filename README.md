# PYthon + OpenCL + workER = pycler

Access the power of GPU with simplicity of Python and portability of OpenCL.
We implement the most essential operations as stream-processing operations on GPU.

Apps:
- Encryption/Hashing.
  - MD5.
  - AES.
- Compression.
  - bz2.
  - gzip.
- Graph Analysis.
  - PageRank & Personalized PR.
  - Linearized Belief Propagation.
  - Graphical non0linear neural nets.
- Probabilistic tasks.
  - Percentile estimation.
  - HyperLogLog counters.
- Machine learning.
  - Stream dimesnion reduction.
  - Stream clustering.
  - Locality Sensitive hashing.
  

We provide a C API and binding for Apache Arrow datatypes to be automatically pushed onto GPU.
