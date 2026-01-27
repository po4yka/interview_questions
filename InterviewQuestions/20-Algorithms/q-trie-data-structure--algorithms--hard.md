---
id: algo-021
title: Trie Data Structure / Префиксное дерево (Trie)
aliases:
- Trie
- Prefix Tree
- Префиксное дерево
- Бор
topic: algorithms
subtopics:
- trie
- prefix-tree
- string
question_kind: coding
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-algorithms
related:
- c-trie
- c-prefix-tree
- q-string-algorithms--algorithms--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- algorithms
- trie
- difficulty/hard
- prefix-tree
- string
sources:
- https://en.wikipedia.org/wiki/Trie
anki_cards:
- slug: algo-021-0-en
  language: en
  anki_id: 1769168919293
  synced_at: '2026-01-26T09:10:14.490300'
- slug: algo-021-0-ru
  language: ru
  anki_id: 1769168919354
  synced_at: '2026-01-26T09:10:14.491696'
---
# Вопрос (RU)
> Что такое Trie (префиксное дерево)? Как его реализовать? Какие задачи решаются с помощью Trie?

# Question (EN)
> What is a Trie (prefix tree)? How do you implement it? What problems are solved using Trie?

---

## Ответ (RU)

**Теория Trie:**
Trie (префиксное дерево, бор) - древовидная структура для хранения строк, где каждый узел представляет символ. Обеспечивает O(m) операции, где m - длина строки. Идеально для автодополнения, проверки префиксов и словарей.

**Базовая реализация:**
```kotlin
class TrieNode {
    val children = mutableMapOf<Char, TrieNode>()
    var isEndOfWord = false
}

class Trie {
    private val root = TrieNode()

    // Вставка слова O(m)
    fun insert(word: String) {
        var node = root

        for (char in word) {
            node = node.children.getOrPut(char) { TrieNode() }
        }

        node.isEndOfWord = true
    }

    // Поиск слова O(m)
    fun search(word: String): Boolean {
        val node = findNode(word)
        return node?.isEndOfWord == true
    }

    // Проверка префикса O(m)
    fun startsWith(prefix: String): Boolean {
        return findNode(prefix) != null
    }

    private fun findNode(prefix: String): TrieNode? {
        var node = root

        for (char in prefix) {
            node = node.children[char] ?: return null
        }

        return node
    }
}

// Использование
val trie = Trie()
trie.insert("apple")
trie.search("apple")   // true
trie.search("app")     // false
trie.startsWith("app") // true
```

**Реализация через массив (быстрее для ASCII):**
```kotlin
class TrieArrayNode {
    val children = arrayOfNulls<TrieArrayNode>(26)
    var isEndOfWord = false
}

class TrieArray {
    private val root = TrieArrayNode()

    fun insert(word: String) {
        var node = root

        for (char in word) {
            val index = char - 'a'
            if (node.children[index] == null) {
                node.children[index] = TrieArrayNode()
            }
            node = node.children[index]!!
        }

        node.isEndOfWord = true
    }

    fun search(word: String): Boolean {
        var node = root

        for (char in word) {
            val index = char - 'a'
            node = node.children[index] ?: return false
        }

        return node.isEndOfWord
    }
}
```

**Автодополнение (все слова с префиксом):**
```kotlin
class TrieWithAutocomplete {
    private val root = TrieNode()

    fun insert(word: String) {
        var node = root
        for (char in word) {
            node = node.children.getOrPut(char) { TrieNode() }
        }
        node.isEndOfWord = true
    }

    fun autocomplete(prefix: String): List<String> {
        val result = mutableListOf<String>()
        val node = findNode(prefix) ?: return result

        collectWords(node, StringBuilder(prefix), result)
        return result
    }

    private fun collectWords(
        node: TrieNode,
        current: StringBuilder,
        result: MutableList<String>
    ) {
        if (node.isEndOfWord) {
            result.add(current.toString())
        }

        for ((char, child) in node.children) {
            current.append(char)
            collectWords(child, current, result)
            current.deleteCharAt(current.lastIndex)
        }
    }

    private fun findNode(prefix: String): TrieNode? {
        var node = root
        for (char in prefix) {
            node = node.children[char] ?: return null
        }
        return node
    }
}
```

