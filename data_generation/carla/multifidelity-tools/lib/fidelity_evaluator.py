
import traceback
from pprint import pprint
import argparse
from argparse import RawTextHelpFormatter
from leaderboard.leaderboard_evaluator import LeaderboardEvaluator
from leaderboard.utils.statistics_manager import StatisticsManager
import os
from types import SimpleNamespace

class FidelityEvaluator(LeaderboardEvaluator):

    def __init__(self, fps, high_quality):
        
        print(f"Initializing Fidelity Evaluator with:\n\n")

        # default config
        config = SimpleNamespace(
            **{ 'agent': os.getenv("TEAM_AGENT"),
            'agent_config': os.getenv("TEAM_CONFIG"),
            'checkpoint': os.getenv("CHECKPOINT_ENDPOINT"),
            'record': os.getenv("RECORD_PATH"),
            'routes': os.getenv("ROUTES"),
            'routes_subset': os.getenv("ROUTES_SUBSET"), #give scenario ID here 
            'scenarios': os.getenv("SCENARIOS"),
            'resume': bool(os.getenv("RESUME")),
            'repetitions': int(os.getenv("REPETITIONS", default=1)),
            'debug': 0,
            'host': 'localhost',
            'timeout': '600',
            'track': 'SENSORS',
            'trafficManagerPort': '8000',
            'trafficManagerSeed': '0'}
        )

        config.fps = fps
        self.frame_rate = config.fps

        config.port = 2000 if high_quality else 2010

        os.makedirs(config.checkpoint, exist_ok=True)
        config.checkpoint = f"{config.checkpoint}/fps_{fps}_highquality_{high_quality}.json"
        
        config.record = f"{config.record}/fps_{fps}_highquality_{high_quality}"
        os.makedirs(config.record, exist_ok=True)
        
        self.config = config
        print("Initialising fidelity evaluator with: ")
        pprint(vars(config))
        statistics_manager = StatisticsManager()
        super().__init__(config, statistics_manager)

        
    def run(self):
        super().run(self.config)

def parse_arguments():
    description = "CARLA AD Leaderboard Evaluation: evaluate your Agent in CARLA scenarios\n"

    # general parameters
    parser = argparse.ArgumentParser(description=description, formatter_class=RawTextHelpFormatter)
    parser.add_argument('--host', default='localhost',
                        help='IP of the host server (default: localhost)')
    parser.add_argument('--port', default='2000', help='TCP port to listen to (default: 2000)')
    parser.add_argument('--trafficManagerPort', default='8000',
                        help='Port to use for the TrafficManager (default: 8000)')
    parser.add_argument('--trafficManagerSeed', default='0',
                        help='Seed used by the TrafficManager (default: 0)')
    parser.add_argument('--debug', type=int, help='Run with debug output', default=0)
    parser.add_argument('--record', type=str, default='',
                        help='Use CARLA recording feature to create a recording of the scenario')
    parser.add_argument('--timeout', default="60.0",
                        help='Set the CARLA client timeout value in seconds')

    # simulation setup
    parser.add_argument('--routes',
                        help='Name of the route to be executed. Point to the route_xml_file to be executed.',
                        required=True)
    parser.add_argument('--scenarios',
                        help='Name of the scenario annotation file to be mixed with the route.',
                        required=True)
    parser.add_argument('--repetitions',
                        type=int,
                        default=1,
                        help='Number of repetitions per route.')
    parser.add_argument('--routes-subset',
                        default='',
                        type=str,
                        help='Execute a specific set of routes')

    # agent-related options
    parser.add_argument("-a", "--agent", type=str, help="Path to Agent's py file to evaluate", required=True)
    parser.add_argument("--agent-config", type=str, help="Path to Agent's configuration file", default="")

    parser.add_argument("--track", type=str, default='SENSORS', help="Participation track: SENSORS, MAP")
    parser.add_argument('--resume', type=bool, default=False, help='Resume execution from last checkpoint?')
    parser.add_argument("--checkpoint", type=str,
                        default='./simulation_results.json',
                        help="Path to checkpoint used for saving statistics and resuming")
    
    ## added FPS support
    parser.add_argument("--fps", type=int, default=20, help="Frames per second")
    args = parser.parse_args()
    
    return args


def main():

    arguments = parse_arguments()
    try:
        fidelity_evaluator = FidelityEvaluator(arguments)
        fidelity_evaluator.run(arguments)

    except Exception as e:
        traceback.print_exc()
    finally:
        del fidelity_evaluator


if __name__ == "__main__":
    print("Welcome fidelity evaluator")
    main()
