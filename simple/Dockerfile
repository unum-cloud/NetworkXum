FROM continuumio/miniconda3:latest
RUN conda config --add channels conda-forge
RUN conda install pymongo urllib3 fire

# More GPGPU packages:
# https://docs.anaconda.com/anaconda/user-guide/tasks/gpu-packages/
# Smallest nices OpenCL-complete Docker image is this one:
# https://github.com/pkienzle/opencl_docker
# https://gitlab.com/nvidia/container-images/opencl/
RUN conda install cudatoolkit pocl intel-compute-runtime beignet ocl-icd-system ocl-icd
RUN conda install pyopencl binutils
RUN conda install clinfo

# Prepare files.
COPY main.py /main.py

CMD nvidia-smi && clinfo