#!/bin/sh
docker build --force-rm -t unum/pycler/simple .
docker run --gpus=all -name="bench-simple-on-gpus" -d unum/pycler/simple
