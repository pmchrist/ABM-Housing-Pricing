# Amsterdam Housing Market Dynamics

The average prices of homes in Amsterdam have seen an yearly increase of 15\% since 2013, and onwards. The housing market has become difficult to predict and explain. To research this topic we propose in our project a basic framework for an Agent-Based Model, of the Amsterdam housing market. The model leverages real-world data provided by the municipality of Amsterdam to incorporate heterogeneity between the houses in the city. The goal of the model is to try and explain the underlying dynamics of the market, with regard to its input parameters.
The paper tries to gain an insight into the house prices and societal contentment of Amsterdam, in detail how they are dependent on:
- the housing growth rate;
- an increase in demand;
- the societal standards;
- agents' preferences; 

The model will be described following the ODD protocol for describing an Agent-Based Model. The model will be interpreted through a local and global sensitivity analysis, alongside a structural validity analysis. The results have shown that the model can replicate some basic dynamics of the housing market. However, for this model to become able to inform policymakers, more future research and alterations have to be accomplished. This is why the proposed model is simply a basic framework for the Amsterdam housing market.
You can read more about theoretical framework and detailed ODD in our paper (link down), or take a look into code. To run it you can follow guide in the next section.

## Installation

## Prerequisites:
All the necessary libraries, frameworks, and modules can be installed through:

```bash
pip3 install -r requirements.txt
```

## Usage
There are multiple ways to run our model. The most interactive one is to use the visualization. In this mode you can play with input parameters and see how Amsterdam's housing market is changing. To do so, make sure your current directory is the 'model' folder and run in console:

```bash
python3 run.py visualization
```

Another choice is to limit the simulation to default parameters and run it with text only output. To do so, make sure your current directory is the 'model' folder and run in console:

```bash
python3 run.py debug
```

To generate output for Sensitivity Analysis you should use:

```bash
python3 run.py batch
```

## Repository
If you want to dive into code in more detail here is the outline of the repository:

* analysis
    * experiments.ipynb: a notebook where all the experiments with model output has been made
    * simulations_for_SA_results_reader.ipynb: a file where the sensitivity analysis is performed
    * plots_experiments: a folder in which all the images from experiments are saved
    * results_for_SA: a folder in which output of simulations are saved for the Sensitivity Analysis
* data
    * Amsterdam_map_fin.json: dataset which contains polygons and location of the boroughs of Amsterdam
    * _combined_datasets.xlsx: a file with combined data from datasets which we use in the model
    * modified_datasets: a folder with datasets which contains datasets that are cleaned and normalized
    * original_datasets: a folder with original datasets, before data cleaning and normalizing
* model
    * agents.py: file with all the Agent classes
    * loader.py: in this file data loader for datasets is implemented
    * model.py: file which contains the main model
    * run.py: in this file we declare the simulation execution
    * server.py: in this file visualisation for our Mesa Geo model is implemented

## Important Links
- Notes: https://docs.google.com/document/d/1djK0TwGeARVyFwg5YD1hHhqHEO6rcuoJM2oxxlm5gyk/edit
- Overleaf: https://www.overleaf.com/1611799474njnmvddrkcck
- Slides: https://docs.google.com/presentation/d/1mKZt-l1SZImBfMfunaePMaebxOk8ldWtiIUQf8XfFts/edit?usp=sharing

## Licence
[MIT](https://choosealicense.com/licenses/mit/)
