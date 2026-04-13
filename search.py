import time
from collections import deque

from graph.escape_graph import NODE_SOLVED
from graph.puzzle_solver import PuzzleSolver

DELAY = 0.5

# punto de entrada llamado por la UI 

def run_search(escape_graph, algo, app):
    if algo == "dfs":
        _dfs(escape_graph, app)
    else:
        _bfs(escape_graph, app)


# resolucion de puzzle (A*) con notificaciones a la UI 

def _unlock_with_puzzle(node_id, escape_graph, app):
    puzzle = escape_graph.get_puzzle(node_id)

    # si el nodo no tiene puzzle asociado, se desbloquea directo
    if not puzzle:
        escape_graph.unlock_node(node_id)
        return

    app.notify_locked(node_id)
    time.sleep(DELAY)
    app.notify_puzzle_start(puzzle)
    time.sleep(DELAY)

    solver = PuzzleSolver(puzzle)
    solved = solver.solve()

    if not solved:
        return

    # reproducir expansiones del A* paso a paso en la UI
    step = 0
    for entry in solver.log:
        if "Expanding node" in entry:
            step += 1
            pnode = entry[entry.find("{") + 1 : entry.find("}")]
            app.notify_puzzle_step(pnode)
            app.update_stats_puzzle(step, solver.total_cost)
            time.sleep(DELAY)

    m = solver.get_metrics()
    app.update_stats_puzzle(m["nodes_expanded"], m["total_cost"])
    app.notify_puzzle_solved(puzzle["goal"], node_id)

    # desbloqueo persistente: de aqui en adelante el nodo queda resuelto
    escape_graph.unlock_node(node_id)
    time.sleep(DELAY)


# BFS global

def _bfs(escape_graph, app):
    start = escape_graph.start_node
    goal  = escape_graph.goal_node

    queue    = deque([[start]])
    visited  = set()
    expanded = 0

    while queue:
        path    = queue.popleft()
        current = path[-1]

        if current in visited:
            continue
        visited.add(current)
        expanded += 1
        depth = len(path) - 1

        escape_graph.set_status(current, NODE_SOLVED)
        app.notify_expand(current, path)
        app.update_stats_global(expanded, depth)
        time.sleep(DELAY)

        if current == goal:
            app.notify_goal_reached(current)
            return path

        for neighbor in escape_graph.get_neighbors(current):
            if neighbor not in visited:
                # si el nodo ya fue desbloqueado antes, is_locked() devuelve False
                # y no se vuelve a resolver el puzzle (desbloqueo persistente)
                if escape_graph.is_locked(neighbor):
                    _unlock_with_puzzle(neighbor, escape_graph, app)
                queue.append(path + [neighbor])

    return None


# DFS global

def _dfs(escape_graph, app):
    start = escape_graph.start_node
    goal  = escape_graph.goal_node

    stack     = [[start]]
    visited   = set()
    expanded  = 0
    max_depth = 0

    while stack:
        path    = stack.pop()
        current = path[-1]

        if current in visited:
            continue
        visited.add(current)
        expanded += 1
        depth = len(path) - 1
        if depth > max_depth:
            max_depth = depth

        escape_graph.set_status(current, NODE_SOLVED)
        app.notify_expand(current, path)
        app.update_stats_global(expanded, max_depth)
        time.sleep(DELAY)

        if current == goal:
            app.notify_goal_reached(current)
            return path

        # se agregan en orden inverso para que la pila explore de izquierda a derecha
        for neighbor in reversed(escape_graph.get_neighbors(current)):
            if neighbor not in visited:
                if escape_graph.is_locked(neighbor):
                    _unlock_with_puzzle(neighbor, escape_graph, app)
                stack.append(path + [neighbor])

    return None


# version consola (sin UI) para pruebas rapidas

def bfs_escape(graph):
    start = graph.start_node
    goal  = graph.goal_node

    queue    = deque([[start]])
    visited  = set()
    expanded = 0
    max_dep  = 0

    print(f"\nBFS: {start} -> {goal}\n")

    while queue:
        path    = queue.popleft()
        current = path[-1]

        if current in visited:
            continue
        visited.add(current)
        expanded += 1
        dep = len(path) - 1
        if dep > max_dep:
            max_dep = dep

        print(f"  Expandiendo: {current}")

        if current == goal:
            print("\n[META]", " -> ".join(path))
            print(f"Expandidos: {expanded}  Profundidad: {max_dep}")
            return path

        for neighbor in graph.get_neighbors(current):
            if neighbor not in visited:
                if graph.is_locked(neighbor):
                    print(f"  Nodo {neighbor} bloqueado - resolviendo puzzle...")
                    puzzle = graph.get_puzzle(neighbor)
                    if puzzle:
                        s = PuzzleSolver(puzzle)
                        s.solve()
                        s.print_metrics()
                    graph.unlock_node(neighbor)
                    print(f"  Nodo {neighbor} desbloqueado")
                queue.append(path + [neighbor])

    print("Sin solucion")
    return None