import xyzservices.providers as xyz

import mesa
import mesa_geo as mg

from model import Housing
from agents import Person, Neighbourhood, House

class HousingElement(mesa.visualization.TextElement):
    """
    Display a text count of how many happy agents there are.
    """

    def __init__(self):
        pass

    def render(self, model):
        return "Amount of Deals: " + str(model.deals)


# Parameters of the model
model_params = {
    "param_1": mesa.visualization.Slider("param_1", 0.5, 0.1, 1.0, 0.1),
    "param_2": mesa.visualization.Slider("param_2", 0.5, 0.1, 1.0, 0.1),
    "money_loving": mesa.visualization.Slider("param_2", 0.2, 0.0, 1.0, 0.1),
    "num_people": 100,
    "num_houses": 100,
    "contentment_threshold": 0.5,
    "noise": 0.0
}


def schelling_draw(agent):
    """
    Portrayal Method for canvas
    """
    portrayal = dict()
    if isinstance(agent, Neighbourhood):
        if agent.moves > 40:
            portrayal["color"] = "Red"
        elif agent.moves > 10:
            portrayal["color"] = "Orange"
        elif agent.moves > 2:
            portrayal["color"] = "Blue"
        else:
            portrayal["color"] = "Grey"
    return portrayal


housing_element = HousingElement()
map_element = mg.visualization.MapModule(
    schelling_draw, [52.3676, 4.9041], 11, tiles=xyz.CartoDB.Positron
)
deals_chart = mesa.visualization.ChartModule([{"Label": "Deals", "Color": "Black"}])
contentment_chart = mesa.visualization.ChartModule([{"Label": "Average Contentment", "Color": "Black"}])
server = mesa.visualization.ModularServer(
    Housing, [map_element, housing_element, deals_chart, contentment_chart], "Housing Market", model_params
)
