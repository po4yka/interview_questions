---
id: cs-ds-graphs
title: Graph Data Structures
topic: data_structures
difficulty: medium
tags:
- cs_data_structures
- graphs
anki_cards:
- slug: cs-ds-graphs-0-en
  language: en
  anki_id: 1769160677624
  synced_at: '2026-01-23T13:31:19.018514'
- slug: cs-ds-graphs-0-ru
  language: ru
  anki_id: 1769160677650
  synced_at: '2026-01-23T13:31:19.019923'
- slug: cs-ds-graphs-1-en
  language: en
  anki_id: 1769160677674
  synced_at: '2026-01-23T13:31:19.021497'
- slug: cs-ds-graphs-1-ru
  language: ru
  anki_id: 1769160677699
  synced_at: '2026-01-23T13:31:19.023297'
- slug: cs-ds-graphs-2-en
  language: en
  anki_id: 1769160677724
  synced_at: '2026-01-23T13:31:19.026451'
- slug: cs-ds-graphs-2-ru
  language: ru
  anki_id: 1769160677751
  synced_at: '2026-01-23T13:31:19.028444'
---
# Graph Data Structures

## Graph Basics

**Graph G = (V, E)**: Set of vertices V and edges E connecting them.

### Types of Graphs

| Type | Description |
|------|-------------|
| **Directed** | Edges have direction (u -> v) |
| **Undirected** | Edges are bidirectional |
| **Weighted** | Edges have numeric values |
| **Unweighted** | All edges equal |
| **Cyclic** | Contains at least one cycle |
| **Acyclic** | No cycles (DAG if directed) |
| **Connected** | Path exists between any two vertices |
| **Sparse** | E << V^2 |
| **Dense** | E ~ V^2 |

### Terminology

- **Degree**: Number of edges connected to vertex
  - In directed: in-degree (incoming) and out-degree (outgoing)
- **Path**: Sequence of vertices connected by edges
- **Cycle**: Path that starts and ends at same vertex
- **Connected component**: Maximal connected subgraph

## Graph Representations

### 1. Adjacency List

Array of lists, each containing neighbors of a vertex.

```python
# Unweighted
graph = {
    0: [1, 2],
    1: [0, 3],
    2: [0, 3],
    3: [1, 2]
}

# Weighted
weighted_graph = {
    0: [(1, 5), (2, 3)],  # (neighbor, weight)
    1: [(0, 5), (3, 2)],
    2: [(0, 3), (3, 7)],
    3: [(1, 2), (2, 7)]
}
```

**Space**: O(V + E)

**Time complexity**:
| Operation | Time |
|-----------|------|
| Add vertex | O(1) |
| Add edge | O(1) |
| Remove edge | O(E) |
| Check edge exists | O(degree) |
| Iterate neighbors | O(degree) |

**Best for**: Sparse graphs, most algorithms.

### 2. Adjacency Matrix

2D array where matrix[i][j] = 1 if edge exists.

```python
# Unweighted (4 vertices)
matrix = [
    [0, 1, 1, 0],
    [1, 0, 0, 1],
    [1, 0, 0, 1],
    [0, 1, 1, 0]
]

# Weighted (0 = no edge, or use float('inf'))
weighted_matrix = [
    [0, 5, 3, 0],
    [5, 0, 0, 2],
    [3, 0, 0, 7],
    [0, 2, 7, 0]
]
```

**Space**: O(V^2)

**Time complexity**:
| Operation | Time |
|-----------|------|
| Add vertex | O(V^2) |
| Add edge | O(1) |
| Remove edge | O(1) |
| Check edge exists | O(1) |
| Iterate neighbors | O(V) |

**Best for**: Dense graphs, frequent edge queries.

### 3. Edge List

List of all edges as tuples.

```python
# Unweighted
edges = [(0, 1), (0, 2), (1, 3), (2, 3)]

# Weighted
weighted_edges = [(0, 1, 5), (0, 2, 3), (1, 3, 2), (2, 3, 7)]
```

**Space**: O(E)

**Best for**: Kruskal's algorithm, simple storage.

### Comparison

