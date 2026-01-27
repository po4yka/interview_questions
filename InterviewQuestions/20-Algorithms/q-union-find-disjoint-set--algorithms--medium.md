---
id: q-union-find-disjoint-set
title: Union-Find / Disjoint Set
difficulty: medium
subtopics:
- data-structures
- graphs
- connectivity
anki_cards:
- slug: q-union-find-disjoint-set-0-en
  language: en
  anki_id: 1769404210915
  synced_at: '2026-01-26T09:10:14.449948'
- slug: q-union-find-disjoint-set-0-ru
  language: ru
  anki_id: 1769404210940
  synced_at: '2026-01-26T09:10:14.451106'
---
# Question (EN)
> Explain the Union-Find (Disjoint Set Union) data structure. How do path compression and union by rank work?

## Answer (EN)

**Union-Find** (also called **Disjoint Set Union** or DSU) is a data structure that tracks elements partitioned into non-overlapping sets. It supports two primary operations efficiently:

### Core Operations

| Operation | Description |
|-----------|-------------|
| `find(x)` | Returns the representative (root) of the set containing `x` |
| `union(x, y)` | Merges the sets containing `x` and `y` |

### What It Solves

- **Dynamic connectivity**: "Are elements A and B in the same group?"
- Efficiently handles incremental grouping (unions) with fast queries

### Naive Implementation

```python
class NaiveUnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))  # Each element is its own parent

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            x = self.parent[x]
        return x

    def union(self, x: int, y: int) -> None:
        root_x = self.find(x)
        root_y = self.find(y)
        self.parent[root_x] = root_y  # Attach one tree to another
```

**Problem**: Trees can become linear chains, making `find()` O(n) in worst case.

### Optimization 1: Path Compression

**Idea**: During `find()`, make all nodes on the path point directly to the root.

```python
def find(self, x: int) -> int:
    if self.parent[x] != x:
        self.parent[x] = self.find(self.parent[x])  # Recursively compress
    return self.parent[x]
```

**Effect**: Flattens the tree structure, making future queries faster.

### Optimization 2: Union by Rank

**Idea**: Always attach the shorter tree under the root of the taller tree.

```python
def __init__(self, n: int):
    self.parent = list(range(n))
    self.rank = [0] * n  # Height estimate

def union(self, x: int, y: int) -> bool:
    root_x, root_y = self.find(x), self.find(y)
    if root_x == root_y:
        return False  # Already in same set

    # Attach smaller tree under larger tree
    if self.rank[root_x] < self.rank[root_y]:
        self.parent[root_x] = root_y
    elif self.rank[root_x] > self.rank[root_y]:
        self.parent[root_y] = root_x
    else:
        self.parent[root_y] = root_x
        self.rank[root_x] += 1
    return True
```

**Alternative**: Union by size (track set sizes instead of ranks).

### Time Complexity

| Implementation | find() | union() |
|----------------|--------|---------|
| Naive | O(n) | O(n) |
| Path compression only | O(log n) amortized | O(log n) |
| Union by rank only | O(log n) | O(log n) |
| **Both optimizations** | **O(alpha(n))** | **O(alpha(n))** |

Where `alpha(n)` is the inverse Ackermann function - effectively constant (< 5 for any practical n).

### Complete Implementation

```python
class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n  # Number of disjoint sets

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        root_x, root_y = self.find(x), self.find(y)
        if root_x == root_y:
            return False

        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1

        self.count -= 1
        return True

    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)
```

### Applications

| Application | How Union-Find Helps |
|-------------|---------------------|
| **Kruskal's MST** | Check if adding edge creates cycle |
| **Connected components** | Group nodes dynamically |
| **Cycle detection** | If `find(u) == find(v)` before union, edge (u,v) creates cycle |
| **Network connectivity** | "Are computers A and B connected?" |
| **Image processing** | Connected component labeling |
| **Percolation** | Does top connect to bottom? |

### Example: Number of Connected Components

```python
def count_components(n: int, edges: list[tuple[int, int]]) -> int:
    uf = UnionFind(n)
    for u, v in edges:
        uf.union(u, v)
    return uf.count
```

### Key Interview Points

1. **Without optimizations**: O(n) per operation
2. **With both optimizations**: O(alpha(n)) ~ O(1) amortized
3. **Space**: O(n) for parent and rank arrays
4. **Cannot efficiently split sets** (union-only structure)

---

# Vopros (RU)
> Объясните структуру данных Union-Find (система непересекающихся множеств). Как работают сжатие путей и объединение по рангу?

## Otvet (RU)

**Union-Find** (также **Disjoint Set Union** или DSU, система непересекающихся множеств) - структура данных для отслеживания элементов, разбитых на непересекающиеся группы. Поддерживает две основные операции:

