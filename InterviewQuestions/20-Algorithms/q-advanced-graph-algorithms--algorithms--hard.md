---
id: 20251012-200007
title: "Advanced Graph Algorithms (Dijkstra, MST, Floyd-Warshall) / Продвинутые алгоритмы на графах"
slug: advanced-graph-algorithms-algorithms-hard
topic: algorithms
subtopics:
  - graph
  - dijkstra
  - mst
  - shortest-path
  - minimum-spanning-tree
status: draft
difficulty: hard
moc: moc-algorithms
date_created: 2025-10-12
date_updated: 2025-10-12
related_questions:
  - q-graph-algorithms-bfs-dfs--algorithms--hard
  - q-dynamic-programming-fundamentals--algorithms--hard
  - q-binary-search-trees-bst--algorithms--hard
tags:
  - algorithms
  - graph
  - dijkstra
  - mst
  - shortest-path
  - floyd-warshall
  - bellman-ford
---

# Advanced Graph Algorithms

## English Version

### Problem Statement

Advanced graph algorithms are essential for solving complex shortest path and minimum spanning tree problems. These algorithms are fundamental in network routing, map applications, social networks, and infrastructure optimization.

**The Question:** How do Dijkstra's algorithm, Minimum Spanning Tree (Kruskal's, Prim's), Floyd-Warshall, and Bellman-Ford work? When should you use each one?

### Detailed Answer

---

### DIJKSTRA'S ALGORITHM

**Find shortest path from source to all other vertices (non-negative weights).**

#### Basic Implementation with Priority Queue

```kotlin
data class Edge(val to: Int, val weight: Int)

data class Node(val vertex: Int, val distance: Int) : Comparable<Node> {
    override fun compareTo(other: Node) = distance - other.distance
}

class Graph(val vertices: Int) {
    val adj = Array(vertices) { mutableListOf<Edge>() }

    fun addEdge(from: Int, to: Int, weight: Int) {
        adj[from].add(Edge(to, weight))
    }
}

fun dijkstra(graph: Graph, source: Int): IntArray {
    val distances = IntArray(graph.vertices) { Int.MAX_VALUE }
    distances[source] = 0

    val priorityQueue = PriorityQueue<Node>()
    priorityQueue.offer(Node(source, 0))

    val visited = BooleanArray(graph.vertices)

    while (priorityQueue.isNotEmpty()) {
        val (u, dist) = priorityQueue.poll()

        if (visited[u]) continue
        visited[u] = true

        // Relax all edges from u
        for (edge in graph.adj[u]) {
            val v = edge.to
            val weight = edge.weight

            if (distances[u] != Int.MAX_VALUE &&
                distances[u] + weight < distances[v]) {
                distances[v] = distances[u] + weight
                priorityQueue.offer(Node(v, distances[v]))
            }
        }
    }

    return distances
}

// Example usage:
val graph = Graph(5)
graph.addEdge(0, 1, 4)
graph.addEdge(0, 2, 1)
graph.addEdge(2, 1, 2)
graph.addEdge(1, 3, 1)
graph.addEdge(2, 3, 5)
graph.addEdge(3, 4, 3)

val distances = dijkstra(graph, 0)
println(distances.contentToString())  // [0, 3, 1, 4, 7]

// Time: O((V + E) log V) with priority queue
// Space: O(V)
```

**How it works:**
```
Graph:
    0
   /|\
  4 1 2
 /  |  \
1   2   3
 \  |  / \
  1 5 5   3
   \|/     \
    3-------4

Step-by-step:
Initial: dist[0]=0, all others=∞

Step 1: Visit 0
  - Update dist[1] = 4
  - Update dist[2] = 1
  PQ: [(2,1), (1,4)]

Step 2: Visit 2 (dist=1)
  - Update dist[1] = min(4, 1+2) = 3
  - Update dist[3] = 1+5 = 6
  PQ: [(1,3), (1,4), (3,6)]

Step 3: Visit 1 (dist=3)
  - Update dist[3] = min(6, 3+1) = 4
  PQ: [(3,4), (1,4), (3,6)]

Step 4: Visit 3 (dist=4)
  - Update dist[4] = 4+3 = 7
  PQ: [(4,7), (1,4), (3,6)]

Result: [0, 3, 1, 4, 7]
```