**Word Search II (поиск слов в сетке):**
```kotlin
fun findWords(board: Array<CharArray>, words: Array<String>): List<String> {
    // Строим Trie из слов
    val root = TrieNode()
    for (word in words) {
        var node = root
        for (char in word) {
            node = node.children.getOrPut(char) { TrieNode() }
        }
        node.isEndOfWord = true
    }

    val result = mutableSetOf<String>()
    val m = board.size
    val n = board[0].size

    fun dfs(i: Int, j: Int, node: TrieNode, path: StringBuilder) {
        if (i < 0 || i >= m || j < 0 || j >= n) return

        val char = board[i][j]
        if (char == '#' || char !in node.children) return

        val nextNode = node.children[char]!!
        path.append(char)

        if (nextNode.isEndOfWord) {
            result.add(path.toString())
        }

        // Помечаем как посещённую
        board[i][j] = '#'

        // DFS в 4 направлениях
        dfs(i + 1, j, nextNode, path)
        dfs(i - 1, j, nextNode, path)
        dfs(i, j + 1, nextNode, path)
        dfs(i, j - 1, nextNode, path)

        // Восстанавливаем
        board[i][j] = char
        path.deleteCharAt(path.lastIndex)
    }

    for (i in 0 until m) {
        for (j in 0 until n) {
            dfs(i, j, root, StringBuilder())
        }
    }

    return result.toList()
}
```

**Design Add and Search Words (с wildcard '.'):**
```kotlin
class WordDictionary {
    private val root = TrieNode()

    fun addWord(word: String) {
        var node = root
        for (char in word) {
            node = node.children.getOrPut(char) { TrieNode() }
        }
        node.isEndOfWord = true
    }

    fun search(word: String): Boolean {
        return searchHelper(word, 0, root)
    }

    private fun searchHelper(word: String, index: Int, node: TrieNode): Boolean {
        if (index == word.length) {
            return node.isEndOfWord
        }

        val char = word[index]

        if (char == '.') {
            // Wildcard - проверяем все дети
            for (child in node.children.values) {
                if (searchHelper(word, index + 1, child)) {
                    return true
                }
            }
            return false
        } else {
            val nextNode = node.children[char] ?: return false
            return searchHelper(word, index + 1, nextNode)
        }
    }
}
```

**Longest Common Prefix:**
```kotlin
fun longestCommonPrefix(strs: Array<String>): String {
    if (strs.isEmpty()) return ""

    // Строим Trie
    val root = TrieNode()
    for (word in strs) {
        if (word.isEmpty()) return ""
        var node = root
        for (char in word) {
            node = node.children.getOrPut(char) { TrieNode() }
        }
        node.isEndOfWord = true
    }

    // Находим общий префикс
    val prefix = StringBuilder()
    var node = root

    while (node.children.size == 1 && !node.isEndOfWord) {
        val (char, child) = node.children.entries.first()
        prefix.append(char)
        node = child
    }

    return prefix.toString()
}
```

**Сравнение Trie с другими структурами:**
| Структура | Поиск | Вставка | Префикс | Память |
|-----------|-------|---------|---------|--------|
| HashSet | O(m) | O(m) | O(nm) | O(nm) |
| Trie | O(m) | O(m) | O(m) | O(nm) |
| Sorted Array | O(m log n) | O(n) | O(m log n) | O(nm) |

**Когда использовать Trie:**
- Автодополнение
- Проверка орфографии
- IP-маршрутизация (longest prefix match)
- Поиск слов с wildcards

## Answer (EN)

**Trie Theory:**
A Trie (prefix tree) is a tree-like structure for storing strings where each node represents a character. Provides O(m) operations where m is string length. Ideal for autocomplete, prefix checking, and dictionaries.

**Basic Implementation:**
```kotlin
class TrieNode {
    val children = mutableMapOf<Char, TrieNode>()
    var isEndOfWord = false
}

class Trie {
    private val root = TrieNode()

    // Insert word O(m)
    fun insert(word: String) {
        var node = root

        for (char in word) {
            node = node.children.getOrPut(char) { TrieNode() }
        }

        node.isEndOfWord = true
    }

    // Search word O(m)
    fun search(word: String): Boolean {
        val node = findNode(word)
        return node?.isEndOfWord == true
    }

    // Check prefix O(m)
    fun startsWith(prefix: String): Boolean {
        return findNode(prefix) != null
    }

    private fun findNode(prefix: String): TrieNode? {
        var node = root

        for (char in prefix) {
            node = node.children[char] ?: return null
        }

        return node
    }
}

// Usage
val trie = Trie()
trie.insert("apple")
trie.search("apple")   // true
trie.search("app")     // false
trie.startsWith("app") // true
```

**Array-based Implementation (faster for ASCII):**
```kotlin
class TrieArrayNode {
    val children = arrayOfNulls<TrieArrayNode>(26)
    var isEndOfWord = false
}

class TrieArray {
    private val root = TrieArrayNode()

    fun insert(word: String) {
        var node = root

        for (char in word) {
            val index = char - 'a'
            if (node.children[index] == null) {
                node.children[index] = TrieArrayNode()
            }
            node = node.children[index]!!
        }

        node.isEndOfWord = true
    }

    fun search(word: String): Boolean {
        var node = root

        for (char in word) {
            val index = char - 'a'
            node = node.children[index] ?: return false
        }

        return node.isEndOfWord
    }
}
```

