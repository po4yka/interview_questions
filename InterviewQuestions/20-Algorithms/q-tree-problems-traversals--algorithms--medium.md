---
id: algo-019
title: Tree Problems and Traversals / Задачи на деревья и обходы
aliases:
- Tree Traversals
- Binary Tree Problems
- LCA
- Обходы деревьев
- Задачи на бинарные деревья
topic: algorithms
subtopics:
- tree
- traversal
- lca
- binary-tree
question_kind: coding
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-algorithms
related:
- c-tree
- c-binary-tree
- q-binary-search-trees-bst--algorithms--hard
created: 2026-01-23
updated: 2026-01-23
tags:
- algorithms
- tree
- difficulty/medium
- traversal
- lca
- binary-tree
sources:
- https://en.wikipedia.org/wiki/Tree_traversal
- https://en.wikipedia.org/wiki/Lowest_common_ancestor
anki_cards:
- slug: algo-019-0-en
  language: en
  anki_id: 1769168920326
  synced_at: '2026-01-23T15:48:41.158513'
- slug: algo-019-0-ru
  language: ru
  anki_id: 1769168920348
  synced_at: '2026-01-23T15:48:41.160303'
---
# Вопрос (RU)
> Объясни обходы бинарного дерева (inorder, preorder, postorder, level-order). Как найти LCA (наименьшего общего предка)? Какие типичные задачи на деревья?

# Question (EN)
> Explain binary tree traversals (inorder, preorder, postorder, level-order). How do you find LCA (Lowest Common Ancestor)? What are typical tree problems?

---

## Ответ (RU)

**Определение узла дерева:**
```kotlin
class TreeNode(var `val`: Int) {
    var left: TreeNode? = null
    var right: TreeNode? = null
}
```

**Обходы дерева - рекурсивно:**
```kotlin
// Inorder: левый -> корень -> правый (отсортированный для BST)
fun inorderTraversal(root: TreeNode?): List<Int> {
    val result = mutableListOf<Int>()

    fun traverse(node: TreeNode?) {
        if (node == null) return
        traverse(node.left)
        result.add(node.`val`)
        traverse(node.right)
    }

    traverse(root)
    return result
}

// Preorder: корень -> левый -> правый (копирование дерева)
fun preorderTraversal(root: TreeNode?): List<Int> {
    val result = mutableListOf<Int>()

    fun traverse(node: TreeNode?) {
        if (node == null) return
        result.add(node.`val`)
        traverse(node.left)
        traverse(node.right)
    }

    traverse(root)
    return result
}

// Postorder: левый -> правый -> корень (удаление дерева)
fun postorderTraversal(root: TreeNode?): List<Int> {
    val result = mutableListOf<Int>()

    fun traverse(node: TreeNode?) {
        if (node == null) return
        traverse(node.left)
        traverse(node.right)
        result.add(node.`val`)
    }

    traverse(root)
    return result
}
```

**Обходы - итеративно со стеком:**
```kotlin
// Inorder итеративно
fun inorderIterative(root: TreeNode?): List<Int> {
    val result = mutableListOf<Int>()
    val stack = ArrayDeque<TreeNode>()
    var current = root

    while (current != null || stack.isNotEmpty()) {
        // Идём максимально влево
        while (current != null) {
            stack.push(current)
            current = current.left
        }

        current = stack.pop()
        result.add(current.`val`)
        current = current.right
    }

    return result
}

// Preorder итеративно
fun preorderIterative(root: TreeNode?): List<Int> {
    if (root == null) return emptyList()

    val result = mutableListOf<Int>()
    val stack = ArrayDeque<TreeNode>()
    stack.push(root)

    while (stack.isNotEmpty()) {
        val node = stack.pop()
        result.add(node.`val`)

        // Правый первым (чтобы левый обработался первым)
        node.right?.let { stack.push(it) }
        node.left?.let { stack.push(it) }
    }

    return result
}
```

