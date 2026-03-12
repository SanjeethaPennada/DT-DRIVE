
import time
from lib.carla_wrapper import CarlaWrapper
from lib.carla_wrapper import CARLA_DIR
import sys
import glob
import os
from pathlib import Path

try:
    sys.path.append(
        f'{CARLA_DIR}/PythonAPI/carla/dist/carla-0.9.10-py3.7-linux-x86_64.egg')
    import carla

except Exception as e:
    print(e)


def get_ego_id(client, file: str):
    file_info = (client.show_recorder_file_info(file, False)).split('\n')
    for i, l in enumerate(file_info):
        if 'vehicle.lincoln.mkz2017' in l:
            print(file_info[i:i+10])
            id = l.split(" ")[2].strip(":")
            return int(id)


def get_file(fps: int, scenario: int, rep: int):
    RECORD_DIR = Path(
        f'../carla-multifidelity_tools/results/rep{rep}/record/')

    file = RECORD_DIR / f'fps_{fps}_highquality_True' / \
        f'RouteScenario_{scenario}_rep0.log'
    if file.exists():
        return str(file.absolute())

    return None


if __name__ == "__main__":

    client = carla.Client("127.0.0.1", 2000)
    f = get_file(fps=20, scenario=6, rep=2)
    print(f)
    id = get_ego_id(client, f)
    print(id)
    client.reload_world()

    client.set_replayer_time_factor(3)
    print(client.replay_file(f, 0.0, 0.0, id))
