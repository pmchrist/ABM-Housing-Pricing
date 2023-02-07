import random
import numpy as np

import mesa
import mesa_geo as mg
from shapely.geometry import Point

# Stable Variables througout simulation
HOUSE_PRICE_MEAN = 543204       # Comes from Data
INCOME_MEAN = 68238             # Comes from Data/Distribution

class Person(mesa.Agent):
    """
    Agent representing a person on the housing market of the city.
    """

    def __init__(self, unique_id: int, model: mesa.Model, living_location: mg.GeoAgent):
        """Create a new agent (person) for the housing market.

        Args:
            unique_id: Unique identifier for the agent.
            model: Mesa model the agent is part of.
            weight_house: Weight for house loving.
            weight_shops: Weight for shops loving.
            weight_crime: Weight for crime loving.
            weight_nature: Weight for nature loving.
            starting_money: Initial amount of money the agent has.
            living_location: Initial living neighbourhood of the agent represented as a GeoAgent.
        """

        super().__init__(unique_id, model)

        # Main param for Utility function
        self.weight_materialistic = model.weight_materialistic          # How much net worth affects person's happiness
        # Weigths for utility function Neighbourhood
        neighbourhood_weights =  np.random.dirichlet(np.ones(4))        # They have to add up to 1
        self.weight_house = neighbourhood_weights[0]
        self.weight_shops = neighbourhood_weights[1]
        self.weight_crime = neighbourhood_weights[2]
        self.weight_nature = neighbourhood_weights[3]
        # Params for wealth evaluation
        self.salary = np.random.lognormal(11.130763621035388, 0.42361311973300236)                # Getting salary from overall distribution
        self.cash = self.model.start_money_multiplier * INCOME_MEAN
        # Weigths for utility function Money
        money_weights =  np.random.dirichlet(np.ones(3))                # They have to add up to 1
        self.weight_cash = money_weights[0]
        self.weight_salary = money_weights[1]
        self.weight_house_value = money_weights[2]
        # Living attributes
        self.neighbourhood = living_location
        self.house = None
        # Values we keep an eye on
        self.contentment = None
        self.seeking = None

    def calculate_contentment(self, neighbourhood, house):
        """
        Calculates the contentness of the agent based on a given neighbourhood.
        This score is a derrivation of the Cobb-Douglas utility function.
        
        Formula: U = H ** a * M ** b
        H: House contentness
        M: Amount of cash
        a: Weight for house loving
        b: Weight for money loving
        
        Args:
            neighbourhood: The neighbourhood you want to calculate an agent's contentness for.
        """

        # Parameter which is static but depends on model, so we have to calculate it each time
        CASH_MEAN = (self.model.start_money_multiplier + 1) * INCOME_MEAN

        # Check if agent is homeless
        if house == None or neighbourhood == None:
            self.neighbourhood_component = 0
            contentment = 0.0
        else:
            # Neighbourhood Score, weights are already normalized
            neighbourhood_component_1 = neighbourhood.housing_quality_index * self.weight_house
            neighbourhood_component_2 = neighbourhood.shops_index * self.weight_shops
            neighbourhood_component_3 = neighbourhood.crime_index * self.weight_crime
            neighbourhood_component_4 = neighbourhood.nature_index * self.weight_nature
            self.neighbourhood_component = neighbourhood_component_1 + neighbourhood_component_2 + neighbourhood_component_3 + neighbourhood_component_4
            # Wealth Score, with Normalization
            # All money params follow the non linear diminishing utility function. Salary&Cash: 0.6*x^0.4, House: 0.4*x^0.6
            wealth_component_1 = self.weight_house  * 0.4*(house.price / HOUSE_PRICE_MEAN)**0.6           # House price mean comes from Dataset, and is Init value
            wealth_component_2 = self.weight_salary * 0.6*(self.salary / INCOME_MEAN)**0.4                # Salary mean comes from distribution
            wealth_component_3 = self.weight_cash   * 0.6*(self.cash   / CASH_MEAN)**0.4                  # Cash Mean comes from Init_Model_Coeff*Mean_Salary, and is Init value
            money_component = wealth_component_1 + wealth_component_2 + wealth_component_3
            contentment = self.neighbourhood_component ** (1.0 - self.weight_materialistic) * money_component ** (self.weight_materialistic)
        # Fix for complex number bug
        if isinstance(contentment, complex):
            contentment = contentment.real

        return contentment

    def get_seeking_status(self):
        """
        Updates the house seeking status of the agent.
        """

        if self.contentment < self.model.contentment_threshold:
            return True
        else:
            return False

    # Used to update values in the beginning, based on the fact the person got a house
    def update_contentment_seeking(self):
        self.contentment = self.calculate_contentment(self.neighbourhood, self.house)
        self.seeking = self.get_seeking_status() 

    def update_attributes(self):
        """
        Updates the agents attributes after every step.
        """

        # Check if agent is lives outside of Amsterdam
        if self.house == None or self.neighbourhood == None:
            # Update Cash, Contentment and seeking status
            self.cash += self.salary
            self.contentment = self.calculate_contentment(None, None)
            self.seeking = True
        # If is already in Amsterdam
        else:
            self.cash += self.salary - self.neighbourhood.expenses
            # If bankrupt
            if self.cash < 0:     # He is bunkrupt
                self.seeking = True
                self.cash = 0               # Reset Net Worth
                self.contentment = 0.0      # Happiness penalty
                self.house.owner = None
                self.cash += self.house.price/2                 # He has to sell for half a price to survive
                self.house = None
            elif self.cash < 3*self.neighbourhood.expenses:    # Available money is less than tripple cost of annual living
                self.contentment = self.contentment*(self.cash/(3*self.neighbourhood.expenses))        # Happiness penalty
            self.contentment = self.calculate_contentment(self.neighbourhood, self.house)
            self.seeking = self.get_seeking_status()

    # Currently only finding contentment, based on 2 parameters
    def step(self):
        """
        Advance Person agent one step.
        """

        # Update Agent's net income and Contentment
        self.update_attributes()

        return

