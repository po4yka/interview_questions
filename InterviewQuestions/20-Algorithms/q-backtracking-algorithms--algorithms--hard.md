---
id: 20251012-200008
title: "Backtracking Algorithms (N-Queens, Sudoku, Subsets) / Алгоритмы с откатом"
aliases: ["Backtracking Algorithms", "Алгоритмы с откатом"]
topic: algorithms
subtopics: [backtracking, recursion, combinatorics]
question_kind: coding
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-algorithms
related: [c-backtracking-algorithm, q-dynamic-programming-fundamentals--algorithms--hard, q-graph-algorithms-bfs-dfs--algorithms--hard]
created: 2025-10-12
updated: 2025-01-25
tags: [algorithms, backtracking, recursion, n-queens, sudoku, permutations, combinations, difficulty/hard]
sources: [https://en.wikipedia.org/wiki/Backtracking]
---

# Вопрос (RU)
> Что такое backtracking? Как решать задачи N-Queens, Sudoku, Permutations, Combinations и Subsets?

# Question (EN)
> What is backtracking? How do you solve N-Queens, Sudoku, Permutations, Combinations, and Subsets problems?

---

## Ответ (RU)

**Теория Backtracking:**
Backtracking - это мощная техника для решения задач с ограничениями. Она строит решения постепенно и отказывается от частичных решений, которые не могут привести к валидным решениям. Используется для головоломок, комбинаторики и оптимизационных задач.

**Основные концепции:**
- Систематический перебор всех возможностей
- Раннее отсечение невалидных ветвей
- Естественное использование рекурсии
- Часто имеет сложность O(2^n) или O(n!)
- Пространственная сложность O(n) для стека рекурсии

**Общий шаблон Backtracking:**
```kotlin
// Универсальный шаблон backtracking
fun backtrack(
    state: MutableList<Any>,
    choices: List<Any>,
    result: MutableList<List<Any>>
) {
    // Базовый случай: решение найдено
    if (isSolution(state)) {
        result.add(state.toList())
        return
    }

    // Пробуем каждый выбор
    for (choice in choices) {
        // 1. Делаем выбор
        if (isValid(state, choice)) {
            state.add(choice)

            // 2. Рекурсия
            backtrack(state, choices, result)

            // 3. Откат (отменяем выбор)
            state.removeAt(state.size - 1)
        }
    }
}
```

**N-Queens Problem:**
```kotlin
// Разместить N ферзей на доске N×N так, чтобы никакие два не атаковали друг друга
fun solveNQueens(n: Int): List<List<String>> {
    val result = mutableListOf<List<String>>()
    val board = Array(n) { CharArray(n) { '.' } }

    backtrackQueens(board, 0, result)
    return result
}

fun backtrackQueens(
    board: Array<CharArray>,
    row: Int,
    result: MutableList<List<String>>
) {
    val n = board.size

    // Базовый случай: все ферзи размещены
    if (row == n) {
        result.add(board.map { String(it) })
        return
    }

    // Пробуем разместить ферзя в каждом столбце
    for (col in 0 until n) {
        if (isValidQueenPlacement(board, row, col)) {
            // Делаем выбор
            board[row][col] = 'Q'

            // Рекурсия
            backtrackQueens(board, row + 1, result)

            // Откат
            board[row][col] = '.'
        }
    }
}

fun isValidQueenPlacement(board: Array<CharArray>, row: Int, col: Int): Boolean {
    val n = board.size

    // Проверяем столбец
    for (i in 0 until row) {
        if (board[i][col] == 'Q') return false
    }

    // Проверяем диагональ (сверху-слева вниз-вправо)
    var i = row - 1
    var j = col - 1
    while (i >= 0 && j >= 0) {
        if (board[i][j] == 'Q') return false
        i--
        j--
    }

    // Проверяем анти-диагональ (сверху-справа вниз-влево)
    i = row - 1
    j = col + 1
    while (i >= 0 && j < n) {
        if (board[i][j] == 'Q') return false
        i--
        j++
    }

    return true
}
```

**Sudoku Solver:**
```kotlin
// Заполнить сетку 9×9 цифрами 1-9 по правилам Судоку
fun solveSudoku(board: Array<CharArray>): Boolean {
    return backtrackSudoku(board, 0, 0)
}

fun backtrackSudoku(board: Array<CharArray>, row: Int, col: Int): Boolean {
    // Переходим к следующей строке
    if (col == 9) {
        return backtrackSudoku(board, row + 1, 0)
    }

    // Базовый случай: все строки заполнены
    if (row == 9) {
        return true
    }

    // Пропускаем заполненные клетки
    if (board[row][col] != '.') {
        return backtrackSudoku(board, row, col + 1)
    }

    // Пробуем цифры 1-9
    for (digit in '1'..'9') {
        if (isValidSudoku(board, row, col, digit)) {
            // Делаем выбор
            board[row][col] = digit

            // Рекурсия
            if (backtrackSudoku(board, row, col + 1)) {
                return true  // Решение найдено!
            }

            // Откат
            board[row][col] = '.'
        }
    }

    return false  // Валидная цифра не найдена
}

fun isValidSudoku(board: Array<CharArray>, row: Int, col: Int, digit: Char): Boolean {
    // Проверяем строку
    for (c in 0..8) {
        if (board[row][c] == digit) return false
    }

    // Проверяем столбец
    for (r in 0..8) {
        if (board[r][col] == digit) return false
    }

    // Проверяем квадрат 3×3
    val boxRow = (row / 3) * 3
    val boxCol = (col / 3) * 3

    for (r in boxRow until boxRow + 3) {
        for (c in boxCol until boxCol + 3) {
            if (board[r][c] == digit) return false
        }
    }

    return true
}
```

**Permutations:**
```kotlin
// Сгенерировать все возможные перестановки элементов
fun permute(nums: IntArray): List<List<Int>> {
    val result = mutableListOf<List<Int>>()
    val current = mutableListOf<Int>()
    val used = BooleanArray(nums.size)

    fun backtrack() {
        // Базовый случай: перестановка завершена
        if (current.size == nums.size) {
            result.add(current.toList())
            return
        }

        // Пробуем каждое неиспользованное число
        for (i in nums.indices) {
            if (used[i]) continue

            // Делаем выбор
            current.add(nums[i])
            used[i] = true

            // Рекурсия
            backtrack()

            // Откат
            current.removeAt(current.size - 1)
            used[i] = false
        }
    }

    backtrack()
    return result
}
```

**Combinations:**
```kotlin
// Сгенерировать все подмножества размера k
fun combine(n: Int, k: Int): List<List<Int>> {
    val result = mutableListOf<List<Int>>()
    val current = mutableListOf<Int>()

    fun backtrack(start: Int) {
        // Базовый случай: комбинация завершена
        if (current.size == k) {
            result.add(current.toList())
            return
        }

        // Пробуем числа от start до n
        for (i in start..n) {
            // Делаем выбор
            current.add(i)

            // Рекурсия (начинаем с i+1 чтобы избежать дубликатов)
            backtrack(i + 1)

            // Откат
            current.removeAt(current.size - 1)
        }
    }

    backtrack(1)
    return result
}
```

**Subsets (Power Set):**
```kotlin
// Сгенерировать все возможные подмножества множества
fun subsets(nums: IntArray): List<List<Int>> {
    val result = mutableListOf<List<Int>>()
    val current = mutableListOf<Int>()

    fun backtrack(start: Int) {
        // Добавляем текущее подмножество (каждое состояние валидно)
        result.add(current.toList())

        // Пробуем добавить каждый оставшийся элемент
        for (i in start until nums.size) {
            // Делаем выбор
            current.add(nums[i])

            // Рекурсия
            backtrack(i + 1)

            // Откат
            current.removeAt(current.size - 1)
        }
    }

    backtrack(0)
    return result
}
```

## Answer (EN)

**Backtracking Theory:**
Backtracking is a powerful technique for solving constraint satisfaction problems. It builds solutions incrementally and abandons partial solutions that cannot lead to valid solutions. Essential for puzzles, combinatorics, and optimization problems.

**Main concepts:**
- Systematically explores all possibilities
- Prunes invalid branches early
- Naturally uses recursion
- Often O(2^n) or O(n!) time complexity
- O(n) space for recursion stack

**General Backtracking Template:**
```kotlin
// Generic backtracking template
fun backtrack(
    state: MutableList<Any>,
    choices: List<Any>,
    result: MutableList<List<Any>>
) {
    // Base case: solution found
    if (isSolution(state)) {
        result.add(state.toList())
        return
    }

    // Try each choice
    for (choice in choices) {
        // 1. Make choice
        if (isValid(state, choice)) {
            state.add(choice)

            // 2. Recurse
            backtrack(state, choices, result)

            // 3. Backtrack (undo choice)
            state.removeAt(state.size - 1)
        }
    }
}
```

**N-Queens Problem:**
```kotlin
// Place N queens on N×N chessboard so no two attack each other
fun solveNQueens(n: Int): List<List<String>> {
    val result = mutableListOf<List<String>>()
    val board = Array(n) { CharArray(n) { '.' } }

    backtrackQueens(board, 0, result)
    return result
}

fun backtrackQueens(
    board: Array<CharArray>,
    row: Int,
    result: MutableList<List<String>>
) {
    val n = board.size

    // Base case: all queens placed
    if (row == n) {
        result.add(board.map { String(it) })
        return
    }

    // Try placing queen in each column
    for (col in 0 until n) {
        if (isValidQueenPlacement(board, row, col)) {
            // Make choice
            board[row][col] = 'Q'

            // Recurse
            backtrackQueens(board, row + 1, result)

            // Backtrack
            board[row][col] = '.'
        }
    }
}

fun isValidQueenPlacement(board: Array<CharArray>, row: Int, col: Int): Boolean {
    val n = board.size

    // Check column
    for (i in 0 until row) {
        if (board[i][col] == 'Q') return false
    }

    // Check diagonal (top-left to bottom-right)
    var i = row - 1
    var j = col - 1
    while (i >= 0 && j >= 0) {
        if (board[i][j] == 'Q') return false
        i--
        j--
    }

    // Check anti-diagonal (top-right to bottom-left)
    i = row - 1
    j = col + 1
    while (i >= 0 && j < n) {
        if (board[i][j] == 'Q') return false
        i--
        j++
    }

    return true
}
```

**Sudoku Solver:**
```kotlin
// Fill 9×9 grid with digits 1-9 following Sudoku rules
fun solveSudoku(board: Array<CharArray>): Boolean {
    return backtrackSudoku(board, 0, 0)
}

fun backtrackSudoku(board: Array<CharArray>, row: Int, col: Int): Boolean {
    // Move to next row
    if (col == 9) {
        return backtrackSudoku(board, row + 1, 0)
    }

    // Base case: all rows filled
    if (row == 9) {
        return true
    }

    // Skip filled cells
    if (board[row][col] != '.') {
        return backtrackSudoku(board, row, col + 1)
    }

    // Try digits 1-9
    for (digit in '1'..'9') {
        if (isValidSudoku(board, row, col, digit)) {
            // Make choice
            board[row][col] = digit

            // Recurse
            if (backtrackSudoku(board, row, col + 1)) {
                return true  // Solution found!
            }

            // Backtrack
            board[row][col] = '.'
        }
    }

    return false  // No valid digit found
}

fun isValidSudoku(board: Array<CharArray>, row: Int, col: Int, digit: Char): Boolean {
    // Check row
    for (c in 0..8) {
        if (board[row][c] == digit) return false
    }

    // Check column
    for (r in 0..8) {
        if (board[r][col] == digit) return false
    }

    // Check 3×3 box
    val boxRow = (row / 3) * 3
    val boxCol = (col / 3) * 3

    for (r in boxRow until boxRow + 3) {
        for (c in boxCol until boxCol + 3) {
            if (board[r][c] == digit) return false
        }
    }

    return true
}
```

**Permutations:**
```kotlin
// Generate all possible orderings of elements
fun permute(nums: IntArray): List<List<Int>> {
    val result = mutableListOf<List<Int>>()
    val current = mutableListOf<Int>()
    val used = BooleanArray(nums.size)

    fun backtrack() {
        // Base case: permutation complete
        if (current.size == nums.size) {
            result.add(current.toList())
            return
        }

        // Try each unused number
        for (i in nums.indices) {
            if (used[i]) continue

            // Make choice
            current.add(nums[i])
            used[i] = true

            // Recurse
            backtrack()

            // Backtrack
            current.removeAt(current.size - 1)
            used[i] = false
        }
    }

    backtrack()
    return result
}
```

**Combinations:**
```kotlin
// Generate all k-sized subsets
fun combine(n: Int, k: Int): List<List<Int>> {
    val result = mutableListOf<List<Int>>()
    val current = mutableListOf<Int>()

    fun backtrack(start: Int) {
        // Base case: combination complete
        if (current.size == k) {
            result.add(current.toList())
            return
        }

        // Try numbers from start to n
        for (i in start..n) {
            // Make choice
            current.add(i)

            // Recurse (start from i+1 to avoid duplicates)
            backtrack(i + 1)

            // Backtrack
            current.removeAt(current.size - 1)
        }
    }

    backtrack(1)
    return result
}
```

**Subsets (Power Set):**
```kotlin
// Generate all possible subsets of a set
fun subsets(nums: IntArray): List<List<Int>> {
    val result = mutableListOf<List<Int>>()
    val current = mutableListOf<Int>()

    fun backtrack(start: Int) {
        // Add current subset (every state is valid)
        result.add(current.toList())

        // Try adding each remaining element
        for (i in start until nums.size) {
            // Make choice
            current.add(nums[i])

            // Recurse
            backtrack(i + 1)

            // Backtrack
            current.removeAt(current.size - 1)
        }
    }

    backtrack(0)
    return result
}
```

---

## Follow-ups

- How does backtracking differ from dynamic programming?
- What are the key optimization techniques for backtracking?
- When should you use backtracking vs other approaches?

## Related Questions

### Prerequisites (Easier)
- [[q-data-structures-overview--algorithms--easy]] - Data structures
- [[q-recursion-basics--algorithms--easy]] - Recursion basics

### Related (Same Level)
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - DP concepts
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]] - Graph algorithms

### Advanced (Harder)
- [[q-advanced-backtracking--algorithms--hard]] - Advanced backtracking
- [[q-constraint-satisfaction--algorithms--hard]] - CSP problems
