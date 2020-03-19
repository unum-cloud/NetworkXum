cd ~/apps/PyCler
git pull
docker build -t unum/pycler/pytorch ./pytorch
docker run --gpus all unum/pycler/pytorch