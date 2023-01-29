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

    def __init__(self, num_houses: int, noise: float, contentment_threshold: float, weigth_money: float, housing_growth_rate: float, population_growth_rate: float):
        """
        Create a model for the housing market.

        Args:
            num_houses: Number of houses in the model, as a fraction of the total number of houses in Amsterdam.
            noise: Noise term added to the parameters of a neighbourhood.
            contentment_threshold: Threshold for agent to start looking for a new house.
            weigth_money: The weight of money in the contentment function.
            housing_growth_rate: The rate at which the number of houses in the model grows.
            population_growth_rate: The rate at which the number of people in the model grows.

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

        # Model parameters
        self.num_houses = num_houses
        self.noise = noise
        self.contentment_threshold = contentment_threshold
        self.weigth_money = weigth_money
        self.housing_growth_rate = housing_growth_rate
        self.population_growth_rate = population_growth_rate
        
        # Tracked statistics
        self.population_size = 0
        self.average_contentment = 0
        self.average_cash = 0
        self.average_house_price = 0
        self.deals = 0
        self.house_seekers = 0

        # Model components
        self.schedule = mesa.time.RandomActivationByType(self)
        self.space = mg.GeoSpace(warn_crs_conversion=False)
        self.datacollector = mesa.DataCollector({"Deals": "deals", "Average Contentment": "average_contentment"})

        # Variable for stopping the model when equilibirum is reached.
        self.running = True

        # Set up the model
        self.setup_environment()

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
            neighbourhoods[i].disposable_income = gemente_data.neighbourhood_households_disposable_income[i]
            neighbourhoods[i].average_neighbourhood_price = sum(gemente_data.target_neighbourhood_houses_price)/len(gemente_data.target_neighbourhood_houses_price)     # Average value of all neighbourhoods is a baseline for the house price
            
            # Add Neighbourhood agent to the scheduler
            self.schedule.add(neighbourhoods[i])

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

        # Load real-world data
        gemente_data = data_loader

        # WEIGHTS ARE RANDOM ATM, AS IF THEY ARE FIXED NO EXCHANGES ARE HAPPENING
        # Add Person agent to the model
        person = Person(unique_id="Initial_Person_"+str(self.population_size+id), 
                        model=self, 
                        weight_house = random.random(), 
                        weight_shops = random.random(), 
                        weight_crime = random.random(), 
                        weight_nature = random.random(),
                        weigth_money = self.weigth_money,
                        # I JUST GAVE THEM A LOT OF MONEY IN THE BEGINNING TO WORK
                        starting_money=10*sum(gemente_data.neighbourhood_households_disposable_income)/len(gemente_data.neighbourhood_households_disposable_income),
                        living_location=neighbourhood)
        self.schedule.add(person)

        # Assign House to the model and add the Person agent as it's owner
        house = House(  unique_id="Initial_House_"+str(self.population_size+id),
                        model=self,
                        crs=neighbourhood.crs,
                        geometry=neighbourhood.random_point(),
                        neighbourhood=neighbourhood, 
                        initial_price=neighbourhood.average_neighbourhood_price,
                        owner=person)
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
            for i in range(1, neighbourhood.capacity):
                self.add_person_and_house(i, neighbourhood)

            # Update counter for People IDs
            self.population_size += neighbourhood.capacity
            
        # Collecting data   
        self.datacollector.collect(self)

        # Print initial parameters
        self.print_init() # DONT CALL THIS FOR SENSITIVITY ANALYSIS
    
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
        
        print("---------------------- INITIAL STATS ----------------------")
        print("Total Wealth:                " + str(np.mean([person.cash for person in self.get_agents(Person)]) * self.population_size))
        print("Average Wealth:              " + str(np.mean([person.cash for person in self.get_agents(Person)])))
        print("Average Contentment:         " + str(np.mean([person.contentment for person in self.get_agents(Person)])))
        print("Average House Price:         " + str(np.mean([house.price for house in self.get_agents(House)])))
        print("House-Seekers:               " + str(len([person for person in self.get_agents(Person) if person.seeking])))
        print("Fraction Unhappy/Happy:      " + str(len([person for person in self.get_agents(Person) if person.seeking])/self.population_size) 
                + " / " + str((self.population_size-len([person for person in self.get_agents(Person) if person.seeking]))/self.population_size))

        print("Number of Houses:            " + str(len([house for house in self.get_agents(House)])))
        print("Number of Empty Houses:      " + str(len([house for house in self.get_agents(House) if house.owner == None])))

        # Print a fun little house :)
        print("\n                                ~~   ")
        print("                               ~       ")
        print("                             _u__      ")
        print("                            /____\\    ")
        print("                            |[][]|     ")
        print("                            |[]..|     ")
        print("                            '--'''\n   ")

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

        # Determine new contentment scores
        new_s1_score = s1.calculate_contentment(s2.neighbourhood)
        new_s2_score = s2.calculate_contentment(s1.neighbourhood)
        s1.contentment = new_s1_score
        s2.contentment = new_s2_score

        # Detrmine price of houses
        # STILL NOT THE FINAL VERSION
        house1_price = (1 + new_s2_score - s2.contentment) * s1.house.price
        house2_price = (1 + new_s1_score - s1.contentment) * s2.house.price

        # Update House prices and history
        s1.house.price = house1_price
        s2.house.price = house2_price

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

        # Update seeking status
        s1.seeking = False
        s2.seeking = False

    def auction(self):
        """
        Performs trades between agents that are willing to sell and trade their house for another house.
        """
        
        # Find all agents that are willing to sell and trade
        sellers = [person for person in self.get_agents(Person) if person.seeking and person.house is not None]

        # Temporary variable to keep track of number of deals
        tmp_deals = 0
        
        # Match two sellers if contentment imporves and they can afford the house
        for s1 in sellers:
            matches = {}
            for s2 in sellers:
                if s1 != s2 and s1 is not None and s2 is not None:

                    # Calculate contentment for both parties in potential new neighbourhoods
                    new_s1_score = s1.calculate_contentment(s2.neighbourhood)
                    new_s2_score = s2.calculate_contentment(s1.neighbourhood)

                    # Check if both parties are happy with the deal
                    if new_s1_score > s1.contentment and new_s2_score > s2.contentment:
                        # Check if agents can afford the houses
                        if s1.cash + s1.house.price > s2.house.price and s2.cash + s2.house.price > s1.house.price:
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

        # MAYBE ADD SOMETHING TO CALCULATE PRICE OF HOUSES
        # Check if person already owns a house
        if person.house:
            # Update money spent
            person.cash -= house.price + person.house.price

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
            person.house.owner = person

    def sell_empty_houses(self):
        """
        Sells empty houses to the highest bidder.
        """
        
        # Find all house seekers and empty houses
        house_seekers = [person for person in self.get_agents(Person) if person.seeking]
        empty_houses = [house for house in self.get_agents(House) if house.owner == None]

        # Shuffle the lists
        random.shuffle(house_seekers)
        random.shuffle(empty_houses)

        # Temporary variable to keep track of number of deals
        tmp_deals = 0
        # Match house seekers with empty houses
        if len(house_seekers) > 0 and len(empty_houses) > 0:
            for seeker in house_seekers:
                for house in empty_houses:
                    
                    # Check if seeker already owns a house
                    if seeker.house:
                        new_contentment = seeker.calculate_contentment(house.neighbourhood)
                        # If seeker is happy with the new house and can afford it, move in
                        if new_contentment > seeker.contentment:
                            if seeker.cash + seeker.house.price > house.price:
                                self.movein_empty(seeker, house)
                                tmp_deals += 1
                    else:
                        # If homeless seeker can afford the house, move in
                        if seeker.cash > house.price:
                            self.movein_empty(seeker, house)
                            tmp_deals += 1
        
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
        for i in range(1, new_agents):
            person = Person(unique_id="NewPerson_"+str(self.population_size+i), 
                            model=self, 
                            weight_house = random.random(), 
                            weight_shops = random.random(), 
                            weight_crime = random.random(), 
                            weight_nature = random.random(),
                            weigth_money = self.weigth_money,
                            # I JUST GAVE THEM A LOT OF MONEY IN THE BEGINNING TO WORK
                            starting_money=random.randint(int(min([neighbourhood.average_neighbourhood_price for neighbourhood in self.get_agents(Neighbourhood)])), int(max([neighbourhood.average_neighbourhood_price for neighbourhood in self.get_agents(Neighbourhood)]))),
                            living_location=None)
            self.schedule.add(person)

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
                price_sum += house.price
                houses_num += 1
            neighbourhood.average_neighbourhood_price = price_sum / houses_num

    def update_statistics(self, agents):
        """
        Updates statistics for the model.
        
        Args:
            agents: List of all agents in the model.
        """

        # Recalculate average contentment
        # PROBABLY STD IS MORE INTERESTING THING TO VISUALIZE
        self.average_contentment = np.mean([person.contentment for person in self.get_agents(Person)])

        # Recalculate average house price of neighbourhoods
        self.update_average_house_price(self.get_agents(Neighbourhood))
        
        # Recalculate average house price of entire city
        self.average_house_price= np.mean([house.price for house in self.get_agents(House)]) 

        # Recalculate the average amount of cash in the city
        self.average_cash = np.mean([person.cash for person in self.get_agents(Person)])

        # Recalculate number of house seekers in the city
        self.house_seekers = len([person for person in self.get_agents(Person) if person.seeking])

    def equilibrium(self):
        """Checks if the model has reached equilibrium."""

        print(self.deals)
        # Check if there are no more deals
        if self.deals < 50: # THIS NOT A GOOD WAY TO CHECK FOR EQUILIBRIUM
            print("------------------- EQUILIBRIUM REACHED -------------------")
            print("After:                       " + str(self.schedule.steps) + " steps")
            print("----------------------- FINAL STATS -----------------------")
            print("Total Wealth:                " + str(self.average_cash * self.population_size))
            print("Average Wealth:              " + str(self.average_cash))
            # print("Average Deals:               " + str(np.mean(self.deals)))
            print("Average Contentment:         " + str(self.average_contentment))
            print("Average House Price:         " + str(self.average_house_price))
            print("House Seekers:               " + str(self.house_seekers))
            print("Fraction Unhappy/Happy:      " + str(self.house_seekers/self.population_size) + " / " + str((self.population_size-self.house_seekers)/self.population_size))
            
            print("Number of Houses:            " + str(len([house for house in self.get_agents(House)])))
            print("Number of Empty Houses:      " + str(len([house for house in self.get_agents(House) if house.owner == None])))
            print("Number of Homeless:          " + str(len([person for person in self.get_agents(Person) if person.house == None])))
           
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
        self.update_statistics(self.schedule.agents)
        self.datacollector.collect(self)
        
        # Check if model has reached equilibrium
        self.equilibrium() # SOMETHING WITH EQUILIBRIUM NOT WORKING

        return
