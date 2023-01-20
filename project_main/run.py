# Pointless file, but it is nicer to run everything by executing  ~python run.py

#from server import server
#server.launch()

from models import Housing
from agents import Person, Neighbourhood

# Run model for 10 steps
model = Housing()
for i in range(10):
    model.step()

# Show who lives where
agents = model.schedule.agents
for agent in agents:
    if isinstance(agent, Neighbourhood): 
        #print(agent.capacity)
        continue
for agent in agents:
    if isinstance(agent, Person): 
        #print(agent.neighbourhood.unique_id)
        continue

print(model.deals)
    

#agent.geometry
#agent.Oppervlakte_m2
## Available Params
## CBS_Buurtcode,        Buurtcode,          Buurt,          Wijkcode,               Wijk,               Gebiedcode,     Gebied,     Stadsdeelcode,  Stadsdeel,  Oppervlakte_m2
## Neighborhood code,    Neighborhood code,  Neighborhood,   Neighborhood Big code,  Neighbourhood Big,  Area code,      Area,       District code,  District,   Surface
#
## Neighbour Regions
#neighbors = m.space.get_neighbors(agent)
#print([a.unique_id for a in neighbors])
## Regioins in close space
#print([a.unique_id for a in m.space.get_neighbors_within_distance(agent, 500)])

