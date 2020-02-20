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
RUN conda install -c conda-forge clinfo 



# Sources: 
# https://github.com/pkienzle/opencl_docker/blob/master/Dockerfile
# https://gitlab.com/nvidia/container-images/opencl/-/blob/ubuntu16.04/runtime/Dockerfile

# Intel
ARG INTEL_DRIVER=opencl_runtime_16.1.1_x64_ubuntu_6.4.0.25.tgz
ARG INTEL_DRIVER_URL=http://registrationcenter-download.intel.com/akdlm/irc_nas/9019
RUN mkdir -p /tmp/opencl-driver-intel
WORKDIR /tmp/opencl-driver-intel
RUN echo INTEL_DRIVER is $INTEL_DRIVER; \
    curl -O $INTEL_DRIVER_URL/$INTEL_DRIVER; \
    if echo $INTEL_DRIVER | grep -q "[.]zip$"; then \
        unzip $INTEL_DRIVER; \
        mkdir fakeroot; \
        for f in intel-opencl-*.tar.xz; do tar -C fakeroot -Jxvf $f; done; \
        cp -R fakeroot/* /; \
        ldconfig; \
    else \
        tar -xzf $INTEL_DRIVER; \
        for i in $(basename $INTEL_DRIVER .tgz)/rpm/*.rpm; do alien --to-deb $i; done; \
        dpkg -i *.deb; \
        rm -rf $INTEL_DRIVER $(basename $INTEL_DRIVER .tgz) *.deb; \
        mkdir -p /etc/OpenCL/vendors; \
        echo /opt/intel/*/lib64/libintelocl.so > /etc/OpenCL/vendors/intel.icd; \
    fi; \
    rm -rf /tmp/opencl-driver-intel;


# AMD
ARG AMD_DRIVER=amdgpu-pro-18.10-572953.tar.xz
ARG AMD_DRIVER_URL=https://www2.ati.com/drivers/linux/ubuntu
RUN mkdir -p /tmp/opencl-driver-amd
WORKDIR /tmp/opencl-driver-amd
RUN echo AMD_DRIVER is $AMD_DRIVER; \
    curl --referer $AMD_DRIVER_URL -O $AMD_DRIVER_URL/$AMD_DRIVER; \
    tar -Jxvf $AMD_DRIVER; \
    cd amdgpu-pro-*; \
    ./amdgpu-install; \
    apt-get install opencl-amdgpu-pro -y; \
    rm -rf /tmp/opencl-driver-amd;
    
# NVidia
RUN mkdir -p /etc/OpenCL/vendors && \
    echo "libnvidia-opencl.so.1" > /etc/OpenCL/vendors/nvidia.icd
ENV NVIDIA_VISIBLE_DEVICES all
ENV NVIDIA_DRIVER_CAPABILITIES compute,utility

RUN rm -f /etc/OpenCL/vendors/mesa.icd

# Prepare files.
COPY main.py /main.py

CMD python3 main.py