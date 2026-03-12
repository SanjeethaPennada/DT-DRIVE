#!/usr/bin/env bash

mkdir -p ads
cd ads

git clone https://github.com/autonomousvision/transfuser.git
cd transfuser
git checkout 2022

# download and extract models
mkdir model_ckpt
wget https://s3.eu-central-1.amazonaws.com/avg-projects/transfuser/models_2022.zip -P model_ckpt
unzip model_ckpt/models_2022.zip -d model_ckpt/
rm model_ckpt/models_2022.zip

# prep python env
conda env create -f environment.yml
conda activate tfuse
pip install --only-binary=torch-scatter torch-scatter -f https://data.pyg.org/whl/torch-1.12.0+cu113.html
pip install --only-binary=mmcv-full mmcv-full==1.6.0 -f https://download.openmmlab.com/mmcv/dist/cu113/torch1.12.0/index.html
pip install mmsegmentation==0.25.0
pip install mmdet==2.25.0


cd ..
cd ..