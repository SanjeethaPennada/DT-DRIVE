# Replication package for the paper 'Empirically Evaluating Flaky Tests for Autonomous Driving Systems in Simulated Environments'

Submitted to TFW 2025, at ICSE 2025.

This directory contains scripts to recreate case studies present in the paper, as well as data used in the results section.
## Directory structure overview:
```
replication_package/
├─ data_generation/
│  ├─ carla/
│  │  ├─ scripts/
│  │  │  ├─ REPLICATE.sh/
│  ├─ metadrive/
│  │  ├─ REPLICATE.sh/
├─ results/
│  ├─ carla/
│  │  ├─ data/
│  │  ├─ notebooks/
│  ├─ metadrive/
│  │  ├─ data/
│  │  ├─ notebooks/
```


## Prerequisites
All scripts assume using:
```
Ubuntu 20.04+
conda
```

## Contents
### Data Generation
In the `data_generation` directory you can find code written to perform ADS evaluations in Simulation Environments.

#### Carla
The `carla/scripts/REPLICATE.sh` allows to evaluate TransFuser++ in CARLA leaderboard scenarios, using our custom package called 'multifidelity-tools'.
Note that evaluation for this paper was perform in the default fidelity settings i.e., EPIC rendering quality in 20FPS.

Steps replicate the data generation
```bash
cd ./data_generation/carla
chmod +x ./scripts/*

# Download CARLA
./scripts/setup_carla.sh 

# Download TF++
./scripts/setup_garage.sh

conda activate garage
./scripts/REPLICATE.sh

```


#### MetaDrive
The directory contains custom code to evaluate `PPO expert policy` in MetaDrive on 200 procedurally generated scenarios.

```bash
cd ./data_generation/metadrive
chmod +x ./REPLICATE.sh

# installs MetaDrive and runs the evaluation
./REPLICATE.sh
```
### Results

This directory contains the data as well as notebooks to generate figures used in the paper for both case studies.

#### Carla

For Carla case study we collected, scenario definitions (in CARLA leaderboard format), scenario replays as well as evaluation results as given by CARLA Leaderboard.

Unfortunately due to large size we couldn't include scenario replays binary files in this directory.

In the 'notebooks' directory you can find scripts to load the evaluation data and generate figures used in the paper.

#### MetaDrive

The data for MetaDrive contains simuation traces, i.e., state of the ADS under test at every timestep.

In the 'notebooks' you can find custom scripts to read and parse the data to evaluate, execution data and generate figures used in the paper.