#!/usr/bin/env bash

export WORK_DIR=$(pwd)
export CARLA_ROOT=${WORK_DIR}/carla

export CARLA_SERVER=${CARLA_ROOT}/CarlaUE4.sh
export PYTHONPATH=$PYTHONPATH:${CARLA_ROOT}/PythonAPI
export PYTHONPATH=$PYTHONPATH:${CARLA_ROOT}/PythonAPI/carla
export PYTHONPATH=$PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/dist/carla-0.9.10-py3.7-linux-x86_64.egg
export SCENARIO_RUNNER_ROOT=${WORK_DIR}/scenario_runner
export LEADERBOARD_ROOT=${WORK_DIR}/leaderboard
export PYTHONPATH="${CARLA_ROOT}/PythonAPI/carla/":"${SCENARIO_RUNNER_ROOT}":"${LEADERBOARD_ROOT}":${PYTHONPATH}

#experiment setup

# scenario definition
export SCENARIOS=${WORK_DIR}/scenario_runner/srunner/data/all_towns_traffic_scenarios.json
export ROUTES=${WORK_DIR}/data/routes/routes_devtest_sliced.xml
#export ROUTES=${WORK_DIR}/data/routes/minimal.xml
# export ROUTES=${WORK_DIR}/data/routes/slice_show.xml
export RESUME=1
export REPETITIONS=1

# save paths
export CHECKPOINT_ENDPOINT=${WORK_DIR}/results/checkpoints
export RECORD_PATH=${WORK_DIR}/results/record
export SAVE_PATH=${WORK_DIR}/results/save

# ads 
export CARLA_GARAGE=${WORK_DIR}/ads/carla_garage
export TEAM_AGENT=${CARLA_GARAGE}/team_code/sensor_agent.py
export TEAM_CONFIG=${CARLA_GARAGE}/pretrained_models/longest6/tfpp_all_0
export DATAGEN=0
export UNCERTAINTY_THRESHOLD=0.33


python3 ${WORK_DIR}/multifidelity-tools/dtdrive_runner.py $@
echo "DET-Drive successfully finished"
