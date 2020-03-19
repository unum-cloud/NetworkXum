cd ~/apps/PyCler
git pull
docker build -t unum/pycler/tf ./tf
docker run --gpus all unum/pycler/tf