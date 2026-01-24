---
id: algo-006
title: Backtracking Algorithms (N-Queens, Sudoku, Subsets) / Алгоритмы с откатом
aliases:
- Backtracking Algorithms
- Алгоритмы с откатом
topic: algorithms
subtopics:
- backtracking
- combinatorics
- recursion
question_kind: coding
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-algorithms
related:
- c-algorithms
- c-backtracking-algorithm
- q-advanced-graph-algorithms--algorithms--hard
created: 2025-10-12
updated: 2025-11-11
tags:
- algorithms
- backtracking
- combinations
- difficulty/hard
- n-queens
- permutations
- recursion
- sudoku
sources:
- https://en.wikipedia.org/wiki/Backtracking
anki_cards:
- slug: algo-006-0-en
  language: en
  anki_id: 1768457298728
  synced_at: '2026-01-23T15:48:41.128764'
- slug: algo-006-0-ru
  language: ru
  anki_id: 1768457298754
  synced_at: '2026-01-23T15:48:41.130027'
- slug: algo-006-1-en
  language: en
  anki_id: 1768457298777
  synced_at: '2026-01-23T15:48:41.131345'
- slug: algo-006-1-ru
  language: ru
  anki_id: 1768457298802
  synced_at: '2026-01-23T15:48:41.132695'
---
# Вопрос (RU)
> Что такое backtracking? Как решать задачи N-Queens, Sudoku, Permutations, Combinations и Subsets?

# Question (EN)
> What is backtracking? How do you solve N-Queens, Sudoku, Permutations, Combinations, and Subsets problems?

---

## Ответ (RU)

**Теория Backtracking:**
Backtracking - это техника для систематического перебора вариантов в задачах с ограничениями. Алгоритм пошагово строит частичное решение и откатывается (backtrack), когда текущая конфигурация не может привести к валидному полному решению. Широко используется для головоломок, комбинаторных и некоторых оптимизационных задач (см. [[c-algorithms]]).

**Основные концепции:**
- Систематический перебор всех (или почти всех) возможностей
- Раннее отсечение невалидных ветвей по проверкам ограничений
- Естественное использование рекурсии (но можно реализовать итеративно со стеком)
- Типичная (часто худшая) сложность: экспоненциальная, например O(2^n) или O(n!) в зависимости от постановки, размеров входа и силы отсечения
- Пространственная сложность обычно O(n) для глубины рекурсии / стека состояния (n — размер решения)

**Общий шаблон Backtracking (упрощённый):**
```kotlin
// Универсальный упрощённый шаблон backtracking
// В реальных задачах множество допустимых choice'ов обычно зависит от текущего state.
fun <T> backtrack(
    state: MutableList<T>,
    choices: List<T>,
    result: MutableList<List<T>>
) {
    // Базовый случай: решение найдено
    if (isSolution(state)) {
        result.add(state.toList())
        return
    }

    // Пробуем каждый возможный выбор для текущего состояния
    for (choice in choices) {
        if (!isValid(state, choice)) continue

        // 1. Делаем выбор
        state.add(choice)

        // 2. Рекурсия
        backtrack(state, choices, result)

        // 3. Откат (отменяем выбор)
        state.removeAt(state.size - 1)
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

    // Пробуем разместить ферзя в каждом столбце текущей строки
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
// Временная сложность: экспоненциальная; грубо O(N!) без учёта отсечения.
```

**Sudoku Solver:**
```kotlin
// Заполнить сетку 9×9 цифрами 1-9 по правилам Судоку
fun solveSudoku(board: Array<CharArray>): Boolean {
    return backtrackSudoku(board, 0, 0)
}

fun backtrackSudoku(board: Array<CharArray>, row: Int, col: Int): Boolean {
    // Базовый случай: все строки обработаны
    if (row == 9) {
        return true
    }

    // Переход на следующую строку
    if (col == 9) {
        return backtrackSudoku(board, row + 1, 0)
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
// Временная сложность (в худшем случае) экспоненциальная относительно количества пустых клеток.
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
// Временная сложность: O(n * n!) по количеству генерируемых перестановок.
```

**Combinations:**
```kotlin
// Сгенерировать все подмножества размера k из чисел 1..n
fun combine(n: Int, k: Int): List<List<Int>> {
    val result = mutableListOf<List<Int>>()
    val current = mutableListOf<Int>()

    fun backtrack(start: Int) {
        // Базовый случай: комбинация завершена
        if (current.size == k) {
            result.add(current.toList())
            return
        }

        // Если оставшихся чисел недостаточно, можно прекратить
        if (current.size + (n - start + 1) < k) return

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
// Временная сложность: O(C(n, k) * k) на генерацию всех комбинаций.
```

