cd ~/apps/PyCler
git pull
docker build -t unum/pycler/simple ./simple
docker run --gpus all unum/pycler/simple