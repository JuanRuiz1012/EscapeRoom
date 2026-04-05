from collections import deque
from graph.escape_graph import NODE_SOLVED

def bfs_escape(graph):
    start = graph.start_node
    goal = graph.goal_node

    queue = deque([[start]])
    visited = set()
    en_cola = set([start])

    nodos_expandidos = 0
    max_profundidad = 0

    print(f"Iniciando BFS desde {start} hacia {goal}\n")

    while queue:
        path = queue.popleft()
        current = path[-1]

        en_cola.discard(current)
        nodos_expandidos += 1

        profundidad_actual = len(path) - 1
        if profundidad_actual > max_profundidad:
            max_profundidad = profundidad_actual

        print(f"Explorando nodo: {current}")

        if current == goal:
            print("\nMETA ENCONTRADA")
            print("Camino:", " -> ".join(path))
            print(f"Nodos expandidos: {nodos_expandidos}")
            print(f"Profundidad maxima alcanzada: {max_profundidad}")
            return path

        if current not in visited:
            visited.add(current)

            neighbors = graph.get_neighbors(current)

            for neighbor in neighbors:
                if neighbor not in visited and neighbor not in en_cola:

                    print(f"  Revisando vecino: {neighbor}")

                    if graph.is_locked(neighbor):
                        print(f"  Nodo {neighbor} esta bloqueado. Resolviendo puzzle...")

                        puzzle = graph.get_puzzle(neighbor)
                        solve_puzzle(puzzle)

                        graph.unlock_node(neighbor)
                        print(f"  Nodo {neighbor} desbloqueado")

                    graph.set_status(neighbor, NODE_SOLVED)

                    new_path = list(path)
                    new_path.append(neighbor)
                    queue.append(new_path)

                    en_cola.add(neighbor)

    print("No se encontro solucion")
    print(f"Nodos expandidos: {nodos_expandidos}")
    print(f"Profundidad maxima alcanzada: {max_profundidad}")
    return None


def solve_puzzle(puzzle):
    print("    Resolviendo subproblema con A* (simulado)")
    print(f"    Nodo inicial: {puzzle['start']}")
    print(f"    Nodo objetivo: {puzzle['goal']}")