---

#### Dijkstra with Path Reconstruction

```kotlin
data class DijkstraResult(
    val distances: IntArray,
    val parents: IntArray
)

fun dijkstraWithPath(graph: Graph, source: Int): DijkstraResult {
    val distances = IntArray(graph.vertices) { Int.MAX_VALUE }
    val parents = IntArray(graph.vertices) { -1 }
    distances[source] = 0

    val pq = PriorityQueue<Node>()
    pq.offer(Node(source, 0))

    val visited = BooleanArray(graph.vertices)

    while (pq.isNotEmpty()) {
        val (u, dist) = pq.poll()

        if (visited[u]) continue
        visited[u] = true

        for (edge in graph.adj[u]) {
            val v = edge.to
            val weight = edge.weight

            if (distances[u] != Int.MAX_VALUE &&
                distances[u] + weight < distances[v]) {
                distances[v] = distances[u] + weight
                parents[v] = u  // Track parent
                pq.offer(Node(v, distances[v]))
            }
        }
    }

    return DijkstraResult(distances, parents)
}

fun reconstructPath(parents: IntArray, target: Int): List<Int> {
    val path = mutableListOf<Int>()
    var current = target

    while (current != -1) {
        path.add(current)
        current = parents[current]
    }

    return path.reversed()
}

// Example:
val result = dijkstraWithPath(graph, 0)
val pathTo4 = reconstructPath(result.parents, 4)
println("Path to 4: $pathTo4")  // [0, 2, 1, 3, 4]
println("Distance: ${result.distances[4]}")  // 7
```

---

#### Dijkstra for Android Navigation

```kotlin
// Real-world example: Route navigation
data class Location(val name: String, val lat: Double, val lon: Double)

data class Route(val to: Location, val distance: Double, val timeMinutes: Int)

class NavigationGraph {
    private val locations = mutableMapOf<Location, MutableList<Route>>()

    fun addRoute(from: Location, to: Location, distance: Double, time: Int) {
        locations.getOrPut(from) { mutableListOf() }
            .add(Route(to, distance, time))
    }

    fun findShortestPath(from: Location, to: Location): NavigationResult? {
        val distances = mutableMapOf<Location, Double>()
        val parents = mutableMapOf<Location, Location?>()
        val pq = PriorityQueue<Pair<Location, Double>>(compareBy { it.second })

        distances[from] = 0.0
        parents[from] = null
        pq.offer(from to 0.0)

        while (pq.isNotEmpty()) {
            val (current, dist) = pq.poll()

            if (current == to) break
            if (dist > (distances[current] ?: Double.MAX_VALUE)) continue

            for (route in locations[current] ?: emptyList()) {
                val newDist = dist + route.distance

                if (newDist < (distances[route.to] ?: Double.MAX_VALUE)) {
                    distances[route.to] = newDist
                    parents[route.to] = current
                    pq.offer(route.to to newDist)
                }
            }
        }

        return if (to in distances) {
            NavigationResult(
                path = reconstructLocationPath(parents, from, to),
                totalDistance = distances[to]!!
            )
        } else null
    }

    private fun reconstructLocationPath(
        parents: Map<Location, Location?>,
        from: Location,
        to: Location
    ): List<Location> {
        val path = mutableListOf<Location>()
        var current: Location? = to

        while (current != null) {
            path.add(current)
            current = parents[current]
        }

        return path.reversed()
    }
}

data class NavigationResult(
    val path: List<Location>,
    val totalDistance: Double
)
```

---

