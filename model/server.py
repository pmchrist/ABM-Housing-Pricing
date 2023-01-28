import xyzservices.providers as xyz

import mesa
import mesa_geo as mg

from model import Housing
from agents import Person, Neighbourhood, House

class HousingElement(mesa.visualization.TextElement):
    """
    Display a text count of how many happy agents there are.
    """

    def render(self, model):
        return f"Amount of Deals: {model.deals}"


# Parameters of the model
model_params = {
    "num_houses": mesa.visualization.Slider("num_houses", 0.01, 0.01, 1.0, 0.01),
    "noise": mesa.visualization.Slider("noise", 0.0, 0.0, 0.2, 0.05),
    "contentment_threshold": mesa.visualization.Slider("contentment_threshold", 15.0, 0.1, 20.0, 0.1),      # As it is not normalized for now, there is some space to play
    "money_loving": mesa.visualization.Slider("money_loving", 0.2, 0.0, 1.0, 0.1),
}


def map_colors(agent):
    """
    Portrayal Method for canvas
    """
    portrayal = dict()
    if isinstance(agent, Neighbourhood):
        if agent.moves > 256:
            portrayal["color"] = "Red"
        elif agent.moves > 128:
            portrayal["color"] = "Orange"
        elif agent.moves > 32:
            portrayal["color"] = "Blue"
        else:
            portrayal["color"] = "Grey"
    elif isinstance(agent, House):
        portrayal["radius"] = 1
        portrayal["shape"] = "circle"
        # Red houses are overpriced
        portrayal["color"] = "Red" if agent.price>agent.neighbourhood.average_neighbourhood_price else "Green"
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
