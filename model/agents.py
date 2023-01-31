import random
import numpy as np

import mesa
import mesa_geo as mg
from shapely.geometry import Point

class Person(mesa.Agent):
    """
    Agent representing a person on the housing market of the city.
    """

    def __init__(self, unique_id: int, model: mesa.Model, starting_money: int, house: mg.GeoAgent, living_location: mg.GeoAgent):
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
        # Weigths for utility function Money
        self.cash = starting_money
        money_weights =  np.random.dirichlet(np.ones(3))                # They have to add up to 1
        self.weight_cash = money_weights[0]
        self.weight_salary = money_weights[1]
        self.weight_house_value = money_weights[2]

        # Living attributes
        self.neighbourhood = living_location
        self.house = house

        # Contentment attributes (check if agent is initialized homeless)
        if self.neighbourhood == None and self.house == None:
            self.contentment = 0.5
            self.seeking = True
        else:
            self.contentment = self.calculate_contentment(self.neighbourhood)
            self.seeking = self.get_seeking_status() 

    def calculate_contentment(self, neighbourhood):
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

        # Check if agent is homeless
        if self.house == None or self.neighbourhood == None:
            contentment = 0.5
        else:
            # Neighbourhood Score
            neighbourhood_component = neighbourhood.housing_quality_index * self.weight_house + neighbourhood.shops_index * self.weight_shops + neighbourhood.crime_index * self.weight_crime + neighbourhood.nature_index * self.weight_nature
            # Net worth score, with normalization
            HOUSE_PRICE_RANGE = 735034.8834
            HOUSE_PRICE_MIN = 167744.5583
            INCOME_RANGE = 30961.77118
            INCOME_MIN = 25119.11441
            cash_div = self.neighbourhood.disposable_income * self.model.start_money_multiplier * 5     # param for cash normalization which depends on income of neighbourhood of living
            money_component = (self.weight_salary * (self.neighbourhood.disposable_income - INCOME_MIN)/INCOME_RANGE + 
            self.weight_house_value * (self.house.price - HOUSE_PRICE_MIN)/HOUSE_PRICE_RANGE + self.weight_cash * self.cash/cash_div)
            if money_component < 0:
                print("weight_salary", self.weight_salary * (self.neighbourhood.disposable_income - INCOME_MIN)/INCOME_RANGE)
                print("weight_house_value", (self.house.price - HOUSE_PRICE_MIN)/HOUSE_PRICE_RANGE)
                print("weight_cash", self.weight_cash * self.cash/cash_div)
                print("\n")
            # Composite score
            #print("Neighbourhood Contentment Component: ", neighbourhood_component)
            #print("Money Contentment Component: ", money_component)
            #print("\n")
            contentment = neighbourhood_component ** (1.0 - self.weight_materialistic) + money_component ** (self.weight_materialistic)
            # Fix for complex number bug
            if isinstance(contentment, complex):
                contentment = contentment.real

        return contentment

    # This function is used only for calculation of the house price, as it depends only on environment quality
    def calculate_contentment_for_house(self, neighbourhood):
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

        # Check if agent is homeless
        if self.house == None or self.neighbourhood == None:
            contentment = 0.5
        else:
            # Neighbourhood Score
            contentment = neighbourhood.housing_quality_index * self.weight_house + neighbourhood.shops_index * self.weight_shops + neighbourhood.crime_index * self.weight_crime + neighbourhood.nature_index * self.weight_nature
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

    def update_attributes(self):
        """
        Updates the agents attributes after every step.
        """

        # Check if agent is homeless
        if self.house == None and self.neighbourhood == None:
            # Update Contentment and seeking status
            self.contentment = 0.5
            self.seeking = True
            # Update net income based on neighbourhood
            self.cash += random.randint(min([neighbourhood.disposable_income for neighbourhood in self.model.get_agents(Neighbourhood)]), max([neighbourhood.disposable_income for neighbourhood in self.model.get_agents(Neighbourhood)]))
        else:
            self.contentment = self.calculate_contentment(self.neighbourhood)
            self.seeking = self.get_seeking_status()
            self.cash += self.neighbourhood.disposable_income   

    # Currently only finding contentment, based on 2 parameters
    def step(self):
        """
        Advance Person agent one step.
        """

        # Update Agent's net income and Contentment
        self.update_attributes()


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
                housing_growth_rate: Housing growth rate of this neighbourhood.
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

        # Neighbourhood attributes
        self.capacity = None
        self.housing_growth_rate = None
        self.disposable_income = None
        self.average_neighbourhood_price = None
        self.houses = []

        # Tracked statistics
        self.moves = 0
    
    def __repr__(self):
        """
        Tjhis function outputs object as a string
        """

        return f'Neighbourhood(name={self.unique_id}, capacity={self.capacity}, disposable_income={self.disposable_income}, housing_quality_index={self.housing_quality_index}, shops_index={self.shops_index}, crime_index={self.crime_index}, nature_index={self.nature_index})'

    def add_houses(self, amount):
        """
        Adds houses to the neighbourhood.

        Args:
            amount: Amount of houses to add.
        """
        
        # Add new houses to the neighbourhood
        for i in range(1, amount):
            house = House(  unique_id=self.unique_id+"_NewHouse_"+str(self.capacity+i),
                            model=self.model,
                            crs=self.crs,
                            geometry=self.random_point(),
                            neighbourhood=self, 
                            initial_price=self.average_neighbourhood_price,
                            owner=None)
            self.model.schedule.add(house)
            self.model.space.add_agents(house)

    def growth(self):
        """
        Gradually increses the capacity of the neighbourhood, and adds houses to it.
        """

        self.capacity = int(self.capacity * self.housing_growth_rate)

        new_houses = self.capacity - len(self.houses)

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
        self.shops_index = self.shops_index + random.uniform(-sigma, sigma)
        self.crime_index = self.crime_index + random.uniform(-sigma, sigma)
        self.nature_index = self.nature_index + random.uniform(-sigma, sigma)

    def random_point(self):
        """
        Get random location for house in neighbourhood
        """

        min_x, min_y, max_x, max_y = self.geometry.bounds
        while not self.geometry.contains(
            random_point := Point(
                random.uniform(min_x, max_x), random.uniform(min_y, max_y)
            )
        ):
            continue
        return random_point

    def step(self):
        """
        Advance neighbourhood one step.
        """

        # Update neighbourhood parameters
        self.noise()
        # Add new houses to the neighbourhood
        self.growth()

        # Reset variables
        price_sum = 0
        houses_num = 0
        
        # Calculate new average price for each neighbourhood
        for house in self.houses:
            price_sum += house.price
            houses_num += 1
        self.average_neighbourhood_price = price_sum / houses_num

        print("\n")
        print(self.unique_id,": " , self.average_neighbourhood_price)

        return


class House(mg.GeoAgent):
    """
    GeoAgent representing a house in a neighbourhood.
    """
    
    def __init__(self, unique_id: int, model: mesa.Model, neighbourhood: Neighbourhood, initial_price: int, geometry, crs):
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
        self.owner = None

        # Assign house to Person agent
        #if owner != None: owner.house = self        # HOW DOES HOUSE OWNS ITSELF???

        # Assign house to Neighbourhood agent
        neighbourhood.houses.append(self)

    def step(self):
        """
        Advance house one step.
        """
        return
    