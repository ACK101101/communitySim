import math

import solara
from matplotlib.figure import Figure
from matplotlib.ticker import MaxNLocator
from mesa.experimental import JupyterViz, make_text
from trans_infra.model import TransInfraNetworkModel


def agent_portrayal(graph):
    def get_agent(node):
        return graph.nodes[node]["agent"][0]

    edge_width = []
    edge_color = []
    for u, v in graph.edges():
        agent1 = get_agent(u)
        agent2 = get_agent(v)
        w = 2
        ec = "#e8e8e8"
        if State.RESISTANT in (agent1.state, agent2.state):
            w = 3
            ec = "black"
        edge_width.append(w)
        edge_color.append(ec)
    node_color_dict = {
        State.INFECTED: "tab:red",
        State.SUSCEPTIBLE: "tab:green",
        State.RESISTANT: "tab:gray",
    }
    node_color = [node_color_dict[get_agent(node).state] for node in graph.nodes()]
    return {
        "width": edge_width,
        "edge_color": edge_color,
        "node_color": node_color,
    }


def make_plot(model):
    # This is for the case when we want to plot multiple measures in 1 figure.
    # We could incorporate this into core Mesa.
    fig = Figure()
    ax = fig.subplots()
    measures = ["Infected", "Susceptible", "Resistant"]
    colors = ["tab:red", "tab:green", "tab:gray"]
    for i, m in enumerate(measures):
        color = colors[i]
        df = model.datacollector.get_model_vars_dataframe()
        ax.plot(df.loc[:, m], label=m, color=color)
    fig.legend()
    # Set integer x axis
    ax.xaxis.set_major_locator(MaxNLocator(integer=True))
    solara.FigureMatplotlib(fig)


model_params = {
    "num_agents": {
        "type": "SliderInt",
        "value": 10,
        "label": "Number of agents",
        "min": 10,
        "max": 100,
        "step": 1,
    },
    "graphfile": './gss.osm'
}

page = JupyterViz(
    VirusOnNetwork,
    model_params,
    measures=[
        make_plot,
        make_text(get_resistant_susceptible_ratio),
    ],
    name="Virus Model",
    agent_portrayal=agent_portrayal,
)
page  # noqa