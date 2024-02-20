import mesa
from .model import TransInfraNetworkModel

import math
from matplotlib.colors import ListedColormap
from collections import OrderedDict


def network_portrayal(model):
    G = model.G
    CMAP = ListedColormap(["lightblue", "orange", "green",])
    NODE_COLOR_DICT =   {'retail': 'b', 
                        'university': 'b', 
                        'school': 'b', 
                        'dormitory': 'orange', 
                        'yes': 'gray', 
                        'roof': 'gray',
                        'commercial': 'b', 
                        'detached': 'orange', 
                        'garage': 'r', 
                        'church': 'b', 
                        'shed': 'gray', 
                        'house': 'orange',
                        'grandstand': 'b', 
                        'apartments': 'orange',
                        'street': 'gray',}

    EDGE_COLOR_DICT =   {'residential': 'g',
                        'secondary': 'r', 
                        'motorway_link': 'r', 
                        'tertiary': 'r',
                        'motorway': 'r', 
                        'primary': 'r', 
                        'unclassified': 'gray', 
                        'service': 'gray', 
                        'footway': 'g',
                        'pedestrian': 'g', 
                        'path': 'g', 
                        'steps': 'g', 
                        'tertiary_link': 'r'}

    def get_node_pop():
        # calc num people in each node
        node_pop = OrderedDict(zip( G.nodes, len(G.nodes)*[0] ))
        for a in model.space.get_all_cell_contents():
                node_pop[a.pos] = node_pop[a.pos] + 1
        return node_pop
        
    # def node_color(agent):
    #     return {State.INFECTED: "#FF0000", State.SUSCEPTIBLE: "#008000"}.get(
    #         agent.state, "#808080"
    #     )
    def node_color():
        node_pop = get_node_pop()
        return [CMAP(i) for i in node_pop.values()]

    # def edge_color(agent1, agent2):
    #     if State.RESISTANT in (agent1.state, agent2.state):
    #         return "#000000"
    #     return "#e8e8e8"
    def edge_color():
        return

    # def edge_width(agent1, agent2):
    #     if State.RESISTANT in (agent1.state, agent2.state):
    #         return 3
    #     return 2
    def edge_width():
        return

    def get_agents(source, target):
        return G.nodes[source]["agent"][0], G.nodes[target]["agent"][0]

    portrayal = {}
    portrayal["nodes"] = [
        {
            "size": 6,
            "color": node_color(agents[0]),
            "tooltip": f"id: {agents[0].unique_id}<br>state: {agents[0].state.name}",
        }
        for (_, agents) in G.nodes.data("agent")
    ]

    portrayal["edges"] = [
        {
            "source": source,
            "target": target,
            "color": edge_color(*get_agents(source, target)),
            "width": edge_width(*get_agents(source, target)),
        }
        for (source, target) in G.edges
    ]

    return portrayal


# network = mesa.visualization.NetworkModule(network_portrayal, 500, 500)
# chart = mesa.visualization.ChartModule(
#     [
#         {"Label": "Social", "Color": "#FF0000"},
#         {"Label": "Susceptible", "Color": "#008000"},
#         {"Label": "Resistant", "Color": "#808080"},
#     ]
# )

# def agent_portrayal(agent):
#     if agent is None:
#         return
#     portrayal = {"Shape": "circle", "r": 0.5, "Filled": "true"}
#     if agent.social == 0:
#         portrayal["Color"] = "grey"
#         portrayal["Layer"] = 1
#         portrayal["r"] = 0.2
#     else:
#         portrayal["Color"] = "red"
#         portrayal["Layer"] = 0
#     return portrayal

# grid = mesa.visualization.CanvasGrid(agent_portrayal, 10, 10, 500, 500)

chart = mesa.visualization.ChartModule(
    [{"Label": "Social", "Color": "#0000FF"}], data_collector_name="datacollector"
)

model_params = {
    "num_agents": mesa.visualization.Slider(
        "Number of agents",
        10,
        10,
        100,
        1,
        description="Choose how many agents to include in the model"
    ),
    "graphfile": './osm_nets/gss.osm'
}

server = mesa.visualization.ModularServer(
    TransInfraNetworkModel,
    [chart],
    "Transportation Infrastructure Model",
    model_params,
)

server.port = 8521