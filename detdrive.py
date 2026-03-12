import os
from pathlib import Path
import argparse

from data_generation.carla.cawsr.json_to_xml_files import XMLToFiles


def check_and_create_io_folders(args):
    Path("./input").mkdir(parents=True, exist_ok=True)
    Path("./output").mkdir(parents=True, exist_ok=True)
    
def parse_input():
    parser = argparse.ArgumentParser(
                    prog='DET-DRIVE',
                    description='Deterministic replay of ADS in CARLA',
                    epilog='TODO: complete epilog text')
    parser.add_argument('-s', '--scenario', default="sample_scenario.json")
    parser.add_argument('-r', '--route')
    parser.add_argument('-a', '--ads', default="transfuser++")
    parser.add_argument('-i', '--input_directory', default="./input")
    parser.add_argument('-o', '--output_directory', default="./output")
    
    args = parser.parse_args()
    return args


def register_environment_variables(args):
    paths = {}
    paths['INPUT_DIR'] = args.input_directory
    paths['OUTPUT_DIR'] = args.output_directory
    paths['WORK_DIR'] = str(Path().resolve())
    paths['REPO_ROOT'] = str(Path(__file__).parent.resolve())
    paths['CARLA_ROOT'] = paths['REPO_ROOT'] + '/data_generation/carla'
    paths['CARLA_SERVER'] = paths['CARLA_ROOT'] + '/CarlaUE4.sh'
    

    os.environ['WORK_DIR'] = paths['WORK_DIR']
    os.environ['CARLA_ROOT'] = paths['CARLA_ROOT']
    os.environ['CARLA_SERVER'] = paths['CARLA_SERVER']
    #os.environ['PYTHONPATH'] = $PYTHONPATH:${CARLA_ROOT}/PythonAPI
    #os.environ['PYTHONPATH'] = $PYTHONPATH:${CARLA_ROOT}/PythonAPI/carla
    #os.environ['PYTHONPATH'] = $PYTHONPATH:$CARLA_ROOT/PythonAPI/carla/dist/carla-0.9.10-py3.7-linux-x86_64.egg
    #os.environ['SCENARIO_RUNNER_ROOT'] = ${WORK_DIR}/scenario_runner
    #os.environ['LEADERBOARD_ROOT'] = ${WORK_DIR}/leaderboard
    #os.environ['PYTHONPATH'] = "${CARLA_ROOT}/PythonAPI/carla/":"${SCENARIO_RUNNER_ROOT}":"${LEADERBOARD_ROOT}":${PYTHONPATH}
    
    #experiment setup
    
    # scenario definition
    #export SCENARIOS=${WORK_DIR}/scenario_runner/srunner/data/all_towns_traffic_scenarios.json
    #export ROUTES=${WORK_DIR}/data/routes/routes_devtest_sliced.xml
        #export ROUTES=${WORK_DIR}/data/routes/minimal.xml
        # export ROUTES=${WORK_DIR}/data/routes/slice_show.xml
    os.environ['RESUME'] = str(1)
    os.environ['REPETITIONS'] = str(1)
    
    # save paths
    #os.environ['CHECKPOINT_ENDPOINT'] = ${WORK_DIR}/results/checkpoints
    #os.environ['RECORD_PATH'] = ${WORK_DIR}/results/record
    #os.environ['SAVE_PATH'] = ${WORK_DIR}/results/save
    
    # ads 
    paths['CARLA_GARAGE'] = paths['REPO_ROOT'] + 'data_generation/carla/ads/carla_garage'

    os.environ['CARLA_GARAGE'] = paths['CARLA_GARAGE']
    os.environ['TEAM_AGENT'] = paths['CARLA_GARAGE'] + '/team_code/sensor_agent.py'
    os.environ['TEAM_CONFIG'] = paths['CARLA_GARAGE'] + '/pretrained_models/longest6/tfpp_all_0'
    os.environ['DATAGEN'] = str(0)
    os.environ['UNCERTAINTY_THRESHOLD'] = str(0.33)

    return paths
    
def convert_scenario_if_necessary(paths, args):
    scenario_file = paths['INPUT_DIR'] + '/' + args.scenario
    if ".json" in scenario_file:
           Path(paths['INPUT_DIR'] + '/temp').mkdir(parents=True, exist_ok=True)
           converter = XMLToFiles()
           converter.parse_scenario(scenario_file, paths['INPUT_DIR'] + "/temp")
           args.route = "temp/route.xml"
           args.scenario = "temp/scenario.xml"

def main():
    # Parse input parameters
    args = parse_input()

    # Check default input and output folders exist & create if not
    check_and_create_io_folders(args)

    # Register environment variables
    paths = register_environment_variables(args)

    # Convert json scenario file to XML if necessary
    convert_scenario_if_necessary(paths, args)


    # Run dtdrive_runner.py
    #python3 ${WORK_DIR}/multifidelity-tools/dtdrive_runner.py $@

    print("DT-Drive successfully finished")
    
if __name__ == '__main__':
    main()