# DT-DRIVE: A Tool for Deterministic Replay-Based Testing of Autonomous Driving Systems 

(Submitted to ASE 2026 (under review))

DT-DRIVE is a framework for testing multiple Autonomous Driving Systems (ADS) in a fully deterministic simulation environment. The framework enables replay-based testing by replacing the ego vehicle in recorded CARLA simulations with an autonomous driving agent(s). This repository contains scripts and tools to test multiple ADS in deterministic replay environment using scenario description or recorded binary files in CARLA simulator. We have validated 132 scenarios using TransFuser++ successfully. We have also tested the tool by running 2 ADSs in same and modified deterministic CARLA world.  

## Directory structure overview:
```
DT-DRIVE/
├─ data_generation/
│  ├─ carla/
│  │  ├─ recordings/
│  │  │  ├─ record/          # Recorded CARLA Replay logs of all 132 scenarios 
│  │  ├─ scripts/
│  │  │  ├─ RECORD.sh/       # Generates replay logs when input is json file
│  │  │  ├─ DTDRIVE.sh/      # Run DET DRIVE when input is a log file
│  │  │  ├─ start_dtdrive_experiment.sh/      # Switch ADS
│  │  │  ├─ ids.py/          # Extracts the IDs of all streetlights that fall within a specified radius of the ego vehicle at any time during the entire scenario (from start to end).
│  │  │  ├─ config.py/       # Configuration file that applies weather/time modifications and uses a .json file to specify entities to be removed.
├─ results/
│  ├─ carla/
│  │  ├─ data/
│  │  ├─ notebooks/
│  │  │  ├─ flakiness.py/    # Flakiness analysis of recorded logs after running RECORD.sh
│  │  │  ├─ determinism.py/  # Deterministic evaluation analysis after running DTDRIVE.sh
```

## Prerequisites

### Hardware
- GPU: NVIDIA Corporation
- Memory: 16GB+
- Storage: 100GB+

### Software
- Ubuntu 20.04
- nvidia driver
- CARLA 0.9.10.1
  
![alt text](https://github.com/SanjeethaPennada/DT-DRIVE/blob/main/dtdrive.jpg)

# DT-DRIVE TOOL 
The `data_generation` directory contains scripts used to generate replay logs for 132 CARLA leaderboard scenarios. The script: `RECORD.sh` runs TransFuser++ on CARLA Leaderboard routes using scenario description files (.json) and records simulation logs (.log) of all the scenarios. These logs are later used to evaluate ADS under deterministic replay conditions. For the experiments reported in the paper, CARLA was run using: 20 FPS simulation rate. The script: `DTDRIVE.sh` runs DT-DRIVE to evaluate TransFuser++ in a fully deterministic replay environment using the previously recorded scenarios. We have also tested DT-DRIVE using two ADSs: TransFuser++ and TransFuser  during the evaluation. The script `start_dtdrive_experiment.sh` is used to switch between these two ADSs during the experiments. The script `ids.py` is used to extract all the street light entities surrounding the ego vehicle within user-specified radius into a .json file, and the script `config.py` is the modification file that lists the entities that needs to be toggled and the weather conditions that needs to be applied in order to run the scenario deterministically in modifed world. The script `ids.py` extracts all streetlight entities surrounding the ego vehicle within a user-specified radius and saves them to a .json file. The script `config.py` serves as a configuration module that contains the entities to be toggled and defines the weather/time conditions required to run the scenario deterministically in a modified world.

### Experimental pipeline

```bash
cd ./data_generation/carla
chmod +x ./scripts/*

# Download CARLA
./scripts/setup_carla.sh

# Download ADS: TransFuser Plus Plus
./scripts/setup_transfuser_plus_plus.sh

# Activate TransFuser Plus Plus environment
conda activate garage

# Download ADS: TransFuser
./scripts/setup_transfuser.sh

# Activate TransFuser environment
conda activate tfuse

# DT-Drive Record
./scripts/RECORD.sh 

# DT-Drive Deterministic Replay
./scripts/DTDRIVE.sh

# DT-Drive Deterministic Replay + Modify
./scripts/DTDRIVE.sh --modify --config-file ./scripts/config.json 
```

## Results
The `results/notebooks` directory has the scripts to load the evaluation data and generate figures used in the paper.
To inspect determinism of scenario evaluations run `determinism.py` and provide path to scenario evaluation points do directory with evaluation results for example:
```bash
# Make sure that plotting and export to Excel libraries are installed
pip install seaborn openpyxl
python ./notebooks/determinism.py ./data/evaluation/dt_drive_TransFuser++/Route_Scenario_36 #TransFuser++ Scenario 36 result in same deterministic world
python ./notebooks/determinism.py ./data/evaluation/dt_drive_TransFuser/Route_Scenario_36 #TransFuser Scenario 36 result in same deterministic world
python ./notebooks/determinism.py ./data/evaluation/dt_drive_TransFuser++_modify/Route_Scenario_36 #TransFuser++ Scenario 36 result in modified  deterministic world
python ./notebooks/determinism.py ./data/evaluation/dt_drive_TransFuser_modify/Route_Scenario_36 #TransFuser Scenario 36 result in modified  deterministic world
```

## Funding
This research was funded by the Engineering and Physical Sciences Research Council (EPSRC) through UK Research and Innovation (Project Reference: EP/Y014219/1)

## Acknowledgements
This implementation is based on code from several repositories. We sincerely thank the authors for their awesome work.
- [Record and Replay with Modifications version 0.1 (REMO_v0.1) TOOL](https://github.com/SanjeethaPennada/REMO-v0.1)
- [Record and Replay with Modifications version 1.0 (REMO_v1.0) TOOL](https://github.com/RSE-Sheffield/REMO)
- [Flakiness Study](https://figshare.com/s/36510668ad05ffa8c0bd?file=50369490)
- [CARLA Garage](https://github.com/autonomousvision/carla_garage)
- [Transfuser](https://github.com/autonomousvision/transfuser)
- [CARLA Leaderboard](https://github.com/carla-simulator/leaderboard)
- [Scenario Runner](https://github.com/carla-simulator/scenario_runner)

























