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

# Following article from 2011 describes OpenCL installation:
# https://streamhpc.com/blog/2011-06-24/install-opencl-on-debianubuntu-orderly/
# For developers OpenCL consists of 5 parts:
# 1. GPUs-only: drivers with OpenCL-support
# 2. The OpenCL header-files
# 3. Vendor specific libraries (needed when using -lOpenCL)
# 4. libOpenCL.so -> a special driver
# 5. An installable client driver
# Currently GPU-drivers are always OpenCL-capable, so you only need to secure 4 steps. 

RUN apt-get update
# 2. Install headers
RUN apt-get install ocl-icd-opencl-dev 
# 3. Vendor specific libraries
# 3.a. Intel
RUN apt-get install libnuma1
RUN alien *.rpm
RUN dpkg -i *.deb
RUN cp /usr/lib64/libOpenCL.so /usr/lib64/OpenCL/vendors/intel/
RUN echo "/usr/lib64/OpenCL/vendors/intel" > /etc/ld.so.conf.d/opencl-vendor-intel.conf
RUN ldconfig
# 3.b. AMD
RUN mkdir -p /usr/lib64/OpenCL/vendors/amd/
RUN mv lib/x86_64/* /usr/lib64/OpenCL/vendors/amd/
RUN echo "/usr/lib64/OpenCL/vendors/amd" > /etc/ld.so.conf.d/opencl-vendor-amd.conf
RUN ldconfig
# 3.c. NVidia.
RUN echo "/usr/local/cuda/lib64" > /etc/ld.so.conf.d/opencl-vendor-nvidia.conf
RUN echo "/usr/local/cuda/lib" >> /etc/ld.so.conf.d/opencl-vendor-nvidia.conf
RUN ldconfig

# 4. libOpenCL.so
RUN ln -s /usr/lib64/libOpenCL.so /usr/lib64/libOpenCL.so.1.2
RUN ln -s /usr/lib/libOpenCL.so /usr/lib/libOpenCL.so.1.2
# 4.a. AMD
RUN ln -s /usr/lib64/OpenCL/vendors/amd/libOpenCL.so /usr/lib64/libOpenCL.so.1.2
RUN ln -s /usr/lib/OpenCL/vendors/amd/libOpenCL.so /usr/lib/libOpenCL.so.1.2
# 4.b. NVidia
RUN ln -s /usr/local/cuda/lib64/libOpenCL.so /usr/lib64/libOpenCL.so.1.1
RUN ln -s /usr/local/cuda/lib/libOpenCL.so /usr/lib/libOpenCL.so.1.1
# 4.c. Intel
RUN ln -s /usr/lib64/OpenCL/vendors/intel/libOpenCL.so /usr/lib64/libOpenCL.so.1.2
RUN ln -s /usr/lib/OpenCL/vendors/intel/libOpenCL.so /usr/lib/libOpenCL.so.1.2
# Add links
RUN ln -s /usr/lib64/libOpenCL.so.1.2 /usr/lib64/libOpenCL.so.1
RUN ln -s /usr/lib64/libOpenCL.so.1 /usr/lib64/libOpenCL.so
RUN ln -s /usr/lib/libOpenCL.so.1.2 /usr/lib/libOpenCL.so.1
RUN ln -s /usr/lib/libOpenCL.so.1 /usr/lib/libOpenCL.so
# Update configs
RUN echo "libatiocl64.so" > /etc/OpenCL/vendors/atiocl64.icd
RUN echo "libatiocl32.so" > /etc/OpenCL/vendors/atiocl32.icd
RUN echo "libintelocl.so" > /etc/OpenCL/vendors/intelocl.icd
RUN echo "libcuda.so" > /etc/OpenCL/vendors/nvidia.icd

# Prepare files.
COPY main.py /main.py

CMD nvidia-smi && clinfo