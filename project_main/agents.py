import random

import mesa
import mesa_geo as mg

#from models import Housing


# Agent for Person who gets a house and moves
class Person(mesa.Agent):
    def __init__(self, unique_id: int, model: mesa.Model) -> None:
        super().__init__(unique_id, model)

# Neighbourhoods are also defined as Agents
class Neighbourhood(mg.GeoAgent):
    def __init__(self) -> None:
        super().__init__()


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