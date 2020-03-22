#!/bin/sh
docker build --force-rm -t unum/pycler/graphdb .
docker-compose -f docker-compose.yml up --no-start
