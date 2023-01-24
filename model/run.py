debug = True

# To run visualization
if not debug:
    from server import server
    server.launch()

# Or, to not run visualization
if debug:
    from model import Housing
    from agents import Person, Neighbourhood, House

    # Some values for statistics at the end
    population = 0
    unhappy_population = 0

    # Run model for 10 steps
    model = Housing(num_people=100, num_houses=100, noise=0.0, contentment_threshold=0.4, weight_1=1.0, weight_2=1.0)
    for i in range(10):
        model.step()

    # Show who lives where (Was used for Debug)
    agents = model.schedule.agents
    for agent in agents:
        if isinstance(agent, Neighbourhood): 
            # print("Amount of people living: ", agent.capacity)
            continue
    for agent in agents:
        if isinstance(agent, Person): 
            population += 1
            if agent.contentment < agent.model.contentment_threshold:
                unhappy_population += 1

    print("Population: ", population)
    print("Unhappy Population %: ", unhappy_population/population)


# Some available stuff to access:
#agent.geometry
#agent.Oppervlakte_m2
## Available Params
## CBS_Buurtcode,        Buurtcode,          Buurt,          Wijkcode,               Wijk,               Gebiedcode,     Gebied,     Stadsdeelcode,  Stadsdeel,  Oppervlakte_m2
## Neighborhood code,    Neighborhood code,  Neighborhood,   Neighborhood Big code,  Neighbourhood Big,  Area code,      Area,       District code,  District,   Surface
#
## Neighbour Regions
#neighbors = m.space.get_neighbors(agent)
#print([a.unique_id for a in neighbors])

## Regioins in close space
#print([a.unique_id for a in m.space.get_neighbors_within_distance(agent, 500)])

