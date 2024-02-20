import mesa
import numpy as np
import networkx as nx
import osmnx as ox
from scipy.sparse import dok_matrix

def compute_total_social(model):
    return sum([np.sum(model.A_social[agent]) for agent in range(model.num_agents)])

def get_max_idxs(arr):
    """Returns indicies of maximum elements in arr"""
    curr_max = 0
    max_idxs = []
    for i, a in enumerate(arr):
        if a > curr_max:
            curr_max = a
            max_idxs = [i]
        elif a == curr_max:
            max_idxs.append(i)
    return max_idxs


class TransInfraNetworkModel(mesa.Model):
    """Transit & place network inhabited by agents"""
    
    def __init__(self, num_agents, graphfile) -> None:
        super().__init__()
        # init environment
        self.graphfile = graphfile
        self.G_trans = self.load_network()                                  # load in modified OSM network
        self.nodes = self.G_trans.nodes(data=True)
        self.space = mesa.space.NetworkGrid(self.G_trans)                   # built-in class for network spaces
        
        # node types for faster search
        self.sleep_nodes = [k for k, v in self.nodes if v['general'] == 'sleep']
        self.work_nodes = [k for k, v in self.nodes if v['general'] == 'work']
        self.social_nodes = [k for k, v in self.nodes if v['general'] == 'social']
        self.node_types = {"sleep": self.sleep_nodes, "work": self.work_nodes, 
                           "social": self.social_nodes}
        
        # init agents
        self.num_agents = num_agents
        self.thresh = 5                                                     # sets thresh for agent-wise needs (ie. sleep)
        self.A_social = dok_matrix((self.num_agents, self.num_agents))      # sparse matrix representation for social ties adjacency list
        self.schedule = mesa.time.RandomActivation(self)                    # controls move order of agents @ each time step
        self.populate()
        
        # built-in class for collecting info for analysis / viz
        self.datacollector = mesa.DataCollector(model_reporters={'Total Social': compute_total_social},
                                                agent_reporters={})
        self.datacollector.collect(self)
    
    def populate(self) -> None:
        # populate network with agents and add each to schedule 
        for i in range(self.num_agents):
            a = PersonAgent(i, self)
            self.schedule.add(a)
            s_nodeid = np.random.choice(self.sleep_nodes)
            self.space.place_agent(a, s_nodeid)
    
    def step(self) -> None:
        """defines what happens each global timestep"""
        self.schedule.step()
        self.datacollector.collect(self)
    
    def load_network(self) -> nx.Graph:
        """loads in modified OSM graph"""
        G_trans = ox.load_graphml(
                    self.graphfile,
                    node_dtypes={'building':str, 'general':str, 'color':str, 'x':float, 'y':float, 'geometry':str},
                    edge_dtypes={'osmid':int, 'highway':str, 'general':str, 'color':str, 'length':float, 'geometry':str})
        G_trans = G_trans.to_undirected()                                   # make undirected
        return G_trans


class PersonAgent(mesa.Agent):
    """An agent that moves around the network collecting resources"""
    
    def __init__(self, unique_id: int, model: mesa.Model) -> None:
        super().__init__(unique_id, model)
        self.needs_type = ["sleep", "work", "social"]
        self.needs_curr = np.zeros(len(self.needs_type))
        self.threshes = np.ones(len(self.needs_type)) * self.model.thresh
        self.path = []
        
    def step(self) -> None:
        """Defines what happens each local timestep"""
        self.action()
        self.move()
        self.talk()
        
    def action(self) -> None:
        # if enroute to a target node, keep moving
        
        # if at target node, collect resource OR
        #   find new target
        pass
    
    def search(self) -> int:
        """Searches for next move based on needs and network"""
        # TODO: use heuristic for narrowing down search so not |n_d|
        # select most urgent need, break ties randomly
        urgent = self.threshes / (self.needs_curr + 1)
        need_idxs = get_max_idxs(urgent)
        target_need = self.needs_type[ np.random.choice(need_idxs) ]
        # search for nodes with attr, choose lowest dist
        min_dist, min_path = np.inf, []
        for t_node in self.model.node_types[ target_need ]:
            dist, path = nx.single_source_dijkstra(self.model.G_trans, 
                                             self.pos, t_node, 
                                             weight="length")
            if dist < min_dist: 
                min_dist, min_path = dist, path
        self.path = min_path[1:]
        
    def move(self) -> None:
        """Move to random neighboring node"""
        # TODO: factor in edge type into speed
        # if enroute to new dest, move along path
        if len(self.path) > 0: 
            self.model.space.move_agent(self, self.path[0])
            self.path = self.path[1:]
        # TODO: option to wait and collect resource or move to new place     
        # if at dest
        else:
            new_t = self.search()
    
    def talk(self) -> None:
        # TODO: implement smarter choice based on social history
        """Chose random agent in same node to build social tie with"""
        nodemates = self.model.space.get_cell_list_contents([self.pos])
        if len(nodemates) > 1:
            other = self.random.choice(nodemates)
            # can't become friends with self
            while other.unique_id == self.unique_id:
                other = self.random.choice(nodemates)
            # curr_social = self.model.A_social[self.unique_id, other.unique_id]
            self.model.A_social[self.unique_id, other.unique_id] += 1
            self.model.A_social[other.unique_id, self.unique_id] += 1
            