**Autocomplete (all words with prefix):**
```kotlin
class TrieWithAutocomplete {
    private val root = TrieNode()

    fun insert(word: String) {
        var node = root
        for (char in word) {
            node = node.children.getOrPut(char) { TrieNode() }
        }
        node.isEndOfWord = true
    }

    fun autocomplete(prefix: String): List<String> {
        val result = mutableListOf<String>()
        val node = findNode(prefix) ?: return result

        collectWords(node, StringBuilder(prefix), result)
        return result
    }

    private fun collectWords(
        node: TrieNode,
        current: StringBuilder,
        result: MutableList<String>
    ) {
        if (node.isEndOfWord) {
            result.add(current.toString())
        }

        for ((char, child) in node.children) {
            current.append(char)
            collectWords(child, current, result)
            current.deleteCharAt(current.lastIndex)
        }
    }

    private fun findNode(prefix: String): TrieNode? {
        var node = root
        for (char in prefix) {
            node = node.children[char] ?: return null
        }
        return node
    }
}
```

**Word Search II (find words in grid):**
```kotlin
fun findWords(board: Array<CharArray>, words: Array<String>): List<String> {
    // Build Trie from words
    val root = TrieNode()
    for (word in words) {
        var node = root
        for (char in word) {
            node = node.children.getOrPut(char) { TrieNode() }
        }
        node.isEndOfWord = true
    }

    val result = mutableSetOf<String>()
    val m = board.size
    val n = board[0].size

    fun dfs(i: Int, j: Int, node: TrieNode, path: StringBuilder) {
        if (i < 0 || i >= m || j < 0 || j >= n) return

        val char = board[i][j]
        if (char == '#' || char !in node.children) return

        val nextNode = node.children[char]!!
        path.append(char)

        if (nextNode.isEndOfWord) {
            result.add(path.toString())
        }

        // Mark as visited
        board[i][j] = '#'

        // DFS in 4 directions
        dfs(i + 1, j, nextNode, path)
        dfs(i - 1, j, nextNode, path)
        dfs(i, j + 1, nextNode, path)
        dfs(i, j - 1, nextNode, path)

        // Restore
        board[i][j] = char
        path.deleteCharAt(path.lastIndex)
    }

    for (i in 0 until m) {
        for (j in 0 until n) {
            dfs(i, j, root, StringBuilder())
        }
    }

    return result.toList()
}
```

**Design Add and Search Words (with wildcard '.'):**
```kotlin
class WordDictionary {
    private val root = TrieNode()

    fun addWord(word: String) {
        var node = root
        for (char in word) {
            node = node.children.getOrPut(char) { TrieNode() }
        }
        node.isEndOfWord = true
    }

    fun search(word: String): Boolean {
        return searchHelper(word, 0, root)
    }

    private fun searchHelper(word: String, index: Int, node: TrieNode): Boolean {
        if (index == word.length) {
            return node.isEndOfWord
        }

        val char = word[index]

        if (char == '.') {
            // Wildcard - check all children
            for (child in node.children.values) {
                if (searchHelper(word, index + 1, child)) {
                    return true
                }
            }
            return false
        } else {
            val nextNode = node.children[char] ?: return false
            return searchHelper(word, index + 1, nextNode)
        }
    }
}
```

**Longest Common Prefix:**
```kotlin
fun longestCommonPrefix(strs: Array<String>): String {
    if (strs.isEmpty()) return ""

    // Build Trie
    val root = TrieNode()
    for (word in strs) {
        if (word.isEmpty()) return ""
        var node = root
        for (char in word) {
            node = node.children.getOrPut(char) { TrieNode() }
        }
        node.isEndOfWord = true
    }

    // Find common prefix
    val prefix = StringBuilder()
    var node = root

    while (node.children.size == 1 && !node.isEndOfWord) {
        val (char, child) = node.children.entries.first()
        prefix.append(char)
        node = child
    }

    return prefix.toString()
}
```

**Trie vs Other Structures:**
| Structure | Search | Insert | Prefix | Memory |
|-----------|--------|--------|--------|--------|
| HashSet | O(m) | O(m) | O(nm) | O(nm) |
| Trie | O(m) | O(m) | O(m) | O(nm) |
| Sorted Array | O(m log n) | O(n) | O(m log n) | O(nm) |

**When to Use Trie:**
- Autocomplete
- Spell checking
- IP routing (longest prefix match)
- Word search with wildcards

---

## Follow-ups

- How do you delete a word from Trie?
- What is a compressed Trie (Radix Tree)?
- How would you implement a Trie with frequency counts?

## Related Questions

### Prerequisites (Easier)
- [[q-string-algorithms--algorithms--medium]] - String basics
- [[q-tree-problems-traversals--algorithms--medium]] - Tree traversals

### Related (Same Level)
- [[q-string-pattern-matching--algorithms--hard]] - Pattern matching
- [[q-backtracking-algorithms--algorithms--hard]] - Backtracking

### Advanced (Harder)
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - DP
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]] - Graph search
