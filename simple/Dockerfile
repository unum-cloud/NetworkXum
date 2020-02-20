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
RUN conda install -c conda-forge ocl-icd

RUN apt-get update && apt-get install -y --no-install-recommends \
        ocl-icd-libopencl1 \
        clinfo && \
    rm -rf /var/lib/apt/lists/*
RUN mkdir -p /etc/OpenCL/vendors && \
    echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility


# Prepare files.
COPY main.py /main.py

CMD nvidia-smi && clinfo