### MINIMUM SPANNING TREE (MST)

**Find subset of edges that connects all vertices with minimum total weight.**

#### Kruskal's Algorithm (Union-Find)

```kotlin
data class MSTEdge(val from: Int, val to: Int, val weight: Int) : Comparable<MSTEdge> {
    override fun compareTo(other: MSTEdge) = weight - other.weight
}

class UnionFind(size: Int) {
    private val parent = IntArray(size) { it }
    private val rank = IntArray(size) { 0 }

    fun find(x: Int): Int {
        if (parent[x] != x) {
            parent[x] = find(parent[x])  // Path compression
        }
        return parent[x]
    }

    fun union(x: Int, y: Int): Boolean {
        val rootX = find(x)
        val rootY = find(y)

        if (rootX == rootY) return false  // Already in same set

        // Union by rank
        when {
            rank[rootX] < rank[rootY] -> parent[rootX] = rootY
            rank[rootX] > rank[rootY] -> parent[rootY] = rootX
            else -> {
                parent[rootY] = rootX
                rank[rootX]++
            }
        }

        return true
    }
}

fun kruskalMST(vertices: Int, edges: List<MSTEdge>): List<MSTEdge> {
    val mst = mutableListOf<MSTEdge>()
    val uf = UnionFind(vertices)

    // Sort edges by weight
    val sortedEdges = edges.sorted()

    for (edge in sortedEdges) {
        // Add edge if it doesn't create cycle
        if (uf.union(edge.from, edge.to)) {
            mst.add(edge)

            // MST has exactly V-1 edges
            if (mst.size == vertices - 1) break
        }
    }

    return mst
}

// Example:
val edges = listOf(
    MSTEdge(0, 1, 4),
    MSTEdge(0, 2, 1),
    MSTEdge(1, 2, 2),
    MSTEdge(1, 3, 5),
    MSTEdge(2, 3, 8),
    MSTEdge(2, 4, 10),
    MSTEdge(3, 4, 2)
)

val mst = kruskalMST(5, edges)
val totalWeight = mst.sumOf { it.weight }

println("MST Edges:")
mst.forEach { println("${it.from} - ${it.to}: ${it.weight}") }
println("Total weight: $totalWeight")

// Output:
// 0 - 2: 1
// 1 - 2: 2
// 3 - 4: 2
// 0 - 1: 4
// Total weight: 9

// Time: O(E log E) for sorting
// Space: O(V)
```

**How Kruskal's works:**
```
All edges sorted by weight:
(0-2:1), (1-2:2), (3-4:2), (0-1:4), (1-3:5), (2-3:8), (2-4:10)

Step 1: Add 0-2 (weight 1) ✓
  Sets: {0,2}, {1}, {3}, {4}

Step 2: Add 1-2 (weight 2) ✓
  Sets: {0,1,2}, {3}, {4}

Step 3: Add 3-4 (weight 2) ✓
  Sets: {0,1,2}, {3,4}

Step 4: Add 0-1 (weight 4) ✗ (already connected)
  Skip

Step 5: Add 1-3 (weight 5) ✓
  Sets: {0,1,2,3,4}

Done! 4 edges selected (V-1 = 4)
```

---

#### Prim's Algorithm (Greedy + Priority Queue)

