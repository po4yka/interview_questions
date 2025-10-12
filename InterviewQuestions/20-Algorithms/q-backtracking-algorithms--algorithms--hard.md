---
id: 20251012-200008
title: "Backtracking Algorithms (N-Queens, Sudoku, Subsets) / Алгоритмы с откатом"
slug: backtracking-algorithms-algorithms-hard
topic: algorithms
subtopics:
  - backtracking
  - recursion
  - combinatorics
  - constraint-satisfaction
status: draft
difficulty: hard
moc: moc-algorithms
date_created: 2025-10-12
date_updated: 2025-10-12
related_questions:
  - q-dynamic-programming-fundamentals--algorithms--hard
  - q-graph-algorithms-bfs-dfs--algorithms--hard
  - q-binary-search-trees-bst--algorithms--hard
tags:
  - algorithms
  - backtracking
  - recursion
  - n-queens
  - sudoku
  - permutations
  - combinations
---

# Backtracking Algorithms

## English Version

### Problem Statement

Backtracking is a powerful algorithmic technique for solving constraint satisfaction problems. It builds solutions incrementally and abandons (backtracks) partial solutions that cannot lead to valid solutions. Essential for puzzles, combinatorics, and optimization problems.

**The Question:** What is backtracking? How do you solve N-Queens, Sudoku Solver, Permutations, Combinations, and Subset problems? When should you use backtracking?

### Detailed Answer

---

### BACKTRACKING FUNDAMENTALS

**Core Concept: Try → Check → Backtrack if invalid**

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

**Key characteristics:**
```
✅ Explores all possibilities systematically
✅ Prunes invalid branches early (optimization)
✅ Uses recursion naturally
✅ Often O(2^n) or O(n!) time complexity
✅ O(n) space for recursion stack
```

---

### N-QUEENS PROBLEM

**Place N queens on N×N chessboard so no two attack each other.**

```kotlin
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

// Example:
val solutions = solveNQueens(4)
println("Total solutions for 4-Queens: ${solutions.size}")  // 2

solutions.forEach { solution ->
    solution.forEach { println(it) }
    println()
}

// Output:
// .Q..
// ...Q
// Q...
// ..Q.
//
// ..Q.
// Q...
// ...Q
// .Q..

// Time: O(n!) - try n choices for row 1, n-1 for row 2, etc.
// Space: O(n) - recursion depth
```

**How N-Queens backtracks:**
```
4×4 Board:

Row 0: Try col 0
  Q... ✓

Row 1: Try col 0 → Invalid (same column)
       Try col 1 → Invalid (diagonal)
       Try col 2 ✓
  Q...
  ..Q.

Row 2: Try col 0 → Invalid
       Try col 1 → Invalid
       Try col 2 → Invalid (same column)
       Try col 3 → Invalid
       → BACKTRACK to row 1

Row 1: Try col 3 ✓
  Q...
  ...Q

Row 2: Try col 0 → Invalid
       Try col 1 ✓
  Q...
  ...Q
  .Q..

Row 3: Try col 0,1,2,3 → All invalid
       → BACKTRACK to row 2
       → BACKTRACK to row 1
       → BACKTRACK to row 0

Row 0: Try col 1 ✓
  .Q..
  (continue searching...)
```

---

#### N-Queens Optimized (Using Sets)

```kotlin
fun solveNQueensOptimized(n: Int): List<List<String>> {
    val result = mutableListOf<List<String>>()
    val board = Array(n) { CharArray(n) { '.' } }

    val cols = mutableSetOf<Int>()
    val diagonals = mutableSetOf<Int>()      // row - col
    val antiDiagonals = mutableSetOf<Int>()  // row + col

    fun backtrack(row: Int) {
        if (row == n) {
            result.add(board.map { String(it) })
            return
        }

        for (col in 0 until n) {
            val diag = row - col
            val antiDiag = row + col

            // Check if position is attacked
            if (col in cols || diag in diagonals || antiDiag in antiDiagonals) {
                continue
            }

            // Make choice
            board[row][col] = 'Q'
            cols.add(col)
            diagonals.add(diag)
            antiDiagonals.add(antiDiag)

            // Recurse
            backtrack(row + 1)

            // Backtrack
            board[row][col] = '.'
            cols.remove(col)
            diagonals.remove(diag)
            antiDiagonals.remove(antiDiag)
        }
    }

    backtrack(0)
    return result
}

// Time: O(n!) - same complexity, but faster constant factor
// Space: O(n)
```

---

### SUDOKU SOLVER

