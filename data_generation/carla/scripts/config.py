import glob
import os
import sys
import time
import json
import carla

try:
    sys.path.append(glob.glob('../carla/dist/carla-*%d.%d-%s.egg' % (
        sys.version_info.major,
        sys.version_info.minor,
        'win-amd64' if os.name == 'nt' else 'linux-x86_64'))[0])
except IndexError:
    pass

# Initialize CARLA client and world
client = carla.Client('localhost', 2000)
client.set_timeout(10.0)
world = client.get_world()

def read_config(json_file):
    try:
        with open(json_file, 'r') as f:
            data = json.load(f)

        return {
          
            "streetlight_ids": data.get("street_light_ids", []),
            "remove_all_street_lights": data.get("remove_all_street_lights", False)
        }

    except Exception as e:
        print(f"Error reading JSON file: {e}")
        return {}

# Function to retrieve all street lights in the world
def get_street_lights(world):
    """Retrieves all street lights in the CARLA world."""
    lmanager = world.get_lightmanager()
    all_lights = lmanager.get_all_lights()
    street_lights = [light for light in all_lights if light.light_group == carla.LightGroup.Street]
    return street_lights

# Function to turn off street lights by their IDs
def turn_off_lights_by_ids(lights, streetlight_ids):
    """Turns off the street lights by their IDs."""
    for light in lights:
        if light.id in streetlight_ids:
            light.turn_off()
            print(f"Street light with ID {light.id} has been turned off.")


def apply_weather(world, weather_cfg):
    weather = carla.WeatherParameters(
        cloudiness=weather_cfg.get("cloudiness", 40.0),
        precipitation=weather_cfg.get("precipitation", 30.0),
        precipitation_deposits=weather_cfg.get("precipitation_deposits", 0.0),
        wind_intensity=weather_cfg.get("wind_intensity", 0.0),
        sun_azimuth_angle=weather_cfg.get("sun_azimuth_angle", 90.0),
        sun_altitude_angle=weather_cfg.get("sun_altitude_angle", -90.0),
        fog_density=weather_cfg.get("fog_density", 0.0),
        wetness=weather_cfg.get("wetness", 0.0)
    )
    world.set_weather(weather)
    print("Weather applied:", weather_cfg)

# Function to configure the environment

def configure_environment(world, config):

    streetlight_ids = config.get("streetlight_ids", [])
    weather_cfg = config.get("weather", {
    "cloudiness": 40.0,
    "precipitation": 30.0,
    "precipitation_deposits": 0.0,
    "wind_intensity": 0.0,
    "sun_azimuth_angle": 90.0,
    "sun_altitude_angle": -90.0,
    "fog_density": 0.0,
    "wetness": 0.0
})

    # -------- Street lights --------
    lmanager = world.get_lightmanager()

    if config.get("remove_all_street_lights", False):
        print("[CONFIG] Turning OFF all street lights")
        lights = lmanager.get_all_lights()
        lmanager.turn_off(lights)

    elif streetlight_ids:
        print("[CONFIG] Turning OFF selected street lights")
        lights = lmanager.get_all_lights()
        selected = [l for l in lights if l.id in streetlight_ids]
        lmanager.turn_off(selected)

    # -------- Weather --------
    if weather_cfg:
        apply_weather(world, weather_cfg)

    world.tick()




