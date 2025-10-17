---
id: 20251012-200004
title: "Graph Algorithms: BFS and DFS / Алгоритмы графов: BFS и DFS"
topic: algorithms
difficulty: hard
status: draft
created: 2025-10-12
tags: - algorithms
  - graphs
  - bfs
  - dfs
  - traversal
moc: moc-algorithms
related:   - q-binary-search-variants--algorithms--medium
  - q-dynamic-programming-fundamentals--algorithms--hard
subtopics:   - graphs
  - bfs
  - dfs
  - traversal
  - shortest-path
---
# Graph Algorithms: BFS and DFS

## English Version

### Problem Statement

Graphs are fundamental data structures representing relationships between entities. BFS (Breadth-First Search) and DFS (Depth-First Search) are essential graph traversal algorithms used in countless applications.

**The Question:** How do BFS and DFS work? When should you use each? What are common graph problems and patterns?

### Detailed Answer

#### Graph Representation

**Adjacency List (Most Common):**
```kotlin
// Graph representation
class Graph(val vertices: Int) {
    val adj = Array(vertices) { mutableListOf<Int>() }
    
    fun addEdge(u: Int, v: Int) {
        adj[u].add(v)
        adj[v].add(u)  // For undirected graph
    }
}

// Example:
val graph = Graph(5)
graph.addEdge(0, 1)
graph.addEdge(0, 2)
graph.addEdge(1, 3)
graph.addEdge(2, 4)

// Adjacency List:
// 0 -> [1, 2]
// 1 -> [0, 3]
// 2 -> [0, 4]
// 3 -> [1]
// 4 -> [2]
```

---

### 1. Breadth-First Search (BFS)

**Explore level by level using a queue.**

```kotlin
fun bfs(graph: Graph, start: Int) {
    val visited = BooleanArray(graph.vertices)
    val queue = LinkedList<Int>()
    
    visited[start] = true
    queue.offer(start)
    
    while (queue.isNotEmpty()) {
        val vertex = queue.poll()
        print("$vertex ")
        
        for (neighbor in graph.adj[vertex]) {
            if (!visited[neighbor]) {
                visited[neighbor] = true
                queue.offer(neighbor)
            }
        }
    }
}

// Example:
//     0
//    / \
//   1   2
//  /     \
// 3       4
//
// BFS from 0: 0 1 2 3 4 (level by level)
```

**How BFS works:**
```
Queue: [0]       Visited: {0}       Level 0
       ↓
Queue: [1, 2]    Visited: {0,1,2}   Level 1
       ↓
Queue: [2, 3]    Visited: {0,1,2,3} Level 1
       ↓
Queue: [3, 4]    Visited: {0,1,2,3,4} Level 2
       ↓
Queue: [4]       Done!
```

**Complexity:**
- **Time:** O(V + E) where V = vertices, E = edges
- **Space:** O(V) for queue and visited array

** Use BFS for:**
- **Shortest path** in unweighted graph
- **Level-order** traversal
- **Connected components**
- Problems requiring **layer-by-layer** exploration

---

### 2. Depth-First Search (DFS)

**Explore as deep as possible using recursion/stack.**

```kotlin
fun dfs(graph: Graph, start: Int, visited: BooleanArray = BooleanArray(graph.vertices)) {
    visited[start] = true
    print("$start ")
    
    for (neighbor in graph.adj[start]) {
        if (!visited[neighbor]) {
            dfs(graph, neighbor, visited)
        }
    }
}

// Iterative DFS with stack
fun dfsIterative(graph: Graph, start: Int) {
    val visited = BooleanArray(graph.vertices)
    val stack = Stack<Int>()
    
    stack.push(start)
    
    while (stack.isNotEmpty()) {
        val vertex = stack.pop()
        
        if (!visited[vertex]) {
            visited[vertex] = true
            print("$vertex ")
            
            // Push neighbors in reverse order to maintain left-to-right
            for (i in graph.adj[vertex].size - 1 downTo 0) {
                if (!visited[graph.adj[vertex][i]]) {
                    stack.push(graph.adj[vertex][i])
                }
            }
        }
    }
}

// Example:
//     0
//    / \
//   1   2
//  /     \
// 3       4
//
// DFS from 0: 0 1 3 2 4 (go deep first)
```

**Complexity:**
- **Time:** O(V + E)
- **Space:** O(V) for recursion stack

