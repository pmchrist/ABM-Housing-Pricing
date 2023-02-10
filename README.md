# Amsterdam Housing Market Dynamics

## Abstract

The average prices of homes in Amsterdam have seen a yearly increase of 15\% since 2013, and onwards. The housing market has become more unpredictable, and therefore more difficult to predict and explain. This paper proposes a basic framework for an Agent-Based Model, of the Amsterdam housing market. The model leverages real-world data provided by the municipality of Amsterdam to incorporate heterogeneity between the houses in the city. The goal of the model is to try and explain the underlying dynamics of the market, with regard to its input parameters. The paper tries to answer what the effects are of (1) the housing growth rate; (2) an increase in demand; (3) the societal standards; (4) agents' preferences; on the house prices and societal contentment of Amsterdam. The model will be described following the ODD protocol for describing an Agent-Based Model. The model will be interpreted through a local and global sensitivity analysis, alongside a structural validity analysis. The results have shown that the model can replicate some basic dynamics of the housing market. However, for this model to become able to inform policymakers, more future research and alterations have to be accomplished. This is why the proposed model is simply a basic framework for the Amsterdam housing market.

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