```kotlin
fun primMST(graph: Graph): List<MSTEdge> {
    val mst = mutableListOf<MSTEdge>()
    val visited = BooleanArray(graph.vertices)
    val pq = PriorityQueue<MSTEdge>()

    // Start from vertex 0
    visited[0] = true
    for (edge in graph.adj[0]) {
        pq.offer(MSTEdge(0, edge.to, edge.weight))
    }

    while (pq.isNotEmpty() && mst.size < graph.vertices - 1) {
        val edge = pq.poll()

        if (visited[edge.to]) continue  // Skip if creates cycle

        // Add edge to MST
        mst.add(edge)
        visited[edge.to] = true

        // Add all edges from new vertex
        for (nextEdge in graph.adj[edge.to]) {
            if (!visited[nextEdge.to]) {
                pq.offer(MSTEdge(edge.to, nextEdge.to, nextEdge.weight))
            }
        }
    }

    return mst
}

// Example:
val graph = Graph(5)
graph.addEdge(0, 1, 4)
graph.addEdge(0, 2, 1)
graph.addEdge(1, 0, 4)
graph.addEdge(1, 2, 2)
graph.addEdge(1, 3, 5)
graph.addEdge(2, 0, 1)
graph.addEdge(2, 1, 2)
graph.addEdge(2, 3, 8)
graph.addEdge(2, 4, 10)
graph.addEdge(3, 1, 5)
graph.addEdge(3, 2, 8)
graph.addEdge(3, 4, 2)
graph.addEdge(4, 2, 10)
graph.addEdge(4, 3, 2)

val mst = primMST(graph)
println("MST Total Weight: ${mst.sumOf { it.weight }}")  // 9

// Time: O((V + E) log V)
// Space: O(V)
```

**Kruskal vs Prim:**
```
Kruskal's:
✅ Better for sparse graphs (few edges)
✅ Easier to implement
✅ Works on disconnected graphs
❌ Requires sorting all edges

Prim's:
✅ Better for dense graphs (many edges)
✅ Can stop early if partial MST needed
✅ More efficient with adjacency matrix
❌ Must start from a specific vertex
```

---

### FLOYD-WARSHALL ALGORITHM

**Find shortest paths between ALL pairs of vertices.**

```kotlin
fun floydWarshall(graph: Array<IntArray>): Array<IntArray> {
    val V = graph.size
    val dist = Array(V) { i -> graph[i].clone() }

    // Try all intermediate vertices
    for (k in 0 until V) {
        for (i in 0 until V) {
            for (j in 0 until V) {
                // If path through k is shorter
                if (dist[i][k] != Int.MAX_VALUE &&
                    dist[k][j] != Int.MAX_VALUE &&
                    dist[i][k] + dist[k][j] < dist[i][j]) {
                    dist[i][j] = dist[i][k] + dist[k][j]
                }
            }
        }
    }

    return dist
}

// Example:
val INF = Int.MAX_VALUE
val graph = arrayOf(
    intArrayOf(0, 3, INF, 5),
    intArrayOf(2, 0, INF, 4),
    intArrayOf(INF, 1, 0, INF),
    intArrayOf(INF, INF, 2, 0)
)

val distances = floydWarshall(graph)

println("Shortest distances between all pairs:")
for (i in distances.indices) {
    for (j in distances[i].indices) {
        if (distances[i][j] == INF) print("INF ")
        else print("${distances[i][j]}  ")
    }
    println()
}

// Output:
// 0  3  7  5
// 2  0  6  4
// 3  1  0  5
// 5  3  2  0

// Time: O(V³)
// Space: O(V²)
```

**How Floyd-Warshall works:**
```
Initial graph:
  0 → 1: 3
  0 → 3: 5
  1 → 0: 2
  1 → 3: 4
  2 → 1: 1
  3 → 2: 2

Iteration k=0 (via vertex 0):
  Check if path i→0→j is shorter than i→j
  dist[1][3] = min(4, dist[1][0] + dist[0][3]) = min(4, 2+5) = 4

Iteration k=1 (via vertex 1):
  dist[0][3] = min(5, dist[0][1] + dist[1][3]) = min(5, 3+4) = 5
  dist[2][0] = min(INF, dist[2][1] + dist[1][0]) = 1+2 = 3
  ...

After all iterations: All-pairs shortest paths computed
```

---

#### Floyd-Warshall with Path Reconstruction

