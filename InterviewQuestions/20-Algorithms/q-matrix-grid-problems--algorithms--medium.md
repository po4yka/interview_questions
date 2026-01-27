---
id: algo-020
title: Matrix and Grid Problems / Задачи на матрицы и сетки
aliases:
- Matrix Problems
- Grid Problems
- 2D Array
- Задачи на матрицы
- Задачи на сетки
topic: algorithms
subtopics:
- matrix
- grid
- 2d-array
question_kind: coding
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-algorithms
related:
- c-matrix
- c-grid
- q-graph-algorithms-bfs-dfs--algorithms--hard
created: 2026-01-23
updated: 2026-01-23
tags:
- algorithms
- matrix
- difficulty/medium
- grid
- 2d-array
sources:
- https://en.wikipedia.org/wiki/Matrix_(mathematics)
anki_cards:
- slug: algo-020-0-en
  language: en
  anki_id: 1769168918843
  synced_at: '2026-01-26T09:10:14.472301'
- slug: algo-020-0-ru
  language: ru
  anki_id: 1769168918874
  synced_at: '2026-01-26T09:10:14.473561'
---
# Вопрос (RU)
> Какие типичные задачи решаются на матрицах? Объясни поворот матрицы, спиральный обход, поиск в отсортированной матрице и DP на сетках.

# Question (EN)
> What typical problems are solved on matrices? Explain matrix rotation, spiral traversal, search in sorted matrix, and DP on grids.

---

## Ответ (RU)

**Теория работы с матрицами:**
Матрица - двумерный массив. Ключ к решению - правильно определить границы и направления обхода. Многие задачи используют DFS/BFS или DP.

**Поворот матрицы на 90 градусов по часовой:**
```kotlin
// In-place поворот
fun rotate(matrix: Array<IntArray>) {
    val n = matrix.size

    // Шаг 1: Транспонирование (отражение по главной диагонали)
    for (i in 0 until n) {
        for (j in i + 1 until n) {
            val temp = matrix[i][j]
            matrix[i][j] = matrix[j][i]
            matrix[j][i] = temp
        }
    }

    // Шаг 2: Отражение по вертикали (реверс строк)
    for (i in 0 until n) {
        matrix[i].reverse()
    }
}

// Пример:
// [1,2,3]    транспонирование    [1,4,7]    реверс    [7,4,1]
// [4,5,6]  ----------------->   [2,5,8]  ------->   [8,5,2]
// [7,8,9]                       [3,6,9]             [9,6,3]
```

**Спиральный обход матрицы:**
```kotlin
fun spiralOrder(matrix: Array<IntArray>): List<Int> {
    if (matrix.isEmpty()) return emptyList()

    val result = mutableListOf<Int>()
    var top = 0
    var bottom = matrix.size - 1
    var left = 0
    var right = matrix[0].size - 1

    while (top <= bottom && left <= right) {
        // Вправо
        for (i in left..right) {
            result.add(matrix[top][i])
        }
        top++

        // Вниз
        for (i in top..bottom) {
            result.add(matrix[i][right])
        }
        right--

        // Влево (если остались строки)
        if (top <= bottom) {
            for (i in right downTo left) {
                result.add(matrix[bottom][i])
            }
            bottom--
        }

        // Вверх (если остались столбцы)
        if (left <= right) {
            for (i in bottom downTo top) {
                result.add(matrix[i][left])
            }
            left++
        }
    }

    return result
}
```

**Генерация спиральной матрицы:**
```kotlin
fun generateMatrix(n: Int): Array<IntArray> {
    val matrix = Array(n) { IntArray(n) }
    var num = 1
    var top = 0
    var bottom = n - 1
    var left = 0
    var right = n - 1

    while (num <= n * n) {
        for (i in left..right) matrix[top][i] = num++
        top++

        for (i in top..bottom) matrix[i][right] = num++
        right--

        for (i in right downTo left) matrix[bottom][i] = num++
        bottom--

        for (i in bottom downTo top) matrix[i][left] = num++
        left++
    }

    return matrix
}
```

