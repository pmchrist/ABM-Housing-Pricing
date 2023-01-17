# File that handles model interaction
# We should also hold all the data collection through here

import random

import mesa
import mesa_geo as mg

from agents import SchellingAgent


# Our main model class
class Housing(mesa.Model):
    def __init__(self) -> None:
        super().__init__()


# Model Example
class GeoSchelling(mesa.Model):
    """Model class for the Schelling segregation model."""

    # Basically, we can pass anything here, width, height and init population are given by map and neighbourhouds amount (in current case)
    def __init__(self, density=0.6, minority_pc=0.2, export_data=False):
        self.density = density
        self.minority_pc = minority_pc
        self.export_data = export_data

        self.schedule = mesa.time.RandomActivation(self)
        self.space = mg.GeoSpace(warn_crs_conversion=False)

        self.happy = 0
        self.datacollector = mesa.DataCollector({"happy": "happy"})

        self.running = True

        # Set up the grid with patches for every region
        ac = mg.AgentCreator(SchellingAgent, model=self)
        agents = ac.from_file("Amsterdam_map_from_github.geojson")
        self.space.add_agents(agents)

        # Set up agents
        for agent in agents:
            if random.random() < self.density:
                if random.random() < self.minority_pc:
                    agent.atype = 1
                else:
                    agent.atype = 0
                self.schedule.add(agent)

    # No idea, some export for visualization, I guess
    def export_agents_to_file(self) -> None:
        self.space.get_agents_as_GeoDataFrame(agent_cls=SchellingAgent).to_crs(
            "epsg:4326"
        ).to_file("data/schelling_agents.geojson", driver="GeoJSON")

    # Step for model, same as in simple mesa
    def step(self):
        """Run one step of the model.

        If All agents are happy, halt the model.
        """
        self.happy = 0  # Reset counter of happy agents
        self.schedule.step()
        self.datacollector.collect(self)

        if self.happy == self.schedule.get_agent_count():
            self.running = False

        if not self.running and self.export_data:
            self.export_agents_to_file()
