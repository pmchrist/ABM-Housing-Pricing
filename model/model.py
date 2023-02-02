from agents import Person, Neighbourhood, House
from loader import data_loader

from agents import keeper_money, keeper_neigh

import random
import numpy as np
import json

import mesa
import mesa_geo as mg

class Housing(mesa.Model):
    """
    A Mesa model for housing market.
    """

    def __init__(self, num_houses: int, noise: float, start_money_multiplier: int, start_money_multiplier_newcomers: int, contentment_threshold: float, weight_materialistic: float, housing_growth_rate: float, population_growth_rate: float, print_stats: bool = False):
        """
        Create a model for the housing market.

        Args:
            num_houses: Number of houses in the model, as a fraction of the total number of houses in Amsterdam.
            noise: Noise term added to the parameters of a neighbourhood.
            start_money_multiplier: Multiplier for the starting money of a person.
            contentment_threshold: Threshold for agent to start looking for a new house.
            weight_materialistic: The weight of money in the contentment function.
            housing_growth_rate: The rate at which the number of houses in the model grows.
            population_growth_rate: The rate at which the number of people in the model grows.

        Attributes:
            num_houses: Number of houses in the model, as a fraction of the total number of houses in Amsterdam.
            population_size: Counter for assiging People IDs.
            average_contentment: The average contentment of all agents.
            average_cash: The average cash of all agents.
            average_house_price: The average house price of all houses.
            deals: The amount of exchanges happening on each step.
            house_seekers: The amount of agents looking for a new house on each step.
            schedule: The scheduler for the model.
            space: The spatial environment for the model.
            datacollector: The datacollector for the model.
            running: Boolean for stopping the model when equilibrium is reached.
        """

        # Model parameters
        self.num_houses = num_houses
        self.noise = noise
        self.contentment_threshold = contentment_threshold
        self.weight_materialistic = weight_materialistic        # Used in Agent Contentment
        self.housing_growth_rate = housing_growth_rate
        self.population_growth_rate = population_growth_rate
        self.start_money_multiplier = start_money_multiplier
        self.start_money_multiplier_newcomers = start_money_multiplier_newcomers
        
        # Tracked statistics
        self.population_size = 0
        self.total_wealth = 0
        self.average_cash = 0
        self.deals = 0
        self.house_seekers = 0
        self.average_contentment_Centrum = 0
        self.average_contentment_Oost = 0
        self.average_contentment_NieuwWest = 0
        self.average_contentment_Zuidoost = 0
        self.average_contentment_Noord = 0
        self.average_contentment_West = 0
        self.average_contentment_Zuid = 0
        self.average_house_price_Centrum = 0
        self.average_house_price_Oost = 0
        self.average_house_price_NieuwWest = 0
        self.average_house_price_Zuidoost = 0
        self.average_house_price_Noord = 0
        self.average_house_price_West = 0
        self.average_house_price_Zuid = 0

        # Model components
        self.schedule = mesa.time.RandomActivationByType(self)
        self.space = mg.GeoSpace(warn_crs_conversion=False)
        self.datacollector = mesa.DataCollector({"Deals": "deals",
         "Average Contentment Centrum": "average_contentment_Centrum",
         "Average Contentment Oost": "average_contentment_Oost",
         "Average Contentment NieuwWest": "average_contentment_NieuwWest",
         "Average Contentment Zuidoost": "average_contentment_Zuidoost",
         "Average Contentment Noord": "average_contentment_Noord",
         "Average Contentment West": "average_contentment_West",
         "Average Contentment Zuid": "average_contentment_Zuid",
         "Average House Price Centrum": "average_house_price_Centrum",
         "Average House Price Oost": "average_house_price_Oost",
         "Average House Price NieuwWest": "average_house_price_NieuwWest",
         "Average House Price Zuidoost": "average_house_price_Zuidoost",
         "Average House Price Noord": "average_house_price_Noord",
         "Average House Price West": "average_house_price_West",
         "Average House Price Zuid": "average_house_price_Zuid"
         })

        # Variable for stopping the model when equilibirum is reached.
        self.running = True
        self.print_statistics = print_stats

        # Set up the model
        self.setup_environment()

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

    def load_neighbourhood_data(self, neighbourhoods):
        """
        Loads the data from the neighbourhoods dataset.

        Args:
            neighbourhood: The neighbourhood to load the data for.
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
        person = Person(unique_id="Initial_Person_"+str(self.population_size+id), 
                        model=self, 
                        living_location=neighbourhood)

        # Assign House to the model and add the Person agent as it's owner
        house = House(  unique_id="Initial_House_"+str(self.population_size+id),
                        model=self,
                        neighbourhood=neighbourhood, 
                        initial_price=neighbourhood.average_neighbourhood_price,
                        owner=person,
                        crs=neighbourhood.crs,
                        geometry=neighbourhood.random_point())
        
        # Assign House to the Person agent
        person.house = house

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
            self.population_size += neighbourhood.capacity
        # Upd contentment with new people
        self.update_average_neighbourhood_contentment(self.get_agents(Neighbourhood))
        self.update_model_params()

        # Collecting data   
        self.datacollector.collect(self)

        # Print initial parameters
        if self.print_statistics: self.print_init()

    def update_model_params(self):    

        list_Houses = self.get_agents(House)
        list_People = self.get_agents(Person)
        list_Neighbourhood = self.get_agents(Neighbourhood)

        self.total_wealth = sum([person.cash for person in list_People if person.house])
        self.average_cash = np.mean([person.cash for person in list_People])
        self.house_seekers = len([person for person in list_People if person.seeking])
        self.amount_of_houses = len(list_Houses)
        self.amount_of_houses_empty = len([house for house in list_Houses if house.owner == None])
        self.amount_of_people = len(list_People)
        self.amount_of_people_homeless = len([person for person in list_People if person.house == None])

        neighbourhood_prices = []
        neighbourhood_contentments = []         # IT IS 0 AT THE BEGINNING FIX IT 
        for neighbourhood in list_Neighbourhood:
            neighbourhood_prices.append(neighbourhood.average_neighbourhood_price)
            neighbourhood_contentments.append(neighbourhood.average_neighbourhood_contentment)
        self.average_contentment_Centrum = neighbourhood_contentments[0]
        self.average_contentment_Oost = neighbourhood_contentments[1]
        self.average_contentment_NieuwWest = neighbourhood_contentments[2]
        self.average_contentment_Zuidoost = neighbourhood_contentments[3]
        self.average_contentment_Noord = neighbourhood_contentments[4]
        self.average_contentment_West = neighbourhood_contentments[5]
        self.average_contentment_Zuid = neighbourhood_contentments[6]
        self.average_house_price_Centrum = neighbourhood_prices[0]
        self.average_house_price_Oost = neighbourhood_prices[1]
        self.average_house_price_NieuwWest = neighbourhood_prices[2]
        self.average_house_price_Zuidoost = neighbourhood_prices[3]
        self.average_house_price_Noord = neighbourhood_prices[4]
        self.average_house_price_West = neighbourhood_prices[5]
        self.average_house_price_Zuid = neighbourhood_prices[6]
        self.average_contentment = np.mean(neighbourhood_contentments)
        self.average_house_price = np.mean(neighbourhood_prices)


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
        print("House Seekers                " + str(self.house_seekers))
        print("Fraction Unhappy/Happy:      " + str(self.house_seekers/self.population_size) 
                + " / " + str((self.population_size-self.house_seekers)/self.population_size))
        print("Number of Houses:            " + str(self.amount_of_houses))
        print("Number of Empty Houses:      " + str(self.amount_of_houses_empty))
        print("Number of People:            " + str(self.amount_of_people))
        print("Number of Homeless:          " + str(self.amount_of_people_homeless))

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
        print("Deals:                       " + str(np.mean(self.deals)))
        print("Total Wealth:                " + str(self.total_wealth))
        print("Average Disposable Money:    " + str(self.average_cash))
        print("Average Contentment          " + str(self.average_contentment))
        print("Average House Price          " + str(self.average_house_price))
        print("House Seekers                " + str(self.house_seekers))
        print("Fraction Unhappy/Happy:      " + str(self.house_seekers/self.population_size) 
                + " / " + str((self.population_size-self.house_seekers)/self.population_size))
        print("Number of Houses:            " + str(self.amount_of_houses))
        print("Number of Empty Houses:      " + str(self.amount_of_houses_empty))
        print("Number of People:            " + str(self.amount_of_people))
        print("Number of Homeless:          " + str(self.amount_of_people_homeless))

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

    def auction_swap(self, s1, s2):
        """
        Performs the swap of cash, neighbourhoods, and houses between two agents.

        Args:
            s1: First Person agent.
            s2: Second Person agent.
        """

        # Detrmine price of houses (**2 just to amplify change)
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
        """
        
        # Find all agents that are willing to sell and trade
        sellers = [person for person in self.get_agents(Person) if person.seeking and person.house is not None]
        random.shuffle(sellers)

        # Temporary variable to keep track of number of deals
        tmp_deals = 0
        
        # Match two sellers if contentment imporves and they can afford the house
        for s1 in sellers:
            matches = {}
            for s2 in sellers:
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
                tmp_deals += 1
                s1.neighbourhood.moves += 1
                top_match.neighbourhood.moves += 1

                # Remove both agents from the list of sellers
                sellers.remove(s1)
                sellers.remove(top_match)

        # Update number of deals statistic
        self.deals = tmp_deals

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
        Sells empty houses to the highest bidder.
        """
        
        # Find all house seekers and empty houses
        empty_houses = [house for house in self.get_agents(House) if house.owner == None]
        house_seekers = [person for person in self.get_agents(Person) if person.seeking]

        # Check if there are any empty houses or house seekers
        if len(empty_houses) == 0 or len(house_seekers) == 0: return

        # Shuffle the lists
        random.shuffle(empty_houses)
        random.shuffle(house_seekers)

        # Temporary variable to keep track of number of deals
        tmp_deals = 0
        # Match house seekers with empty houses
        for house in empty_houses:
            for seeker in house_seekers:
                # Check if seeker already owns a house
                if seeker.house:
                    new_contentment = seeker.calculate_contentment(house.neighbourhood, house)
                    # If seeker is happy with the new house and can afford it, move in
                    if new_contentment > seeker.contentment:
                        if seeker.cash + seeker.house.price > house.price:
                            self.movein_empty(seeker, house)
                            tmp_deals += 1
                            break   # Go to next avalible house
                else:
                    # If seeker (from outside Amsterdam) can afford the house, move in
                    if seeker.cash > house.price:
                        self.movein_empty(seeker, house)
                        tmp_deals += 1
                        break   # Go to next avalible house
        
        # Update number of deals statistic
        self.deals += tmp_deals

    def grow_population(self):
        """
        Grows the population size and adds new Person agents to the model.
        """

        # Calculate number of new agents
        new_agents = int(self.population_size * self.population_growth_rate) - self.population_size
        
        # Update population size
        self.population_size += new_agents

        # Add new agents
        for i in range(0, new_agents):
            person = Person(unique_id="NewPerson_"+str(self.population_size+i), 
                            model=self, 
                            living_location=None)
            person.cash = self.start_money_multiplier_newcomers * person.cash     # Newcomers are supposed to get more money as they come, because they don't own a house
            self.schedule.add(person)

    def update_average_neighbourhood_price(self, neighbourhoods):
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
                price_sum += house.price
                houses_num += 1
            neighbourhood.average_neighbourhood_price = price_sum / houses_num

    def update_average_neighbourhood_contentment(self, neighbourhoods):
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
            contentment_sum = 0
            people_num = 0
            
            # Calculate new average price for each neighbourhood
            for house in neighbourhood.houses:
                if house.owner != None: person = house.owner
                contentment_sum += person.contentment
                people_num += 1
            neighbourhood.average_neighbourhood_contentment = contentment_sum / people_num


    def update_statistics(self):
        """
        Updates statistics for the model.
        
        Args:
            agents: List of all agents in the model.
        """

        self.update_model_params()

        self.update_average_neighbourhood_price(self.get_agents(Neighbourhood))
        self.update_average_neighbourhood_contentment(self.get_agents(Neighbourhood))
        
    # IS DISABLED FOR NOW
    def equilibrium(self):
        """Checks if the model has reached equilibrium."""
        
        # Check if there are no more deals
        if self.deals == 0:          # Is disabled, because now that we have growth new deals might always happen
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

        # Updating statistics and collecting data
        self.update_statistics()
        self.datacollector.collect(self)

        print("\n")
        if self.print_statistics: self.print_stats()

        # Check if model has reached equilibrium
        self.equilibrium()

        # Just checking if agents are still follow desired distribution, used for debug
        #print("Neigh: ", np.mean(keeper_neigh), np.std(keeper_neigh))
        #print("Money: ", np.mean(keeper_money), np.std(keeper_money))

        return
