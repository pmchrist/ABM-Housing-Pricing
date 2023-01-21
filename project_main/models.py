# File that handles model interaction
# We should also manage all the data imports here (as they are part of neighbourhood init)

from agents import Neighbourhood
from agents import Person
from agents import SchellingAgent

import random
import json

import mesa
import mesa_geo as mg


# Model 
class Housing(mesa.Model):

    def __init__(self, weight_1, weight_2):
        """Create a model for the housing market.

        Attributes:
            schedule: The scheduler for the model.
            space: The spatial environment for the model.
            deals: The amount of exchanges happening on each step.
        """
        
        # Variable Agent params for creation of model
        self.weight_1 = weight_1    # If they are fixed, no exchanges are happening
        self.weight_2 = weight_2    # If they are fixed, no exchanges are happening

        # Running statistics of the model
        self.population_size = 0   # needed for counter to keep correct People IDs
        self.average_contentment = 0    # Average contentment in Agents
        self.deals = 0  # Amount of exchanges happening on each step
        self.running = True

        # Attributes
        self.schedule = mesa.time.RandomActivationByType(self)
        self.space = mg.GeoSpace(warn_crs_conversion=False)
        self.datacollector = mesa.DataCollector({"Deals": "deals", "Average Contentment": "average_contentment"})

        # Seting up Mesa Geo Agents
        # Set up the grid with patches for every region (Adding neighbourhood agents)
        f = open('Amsterdam_map_from_github.geojson')
        geojson_states = json.load(f)
        neighbourhood_Agents = mg.AgentCreator(agent_class=Neighbourhood, model=self)
        neighbourhoods = neighbourhood_Agents.from_GeoJSON(GeoJSON=geojson_states, unique_id="name")     # Set unique Id to one from dataset
        self.space.add_agents(neighbourhoods)

        # Set up Neighbourhoods with People
        for geo_agent in neighbourhoods:
            # Init each neighbourhood with their parameters
            # IN FINAL VERSION INITIALIZE THEM WITH THE REAL LIFE VALUES FROM DATASET
            geo_agent.param_1 = random.random()
            geo_agent.param_2 = random.random()
            geo_agent.capacity = random.randint(10, 50)
            geo_agent.salary = random.randint(10,20)
            geo_agent.cost_of_living = random.randint(10,20)
            geo_agent.average_house_price = random.randint(50,150)
            self.schedule.add(geo_agent)
            # Creating People and assigning them to a region
            for i in range(geo_agent.capacity):
                # WEIGHTS ARE RANDOM, AS IF THEY ARE FIXED NO EXCHANGES ARE HAPPENING
                person = Person(unique_id=self.population_size+i, model=self, weight_1=random.random(), weight_2=random.random(), starting_money=random.randint(200, 500), living_location=geo_agent)
                self.schedule.add(person)
                # Upadating contentment for the init
                self.average_contentment += person.contentment
            # Update counter for People IDs
            self.population_size += geo_agent.capacity
        self.average_contentment = self.average_contentment/self.population_size
        #print("Init Average Contentment: ", self.average_contentment)

    # Step for model, same as in simple mesa
    def step(self):
        """Advance the model by one step.""" 

        self.deals = 0  # Reset counter of deals
        self.average_contentment = 0
        self.schedule.step() # runs step in Agents
        
        # For each agent (Person) check if he wants to sell
        agents = self.schedule.agents
        sellers = []
        for agent in agents:
            if isinstance(agent, Person): 
                if agent.selling: sellers.append(agent)

        # Find potential trades
        for seller in sellers:
            for buyer in sellers:
                if buyer != seller and buyer is not None and seller is not None:
                    # Calculate contentment for both parties in potential new neighbourhoods
                    new_seller_score = seller.calculate_contentment(buyer.neighbourhood)
                    new_buyer_score = buyer.calculate_contentment(seller.neighbourhood)
                    # Improve buyer seller matching, by getting all better offers, and choose from them
                    # If both parties are happy with the deal, swap houses
                    if new_buyer_score > buyer.contentment and new_seller_score > seller.contentment:
                        # TO WORK PROPERLY, NEEDS CALCULATION OF AVERAGE HOUSE PRICE AND UPDATE IN UTILITY FUNCTION
                        # ALSO IMPLEMENT HERE AVERAGE HOUSE PRICE IN NEIGHBOURHOOD UPDATE
                        # Money paid, based on the deviation from contentment score threshold
                        # Transactions payed for houses
                        buyer.cash -= (1 + new_buyer_score - buyer.contentment) * buyer.neighbourhood.average_house_price
                        seller.cash -= (1 + new_seller_score - seller.contentment) * seller.neighbourhood.average_house_price
                        # Money earned, based on the deviation from contentment score threshold
                        buyer.cash += (1 + new_seller_score - seller.contentment) * seller.neighbourhood.average_house_price
                        seller.cash += (1 + new_buyer_score - buyer.contentment) * buyer.neighbourhood.average_house_price
                        # Swapping houses
                        buyer_destination = seller.neighbourhood
                        seller_destination = buyer.neighbourhood
                        buyer.neighbourhood = buyer_destination
                        seller.neighbourhood = seller_destination
                        # Updating statistics
                        self.deals += 1
                        seller.neighbourhood.moves += 1
                        # As they already exchanged, they should not do it again and we forget them
                        seller = None
                        buyer = None
                        
        # Getting average contentment:
        for agent in agents:
            if isinstance(agent, Person): 
                self.average_contentment += agent.contentment
        self.average_contentment = self.average_contentment / self.population_size
        # Probably STD is more interesting thing to visualize

        # Do something in neighbourhoods
        for agent in agents:
            if isinstance(agent, Neighbourhood): 
                # Nothing for now
               break
        
        # Managing running of simulator and setting next turn
        if self.deals == 0:
            self.running = False
        self.datacollector.collect(self)
        
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
