import xyzservices.providers as xyz

import mesa
import mesa_geo as mg

from model import Housing
from agents import Person, Neighbourhood, House


# Parameters of the model for visualization
model_params = {
    "num_houses": mesa.visualization.Slider("num_houses", 0.001, 0.0001, 0.01, 0.0005),
    "noise": mesa.visualization.Slider("noise", 0.0, 0.0, 0.01, 0.001),
    "start_money_multiplier": mesa.visualization.Slider("start_money_multiplier", 2, 0, 10, 1),
    "start_money_multiplier_newcomers": mesa.visualization.Slider("start_money_multiplier_newcomers", 2, 0, 10, 1),
    "contentment_threshold": mesa.visualization.Slider("contentment_threshold", 0.6, 0.0, 1.0, 0.1),
    "weight_materialistic": mesa.visualization.Slider("weight_materialistic", 0.5, 0.0, 1.0, 0.1),
    "housing_growth_rate": mesa.visualization.Slider("housing_growth_rate", 1.0, 1.0, 1.05, 0.01),
    "population_growth_rate": mesa.visualization.Slider("population_growth_rate", 1.0, 1.0, 1.05, 0.01),
}

# Map: Neighbourhood Contentment and House price
def map_colors(agent):
    """
    Portrayal Method for canvas
    """
    portrayal = dict()
    if isinstance(agent, Neighbourhood):
        if agent.average_contentment > 0.65:
            portrayal["color"] = "Green"
        elif agent.average_contentment > 0.55:
            portrayal["color"] = "Blue"
        elif agent.average_contentment > 0.45:
            portrayal["color"] = "Orange"
        else:
            portrayal["color"] = "Red"
    elif isinstance(agent, House):
        portrayal["radius"] = 1
        portrayal["shape"] = "circle"
        if agent.price == None: portrayal["color"] = "Grey"
        else:
            if agent.price/543204 > 1.10:
                portrayal["color"] = "Red"
            elif agent.price/543204 > 1.05:
                portrayal["color"] = "Orange"
            elif agent.price/543204 >= 1.0:
                portrayal["color"] = "Green"
            else:
                portrayal["color"] = "Blue"
    return portrayal
map_element = mg.visualization.MapModule(
    map_colors, [52.3676, 4.9041], 11, tiles=xyz.CartoDB.Positron
)

# Text: Amoung of deals happened
class HousingElement(mesa.visualization.TextElement):
    """
    Displays a text count of how many deals have happened so far.
    """

    def render(self, model):
        return f"Amount of Deals: {model.deals}"
housing_element = HousingElement()

# Charts: Comparing different Neighbourhoods
contentment_chart = mesa.visualization.ChartModule([{"Label": "average_contentment_Centrum", "Color": "#e1324a"},
                                            {"Label": "average_contentment_Oost", "Color": "#328637"},
                                            {"Label": "average_contentment_NieuwWest", "Color": "#fec8f1"},
                                            {"Label": "average_contentment_Zuidoost", "Color": "#1279b2"},
                                            {"Label": "average_contentment_Noord", "Color": "#a4fbfd"},
                                            {"Label": "average_contentment_West", "Color": "#f2c647"},
                                            {"Label": "average_contentment_Zuid", "Color": "#76c639"}]
                                            )
price_chart = mesa.visualization.ChartModule([{"Label": "average_house_price_Centrum", "Color": "#e1324a"},
                                            {"Label": "average_house_price_Oost", "Color": "#328637"},
                                            {"Label": "average_house_price_NieuwWest", "Color": "#fec8f1"},
                                            {"Label": "average_house_price_Zuidoost", "Color": "#1279b2"},
                                            {"Label": "average_house_price_Noord", "Color": "#a4fbfd"},
                                            {"Label": "average_house_price_West", "Color": "#f2c647"},
                                            {"Label": "average_house_price_Zuid", "Color": "#76c639"}]
                                            )

server = mesa.visualization.ModularServer(
    Housing, [map_element, housing_element, contentment_chart, price_chart], "Housing Market", model_params
)