```kotlin
data class FloydWarshallResult(
    val distances: Array<IntArray>,
    val next: Array<IntArray?>
)

fun floydWarshallWithPath(graph: Array<IntArray>): FloydWarshallResult {
    val V = graph.size
    val dist = Array(V) { i -> graph[i].clone() }
    val next = Array(V) { IntArray(V) { -1 } }

    // Initialize next array
    for (i in 0 until V) {
        for (j in 0 until V) {
            if (graph[i][j] != Int.MAX_VALUE && i != j) {
                next[i][j] = j
            }
        }
    }

    for (k in 0 until V) {
        for (i in 0 until V) {
            for (j in 0 until V) {
                if (dist[i][k] != Int.MAX_VALUE &&
                    dist[k][j] != Int.MAX_VALUE &&
                    dist[i][k] + dist[k][j] < dist[i][j]) {
                    dist[i][j] = dist[i][k] + dist[k][j]
                    next[i][j] = next[i][k]
                }
            }
        }
    }

    return FloydWarshallResult(dist, next)
}

fun reconstructPath(next: Array<IntArray?>, from: Int, to: Int): List<Int> {
    if (next[from][to] == -1) return emptyList()

    val path = mutableListOf(from)
    var current = from

    while (current != to) {
        current = next[current][to]
        path.add(current)
    }

    return path
}

// Example:
val result = floydWarshallWithPath(graph)
val path = reconstructPath(result.next, 0, 2)
println("Path from 0 to 2: $path")  // [0, 3, 2]
println("Distance: ${result.distances[0][2]}")  // 7
```

---

### BELLMAN-FORD ALGORITHM

**Find shortest path with NEGATIVE weights (detects negative cycles).**

```kotlin
fun bellmanFord(graph: Graph, edges: List<MSTEdge>, source: Int): IntArray? {
    val V = graph.vertices
    val distances = IntArray(V) { Int.MAX_VALUE }
    distances[source] = 0

    // Relax all edges V-1 times
    repeat(V - 1) {
        for (edge in edges) {
            val (u, v, weight) = edge

            if (distances[u] != Int.MAX_VALUE &&
                distances[u] + weight < distances[v]) {
                distances[v] = distances[u] + weight
            }
        }
    }

    // Check for negative cycles
    for (edge in edges) {
        val (u, v, weight) = edge

        if (distances[u] != Int.MAX_VALUE &&
            distances[u] + weight < distances[v]) {
            return null  // Negative cycle detected!
        }
    }

    return distances
}

// Example with negative weights:
val edges = listOf(
    MSTEdge(0, 1, 4),
    MSTEdge(0, 2, 5),
    MSTEdge(1, 3, 3),
    MSTEdge(2, 1, -6),  // Negative weight
    MSTEdge(3, 2, 2)
)

val graph = Graph(4)
val distances = bellmanFord(graph, edges, 0)

if (distances != null) {
    println("Shortest distances: ${distances.contentToString()}")
    // [0, -1, 5, 2]
} else {
    println("Negative cycle detected!")
}

// Time: O(V * E)
// Space: O(V)
```

**Bellman-Ford vs Dijkstra:**
```
Bellman-Ford:
✅ Works with negative weights
✅ Detects negative cycles
✅ Simpler to implement
❌ Slower: O(V * E)

Dijkstra:
✅ Faster: O((V+E) log V)
✅ More efficient for most cases
❌ Fails with negative weights
❌ Cannot detect negative cycles
```

---

### ALGORITHM COMPARISON