**Level Order Traversal (BFS):**
```kotlin
fun levelOrder(root: TreeNode?): List<List<Int>> {
    if (root == null) return emptyList()

    val result = mutableListOf<List<Int>>()
    val queue = ArrayDeque<TreeNode>()
    queue.add(root)

    while (queue.isNotEmpty()) {
        val level = mutableListOf<Int>()
        val levelSize = queue.size

        repeat(levelSize) {
            val node = queue.removeFirst()
            level.add(node.`val`)

            node.left?.let { queue.add(it) }
            node.right?.let { queue.add(it) }
        }

        result.add(level)
    }

    return result
}
```

**Lowest Common Ancestor (LCA):**
```kotlin
// LCA для бинарного дерева
fun lowestCommonAncestor(
    root: TreeNode?,
    p: TreeNode?,
    q: TreeNode?
): TreeNode? {
    if (root == null || root == p || root == q) return root

    val left = lowestCommonAncestor(root.left, p, q)
    val right = lowestCommonAncestor(root.right, p, q)

    // Если оба найдены в разных поддеревьях, root - LCA
    if (left != null && right != null) return root

    // Иначе возвращаем ненулевой результат
    return left ?: right
}

// LCA для BST (оптимизация)
fun lowestCommonAncestorBST(
    root: TreeNode?,
    p: TreeNode?,
    q: TreeNode?
): TreeNode? {
    var current = root

    while (current != null) {
        when {
            p!!.`val` < current.`val` && q!!.`val` < current.`val` ->
                current = current.left
            p.`val` > current.`val` && q!!.`val` > current.`val` ->
                current = current.right
            else -> return current  // Разделение = LCA
        }
    }

    return null
}
```

**Maximum Depth of Binary Tree:**
```kotlin
fun maxDepth(root: TreeNode?): Int {
    if (root == null) return 0
    return 1 + maxOf(maxDepth(root.left), maxDepth(root.right))
}
```

**Same Tree / Symmetric Tree:**
```kotlin
fun isSameTree(p: TreeNode?, q: TreeNode?): Boolean {
    if (p == null && q == null) return true
    if (p == null || q == null) return false
    return p.`val` == q.`val` &&
           isSameTree(p.left, q.left) &&
           isSameTree(p.right, q.right)
}

fun isSymmetric(root: TreeNode?): Boolean {
    fun isMirror(t1: TreeNode?, t2: TreeNode?): Boolean {
        if (t1 == null && t2 == null) return true
        if (t1 == null || t2 == null) return false
        return t1.`val` == t2.`val` &&
               isMirror(t1.left, t2.right) &&
               isMirror(t1.right, t2.left)
    }
    return isMirror(root, root)
}
```

**Path Sum:**
```kotlin
// Есть ли путь с суммой targetSum?
fun hasPathSum(root: TreeNode?, targetSum: Int): Boolean {
    if (root == null) return false

    // Лист
    if (root.left == null && root.right == null) {
        return root.`val` == targetSum
    }

    val remaining = targetSum - root.`val`
    return hasPathSum(root.left, remaining) ||
           hasPathSum(root.right, remaining)
}

// Все пути с суммой targetSum
fun pathSum(root: TreeNode?, targetSum: Int): List<List<Int>> {
    val result = mutableListOf<List<Int>>()

    fun dfs(node: TreeNode?, remaining: Int, path: MutableList<Int>) {
        if (node == null) return

        path.add(node.`val`)

        if (node.left == null && node.right == null && remaining == node.`val`) {
            result.add(path.toList())
        } else {
            dfs(node.left, remaining - node.`val`, path)
            dfs(node.right, remaining - node.`val`, path)
        }

        path.removeAt(path.lastIndex)  // Backtrack
    }

    dfs(root, targetSum, mutableListOf())
    return result
}
```

