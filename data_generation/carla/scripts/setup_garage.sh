#!/usr/bin/env bash


cd ads
cd carla_garage

# download and extract models
wget https://s3.eu-central-1.amazonaws.com/avg-projects-2/jaeger2023arxiv/models/pretrained_models.zip
unzip pretrained_models.zip
rm pretrained_models.zip

# prep python env
conda env create -f environment.yml
conda activate garage

cd ..
cd ..