```kotlin
data class GraphAlgorithm(
    val name: String,
    val useCase: String,
    val timeComplexity: String,
    val negativeWeights: Boolean,
    val allPairs: Boolean
)

val algorithms = listOf(
    GraphAlgorithm(
        "Dijkstra",
        "Single-source shortest path",
        "O((V+E) log V)",
        negativeWeights = false,
        allPairs = false
    ),
    GraphAlgorithm(
        "Bellman-Ford",
        "Shortest path with negative weights",
        "O(V * E)",
        negativeWeights = true,
        allPairs = false
    ),
    GraphAlgorithm(
        "Floyd-Warshall",
        "All-pairs shortest paths",
        "O(V³)",
        negativeWeights = true,
        allPairs = true
    ),
    GraphAlgorithm(
        "Kruskal's MST",
        "Minimum spanning tree",
        "O(E log E)",
        negativeWeights = true,
        allPairs = false
    ),
    GraphAlgorithm(
        "Prim's MST",
        "Minimum spanning tree",
        "O((V+E) log V)",
        negativeWeights = true,
        allPairs = false
    )
)
```

**When to use each:**
```
Use Dijkstra when:
✅ Single source shortest path
✅ Non-negative weights
✅ Need best performance
✅ Sparse or dense graphs

Use Bellman-Ford when:
✅ Negative edge weights exist
✅ Need to detect negative cycles
✅ Simple implementation preferred
✅ Graph is not too large

Use Floyd-Warshall when:
✅ Need all-pairs shortest paths
✅ Dense graphs (many edges)
✅ Graph is small (V ≤ 400)
✅ Negative weights allowed

Use Kruskal's MST when:
✅ Sparse graphs
✅ Edges already sorted
✅ Union-Find available

Use Prim's MST when:
✅ Dense graphs
✅ Adjacency list representation
✅ Need to start from specific vertex
```

---

### Real-World Applications

#### Network Routing (Dijkstra)

```kotlin
// Internet packet routing
class NetworkRouter {
    data class Router(val id: String, val latencyMs: Int)

    fun findFastestRoute(
        network: Map<String, List<Router>>,
        source: String,
        destination: String
    ): List<String> {
        val distances = mutableMapOf<String, Int>()
        val parents = mutableMapOf<String, String?>()
        val pq = PriorityQueue<Pair<String, Int>>(compareBy { it.second })

        distances[source] = 0
        parents[source] = null
        pq.offer(source to 0)

        while (pq.isNotEmpty()) {
            val (current, latency) = pq.poll()

            if (current == destination) break

            for (router in network[current] ?: emptyList()) {
                val newLatency = latency + router.latencyMs

                if (newLatency < (distances[router.id] ?: Int.MAX_VALUE)) {
                    distances[router.id] = newLatency
                    parents[router.id] = current
                    pq.offer(router.id to newLatency)
                }
            }
        }

        // Reconstruct path
        val path = mutableListOf<String>()
        var current: String? = destination
        while (current != null) {
            path.add(current)
            current = parents[current]
        }

        return path.reversed()
    }
}
```

---

#### Network Design (MST)

```kotlin
// Minimize cable cost for connecting offices
class NetworkDesigner {
    data class Office(val name: String, val location: Pair<Double, Double>)
    data class Cable(val from: Office, val to: Office, val cost: Double)

    fun minimumCableCost(offices: List<Office>): Double {
        val edges = mutableListOf<MSTEdge>()
        val officeIndex = offices.withIndex().associate { it.value to it.index }

        // Create all possible cables with costs
        for (i in offices.indices) {
            for (j in i + 1 until offices.size) {
                val distance = euclideanDistance(
                    offices[i].location,
                    offices[j].location
                )
                val cost = (distance * 100).toInt()  // $100 per km

                edges.add(MSTEdge(i, j, cost))
            }
        }

        val mst = kruskalMST(offices.size, edges)
        return mst.sumOf { it.weight }.toDouble()
    }

    private fun euclideanDistance(
        p1: Pair<Double, Double>,
        p2: Pair<Double, Double>
    ): Double {
        val dx = p1.first - p2.first
        val dy = p1.second - p2.second
        return sqrt(dx * dx + dy * dy)
    }
}
```

---

#### Flight Connections (Floyd-Warshall)

