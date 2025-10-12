---
id: 20251012-200005
title: "Binary Search Trees and AVL Trees / Бинарные деревья поиска и AVL деревья"
slug: binary-search-trees-bst-algorithms-hard
topic: algorithms
subtopics:
  - trees
  - bst
  - avl
  - balanced-trees
  - tree-traversal
status: draft
difficulty: hard
moc: moc-algorithms
date_created: 2025-10-12
date_updated: 2025-10-12
related_questions:
  - q-binary-search-variants--algorithms--medium
  - q-graph-algorithms-bfs-dfs--algorithms--hard
tags:
  - algorithms
  - trees
  - bst
  - avl
  - data-structures
---

# Binary Search Trees and AVL Trees

## English Version

### Problem Statement

Binary Search Trees (BST) are fundamental data structures that allow efficient search, insertion, and deletion. AVL trees are self-balancing BSTs that maintain O(log n) operations even with sequential insertions.

**The Question:** How do BSTs work? What are the common operations? How do AVL trees maintain balance? What are tree traversal algorithms?

### Detailed Answer

#### Binary Search Tree (BST)

**Property:** For every node:
- All values in **left subtree** < node value
- All values in **right subtree** > node value

```kotlin
class TreeNode(
    var value: Int,
    var left: TreeNode? = null,
    var right: TreeNode? = null
)

class BST {
    var root: TreeNode? = null
    
    // Search: O(h) where h = height
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
            // Duplicate values typically ignored
        }
        
        return node
    }
    
    // Delete: O(h)
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
                
                // Case 3: Two children
                // Find inorder successor (smallest in right subtree)
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

// Example:
val bst = BST()
bst.insert(50)
bst.insert(30)
bst.insert(70)
bst.insert(20)
bst.insert(40)
bst.insert(60)
bst.insert(80)

//        50
//       /  \
//      30   70
//     / \   / \
//    20 40 60 80
```

---

### Tree Traversals

#### 1. Inorder (Left → Root → Right)

**Produces sorted order for BST!**

```kotlin
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

// Iterative with stack
fun inorderIterative(root: TreeNode?): List<Int> {
    val result = mutableListOf<Int>()
    val stack = Stack<TreeNode>()
    var current = root
    
    while (current != null || stack.isNotEmpty()) {
        // Go to leftmost node
        while (current != null) {
            stack.push(current)
            current = current.left
        }
        
        current = stack.pop()
        result.add(current.value)
        current = current.right
    }
    
    return result
}

// Example:
//     50
//    /  \
//   30   70
//  / \   / \
// 20 40 60 80
//
// Inorder: [20, 30, 40, 50, 60, 70, 80] (sorted!)
```

#### 2. Preorder (Root → Left → Right)

**Used for creating copy of tree.**

```kotlin
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

// Preorder: [50, 30, 20, 40, 70, 60, 80]
```

#### 3. Postorder (Left → Right → Root)

**Used for deleting tree.**

```kotlin
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

// Postorder: [20, 40, 30, 60, 80, 70, 50]
```

#### 4. Level-Order (BFS)

```kotlin
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

// Level-order: [[50], [30, 70], [20, 40, 60, 80]]
```

---

### Common BST Problems

#### 1. Validate BST

```kotlin
fun isValidBST(root: TreeNode?): Boolean {
    fun validate(node: TreeNode?, min: Int?, max: Int?): Boolean {
        if (node == null) return true
        
        if ((min != null && node.value <= min) || 
            (max != null && node.value >= max)) {
            return false
        }
        
        return validate(node.left, min, node.value) &&
               validate(node.right, node.value, max)
    }
    
    return validate(root, null, null)
}
```

#### 2. Lowest Common Ancestor (LCA)

