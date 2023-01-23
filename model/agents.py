import random
import mesa
import mesa_geo as mg

class Person(mesa.Agent):
    """
    Agent representing a person on the housing market of the city.
    """

    def __init__(self, unique_id: int, model: mesa.Model, weight_1: float, weight_2: float, starting_money: int, living_location: mg.GeoAgent, contentment_threshold=0.4):
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

        # Parameters that are fixed and assigned on init of agent.
        self.weight_1 = weight_1
        self.weight_2 = weight_2

        # Parameters that depend on the neighbourhood and are assigned on init of neighbourhood.
        self.cash = starting_money
        self.neighbourhood = living_location
        self.contentment_threshold = contentment_threshold

        # Parameters that are dynamic and re-calculated on each step().
        self.contentment = self.calculate_contentment(self.neighbourhood)
        self.selling = self.get_selling_status()

    def calculate_contentment(self, neighbourhood):
        """Updates the contentness score of the agent."""
        # THIS IS A TEST FORMULA, SHOULD BE BASED ON NEIGHBOURHOOD DATA
        return self.weight_1 * neighbourhood.param_1 + self.weight_2 * neighbourhood.param_2

    def get_selling_status(self):
        """Updates the house selling status of the agent."""

        if self.contentment < self.contentment_threshold:
            return True
        else:
            return False

    def update_attributes(self):
        """Updates the agents attributes after every step."""
        # Decreasing gradually to reflect boredom from neighbourhood
        #self.weight_1 = self.weight_1 * .95 # If we use these params in the final verson, we should also reset them after each move
        #self.weight_2 = self.weight_2 * .95

        # Update net income based on neighbourhood.
        self.cash = self.cash - self.neighbourhood.cost_of_living
        self.cash = self.cash + self.neighbourhood.salary

        # Update Contentment and Selling status
        self.contentment = self.calculate_contentment(self.neighbourhood)
        self.selling = self.get_selling_status()     # Depends on Contentment

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
        """Create a new neighbourhood.
        
        Args:
            unique_id: Unique identifier for the agent, or neigbourhood name.
            model: Mesa model the agent is part of.
            geometry: GeoJSON geometry object.
            crs: Coordinate reference system.
        """

        super().__init__(unique_id, model, geometry, crs)
        self.moves = 0 # amount of traded houses in this neighbourhood
        self.capacity = None # max amount of houses in this neighbourhood
        self.param_1 = None # some parameter for contentness function
        self.param_2 = None # some parameter for contentness function
        self.salary = None # average salary in this neighbourhood
        self.cost_of_living = None # average cost of living in this neighbourhood
        self.average_house_price = None # average house price in this neighbourhood

    def growth(self):
        """Gradually increses attributes of neigbouhood."""
        
        self.salary = self.salary * 1.01
        self.cost_of_living =  self.cost_of_living * 1.01

        # I think these should be recalculated and determined by the house class
        # self.average_house_price = self.average_house_price * 1.01
        # self.capacity = self.capacity * 1.01

    def noise(self):
        """Add stochastic noise to param_1 and params_2."""

        sigma = 0.0
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
    # I THINK WE NEED INCLUDE GEOMETRY AND CRS IN FINAL VERSION FOR VISUALISATION
    def __init__(self, unique_id: int, model: mesa.Model, neighbourhood: Neighbourhood, price: int, owner: Person, geometry, crs):
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
        self.price = price
        self.owner = owner
        # self.is_red = None # attribute determining the color of the house

    def inflation(self):
        """Gradually increases the price of the house."""

        self.price = self.price * 1.01

    def step(self):
        """
        Advance house one step.
        """
        self.inflation()
    