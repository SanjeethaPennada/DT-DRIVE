#!/usr/bin/env bash

mkdir -p ads
cd ads

REPO_URL="https://github.com/autonomousvision/carla_garage.git"
COMMIT="bc87dca"
DIR="transfuser_plus_plus"

git clone "$REPO_URL" "$DIR"
cd "$DIR"
git checkout "$COMMIT"

# download and extract models
wget https://s3.eu-central-1.amazonaws.com/avg-projects-2/jaeger2023arxiv/models/pretrained_models.zip
unzip pretrained_models.zip
rm pretrained_models.zip

# prep python env
conda env create -f environment.yml
conda activate garage

cd ..
cd ..