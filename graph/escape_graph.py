import networkx as nx

# ESTADOS POSIBLES DE UN NODOS
NODE_SOLVED    = "solved"
NODE_AVAILABLE = "available"
NODE_LOCKED    = "locked"

class EscapeGraph:

    def __init__(self):
        self.graph = nx.DiGraph()
        self.start_node = None
        self.goal_node = None

# CONSTRUCCION DEL GRAFO

    def add_node(self, node_id, status=NODE_AVAILABLE, puzzle=None):
         
# AGREGA UN NODO AL GRAFO

        self.graph.add_node(node_id, status=status, puzzle=puzzle)

    def add_edge(self, from_node, to_node, cost=1):
        """Agrega una arista dirigida con un costo asociado."""
        self.graph.add_edge(from_node, to_node, cost=cost)

    def set_start(self, node_id):
        self.start_node = node_id
        self.set_status(node_id, NODE_SOLVED)

    def set_goal(self, node_id):
        self.goal_node = node_id

# CONSULTAS DE ESTADO

    def get_status(self, node_id):
        return self.graph.nodes[node_id]["status"]

    def is_locked(self, node_id):
        return self.get_status(node_id) == NODE_LOCKED

    def is_solved(self, node_id):
        return self.get_status(node_id) == NODE_SOLVED

    def get_puzzle(self, node_id):
        return self.graph.nodes[node_id].get("puzzle", None)

    def get_neighbors(self, node_id):
        return list(self.graph.successors(node_id))

    def get_edge_cost(self, from_node, to_node):
        return self.graph[from_node][to_node]["cost"]

    def get_all_nodes(self):
        return list(self.graph.nodes)

    def get_all_edges(self):
        return list(self.graph.edges(data=True))

# MODIFICACION DE ESTADO

    def set_status(self, node_id, status):
        self.graph.nodes[node_id]["status"] = status

    def unlock_node(self, node_id):
# DESBLOQIEO DE LOS NODOS DE FORMA PERSISTENTE
        if self.is_locked(node_id):
            self.set_status(node_id, NODE_SOLVED)

# print summary
    def summary(self):
        print(f"\nNodos ({self.graph.number_of_nodes()}):")
        for node, data in self.graph.nodes(data=True):
            marker = " (-) nodo bloqueado " if data["status"] == NODE_LOCKED else \
                     " (+) nodo resuelto " if data["status"] == NODE_SOLVED  else "(=) nodo disponible"
            print(f"  {marker} {node} → estado: {data['status']}")
        print(f"\nAristas ({self.graph.number_of_edges()}):")
        for u, v, data in self.graph.edges(data=True):
            print(f"  {u} ──({data['cost']})──▶ {v}")
        print(f"\nInicio: {self.start_node}  |  Meta: {self.goal_node}")