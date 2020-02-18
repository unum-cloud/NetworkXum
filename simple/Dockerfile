# Compute images will be both slimmer and faster 
# with Ubuntu base image instead of Alpine linus:
# https://pythonspeed.com/articles/alpine-docker-python/
FROM python:3.7-slim
RUN pip3 install pymongo~=3.10.0 urllib3~=1.24.3 fire~=0.2.1

# Install OpenCL driver before the lib:
# https://stackoverflow.com/a/52946862
RUN pip3 install --no-cache-dir pocl 
RUN pip3 install --no-cache-dir pybind11 
RUN pip3 install --no-cache-dir pyopencl 
RUN pip3 install --no-cache-dir matplotlib pandas
# RUN pip3 install rapids

# Prepare files.
COPY main.py /main.py

CMD python3 main.py