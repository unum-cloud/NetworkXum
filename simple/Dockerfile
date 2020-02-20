FROM python:3.7-slim
RUN pip3 install pymongo~=3.10.0 urllib3~=1.24.3 fire~=0.2.1

ENV PATH="/root/miniconda3/bin:${PATH}"
ARG PATH="/root/miniconda3/bin:${PATH}"

RUN apt-get update
RUN apt-get install -y wget && rm -rf /var/lib/apt/lists/*
RUN wget \
    https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh \
    && mkdir /root/.conda \
    && bash Miniconda3-latest-Linux-x86_64.sh -b \
    && rm -f Miniconda3-latest-Linux-x86_64.sh \
RUN conda --version

RUN conda install -c conda-forge pyopencl


# Prepare files.
COPY main.py /main.py

CMD python3 main.py