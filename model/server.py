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
    "num_houses": mesa.visualization.Slider("num_houses", 0.001, 0.0001, 0.01, 0.0005),
    "noise": mesa.visualization.Slider("noise", 0.0, 0.0, 0.005, 0.001),
    "start_money_multiplier": mesa.visualization.Slider("start_money_multiplier", 2, 0, 5, 1),
    "start_money_multiplier_newcomers": mesa.visualization.Slider("start_money_multiplier_newcomers", 2, 0, 5, 1),
    "contentment_threshold": mesa.visualization.Slider("contentment_threshold", 0.5, 0.0, 1.0, 0.1),      # As it is not normalized for now, there is some space to play
    "weight_materialistic": mesa.visualization.Slider("weight_materialistic", 0.5, 0.0, 1.0, 0.1),
    "housing_growth_rate": mesa.visualization.Slider("housing_growth_rate", 1.0, 1.0, 1.2, 0.01),
    "population_growth_rate": mesa.visualization.Slider("population_growth_rate", 1.00, 1.0, 1.2, 0.01),
}

# New Portrayal (Neighbourhood Prices and Salary)
def map_colors_house_price_vs_salary(agent):
    """
    Portrayal Method for canvas
    """
    portrayal = dict()
    if isinstance(agent, Neighbourhood):
        if agent.average_contentment > 1.5*agent.model.contentment_threshold:
            portrayal["color"] = "Red"
        elif agent.average_contentment > 1.2*agent.model.contentment_threshold:
            portrayal["color"] = "Orange"
        elif agent.average_contentment > 0.9*agent.model.contentment_threshold:
            portrayal["color"] = "Green"
        else:
            portrayal["color"] = "Blue"

    elif isinstance(agent, House):
        portrayal["radius"] = 1
        portrayal["shape"] = "circle"
        if agent.owner == None: portrayal["color"] = "Grey"
        else:
            if agent.owner.salary/68238 > 1.4:
                portrayal["color"] = "Green"
            elif agent.owner.salary/68238 > 1.0:
                portrayal["color"] = "Blue"
            elif agent.owner.salary/68238 > 0.6:
                portrayal["color"] = "Orange"
            else:
                portrayal["color"] = "Red"

    return portrayal


housing_element = HousingElement()
map_element = mg.visualization.MapModule(
    map_colors_house_price_vs_salary, [52.3676, 4.9041], 11, tiles=xyz.CartoDB.Positron
)

price_chart = mesa.visualization.ChartModule([{"Label": "average_house_price_Centrum", "Color": "#e1324a"},
                                            {"Label": "average_house_price_Oost", "Color": "#328637"},
                                            {"Label": "average_house_price_NieuwWest", "Color": "#fec8f1"},
                                            {"Label": "average_house_price_Zuidoost", "Color": "#1279b2"},
                                            {"Label": "average_house_price_Noord", "Color": "#a4fbfd"},
                                            {"Label": "average_house_price_West", "Color": "#f2c647"},
                                            {"Label": "average_house_price_Zuid", "Color": "#76c639"}]
                                            )
contentment_chart = mesa.visualization.ChartModule([{"Label": "average_contentment_Centrum", "Color": "#e1324a"},
                                            {"Label": "average_contentment_Oost", "Color": "#328637"},
                                            {"Label": "average_contentment_NieuwWest", "Color": "#fec8f1"},
                                            {"Label": "average_contentment_Zuidoost", "Color": "#1279b2"},
                                            {"Label": "average_contentment_Noord", "Color": "#a4fbfd"},
                                            {"Label": "average_contentment_West", "Color": "#f2c647"},
                                            {"Label": "average_contentment_Zuid", "Color": "#76c639"}]
                                            )

server = mesa.visualization.ModularServer(
    Housing, [map_element, housing_element, contentment_chart, price_chart], "Housing Market", model_params
)
