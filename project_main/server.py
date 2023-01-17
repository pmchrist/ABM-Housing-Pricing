# README:
# No idea for now how it works. Basically handles visualization only

import xyzservices.providers as xyz

import mesa
import mesa_geo as mg

from models import GeoSchelling


class HappyElement(mesa.visualization.TextElement):
    """
    Display a text count of how many happy agents there are.
    """

    def __init__(self):
        pass

    def render(self, model):
        return "Happy agents: " + str(model.happy)


model_params = {
    "density": mesa.visualization.Slider("Agent density", 0.6, 0.1, 1.0, 0.1),
    "minority_pc": mesa.visualization.Slider("Fraction minority", 0.2, 0.00, 1.0, 0.05),
    "export_data": mesa.visualization.Checkbox("Export data after simulation", False),
}


def schelling_draw(agent):
    """
    Portrayal Method for canvas
    """
    portrayal = dict()
    if agent.atype is None:
        portrayal["color"] = "Grey"
    elif agent.atype == 0:
        portrayal["color"] = "Red"
    else:
        portrayal["color"] = "Blue"
    return portrayal


happy_element = HappyElement()
map_element = mg.visualization.MapModule(
    schelling_draw, [52.3676, 4.9041], 11, tiles=xyz.CartoDB.Positron
)
happy_chart = mesa.visualization.ChartModule([{"Label": "happy", "Color": "Black"}])
server = mesa.visualization.ModularServer(
    GeoSchelling, [map_element, happy_element, happy_chart], "Schelling", model_params
)
