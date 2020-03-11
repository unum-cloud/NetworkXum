FROM continuumio/miniconda3:latest
RUN conda install -c anaconda pymongo
# The bindings are in the standard library already:
# https://docs.python.org/2/library/sqlite3.html
RUN conda install -c conda-forge sqlite
RUN conda install -c activisiongamescience rocksdb
RUN conda install -c activisiongamescience python-rocksdb

# Compare to pure on-GPU analytics
# https://github.com/rapidsai/cugraph
RUN conda install -c rapidsai cugraph

# Standard tools for benchmarking:
# https://github.com/ionelmc/pytest-benchmark
RUN conda install -c conda-forge pytest-benchmark

# In the future we will be capable of manually
# controlling the "GPUDirect Storage" pass-through
# from NVME to GPU.
# https://devblogs.nvidia.com/gpudirect-storage/