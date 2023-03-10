from agents import Person, Neighbourhood, House
from loader import data_loader

import random
import numpy as np
import json

import mesa
import mesa_geo as mg

class Housing(mesa.Model):
    """
    A Mesa model for housing market.
    """

    def __init__(self, num_houses: np.float32 = 0.001, noise: np.float32 = 0.0, start_money_multiplier: np.uint8 = 2, start_money_multiplier_newcomers: np.uint8 = 2, contentment_threshold: np.float32 = 0.8, weight_materialistic: np.float32 = 0.5, housing_growth_rate: np.float32 = 1.01, population_growth_rate: np.float32 = 1.01, print_statistics: bool = False):
        """
        Create a model for the housing market.

        Args:
            num_houses: Number of houses in the model, as a fraction of the total number of houses in Amsterdam.
            noise: Noise term added to the parameters of a neighbourhood.
            start_money_multiplier: Multiplier for the starting money of a person.
            start_money_multiplier_newcomers: Bonus multiplier for the starting money of a person who enters housing market from outside.
            contentment_threshold: Threshold for agent to start looking for a new house.
            weight_materialistic: The weight of monetary parameters in the contentment function.
            housing_growth_rate: The rate at which the number of houses in the model grows.
            population_growth_rate: The rate at which the number of people in the model grows.
            print_statistics: Flag if model outputs temporal results to the console

        Attributes:
            population: Counter for assiging People IDs.
            amount_population_homeless: Amount of people who do not own a house.
            deals: The amount of exchanges happened so far.
            amount_of_houses: Amount of houses in the city.
            average_contentment: The average contentment of all agents.
            average_cash: The average cash of all agents.
            average_house_price: The average house price of all houses.
            schedule: The scheduler for the model.
            space: The spatial environment for the model.
            running: Boolean for stopping the model.
        """

        # Model parameters
        self.contentment_threshold = contentment_threshold
        self.weight_materialistic = weight_materialistic        # Used in Agent Contentment
        self.num_houses = num_houses
        self.housing_growth_rate = housing_growth_rate
        self.population_growth_rate = population_growth_rate
        self.start_money_multiplier = start_money_multiplier
        self.start_money_multiplier_newcomers = start_money_multiplier_newcomers
        self.noise = noise
        self.print_statistics = print_statistics

        # Model's Global Stats
        self.population = 0
        self.amount_population_homeless = 0
        self.deals = 0
        self.amount_of_houses = 0
        self.average_contentment = 0
        self.average_cash = 0
        self.average_house_price = 0

        # Model components
        self.schedule = mesa.time.RandomActivationByType(self)
        self.space = mg.GeoSpace(warn_crs_conversion=False)

        # Variable for stopping the model when equilibirum is reached.
        self.running = True

        # Set up the model
        self.setup_environment()

    def add_neighbourhoods(self, fn='../data/Amsterdam_map_fin.json'):
        """
        Adds Neighbourhood agents to the model.

        Args:
            fn: The path to the GeoJSON file containing the neighbourhoods' polygons
        """

        # Seting up GeoAgents for neighbourhoods
        geojson_states = json.load(open(fn))
        neighbourhood_agents = mg.AgentCreator(agent_class=Neighbourhood, model=self)
        neighbourhoods = neighbourhood_agents.from_GeoJSON(GeoJSON=geojson_states, unique_id="Stadsdeel")     # Set unique Id to one from dataset
        self.space.add_agents(neighbourhoods)

        return neighbourhoods

    def load_neighbourhood_data(self, neighbourhoods):
        """
        Loads the data from the neighbourhoods dataset to set neighbourhood parameters to real life values.

        Args:
            neighbourhoods: List of Neighbourhoods to initialize.
        """

        # Load real-world data
        gemente_data = data_loader

        # Add data to corresponding neighbourhoods
        for i in range(len(neighbourhoods)):
            neighbourhoods[i].housing_quality_index = gemente_data.neighbourhood_housing_quality[i]
            neighbourhoods[i].shops_index = gemente_data.neighbourhood_shops[i]
            neighbourhoods[i].crime_index = gemente_data.neighbourhood_crime[i]
            neighbourhoods[i].nature_index = gemente_data.neighbourhood_nature[i]
            neighbourhoods[i].capacity = int(gemente_data.neighbourhood_households_amount[i] * self.num_houses)
            neighbourhoods[i].housing_growth_rate = self.housing_growth_rate
            neighbourhoods[i].expenses = gemente_data.neighbourhood_households_expenses[i]
            neighbourhoods[i].average_neighbourhood_price = sum(gemente_data.target_neighbourhood_houses_price)/len(gemente_data.target_neighbourhood_houses_price)     # Average value of all neighbourhoods is a baseline for the house price
            
            # Add Neighbourhood agent to the scheduler
            self.schedule.add(neighbourhoods[i])

    def add_person_and_house(self, id, neighbourhood):
        """
        Adds a Person and a House agent to the model.

        Args:
            id: The id of the Person and House agent.
            neighbourhood: The neighbourhood the agents are assigned to.
        """

        # Add Person agent to the model
        person = Person(unique_id="Initial_Person_"+str(self.population+id), 
                        model=self, 
                        living_location=neighbourhood)

        # Assign House to the model and add the Person agent as it's owner
        house = House(  unique_id="Initial_House_"+str(self.population+id),
                        model=self,
                        neighbourhood=neighbourhood, 
                        initial_price=neighbourhood.average_neighbourhood_price,
                        owner=person,
                        crs=neighbourhood.crs,
                        geometry=neighbourhood.random_point())
        
        # Assign House to the Person agent
        person.house = house
        person.update_contentment_seeking()

        # Add agents to the environment
        self.schedule.add(person)
        self.schedule.add(house)
        self.space.add_agents(house)
    
    def setup_environment(self):
        """
        Adds Neighbourhoods, Persons, and Houses agents to the model.

        """

        # Add Neighbourhoods GeoAgents to the model
        neighbourhoods = self.add_neighbourhoods()

        # Initialize each Neighbourhood by loading data from the dataset
        self.load_neighbourhood_data(neighbourhoods)

        # Add Person and House agents to the model and assign them to a Neighbourhood
        for neighbourhood in neighbourhoods:
            for i in range(0, neighbourhood.capacity):
                self.add_person_and_house(i, neighbourhood)

            # Update counter for People IDs
            self.population += neighbourhood.capacity
        # Upd contentment with new people
        self.update_neighbourhoods_stats(self.get_agents(Neighbourhood))
        if self.print_statistics: self.update_model_params()

        # Create Data Collector
        self.init_data_collector()
        # Collecting data   
        self.datacollector.collect(self)

        # Print initial parameters
        if self.print_statistics: self.print_init()

    def init_data_collector(self):
        """
        Initializes a datacollector for our model        
        """
        
        # Updating model level values
        self.update_statistics()

        # Gather Neighbourhood objects
        self.list_Neighbourhoods_data = self.get_agents(Neighbourhood)

        # Making a dictionary with all the parameters
        model_reporters = {
                "population":               lambda m: m.population,
                "population_homeless":      lambda m: m.amount_population_homeless,
                "amount_of_houses_Centrum":   lambda m: m.list_Neighbourhoods_data[0].capacity,
                "amount_of_houses_Oost":      lambda m: m.list_Neighbourhoods_data[1].capacity,
                "amount_of_houses_NieuwWest": lambda m: m.list_Neighbourhoods_data[2].capacity,
                "amount_of_houses_Zuidoost":  lambda m: m.list_Neighbourhoods_data[3].capacity,
                "amount_of_houses_Noord":     lambda m: m.list_Neighbourhoods_data[4].capacity,
                "amount_of_houses_West":      lambda m: m.list_Neighbourhoods_data[5].capacity,
                "amount_of_houses_Zuid":      lambda m: m.list_Neighbourhoods_data[6].capacity,
                "amount_of_empty_houses_Centrum":     lambda m: m.list_Neighbourhoods_data[0].empty_houses,
                "amount_of_empty_houses_Oost":        lambda m: m.list_Neighbourhoods_data[1].empty_houses,
                "amount_of_empty_houses_NieuwWest":   lambda m: m.list_Neighbourhoods_data[2].empty_houses,
                "amount_of_empty_houses_Zuidoost":    lambda m: m.list_Neighbourhoods_data[3].empty_houses,
                "amount_of_empty_houses_Noord":       lambda m: m.list_Neighbourhoods_data[4].empty_houses,
                "amount_of_empty_houses_West":        lambda m: m.list_Neighbourhoods_data[5].empty_houses,
                "amount_of_empty_houses_Zuid":        lambda m: m.list_Neighbourhoods_data[6].empty_houses,
                "move_in_Centrum":   lambda m: m.list_Neighbourhoods_data[0].move_in,
                "move_in_Oost":      lambda m: m.list_Neighbourhoods_data[1].move_in,
                "move_in_NieuwWest": lambda m: m.list_Neighbourhoods_data[2].move_in,
                "move_in_Zuidoost":  lambda m: m.list_Neighbourhoods_data[3].move_in,
                "move_in_Noord":     lambda m: m.list_Neighbourhoods_data[4].move_in,
                "move_in_West":      lambda m: m.list_Neighbourhoods_data[5].move_in,
                "move_in_Zuid":      lambda m: m.list_Neighbourhoods_data[6].move_in,
                "move_out_Centrum":   lambda m: m.list_Neighbourhoods_data[0].move_out,
                "move_out_Oost":      lambda m: m.list_Neighbourhoods_data[1].move_out,
                "move_out_NieuwWest": lambda m: m.list_Neighbourhoods_data[2].move_out,
                "move_out_Zuidoost":  lambda m: m.list_Neighbourhoods_data[3].move_out,
                "move_out_Noord":     lambda m: m.list_Neighbourhoods_data[4].move_out,
                "move_out_West":      lambda m: m.list_Neighbourhoods_data[5].move_out,
                "move_out_Zuid":      lambda m: m.list_Neighbourhoods_data[6].move_out,
                "average_contentment_Centrum":   lambda m: m.list_Neighbourhoods_data[0].average_contentment,
                "average_contentment_Oost":      lambda m: m.list_Neighbourhoods_data[1].average_contentment,
                "average_contentment_NieuwWest": lambda m: m.list_Neighbourhoods_data[2].average_contentment,
                "average_contentment_Zuidoost":  lambda m: m.list_Neighbourhoods_data[3].average_contentment,
                "average_contentment_Noord":     lambda m: m.list_Neighbourhoods_data[4].average_contentment,
                "average_contentment_West":      lambda m: m.list_Neighbourhoods_data[5].average_contentment,
                "average_contentment_Zuid":      lambda m: m.list_Neighbourhoods_data[6].average_contentment,
                "average_house_price_Centrum":   lambda m: m.list_Neighbourhoods_data[0].average_house_price,
                "average_house_price_Oost":      lambda m: m.list_Neighbourhoods_data[1].average_house_price,
                "average_house_price_NieuwWest": lambda m: m.list_Neighbourhoods_data[2].average_house_price,
                "average_house_price_Zuidoost":  lambda m: m.list_Neighbourhoods_data[3].average_house_price,
                "average_house_price_Noord":     lambda m: m.list_Neighbourhoods_data[4].average_house_price,
                "average_house_price_West":      lambda m: m.list_Neighbourhoods_data[5].average_house_price,
                "average_house_price_Zuid":      lambda m: m.list_Neighbourhoods_data[6].average_house_price,
            }

        # Initializing datacollector object
        self.datacollector = mesa.DataCollector(
            model_reporters=model_reporters
        )

    # Used only for debug and text output
    def update_model_params(self):
        """
        Updates all parameters for the model output to the console (if print_statistics == True)
        """

        list_Houses = self.get_agents(House)
        list_People = self.get_agents(Person)

        self.amount_population_homeless = len([person for person in list_People if person.house == None])
        self.population_house_seekers = len([person for person in list_People if person.seeking])
        self.amount_of_houses = len(list_Houses)
        self.amount_of_houses_empty = len([house for house in list_Houses if house.owner == None])
        self.average_contentment = np.mean([person.contentment for person in list_People])
        self.total_wealth = np.sum([person.cash for person in list_People])
        self.average_cash = np.mean([person.cash for person in list_People])
        self.average_house_price = np.mean([house.price for house in list_Houses])

    # Outputs to the console
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
        print("Amount of Houses, fraction:  " + str(self.num_houses))
        print("Noise:                       " + str(self.noise))
        print("Contentment threshold:       " + str(self.contentment_threshold))
        print("Starting money, multiplier:  " + str(self.num_houses))
        print("Weight materialistic:        " + str(self.weight_materialistic))
        print("Housing Growth rate:         " + str(self.weight_materialistic))
        print("Population Growth rate:      " + str(self.population_growth_rate))
        print("---------------------- INITIAL STATS ----------------------")
        print("Total Wealth:                " + str(self.total_wealth))
        print("Average Disposable Money:    " + str(self.average_cash))
        print("Average Contentment          " + str(self.average_contentment))
        print("Average House Price          " + str(self.average_house_price))
        print("House Seekers                " + str(self.population_house_seekers))
        print("Fraction Unhappy/Happy:      " + str(self.population_house_seekers/self.population) 
                + " / " + str((self.population-self.population_house_seekers)/self.population))
        print("Number of Houses:            " + str(self.amount_of_houses))
        print("Number of Empty Houses:      " + str(self.amount_of_houses_empty))
        print("Number of People:            " + str(self.population))
        print("Number of Homeless:          " + str(self.amount_population_homeless))

        # Print a fun little house :)
        print("\n                                ~~   ")
        print("                               ~       ")
        print("                             _u__      ")
        print("                            /____\\    ")
        print("                            |[][]|     ")
        print("                            |[]..|     ")
        print("                            '--'''\n   ")

    def print_stats(self):
        """
        Prints the output of the model.
        """

        print("--------------------- STEP COMPLETED ----------------------")
        print("After:                       " + str(self.schedule.steps) + " steps")
        print("----------------------- FINAL STATS -----------------------")
        print("Deals:                       " + str(self.deals))
        print("Total Wealth:                " + str(self.total_wealth))
        print("Average Disposable Money:    " + str(self.average_cash))
        print("Average Contentment          " + str(self.average_contentment))
        print("Average House Price          " + str(self.average_house_price))
        print("House Seekers                " + str(self.population_house_seekers))
        print("Fraction Unhappy/Happy:      " + str(self.population_house_seekers/self.population) 
                + " / " + str((self.population-self.population_house_seekers)/self.population))
        print("Number of Houses:            " + str(self.amount_of_houses))
        print("Number of Empty Houses:      " + str(self.amount_of_houses_empty))
        print("Number of People:            " + str(self.population))
        print("Number of Homeless:          " + str(self.amount_population_homeless))

    def get_agents(self, agent_class):
        """
        Returns a list of all the specifiied Agents in the model.

        Args:
            agent_class: The class of the agents type to be returned.
        """

        agents = []
        for agent in self.schedule.agents:
            if isinstance(agent, agent_class):
                agents.append(agent)
        return agents

    def auction_swap(self, s1, s2):
        """
        Performs the house exchange between two Person agents. They swap Houses, Neighbourhood and get or lose some cash (based on the house value).

        Args:
            s1: First Person agent.
            s2: Second Person agent.
        """

        # Detrmine price of houses (**2 just to amplify the change)
        new_house1_price = (1 + s2.calculate_contentment(s1.neighbourhood, s1.house) - s2.calculate_contentment(s2.neighbourhood, s2.house))**2 * s1.house.price
        new_house2_price = (1 + s1.calculate_contentment(s2.neighbourhood, s2.house) - s1.calculate_contentment(s1.neighbourhood, s1.house))**2 * s2.house.price

        # Update House prices and history
        s1.house.price = new_house1_price
        s2.house.price = new_house2_price

        # Update Cash of People
        s1.cash += new_house1_price - new_house2_price
        s2.cash += new_house2_price - new_house1_price

        # Swapping neighbourhoods
        s1_destination = s2.neighbourhood
        s2_destination = s1.neighbourhood
        s1.neighbourhood = s1_destination
        s2.neighbourhood = s2_destination
        
        # Swapping Houses
        s1_new_house = s2.house
        s2_new_house = s1.house
        s1_new_house.owner = s1
        s2_new_house.owner = s2
        s1.house = s1_new_house
        s2.house = s2_new_house

        # Update seeking status
        s1.seeking = False
        s2.seeking = False

    def auction(self):
        """
        Performs trades between agents that are willing to sell and trade their house for another house.
        Or simply put matches Person agents that are willing to leave their neighbourhood (ontentment < contentment_threshold).
        """
        
        # Find all agents that are willing to sell and trade
        sellers = [person for person in self.get_agents(Person) if person.seeking and person.house is not None]
        random.shuffle(sellers)
        
        # Match two sellers if contentment imporves and they can afford the house
        for s1 in sellers:
            matches = {}
            # Sampling only few sellers to improve speed and simulate not perfect choice (bounded rationality)
            house_viewings = 100
            if len(sellers) < 100: house_viewings=len(sellers)
            sellers_sample = random.choices(sellers, k=house_viewings)
            # Starting matching process
            for s2 in sellers_sample:
                if s1 != s2 and s1 is not None and s2 is not None:
                    # Calculate contentment for both parties in potential new neighbourhoods
                    new_s1_score = s1.calculate_contentment(s2.neighbourhood, s2.house)
                    new_s2_score = s2.calculate_contentment(s1.neighbourhood, s1.house)
                    # Check if both parties are happy with the deal
                    if new_s1_score > s1.contentment and new_s2_score > s2.contentment:    
                        # Detrmine price of houses (**2 just to amplify change)
                        new_house1_price = (1 + s2.calculate_contentment(s1.neighbourhood, s1.house) - s2.calculate_contentment(s2.neighbourhood, s2.house))**2 * s1.house.price
                        new_house2_price = (1 + s1.calculate_contentment(s2.neighbourhood, s2.house) - s1.calculate_contentment(s1.neighbourhood, s1.house))**2 * s2.house.price
                        # Check if agents can afford the houses
                        if s1.cash + new_house1_price > new_house2_price and s2.cash + new_house2_price > new_house1_price:
                            # Save the potential match
                            matches[s2] = ((new_s1_score - s1.contentment) + (new_s2_score - s2.contentment)) / 2
            
            # If there are any matches, perform the swap with the best match for s1
            if len(matches) > 0: 
                # Maximalize the joint contentment improvement
                top_match = max(matches, key=matches.get)

                # Swap houses
                self.auction_swap(s1, top_match)

                # Updating statistics
                self.deals += 1
                s1.neighbourhood.move_out += 1
                top_match.neighbourhood.move_in += 1

                # Remove both agents from the list of sellers
                sellers.remove(s1)
                sellers.remove(top_match)

    def movein_empty(self, person, house):
        """
        Moves a person into an empty house.

        Args:
            person: Person agent.
            house: House agent.
        """

        # Check if person already owns a house
        if person.house:
            # Update money spent
            person.cash += person.house.price - house.price
            # Empty old house
            person.house.owner = None
            # Update agents neighbourhood
            person.neighbourhood = house.neighbourhood
            # Move into new house
            person.house = house
            person.house.owner = person
        # Else person does not own a house
        else:
            person.cash -= house.price
            person.neighbourhood = house.neighbourhood
            person.house = house
            house.owner = person

    def sell_empty_houses(self):
        """
        Sells empty houses to the highest bidders.
        """
        
        # Find all house seekers and empty houses
        empty_houses = [house for house in self.get_agents(House) if house.owner == None]
        population_house_seekers = [person for person in self.get_agents(Person) if person.seeking]

        # Check if there are any empty houses or house seekers
        if len(empty_houses) == 0 or len(population_house_seekers) == 0: return

        # Shuffle the lists
        random.shuffle(empty_houses)
        random.shuffle(population_house_seekers)

        # Match house seekers with empty houses
        for house in empty_houses:
            for seeker in population_house_seekers:
                # Check if seeker already owns a house
                if seeker.house:
                    new_contentment = seeker.calculate_contentment(house.neighbourhood, house)
                    # If seeker is happy with the new house and can afford it, move in
                    if new_contentment > seeker.contentment:
                        if seeker.cash + seeker.house.price > house.price:
                            self.deals += 2
                            house.neighbourhood.move_in += 1
                            seeker.neighbourhood.move_out += 1
                            self.movein_empty(seeker, house)
                            break   # Go to next avalible house
                else:
                    # If seeker (from outside Amsterdam) can afford the house, move in
                    if seeker.cash > house.price:
                        self.deals += 1
                        house.neighbourhood.move_in += 1
                        self.movein_empty(seeker, house)
                        break   # Go to next avalible house

    def grow_population(self):
        """
        Grows the population size and adds new Person agents to the model.
        """

        # Calculate number of new agents
        new_agents = int(self.population * self.population_growth_rate) - self.population
        
        # Update population size
        self.population += new_agents

        # Add new agents
        for i in range(0, new_agents):
            person = Person(unique_id="NewPerson_"+str(self.population+i), 
                            model=self, 
                            living_location=None)
            person.cash = self.start_money_multiplier_newcomers * person.cash     # Newcomers are supposed to get more money as they come, because they don't own a house
            self.schedule.add(person)

    # Used for model init to update stats after people and house init
    def update_neighbourhoods_stats(self, neighbourhoods):
        """
        Updates parameters of all Neighbourhoods.

        Args:
            neighbourhoods: List of neighbourhoods to be updated.
        """

        for neighbourhood in neighbourhoods:
            neighbourhood.update_stats()

    def update_statistics(self):
        """
        Updates all statistics for the model.
        """

        # Updating model params to gather
        list_People = self.get_agents(Person)
        self.amount_population_homeless = len([person for person in list_People if person.house == None])

        # Updating statistics used in console output
        if self.print_statistics: self.update_model_params()
  
    # Is disabled, as with growing rate, it is always perturbed
    def equilibrium(self):
        """Checks if the model has reached equilibrium."""
        
        # Check if there are no more deals
        if self.deals < 0:
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

        # Grow population
        self.grow_population()

        # Perfrom house trades
        self.auction()
        
        # Sell empty houses
        self.sell_empty_houses()

        # Advance all Agents by one step
        self.schedule.step()

        # Updating statistics (Model Related) and collecting data
        self.update_statistics()
        self.datacollector.collect(self)

        if self.print_statistics:
            print("\n")
            self.print_stats()

        # Check if model has reached equilibrium
        #self.equilibrium()

        return
