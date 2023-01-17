import warnings

warnings.filterwarnings("ignore")

import mesa
import mesa_geo as mg
import json



f = open('Amsterdam_map_from_gemente.geojson')
geojson_states = json.load(f)





# Agent
class State(mg.GeoAgent):
    def __init__(self, unique_id, model, geometry, crs):
        super().__init__(unique_id, model, geometry, crs)

# Model
class GeoModel(mesa.Model):
    def __init__(self):
        self.space = mg.GeoSpace()

        ac = mg.AgentCreator(agent_class=State, model=self)
        agents = ac.from_GeoJSON(GeoJSON=geojson_states, unique_id="Buurt")     # Set unique Id to one from dataset
        self.space.add_agents(agents)





    

m = GeoModel()

# Showing Params of Agent
agent = m.space.agents[0]
print(agent.unique_id)
agent.geometry
agent.Oppervlakte_m2
# Available Params
# CBS_Buurtcode,        Buurtcode,          Buurt,          Wijkcode,               Wijk,               Gebiedcode,     Gebied,     Stadsdeelcode,  Stadsdeel,  Oppervlakte_m2
# Neighborhood code,    Neighborhood code,  Neighborhood,   Neighborhood Big code,  Neighbourhood Big,  Area code,      Area,       District code,  District,   Surface

# Neighbour Regions
neighbors = m.space.get_neighbors(agent)
print([a.unique_id for a in neighbors])
# Regioins in close space
print([a.unique_id for a in m.space.get_neighbors_within_distance(agent, 500)])

