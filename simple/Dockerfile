FROM python:3.7-alpine
RUN pip3 install pymongo~=3.10.0 urllib3~=1.24.3 fire~=0.2.1
RUN pip3 install pyopencl numpy #rapids

# Prepare files.
COPY main.py /main.py

CMD python3 main.py