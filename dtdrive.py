import os
from pathlib import Path
import argparse
import sys

# Adds relevant directories to the path so python can find scenario runner etc.
def update_path():
    print("Updating path...")
    paths = {}
    paths['WORK_DIR'] = str(Path().resolve())
    paths['REPO_ROOT'] = str(Path(__file__).parent.resolve())
    paths['CARLA_ROOT'] = paths['REPO_ROOT'] + '/data_generation/carla'

    sys.path.append(paths['CARLA_ROOT'])
    sys.path.append(paths['CARLA_ROOT'] + '/carla/PythonAPI')
    sys.path.append(paths['CARLA_ROOT'] + '/carla/PythonAPI/carla')
    sys.path.append(paths['CARLA_ROOT'] + '/carla/PythonAPI/carla/dist/carla-0.9.10-py3.7-linux-x86_64.egg')
    os.environ['SCENARIO_RUNNER_ROOT'] = paths['CARLA_ROOT'] + '/scenario_runner'
    os.environ['LEADERBOARD_ROOT'] = paths['CARLA_ROOT'] + '/leaderboard'
    sys.path.append(paths['CARLA_ROOT'] + "/PythonAPI/carla/")
    sys.path.append(os.environ['SCENARIO_RUNNER_ROOT'])
    sys.path.append(os.environ['LEADERBOARD_ROOT'])

update_path()

# Imports
from data_generation.carla.cawsr.json_to_xml_files import XMLToFiles
from data_generation.carla.leaderboard.leaderboard.utils.statistics_manager import StatisticsManager
from data_generation.carla.multifidelity_tools.dtdrive_runner import ReplayADSRunner
import carla
import scenario_runner

# Ensures input and output folders exist
def check_and_create_io_folders(args):
    Path("./input").mkdir(parents=True, exist_ok=True)
    Path("./output").mkdir(parents=True, exist_ok=True)
    
# Specifies and parses command line arguments
def parse_input():
    parser = argparse.ArgumentParser(
                    prog='DET-DRIVE',
                    description='Deterministic replay of ADS in CARLA',
                    epilog='TODO: complete epilog text')
    parser.add_argument('-s', '--scenario', default="sample_scenario.json")
    parser.add_argument('-r', '--route', default="")
    parser.add_argument('-a', '--ads', default="transfuser++")
    parser.add_argument('-i', '--input_directory', default="input")
    parser.add_argument('-o', '--output_directory', default="output")
    
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
    os.environ['PYTHONPATH'] += os.pathsep + paths['CARLA_ROOT'] + '/PythonAPI'
    os.environ['PYTHONPATH'] += os.pathsep + paths['CARLA_ROOT'] + '/PythonAPI/carla'
    os.environ['PYTHONPATH'] += os.pathsep + paths['CARLA_ROOT'] + '/PythonAPI/carla/dist/carla-0.9.10-py3.7-linux-x86_64.egg'
    os.environ['SCENARIO_RUNNER_ROOT'] = paths['CARLA_ROOT'] + '/scenario_runner'
    os.environ['LEADERBOARD_ROOT'] = paths['CARLA_ROOT'] + '/leaderboard'
    os.environ['PYTHONPATH'] += os.pathsep + "${CARLA_ROOT}/PythonAPI/carla/" + os.pathsep + "${SCENARIO_RUNNER_ROOT}" + os.pathsep + "${LEADERBOARD_ROOT}"

    #experiment setup
    os.environ['RESUME'] = str(1)
    os.environ['REPETITIONS'] = str(1)
    
    # save paths
    os.environ['CHECKPOINT_ENDPOINT'] = paths['CARLA_ROOT'] + '/results/checkpoints'
    os.environ['RECORD_PATH'] = paths['CARLA_ROOT'] + '/results/record'
    os.environ['SAVE_PATH'] = paths['CARLA_ROOT'] + '/results/save'
    
    # ads 
    paths['CARLA_GARAGE'] = paths['REPO_ROOT'] + '/data_generation/carla/ads/carla_garage'

    os.environ['CARLA_GARAGE'] = paths['CARLA_GARAGE']
    os.environ['TEAM_AGENT'] = paths['CARLA_GARAGE'] + '/team_code/sensor_agent.py'
    os.environ['TEAM_CONFIG'] = paths['CARLA_GARAGE'] + '/pretrained_models/longest6/tfpp_all_0'
    os.environ['DATAGEN'] = str(0)
    os.environ['UNCERTAINTY_THRESHOLD'] = str(0.33)

    return paths
    
