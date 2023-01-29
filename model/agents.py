import random

import mesa
import mesa_geo as mg
from shapely.geometry import Point

class Person(mesa.Agent):
    """
    Agent representing a person on the housing market of the city.
    """

    def __init__(self, unique_id: int, model: mesa.Model, weight_house: float, weight_shops: float, weight_crime: float, weight_nature: float, weigth_money: float, starting_money: int, living_location: mg.GeoAgent):
        """Create a new agent (person) for the housing market.

        Args:
            unique_id: Unique identifier for the agent.
            model: Mesa model the agent is part of.
            weight_house: Weight for house loving.
            weight_shops: Weight for shops loving.
            weight_crime: Weight for crime loving.
            weight_nature: Weight for nature loving.
            weigth_money: Weight for money loving.
            starting_money: Initial amount of money the agent has.
            living_location: Initial living neighbourhood of the agent represented as a GeoAgent.
        """

        super().__init__(unique_id, model)

        # Weigths for utility function
        self.weight_house = weight_house
        self.weight_shops = weight_shops
        self.weight_crime = weight_crime
        self.weight_nature = weight_nature
        self.weigth_money = weigth_money

        # Money attributes
        self.cash = starting_money

        # Living attributes
        self.neighbourhood = living_location
        self.house = None
        
        # Contentment attributes (check if agent is initialized homeless)
        if living_location == None:
            self.contentment = 0
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
        if self.house == None and self.neighbourhood == None:
            contentment = 0
        else:
            # STILL NOT COMPLETELY CORRECT
            H = neighbourhood.housing_quality_index * self.weight_house + neighbourhood.shops_index * self.weight_shops + neighbourhood.crime_index * self.weight_crime + neighbourhood.nature_index * self.weight_nature
            # Use monetary value (how much it is worth) of a house in calculations too,
            # Also, use the income based on neighbourhood (neighbourhood.disposable_income)
            contentment = (H ** (1 - self.weigth_money)) * (self.cash ** self.weigth_money)
            # TEMPORARY FIX FOR THE COMPLEX NUMBER BUG
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
            self.contentment = 0
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
        self.average_neighbourhood_price = 0
        self.houses = []

        # Tracked statistics
        self.moves = 0
    
    def __repr__(self):
        """
        WHAT IS THIS CHRISTOS?
        """

        return f'Neighbourhood(name={self.unique_id}, capacity={self.capacity}, disposable_income={self.disposable_income}, housing_quality={self.housing_quality}, shops_index={self.shops_index}, crime_index={self.crime_index}, nature_index={self.nature_index})'

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

        # Assign house to Person agent
        if owner != None: owner.house = self

        # Assign house to Neighbourhood agent
        neighbourhood.houses.append(self)

    def step(self):
        """
        Advance house one step.
        """
        return
    