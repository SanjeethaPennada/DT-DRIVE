#DT-DRIVE application

import carla
import importlib
import os
import sys
import time
import json
import subprocess
import signal
from pathlib import Path
import xml.etree.ElementTree as ET
from srunner.tools.route_manipulation import interpolate_trajectory
from leaderboard.scenarios.scenario_manager import ScenarioManager
from leaderboard.scenarios.route_scenario import RouteScenario
from leaderboard.utils.statistics_manager import StatisticsManager
from leaderboard.utils.route_indexer import RouteIndexer
from leaderboard.autoagents.agent_wrapper import AgentWrapper
from srunner.scenariomanager.carla_data_provider import CarlaDataProvider
from leaderboard.envs.sensor_interface import SensorInterface


# ---------------------------------------------------
# Paths
# ---------------------------------------------------

BASE_DIR = Path(__file__).resolve().parents[1]
ROUTE_FILE = str(BASE_DIR / "data/routes/routes_devtest_sliced.xml")
SCENARIO_FILE = str(BASE_DIR / "scenario_runner/srunner/data/all_towns_traffic_scenarios.json")
rep = int(os.environ.get("REP", 0))
REPLAY_DIR = str(BASE_DIR / "recordings/rep1/record/fps_20_highquality_True")

#FPS 
FPS = 20

# ---------------------------------------------------
# Mapping replay and subset
# ---------------------------------------------------


REPLAY_ROUTE_MAP = {
"RouteScenario_36_rep0.log": "36"  #Example Scenario
}

# ---------------------------------------------------
# Route Parsing
# Loading Town
# ---------------------------------------------------

def get_town_for_route(route_file, route_id):

    tree = ET.parse(route_file)
    root = tree.getroot()

    for route in root.iter("route"):

        if route.attrib["id"] == str(route_id):
            return route.attrib["town"]

    raise RuntimeError(f"Route {route_id} not found in {route_file}")

# ---------------------------------------------------
# checkpoint initialization
# ---------------------------------------------------

def initialize_checkpoint(path):

    data = None

    if os.path.exists(path):
        try:
            with open(path, "r") as f:
                data = json.load(f)
        except:
            data = None

    if not data or "_checkpoint" not in data:
        data = {
            "_checkpoint": {
                "global_record": {},
                "progress": [0, 1],
                "records": []
            }
        }

    # required fields
    cp = data["_checkpoint"]

    if "progress" not in cp or len(cp["progress"]) < 2:
        cp["progress"] = [0, 1]

    if "records" not in cp:
        cp["records"] = []

    if "global_record" not in cp:
        cp["global_record"] = {}

    with open(path, "w") as f:
        json.dump(data, f, indent=4)

# ---------------------------------------------------
# runner
# ---------------------------------------------------

class ReplayADSRunner:

    def __init__(self, agent_path, agent_config, route_index, replay_file, subset, statistics_manager):

        self.route_index = route_index
        self.agent_path = agent_path
        self.agent_config = agent_config
        self.replay_file = replay_file
        self.subset = subset
        self.statistics_manager = statistics_manager
        self.sensor_interface = SensorInterface()
        self.replay_actor_ids = set()