**Fill 9×9 grid with digits 1-9 following Sudoku rules.**

```kotlin
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

// Example:
val sudokuBoard = arrayOf(
    charArrayOf('5', '3', '.', '.', '7', '.', '.', '.', '.'),
    charArrayOf('6', '.', '.', '1', '9', '5', '.', '.', '.'),
    charArrayOf('.', '9', '8', '.', '.', '.', '.', '6', '.'),
    charArrayOf('8', '.', '.', '.', '6', '.', '.', '.', '3'),
    charArrayOf('4', '.', '.', '8', '.', '3', '.', '.', '1'),
    charArrayOf('7', '.', '.', '.', '2', '.', '.', '.', '6'),
    charArrayOf('.', '6', '.', '.', '.', '.', '2', '8', '.'),
    charArrayOf('.', '.', '.', '4', '1', '9', '.', '.', '5'),
    charArrayOf('.', '.', '.', '.', '8', '.', '.', '7', '9')
)

if (solveSudoku(sudokuBoard)) {
    sudokuBoard.forEach { println(it.joinToString(" ")) }
}

// Time: O(9^(n*n)) worst case, much better with pruning
// Space: O(n*n) for recursion stack
```

---

### PERMUTATIONS

**Generate all possible orderings of elements.**

```kotlin
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

// Example:
val nums = intArrayOf(1, 2, 3)
val perms = permute(nums)
println("Permutations: $perms")
// [[1,2,3], [1,3,2], [2,1,3], [2,3,1], [3,1,2], [3,2,1]]

// Time: O(n * n!) - n! permutations, O(n) to copy each
// Space: O(n) - recursion depth
```

**How permutations backtrack:**
```
nums = [1, 2, 3]

Level 0: Choose 1
  current = [1]
  used = [T, F, F]

  Level 1: Choose 2
    current = [1, 2]
    used = [T, T, F]

    Level 2: Choose 3
      current = [1, 2, 3] ✓ Add to result
      Backtrack to Level 1

  Level 1: Choose 3
    current = [1, 3]
    used = [T, F, T]

    Level 2: Choose 2
      current = [1, 3, 2] ✓ Add to result
      Backtrack to Level 0

Level 0: Choose 2
  current = [2]
  ...
```

---

#### Permutations with Duplicates

```kotlin
fun permuteUnique(nums: IntArray): List<List<Int>> {
    val result = mutableListOf<List<Int>>()
    val current = mutableListOf<Int>()
    val used = BooleanArray(nums.size)

    nums.sort()  // Sort to group duplicates

    fun backtrack() {
        if (current.size == nums.size) {
            result.add(current.toList())
            return
        }

        for (i in nums.indices) {
            if (used[i]) continue

            // Skip duplicates: if previous same number not used
            if (i > 0 && nums[i] == nums[i - 1] && !used[i - 1]) {
                continue
            }

            current.add(nums[i])
            used[i] = true

            backtrack()

            current.removeAt(current.size - 1)
            used[i] = false
        }
    }

    backtrack()
    return result
}

// Example:
val nums = intArrayOf(1, 1, 2)
val perms = permuteUnique(nums)
println(perms)  // [[1,1,2], [1,2,1], [2,1,1]]
```

---

### COMBINATIONS

**Generate all k-sized subsets.**

```kotlin
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

// Example:
val combos = combine(4, 2)
println("Combinations C(4,2): $combos")
// [[1,2], [1,3], [1,4], [2,3], [2,4], [3,4]]

// Time: O(C(n,k) * k) = O(n! / (k!(n-k)!) * k)
// Space: O(k) - recursion depth
```

---

#### Combination Sum (Elements Reusable)

```kotlin
fun combinationSum(candidates: IntArray, target: Int): List<List<Int>> {
    val result = mutableListOf<List<Int>>()
    val current = mutableListOf<Int>()

    candidates.sort()  // Optimization for early termination

    fun backtrack(start: Int, remaining: Int) {
        // Base cases
        if (remaining == 0) {
            result.add(current.toList())
            return
        }
        if (remaining < 0) return

        for (i in start until candidates.size) {
            val num = candidates[i]

            // Early termination
            if (num > remaining) break

            // Make choice
            current.add(num)

            // Recurse (can reuse same element)
            backtrack(i, remaining - num)

            // Backtrack
            current.removeAt(current.size - 1)
        }
    }

    backtrack(0, target)
    return result
}

// Example:
val candidates = intArrayOf(2, 3, 6, 7)
val target = 7
val combos = combinationSum(candidates, target)
println(combos)  // [[2,2,3], [7]]

// Time: O(n^(t/m)) where t=target, m=min candidate
// Space: O(t/m) - recursion depth
```