**Поиск в отсортированной матрице:**
```kotlin
// Матрица отсортирована по строкам и столбцам
// Начинаем с правого верхнего угла
fun searchMatrix(matrix: Array<IntArray>, target: Int): Boolean {
    if (matrix.isEmpty()) return false

    val m = matrix.size
    val n = matrix[0].size

    var row = 0
    var col = n - 1

    while (row < m && col >= 0) {
        when {
            matrix[row][col] == target -> return true
            matrix[row][col] > target -> col--  // Идём влево
            else -> row++  // Идём вниз
        }
    }

    return false
}

// Матрица полностью отсортирована (каждая строка начинается после предыдущей)
// Бинарный поиск как в 1D массиве
fun searchMatrixSorted(matrix: Array<IntArray>, target: Int): Boolean {
    if (matrix.isEmpty()) return false

    val m = matrix.size
    val n = matrix[0].size
    var left = 0
    var right = m * n - 1

    while (left <= right) {
        val mid = left + (right - left) / 2
        val midVal = matrix[mid / n][mid % n]

        when {
            midVal == target -> return true
            midVal < target -> left = mid + 1
            else -> right = mid - 1
        }
    }

    return false
}
```

**Set Matrix Zeroes:**
```kotlin
fun setZeroes(matrix: Array<IntArray>) {
    val m = matrix.size
    val n = matrix[0].size
    var firstRowZero = false
    var firstColZero = false

    // Проверяем первую строку и столбец
    for (j in 0 until n) if (matrix[0][j] == 0) firstRowZero = true
    for (i in 0 until m) if (matrix[i][0] == 0) firstColZero = true

    // Используем первую строку/столбец как маркеры
    for (i in 1 until m) {
        for (j in 1 until n) {
            if (matrix[i][j] == 0) {
                matrix[i][0] = 0
                matrix[0][j] = 0
            }
        }
    }

    // Заполняем нулями по маркерам
    for (i in 1 until m) {
        for (j in 1 until n) {
            if (matrix[i][0] == 0 || matrix[0][j] == 0) {
                matrix[i][j] = 0
            }
        }
    }

    // Обрабатываем первую строку и столбец
    if (firstRowZero) for (j in 0 until n) matrix[0][j] = 0
    if (firstColZero) for (i in 0 until m) matrix[i][0] = 0
}
```

**DP на сетке - Unique Paths:**
```kotlin
fun uniquePaths(m: Int, n: Int): Int {
    val dp = Array(m) { IntArray(n) { 1 } }

    for (i in 1 until m) {
        for (j in 1 until n) {
            dp[i][j] = dp[i - 1][j] + dp[i][j - 1]
        }
    }

    return dp[m - 1][n - 1]
}

// Оптимизация памяти до O(n)
fun uniquePathsOptimized(m: Int, n: Int): Int {
    val dp = IntArray(n) { 1 }

    for (i in 1 until m) {
        for (j in 1 until n) {
            dp[j] += dp[j - 1]
        }
    }

    return dp[n - 1]
}
```

**Minimum Path Sum:**
```kotlin
fun minPathSum(grid: Array<IntArray>): Int {
    val m = grid.size
    val n = grid[0].size
    val dp = Array(m) { IntArray(n) }

    dp[0][0] = grid[0][0]

    // Первая строка
    for (j in 1 until n) dp[0][j] = dp[0][j - 1] + grid[0][j]

    // Первый столбец
    for (i in 1 until m) dp[i][0] = dp[i - 1][0] + grid[i][0]

    // Остальные ячейки
    for (i in 1 until m) {
        for (j in 1 until n) {
            dp[i][j] = minOf(dp[i - 1][j], dp[i][j - 1]) + grid[i][j]
        }
    }

    return dp[m - 1][n - 1]
}
```

