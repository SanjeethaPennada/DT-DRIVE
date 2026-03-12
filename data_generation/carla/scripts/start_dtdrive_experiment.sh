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

# ads (TF)
export TF_DIR=${WORK_DIR}/ads/transfuser
export TEAM_AGENT=${TF_DIR}/team_code_transfuser/submission_agent.py
export TEAM_CONFIG=${TF_DIR}/model_ckpt/models_2022/transfuser

# ads (TF++)
# export TFPP_DIR=${WORK_DIR}/ads/transfuser_plus_plus
# export TEAM_AGENT=${TFPP_DIR}/team_code/sensor_agent.py
# export TEAM_CONFIG=${TFPP_DIR}/pretrained_models/longest6/tfpp_all_0
# export UNCERTAINTY_THRESHOLD=0.33

export DATAGEN=0



python3 ${WORK_DIR}/multifidelity_tools/dtdrive_runner.py $@
echo "DT-Drive successfully finished"
