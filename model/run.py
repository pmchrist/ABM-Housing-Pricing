# What to run
debug = False
batch = True
local_SA = True
global_SA = True

import mesa
import pandas as pd
import numpy as np

from model import Housing
from agents import Person, Neighbourhood, House
from multiprocessing import freeze_support

from SALib.sample import saltelli


# Needs a lot of updates: 1) Update Model Init, 2) Add Sampling, 3) Save Pickle between Steps 4) Save Final Output
if batch:

    replicates = 100        # Same runs during batch
    max_steps = 20          # Max step for simualtion
    distinct_samples = 10   # Resolution of sampling space
    number_processes = 20   # Amount of CPU threads to use

    # # All params range, for reference
    # params = {
    #     "num_houses":           np.linspace(0.0001, 0.01, distinct_samples),
    #     "noise":                np.linspace(0.0, 0.005, distinct_samples),
    #     "start_money_multiplier":           np.linspace(0.0, 10.0, distinct_samples, dtype=int),
    #     "start_money_multiplier_newcomers": np.linspace(0.0, 10.0, distinct_samples, dtype=int),
    #     "contentment_threshold":            np.linspace(0.1, 0.9, distinct_samples),
    #     "weight_materialistic":             np.linspace(0.1, 0.9, distinct_samples),
    #     "housing_growth_rate":              np.linspace(1.0, 1.02, distinct_samples),
    #     "population_growth_rate":           np.linspace(1.0, 1.02, distinct_samples)
    # }

    if local_SA:
        # Simple SA
        params_0 = {
            "num_houses":   np.linspace(0.0001, 0.01, distinct_samples),
            "noise":                            0.0,
            "start_money_multiplier":           2,
            "start_money_multiplier_newcomers": 2,
            "contentment_threshold":            0.75,
            "weight_materialistic":             0.5,
            "housing_growth_rate":              1.01,
            "population_growth_rate":           1.01
        }
        params_1 = {
            "num_houses":                       0.001,
            "noise":                            np.linspace(0.0, 0.005, distinct_samples),
            "start_money_multiplier":           2,
            "start_money_multiplier_newcomers": 2,
            "contentment_threshold":            0.75,
            "weight_materialistic":             0.5,
            "housing_growth_rate":              1.01,
            "population_growth_rate":           1.01
        }
        params_2 = {
            "num_houses":                       0.001,
            "noise":                            0.0,
            "start_money_multiplier":           np.linspace(0.0, 10.0, distinct_samples, dtype=int),
            "start_money_multiplier_newcomers": 2,
            "contentment_threshold":            0.75,
            "weight_materialistic":             0.5,
            "housing_growth_rate":              1.01,
            "population_growth_rate":           1.01
        }
        params_3 = {
            "num_houses":                       0.001,
            "noise":                            0.0,
            "start_money_multiplier":           2,
            "start_money_multiplier_newcomers": np.linspace(0.0, 10.0, distinct_samples, dtype=int),
            "contentment_threshold":            0.75,
            "weight_materialistic":             0.5,
            "housing_growth_rate":              1.01,
            "population_growth_rate":           1.01
        }
        params_4 = {
            "num_houses":                       0.001,
            "noise":                            0.0,
            "start_money_multiplier":           2,
            "start_money_multiplier_newcomers": 2,
            "contentment_threshold":            np.linspace(0.0, 1.0, distinct_samples),
            "weight_materialistic":             0.5,
            "housing_growth_rate":              1.01,
            "population_growth_rate":           1.01
        }
        params_5 = {
            "num_houses":                       0.001,
            "noise":                            0.0,
            "start_money_multiplier":           2,
            "start_money_multiplier_newcomers": 2,
            "contentment_threshold":            0.75,
            "weight_materialistic":             np.linspace(0.0, 1.0, distinct_samples),
            "housing_growth_rate":              1.01,
            "population_growth_rate":           1.01
        }
        params_6 = {
            "num_houses":                       0.001,
            "noise":                            0.0,
            "start_money_multiplier":           2,
            "start_money_multiplier_newcomers": 2,
            "contentment_threshold":            0.75,
            "weight_materialistic":             0.5,
            "housing_growth_rate":              np.linspace(1.0, 1.02, distinct_samples),
            "population_growth_rate":           1.01
        }
        params_7 = {
            "num_houses":                       0.001,
            "noise":                            0.0,
            "start_money_multiplier":           2,
            "start_money_multiplier_newcomers": 2,
            "contentment_threshold":            0.75,
            "weight_materialistic":             0.5,
            "housing_growth_rate":              1.01,
            "population_growth_rate":           np.linspace(1.0, 1.02, distinct_samples)
        }
        if __name__ == '__main__':
            freeze_support()
            results_0 = mesa.batch_run(
                Housing,
                parameters=params_0,
                iterations=replicates,
                max_steps=max_steps,
                number_processes=number_processes,
                data_collection_period=1,
                display_progress=True,
            )
            results_1 = mesa.batch_run(
                Housing,
                parameters=params_1,
                iterations=replicates,
                max_steps=max_steps,
                number_processes=number_processes,
                data_collection_period=1,
                display_progress=True,
            )
            results_2 = mesa.batch_run(
                Housing,
                parameters=params_2,
                iterations=replicates,
                max_steps=max_steps,
                number_processes=number_processes,
                data_collection_period=1,
                display_progress=True,
            )
            results_3 = mesa.batch_run(
                Housing,
                parameters=params_3,
                iterations=replicates,
                max_steps=max_steps,
                number_processes=number_processes,
                data_collection_period=1,
                display_progress=True,
            )
            results_4 = mesa.batch_run(
                Housing,
                parameters=params_4,
                iterations=replicates,
                max_steps=max_steps,
                number_processes=number_processes,
                data_collection_period=1,
                display_progress=True,
            )
            results_5 = mesa.batch_run(
                Housing,
                parameters=params_5,
                iterations=replicates,
                max_steps=max_steps,
                number_processes=number_processes,
                data_collection_period=1,
                display_progress=True,
            )
            results_6 = mesa.batch_run(
                Housing,
                parameters=params_6,
                iterations=replicates,
                max_steps=max_steps,
                number_processes=number_processes,
                data_collection_period=1,
                display_progress=True,
            )
            results_7 = mesa.batch_run(
                Housing,
                parameters=params_7,
                iterations=replicates,
                max_steps=max_steps,
                number_processes=number_processes,
                data_collection_period=1,
                display_progress=True,
            )
            if results_0 and results_1 and results_2 and results_3 and results_4 and results_5 and results_6 and results_7:
                results_df = pd.concat([pd.DataFrame(results_0), pd.DataFrame(results_1), pd.DataFrame(results_2), pd.DataFrame(results_3), pd.DataFrame(results_4), pd.DataFrame(results_5), pd.DataFrame(results_6), pd.DataFrame(results_7)], ignore_index=True)
                results_df.to_csv("output_localSA.csv", index=False, float_format='%.5f')

    if global_SA:
        problem = {
            'num_vars': 8,
            'names': ['num_houses', 'noise', 'start_money_multiplier', 'start_money_multiplier_newcomers', 'contentment_threshold', 'weight_materialistic', 'housing_growth_rate', 'population_growth_rate'],
            'bounds': [[0.0001, 0.01], [0.0, 0.005], [1, 5], [1, 5], [0.1, 0.9], [0.1, 0.9], [1.0, 1.02], [1.0, 1.02]]
        }

        # We get all our samples here
        param_values = saltelli.sample(problem, distinct_samples)   # 18000 Samples
        results_df = pd.DataFrame()

        for i in range(len(param_values)):
            # Assigning params
            params = {
                "num_houses":           param_values[i][0],
                "noise":                param_values[i][1],
                "start_money_multiplier":           param_values[i][2],
                "start_money_multiplier_newcomers": param_values[i][3],
                "contentment_threshold":            param_values[i][4],
                "weight_materialistic":             param_values[i][5],
                "housing_growth_rate":              param_values[i][6],
                "population_growth_rate":           param_values[i][7]
            }

            if __name__ == '__main__':
                freeze_support()
                results = mesa.batch_run(
                    Housing,
                    parameters=params,
                    iterations=replicates,
                    max_steps=max_steps,
                    number_processes=number_processes,
                    data_collection_period=1,
                    display_progress=True,
                )

                if results:
                    print(i, len(param_values))
                    results_df_temp = pd.DataFrame(results)
                    results_df = pd.concat([pd.DataFrame(results_df), pd.DataFrame(results_df_temp)], ignore_index=True)
                    if len(results_df) >= len(param_values):
                        results_df.to_csv("output_globalSA.csv", index=False, float_format='%.5f')

else:
    # Run text output visualization
    if debug:
        # Run model for 10 steps
        model = Housing(num_houses=0.001, noise=0.0, start_money_multiplier=2, start_money_multiplier_newcomers=2, contentment_threshold=0.75, weight_materialistic=0.5, housing_growth_rate=1.02, population_growth_rate=1.01, print_statistics=True)
        for i in range(20):
            model.step()
    # Run visualization
    else:
        from server import server
        server.launch()
