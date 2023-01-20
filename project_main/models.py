# File that handles model interaction
# We should also manage all the data imports here (as they are part of neighbourhood init)

from agents import Neighbourhood
from agents import Person
from agents import SchellingAgent

import random
import json

import mesa
import mesa_geo as mg



# Our main model class
# Model 
class Housing(mesa.Model):

    def __init__(self):

        self.schedule = mesa.time.RandomActivationByType(self)
        self.space = mg.GeoSpace(warn_crs_conversion=False)
        self.deals = 0  # Amount of exchanges happening on each step
        #self.datacollector = mesa.datacollection.DataCollector()

        # Seting up Mesa Geo Agents
        # Set up the grid with patches for every region (Adding neighbourhood agents)
        f = open('Amsterdam_map_from_github.geojson')
        geojson_states = json.load(f)
        neighbourhood_Agents = mg.AgentCreator(agent_class=Neighbourhood, model=self)
        neighbourhoods = neighbourhood_Agents.from_GeoJSON(GeoJSON=geojson_states, unique_id="name")     # Set unique Id to one from dataset
        self.space.add_agents(neighbourhoods)
        # Set up Neighbourhoods with People
        k = 0   # needed for counter to keep correct People IDs
        for geo_agent in neighbourhoods:
            # Init each neighbourhood with their parameters
            # IN FINAL VERSION INITIALIZE THEM WITH THE REAL LIFE VALUES FROM DATASET
            geo_agent.param_1 = random.random()
            geo_agent.param_2 = random.random()
            geo_agent.capacity = random.randint(1, 10)
            geo_agent.salary = random.randint(10,20)
            geo_agent.cost_of_living = random.randint(10,20)
            self.schedule.add(geo_agent)
            # Creating People and assigning them to a region
            for i in range(geo_agent.capacity):
                person = Person(unique_id=k+i, model=self, weight_1=random.random(), weight_2=random.random(), starting_money=random.randint(100, 200), living_location=geo_agent)
                self.schedule.add(person)
            # Update counter for People IDs
            k += geo_agent.capacity


    # Step for model, same as in simple mesa
    def step(self):
        self.schedule.step()    # runs step in Agents

        # For each agent (Person) check if he wants to sell
        agents = self.schedule.agents
        sellers = []
        for agent in agents:
            if isinstance(agent, Person): 
                if agent.selling: sellers.append(agent)
        # Manage housing market
        for seller in sellers:
            for buyer in sellers:
                if buyer != seller:
                    new_seller_score = seller.calculate_contentment(buyer.neighbourhood)
                    new_buyer_score = buyer.calculate_contentment(seller.neighbourhood)
                    # Improve buyer seller matching, by getting all better offers, and choose from them
                    # If a person for whom exchanges also improves contentment, swap houses
                    if new_buyer_score > buyer.contentment and new_seller_score > seller.contentment:
                        # Swapping houses
                        buyer_destination = seller.neighbourhood
                        seller_destination = buyer.neighbourhood
                        buyer.neighbourhood = buyer_destination
                        seller.neighbourhood = seller_destination
                        self.deals += 1
                        # Add money paid, based on the deviation from contentment score threshold
        # Just showing amount of trades after current step
        print(self.deals)
        self.deals=0

        # Do something in neighbourhoods
        for agent in agents:
            if isinstance(agent, Neighbourhood): 
                # Nothing for now
               break
        
        return







# Model Example
class GeoSchelling(mesa.Model):
    """Model class for the Schelling segregation model."""

    # Basically, we can pass anything here, width, height and init population are given by map and neighbourhouds amount (in current case)
    def __init__(self, density=0.6, minority_pc=0.2, export_data=False):
        self.density = density
        self.minority_pc = minority_pc
        self.export_data = export_data

        self.schedule = mesa.time.RandomActivation(self)
        self.space = mg.GeoSpace(warn_crs_conversion=False)

        self.happy = 0
        self.datacollector = mesa.DataCollector({"happy": "happy"})

        self.running = True

        # Set up the grid with patches for every region
        ac = mg.AgentCreator(SchellingAgent, model=self)
        agents = ac.from_file("Amsterdam_map_from_github.geojson")
        self.space.add_agents(agents)

        # Set up agents
        for agent in agents:
            if random.random() < self.density:
                if random.random() < self.minority_pc:
                    agent.atype = 1
                else:
                    agent.atype = 0
                self.schedule.add(agent)

    # No idea, some export for visualization, I guess
    def export_agents_to_file(self) -> None:
        self.space.get_agents_as_GeoDataFrame(agent_cls=SchellingAgent).to_crs(
            "epsg:4326"
        ).to_file("data/schelling_agents.geojson", driver="GeoJSON")

    # Step for model, same as in simple mesa
    def step(self):
        """Run one step of the model.

        If All agents are happy, halt the model.
        """
        self.happy = 0  # Reset counter of happy agents
        self.schedule.step()
        self.datacollector.collect(self)

        if self.happy == self.schedule.get_agent_count():
            self.running = False

        if not self.running and self.export_data:
            self.export_agents_to_file()