### Базовые операции

| Операция | Описание |
|----------|----------|
| `find(x)` | Возвращает представителя (корень) множества, содержащего `x` |
| `union(x, y)` | Объединяет множества, содержащие `x` и `y` |

### Какие задачи решает

- **Динамическая связность**: "Находятся ли элементы A и B в одной группе?"
- Эффективная обработка инкрементальной группировки с быстрыми запросами

### Наивная реализация

```python
class NaiveUnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))  # Каждый элемент - сам себе родитель

    def find(self, x: int) -> int:
        while self.parent[x] != x:
            x = self.parent[x]
        return x

    def union(self, x: int, y: int) -> None:
        root_x = self.find(x)
        root_y = self.find(y)
        self.parent[root_x] = root_y  # Присоединяем одно дерево к другому
```

**Проблема**: Деревья могут вырождаться в линейные цепочки, делая `find()` O(n) в худшем случае.

### Оптимизация 1: Сжатие путей (Path Compression)

**Идея**: При вызове `find()` все узлы на пути перенаправляются напрямую к корню.

```python
def find(self, x: int) -> int:
    if self.parent[x] != x:
        self.parent[x] = self.find(self.parent[x])  # Рекурсивное сжатие
    return self.parent[x]
```

**Эффект**: Уплощает структуру дерева, ускоряя будущие запросы.

### Оптимизация 2: Объединение по рангу (Union by Rank)

**Идея**: Всегда присоединять меньшее дерево под корень большего.

```python
def __init__(self, n: int):
    self.parent = list(range(n))
    self.rank = [0] * n  # Оценка высоты

def union(self, x: int, y: int) -> bool:
    root_x, root_y = self.find(x), self.find(y)
    if root_x == root_y:
        return False  # Уже в одном множестве

    # Присоединяем меньшее дерево к большему
    if self.rank[root_x] < self.rank[root_y]:
        self.parent[root_x] = root_y
    elif self.rank[root_x] > self.rank[root_y]:
        self.parent[root_y] = root_x
    else:
        self.parent[root_y] = root_x
        self.rank[root_x] += 1
    return True
```

**Альтернатива**: Объединение по размеру (хранить размеры множеств вместо рангов).

### Временная сложность

| Реализация | find() | union() |
|------------|--------|---------|
| Наивная | O(n) | O(n) |
| Только сжатие путей | O(log n) амортиз. | O(log n) |
| Только объединение по рангу | O(log n) | O(log n) |
| **Обе оптимизации** | **O(alpha(n))** | **O(alpha(n))** |

Где `alpha(n)` - обратная функция Аккермана, практически константа (< 5 для любого реального n).

### Полная реализация

```python
class UnionFind:
    def __init__(self, n: int):
        self.parent = list(range(n))
        self.rank = [0] * n
        self.count = n  # Количество непересекающихся множеств

    def find(self, x: int) -> int:
        if self.parent[x] != x:
            self.parent[x] = self.find(self.parent[x])
        return self.parent[x]

    def union(self, x: int, y: int) -> bool:
        root_x, root_y = self.find(x), self.find(y)
        if root_x == root_y:
            return False

        if self.rank[root_x] < self.rank[root_y]:
            self.parent[root_x] = root_y
        elif self.rank[root_x] > self.rank[root_y]:
            self.parent[root_y] = root_x
        else:
            self.parent[root_y] = root_x
            self.rank[root_x] += 1

        self.count -= 1
        return True

    def connected(self, x: int, y: int) -> bool:
        return self.find(x) == self.find(y)
```

### Применения

| Применение | Как помогает Union-Find |
|------------|------------------------|
| **Алгоритм Краскала (MST)** | Проверка, создаёт ли ребро цикл |
| **Компоненты связности** | Динамическая группировка узлов |
| **Поиск циклов** | Если `find(u) == find(v)` до union, ребро (u,v) создаёт цикл |
| **Сетевая связность** | "Связаны ли компьютеры A и B?" |
| **Обработка изображений** | Разметка связных компонент |
| **Перколяция** | Соединяется ли верх с низом? |

### Пример: Количество компонент связности

```python
def count_components(n: int, edges: list[tuple[int, int]]) -> int:
    uf = UnionFind(n)
    for u, v in edges:
        uf.union(u, v)
    return uf.count
```

### Ключевые моменты для собеседования

1. **Без оптимизаций**: O(n) на операцию
2. **С обеими оптимизациями**: O(alpha(n)) ~ O(1) амортизированно
3. **Память**: O(n) для массивов parent и rank
4. **Нельзя эффективно разделять множества** (только объединение)
