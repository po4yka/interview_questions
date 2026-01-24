---
id: cs-algo-graph
title: Graph Algorithms
topic: algorithms
difficulty: hard
tags:
- cs_algorithms
- graphs
anki_cards:
- slug: cs-algo-graph-0-en
  language: en
  anki_id: 1769160677926
  synced_at: '2026-01-23T13:31:19.037674'
- slug: cs-algo-graph-0-ru
  language: ru
  anki_id: 1769160677950
  synced_at: '2026-01-23T13:31:19.039515'
- slug: cs-algo-graph-1-en
  language: en
  anki_id: 1769160677974
  synced_at: '2026-01-23T13:31:19.040794'
- slug: cs-algo-graph-1-ru
  language: ru
  anki_id: 1769160677999
  synced_at: '2026-01-23T13:31:19.042025'
- slug: cs-algo-graph-2-en
  language: en
  anki_id: 1769160678025
  synced_at: '2026-01-23T13:31:19.043196'
- slug: cs-algo-graph-2-ru
  language: ru
  anki_id: 1769160678049
  synced_at: '2026-01-23T13:31:19.044557'
- slug: cs-algo-graph-3-en
  language: en
  anki_id: 1769160678075
  synced_at: '2026-01-23T13:31:19.046348'
- slug: cs-algo-graph-3-ru
  language: ru
  anki_id: 1769160678099
  synced_at: '2026-01-23T13:31:19.047835'
- slug: cs-algo-graph-4-en
  language: en
  anki_id: 1769160678124
  synced_at: '2026-01-23T13:31:19.049100'
- slug: cs-algo-graph-4-ru
  language: ru
  anki_id: 1769160678149
  synced_at: '2026-01-23T13:31:19.050285'
---
# Graph Algorithms

## Graph Representations

### Adjacency List

Best for sparse graphs. Space: O(V + E).

```python
graph = {
    'A': ['B', 'C'],
    'B': ['A', 'D'],
    'C': ['A', 'D'],
    'D': ['B', 'C']
}
```

### Adjacency Matrix

Best for dense graphs. Space: O(V^2).

```python
#     A  B  C  D
# A [[0, 1, 1, 0],
# B  [1, 0, 0, 1],
# C  [1, 0, 0, 1],
# D  [0, 1, 1, 0]]
```

## Traversal Algorithms

### Breadth-First Search (BFS)

**Mechanism**: Explore all neighbors before moving to next level. Uses queue.

**Complexity**: O(V + E)

**Use cases**: Shortest path (unweighted), level-order traversal, connectivity.

```python
from collections import deque

def bfs(graph, start):
    visited = set([start])
    queue = deque([start])
    result = []

    while queue:
        node = queue.popleft()
        result.append(node)

        for neighbor in graph[node]:
            if neighbor not in visited:
                visited.add(neighbor)
                queue.append(neighbor)

    return result
```

### Depth-First Search (DFS)

**Mechanism**: Explore as far as possible before backtracking. Uses stack/recursion.

**Complexity**: O(V + E)

**Use cases**: Cycle detection, topological sort, connected components, path finding.

```python
def dfs_recursive(graph, node, visited=None):
    if visited is None:
        visited = set()

    visited.add(node)
    result = [node]

    for neighbor in graph[node]:
        if neighbor not in visited:
            result.extend(dfs_recursive(graph, neighbor, visited))

    return result

def dfs_iterative(graph, start):
    visited = set()
    stack = [start]
    result = []

    while stack:
        node = stack.pop()
        if node not in visited:
            visited.add(node)
            result.append(node)
            # Add neighbors in reverse to maintain order
            for neighbor in reversed(graph[node]):
                if neighbor not in visited:
                    stack.append(neighbor)

    return result
```

## Shortest Path Algorithms

### Dijkstra's Algorithm

**Purpose**: Shortest path from source to all vertices (non-negative weights).

**Complexity**: O((V + E) log V) with binary heap.

**Limitation**: Doesn't work with negative weights.

```python
import heapq

def dijkstra(graph, start):
    distances = {node: float('inf') for node in graph}
    distances[start] = 0
    pq = [(0, start)]
    visited = set()

    while pq:
        curr_dist, node = heapq.heappop(pq)

        if node in visited:
            continue
        visited.add(node)

        for neighbor, weight in graph[node]:
            distance = curr_dist + weight
            if distance < distances[neighbor]:
                distances[neighbor] = distance
                heapq.heappush(pq, (distance, neighbor))

    return distances
```

### Bellman-Ford Algorithm

**Purpose**: Shortest path with negative weights, detects negative cycles.

**Complexity**: O(V * E)