**Maximal Square:**
```kotlin
fun maximalSquare(matrix: Array<CharArray>): Int {
    if (matrix.isEmpty()) return 0

    val m = matrix.size
    val n = matrix[0].size
    val dp = Array(m + 1) { IntArray(n + 1) }
    var maxSide = 0

    for (i in 1..m) {
        for (j in 1..n) {
            if (matrix[i - 1][j - 1] == '1') {
                dp[i][j] = minOf(
                    dp[i - 1][j],
                    dp[i][j - 1],
                    dp[i - 1][j - 1]
                ) + 1
                maxSide = maxOf(maxSide, dp[i][j])
            }
        }
    }

    return maxSide * maxSide
}
```

## Answer (EN)

**Matrix Theory:**
A matrix is a 2D array. The key is correctly defining boundaries and traversal directions. Many problems use DFS/BFS or DP.

**Rotate Matrix 90 Degrees Clockwise:**
```kotlin
// In-place rotation
fun rotate(matrix: Array<IntArray>) {
    val n = matrix.size

    // Step 1: Transpose (reflect along main diagonal)
    for (i in 0 until n) {
        for (j in i + 1 until n) {
            val temp = matrix[i][j]
            matrix[i][j] = matrix[j][i]
            matrix[j][i] = temp
        }
    }

    // Step 2: Reflect vertically (reverse rows)
    for (i in 0 until n) {
        matrix[i].reverse()
    }
}

// Example:
// [1,2,3]    transpose    [1,4,7]    reverse    [7,4,1]
// [4,5,6]  ---------->   [2,5,8]  --------->   [8,5,2]
// [7,8,9]                [3,6,9]               [9,6,3]
```

**Spiral Matrix Traversal:**
```kotlin
fun spiralOrder(matrix: Array<IntArray>): List<Int> {
    if (matrix.isEmpty()) return emptyList()

    val result = mutableListOf<Int>()
    var top = 0
    var bottom = matrix.size - 1
    var left = 0
    var right = matrix[0].size - 1

    while (top <= bottom && left <= right) {
        // Right
        for (i in left..right) {
            result.add(matrix[top][i])
        }
        top++

        // Down
        for (i in top..bottom) {
            result.add(matrix[i][right])
        }
        right--

        // Left (if rows remain)
        if (top <= bottom) {
            for (i in right downTo left) {
                result.add(matrix[bottom][i])
            }
            bottom--
        }

        // Up (if columns remain)
        if (left <= right) {
            for (i in bottom downTo top) {
                result.add(matrix[i][left])
            }
            left++
        }
    }

    return result
}
```

**Generate Spiral Matrix:**
```kotlin
fun generateMatrix(n: Int): Array<IntArray> {
    val matrix = Array(n) { IntArray(n) }
    var num = 1
    var top = 0
    var bottom = n - 1
    var left = 0
    var right = n - 1

    while (num <= n * n) {
        for (i in left..right) matrix[top][i] = num++
        top++

        for (i in top..bottom) matrix[i][right] = num++
        right--

        for (i in right downTo left) matrix[bottom][i] = num++
        bottom--

        for (i in bottom downTo top) matrix[i][left] = num++
        left++
    }

    return matrix
}
```

**Search in Sorted Matrix:**
```kotlin
// Matrix sorted by rows and columns
// Start from top-right corner
fun searchMatrix(matrix: Array<IntArray>, target: Int): Boolean {
    if (matrix.isEmpty()) return false

    val m = matrix.size
    val n = matrix[0].size

    var row = 0
    var col = n - 1

    while (row < m && col >= 0) {
        when {
            matrix[row][col] == target -> return true
            matrix[row][col] > target -> col--  // Go left
            else -> row++  // Go down
        }
    }

    return false
}

// Fully sorted matrix (each row starts after previous)
// Binary search as 1D array
fun searchMatrixSorted(matrix: Array<IntArray>, target: Int): Boolean {
    if (matrix.isEmpty()) return false

    val m = matrix.size
    val n = matrix[0].size
    var left = 0
    var right = m * n - 1

    while (left <= right) {
        val mid = left + (right - left) / 2
        val midVal = matrix[mid / n][mid % n]

        when {
            midVal == target -> return true
            midVal < target -> left = mid + 1
            else -> right = mid - 1
        }
    }

    return false
}
```