**Serialize and Deserialize Binary Tree:**
```kotlin
class Codec {
    fun serialize(root: TreeNode?): String {
        val result = StringBuilder()

        fun preorder(node: TreeNode?) {
            if (node == null) {
                result.append("null,")
                return
            }
            result.append("${node.`val`},")
            preorder(node.left)
            preorder(node.right)
        }

        preorder(root)
        return result.toString()
    }

    fun deserialize(data: String): TreeNode? {
        val nodes = data.split(",").toMutableList()
        var index = 0

        fun build(): TreeNode? {
            if (index >= nodes.size || nodes[index] == "null" || nodes[index].isEmpty()) {
                index++
                return null
            }

            val node = TreeNode(nodes[index].toInt())
            index++
            node.left = build()
            node.right = build()
            return node
        }

        return build()
    }
}
```

## Answer (EN)

**Tree Node Definition:**
```kotlin
class TreeNode(var `val`: Int) {
    var left: TreeNode? = null
    var right: TreeNode? = null
}
```

**Tree Traversals - Recursive:**
```kotlin
// Inorder: left -> root -> right (sorted for BST)
fun inorderTraversal(root: TreeNode?): List<Int> {
    val result = mutableListOf<Int>()

    fun traverse(node: TreeNode?) {
        if (node == null) return
        traverse(node.left)
        result.add(node.`val`)
        traverse(node.right)
    }

    traverse(root)
    return result
}

// Preorder: root -> left -> right (copy tree)
fun preorderTraversal(root: TreeNode?): List<Int> {
    val result = mutableListOf<Int>()

    fun traverse(node: TreeNode?) {
        if (node == null) return
        result.add(node.`val`)
        traverse(node.left)
        traverse(node.right)
    }

    traverse(root)
    return result
}

// Postorder: left -> right -> root (delete tree)
fun postorderTraversal(root: TreeNode?): List<Int> {
    val result = mutableListOf<Int>()

    fun traverse(node: TreeNode?) {
        if (node == null) return
        traverse(node.left)
        traverse(node.right)
        result.add(node.`val`)
    }

    traverse(root)
    return result
}
```

**Traversals - Iterative with Stack:**
```kotlin
// Inorder iterative
fun inorderIterative(root: TreeNode?): List<Int> {
    val result = mutableListOf<Int>()
    val stack = ArrayDeque<TreeNode>()
    var current = root

    while (current != null || stack.isNotEmpty()) {
        // Go as left as possible
        while (current != null) {
            stack.push(current)
            current = current.left
        }

        current = stack.pop()
        result.add(current.`val`)
        current = current.right
    }

    return result
}

// Preorder iterative
fun preorderIterative(root: TreeNode?): List<Int> {
    if (root == null) return emptyList()

    val result = mutableListOf<Int>()
    val stack = ArrayDeque<TreeNode>()
    stack.push(root)

    while (stack.isNotEmpty()) {
        val node = stack.pop()
        result.add(node.`val`)

        // Right first (so left is processed first)
        node.right?.let { stack.push(it) }
        node.left?.let { stack.push(it) }
    }

    return result
}
```

**Level Order Traversal (BFS):**
```kotlin
fun levelOrder(root: TreeNode?): List<List<Int>> {
    if (root == null) return emptyList()

    val result = mutableListOf<List<Int>>()
    val queue = ArrayDeque<TreeNode>()
    queue.add(root)

    while (queue.isNotEmpty()) {
        val level = mutableListOf<Int>()
        val levelSize = queue.size

        repeat(levelSize) {
            val node = queue.removeFirst()
            level.add(node.`val`)

            node.left?.let { queue.add(it) }
            node.right?.let { queue.add(it) }
        }

        result.add(level)
    }

    return result
}
```

**Lowest Common Ancestor (LCA):**
```kotlin
// LCA for binary tree
fun lowestCommonAncestor(
    root: TreeNode?,
    p: TreeNode?,
    q: TreeNode?
): TreeNode? {
    if (root == null || root == p || root == q) return root

    val left = lowestCommonAncestor(root.left, p, q)
    val right = lowestCommonAncestor(root.right, p, q)

    // If both found in different subtrees, root is LCA
    if (left != null && right != null) return root

    // Otherwise return non-null result
    return left ?: right
}

// LCA for BST (optimized)
fun lowestCommonAncestorBST(
    root: TreeNode?,
    p: TreeNode?,
    q: TreeNode?
): TreeNode? {
    var current = root

    while (current != null) {
        when {
            p!!.`val` < current.`val` && q!!.`val` < current.`val` ->
                current = current.left
            p.`val` > current.`val` && q!!.`val` > current.`val` ->
                current = current.right
            else -> return current  // Split point = LCA
        }
    }

    return null
}
```