---

### SUBSETS (POWER SET)

**Generate all possible subsets of a set.**

```kotlin
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

// Example:
val nums = intArrayOf(1, 2, 3)
val subsets = subsets(nums)
println("Subsets: $subsets")
// [[], [1], [1,2], [1,2,3], [1,3], [2], [2,3], [3]]

// Time: O(2^n * n) - 2^n subsets, O(n) to copy each
// Space: O(n) - recursion depth
```

**Subset generation tree:**
```
                    []
                 /  |  \
              [1]  [2] [3]
             /  \    |
         [1,2] [1,3] [2,3]
          /
      [1,2,3]

At each level, decide: include element or not
```

---

#### Subsets with Duplicates

```kotlin
fun subsetsWithDup(nums: IntArray): List<List<Int>> {
    val result = mutableListOf<List<Int>>()
    val current = mutableListOf<Int>()

    nums.sort()  // Sort to group duplicates

    fun backtrack(start: Int) {
        result.add(current.toList())

        for (i in start until nums.size) {
            // Skip duplicates at same recursion level
            if (i > start && nums[i] == nums[i - 1]) continue

            current.add(nums[i])
            backtrack(i + 1)
            current.removeAt(current.size - 1)
        }
    }

    backtrack(0)
    return result
}

// Example:
val nums = intArrayOf(1, 2, 2)
val subsets = subsetsWithDup(nums)
println(subsets)  // [[], [1], [1,2], [1,2,2], [2], [2,2]]
```

---

### WORD SEARCH

**Find if word exists in 2D board (can move up/down/left/right).**

```kotlin
fun exist(board: Array<CharArray>, word: String): Boolean {
    val rows = board.size
    val cols = board[0].size

    fun backtrack(row: Int, col: Int, index: Int): Boolean {
        // Base case: word found
        if (index == word.length) return true

        // Out of bounds or mismatch
        if (row !in 0 until rows ||
            col !in 0 until cols ||
            board[row][col] != word[index]) {
            return false
        }

        // Mark as visited
        val temp = board[row][col]
        board[row][col] = '#'

        // Try all 4 directions
        val found = backtrack(row + 1, col, index + 1) ||
                    backtrack(row - 1, col, index + 1) ||
                    backtrack(row, col + 1, index + 1) ||
                    backtrack(row, col - 1, index + 1)

        // Backtrack (restore)
        board[row][col] = temp

        return found
    }

    // Try starting from each cell
    for (row in 0 until rows) {
        for (col in 0 until cols) {
            if (backtrack(row, col, 0)) {
                return true
            }
        }
    }

    return false
}

// Example:
val board = arrayOf(
    charArrayOf('A', 'B', 'C', 'E'),
    charArrayOf('S', 'F', 'C', 'S'),
    charArrayOf('A', 'D', 'E', 'E')
)

println(exist(board, "ABCCED"))  // true
println(exist(board, "SEE"))     // true
println(exist(board, "ABCB"))    // false

// Time: O(m*n * 4^L) where L = word length
// Space: O(L) - recursion depth
```

---

### GENERATE PARENTHESES

**Generate all valid combinations of n pairs of parentheses.**

```kotlin
fun generateParenthesis(n: Int): List<String> {
    val result = mutableListOf<String>()

    fun backtrack(current: StringBuilder, open: Int, close: Int) {
        // Base case: all parentheses used
        if (current.length == 2 * n) {
            result.add(current.toString())
            return
        }

        // Add opening parenthesis if available
        if (open < n) {
            current.append('(')
            backtrack(current, open + 1, close)
            current.deleteCharAt(current.length - 1)
        }

        // Add closing parenthesis if valid
        if (close < open) {
            current.append(')')
            backtrack(current, open, close + 1)
            current.deleteCharAt(current.length - 1)
        }
    }

    backtrack(StringBuilder(), 0, 0)
    return result
}

// Example:
val parens = generateParenthesis(3)
println(parens)
// ["((()))", "(()())", "(())()", "()(())", "()()()"]

// Time: O(4^n / √n) - Catalan number
// Space: O(n) - recursion depth
```

**Generation tree (n=2):**
```
                    ""
                    |
                   "("
                 /    \
              "(("    "()"
               |        |
             "(()"    "()("
               |        |
            "(())"   "()()"
```

---

### PALINDROME PARTITIONING

**Partition string into palindromic substrings.**

