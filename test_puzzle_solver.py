

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from graph.puzzle_solver import PuzzleSolver

def test_passed(nombre):
    print(f"  ✅ PASSED: {nombre}")

def test_failed(nombre, detalle):
    print(f"  ❌ FAILED: {nombre} → {detalle}")

# ──────────────────────────────────────────────────────────────────────
# TEST 1: Camino óptimo (el del ejemplo del proyecto)
# S→B→D→E cuesta 12, S→B→C→E cuesta 19 → A* debe elegir 12
# ──────────────────────────────────────────────────────────────────────
def test_camino_optimo():
    puzzle = {
        "nodes": ["S", "B", "C", "D", "E"],
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
    solver = PuzzleSolver(puzzle)
    solved = solver.solve()

    assert solved == True,                      "Debería encontrar solución"
    assert solver.total_cost == 12,             f"Costo esperado 12, obtuvo {solver.total_cost}"
    assert solver.path == ["S","B","D","E"],    f"Camino esperado S→B→D→E, obtuvo {solver.path}"
    test_passed("Camino óptimo S→B→D→E con costo 12")

# ──────────────────────────────────────────────────────────────────────
# TEST 2: Puzzle sin solución (goal no alcanzable)
# ──────────────────────────────────────────────────────────────────────
def test_sin_solucion():
    puzzle = {
        "nodes": ["S", "A", "B"],
        "edges": [
            ("S", "A", 5),   # B no tiene aristas entrantes → no se puede llegar
        ],
        "start": "S",
        "goal":  "B"
    }
    solver = PuzzleSolver(puzzle)
    solved = solver.solve()

    assert solved == False, "Debería retornar False cuando no hay solución"
    test_passed("Puzzle sin solución retorna False")

# ──────────────────────────────────────────────────────────────────────
# TEST 3: Camino directo (un solo paso)
# ──────────────────────────────────────────────────────────────────────
def test_camino_directo():
    puzzle = {
        "nodes": ["S", "E"],
        "edges": [
            ("S", "E", 3),
        ],
        "start": "S",
        "goal":  "E"
    }
    solver = PuzzleSolver(puzzle)
    solved = solver.solve()

    assert solved == True,               "Debería encontrar solución"
    assert solver.total_cost == 3,       f"Costo esperado 3, obtuvo {solver.total_cost}"
    assert solver.path == ["S", "E"],    f"Camino esperado S→E, obtuvo {solver.path}"
    test_passed("Camino directo S→E con costo 3")

# ──────────────────────────────────────────────────────────────────────
# TEST 4: Métricas se registran correctamente
# ──────────────────────────────────────────────────────────────────────
def test_metricas():
    puzzle = {
        "nodes": ["S", "B", "C", "D", "E"],
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
    solver = PuzzleSolver(puzzle)
    solver.solve()
    metrics = solver.get_metrics()

    assert "nodes_expanded"  in metrics,         "Falta nodes_expanded en métricas"
    assert "total_cost"      in metrics,         "Falta total_cost en métricas"
    assert "execution_time"  in metrics,         "Falta execution_time en métricas"
    assert "path"            in metrics,         "Falta path en métricas"
    assert metrics["nodes_expanded"] > 0,        "nodes_expanded debe ser mayor a 0"
    assert metrics["execution_time"] >= 0,       "execution_time debe ser >= 0"
    test_passed("Métricas registradas correctamente")

# ──────────────────────────────────────────────────────────────────────
# TEST 5: Log se genera correctamente
# ──────────────────────────────────────────────────────────────────────
def test_log():
    puzzle = {
        "nodes": ["S", "E"],
        "edges": [("S", "E", 1)],
        "start": "S",
        "goal":  "E"
    }
    solver = PuzzleSolver(puzzle)
    solver.solve()

    assert len(solver.log) > 0,                          "El log no debe estar vacío"
    assert any("Expanding" in l for l in solver.log),    "Log debe tener mensajes de expansión"
    assert any("Solved" in l for l in solver.log),       "Log debe confirmar que se resolvió"
    test_passed("Log generado correctamente")


# ──────────────────────────────────────────────────────────────────────
# EJECUTAR TODOS LOS TESTS
# ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n══ Tests PuzzleSolver (A*) ══════════════════\n")
    tests = [
        test_camino_optimo,
        test_sin_solucion,
        test_camino_directo,
        test_metricas,
        test_log,
    ]
    passed = 0
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            test_failed(test.__name__, str(e))
        except Exception as e:
            test_failed(test.__name__, f"Error inesperado: {e}")

    print(f"\n══ Resultado: {passed}/{len(tests)} tests pasaron ════════════\n")