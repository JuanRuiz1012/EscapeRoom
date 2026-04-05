from graph.escape_graph import EscapeGraph, NODE_LOCKED
from search import bfs_escape

def build_example_graph():
     
##### CREACIÓN DEL GRAFO

    g = EscapeGraph()

##### PUZZLE QUE DESBLOQUEA EL NODO """C"""
    puzzle_C = {
        "nodes": ["S", "B", "C", "D", "E"],
###### EDGES SON LAS ARISTAS 
        "edges": [
            ("S", "B", 7),
            ("B", "C", 8),
            ("B", "D", 3),
            ("D", "E", 2),
            ("C", "E", 4),
        ],
        "start": "S",
        "goal":  "E"
    }

##### NODOS DEL GRAFO
    g.add_node("A")
    g.add_node("B")
    g.add_node("C", status=NODE_LOCKED, puzzle=puzzle_C)
    g.add_node("E")
    g.add_node("G")
    g.add_node("H")
    g.add_node("I")
    g.add_node("J")
    g.add_node("K")
    g.add_node("L")
    g.add_node("M")

##### ARISTAS DEL GRAFO
    g.add_edge("A", "B")
    g.add_edge("A", "E")
    g.add_edge("B", "C")
    g.add_edge("E", "C")
    g.add_edge("E", "G")
    g.add_edge("C", "I")
    g.add_edge("G", "K")
    g.add_edge("H", "G")
    g.add_edge("H", "J")
    g.add_edge("I", "L")
    g.add_edge("K", "M")

######## INICIO DEL GRAFO Y LA META 
    g.set_start("A")
    g.set_goal("L")

    return g


if __name__ == "__main__":
    grafo = build_example_graph()
    grafo.summary()
    
    bfs_escape(grafo)