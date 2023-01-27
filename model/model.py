from agents import Person, Neighbourhood, House

import random
import numpy as np
import json

import mesa
import mesa_geo as mg

class Housing(mesa.Model):
    """
    A Mesa model for housing market.
    """

    def __init__(self, num_people: int, num_houses: int, noise: float, contentment_threshold: float, param_1: float, param_2: float, money_loving: float):
        """
        Create a model for the housing market.

        Args:
            num_people: Number of people in the model.
            num_houses: Number of houses in the model.
            noise: Noise term added to the parameters of a neighbourhood.
            contentment_threshold: Threshold for agent to start selling the house.
            param_1: PARAMETER WE ARE ANALYZING.
            param_2: PARAMETER WE ARE ANALYZING.

        Attributes:
            population_size: Counter for assiging People IDs.
            average_contentment: The average contentment of all agents.
            average_house_price: The average house price of all houses.
            deals: The amount of exchanges happening on each step.
            schedule: The scheduler for the model.
            space: The spatial environment for the model.
            datacollector: The datacollector for the model.
            running: Boolean for stopping the model when equilibrium is reached.
        """
        
        # Variables representing parameters
        self.param_1 = param_1
        self.param_2 = param_2
        self.money_loving = money_loving

        # Variables for keeping track of statistics of the model
        self.population_size = 0
        self.average_contentment = []
        self.average_cash = []
        self.average_house_price = []
        self.deals = []
        self.house_seekers = []

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
        neighbourhood.average_house_price_history.append(random.randint(50,150))
        self.schedule.add(neighbourhood)

    def add_neighbourhoods(self, fn='../data/Amsterdam_map_fin.json'):
        """
        Adds Neighbourhood agents to the model.

        Args:
            fn: The path to the GeoJSON file containing the neighbourhoods.
        """

        # Seting up GeoAgents for neighbourhoods
        geojson_states = json.load(open(fn))
        neighbourhood_agents = mg.AgentCreator(agent_class=Neighbourhood, model=self)
        neighbourhoods = neighbourhood_agents.from_GeoJSON(GeoJSON=geojson_states, unique_id="Stadsdeel")     # Set unique Id to one from dataset
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
                        money_loving=self.money_loving,
                        starting_money=random.randint(200, 500), 
                        living_location=neighbourhood)
        self.schedule.add(person)

        # Assign houses to each of the Person agents
        house = House(  unique_id="House_"+str(self.population_size+id), # FIND BETTER WAY FOR ID ASSIGNMENT
                        model=self, 
                        neighbourhood=neighbourhood, 
                        initial_price=neighbourhood.average_house_price_history[-1], # MAYEBE ADD SOME RANDOMNESS TO THIS 
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

        tmp_contentment = 0
        for neighbourhood in neighbourhoods:
            # Initialize each Neighbourhood by loading data from the dataset
            self.load_neighbourhood_data(neighbourhood)

            # Create Person and House agents and assign them to a Neighbourhood
            for i in range(1, neighbourhood.capacity):
                person, house = self.add_person_and_house(i, neighbourhood)

                # Upadating contentment for the init
                tmp_contentment += person.contentment

            # Update counter for People IDs
            self.population_size += neighbourhood.capacity
            
        # Calculate average contentment
        self.average_contentment.append(tmp_contentment / self.population_size)
        
        # Print initial parameters
        self.print_init()

        # Collecting data   
        self.datacollector.collect(self)
    
    def print_init(self):
        """
        Prints the initial parameters and stats of the model.
        """

        # Print a pretty header ;)
        print("   __ __              _             __  ___         __       __ ")
        print("  / // /__  __ _____ (_)__  ___ _  /  |/  /__ _____/ /_____ / /_")
        print(" / _  / _ \/ // (_-</ / _ \/ _ `/ / /|_/ / _ `/ __/  '_/ -_) __/")
        print("/_//_/\___/\_,_/___/_/_//_/\_, / /_/  /_/\_,_/_/ /_/\_\\__/\__/ ")
        print("   ___             __     /___/   __                            ")
        print("  / _ | __ _  ___ / /____ _______/ /__ ___ _                    ")
        print(" / __ |/  ' \(_-</ __/ -_) __/ _  / _ `/  ' \                   ")
        print("/_/ |_/_/_/_/___/\__/\__/_/  \_,_/\_,_/_/_/_/                 \n")
        

        # Print initial parameters and stats
        print("---------------------- INITIAL MODEL ----------------------")
        print("Population size:             " + str(self.population_size))
        print("Number of neighbourhoods:    " + str(len(self.get_agents(Neighbourhood))))
        print("Contentment threshold:       " + str(self.contentment_threshold))
        print("Noise:                       " + str(self.noise))
        print("Parameter 1:                 " + str(self.param_1))
        print("Parameter 2:                 " + str(self.param_2))
        
        print("---------------------- INITIAL STATS ----------------------")
        print("Total Wealth:                " + str(np.mean([person.cash for person in self.get_agents(Person)]) * self.population_size))
        print("Average Wealth:              " + str(np.mean([person.cash for person in self.get_agents(Person)])))
        print("Average Contentment:         " + str(self.average_contentment[-1]))
        print("Average House Price:         " + str(np.mean([house.price_history[-1] for house in self.get_agents(House)])))
        print("House-Seekers:               " + str(len([person for person in self.get_agents(Person) if person.selling])))
        print("Fraction Unhappy/Happy:      " + str(len([person for person in self.get_agents(Person) if person.selling])/self.population_size) 
                + " / " + str((self.population_size-len([person for person in self.get_agents(Person) if person.selling]))/self.population_size))

        # Print a fun little house :)
        print("\n                                ~~   ")
        print("                               ~       ")
        print("                             _u__      ")
        print("                            /____\\    ")
        print("                            |[][]|     ")
        print("                            |[]..|     ")
        print("                            '--'''\n   ")

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
        # LOOK AT THIS
        house1_price = (1 + new_s2_score - s2.contentment) * s1.house.price_history[-1] # Money paid, based on the deviation from contentment score threshold
        house2_price = (1 + new_s1_score - s1.contentment) * s2.house.price_history[-1]

        # Update House prices and history
        s1.house.price_history.append(house1_price)
        s2.house.price_history.append(house2_price)

        # Cash transaction
        s1.cash += house1_price - house2_price
        s2.cash += house2_price - house1_price

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

    def get_agents(self, agent_class):
        """
        Returns a list of all the specifiied Agents in the model.

        Args:
            agent_class: The class of the agents to be returned.
        """

        agents = []
        for agent in self.schedule.agents:
            if isinstance(agent, agent_class):
                agents.append(agent)
        return agents

    def update_average_house_price(self, neighbourhoods):
        """
        Updates average house price for each neighbourhood.

        Args:
            neighbourhoods: List of all neighbourhoods in the model.
        """

        for neighbourhood in neighbourhoods:
            # Check if houses in neighbourhood
            if len(neighbourhood.houses) == 0:
                continue

            # Reset variables
            price_sum = 0
            houses_num = 0
            
            # Calculate new average price for each neighbourhood
            for house in neighbourhood.houses:
                price_sum += house.price_history[-1]
                houses_num += 1
            neighbourhood.average_house_price_history.append(price_sum / houses_num)

    def auction(self, sellers):
        """
        Performs trades between agents that are willing to sell.

        Args:
            sellers: List of agents that are willing to sell.
        """
        
        tmp_deals = 0
        for s1 in sellers:
            matches = {}
            for s2 in sellers:
                if s1 != s2 and s1 is not None and s2 is not None:
                    # Calculate contentment for both parties in potential new neighbourhoods
                    new_s1_score = s1.calculate_contentment(s2.neighbourhood)
                    new_s2_score = s2.calculate_contentment(s1.neighbourhood)

                    # If both parties are happy with the deal, save the potential match
                    if new_s1_score > s1.contentment and new_s2_score > s2.contentment:
                        # Check if agents can afford the houses
                        if s1.cash + s1.house.price_history[-1] > s2.house.price_history[-1] and s2.cash + s2.house.price_history[-1] > s1.house.price_history[-1]:
                            matches[s2] = new_s1_score
            
            # If there are any matches, perform the swap with the best match for s1
            if len(matches) > 0: 
                # Find the best match
                top_match = max(matches, key=matches.get)

                # Swap houses
                self.swap(s1, top_match, matches[top_match], top_match.calculate_contentment(s1.neighbourhood))

                # Updating statistics
                tmp_deals += 1
                s1.neighbourhood.moves += 1
                top_match.neighbourhood.moves += 1

                # Remove both agents from the list of sellers
                sellers.remove(s1)
                sellers.remove(top_match)

        # Update number of deals statistic
        self.deals.append(tmp_deals)

    def update_statistics(self, agents):
        """
        Updates statistics for the model.
        
        Args:
            agents: List of all agents in the model.
        """

        # Recalculate average contentment
        tmp_contentment = 0
        for person in self.get_agents(Person):
            tmp_contentment += person.contentment
        self.average_contentment.append(tmp_contentment / self.population_size)
        # Probably STD is more interesting thing to visualize

        # Recalculate average house price of entire city
        self.average_house_price.append(np.mean([house.price_history[-1] for house in self.get_agents(House)]))

        # Recalculate the average amount of cash in the city
        self.average_cash.append(np.mean([person.cash for person in self.get_agents(Person)]))

        # Recalculate number of house seekers in the city
        self.house_seekers.append(len([person for person in self.get_agents(Person) if person.selling]))

    def equilibrium(self):
        """Checks if the model has reached equilibrium."""

        # Check if there are no more deals
        if self.deals[-1] == 0:
            print("------------------- EQUILIBRIUM REACHED -------------------")
            print("After:                       " + str(self.schedule.steps) + " steps")
            print("----------------------- FINAL STATS -----------------------")
            print("Total Wealth:                " + str(self.average_cash[-1] * self.population_size))
            print("Average Wealth:              " + str(self.average_cash[-1]))
            print("Average Deals:               " + str(np.mean(self.deals)))
            print("Average Contentment:         " + str(self.average_contentment[-1]))
            print("Average House Price:         " + str(self.average_house_price[-1]))
            print("House Seekers:               " + str(self.house_seekers[-1]))
            print("Fraction Unhappy/Happy:      " + str(self.house_seekers[-1]/self.population_size) + " / " + str((self.population_size-self.house_seekers[-1])/self.population_size))
            
            self.running = False
        else:
            self.running = True

    def step(self):
        """
        Advance the model by one step.
        """ 

        # Stop if model has reached equilibrium
        if self.running == False:
            return

        # Find all agents that are willing to sell
        sellers = self.find_sellers(self.get_agents(Person))

        # Perfrom house trades
        self.auction(sellers)

        # Advance all Agents by one step
        self.schedule.step() # runs step in Agents to update values based on new neighbourhood
        
        # Recalculate average house price per neighbourhood
        neighbourhoods = self.get_agents(Neighbourhood)
        self.update_average_house_price(neighbourhoods)
        
        # Updating statistics and collecting data
        self.update_statistics(self.schedule.agents)
        self.datacollector.collect(self)
        
        # Check if model has reached equilibrium
        self.equilibrium()

        return
