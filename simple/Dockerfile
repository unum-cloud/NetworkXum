FROM continuumio/miniconda3:latest
# https://anaconda.org/anaconda/pymongo
RUN conda install -c anaconda pymongo=3.9.0
# https://anaconda.org/anaconda/urllib3
RUN conda install -c anaconda urllib3=1.25.8
RUN conda install -c conda-forge fire=0.1.1

# More GPGPU packages:
# https://docs.anaconda.com/anaconda/user-guide/tasks/gpu-packages/
# RUN conda install -c hcc cuda-driver
RUN conda install -c anaconda cudatoolkit 
RUN conda install -c conda-forge pocl
# RUN conda install -c conda-forge khronos-opencl-icd-loader
RUN conda install -c conda-forge pyopencl

# Prepare files.
COPY main.py /main.py

CMD python3 main.py