**Maximum Depth of Binary Tree:**
```kotlin
fun maxDepth(root: TreeNode?): Int {
    if (root == null) return 0
    return 1 + maxOf(maxDepth(root.left), maxDepth(root.right))
}
```

**Same Tree / Symmetric Tree:**
```kotlin
fun isSameTree(p: TreeNode?, q: TreeNode?): Boolean {
    if (p == null && q == null) return true
    if (p == null || q == null) return false
    return p.`val` == q.`val` &&
           isSameTree(p.left, q.left) &&
           isSameTree(p.right, q.right)
}

fun isSymmetric(root: TreeNode?): Boolean {
    fun isMirror(t1: TreeNode?, t2: TreeNode?): Boolean {
        if (t1 == null && t2 == null) return true
        if (t1 == null || t2 == null) return false
        return t1.`val` == t2.`val` &&
               isMirror(t1.left, t2.right) &&
               isMirror(t1.right, t2.left)
    }
    return isMirror(root, root)
}
```

**Path Sum:**
```kotlin
// Is there a path with sum targetSum?
fun hasPathSum(root: TreeNode?, targetSum: Int): Boolean {
    if (root == null) return false

    // Leaf
    if (root.left == null && root.right == null) {
        return root.`val` == targetSum
    }

    val remaining = targetSum - root.`val`
    return hasPathSum(root.left, remaining) ||
           hasPathSum(root.right, remaining)
}

// All paths with sum targetSum
fun pathSum(root: TreeNode?, targetSum: Int): List<List<Int>> {
    val result = mutableListOf<List<Int>>()

    fun dfs(node: TreeNode?, remaining: Int, path: MutableList<Int>) {
        if (node == null) return

        path.add(node.`val`)

        if (node.left == null && node.right == null && remaining == node.`val`) {
            result.add(path.toList())
        } else {
            dfs(node.left, remaining - node.`val`, path)
            dfs(node.right, remaining - node.`val`, path)
        }

        path.removeAt(path.lastIndex)  // Backtrack
    }

    dfs(root, targetSum, mutableListOf())
    return result
}
```

**Serialize and Deserialize Binary Tree:**
```kotlin
class Codec {
    fun serialize(root: TreeNode?): String {
        val result = StringBuilder()

        fun preorder(node: TreeNode?) {
            if (node == null) {
                result.append("null,")
                return
            }
            result.append("${node.`val`},")
            preorder(node.left)
            preorder(node.right)
        }

        preorder(root)
        return result.toString()
    }

    fun deserialize(data: String): TreeNode? {
        val nodes = data.split(",").toMutableList()
        var index = 0

        fun build(): TreeNode? {
            if (index >= nodes.size || nodes[index] == "null" || nodes[index].isEmpty()) {
                index++
                return null
            }

            val node = TreeNode(nodes[index].toInt())
            index++
            node.left = build()
            node.right = build()
            return node
        }

        return build()
    }
}
```

---

## Follow-ups

- How do you find the diameter of a binary tree?
- How do you invert a binary tree?
- What is Morris Traversal and when would you use it?

## Related Questions

### Prerequisites (Easier)
- [[q-data-structures-overview--algorithms--easy]] - Data structures basics
- [[q-stack-queue-problems--algorithms--medium]] - Stack for traversals

### Related (Same Level)
- [[q-binary-search-trees-bst--algorithms--hard]] - BST operations
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]] - Graph traversals

### Advanced (Harder)
- [[q-trie-data-structure--algorithms--hard]] - Trie (prefix tree)
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - DP on trees
