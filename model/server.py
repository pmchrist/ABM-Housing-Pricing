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
    "num_houses": mesa.visualization.Slider("num_houses", 0.5, 0.1, 1.0, 0.1),
    "noise": mesa.visualization.Slider("noise", 0.0, 0.0, 0.2, 0.05),
    "contentment_threshold": mesa.visualization.Slider("contentment_threshold", 0.5, 0.1, 5.0, 0.1),      # As it is not normalized for now, there is some space to play
    "money_loving": mesa.visualization.Slider("money_loving", 0.2, 0.0, 1.0, 0.1),
}


def map_colors(agent):
    """
    Portrayal Method for canvas
    """
    portrayal = dict()
    if isinstance(agent, Neighbourhood):
        if agent.moves > 16:
            portrayal["color"] = "Red"
        elif agent.moves > 8:
            portrayal["color"] = "Orange"
        elif agent.moves > 4:
            portrayal["color"] = "Blue"
        else:
            portrayal["color"] = "Grey"
    return portrayal


housing_element = HousingElement()
map_element = mg.visualization.MapModule(
    map_colors, [52.3676, 4.9041], 11, tiles=xyz.CartoDB.Positron
)
deals_chart = mesa.visualization.ChartModule([{"Label": "Deals", "Color": "Black"}])
contentment_chart = mesa.visualization.ChartModule([{"Label": "Average Contentment", "Color": "Black"}])
server = mesa.visualization.ModularServer(
    Housing, [map_element, housing_element, deals_chart, contentment_chart], "Housing Market", model_params
)
