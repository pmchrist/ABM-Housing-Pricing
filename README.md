# Amsterdam Housing Market Dynamics

## Description

Housing model for Amsterdam ...

## Installation

Prerequisites
All the necessary libraries, frameworks, and modules can be installed through:

```bash
pip3 install -r requirements.txt
```

## Usage
To run the model, make sure your current directory is the 'model' folder and run the following command.

```bash
python3 run.py -v
```

To run the model, make sure your current directory is the 'model' folder. There are multiple ways to run our model.
To run it with text console output mode use:

```bash
python3 run.py debug
```

If you run the model with visualization, you can easily change the input parameters. To do so use:

```bash
python3 run.py visualization
```

To run Sensitivity Analysis you should use:

```bash
python3 run.py batch
```

## Repository
If you want to dive into code here is the outline of the repository:

/analysis
    /experiments.ipynb:  a notebook where all the analysis has been made
    /sensitivity.py:     a file where the sensitivity analysis is performed
    results of simulations
/data
    /original_datasets:         original datasets, before data cleaning
    /something_very_detailed:   datasets which we did not use but helped us in the assignment
    used datasets
/model
    model.py        file which contains the main model
    agents.py       file with all the Agent classes
    loader.py       in this file data loader for datasets is implemented
    server.py       in this file visualisation for our Mesa Geo model is implemented
    run.py          in this file we declare the simulation execution

## References

## Important Links
- Notes: https://docs.google.com/document/d/1djK0TwGeARVyFwg5YD1hHhqHEO6rcuoJM2oxxlm5gyk/edit
- Overleaf: https://www.overleaf.com/1611799474njnmvddrkcck
- Slides: https://docs.google.com/presentation/d/1mKZt-l1SZImBfMfunaePMaebxOk8ldWtiIUQf8XfFts/edit?usp=sharing

## Licence
[MIT](https://choosealicense.com/licenses/mit/)
