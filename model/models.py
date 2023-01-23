# File that handles model interaction
# We should also manage all the data imports here (as they are part of neighbourhood init)

from agents import Person
from agents import Neighbourhood
from agents import House

import random
import json

import mesa
import mesa_geo as mg


# Model 
class Housing(mesa.Model):
    """A Mesa model for housing market."""

    def __init__(self, num_people, num_houses, weight_1, weight_2):
        """Create a model for the housing market.

        Args:
            num_people: Number of people in the model.
            num_houses: Number of houses in the model.
            weight_1: Weight of the first parameter in the contentment function.
            weight_2: Weight of the second parameter in the contentment function.

        Attributes:
            schedule: The scheduler for the model.
            space: The spatial environment for the model.
            deals: The amount of exchanges happening on each step.
        """
        
        # Variables representing agents preferences
        self.weight_1 = weight_1
        self.weight_2 = weight_2

        # Variables for keeping track of statistics of the model
        self.population_size = 0 # Counter for assiging People IDs
        self.average_contentment = 0 # Average contentment of all agents
        self.deals = 0  # Counter for amount of trades happening on each step

        # Attributes
        self.schedule = mesa.time.RandomActivationByType(self)
        self.space = mg.GeoSpace(warn_crs_conversion=False)
        self.datacollector = mesa.DataCollector({"Deals": "deals", "Average Contentment": "average_contentment"})

        # Variable for stopping the model when equilibirum is reached.
        self.running = True

        # Seting up GeoAgents for neighbourhoods
        f = open('../data/Amsterdam_map_from_github.geojson')
        geojson_states = json.load(f)
        neighbourhood_agents = mg.AgentCreator(agent_class=Neighbourhood, model=self)
        neighbourhoods = neighbourhood_agents.from_GeoJSON(GeoJSON=geojson_states, unique_id="name")     # Set unique Id to one from dataset
        self.space.add_agents(neighbourhoods)

        # Assign neighbourhoods to each of the Person agents
        for neighbourhood in neighbourhoods:

            # Initialize each Neighbourhood with their corresponding values
            # IN FINAL VERSION INITIALIZE THEM WITH THE REAL LIFE VALUES FROM DATASET
            neighbourhood.param_1 = random.random()
            neighbourhood.param_2 = random.random()
            neighbourhood.capacity = random.randint(1, 5)
            neighbourhood.salary = random.randint(10,20)
            neighbourhood.cost_of_living = random.randint(10,20)
            neighbourhood.average_house_price = random.randint(50,150)
            # Add neighbourhood to schedule
            self.schedule.add(neighbourhood)

            # Create People and assign them to a Neighbourhood
            for i in range(1, neighbourhood.capacity):
                # WEIGHTS ARE RANDOM ATM, AS IF THEY ARE FIXED NO EXCHANGES ARE HAPPENING
                person = Person(unique_id=self.population_size+i, 
                                model=self, 
                                weight_1=random.random(), 
                                weight_2=random.random(), 
                                starting_money=random.randint(200, 500), 
                                living_location=neighbourhood)
                self.schedule.add(person)

                # Assign houses to each of the Person agents
                house = House(  unique_id=self.population_size+i+10000, 
                                model=self, 
                                neighbourhood=neighbourhood, 
                                price=neighbourhood.average_house_price, 
                                owner=person,
                                geometry=neighbourhood.geometry,
                                crs=neighbourhood.crs)
                self.schedule.add(house)

                # Upadating contentment for the init
                self.average_contentment += person.contentment

            # Update counter for People IDs
            self.population_size += neighbourhood.capacity
            
        # Calculate average contentment
        self.average_contentment = self.average_contentment / self.population_size
        print("Initial Average Contentment: ", self.average_contentment)

        # Collecting data   
        self.datacollector.collect(self)

    # Step for model, same as in simple mesa
    def step(self):
        """Advance the model by one step.""" 

        self.deals = 0  # Reset counter of deals
        self.average_contentment = 0
        
        # Working with People
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

        # Working with Neighbourhoods
        for agent in agents:
            if isinstance(agent, Neighbourhood): 
                # Nothing for now
               break        

        # Advancing All Agents for one step
        self.schedule.step() # runs step in Agents to update values based on new neighbourhood

        # Getting stats for visualization
        # Getting average contentment:
        for agent in agents:
            if isinstance(agent, Person):
                self.average_contentment += agent.contentment
        self.average_contentment = self.average_contentment / self.population_size
        # Probably STD is more interesting thing to visualize

        self.datacollector.collect(self)

        # Managing running of simulator and setting next turn
        if self.deals == 0:
            self.running = False

        return
