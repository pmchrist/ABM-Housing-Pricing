# What to run
debug = False
batch = True

import mesa
import pandas as pd
import numpy as np

from model import Housing
from agents import Person, Neighbourhood, House
from multiprocessing import freeze_support

from SALib.sample import saltelli
from SALib.analyze import sobol


# Needs a lot of updates: 1) Update Model Init, 2) Add Sampling, 3) Save Pickle between Steps 4) Save Final Output
if batch:

    replicates = 10         # Same runs during batch
    max_steps = 20          # Max step for simualtion
    distinct_samples = 10   # Resolution of sampling space
    number_processes = 20   # Amount of CPU threads to use

    params = {
        "num_houses":           np.linspace(0.0001, 0.01, distinct_samples),
        "noise":                np.linspace(0.0, 0.1, distinct_samples),
        "start_money_multiplier":           np.arange(1, 5, distinct_samples),
        "start_money_multiplier_newcomers": np.arange(1, 5, distinct_samples),
        "contentment_threshold":            np.linspace(0.0, 1.0, distinct_samples),
        "weight_materialistic":             np.linspace(0.0, 1.0, distinct_samples),
        "housing_growth_rate":              np.linspace(1.0, 1.02, distinct_samples),
        "population_growth_rate":           np.linspace(1.0, 1.02, distinct_samples)
    }

    problem = {
        'num_vars': 8,
        'names': ['num_houses', 'noise', 'start_money_multiplier', 'start_money_multiplier_newcomers', 'contentment_threshold', 'weight_materialistic', 'housing_growth_rate', 'population_growth_rate'],
        'bounds': [[0.0001, 0.01], [0.0, 0.1], [1, 5], [1, 5], [0.0, 1.0], [0.0, 1.0], [1.0, 1.02], [1.0, 1.02]]
    }

    # We get all our samples here
    param_values = saltelli.sample(problem, distinct_samples)   # 18000 Samples

    results = []

    # Local SA Dataset
    # Vary one linspace, and fix others to default, one by one for each
    # Probably same as old one, but vary params in input

    # Global SA Dataset
    # Use param_values from saltelli, need to be combined and rotated

    # Old runner, all possible combinations
    # If for freeze_support() is only necessary on windows
    if __name__ == '__main__':
        freeze_support()
        results = mesa.batch_run(
            Housing,
            parameters=params,
            iterations=replicates,
            max_steps=max_steps,
            number_processes=20,
            data_collection_period=1,
            display_progress=True,
        )
    
    if results:
        results_df = pd.DataFrame(results)
        results_df.to_csv("output.csv", index=False, float_format='%.5f')

else:
    # Run text output visualization
    if debug:
        # Run model for 10 steps
        model = Housing(num_houses=0.001, noise=0.0, start_money_multiplier=2, start_money_multiplier_newcomers=2, contentment_threshold=0.6, weight_materialistic=0.5, housing_growth_rate=1.03, population_growth_rate=1.01, print_statistics=True)
        for i in range(20):
            model.step()
    # Run visualization
    else:
        from server import server
        server.launch()
