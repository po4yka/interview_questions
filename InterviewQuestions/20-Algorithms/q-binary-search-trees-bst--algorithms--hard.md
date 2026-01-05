---
id: algo-007
title: "Binary Search Trees and AVL Trees / Бинарные деревья поиска и AVL деревья"
aliases: ["AVL Trees", "AVL деревья", "Binary Search Trees", "Бинарные деревья поиска"]
topic: algorithms
subtopics: [avl, bst, trees]
question_kind: coding
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-algorithms
related: [c-algorithms, q-binary-search-variants--algorithms--medium]
created: 2025-10-12
updated: 2025-11-11
tags: [algorithms, avl, bst, data-structures, difficulty/hard, trees]
sources: ["https://en.wikipedia.org/wiki/AVL_tree", "https://en.wikipedia.org/wiki/Binary_search_tree"]

---
# Вопрос (RU)
> Как работают BST? Каковы основные операции? Как AVL деревья поддерживают баланс?

# Question (EN)
> How do BSTs work? What are the common operations? How do AVL trees maintain balance?

---

## Ответ (RU)

**Теория BST:**
Бинарное дерево поиска (BST) - структура данных, где для каждого узла все значения в левом поддереве меньше значения узла, а все значения в правом поддереве больше. Это свойство обеспечивает эффективный поиск, вставку и удаление. На практике также нужно явно определить политику работы с дубликатами (запрет, хранение счётчика, всегда влево/вправо и т.п.); в приведённом коде дубликаты просто игнорируются.

**Основные операции BST:**
- Поиск: O(h), где h - высота дерева
- Вставка: O(h)
- Удаление: O(h)
- В худшем случае (вырожденное дерево): O(n)
- В среднем случае при достаточно случайном порядке вставок или сбалансированной структуре: O(log n)

**BST Implementation:**
```kotlin
class TreeNode(
    var value: Int,
    var left: TreeNode? = null,
    var right: TreeNode? = null
)

class BST {
    var root: TreeNode? = null

    // Поиск: O(h)
    fun search(value: Int): TreeNode? {
        var current = root

        while (current != null) {
            when {
                value == current.value -> return current
                value < current.value -> current = current.left
                else -> current = current.right
            }
        }

        return null
    }

    // Вставка: O(h)
    fun insert(value: Int) {
        root = insertRec(root, value)
    }

    private fun insertRec(node: TreeNode?, value: Int): TreeNode {
        if (node == null) return TreeNode(value)

        when {
            value < node.value -> node.left = insertRec(node.left, value)
            value > node.value -> node.right = insertRec(node.right, value)
            // Дубликаты игнорируются (альтернативные политики возможны)
        }

        return node
    }

    // Удаление: O(h) - три случая
    fun delete(value: Int) {
        root = deleteRec(root, value)
    }

    private fun deleteRec(node: TreeNode?, value: Int): TreeNode? {
        if (node == null) return null

        when {
            value < node.value -> node.left = deleteRec(node.left, value)
            value > node.value -> node.right = deleteRec(node.right, value)
            else -> {
                // Узел для удаления найден
                // Случай 1: Листовой узел
                if (node.left == null && node.right == null) {
                    return null
                }
                // Случай 2: Один ребёнок
                if (node.left == null) return node.right
                if (node.right == null) return node.left

                // Случай 3: Два ребёнка - находим inorder-преемника
                val successor = findMin(node.right!!)
                node.value = successor.value
                node.right = deleteRec(node.right, successor.value)
            }
        }

        return node
    }

    private fun findMin(node: TreeNode): TreeNode {
        var current = node
        while (current.left != null) {
            current = current.left!!
        }
        return current
    }
}
```