# ---------------------------------------------------
# Setup and start running replay log (REMO tool)
# ---------------------------------------------------

    def setup_and_start_replay(self):

        print("Connecting to CARLA")

        self.client = carla.Client("localhost", 2000)
        self.client.set_timeout(20)

        # -------- determine town from route file --------
        town = get_town_for_route(ROUTE_FILE, self.subset)

        print("Loading town:", town)

        self.world = self.client.load_world(town)
                             
                             
        

        for _ in range(10):
            self.world.tick()

        CarlaDataProvider.set_client(self.client)
        CarlaDataProvider.set_world(self.world)

        #deterministic settings
        settings = self.world.get_settings()
        settings.synchronous_mode = True
        settings.fixed_delta_seconds = 1.0 / FPS
        self.world.apply_settings(settings)

        print("Starting replay:", self.replay_file)

        self.client.set_replayer_ignore_hero(True)
        
        self.client.replay_file(self.replay_file, 0, 0, 0)
        
        for _ in range(1):
            self.world.tick()
            
        
            

        print("[experiment_runner] Replay actors spawned")
        # store replay actor ids
        self.replay_actor_ids = set(a.id for a in self.world.get_actors())
        print("Replay actors captured:", len(self.replay_actor_ids))

        ego_transform = None

        for actor in self.world.get_actors().filter("vehicle.*"):

            if actor.attributes.get("role_name") == "hero":

                ego_transform = actor.get_transform()

                print("Removing replay ego:", ego_transform.location)

                actor.set_location(carla.Location(10000, 10000, 10000))
                self.world.tick()

                actor.destroy()
                self.world.tick()

                break

        if ego_transform is None:
            print("[experiment_runner] WARNING: no hero vehicle found in replay.")



    # --------------------------------------------------
    # load route via RouteIndexer 
    # --------------------------------------------------

    def load_route(self):

        print("Loading route subset:", self.subset)

        route_indexer = RouteIndexer(
            ROUTE_FILE,
            SCENARIO_FILE,
            1,
            self.subset
        )

        config = route_indexer.next()

        self.route_config = config

        gps_route, world_route = interpolate_trajectory(
            self.world,
            config.trajectory
        )

        self.global_plan = gps_route
        self.global_plan_world = world_route

        print("Route loaded:", config.name)


    # --------------------------------------------------
    # load agent
    # --------------------------------------------------

    def load_agent(self):

        print("Loading ADS agent")

        module_name = os.path.basename(self.agent_path).split(".")[0]

        sys.path.insert(0, os.path.dirname(self.agent_path))

        module = importlib.import_module(module_name)

        entry_point = module.get_entry_point()

        agent_class = getattr(module, entry_point)

        self.agent = agent_class(self.agent_config)

        self.agent.setup(self.agent_config)

        self.agent.set_global_plan(
            self.global_plan,
            self.global_plan_world
        )

        self.route_config.agent = self.agent

        print("Agent loaded")


    # --------------------------------------------------------------
    # Remove actors spawned (not actors in replay and ego vehicle)
    # --------------------------------------------------------------

    def remove_non_replay_actors(self):

        print("Removing non-replay actors")

        for actor in self.world.get_actors():

            # keep replay actors
            if actor.id in self.replay_actor_ids:
                continue

            # keep ego vehicle
            role = actor.attributes.get("role_name")
            if role == "hero":
                continue

            # keep sensors
            if actor.type_id.startswith("sensor"):
                continue

            try:
               
                actor.destroy()
            except:
                pass

        self.world.tick()

    def remove_scenario_actors(self):

        print("Removing scenario actors only")

        scenario = self.manager.scenario

        if not hasattr(scenario, "other_actors"):
            print("No scenario actors")
            return

        actors_to_remove = list(scenario.other_actors)

        for actor in actors_to_remove:

            try:
                if actor and actor.is_alive:

                    print("Removing scenario actor:", actor.type_id, actor.id)

                    actor.set_location(carla.Location(10000,10000,10000))

                    actor.destroy()

                    self.world.tick()

            except Exception as e:
                print("Failed removing actor:", e)

        # clear scenario internal list
        scenario.other_actors = []

        # allow world to stabilize
        for _ in range(5):
            self.world.tick()

        print("Scenario actors removed")

    # --------------------------------------------------
    # attach ADS via ScenarioManager
    # --------------------------------------------------
    def attach_ads(self):

        print("Attaching ADS")

        CarlaDataProvider.set_client(self.client)
        CarlaDataProvider.set_world(self.world)

        self.route_config.index = self.route_index

        self.statistics_manager.set_route(
            self.route_config.name,
            self.route_index
        )

        self.statistics_manager._total_routes = len(REPLAY_ROUTE_MAP)

        self.route_config.scenario_file = str(
            BASE_DIR / "scenario_runner/srunner/data/no_scenarios.json"
        )

        scenario = RouteScenario(
            self.world,
            self.route_config,
            debug_mode=False
        )

        # create manager first
        self.manager = ScenarioManager(
            timeout=20,
            debug_mode=False
        )

        # load scenario
        self.manager.load_scenario(
            scenario,
            self.agent,
            0
        )

        # now scenario exists inside manager
        self.remove_scenario_actors()
        self.remove_non_replay_actors()
        time.sleep(5)
        for _ in range(10):
            self.world.tick()   

        # register scenario for statistics
        self.statistics_manager.set_scenario(self.manager.scenario)

    # --------------------------------------------------
    # run ego agent in replay or deterministic world
    # --------------------------------------------------

    def run(self):

        print("Running scenario")

        start_system = time.time()
        start_game = self.world.get_snapshot().timestamp.elapsed_seconds

        self.manager.run_scenario()

        end_system = time.time()
        end_game = self.world.get_snapshot().timestamp.elapsed_seconds

        duration_system = end_system - start_system
        duration_game = end_game - start_game

        route_record = self.statistics_manager.compute_route_statistics(
            self.route_config,
            duration_system,
            duration_game
        )

        StatisticsManager.save_record(
            route_record,
            self.route_config.index,
            os.environ["CHECKPOINT_ENDPOINT"]
        )

        global_record = self.statistics_manager.compute_global_statistics(len(REPLAY_ROUTE_MAP))

        StatisticsManager.save_global_record(
            global_record,
            self.agent.sensors(),
            1,
            os.environ["CHECKPOINT_ENDPOINT"]
        )

        print("Finished")


# ---------------------------------------------------
# Evaluation results - directory preparation
# ---------------------------------------------------

def prepare_run_dirs():

    root = Path("results")
    checkpoints = root / "checkpoints"

    checkpoints.mkdir(parents=True, exist_ok=True)

    checkpoint_file = checkpoints / f"fps_{FPS}_highquality_True.json"

    return {
        "root": root,
        "checkpoint": str(checkpoint_file)
    }


# ---------------------------------------------------
# main
# ---------------------------------------------------

def main():

    agent_path = os.environ["TEAM_AGENT"]
    agent_config = os.environ["TEAM_CONFIG"]

    statistics_manager = StatisticsManager()

    dirs = prepare_run_dirs()

    initialize_checkpoint(dirs["checkpoint"])

    os.environ["CHECKPOINT_ENDPOINT"] = dirs["checkpoint"]
        
    #root counter to compute evaluations
    route_counter = 0

    for replay_name, subset in REPLAY_ROUTE_MAP.items():

        replay_file = str(Path(REPLAY_DIR) / replay_name)

        print("\n=================================")
        print("Replay:", replay_file)
        print("Route subset:", subset)
        print("=================================\n")


        runner = ReplayADSRunner(
            agent_path,
            agent_config,
            route_counter,
            replay_file,
            subset,
            statistics_manager
        )
        
        runner.setup_and_start_replay()
        runner.remove_non_replay_actors()
        runner.load_route()
        runner.load_agent()
        runner.attach_ads()
        runner.run()

        # increment after each run
        route_counter += 1


if __name__ == "__main__":
    main()