class Neighbourhood(mg.GeoAgent):
    """
    GeoAgent representing a neighbourhood in the city.
    """

    def __init__(self, unique_id: str, model: mesa.Model, geometry, crs):
        """
        Create a new neighbourhood.
        
        Args:
            unique_id: Unique identifier for the agent, or neigbourhood name.
            model: Mesa model the agent is part of.
            geometry: GeoJSON geometry object.
            crs: Coordinate reference system.

            Attributes:
                housing_quality_index: Housing quality index of this neighbourhood.
                shops_index: Shops index of this neighbourhood.
                crime_index: Crime index of this neighbourhood.
                nature_index: Nature index of this neighbourhood.
                capacity: Max amount of houses in this neighbourhood.
                disposable_income: Net average income of this neighbourhood.
                average_house_price_history: Average house price in this neighbourhood.
                houses: List of houses in this neighbourhood.
                moves: Amount of traded houses in this neighbourhood.
        """

        super().__init__(unique_id, model, geometry, crs)

        # Neighbourhood parameters
        self.housing_quality_index = None
        self.shops_index = None
        self.crime_index = None
        self.nature_index = None
        self.expenses = None
        self.houses = []

        # Tracked statistics
        # Neighbourhood Values
        self.capacity = None                                # amount_of_houses
        self.empty_houses = None                            # amount_of_empty_houses
        self.move_in = 0                                    # Movements
        self.move_out = 0
        # Values derived from Citizens (Person)
        self.average_contentment = None                     # contentment
        self.average_neighbourhood_component= None          # average_neighbourhood_component
        self.average_house_price = None                     # average_house_price
        self.average_salaries = None                        # average_salaries
        self.average_cash = None                            # average_cash

    def add_houses(self, amount):
        """
        Adds houses to the neighbourhood.

        Args:
            amount: Amount of houses to add.
        """
        
        # Add new houses to the neighbourhood
        for i in range(0, amount):
            house = House(  unique_id=self.unique_id+"_NewHouse_"+str(self.capacity+i),
                            model=self.model,
                            neighbourhood=self, 
                            initial_price=self.average_neighbourhood_price,
                            owner=None,
                            crs=self.crs,
                            geometry=self.random_point())
            self.model.schedule.add(house)
            self.model.space.add_agents(house)

    def growth(self):
        """
        Gradually increses the capacity of the neighbourhood, and adds houses to it.
        """

        # Assign new capacity
        self.capacity = int(self.capacity * self.model.housing_growth_rate)

        # Calculate number of new houses
        new_houses = self.capacity - len(self.houses)

        # If there is space for new houses, add them
        if new_houses > 0:
            self.add_houses(new_houses)

    def noise(self):
        """
        Adds stochastic noise to the neighbourhood's parameters.
        """

        # Noise term
        sigma = self.model.noise

        # Add noise to neighbourhood parameters
        self.housing_quality_index = self.housing_quality_index + random.uniform(-sigma, sigma)
        if self.housing_quality_index < 0: self.housing_quality_index = 0
        self.shops_index = self.shops_index + random.uniform(-sigma, sigma)
        if self.shops_index < 0: self.shops_index = 0
        self.crime_index = self.crime_index + random.uniform(-sigma, sigma)
        if self.crime_index < 0: self.crime_index = 0
        self.nature_index = self.nature_index + random.uniform(-sigma, sigma)
        if self.nature_index < 0: self.nature_index = 0

    def random_point(self):
        """
        Get random location for house's visualization in neighbourhood
        """

        min_x, min_y, max_x, max_y = self.geometry.bounds
        while not self.geometry.contains(
            random_point := Point(
                random.uniform(min_x, max_x), random.uniform(min_y, max_y)
            )
        ):
            continue
        return random_point

    def __repr__(self):
        """
        This function outputs object as a string
        """

        return f'Neighbourhood(name={self.unique_id}, capacity={self.capacity}, housing_quality_index={self.housing_quality_index}, shops_index={self.shops_index}, crime_index={self.crime_index}, nature_index={self.nature_index})'

    def update_stats(self):

        # Create target variables
        locals_contentment = []
        locals_neighbourhood_component = []
        housing_prices = []
        locals_salaries = []
        locals_cash = []

        # Calculate new stats for neighbourhood
        self.capacity = len(self.houses)
        self.empty_houses = 0
        for house in self.houses:
            # House Related Values:
            housing_prices.append(house.price)
            if house.owner == None:
                self.empty_houses += 1           
            else:
                # Person Related Values:
                person = house.owner
                locals_contentment.append(person.contentment)
                locals_neighbourhood_component.append(person.neighbourhood_component)
                locals_salaries.append(person.salary)
                locals_cash.append(person.cash)

        # Update final stats
        self.average_contentment = np.mean(locals_contentment)
        self.average_neighbourhood_component = np.mean(locals_neighbourhood_component)
        self.average_house_price = np.mean(housing_prices)
        self.average_salaries = np.mean(locals_salaries)
        self.average_cash = np.mean(locals_cash)

    def step(self):
        """
        Advance neighbourhood one step.
        """

        # Update neighbourhood parameters
        if self.model.noise > 0.0: self.noise()
        # Add new houses to the neighbourhood
        self.growth()
        # Update statistics 
        self.update_stats()        
        
        return

class House(mg.GeoAgent):
    """
    GeoAgent representing a house in a neighbourhood.
    """
    
    def __init__(self, unique_id: int, model: mesa.Model, neighbourhood: Neighbourhood, initial_price: int, owner: Person, geometry, crs):
        """
        Create a new house.
        
        Args:
            unique_id: Unique identifier for the agent.
            model: Mesa model the agent is part of.
            neighbourhood: Neighbourhood the house is located in.
            initial_price: Initial price of the house.
            owner: Initial owner of the house.
            geometry: GeoJSON geometry object.
            crs: Coordinate reference system.
        
        """

        super().__init__(unique_id, model, geometry, crs)

        # House attributes
        self.neighbourhood = neighbourhood
        self.price = initial_price
        self.owner = owner

        # Assign house to Neighbourhood agent
        neighbourhood.houses.append(self)

    def step(self):
        """
        Advance house one step.
        """

        return
    