** Use DFS for:**
- **Topological sort**
- **Cycle detection**
- **Path finding** (not necessarily shortest)
- **Connected components**
- **Backtracking** problems

---

### 3. Shortest Path (BFS)

**Find shortest path between two nodes.**

```kotlin
fun shortestPath(graph: Graph, start: Int, end: Int): Int {
    val visited = BooleanArray(graph.vertices)
    val queue = LinkedList<Pair<Int, Int>>()  // (vertex, distance)
    
    visited[start] = true
    queue.offer(start to 0)
    
    while (queue.isNotEmpty()) {
        val (vertex, dist) = queue.poll()
        
        if (vertex == end) return dist
        
        for (neighbor in graph.adj[vertex]) {
            if (!visited[neighbor]) {
                visited[neighbor] = true
                queue.offer(neighbor to dist + 1)
            }
        }
    }
    
    return -1  // No path found
}

// With path reconstruction:
fun shortestPathWithPath(graph: Graph, start: Int, end: Int): List<Int>? {
    val visited = BooleanArray(graph.vertices)
    val parent = IntArray(graph.vertices) { -1 }
    val queue = LinkedList<Int>()
    
    visited[start] = true
    queue.offer(start)
    
    while (queue.isNotEmpty()) {
        val vertex = queue.poll()
        
        if (vertex == end) {
            // Reconstruct path
            val path = mutableListOf<Int>()
            var curr = end
            while (curr != -1) {
                path.add(0, curr)
                curr = parent[curr]
            }
            return path
        }
        
        for (neighbor in graph.adj[vertex]) {
            if (!visited[neighbor]) {
                visited[neighbor] = true
                parent[neighbor] = vertex
                queue.offer(neighbor)
            }
        }
    }
    
    return null
}
```

---

### 4. Number of Islands (BFS/DFS)

**Count connected components in 2D grid.**

```kotlin
fun numIslands(grid: Array<CharArray>): Int {
    if (grid.isEmpty()) return 0
    
    val m = grid.size
    val n = grid[0].size
    var count = 0
    
    fun dfs(i: Int, j: Int) {
        if (i < 0 || i >= m || j < 0 || j >= n || grid[i][j] == '0') {
            return
        }
        
        grid[i][j] = '0'  // Mark as visited
        
        // Explore 4 directions
        dfs(i + 1, j)  // Down
        dfs(i - 1, j)  // Up
        dfs(i, j + 1)  // Right
        dfs(i, j - 1)  // Left
    }
    
    for (i in 0 until m) {
        for (j in 0 until n) {
            if (grid[i][j] == '1') {
                count++
                dfs(i, j)
            }
        }
    }
    
    return count
}

// Example:
val grid = arrayOf(
    charArrayOf('1','1','0','0','0'),
    charArrayOf('1','1','0','0','0'),
    charArrayOf('0','0','1','0','0'),
    charArrayOf('0','0','0','1','1')
)
println(numIslands(grid))  // 3 islands
```

---

### 5. Course Schedule (Cycle Detection)

**Can finish all courses? (Detect cycle in directed graph)**

```kotlin
fun canFinish(numCourses: Int, prerequisites: Array<IntArray>): Boolean {
    val adj = Array(numCourses) { mutableListOf<Int>() }
    
    // Build adjacency list
    for ((course, prereq) in prerequisites) {
        adj[prereq].add(course)
    }
    
    val visited = IntArray(numCourses)  // 0=unvisited, 1=visiting, 2=visited
    
    fun hasCycle(course: Int): Boolean {
        if (visited[course] == 1) return true  // Cycle detected!
        if (visited[course] == 2) return false // Already visited
        
        visited[course] = 1  // Mark as visiting
        
        for (neighbor in adj[course]) {
            if (hasCycle(neighbor)) return true
        }
        
        visited[course] = 2  // Mark as visited
        return false
    }
    
    for (i in 0 until numCourses) {
        if (hasCycle(i)) return false
    }
    
    return true
}

// Example:
val prerequisites = arrayOf(
    intArrayOf(1, 0),  // Course 1 requires course 0
    intArrayOf(0, 1)   // Course 0 requires course 1 → Cycle!
)
println(canFinish(2, prerequisites))  // false
```

---

### 6. Topological Sort (DFS)

**Order courses by dependencies.**