**Tree Traversals:**
```kotlin
// Inorder (Левый → Корень → Правый) - даёт отсортированный порядок для BST
fun inorderTraversal(node: TreeNode?): List<Int> {
    val result = mutableListOf<Int>()

    fun traverse(n: TreeNode?) {
        if (n == null) return

        traverse(n.left)      // Левый
        result.add(n.value)   // Корень
        traverse(n.right)     // Правый
    }

    traverse(node)
    return result
}

// Preorder (Корень → Левый → Правый) - часто используют для сериализации/копирования дерева
fun preorderTraversal(node: TreeNode?): List<Int> {
    val result = mutableListOf<Int>()

    fun traverse(n: TreeNode?) {
        if (n == null) return

        result.add(n.value)   // Корень
        traverse(n.left)      // Левый
        traverse(n.right)     // Правый
    }

    traverse(node)
    return result
}

// Postorder (Левый → Правый → Корень) - удобно для удаления дерева или вычисления на поддеревьях
fun postorderTraversal(node: TreeNode?): List<Int> {
    val result = mutableListOf<Int>()

    fun traverse(n: TreeNode?) {
        if (n == null) return

        traverse(n.left)      // Левый
        traverse(n.right)     // Правый
        result.add(n.value)   // Корень
    }

    traverse(node)
    return result
}

// Level-order (BFS) - обход по уровням
fun levelOrder(root: TreeNode?): List<List<Int>> {
    if (root == null) return emptyList()

    val result = mutableListOf<List<Int>>()
    val queue = LinkedList<TreeNode>()
    queue.offer(root)

    while (queue.isNotEmpty()) {
        val levelSize = queue.size
        val level = mutableListOf<Int>()

        repeat(levelSize) {
            val node = queue.poll()
            level.add(node.value)

            node.left?.let { queue.offer(it) }
            node.right?.let { queue.offer(it) }
        }

        result.add(level)
    }

    return result
}
```

**AVL Trees (Self-Balancing BST):**
AVL деревья являются самобалансирующимися BST: они поддерживают высоту дерева O(log n), поэтому операции поиска, вставки и удаления работают за O(log n) в худшем случае. Для каждого узла разность высот между левым и правым поддеревьями не превышает 1.

**Balance Factor:** height(left) - height(right) ∈ {-1, 0, 1}

```kotlin
class AVLNode(
    var value: Int,
    var left: AVLNode? = null,
    var right: AVLNode? = null,
    var height: Int = 1
)

class AVLTree {
    var root: AVLNode? = null

    private fun height(node: AVLNode?): Int = node?.height ?: 0

    private fun balanceFactor(node: AVLNode?): Int {
        if (node == null) return 0
        return height(node.left) - height(node.right)
    }

    private fun updateHeight(node: AVLNode) {
        node.height = 1 + maxOf(height(node.left), height(node.right))
    }

    // Правая ротация для исправления Left-Left случая
    private fun rotateRight(y: AVLNode): AVLNode {
        val x = y.left!!
        val B = x.right

        x.right = y
        y.left = B

        updateHeight(y)
        updateHeight(x)

        return x
    }

    // Левая ротация для исправления Right-Right случая
    private fun rotateLeft(x: AVLNode): AVLNode {
        val y = x.right!!
        val B = y.left

        y.left = x
        x.right = B

        updateHeight(x)
        updateHeight(y)

        return y
    }

    fun insert(value: Int) {
        root = insertRec(root, value)
    }

    private fun insertRec(node: AVLNode?, value: Int): AVLNode {
        // Стандартная вставка BST
        if (node == null) return AVLNode(value)

        when {
            value < node.value -> node.left = insertRec(node.left, value)
            value > node.value -> node.right = insertRec(node.right, value)
            else -> return node  // Дубликат не вставляем
        }

        // Обновляем высоту текущего узла
        updateHeight(node)

        // Вычисляем фактор баланса
        val balance = balanceFactor(node)

        // Четыре стандартных случая дисбаланса на пути вставки:
        // Left-Left Case
        if (balance > 1 && value < node.left!!.value) {
            return rotateRight(node)
        }

        // Right-Right Case
        if (balance < -1 && value > node.right!!.value) {
            return rotateLeft(node)
        }

        // Left-Right Case
        if (balance > 1 && value > node.left!!.value) {
            node.left = rotateLeft(node.left!!)
            return rotateRight(node)
        }

        // Right-Left Case
        if (balance < -1 && value < node.right!!.value) {
            node.right = rotateRight(node.right!!)
            return rotateLeft(node)
        }

        return node
    }
}
```