```kotlin
fun partition(s: String): List<List<String>> {
    val result = mutableListOf<List<String>>()
    val current = mutableListOf<String>()

    fun isPalindrome(str: String, start: Int, end: Int): Boolean {
        var left = start
        var right = end
        while (left < right) {
            if (str[left] != str[right]) return false
            left++
            right--
        }
        return true
    }

    fun backtrack(start: Int) {
        // Base case: reached end
        if (start == s.length) {
            result.add(current.toList())
            return
        }

        // Try all possible partitions
        for (end in start until s.length) {
            if (isPalindrome(s, start, end)) {
                // Make choice
                current.add(s.substring(start, end + 1))

                // Recurse
                backtrack(end + 1)

                // Backtrack
                current.removeAt(current.size - 1)
            }
        }
    }

    backtrack(0)
    return result
}

// Example:
val partitions = partition("aab")
println(partitions)  // [["a","a","b"], ["aa","b"]]

// Time: O(n * 2^n) - 2^n partitions, O(n) palindrome check
// Space: O(n) - recursion depth
```

---

### BACKTRACKING OPTIMIZATION TECHNIQUES

#### 1. Early Termination

```kotlin
fun combinationSumOptimized(candidates: IntArray, target: Int): List<List<Int>> {
    candidates.sort()  // Key optimization!
    val result = mutableListOf<List<Int>>()
    val current = mutableListOf<Int>()

    fun backtrack(start: Int, remaining: Int) {
        if (remaining == 0) {
            result.add(current.toList())
            return
        }

        for (i in start until candidates.size) {
            val num = candidates[i]

            // Early termination: no point checking larger numbers
            if (num > remaining) break  // ✅ Much faster than continue

            current.add(num)
            backtrack(i, remaining - num)
            current.removeAt(current.size - 1)
        }
    }

    backtrack(0, target)
    return result
}
```

---

#### 2. Memoization

```kotlin
fun wordBreak(s: String, wordDict: List<String>): List<String> {
    val wordSet = wordDict.toSet()
    val memo = mutableMapOf<Int, List<String>>()

    fun backtrack(start: Int): List<String> {
        // Check memo
        if (start in memo) return memo[start]!!

        if (start == s.length) return listOf("")

        val result = mutableListOf<String>()

        for (end in start + 1..s.length) {
            val word = s.substring(start, end)

            if (word in wordSet) {
                val suffixes = backtrack(end)
                for (suffix in suffixes) {
                    result.add(
                        if (suffix.isEmpty()) word
                        else "$word $suffix"
                    )
                }
            }
        }

        memo[start] = result
        return result
    }

    return backtrack(0)
}

// Example:
val s = "catsanddog"
val wordDict = listOf("cat", "cats", "and", "sand", "dog")
println(wordBreak(s, wordDict))
// ["cats and dog", "cat sand dog"]
```

---

#### 3. Pruning with Constraints

```kotlin
// Prune based on domain constraints
fun solveNQueensPruned(n: Int): Int {
    var count = 0
    val cols = mutableSetOf<Int>()
    val diags = mutableSetOf<Int>()
    val antiDiags = mutableSetOf<Int>()

    fun backtrack(row: Int) {
        if (row == n) {
            count++
            return
        }

        for (col in 0 until n) {
            val diag = row - col
            val antiDiag = row + col

            // Prune invalid branches immediately
            if (col in cols || diag in diags || antiDiag in antiDiags) {
                continue  // ✅ Skip entire subtree
            }

            cols.add(col)
            diags.add(diag)
            antiDiags.add(antiDiag)

            backtrack(row + 1)

            cols.remove(col)
            diags.remove(diag)
            antiDiags.remove(antiDiag)
        }
    }

    backtrack(0)
    return count
}
```

---

### Real-World Applications

#### Android: Form Validation with Constraints

```kotlin
// Validate form with interdependent constraints
data class FormField(val name: String, val value: String)

class FormValidator {
    private val constraints = mapOf<String, (Map<String, String>) -> Boolean>(
        "email" to { fields ->
            fields["email"]?.contains("@") == true
        },
        "password" to { fields ->
            fields["password"]?.let { it.length >= 8 } == true
        },
        "confirmPassword" to { fields ->
            fields["password"] == fields["confirmPassword"]
        },
        "age" to { fields ->
            fields["age"]?.toIntOrNull()?.let { it >= 18 } == true
        }
    )

    fun findValidConfiguration(
        fields: List<String>,
        possibleValues: Map<String, List<String>>
    ): Map<String, String>? {
        val current = mutableMapOf<String, String>()

        fun backtrack(index: Int): Boolean {
            if (index == fields.size) return true

            val field = fields[index]

            for (value in possibleValues[field] ?: emptyList()) {
                current[field] = value

                // Check if valid with current constraints
                val isValid = constraints[field]?.invoke(current) ?: true

                if (isValid && backtrack(index + 1)) {
                    return true
                }

                current.remove(field)
            }

            return false
        }

        return if (backtrack(0)) current.toMap() else null
    }
}
```

