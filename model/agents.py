import random

import mesa
import mesa_geo as mg

class Person(mesa.Agent):
    """
    Agent representing a person on the housing market of the city.
    """

    def __init__(self, unique_id: int, model: mesa.Model, weight_house: float, weight_shops: float, weight_crime: float, weight_nature: float, money_loving: float, starting_money: int, living_location: mg.GeoAgent):
        """Create a new agent (person) for the housing market.

        Args:
            unique_id: Unique identifier for the agent.
            model: Mesa model the agent is part of.
            weight_1: Weight representing an agents preference for Contentness function.
            weight_2: A second weight representing an agents preference.
            starting_money: Initial amount of money the agent has.
            living_location: Initial living neighbourhood of the agent represented as a GeoAgent.
            contentness_threshold: Threshold for agent to start selling the house.
        """

        super().__init__(unique_id, model)

        self.weight_house = weight_house
        self.weight_shops = weight_shops
        self.weight_crime = weight_crime
        self.weight_nature = weight_nature
        self.money_loving = money_loving
        self.cash = starting_money
        self.neighbourhood = living_location
        self.contentment = self.calculate_contentment(self.neighbourhood)
        self.selling = self.get_selling_status()
        self.house = None

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

        # STILL NOT COMPLETELY CORRECT
        H = neighbourhood.housing_quality * self.weight_house + neighbourhood.shops_index * self.weight_shops + neighbourhood.crime_index * self.weight_crime + neighbourhood.nature_index * self.weight_nature
        # Use monetary value (how much it is worth) of a house in calculations too,
        # Also, use the income based on neighbourhood (neighbourhood.disposable_income)
        contentment = (H ** (1 - self.money_loving)) * (self.cash ** self.money_loving)

        return contentment

    def get_selling_status(self):
        """
        Updates the house selling status of the agent.
        """

        if self.contentment < self.model.contentment_threshold:
            return True
        else:
            return False

    def update_attributes(self):
        """
        Updates the agents attributes after every step.
        """

        # Update net income based on neighbourhood.
        self.cash = self.cash + self.neighbourhood.disposable_income

        # Update Contentment and Selling status
        self.contentment = self.calculate_contentment(self.neighbourhood)
        self.selling = self.get_selling_status()     # Depends on Contentment

        # Decreasing gradually to reflect boredom from neighbourhood
        #self.weight_1 = self.weight_1 * .95 # If we use these params in the final verson, we should also reset them after each move
        #self.weight_2 = self.weight_2 * .95

    # Currently only finding contentment, based on 2 parameters
    def step(self):
        """
        Advance agent one step.
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
                moves: Amount of traded houses in this neighbourhood.
                capacity: Max amount of houses in this neighbourhood.
                param_1: Some parameter for contentness function.
                param_2: Some parameter for contentness function.
                salary: Average salary in this neighbourhood.
                cost_of_living: Average cost of living in this neighbourhood.
                average_house_price_history: List of average house prices in this neighbourhood.
                houses: List of houses in this neighbourhood.
        """

        super().__init__(unique_id, model, geometry, crs)

        # Parameters that are fixed
        self.capacity = None
        self.disposable_income = None
        self.housing_quality = None
        self.shops_index = None
        self.crime_index = None
        self.nature_index = None

        # Parameters that are we tracking in the simulation
        self.moves = 0
        self.average_neighbourhood_price = 0
        # House_id_s
        self.houses = []
    
    def __repr__(self):
        return f'Neighbourhood(name={self.unique_id}, capacity={self.capacity}, disposable_income={self.disposable_income}, housing_quality={self.housing_quality}, shops_index={self.shops_index}, crime_index={self.crime_index}, nature_index={self.nature_index})'

    def growth(self):
        """
        Gradually increses attributes of neigbouhood.
        """
        # Should we do anything?
        # self.capacity = self.capacity * 1.01
        # self.disposable_income = self.disposable_income * 1.01

    def noise(self):
        """
        Add stochastic noise to init params
        """
        sigma = self.model.noise

        self.housing_quality = self.housing_quality + random.uniform(-sigma, sigma)
        self.shops_index = self.shops_index + random.uniform(-sigma, sigma)
        self.crime_index = self.crime_index + random.uniform(-sigma, sigma)
        self.nature_index = self.nature_index + random.uniform(-sigma, sigma)

    def step(self):
        """
        Advance neighbourhood one step.
        """

        #self.growth()
        #self.noise()

    


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
            price: Price of the house.
            owner: Owner of the house.
            is_red: Boolean indicating if the house is red or not.
            geometry: GeoJSON geometry object.
            crs: Coordinate reference system.
        
        """

        super().__init__(unique_id, model, geometry, crs)

        self.neighbourhood = neighbourhood
        self.price = initial_price
        self.owner = owner

        # Assign house to Person agent
        owner.house = self

        # Assign house to Neighbourhood agent
        self.neighbourhood.houses.append(self)

    def inflation(self):
        """
        Gradually increases the price of the house.
        """

        self.price = self.price * 1.01

    def step(self):
        """
        Advance house one step.
        """

        self.inflation()
    