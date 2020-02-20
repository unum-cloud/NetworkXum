FROM continuumio/miniconda3:latest

# Compilers
RUN conda install -c conda-forge clang
RUN conda install -c conda-forge clangxx

# Mega-frameworks
RUN conda install -c conda-forge boost
RUN conda install -c conda-forge poco
RUN conda install -c conda-forge openssl

# Essentials
RUN conda install -c conda-forge fmt
RUN conda install -c conda-forge nlohmann_json
RUN conda install -c conda-forge curl

# Persistent Data
RUN conda install -c anaconda mongo-driver 
RUN conda install -c conda-forge sqlite
RUN conda install -c activisiongamescience rocksdb

# Performance
RUN conda install -c anaconda intel-openmp
RUN conda install -c anaconda cudatoolkit 
RUN conda install -c anaconda cudnn
RUN conda install -c conda-forge pocl
RUN conda install -c conda-forge binutils
RUN conda install -c conda-forge openmpi

# Math & AI
RUN conda install -c conda-forge eigen
RUN conda install -c conda-forge opencv
RUN conda install -c conda-forge halide
RUN conda install -c conda-forge dlib
RUN conda install -c fxihub arrayfire
RUN conda install -c anaconda tensorflow-gpu
RUN conda install -c pytorch pytorch

# Algorithms & Data Structures
RUN conda install -c conda-forge xgboost
RUN conda install -c conda-forge catboost

# Prepare files.

CMD nvidia-smi