**Subsets (Power `Set`):**
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
// Временная сложность: O(2^n * n) на генерацию всех подмножеств.
```

## Answer (EN)

**Backtracking Theory:**
Backtracking is a technique for systematically exploring search spaces in constraint satisfaction and combinatorial problems. It incrementally builds a partial solution and backtracks when the current configuration cannot lead to any valid complete solution. Commonly used for puzzles, combinatorics, and some optimization/search problems (see [[c-algorithms]]).

**Main concepts:**
- Systematically explores all (or almost all) possibilities
- Prunes invalid branches early using constraint checks
- Naturally implemented via recursion (or iteratively with an explicit stack)
- Typical (often worst-case) complexity is exponential, e.g. O(2^n) or O(n!), depending on the problem, input size, and pruning power
- Space complexity usually O(n) for recursion depth / state stack (n being the solution size)

**General Backtracking Template (simplified):**
```kotlin
// Generic simplified backtracking template.
// In real problems, available choices usually depend on the current state.
fun <T> backtrack(
    state: MutableList<T>,
    choices: List<T>,
    result: MutableList<List<T>>
) {
    // Base case: solution found
    if (isSolution(state)) {
        result.add(state.toList())
        return
    }

    // Try each possible choice for the current state
    for (choice in choices) {
        if (!isValid(state, choice)) continue

        // 1. Make choice
        state.add(choice)

        // 2. Recurse
        backtrack(state, choices, result)

        // 3. Backtrack (undo choice)
        state.removeAt(state.size - 1)
    }
}
```

**N-Queens Problem:**
```kotlin
// Place N queens on an N×N chessboard so no two attack each other
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

    // Try placing a queen in each column of the current row
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
// Time complexity: exponential; roughly O(N!) in the worst case without advanced pruning.
```

**Sudoku Solver:**
```kotlin
// Fill a 9×9 grid with digits 1-9 following Sudoku rules
fun solveSudoku(board: Array<CharArray>): Boolean {
    return backtrackSudoku(board, 0, 0)
}

fun backtrackSudoku(board: Array<CharArray>, row: Int, col: Int): Boolean {
    // Base case: all rows processed
    if (row == 9) {
        return true
    }

    // Move to next row
    if (col == 9) {
        return backtrackSudoku(board, row + 1, 0)
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
// Time complexity: exponential in the number of empty cells (backtracking over possibilities).
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
// Time complexity: O(n * n!) to generate all permutations.
```

**Combinations:**
```kotlin
// Generate all k-sized subsets from 1..n
fun combine(n: Int, k: Int): List<List<Int>> {
    val result = mutableListOf<List<Int>>()
    val current = mutableListOf<Int>()

    fun backtrack(start: Int) {
        // Base case: combination complete
        if (current.size == k) {
            result.add(current.toList())
            return
        }

        // Prune: if not enough numbers left to reach size k
        if (current.size + (n - start + 1) < k) return

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
// Time complexity: O(C(n, k) * k) to generate all combinations.
```

**Subsets (Power `Set`):**
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
// Time complexity: O(2^n * n) to generate the entire power set.
```

---

## Дополнительные Вопросы (RU)

- Чем backtracking отличается от динамического программирования?
- Каковы ключевые техники оптимизации backtracking-алгоритмов?
- Когда следует использовать backtracking по сравнению с другими подходами?

## Follow-ups

- How does backtracking differ from dynamic programming?
- What are the key optimization techniques for backtracking?
- When should you use backtracking vs other approaches?

## Ссылки (RU)

- [[c-algorithms]]
- "https://en.wikipedia.org/wiki/Backtracking"

## References

- [[c-algorithms]]
- "https://en.wikipedia.org/wiki/Backtracking"

## Связанные Вопросы (RU)

### Предпосылки (проще)
- [[q-data-structures-overview--algorithms--easy]] - Структуры данных

### Связанные (тот Же уровень)
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - Базовые концепции динамического программирования
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]] - Графовые алгоритмы

### Продвинутое (сложнее)

## Related Questions

### Prerequisites (Easier)
- [[q-data-structures-overview--algorithms--easy]] - Data structures

### Related (Same Level)
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - DP concepts
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]] - Graph algorithms

### Advanced (Harder)
