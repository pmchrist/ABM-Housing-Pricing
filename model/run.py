# What to run
debug = False
batch = False

import mesa
import pandas as pd

from model import Housing
from agents import Person, Neighbourhood, House
from multiprocessing import freeze_support


# To run visualization
if not debug:
    from server import server
    server.launch()


if batch and debug:

    #params = {"width": 10, "height": 10, "N": range(10, 500, 10)}
    # We should use some sampling to use paramter range for the complete running
    params = {"num_houses": 0.01,
            "noise": 0.0,
            "contentment_threshold": 15,
            "money_loving": 0.2}

    results = []

    # If for freeze_support() is only necessary on windows
    if __name__ == '__main__':
        freeze_support()
        results = mesa.batch_run(
            Housing,
            parameters=params,
            iterations=10,
            max_steps=20,
            number_processes=20,
            data_collection_period=1,
            display_progress=True,
        )
    
    if results:
        results_df = pd.DataFrame(results)
        print(results_df.keys())


# Or, to not run visualization
if debug:
    # Some values for statistics at the end
    population = 0
    unhappy_population = 0

    # Run model for 10 steps
    model = Housing(num_houses=0.01, noise=0.0, contentment_threshold=15.0, money_loving=0.2)
    for i in range(10):
        model.step()

    # Show who lives where (Was used for Debug)
    agents = model.schedule.agents
    for agent in agents:
        if isinstance(agent, Neighbourhood): 
            # print("Amount of people living: ", agent.capacity)
            continue
    for agent in agents:
        if isinstance(agent, Person): 
            population += 1
            if agent.contentment < agent.model.contentment_threshold:
                unhappy_population += 1

    # print("Population: ", population)
    # print("Unhappy Population %: ", unhappy_population/population)
