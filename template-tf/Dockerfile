FROM continuumio/miniconda3:latest
RUN conda install -c anaconda pymongo
RUN conda install -c anaconda urllib3
RUN conda install -c conda-forge fire

RUN conda install -c anaconda tensorflow-gpu

CMD nvidia-smi