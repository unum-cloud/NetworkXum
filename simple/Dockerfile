FROM python:3.7-alpine
RUN pip3 install pymongo~=3.10.0 urllib3~=1.24.3 fire~=0.2.1

# Installing NumPy with PIP can be problemtic.
# Here is one potential solution (other than Anaconda or Miniconda):
# https://stackoverflow.com/a/57485724
RUN apk add --update --no-cache py3-numpy
ENV PYTHONPATH=/usr/lib/python3.7/site-packages
RUN pip3 install pybind11 pyopencl #rapids

# Prepare files.
COPY main.py /main.py

CMD python3 main.py