| Representation | Space | Edge Query | Iterate Neighbors |
|----------------|-------|------------|-------------------|
| Adjacency List | O(V+E) | O(degree) | O(degree) |
| Adjacency Matrix | O(V^2) | O(1) | O(V) |
| Edge List | O(E) | O(E) | O(E) |

## Implementation

### Graph Class with Adjacency List

```python
class Graph:
    def __init__(self, directed=False):
        self.adj = {}
        self.directed = directed

    def add_vertex(self, v):
        if v not in self.adj:
            self.adj[v] = []

    def add_edge(self, u, v, weight=1):
        self.add_vertex(u)
        self.add_vertex(v)
        self.adj[u].append((v, weight))
        if not self.directed:
            self.adj[v].append((u, weight))

    def remove_edge(self, u, v):
        self.adj[u] = [(n, w) for n, w in self.adj[u] if n != v]
        if not self.directed:
            self.adj[v] = [(n, w) for n, w in self.adj[v] if n != u]

    def has_edge(self, u, v):
        return any(n == v for n, _ in self.adj.get(u, []))

    def neighbors(self, v):
        return [n for n, _ in self.adj.get(v, [])]

    def degree(self, v):
        return len(self.adj.get(v, []))

    def vertices(self):
        return list(self.adj.keys())

    def edges(self):
        result = []
        seen = set()
        for u in self.adj:
            for v, w in self.adj[u]:
                if self.directed or (v, u) not in seen:
                    result.append((u, v, w))
                    seen.add((u, v))
        return result
```

## Special Graph Types

### Directed Acyclic Graph (DAG)

Directed graph with no cycles. Used for:
- Topological sorting
- Dependency resolution
- Task scheduling

### Bipartite Graph

Vertices can be divided into two sets with edges only between sets.

**Detection**: BFS/DFS coloring - if we can 2-color the graph, it's bipartite.

```python
def is_bipartite(graph):
    color = {}

    def bfs(start):
        queue = [start]
        color[start] = 0
        while queue:
            node = queue.pop(0)
            for neighbor in graph[node]:
                if neighbor not in color:
                    color[neighbor] = 1 - color[node]
                    queue.append(neighbor)
                elif color[neighbor] == color[node]:
                    return False
        return True

    for vertex in graph:
        if vertex not in color:
            if not bfs(vertex):
                return False
    return True
```

### Complete Graph

Every vertex connected to every other vertex. E = V(V-1)/2.

### Tree

Connected acyclic graph. E = V - 1.

## Union-Find (Disjoint Set)

Efficient structure for tracking connected components.

```python
class UnionFind:
    def __init__(self, n):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n  # Number of components

    def find(self, x):
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])  # Path compression
        return self.parent[x]

    def union(self, x, y):
        px, py = self.find(x), self.find(y)
        if px == py:
            return False

        # Union by rank
        if self.rank[px] < self.rank[py]:
            px, py = py, px
        self.parent[py] = px
        if self.rank[px] == self.rank[py]:
            self.rank[px] += 1
        self.count -= 1
        return True

    def connected(self, x, y):
        return self.find(x) == self.find(y)

    def get_count(self):
        return self.count
```

**Complexity**: O(alpha(n)) per operation where alpha is inverse Ackermann (effectively constant).

**Applications**:
- Cycle detection (undirected)
- Kruskal's MST
- Connected components
- Network connectivity

## Graph Problems Quick Reference

| Problem | Algorithm | Complexity |
|---------|-----------|------------|
| Connectivity | BFS/DFS | O(V + E) |
| Shortest path (unweighted) | BFS | O(V + E) |
| Shortest path (weighted) | Dijkstra | O((V+E) log V) |
| All pairs shortest | Floyd-Warshall | O(V^3) |
| MST | Kruskal/Prim | O(E log V) |
| Cycle detection | DFS | O(V + E) |
| Topological sort | Kahn/DFS | O(V + E) |
| Strongly connected | Tarjan/Kosaraju | O(V + E) |
| Bipartite check | BFS coloring | O(V + E) |

## Interview Tips

1. **Clarify graph properties**: Directed? Weighted? Cyclic? Connected?
2. **Choose representation**: Adjacency list for most cases
3. **Consider Union-Find**: For dynamic connectivity problems
4. **Watch for disconnected graphs**: Handle multiple components
5. **Edge cases**: Empty graph, single vertex, self-loops
