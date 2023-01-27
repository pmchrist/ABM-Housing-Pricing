import random

import mesa
import mesa_geo as mg

class Person(mesa.Agent):
    """
    Agent representing a person on the housing market of the city.
    """

    def __init__(self, unique_id: int, model: mesa.Model, weight_1: float, weight_2: float, money_loving: float, starting_money: int, living_location: mg.GeoAgent):
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

        self.weight_1 = weight_1
        self.weight_2 = weight_2
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
        H = neighbourhood.param_1 * self.weight_1 + neighbourhood.param_2 * self.weight_2
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
        self.cash = self.cash - self.neighbourhood.cost_of_living
        self.cash = self.cash + self.neighbourhood.avarage_salary

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
        self.moves = 0
        self.capacity = None
        self.param_1 = None
        self.param_2 = None
        self.avarage_salary = None
        self.cost_of_living = None
        self.average_house_price_history = []
        self.houses = []

    def growth(self):
        """
        Gradually increses attributes of neigbouhood.
        """
        
        self.avarage_salary = self.avarage_salary * 1.01
        self.cost_of_living =  self.cost_of_living * 1.01

        # DO WE GRADUALLY INCREASE CAPACITY OF THE NEIGHBOURHOOD?
        # self.capacity = self.capacity * 1.01

    def noise(self):
        """
        Add stochastic noise to param_1 and params_2.
        """

        sigma = self.model.noise
        self.param_1 = self.param_1 + random.uniform(-sigma, sigma)
        self.param_2 = self.param_2 + random.uniform(-sigma, sigma)

    def step(self):
        """
        Advance neighbourhood one step.
        """

        self.growth()
        self.noise()


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
        self.price_history = [initial_price]
        self.owner = owner

        # Assign house to Person agent
        owner.house = self

        # Assign house to Neighbourhood agent
        self.neighbourhood.houses.append(self)

    def inflation(self):
        """
        Gradually increases the price of the house.
        """

        self.price_history[-1] = self.price_history[-1] * 1.01

    def step(self):
        """
        Advance house one step.
        """

        self.inflation()
    