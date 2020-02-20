FROM continuumio/miniconda3:latest
# https://anaconda.org/anaconda/pymongo
# https://anaconda.org/anaconda/urllib3
RUN conda install -c anaconda pymongo
RUN conda install -c anaconda urllib3
RUN conda install -c conda-forge fire

# More GPGPU packages:
# https://docs.anaconda.com/anaconda/user-guide/tasks/gpu-packages/
# Smallest nices OpenCL-complete Docker image is this one:
# https://github.com/pkienzle/opencl_docker
RUN conda install -c anaconda cudatoolkit 
RUN conda install -c conda-forge pocl
# RUN conda install -c conda-forge khronos-opencl-icd-loader
RUN conda install -c conda-forge pyopencl
RUN conda install -c conda-forge binutils
RUN conda install -c conda-forge nvidia-ml

# Source: https://github.com/pkienzle/opencl_docker/blob/master/Dockerfile
RUN mkdir -p /etc/OpenCL/vendors && \
    echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility
RUN rm -f /etc/OpenCL/vendors/mesa.icd

# Prepare files.
COPY main.py /main.py

CMD python3 main.py