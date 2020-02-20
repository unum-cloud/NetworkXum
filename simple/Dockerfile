FROM continuumio/miniconda3:latest
RUN conda install -c anaconda pymongo
RUN conda install -c anaconda urllib3
RUN conda install -c conda-forge fire

# More GPGPU packages:
# https://docs.anaconda.com/anaconda/user-guide/tasks/gpu-packages/
# Smallest nices OpenCL-complete Docker image is this one:
# https://github.com/pkienzle/opencl_docker
# https://gitlab.com/nvidia/container-images/opencl/
RUN conda install -c anaconda cudatoolkit 
RUN conda install -c conda-forge pocl
RUN conda install -c conda-forge pyopencl
RUN conda install -c conda-forge binutils
RUN conda install -c conda-forge nvidia-ml
RUN conda install -c conda-forge clinfo

# Prepare files.
COPY main.py /main.py

CMD nvidia-smi && clinfo