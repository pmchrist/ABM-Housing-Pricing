# What to run
debug = True
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

# Needs a lot of updates: 1) Update Model Init, 2) Add Sampling, 3) Save Pickle between Steps 4) Save Final Output
if batch:

    #params = {"width": 10, "height": 10, "N": range(10, 500, 10)}
    # We should use some sampling to use paramter range for the complete running
    params = {"num_houses": 0.001,
            "noise": 0.0,
            "start_money_multiplier": 2,
            "start_money_multiplier_newcomers": 2,
            "contentment_threshold": 0.8,
            "weight_materialistic": 0.5,
            "housing_growth_rate": 1.02,
            "population_growth_rate": 1.02}

    results = []

    # If for freeze_support() is only necessary on windows
    if __name__ == '__main__':
        freeze_support()
        results = mesa.batch_run(
            Housing,
            parameters=params,
            iterations=2,
            max_steps=20,
            number_processes=5,
            data_collection_period=1,
            display_progress=True,
        )
    
    if results:
        results_df = pd.DataFrame(results)
        results_df.to_excel("output.xlsx") 


# Or, to not run visualization
if debug:
    # Run model for 10 steps
    model = Housing(num_houses=0.001, noise=0.0, start_money_multiplier=2, start_money_multiplier_newcomers=2, contentment_threshold=0.6, weight_materialistic=0.5, housing_growth_rate=1.03, population_growth_rate=1.01, print_stats=True)
    for i in range(20):
        model.step()