```kotlin
fun findOrder(numCourses: Int, prerequisites: Array<IntArray>): IntArray {
    val adj = Array(numCourses) { mutableListOf<Int>() }
    val result = mutableListOf<Int>()
    val visited = IntArray(numCourses)
    
    // Build adjacency list
    for ((course, prereq) in prerequisites) {
        adj[prereq].add(course)
    }
    
    fun hasCycle(course: Int): Boolean {
        if (visited[course] == 1) return true
        if (visited[course] == 2) return false
        
        visited[course] = 1
        
        for (neighbor in adj[course]) {
            if (hasCycle(neighbor)) return true
        }
        
        visited[course] = 2
        result.add(0, course)  // Add to front (reverse postorder)
        return false
    }
    
    for (i in 0 until numCourses) {
        if (hasCycle(i)) return intArrayOf()
    }
    
    return result.toIntArray()
}

// Example:
val prerequisites = arrayOf(
    intArrayOf(1, 0),  // Course 1 requires course 0
    intArrayOf(2, 0),  // Course 2 requires course 0
    intArrayOf(3, 1),  // Course 3 requires course 1
    intArrayOf(3, 2)   // Course 3 requires course 2
)
println(findOrder(4, prerequisites).contentToString())  // [0, 1, 2, 3] or [0, 2, 1, 3]
```

---

### 7. Clone Graph

**Deep copy a graph.**

```kotlin
class Node(var `val`: Int) {
    var neighbors: ArrayList<Node?> = ArrayList()
}

fun cloneGraph(node: Node?): Node? {
    if (node == null) return null
    
    val visited = mutableMapOf<Node, Node>()
    
    fun dfs(node: Node): Node {
        if (node in visited) return visited[node]!!
        
        val clone = Node(node.`val`)
        visited[node] = clone
        
        for (neighbor in node.neighbors) {
            neighbor?.let {
                clone.neighbors.add(dfs(it))
            }
        }
        
        return clone
    }
    
    return dfs(node)
}
```

---

### 8. Word Ladder (BFS)

**Shortest transformation sequence from beginWord to endWord.**

```kotlin
fun ladderLength(beginWord: String, endWord: String, wordList: List<String>): Int {
    val wordSet = wordList.toSet()
    if (endWord !in wordSet) return 0
    
    val queue = LinkedList<Pair<String, Int>>()
    queue.offer(beginWord to 1)
    
    while (queue.isNotEmpty()) {
        val (word, level) = queue.poll()
        
        if (word == endWord) return level
        
        // Try all possible one-letter transformations
        for (i in word.indices) {
            val chars = word.toCharArray()
            for (c in 'a'..'z') {
                chars[i] = c
                val newWord = String(chars)
                
                if (newWord in wordSet) {
                    queue.offer(newWord to level + 1)
                    wordSet as MutableSet
                    wordSet.remove(newWord)  // Mark as visited
                }
            }
        }
    }
    
    return 0
}

// Example:
val wordList = listOf("hot","dot","dog","lot","log","cog")
println(ladderLength("hit", "cog", wordList))  // 5 (hit->hot->dot->dog->cog)
```

---

### 9. Dijkstra's Algorithm (Shortest Path with Weights)

**Find shortest path in weighted graph.**

```kotlin
fun dijkstra(graph: Array<MutableList<Pair<Int, Int>>>, start: Int): IntArray {
    val n = graph.size
    val dist = IntArray(n) { Int.MAX_VALUE }
    val pq = PriorityQueue<Pair<Int, Int>>(compareBy { it.second })
    
    dist[start] = 0
    pq.offer(start to 0)
    
    while (pq.isNotEmpty()) {
        val (vertex, d) = pq.poll()
        
        if (d > dist[vertex]) continue
        
        for ((neighbor, weight) in graph[vertex]) {
            val newDist = dist[vertex] + weight
            if (newDist < dist[neighbor]) {
                dist[neighbor] = newDist
                pq.offer(neighbor to newDist)
            }
        }
    }
    
    return dist
}

// Example:
val graph = Array(5) { mutableListOf<Pair<Int, Int>>() }
graph[0].add(1 to 4)  // Edge from 0 to 1 with weight 4
graph[0].add(2 to 1)
graph[2].add(1 to 2)
graph[1].add(3 to 1)
graph[2].add(3 to 5)

val distances = dijkstra(graph, 0)
println(distances.contentToString())  // [0, 3, 1, 4, ∞]
```

