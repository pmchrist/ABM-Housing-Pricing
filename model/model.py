from agents import Person
from agents import Neighbourhood
from agents import House

import random
import json

import mesa
import mesa_geo as mg

class Housing(mesa.Model):
    """
    A Mesa model for housing market.
    """

    def __init__(self, num_people: int, num_houses: int, noise: float, contentment_threshold: float, weight_1: float, weight_2: float):
        """
        Create a model for the housing market.

        Args:
            num_people: Number of people in the model.
            num_houses: Number of houses in the model.
            noise: Noise term added to the parameters of a neighbourhood.
            contentment_threshold: Threshold for agent to start selling the house.
            weight_1: Weight of the first parameter in the contentment function.
            weight_2: Weight of the second parameter in the contentment function.

        Attributes:
            deals: The amount of exchanges happening on each step.
            schedule: The scheduler for the model.
            space: The spatial environment for the model.
            datacollector: The datacollector for the model.
            running: Boolean for stopping the model when equilibrium is reached.
        """
        
        # Variables representing agents preferences
        self.weight_1 = weight_1
        self.weight_2 = weight_2

        # Variables for keeping track of statistics of the model
        self.population_size = 0 # Counter for assiging People IDs
        self.average_contentment = 0 # Average contentment of all agents
        self.deals = 0  # Counter for amount of trades happening on each step

        # Attributes
        self.contentment_threshold = contentment_threshold
        self.noise = noise
        self.schedule = mesa.time.RandomActivationByType(self)
        self.space = mg.GeoSpace(warn_crs_conversion=False)
        self.datacollector = mesa.DataCollector({"Deals": "deals", "Average Contentment": "average_contentment"})

        # Variable for stopping the model when equilibirum is reached.
        self.running = True

        # Set up the model
        self.setup_environment(num_people, num_houses)

    def load_neighbourhood_data(self, neighbourhood):
        """
        Loads the data from the neighbourhoods dataset.

        Args:
            neighbourhood: The neighbourhood to load the data for.
        """

        # IN FINAL VERSION INITIALIZE THEM WITH THE REAL LIFE VALUES FROM DATASET
        neighbourhood.param_1 = random.random()
        neighbourhood.param_2 = random.random()
        neighbourhood.capacity = random.randint(1, 5)
        neighbourhood.avarage_salary = random.randint(10,20)
        neighbourhood.cost_of_living = random.randint(10,20)
        neighbourhood.average_house_price = random.randint(50,150)
        self.schedule.add(neighbourhood)

    def add_neighbourhoods(self, fn='../data/Amsterdam_map_from_github.geojson'):
        """
        Adds Neighbourhood agents to the model.

        Args:
            fn: The path to the GeoJSON file containing the neighbourhoods.
        """

        # Seting up GeoAgents for neighbourhoods
        geojson_states = json.load(open(fn))
        neighbourhood_agents = mg.AgentCreator(agent_class=Neighbourhood, model=self)
        neighbourhoods = neighbourhood_agents.from_GeoJSON(GeoJSON=geojson_states, unique_id="name")     # Set unique Id to one from dataset
        self.space.add_agents(neighbourhoods)

        return neighbourhoods

    def add_person_and_house(self, id, neighbourhood):
        """
        Adds a Person and a House agent to the model.

        Args:
            id: The id of the Person and House agent.
            neighbourhood: The neighbourhood the agents are assigned to.
        """

        # WEIGHTS ARE RANDOM ATM, AS IF THEY ARE FIXED NO EXCHANGES ARE HAPPENING
        person = Person(unique_id="Person_"+str(self.population_size+id), 
                        model=self, 
                        weight_1=random.random(), 
                        weight_2=random.random(), 
                        starting_money=random.randint(200, 500), 
                        living_location=neighbourhood)
        self.schedule.add(person)

        # Assign houses to each of the Person agents
        house = House(  unique_id="House_"+str(self.population_size+id), # FIND BETTER WAY FOR ID ASSIGNMENT
                        model=self, 
                        neighbourhood=neighbourhood, 
                        price=neighbourhood.average_house_price, # MAYEBE ADD SOME RANDOMNESS TO THIS 
                        owner=person,
                        geometry=neighbourhood.geometry,
                        crs=neighbourhood.crs)
        self.schedule.add(house)

        return person, house

    
    def setup_environment(self, num_people, num_houses):
        """
        Adds Neighbourhoods, Persons, and Houses agents to the model.

        Args:
            num_people: Number of people in the model.
            num_houses: Number of houses in the model.
        """

        # Add Neighbourhoods GeoAgents to the model
        neighbourhoods = self.add_neighbourhoods()

        for neighbourhood in neighbourhoods:
            # Initialize each Neighbourhood by loading data from the dataset
            self.load_neighbourhood_data(neighbourhood) # THIS STEP COULD BE PERFORMED OUTSIDE OF THE LOOP

            # Create Person and House agents and assign them to a Neighbourhood
            for i in range(1, neighbourhood.capacity):
                person, house = self.add_person_and_house(i, neighbourhood)

                # Upadating contentment for the init
                self.average_contentment += person.contentment

            # Update counter for People IDs
            self.population_size += neighbourhood.capacity
            
        # Calculate average contentment
        self.average_contentment = self.average_contentment / self.population_size
        print("Initial Average Contentment: ", self.average_contentment)

        # Collecting data   
        self.datacollector.collect(self)
    
    def find_sellers(self, agents):
        """
        Finds all Person agents that are willing to sell their houses.

        Args:
            agents: List of all agents in the model.
        """

        sellers = []
        for agent in agents:
            if isinstance(agent, Person): 
                if agent.selling: sellers.append(agent)
        return sellers

    def swap(self, s1, s2, new_s1_score, new_s2_score):
        """
        Performs the swap of cash, neighbourhoods, and houses between two agents.

        Args:
            s1: First Person agent.
            s2: Second Person agent.
            new_s1_score: New contentment score for the first agent.
            new_s2_score: New contentment score for the second agent.
        """
        
        # Detrmine price of houses
        s1_price = (1 + new_s1_score - s1.contentment) * s1.neighbourhood.average_house_price # Money paid, based on the deviation from contentment score threshold
        s2_price = (1 + new_s2_score - s2.contentment) * s2.neighbourhood.average_house_price
        
        # Cash transaction
        s1.cash += s1_price - s2_price
        s2.cash += s2_price - s1_price

        # Swapping neighbourhoods
        s1_destination = s2.neighbourhood
        s2_destination = s1.neighbourhood
        s1.neighbourhood = s1_destination
        s2.neighbourhood = s2_destination
        
        # Swapping Houses
        s1_new_house = s2.house
        s2_new_house = s1.house
        s1.house = s1_new_house
        s2.house = s2_new_house

    def get_neighbourhoods(self):
        """
        Returns a list of all neighbourhoods in the model.
        """

        neighbourhoods = []
        for agent in self.schedule.agents:
            if isinstance(agent, Neighbourhood):
                neighbourhoods.append(agent)
        return neighbourhoods

    def update_average_house_price(self, neighbourhoods):
        """
        Updates average house price for each neighbourhood.

        Args:
            neighbourhoods: List of all neighbourhoods in the model.
        """

        for neighbourhood in neighbourhoods:
            # check if houses in neighbourhood
            if len(neighbourhood.houses) == 0:
                continue
            # reset variables
            price_sum = 0
            houses_num = 0
            # calculate new average price for each neighbourhood
            for house in neighbourhood.houses:
                price_sum += house.price
                houses_num += 1
            neighbourhood.average_house_price = price_sum / houses_num

    def auction(self, sellers):
        """
        Performs trades between agents that are willing to sell.

        Args:
            sellers: List of agents that are willing to sell.
        """
        
        for s1 in sellers:
            for s2 in sellers:
                if s1 != s2 and s1 is not None and s2 is not None:
                    # Calculate contentment for both parties in potential new neighbourhoods
                    new_s1_score = s1.calculate_contentment(s2.neighbourhood)
                    new_s2_score = s2.calculate_contentment(s1.neighbourhood)

                    # Improve buyer seller matching, by getting all better offers, and choose from them
                    # If both parties are happy with the deal, swap houses
                    if new_s1_score > s1.contentment and new_s2_score > s2.contentment:
                        self.swap(s1, s2, new_s1_score, new_s2_score)
 
                        # Updating statistics
                        self.deals += 1
                        s1.neighbourhood.moves += 1
                        s2.neighbourhood.moves += 1

                        # As they already exchanged, they should not do it again and we forget them
                        s1 = None
                        s2 = None

    def update_statistics(self, agents):
        """
        Updates statistics for the model.
        
        Args:
            agents: List of all agents in the model.
        """

        # Getting stats for visualization
        for agent in agents:
            if isinstance(agent, Person):
                self.average_contentment += agent.contentment
        self.average_contentment = self.average_contentment / self.population_size
        # Probably STD is more interesting thing to visualize

    def equilibrium(self):
        """Checks if the model has reached equilibrium."""

        # Check if there are no more deals
        if self.deals == 0:
            self.running = False
        else:
            self.running = True

    def step(self):
        """
        Advance the model by one step.
        """ 

        # Resetting deals counter and average_contentment
        self.deals = 0
        self.average_contentment = 0

        # Getting all agents
        agents = self.schedule.agents

        # Find all agents that are willing to sell
        sellers = self.find_sellers(agents)

        # Perfrom house trades
        self.auction(sellers)

        # Working with Neighbourhoods
        for agent in agents:
            if isinstance(agent, Neighbourhood): 
                # Nothing for now
               break        

        # Advance all Agents by one step
        self.schedule.step() # runs step in Agents to update values based on new neighbourhood
        
        # Recalculate average house price per neighbourhood
        neighbourhoods = self.get_neighbourhoods()
        self.update_average_house_price(neighbourhoods)
        
        # Updating statistics and collecting data
        self.update_statistics(agents)
        self.datacollector.collect(self)
        
        # Managing running of simulator and setting next turn
        self.equilibrium()

        return
