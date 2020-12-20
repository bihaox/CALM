from __future__ import print_function
from __future__ import division
from builtins import range
from past.utils import old_div
import MalmoPython
import os
import sys
import time
import TextGen
import os
import sys
import time
import json
import random
from tqdm import tqdm
from collections import deque
import matplotlib.pyplot as plt 
import numpy as np
from numpy.random import randint
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
import torch.nn.functional as F


# Hyperparameters
SIZE = 50
WEATHER="clear"
time_now=5000
OBS_SIZE = 10
REPLAY_BUFFER_SIZE = 10000
BATCH_SIZE = 128
GAMMA = .9
TARGET_UPDATE = 100
WORLD_PATH = os.path.join(os.path.dirname(__file__), 'New World')
ACTION_DICT = {
    0: 'move 1',  # Move one block forward
    1: 'turn 1',  # Turn 90 degrees to the right
    2: 'turn -1',  # Turn 90 degrees to the left
    3: 'attack 1'  # Destroy block
}

if sys.version_info[0] == 2:
    sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)  # flush print output immediately
else:
    import functools
    print = functools.partial(print, flush=True)


def get_observation(world_state,weather,time_now):
    """
    Use the agent observation API to get a 2 x 5 x 5 grid around the agent. 
    The agent is in the center square facing up.

    Args
        world_state: <object> current agent world state

    Returns
        observation: <np.array>
    """
    obs = np.zeros((2, OBS_SIZE, OBS_SIZE))
    object_list=[]
    while world_state.is_mission_running:
        time.sleep(0.1)
        world_state = agent_host.getWorldState()
       
        if len(world_state.errors) > 0:
            raise AssertionError('Could not load grid.')

        if world_state.number_of_observations_since_last_state > 0:
            # First we get the json from the observation API
            msg = world_state.observations[-1].text
            observations = json.loads(msg)
            # Get observation
            if weather != 'clear':
                object_list.append(weather)
            if time_now>13000:
                object_list.append("night")
            else:
                object_list.append("morning")
            grid = observations['floorAll']
            
            if grid.count('water')>3:
                object_list.append("river")
            if grid.count('leaves')>2:
                object_list.append("tree")
            if grid.count('lava')>1:
                object_list.append("lava")
                
            animal=observations['NearbyEntities']
            target_ani=['Sheep','Cow','Pig']
            for i in animal:
                if i['name'] not in object_list and i['name'] in target_ani:
                    object_list.append(i['name'])
            break
            
           
    return object_list

 
missionXML='''<?xml version="1.0" encoding="UTF-8" standalone="no" ?>
            <Mission xmlns="http://ProjectMalmo.microsoft.com" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
            
              <About>
                <Summary>Generate Text With Malmo</Summary>
              </About>
              
            <ServerSection>
              <ServerInitialConditions>
                <Time>
                    <StartTime>'''+str(time_now)+'''</StartTime>
                    <AllowPassageOfTime>false</AllowPassageOfTime>
                </Time>
                <Weather>'''+WEATHER+'''</Weather>
              </ServerInitialConditions>
              <ServerHandlers>
                  <FileWorldGenerator src="'''+ WORLD_PATH + '''"/>
                  <ServerQuitFromTimeUp timeLimitMs="3000000"/>
                  <ServerQuitWhenAnyAgentFinishes/>
                </ServerHandlers>
              </ServerSection>
              
              <AgentSection mode="Survival">
                <Name>MalmoTutorialBot</Name>
                <AgentStart>
                    <Inventory>
                        <InventoryItem slot="8" type="diamond_pickaxe"/>
                    </Inventory>
                </AgentStart>
                <AgentHandlers>
                <ChatCommands/>
                  <ObservationFromFullStats/>
                  <ObservationFromGrid>
                            <Grid name="floorAll">
                                <min x="-'''+str(int(OBS_SIZE/2))+'''" y="-2" z="-'''+str(int(OBS_SIZE/2))+'''"/>
                                <max x="'''+str(int(OBS_SIZE/2))+'''" y="3" z="'''+str(int(OBS_SIZE/2))+'''"/>
                            </Grid>
                  </ObservationFromGrid>
                  <ObservationFromNearbyEntities>
                        <Range name="NearbyEntities"
                        xrange="10"
                        yrange="4"
                        zrange="2"
                        update_frequency="1"/>
                  </ObservationFromNearbyEntities>
                  <ContinuousMovementCommands turnSpeedDegs="180"/>
                  <InventoryCommands/>
                  <AgentQuitFromReachingPosition>
                    <Marker x="-26.5" y="40.0" z="0.5" tolerance="0.5" description="Goal_found"/>
                  </AgentQuitFromReachingPosition>
                </AgentHandlers>
              </AgentSection>
            </Mission>'''

# Create default Malmo objects:
prvious_list=[]
agent_host = MalmoPython.AgentHost()
try:
    agent_host.parse( sys.argv )
except RuntimeError as e:
    print('ERROR:',e)
    print(agent_host.getUsage())
    exit(1)
if agent_host.receivedArgument("help"):
    print(agent_host.getUsage())
    exit(0)

my_mission = MalmoPython.MissionSpec(missionXML, True)
my_mission_record = MalmoPython.MissionRecordSpec()

# Attempt to start a mission:
max_retries = 3
for retry in range(max_retries):
    try:
        agent_host.startMission( my_mission, my_mission_record )
        break
    except RuntimeError as e:
        if retry == max_retries - 1:
            print("Error starting mission:",e)
            exit(1)
        else:
            time.sleep(2)

# Loop until mission starts:

world_state = agent_host.getWorldState()
while not world_state.has_mission_begun:
    print(".", end="")
    time.sleep(0.1)
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print("Error:",error.text)

print()
TOTAL_LOOP = 25
textGen = TextGen.TextGen()
#genre_list = ['superhero', 'sci_fi', 'action', 'drama', 'horror', 'thriller']
genre_list = ['superhero', 'sci_fi']
mode = 'nucleus'
search_size = 10
# Loop until mission ends:

while world_state.is_mission_running:
    time.sleep(0.1)
    signal = input('Please enter any key to start detect')
    world_state = agent_host.getWorldState()
    for error in world_state.errors:
        print("Error:",error.text)
    obs=get_observation(world_state,WEATHER,time_now)
    obs = [x.lower() for x in obs]
    
    
    print()
    print('observation:', obs)
    
    prvious_list = list(obs)

    genre = genre_list[random.randint(0,len(genre_list)-1)]
    print('genre:', genre)
    if genre == 'sci_fi' or genre =='superhero':
        input_word = ['In the future', 'In the year of 2077', 'Yesterday'][randint(0, 3)]
    elif genre == 'horror' or genre =='thriller':
        input_word = ['In a darks house', 'In the deep forest', 'Midnight'][randint(0, 3)]
    else:
        input_word = ['This summer', 'Long long ago', 'Today'][randint(0, 3)]
    
    target_list = obs
    sentence=textGen.generate_target_list(input_word, target_list, genre, search_size,TOTAL_LOOP, mode)
    print()
    print(sentence)
    print()
    agent_host.sendCommand("chat " + sentence)
        
   

print()
print("Mission ended")
# Mission has ended.
