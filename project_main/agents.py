import random
import mesa
import mesa_geo as mg



# Agent for Person who gets a house and moves between areas
class Person(mesa.Agent):
    """Housing market agent (a Person living in the city)"""

    def __init__(self, unique_id: int, model: mesa.Model, weight_1: float, weight_2: float, starting_money: int, living_location: mg.GeoAgent):
        """Create a new agent (person) for the housing market.

        Args:
            unique_id: Unique identifier for the agent.
            weight_1: Weight for Contentness function.
            weight_2: Weight for Contentness function.
            starting_money: Initial amount of money the agent has.
            living_location: Current living neighbourhood of the agent.
            contentness_threshold: Threshold for agent to start selling the house.
        """
        
        super().__init__(unique_id, model)      # Weights for utility function
        # Parameters that depend only on the agent (are init on creation of a person)
        self.weight_1 = weight_1    # Weight for Contentment function
        self.weight_2 = weight_2    # Weight for Contentment function
        self.contentment_threshold = 0.4    # If contentment drops under, person wants to sell his house(0.4 is just for example)
        # Parameters that depend on the initial neighbourhood (are assigned on init of neighbourhood)
        self.cash = starting_money
        self.neighbourhood = living_location
        # Parameters that are dynamic and calculated on each step()
        self.contentment = self.calculate_contentment(self.neighbourhood)
        self.selling = self.get_selling_status()

    def calculate_contentment(self, neighbourhood):
        """Updates the contentness score of the agent."""

        return self.weight_1 * neighbourhood.param_1 + self.weight_2 * neighbourhood.param_2

    def get_selling_status(self):
        """Updates the house selling status of the agent."""

        if self.contentment < self.contentment_threshold:
            return True
        else:
            return False

    def update_attributes(self):
        """Updates the agents attributes after every step."""

        # .95 is a random number, should be based on neighbourhood data
        # If we use these params in the final verson, we should also reset them after each move
        #self.weight_1 = self.weight_1 * .95        # Decreasing gradually to reflect boredom from neighbourhood
        #self.weight_2 = self.weight_2 * .95        # Decreasing gradually to reflect boredom from neighbourhood
        self.cash = self.cash - self.neighbourhood.cost_of_living     # Decreasing money based on neighbourhood
        self.cash = self.cash + self.neighbourhood.salary             # Increasong money based on neighbourhood
        self.contentment = self.calculate_contentment(self.neighbourhood)
        self.selling = self.get_selling_status()     # Depends on Contentment

    # Currently only finding contentment, based on 2 parameters
    def step(self):
        """Advance agent one step."""

        # Update Agent's social status and Contentment
        self.update_attributes()

   


# Agent for Neighbourhood
class Neighbourhood(mg.GeoAgent):
    def __init__(self, unique_id, model, geometry, crs):
        super().__init__(unique_id, model, geometry, crs)
        self.moves = 0
        self.capacity = None
        self.param_1 = None
        self.param_2 = None
        self.salary = None
        self.cost_of_living = None
        self.average_house_price = None

    def step(self):
        """
        Nothing for now, however, we might want to add some stochastic noise here to param_1 and params_2.
        Instead of decreasing gradually weights for boredom in Agent, we should simulate change in region, random walker for params.
        As it is more realistic for region to change randomly. It is random as for us these dynamics are just noise and not point of simulation.
        """
        return




# Example to use as reference
# Initiating Neighbourhood (Agent)
class SchellingAgent(mg.GeoAgent):
    """Schelling segregation agent."""

    # Init for Agent of this model
    def __init__(self, unique_id, model, geometry, crs, agent_type=None):
        """Create a new Schelling agent.

        Args:
            unique_id: Unique identifier for the agent.
            agent_type: Indicator for the agent's type (minority=1, majority=0)
        """
        # Init for base clas
        super().__init__(unique_id, model, geometry, crs)
        self.atype = agent_type     # Some local variable used in this model

    # Step thing, same as in base mesa
    def step(self):
        """Advance agent one step."""
        similar = 0
        different = 0
        neighbors = self.model.space.get_neighbors(self)
        if neighbors:
            for neighbor in neighbors:
                if neighbor.atype is None:
                    continue
                elif neighbor.atype == self.atype:
                    similar += 1
                else:
                    different += 1

        # If unhappy, move:
        if similar < different:
            # Select an empty region
            empties = [a for a in self.model.space.agents if a.atype is None]
            # Switch atypes and add/remove from scheduler
            new_region = random.choice(empties)
            new_region.atype = self.atype
            self.model.schedule.add(new_region)
            self.atype = None
            self.model.schedule.remove(self)
        else:
            self.model.happy += 1

    # Some built-in thingy to output object as string
    def __repr__(self):
        return "Agent " + str(self.unique_id)