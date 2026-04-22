#!/usr/bin/env python
#This generates ids surrounding the ego vehicle within 50m radius. All the ids along with traffic light ids are saved in output.json file and their locations in location.json file.
#Even though this study did not use traffic light ids, but have included for future work. 

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


def get_objects_at_location(world, location, radius, label):
    """Retrieve objects of a given label within a specified radius of a location."""
    all_objects = world.get_environment_objects(label)
    return [obj.id for obj in all_objects if location.distance(obj.transform.location) <= radius]

def get_nearby_traffic_and_street_lights(world, location, radius):
    """Retrieve nearby traffic light and street light IDs and locations."""
    entity_ids = {"traffic_light_ids": set(), "street_light_ids": set()}
    entity_locations = {"traffic_lights": {}, "street_lights": {}}
    
    # Get all actors in the world
    actors = world.get_actors()

    # Get traffic light IDs and locations
    for actor in actors:
        if 'traffic_light' in actor.type_id:
            if location.distance(actor.get_transform().location) <= radius:
                entity_ids["traffic_light_ids"].add(actor.id)
                entity_locations["traffic_lights"][actor.id] = actor.get_transform().location
    
    # Get street light IDs and locations using Light Manager
    light_manager = world.get_lightmanager()
    all_lights = light_manager.get_all_lights()
    for light in all_lights:
        if location.distance(light.location) <= radius:
            entity_ids["street_light_ids"].add(light.id)
            entity_locations["street_lights"][light.id] = light.location
    
    return entity_ids, entity_locations


def monitor_vehicle_spawn_and_record_data(world, radius=20.0):
    """Monitor the world for ego vehicle spawn and record data for nearby buildings and traffic lights."""
    
    vehicle_found = False
    vehicles = {}

    # Continuously monitor the world for the ego vehicle
    while not vehicle_found:
        actors = world.get_actors()
        for actor in actors:
            if actor.attributes.get('role_name') == 'hero':
                print(f"Ego vehicle spawned, starting to track...")
                vehicle_found = True
                vehicles[actor.id] = actor  # Store reference to the vehicle
                break

    
    # Initialize sets for storing unique IDs and locations
   
    unique_traffic_light_ids = set()
    unique_street_light_ids = set()
    traffic_light_locations = {}
    street_light_locations = {}


    # Track the ego vehicle's movement and record data
    while True:
        for vehicle in vehicles.values():
            location = vehicle.get_location()
                
            # Retrieve nearby light IDs           
            light_ids, light_locations = get_nearby_traffic_and_street_lights(world, location, radius)
            
            # Add to unique sets           
            unique_traffic_light_ids.update(light_ids["traffic_light_ids"])
            unique_street_light_ids.update(light_ids["street_light_ids"])
            
            # Add locations to the dictionaries
            traffic_light_locations.update(light_locations["traffic_lights"])
            street_light_locations.update(light_locations["street_lights"])
         
            # Print data to verify
            print(f"Vehicle at {location},  Traffic Light IDs: {unique_traffic_light_ids}, Street Light IDs: {unique_street_light_ids}")
                
        # Store the collected data periodically
        final_results = {
           
            'street_light_ids': list(unique_street_light_ids)
        }

        # Save to config.json
        with open('config.json', 'w') as f:
            json.dump(final_results, f, indent=4)

def main():
    monitor_vehicle_spawn_and_record_data(world)

if __name__ == '__main__':
    main()