**Set Matrix Zeroes:**
```kotlin
fun setZeroes(matrix: Array<IntArray>) {
    val m = matrix.size
    val n = matrix[0].size
    var firstRowZero = false
    var firstColZero = false

    // Check first row and column
    for (j in 0 until n) if (matrix[0][j] == 0) firstRowZero = true
    for (i in 0 until m) if (matrix[i][0] == 0) firstColZero = true

    // Use first row/column as markers
    for (i in 1 until m) {
        for (j in 1 until n) {
            if (matrix[i][j] == 0) {
                matrix[i][0] = 0
                matrix[0][j] = 0
            }
        }
    }

    // Fill zeros by markers
    for (i in 1 until m) {
        for (j in 1 until n) {
            if (matrix[i][0] == 0 || matrix[0][j] == 0) {
                matrix[i][j] = 0
            }
        }
    }

    // Handle first row and column
    if (firstRowZero) for (j in 0 until n) matrix[0][j] = 0
    if (firstColZero) for (i in 0 until m) matrix[i][0] = 0
}
```

**Grid DP - Unique Paths:**
```kotlin
fun uniquePaths(m: Int, n: Int): Int {
    val dp = Array(m) { IntArray(n) { 1 } }

    for (i in 1 until m) {
        for (j in 1 until n) {
            dp[i][j] = dp[i - 1][j] + dp[i][j - 1]
        }
    }

    return dp[m - 1][n - 1]
}

// Memory optimization to O(n)
fun uniquePathsOptimized(m: Int, n: Int): Int {
    val dp = IntArray(n) { 1 }

    for (i in 1 until m) {
        for (j in 1 until n) {
            dp[j] += dp[j - 1]
        }
    }

    return dp[n - 1]
}
```

**Minimum Path Sum:**
```kotlin
fun minPathSum(grid: Array<IntArray>): Int {
    val m = grid.size
    val n = grid[0].size
    val dp = Array(m) { IntArray(n) }

    dp[0][0] = grid[0][0]

    // First row
    for (j in 1 until n) dp[0][j] = dp[0][j - 1] + grid[0][j]

    // First column
    for (i in 1 until m) dp[i][0] = dp[i - 1][0] + grid[i][0]

    // Rest of cells
    for (i in 1 until m) {
        for (j in 1 until n) {
            dp[i][j] = minOf(dp[i - 1][j], dp[i][j - 1]) + grid[i][j]
        }
    }

    return dp[m - 1][n - 1]
}
```

**Maximal Square:**
```kotlin
fun maximalSquare(matrix: Array<CharArray>): Int {
    if (matrix.isEmpty()) return 0

    val m = matrix.size
    val n = matrix[0].size
    val dp = Array(m + 1) { IntArray(n + 1) }
    var maxSide = 0

    for (i in 1..m) {
        for (j in 1..n) {
            if (matrix[i - 1][j - 1] == '1') {
                dp[i][j] = minOf(
                    dp[i - 1][j],
                    dp[i][j - 1],
                    dp[i - 1][j - 1]
                ) + 1
                maxSide = maxOf(maxSide, dp[i][j])
            }
        }
    }

    return maxSide * maxSide
}
```

---

## Follow-ups

- How do you count islands in a grid (DFS/BFS)?
- What is the time complexity of spiral traversal?
- How do you rotate a matrix by 180 degrees?

## Related Questions

### Prerequisites (Easier)
- [[q-data-structures-overview--algorithms--easy]] - Data structures
- [[q-prefix-sum-range-queries--algorithms--medium]] - 2D prefix sums

### Related (Same Level)
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]] - Grid as graph
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - DP

### Advanced (Harder)
- [[q-backtracking-algorithms--algorithms--hard]] - Backtracking on grid
- [[q-advanced-graph-algorithms--algorithms--hard]] - Advanced graphs
