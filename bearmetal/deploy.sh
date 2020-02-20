cd ~/apps/PyCler
git pull
docker build -t unum/pycler/bearmetal ./bearmetal
docker run --gpus all unum/pycler/bearmetal