```kotlin
fun lowestCommonAncestor(root: TreeNode?, p: TreeNode, q: TreeNode): TreeNode? {
    if (root == null) return null
    
    // Both in left subtree
    if (p.value < root.value && q.value < root.value) {
        return lowestCommonAncestor(root.left, p, q)
    }
    
    // Both in right subtree
    if (p.value > root.value && q.value > root.value) {
        return lowestCommonAncestor(root.right, p, q)
    }
    
    // Split or one is root
    return root
}
```

#### 3. Kth Smallest Element

```kotlin
fun kthSmallest(root: TreeNode?, k: Int): Int {
    val stack = Stack<TreeNode>()
    var current = root
    var count = 0
    
    while (current != null || stack.isNotEmpty()) {
        while (current != null) {
            stack.push(current)
            current = current.left
        }
        
        current = stack.pop()
        count++
        
        if (count == k) return current.value
        
        current = current.right
    }
    
    throw IllegalArgumentException("k is larger than tree size")
}
```

#### 4. Convert Sorted Array to BST

```kotlin
fun sortedArrayToBST(nums: IntArray): TreeNode? {
    fun build(left: Int, right: Int): TreeNode? {
        if (left > right) return null
        
        val mid = left + (right - left) / 2
        val node = TreeNode(nums[mid])
        
        node.left = build(left, mid - 1)
        node.right = build(mid + 1, right)
        
        return node
    }
    
    return build(0, nums.size - 1)
}

// Example:
val nums = intArrayOf(1, 2, 3, 4, 5, 6, 7)
val bst = sortedArrayToBST(nums)
//       4
//      / \
//     2   6
//    / \ / \
//   1  3 5  7
```

---

### AVL Trees (Self-Balancing BST)

**Property:** For every node, height difference between left and right subtrees ≤ 1

**Balance Factor** = height(left) - height(right)
- Must be -1, 0, or 1
- If |balance factor| > 1 → need rotation

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
    
    // Right Rotation
    //       y                x
    //      / \              / \
    //     x   C    =>      A   y
    //    / \                  / \
    //   A   B                B   C
    private fun rotateRight(y: AVLNode): AVLNode {
        val x = y.left!!
        val B = x.right
        
        x.right = y
        y.left = B
        
        updateHeight(y)
        updateHeight(x)
        
        return x
    }
    
    // Left Rotation
    //     x                  y
    //    / \                / \
    //   A   y      =>      x   C
    //      / \            / \
    //     B   C          A   B
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
            else -> return node  // Duplicate
        }
        
        // Update height
        updateHeight(node)
        
        // Get balance factor
        val balance = balanceFactor(node)
        
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

// Example:
val avl = AVLTree()
avl.insert(10)
avl.insert(20)
avl.insert(30)  // Triggers rotation!

// Before rotation:   After rotation:
//     10                  20
//      \                 /  \
//      20               10  30
//       \
//       30
```

**Four Rotation Cases:**

```
1. Left-Left (LL):
       z                y
      /                / \
     y        =>      x   z
    /
   x
   Solution: Right rotation on z

2. Right-Right (RR):
   x                    y
    \                  / \
     y        =>      x   z
      \
       z
   Solution: Left rotation on x

3. Left-Right (LR):
     z                z              x
    /                /              / \
   x        =>      x      =>      y   z
    \              /
     y            y
   Solution: Left rotation on x, then right rotation on z

4. Right-Left (RL):
   x                x              y
    \                \            / \
     z      =>        y    =>    x   z
    /                  \
   y                    z
   Solution: Right rotation on z, then left rotation on x
```

---

### BST vs AVL Comparison

| Operation | BST Average | BST Worst | AVL |
|-----------|-------------|-----------|-----|
| **Search** | O(log n) | O(n) | O(log n) |
| **Insert** | O(log n) | O(n) | O(log n) |
| **Delete** | O(log n) | O(n) | O(log n) |
| **Space** | O(n) | O(n) | O(n) |

**BST worst case:** Skewed tree (becomes linked list)
```
10
 \
  20
   \
    30
     \
      40  ← O(n) height!