---

### BFS vs DFS Comparison

| Feature | BFS | DFS |
|---------|-----|-----|
| **Data Structure** | Queue | Stack/Recursion |
| **Order** | Level by level | Deep first |
| **Shortest Path** |  Yes (unweighted) |  No |
| **Space** | O(w) w=width | O(h) h=height |
| **Complete** |  Yes |  May get stuck |
| **Use Case** | Shortest path, levels | Topological, cycles |

---

### Real-World Android Example

```kotlin
// Social network: Find mutual friends
class SocialNetwork {
    private val friends = mutableMapOf<Int, MutableList<Int>>()
    
    fun addFriendship(user1: Int, user2: Int) {
        friends.getOrPut(user1) { mutableListOf() }.add(user2)
        friends.getOrPut(user2) { mutableListOf() }.add(user1)
    }
    
    fun findMutualFriends(user1: Int, user2: Int): List<Int> {
        val friends1 = friends[user1]?.toSet() ?: emptySet()
        val friends2 = friends[user2]?.toSet() ?: emptySet()
        return friends1.intersect(friends2).toList()
    }
    
    fun degreesOfSeparation(user1: Int, user2: Int): Int {
        val visited = mutableSetOf<Int>()
        val queue = LinkedList<Pair<Int, Int>>()
        
        visited.add(user1)
        queue.offer(user1 to 0)
        
        while (queue.isNotEmpty()) {
            val (user, degree) = queue.poll()
            
            if (user == user2) return degree
            
            for (friend in friends[user] ?: emptyList()) {
                if (friend !in visited) {
                    visited.add(friend)
                    queue.offer(friend to degree + 1)
                }
            }
        }
        
        return -1  // Not connected
    }
}
```

---

### Key Takeaways

1. **BFS** = Level-by-level, uses queue, finds shortest path
2. **DFS** = Go deep, uses stack/recursion, good for paths/cycles
3. **Time complexity:** O(V + E) for both
4. **BFS for:** Shortest path, connected components, level-order
5. **DFS for:** Topological sort, cycle detection, backtracking
6. **Graph representation:** Adjacency list most common
7. **Visited array** essential to avoid infinite loops
8. **Cycle detection:** Use 3 states (unvisited, visiting, visited)
9. **Topological sort** requires DFS with postorder
10. **Real applications:** Social networks, maps, dependencies

---

## Russian Version

### Постановка задачи

Графы - фундаментальные структуры данных, представляющие отношения между сущностями. BFS и DFS - важнейшие алгоритмы обхода графов.

**Вопрос:** Как работают BFS и DFS? Когда следует использовать каждый? Каковы распространённые задачи и паттерны с графами?

### Ключевые выводы

1. **BFS** = Уровень за уровнем, использует очередь, находит кратчайший путь
2. **DFS** = Идти вглубь, использует стек/рекурсию, хорош для путей/циклов
3. **Временная сложность:** O(V + E) для обоих
4. **BFS для:** Кратчайший путь, компоненты связности
5. **DFS для:** Топологическая сортировка, обнаружение циклов
6. **Представление графа:** Список смежности наиболее распространён
7. **Visited массив** необходим для избежания бесконечных циклов

## Follow-ups

1. What is the difference between BFS and DFS space complexity?
2. How do you detect a cycle in an undirected vs directed graph?
3. What is bidirectional BFS and when is it useful?
4. How do you find strongly connected components (Kosaraju's algorithm)?
5. What is the difference between Dijkstra's and Bellman-Ford algorithms?
6. How do you implement A* search algorithm?
7. What is minimum spanning tree (Kruskal's, Prim's)?
8. How do you find articulation points in a graph?
9. What is the traveling salesman problem?
10. How do you implement union-find (disjoint set)?

---

## Related Questions

### Android Implementation
- [[q-compose-canvas-graphics--jetpack-compose--hard]] - Data Structures
- [[q-cache-implementation-strategies--android--medium]] - Data Structures
- [[q-recomposition-choreographer--android--hard]] - Data Structures
- [[q-android-security-practices-checklist--android--medium]] - Data Structures
- [[q-rxjava-pagination-recyclerview--android--medium]] - Data Structures

### Kotlin Language Features
- [[q-kotlin-collections--kotlin--medium]] - Data Structures

### System Design Concepts
- [[q-message-queues-event-driven--system-design--medium]] - Data Structures