# If a JSON scenario is supplied, convert it to scenario runner compatible XML files
def convert_scenario_if_necessary(paths, args):
    scenario_file = paths['INPUT_DIR'] + '/' + args.scenario
    if ".json" in scenario_file:
           Path(paths['INPUT_DIR'] + '/temp').mkdir(parents=True, exist_ok=True)
           converter = XMLToFiles()
           converter.parse_scenario(scenario_file, paths['INPUT_DIR'] + "/temp")
           args.route = "temp/route.xml"
           args.scenario = "temp/scenario.xml"

# Runs a new scenario and records it
def run_scenario(paths, args):
    agent_path = os.environ["TEAM_AGENT"]
    agent_config = os.environ["TEAM_CONFIG"]

    # Configure the scenario
    sr_args = argparse.Namespace()
    sr_args.timeout = 20
    sr_args.host = "127.0.0.1"
    sr_args.port = 2000
    sr_args.agent = agent_path
    sr_args.debug = None
    sr_args.sync = True
    sr_args.openscenario = False
    sr_args.repetitions = 1
    sr_args.reloadWorld = True
    sr_args.record = True
    sr_args.trafficManagerPort = 8000
    sr_args.agentConfig = agent_config
    sr_args.waitForEgo = False
    sr_args.route = [str(paths['REPO_ROOT'] + '/' + paths['INPUT_DIR'] + '/' + args.route),
        str(paths['REPO_ROOT'] + '/' + paths['INPUT_DIR'] + '/' + args.scenario),
        0]
    sr_args.configFile = '' 

    # Run the scenario
    sr = scenario_runner.ScenarioRunner(sr_args)
    sr.run()
    
# Load and run a replay with a new instance of the ADS
def run_replay(paths, args):
    agent_path = os.environ["TEAM_AGENT"]
    agent_config = os.environ["TEAM_CONFIG"]

    statistics_manager = StatisticsManager()

    #dirs = prepare_run_dirs(rep)

    #initialize_checkpoint(dirs["checkpoint"])

    #os.environ["CHECKPOINT_ENDPOINT"] = dirs["checkpoint"]
        
    #root counter to compute evaluations
    route_counter = 0

    replay_file = str(paths['INPUT_DIR'] + '/' + args.scenario)
    
    runner = ReplayADSRunner(
        agent_path,
        agent_config,
        route_counter,
        replay_file,
        0,
        statistics_manager,
        paths['REPO_ROOT'],
        paths['INPUT_DIR'] + '/' + args.route,
        paths['INPUT_DIR'] + '/' + args.scenario
    )
    
    runner.setup_and_start_replay()
    runner.remove_non_replay_actors()
    runner.load_route()
    runner.load_agent()
    runner.attach_ads()
    runner.run()


def main():
    # Parse input parameters
    args = parse_input()

    # Check default input and output folders exist & create if not
    check_and_create_io_folders(args)

    # Register environment variables
    paths = register_environment_variables(args)

    # Convert json scenario file to XML if necessary
    convert_scenario_if_necessary(paths, args)

    # Run scenario
    if ".log" in args.scenario:
        run_replay(paths, args)
    else:
        run_scenario(paths, args)

    print("DT-Drive successfully finished")
    
if __name__ == '__main__':
    main()