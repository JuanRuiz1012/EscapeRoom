# Escape Room Solver — Proyecto IA

Sistema que modela y resuelve automáticamente un escape room usando una arquitectura híbrida de búsqueda:
búsqueda no informada (BFS o DFS) a nivel global y A\* para resolver los acertijos de nodos bloqueados.

## Integrantes

- Jhorman Ricardo Loaiza 2359710
- Juan Diego Ospina 2359486
- Julian Andres Rojas 2459687
- Mauricio Alejandro Rojas 2359701
- Juan Felipe Ruiz 2359397

## Estructura del proyecto

```
ProyectoIA1/
├── graph/
│   ├── __init__.py          
│   ├── escape_graph.py      
│   ├── example_graph.py    
│   └── puzzle_solver.py     
├── ui/
│   ├── console_panel.py    
│   ├── graph_canvas.py     
│   ├── main_window.py       
│   ├── puzzle_canvas.py     
│   └── stats_panel.py       
├── search.py               
├── main.py                 
├── test_puzzle_solver.py    
└── README.md
```

## Requisitos

- Python 3.10 o superior
- Librería `networkx`
- `tkinter` incluido en Python

## Instalación

**1. Crear entorno virtual**

```bash
python -m venv venv
```

**2. Activarlo**

- Windows CMD: `venv\Scripts\activate`
- macOS / Linux: `source venv/bin/activate`

**3. Instalar dependencias**

```bash
pip install networkx
```

## Ejecución

### Interfaz gráfica

```bash
python main.py
```

### Ver solo el grafo en consola

```bash
python -m graph.example_graph
```

### Ejecutar tests del solver A\*

```bash
python test_puzzle_solver.py
```

## Cómo funciona

1. Abre la aplicación con `python main.py`.
2. Selecciona el algoritmo global (**BFS** o **DFS**) en el menú desplegable.
3. Presiona **▶ Run**.
4. El algoritmo recorre el grafo global. Cada nodo expandido se marca en verde.
5. Cuando encuentra un nodo bloqueado, activa el **Puzzle Solver** en el panel derecho.
6. El A\* resuelve el sub-grafo del puzzle paso a paso.
7. Al resolver el puzzle, el nodo queda **desbloqueado de forma persistente**: si otra ruta llega a él, no se vuelve a resolver.
8. El solver continúa hasta alcanzar el nodo meta **L**.
9. Las estadísticas (nodos expandidos, profundidad, costo, tiempo) se actualizan en tiempo real.
10. Usa **↺ Reset** para volver al estado inicial y probar de nuevo.

## Decisiones de diseño relevantes

### Desbloqueo persistente

`escape_graph.unlock_node(node_id)` cambia el estado del nodo de `locked` a `solved`.
A partir de ese momento, `is_locked()` devuelve `False`, por lo que cualquier camino
posterior que llegue a ese nodo lo trata como disponible sin re-ejecutar el puzzle.

### Heurística del A\*

`h(n) = saltos_mínimos_al_goal × costo_mínimo_de_arista`

Se calcula con BFS inverso desde el goal. Es admisible: nunca sobreestima el costo real.

### Integración BFS/DFS ↔ A\*

`search.py` contiene la función `run_search(escape_graph, algo, app)` que la UI llama
en un hilo separado al presionar Run. Internamente llama a `_bfs` o `_dfs`, y cuando
encuentra un nodo bloqueado delega en `_unlock_with_puzzle`, que instancia `PuzzleSolver`
y notifica cada paso a la interfaz mediante los métodos `app.notify_*`.