---

#### Scheduling with Conflicts

```kotlin
// Schedule meetings avoiding conflicts
data class Meeting(val id: Int, val duration: Int)
data class TimeSlot(val start: Int, val end: Int)

class MeetingScheduler {
    fun scheduleAll(
        meetings: List<Meeting>,
        availableSlots: List<TimeSlot>
    ): Map<Meeting, TimeSlot>? {
        val schedule = mutableMapOf<Meeting, TimeSlot>()

        fun backtrack(index: Int): Boolean {
            if (index == meetings.size) return true

            val meeting = meetings[index]

            for (slot in availableSlots) {
                if (canSchedule(meeting, slot, schedule)) {
                    schedule[meeting] = slot

                    if (backtrack(index + 1)) {
                        return true
                    }

                    schedule.remove(meeting)
                }
            }

            return false
        }

        return if (backtrack(0)) schedule else null
    }

    private fun canSchedule(
        meeting: Meeting,
        slot: TimeSlot,
        existing: Map<Meeting, TimeSlot>
    ): Boolean {
        // Check if meeting fits in slot
        if (slot.end - slot.start < meeting.duration) return false

        // Check for conflicts with existing schedule
        for ((_, existingSlot) in existing) {
            if (overlaps(slot, existingSlot)) return false
        }

        return true
    }

    private fun overlaps(slot1: TimeSlot, slot2: TimeSlot): Boolean {
        return slot1.start < slot2.end && slot2.start < slot1.end
    }
}
```

---

### Key Takeaways

1. **Backtracking** explores all possibilities systematically with early pruning
2. **Template:** Make choice → Recurse → Backtrack (undo choice)
3. **N-Queens:** Classic constraint satisfaction, O(n!) time
4. **Sudoku:** Constraint propagation + backtracking
5. **Permutations:** Generate all orderings, O(n! * n) time
6. **Combinations:** Choose k from n, O(C(n,k) * k) time
7. **Subsets:** Power set generation, O(2^n * n) time
8. **Optimizations:** Early termination, memoization, pruning
9. **Use backtracking** for constraint satisfaction, puzzles, combinatorics
10. **Space complexity** typically O(n) for recursion stack

---

## Russian Version

### Постановка задачи

Backtracking (алгоритм с откатом) - мощная техника для решения задач с ограничениями. Она строит решения постепенно и отказывается (откатывается) от частичных решений, которые не могут привести к валидным решениям. Необходима для головоломок, комбинаторики и оптимизационных задач.

**Вопрос:** Что такое backtracking? Как решать задачи N-Queens, Sudoku Solver, Permutations, Combinations и Subsets? Когда использовать backtracking?

### Ключевые выводы

1. **Backtracking** исследует все возможности систематически с ранним отсечением
2. **Шаблон:** Сделать выбор → Рекурсия → Откат (отменить выбор)
3. **N-Queens:** Классическая задача с ограничениями, O(n!) время
4. **Sudoku:** Распространение ограничений + backtracking
5. **Permutations:** Генерация всех перестановок, O(n! * n) время
6. **Combinations:** Выбрать k из n, O(C(n,k) * k) время
7. **Subsets:** Генерация множества подмножеств, O(2^n * n) время
8. **Оптимизации:** Ранняя остановка, мемоизация, отсечение
9. **Используйте backtracking** для задач с ограничениями, головоломок, комбинаторики
10. **Пространственная сложность** обычно O(n) для стека рекурсии

## Follow-ups

1. How does constraint propagation improve Sudoku solving?
2. What is the difference between backtracking and dynamic programming?
3. How do you implement iterative backtracking without recursion?
4. What is the relationship between backtracking and DFS?
5. How do you optimize N-Queens for large N (e.g., N=100)?
6. What is the Branch and Bound algorithm?
7. How do you implement backtracking with bit manipulation?
8. What is the Dancing Links algorithm for exact cover problems?
9. How do you parallelize backtracking algorithms?
10. What are the differences between backtracking, brute force, and exhaustive search?