## Answer (EN)

**BST Theory:**
Binary Search Tree (BST) is a data structure where for every node, all values in the left subtree are less than the node's value, and all values in the right subtree are greater. This property enables efficient search, insertion, and deletion. In practice, you must define how to handle duplicates (disallow, keep a count, always go left/right, etc.); in the code below duplicates are simply ignored.

**Main BST Operations:**
- Search: O(h), where h = height
- Insert: O(h)
- Delete: O(h)
- Worst case (skewed tree): O(n)
- Average case, assuming random insertion order or a balanced structure: O(log n)

**BST Implementation:**
```kotlin
class TreeNode(
    var value: Int,
    var left: TreeNode? = null,
    var right: TreeNode? = null
)

class BST {
    var root: TreeNode? = null

    // Search: O(h)
    fun search(value: Int): TreeNode? {
        var current = root

        while (current != null) {
            when {
                value == current.value -> return current
                value < current.value -> current = current.left
                else -> current = current.right
            }
        }

        return null
    }

    // Insert: O(h)
    fun insert(value: Int) {
        root = insertRec(root, value)
    }

    private fun insertRec(node: TreeNode?, value: Int): TreeNode {
        if (node == null) return TreeNode(value)

        when {
            value < node.value -> node.left = insertRec(node.left, value)
            value > node.value -> node.right = insertRec(node.right, value)
            // Duplicates are ignored (other policies are possible)
        }

        return node
    }

    // Delete: O(h) - three cases
    fun delete(value: Int) {
        root = deleteRec(root, value)
    }

    private fun deleteRec(node: TreeNode?, value: Int): TreeNode? {
        if (node == null) return null

        when {
            value < node.value -> node.left = deleteRec(node.left, value)
            value > node.value -> node.right = deleteRec(node.right, value)
            else -> {
                // Node to delete found
                // Case 1: Leaf node
                if (node.left == null && node.right == null) {
                    return null
                }
                // Case 2: One child
                if (node.left == null) return node.right
                if (node.right == null) return node.left

                // Case 3: Two children - find inorder successor
                val successor = findMin(node.right!!)
                node.value = successor.value
                node.right = deleteRec(node.right, successor.value)
            }
        }

        return node
    }

    private fun findMin(node: TreeNode): TreeNode {
        var current = node
        while (current.left != null) {
            current = current.left!!
        }
        return current
    }
}
```

**Tree Traversals:**
```kotlin
// Inorder (Left → Root → Right) - produces sorted order for BST
fun inorderTraversal(node: TreeNode?): List<Int> {
    val result = mutableListOf<Int>()

    fun traverse(n: TreeNode?) {
        if (n == null) return

        traverse(n.left)      // Left
        result.add(n.value)   // Root
        traverse(n.right)     // Right
    }

    traverse(node)
    return result
}

// Preorder (Root → Left → Right) - often used for serialization/copying
fun preorderTraversal(node: TreeNode?): List<Int> {
    val result = mutableListOf<Int>()

    fun traverse(n: TreeNode?) {
        if (n == null) return

        result.add(n.value)   // Root
        traverse(n.left)      // Left
        traverse(n.right)     // Right
    }

    traverse(node)
    return result
}

// Postorder (Left → Right → Root) - useful for deleting the tree or bottom-up computations
fun postorderTraversal(node: TreeNode?): List<Int> {
    val result = mutableListOf<Int>()

    fun traverse(n: TreeNode?) {
        if (n == null) return

        traverse(n.left)      // Left
        traverse(n.right)     // Right
        result.add(n.value)   // Root
    }

    traverse(node)
    return result
}

// Level-order (BFS) - level by level traversal
fun levelOrder(root: TreeNode?): List<List<Int>> {
    if (root == null) return emptyList()

    val result = mutableListOf<List<Int>>()
    val queue = LinkedList<TreeNode>()
    queue.offer(root)

    while (queue.isNotEmpty()) {
        val levelSize = queue.size
        val level = mutableListOf<Int>()

        repeat(levelSize) {
            val node = queue.poll()
            level.add(node.value)

            node.left?.let { queue.offer(it) }
            node.right?.let { queue.offer(it) }
        }

        result.add(level)
    }

    return result
}
```