```kotlin
// Find shortest flight connections between all city pairs
class FlightNetwork {
    data class City(val code: String, val name: String)

    fun findAllConnections(
        cities: List<City>,
        flights: List<Triple<Int, Int, Int>>  // (from, to, hours)
    ): Array<IntArray> {
        val V = cities.size
        val graph = Array(V) { IntArray(V) { Int.MAX_VALUE } }

        // Initialize diagonal
        for (i in 0 until V) {
            graph[i][i] = 0
        }

        // Add direct flights
        for ((from, to, hours) in flights) {
            graph[from][to] = hours
        }

        return floydWarshall(graph)
    }

    fun findFastestConnection(
        distances: Array<IntArray>,
        cities: List<City>,
        from: String,
        to: String
    ): Int? {
        val fromIndex = cities.indexOfFirst { it.code == from }
        val toIndex = cities.indexOfFirst { it.code == to }

        if (fromIndex == -1 || toIndex == -1) return null

        val hours = distances[fromIndex][toIndex]
        return if (hours == Int.MAX_VALUE) null else hours
    }
}
```

---

### Key Takeaways

1. **Dijkstra** - Single-source shortest path, non-negative weights, O((V+E) log V)
2. **Bellman-Ford** - Handles negative weights, detects negative cycles, O(V*E)
3. **Floyd-Warshall** - All-pairs shortest paths, O(V³), use for small dense graphs
4. **Kruskal's MST** - Union-Find based, O(E log E), good for sparse graphs
5. **Prim's MST** - Priority queue based, O((V+E) log V), good for dense graphs
6. **Use Dijkstra** for most shortest path problems (GPS, routing)
7. **Use Floyd-Warshall** when you need distances between all pairs
8. **Use MST** for network design, clustering, minimum cost connections
9. **Priority Queue** is essential for efficient graph algorithms
10. **Path reconstruction** requires tracking parent/next pointers

---

## Russian Version

### Постановка задачи

Продвинутые алгоритмы на графах необходимы для решения сложных задач кратчайших путей и минимальных остовных деревьев. Эти алгоритмы фундаментальны в сетевой маршрутизации, картографических приложениях, социальных сетях и оптимизации инфраструктуры.

**Вопрос:** Как работают алгоритмы Дейкстры, минимального остовного дерева (Краскала, Прима), Флойда-Уоршелла и Беллмана-Форда? Когда использовать каждый из них?

### Ключевые выводы

1. **Дейкстра** - Кратчайший путь из одной вершины, неотрицательные веса, O((V+E) log V)
2. **Беллман-Форд** - Работает с отрицательными весами, находит отрицательные циклы, O(V*E)
3. **Флойд-Уоршелл** - Кратчайшие пути между всеми парами, O(V³), для малых плотных графов
4. **Краскал (MST)** - На основе Union-Find, O(E log E), хорош для разреженных графов
5. **Прим (MST)** - На основе приоритетной очереди, O((V+E) log V), хорош для плотных графов
6. **Используйте Дейкстру** для большинства задач кратчайшего пути (GPS, маршрутизация)
7. **Используйте Флойда-Уоршелла** когда нужны расстояния между всеми парами вершин
8. **Используйте MST** для проектирования сетей, кластеризации, минимальной стоимости соединений
9. **Приоритетная очередь** критична для эффективных алгоритмов на графах
10. **Восстановление пути** требует отслеживания родительских указателей

## Follow-ups

1. How does A* algorithm improve on Dijkstra for pathfinding?
2. What is the difference between Kruskal's and Prim's MST algorithms?
3. How do you detect a negative cycle using Bellman-Ford?
4. When would you use Floyd-Warshall over running Dijkstra V times?
5. How does the priority queue optimization work in Dijkstra?
6. What is the role of Union-Find in Kruskal's algorithm?
7. How do you handle disconnected graphs in MST algorithms?
8. What is the Johnson's algorithm for all-pairs shortest paths?
9. How do you implement bidirectional Dijkstra?
10. What are the trade-offs between adjacency matrix and adjacency list for these algorithms?