```python
def bellman_ford(graph, start, vertices):
    distances = {v: float('inf') for v in vertices}
    distances[start] = 0

    # Relax all edges V-1 times
    for _ in range(len(vertices) - 1):
        for u in graph:
            for v, weight in graph[u]:
                if distances[u] + weight < distances[v]:
                    distances[v] = distances[u] + weight

    # Check for negative cycles
    for u in graph:
        for v, weight in graph[u]:
            if distances[u] + weight < distances[v]:
                raise ValueError("Negative cycle detected")

    return distances
```

### Floyd-Warshall Algorithm

**Purpose**: All-pairs shortest path.

**Complexity**: O(V^3)

```python
def floyd_warshall(graph, n):
    dist = [[float('inf')] * n for _ in range(n)]

    # Initialize
    for i in range(n):
        dist[i][i] = 0
    for u, v, w in graph:  # edges as (from, to, weight)
        dist[u][v] = w

    # Dynamic programming
    for k in range(n):
        for i in range(n):
            for j in range(n):
                dist[i][j] = min(dist[i][j], dist[i][k] + dist[k][j])

    return dist
```

### A* Algorithm

**Purpose**: Shortest path with heuristic (informed search).

**Complexity**: Depends on heuristic quality.

**Key**: f(n) = g(n) + h(n) where g = cost so far, h = heuristic estimate.

```python
def astar(graph, start, goal, heuristic):
    open_set = [(0, start)]
    came_from = {}
    g_score = {start: 0}

    while open_set:
        _, current = heapq.heappop(open_set)

        if current == goal:
            return reconstruct_path(came_from, current)

        for neighbor, weight in graph[current]:
            tentative_g = g_score[current] + weight

            if tentative_g < g_score.get(neighbor, float('inf')):
                came_from[neighbor] = current
                g_score[neighbor] = tentative_g
                f_score = tentative_g + heuristic(neighbor, goal)
                heapq.heappush(open_set, (f_score, neighbor))

    return None  # No path found
```

## Topological Sort

**Purpose**: Linear ordering of vertices in DAG where u comes before v if edge u->v exists.

**Use cases**: Build systems, task scheduling, course prerequisites.

### Kahn's Algorithm (BFS)

```python
from collections import deque

def topological_sort_kahn(graph, vertices):
    in_degree = {v: 0 for v in vertices}
    for u in graph:
        for v in graph[u]:
            in_degree[v] += 1

    queue = deque([v for v in vertices if in_degree[v] == 0])
    result = []

    while queue:
        node = queue.popleft()
        result.append(node)

        for neighbor in graph.get(node, []):
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if len(result) != len(vertices):
        raise ValueError("Cycle detected")

    return result
```

### DFS-based

```python
def topological_sort_dfs(graph, vertices):
    visited = set()
    stack = []

    def dfs(node):
        visited.add(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                dfs(neighbor)
        stack.append(node)

    for vertex in vertices:
        if vertex not in visited:
            dfs(vertex)

    return stack[::-1]
```

## Minimum Spanning Tree

### Kruskal's Algorithm

**Approach**: Sort edges, add smallest edge that doesn't create cycle.

**Complexity**: O(E log E)

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        return True

def kruskal(n, edges):
    edges.sort(key=lambda x: x[2])  # Sort by weight
    uf = UnionFind(n)
    mst = []

    for u, v, w in edges:
        if uf.union(u, v):
            mst.append((u, v, w))
            if len(mst) == n - 1:
                break

    return mst
```

### Prim's Algorithm

**Approach**: Start from vertex, always add minimum edge connecting to MST.

**Complexity**: O((V + E) log V) with binary heap.

## Cycle Detection

### Undirected Graph (Union-Find)

```python
def has_cycle_undirected(n, edges):
    uf = UnionFind(n)
    for u, v in edges:
        if uf.find(u) == uf.find(v):
            return True
        uf.union(u, v)
    return False
```

### Directed Graph (DFS with colors)

```python
def has_cycle_directed(graph):
    WHITE, GRAY, BLACK = 0, 1, 2
    color = {node: WHITE for node in graph}

    def dfs(node):
        color[node] = GRAY
        for neighbor in graph.get(node, []):
            if color[neighbor] == GRAY:  # Back edge
                return True
            if color[neighbor] == WHITE and dfs(neighbor):
                return True
        color[node] = BLACK
        return False

    return any(dfs(node) for node in graph if color[node] == WHITE)
```

## Algorithm Selection Guide

| Problem | Algorithm | Complexity |
|---------|-----------|------------|
| Shortest path (unweighted) | BFS | O(V + E) |
| Shortest path (non-negative) | Dijkstra | O((V+E) log V) |
| Shortest path (negative) | Bellman-Ford | O(V * E) |
| All pairs shortest | Floyd-Warshall | O(V^3) |
| MST | Kruskal/Prim | O(E log V) |
| Topological order | Kahn/DFS | O(V + E) |
| Cycle detection | DFS/Union-Find | O(V + E) |
