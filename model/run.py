import mesa
import pandas as pd
import numpy as np
import sys

from model import Housing
from multiprocessing import freeze_support

from SALib.sample import saltelli

# Needs a lot of updates: 1) Update Model Init, 2) Add Sampling, 3) Save Pickle between Steps 4) Save Final Output
if (sys.argv[1] == "batch"):
    local_SA = True
    global_SA = True
    # OFAT
    if local_SA:

        replicates = 10         # Same runs during batch
        max_steps = 20          # Max step for simualtion
        distinct_samples = 100  # Resolution of sampling space
        number_processes = 12   # Amount of CPU threads to use

        # Simple SA
        # OFAT with variable num_houses
        params_0 = {
            "num_houses":                       np.linspace(0.0001, 0.01, distinct_samples),
            "noise":                            0.0,
            "start_money_multiplier":           2,
            "start_money_multiplier_newcomers": 2,
            "contentment_threshold":            0.75,
            "weight_materialistic":             0.5,
            "housing_growth_rate":              1.01,
            "population_growth_rate":           1.01
        }
        # OFAT with variable noise
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
        # OFAT with variable start_money_multiplier
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
        # OFAT with variable start_money_multiplier_newcomers
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
        # OFAT with variable contentment_threshold
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
        # OFAT with variable weight_materialistic
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
        # OFAT with variable housing_growth_rate
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
        # OFAT with variable population_growth_rate
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
        # Starting OFATs
        if __name__ == '__main__':          # Necessary to work on Windows
            freeze_support()                # Necessary to work on Windows
            # OFAT with variable num_houses
            results_0 = mesa.batch_run(
                Housing,
                parameters=params_0,
                iterations=replicates,
                max_steps=max_steps,
                number_processes=number_processes,
                data_collection_period=1,
                display_progress=True,
            )
            # OFAT with variable noise
            results_1 = mesa.batch_run(
                Housing,
                parameters=params_1,
                iterations=replicates,
                max_steps=max_steps,
                number_processes=number_processes,
                data_collection_period=1,
                display_progress=True,
            )
            # OFAT with variable start_money_multiplier
            results_2 = mesa.batch_run(
                Housing,
                parameters=params_2,
                iterations=replicates,
                max_steps=max_steps,
                number_processes=number_processes,
                data_collection_period=1,
                display_progress=True,
            )
            # OFAT with variable start_money_multiplier_newcomers
            results_3 = mesa.batch_run(
                Housing,
                parameters=params_3,
                iterations=replicates,
                max_steps=max_steps,
                number_processes=number_processes,
                data_collection_period=1,
                display_progress=True,
            )
            # OFAT with variable contentment_threshold
            results_4 = mesa.batch_run(
                Housing,
                parameters=params_4,
                iterations=replicates,
                max_steps=max_steps,
                number_processes=number_processes,
                data_collection_period=1,
                display_progress=True,
            )
            # OFAT with variable weight_materialistic
            results_5 = mesa.batch_run(
                Housing,
                parameters=params_5,
                iterations=replicates,
                max_steps=max_steps,
                number_processes=number_processes,
                data_collection_period=1,
                display_progress=True,
            )
            # OFAT with variable housing_growth_rate
            results_6 = mesa.batch_run(
                Housing,
                parameters=params_6,
                iterations=replicates,
                max_steps=max_steps,
                number_processes=number_processes,
                data_collection_period=1,
                display_progress=True,
            )
            # OFAT with variable population_growth_rate
            results_7 = mesa.batch_run(
                Housing,
                parameters=params_7,
                iterations=replicates,
                max_steps=max_steps,
                number_processes=number_processes,
                data_collection_period=1,
                display_progress=True,
            )
            # Combining results to output to final file
            if results_0 and results_1 and results_2 and results_3 and results_4 and results_5 and results_6 and results_7:
                results_df = pd.concat([pd.DataFrame(results_0), pd.DataFrame(results_1), pd.DataFrame(results_2), pd.DataFrame(results_3), pd.DataFrame(results_4), pd.DataFrame(results_5), pd.DataFrame(results_6), pd.DataFrame(results_7)], ignore_index=True)
                results_df.to_parquet("output_local_SA.parquet")
    # Sobol SA
    if global_SA:

        replicates = 10         # Same runs during batch
        max_steps = 20          # Max step for simualtion
        distinct_samples = 512  # Resolution of sampling space
        number_processes = 12   # Amount of CPU threads to use

        # Problem with only "important" parameters
        problem = {
            'num_vars': 5,
            'names': ['start_money_multiplier', 'contentment_threshold', 'weight_materialistic', 'housing_growth_rate', 'population_growth_rate'],
            'bounds': [[0, 10], [0.0, 1.0], [0.0, 1.0], [1.0, 1.02], [1.0, 1.02]]
        }

        # We get all our samples
        param_values = saltelli.sample(problem, distinct_samples)
        # Init empty Dataframe to fill
        results_df = pd.DataFrame()

        # Running simulation with parameters we generated
        for i in range(0, len(param_values)):
            # Assigning params
            params = {
                "num_houses":                       0.001,
                "noise":                            0.0,
                "start_money_multiplier":           param_values[i][0],
                "start_money_multiplier_newcomers": 2,
                "contentment_threshold":            param_values[i][1],
                "weight_materialistic":             param_values[i][2],
                "housing_growth_rate":              param_values[i][3],
                "population_growth_rate":           param_values[i][4]
            }
            # Starting simulation
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
                # If all replicates are finished
                if results:
                    print(i, len(param_values))     # How far are we
                    results_df_temp = pd.DataFrame(results)
                    results_df = pd.concat([pd.DataFrame(results_df), pd.DataFrame(results_df_temp)], ignore_index=True)
                    # Saving temporary results
                    if ((i+1) % 256 == 0):
                        results_df.to_parquet("output_global_SA_" + str(i) + ".parquet")
                        results_df = pd.DataFrame()         # Resetting dataframe to avoid memory overflow
# Run text output simulation
elif (sys.argv[1] == "debug"):
    # Run model for 10 steps
    model = Housing(num_houses=0.001, noise=0.0, start_money_multiplier=2, start_money_multiplier_newcomers=2, contentment_threshold=0.75, weight_materialistic=0.5, housing_growth_rate=1.02, population_growth_rate=1.01, print_statistics=True)
    for i in range(20):
        model.step()
# Run visualization
elif (sys.argv[1] == "visualization"):
    from server import server
    server.launch()