**AVL Trees (Self-Balancing BST):**
AVL trees are self-balancing BSTs: they maintain tree height O(log n), so search, insert, and delete operations run in O(log n) time in the worst case. For every node, the height difference between left and right subtrees is at most 1.

**Balance Factor:** height(left) - height(right) ∈ {-1, 0, 1}

```kotlin
class AVLNode(
    var value: Int,
    var left: AVLNode? = null,
    var right: AVLNode? = null,
    var height: Int = 1
)

class AVLTree {
    var root: AVLNode? = null

    private fun height(node: AVLNode?): Int = node?.height ?: 0

    private fun balanceFactor(node: AVLNode?): Int {
        if (node == null) return 0
        return height(node.left) - height(node.right)
    }

    private fun updateHeight(node: AVLNode) {
        node.height = 1 + maxOf(height(node.left), height(node.right))
    }

    // Right rotation for Left-Left case
    private fun rotateRight(y: AVLNode): AVLNode {
        val x = y.left!!
        val B = x.right

        x.right = y
        y.left = B

        updateHeight(y)
        updateHeight(x)

        return x
    }

    // Left rotation for Right-Right case
    private fun rotateLeft(x: AVLNode): AVLNode {
        val y = x.right!!
        val B = y.left

        y.left = x
        x.right = B

        updateHeight(x)
        updateHeight(y)

        return y
    }

    fun insert(value: Int) {
        root = insertRec(root, value)
    }

    private fun insertRec(node: AVLNode?, value: Int): AVLNode {
        // Standard BST insert
        if (node == null) return AVLNode(value)

        when {
            value < node.value -> node.left = insertRec(node.left, value)
            value > node.value -> node.right = insertRec(node.right, value)
            else -> return node  // Do not insert duplicates
        }

        // Update height of this node
        updateHeight(node)

        // Compute balance factor
        val balance = balanceFactor(node)

        // Four standard imbalance cases along the insertion path:
        // Left-Left Case
        if (balance > 1 && value < node.left!!.value) {
            return rotateRight(node)
        }

        // Right-Right Case
        if (balance < -1 && value > node.right!!.value) {
            return rotateLeft(node)
        }

        // Left-Right Case
        if (balance > 1 && value > node.left!!.value) {
            node.left = rotateLeft(node.left!!)
            return rotateRight(node)
        }

        // Right-Left Case
        if (balance < -1 && value < node.right!!.value) {
            node.right = rotateRight(node.right!!)
            return rotateLeft(node)
        }

        return node
    }
}
```

---

## Follow-ups

- What is the difference between BST and Binary Tree?
- How do AVL trees compare to Red-Black trees?
- What are the four rotation cases in AVL trees?

## References

- [[c-algorithms]]
- "https://en.wikipedia.org/wiki/AVL_tree"
- "https://en.wikipedia.org/wiki/Binary_search_tree"

## Related Questions

### Prerequisites (Easier)
- [[q-data-structures-overview--algorithms--easy]] - Data structures basics
- [[q-binary-search-variants--algorithms--medium]] - Binary search concepts

### Related (Same Level)
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]] - Graph traversal
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - DP concepts

### Advanced (Harder)

## Дополнительные Вопросы (RU)
- В чем разница между BST и бинарным деревом?
- Как AVL деревья сравниваются с красно-черными деревьями?
- Каковы четыре типа вращений в AVL деревьях?
## Связанные Вопросы (RU)
### Предпосылки (проще)
- [[q-data-structures-overview--algorithms--easy]] - Базовые структуры данных
- [[q-binary-search-variants--algorithms--medium]] - Концепции бинарного поиска
### Связанные (тот Же уровень)
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]] - Обходы графов
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - Основы динамического программирования
### Продвинутые (сложнее)