```

**AVL guarantees:** Height always O(log n)

---

### Real-World Android Example

```kotlin
// File system directory tree
data class FileNode(
    val name: String,
    var isDirectory: Boolean = false,
    var left: FileNode? = null,
    var right: FileNode? = null
)

class FileSystem {
    private var root: FileNode? = null
    
    fun addFile(path: String) {
        val fileName = path.substringAfterLast('/')
        root = insert(root, fileName, false)
    }
    
    fun addDirectory(path: String) {
        val dirName = path.substringAfterLast('/')
        root = insert(root, dirName, true)
    }
    
    private fun insert(node: FileNode?, name: String, isDir: Boolean): FileNode {
        if (node == null) return FileNode(name, isDir)
        
        when {
            name < node.name -> node.left = insert(node.left, name, isDir)
            name > node.name -> node.right = insert(node.right, name, isDir)
        }
        
        return node
    }
    
    fun listFiles(): List<String> {
        val result = mutableListOf<String>()
        
        fun inorder(node: FileNode?) {
            if (node == null) return
            inorder(node.left)
            result.add(if (node.isDirectory) "${node.name}/" else node.name)
            inorder(node.right)
        }
        
        inorder(root)
        return result
    }
}
```

---

### Key Takeaways

1. **BST property:** Left < Root < Right
2. **Operations:** Search, Insert, Delete all O(h) where h = height
3. **Traversals:** Inorder (sorted), Preorder (copy), Postorder (delete), Level-order (BFS)
4. **Inorder on BST** produces sorted sequence
5. **BST worst case:** O(n) when unbalanced (skewed tree)
6. **AVL trees:** Self-balancing, guaranteed O(log n) operations
7. **Balance factor:** height(left) - height(right), must be -1, 0, or 1
8. **Rotations:** Four cases (LL, RR, LR, RL) to maintain balance
9. **AVL overhead:** More rotations on insert/delete but faster searches
10. **Use BST** for simple cases, **AVL** when balance critical

---

## Russian Version

### Постановка задачи

Бинарные деревья поиска (BST) - фундаментальные структуры данных, позволяющие эффективный поиск, вставку и удаление. AVL деревья - самобалансирующиеся BST, которые поддерживают O(log n) операции даже при последовательных вставках.

**Вопрос:** Как работают BST? Каковы основные операции? Как AVL деревья поддерживают баланс? Каковы алгоритмы обхода деревьев?

### Ключевые выводы

1. **Свойство BST:** Левое < Корень < Правое
2. **Операции:** Поиск, Вставка, Удаление все O(h) где h = высота
3. **Обходы:** Inorder (sorted), Preorder (copy), Postorder (delete), Level-order (BFS)
4. **Inorder на BST** производит отсортированную последовательность
5. **BST худший случай:** O(n) когда несбалансирован
6. **AVL деревья:** Самобалансирующиеся, гарантированный O(log n)
7. **Balance factor:** height(left) - height(right), должен быть -1, 0, или 1
8. **Вращения:** Четыре случая (LL, RR, LR, RL) для поддержания баланса

## Follow-ups

1. What is the difference between BST and Binary Tree?
2. How do you find the height of a binary tree?
3. What is a Red-Black tree and how does it compare to AVL?
4. How do you serialize and deserialize a binary tree?
5. What is the diameter of a binary tree?
6. How do you check if a tree is balanced?
7. What is Morris traversal (O(1) space inorder)?
8. How do you find the successor/predecessor in BST?
9. What is a B-tree and when is it used?
10. How do you implement a Trie (prefix tree)?

---

## Related Questions

### Prerequisites (Easier)
- [[q-binary-search-variants--algorithms--medium]] - binary search variants   algorithms 
### Prerequisites (Easier)
- [[q-binary-search-variants--algorithms--medium]] - binary search variants   algorithms 
### Prerequisites (Easier)
- [[q-binary-search-variants--algorithms--medium]] - binary search variants   algorithms 
