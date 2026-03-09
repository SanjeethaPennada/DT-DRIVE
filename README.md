# DET-DRIVE: A Tool for Deterministic Replay-Based Evaluation of Autonomous Driving Systems 
# (or)
# DET-Drive: A Deterministic Replay Framework for Evaluating Autonomous Driving Systems in CARLA

(Submitted to ICST 2026 (under review))

DET-DRIVE is a framework for evaluating Autonomous Driving Systems (ADS) in a fully deterministic simulation environment. The framework enables replay-based evaluation by replacing the ego vehicle in recorded CARLA simulations with an autonomous driving agent(s). 
This repository contains scripts and tools to:
• generate replay logs of flaky scenarios in CARLA  
• evaluate ADS in deterministic replay environments using DET-DRIVE  
• reproduce the experimental results presented in the paper

## Directory structure overview:
```
DET-DRIVE/
├─ data_generation/
│  ├─ carla/
│  │  ├─ flaky_data_bucket/
│  │  │  ├─ record/          # Recorded CARLA Replay logs of flaky scenarios 
│  │  ├─ scripts/
│  │  │  ├─ REPLICATE.sh/    # Generates replay logs of flaky scenarios
│  │  │  ├─ DETDRIVE.sh/     # Run deterministic evaluation
├─ results/
│  ├─ carla/
│  │  ├─ data/
│  │  ├─ notebooks/
│  │  │  ├─ flakiness.py/    # Flakiness analysis
│  │  │  ├─ determinism.py/  # Deterministic evaluation analysis
```

## Prerequisites
All scripts assume using:
```
Ubuntu 20.04+
CARLA 0.9.10.1
conda
```
Install the required packages using:
```
pip install -r requirements.txt
```
# Contents

## 1. Recording Replay Logs for Flaky Scenarios
The `data_generation` directory contains scripts used to generate replay logs for 43 flaky CARLA leaderboard scenarios.

## 2. CARLA
The script: 'REPLICATE.sh' runs **TransFuser++** on CARLA Leaderboard routes and records simulation logs for flaky scenarios. These logs are later used to evaluate ADS under deterministic replay conditions.
For the experiments reported in the paper, CARLA was run using: 20 FPS simulation rate. 

## 3. Deterministic Evaluation with DET-DRIVE
The script: 'DETDRIVE.sh' runs DET-DRIVE to evaluate TransFuser++ in a fully deterministic replay environment using the previously recorded scenarios.
During evaluation:
1. A CARLA replay log is loaded.
2. The original ego vehicle is removed.
3. The ADS under test is attached as the new ego agent.
4. The agent drives in the replayed environment under deterministic simulation settings.
This enables consistent and reproducible evaluation across multiple runs.
The following pipeline illustrates how DET-DRIVE evaluates an autonomous driving system in a deterministic replay environment.

```
  Recorded Replay Logs
         │
         ▼
┌─────────────────────────┐
│   REMO Replay Loader    │
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│    REMO Ego Removal     │
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│ Route & Scenario Loader │
│   (CARLA Leaderboard)   │
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│   Attach ADS Agent      │
│   (Agent Under Test)    │
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│ Deterministic Execution │
│    (Sync Simulation)    │
└───────────┬─────────────┘
            ▼
┌─────────────────────────┐
│   Evaluation Metrics    │
│  (Statistics Manager)   │
└─────────────────────────┘
```
### Experimental pipeline

```bash
cd ./data_generation/carla
chmod +x ./scripts/*

# Download CARLA
./scripts/setup_carla.sh

# Download TransFuser++
./scripts/setup_garage.sh

# Activate environment
conda activate garage

# Generate flaky scenarios
./scripts/REPLICATE.sh

# Run DET-DRIVE deterministic evaluation
./scripts/DETDRIVE.sh
```
## 4. Results
The 'notebooks' directory has the scripts to load the evaluation data and generate figures used in the paper. This directory contains the data as well as notebooks to generate figures used in the paper.

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





