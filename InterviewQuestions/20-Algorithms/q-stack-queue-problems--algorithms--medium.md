---
id: algo-016
title: Stack and Queue Problems / Задачи на стек и очередь
aliases:
- Stack Problems
- Queue Problems
- Monotonic Stack
- Задачи на стек
- Задачи на очередь
- Монотонный стек
topic: algorithms
subtopics:
- stack
- queue
- monotonic-stack
question_kind: coding
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-algorithms
related:
- c-stack
- c-queue
- q-data-structures-overview--algorithms--easy
created: 2026-01-23
updated: 2026-01-23
tags:
- algorithms
- stack
- difficulty/medium
- queue
- monotonic-stack
sources:
- https://en.wikipedia.org/wiki/Stack_(abstract_data_type)
- https://en.wikipedia.org/wiki/Monotone_priority_queue
anki_cards:
- slug: algo-016-0-en
  language: en
  anki_id: 1769168919194
  synced_at: '2026-01-26T09:10:14.484530'
- slug: algo-016-0-ru
  language: ru
  anki_id: 1769168919221
  synced_at: '2026-01-26T09:10:14.486169'
---
# Вопрос (RU)
> Объясни типичные задачи на стек: валидация скобок, монотонный стек, Min Stack. Как реализовать очередь с помощью стеков?

# Question (EN)
> Explain typical stack problems: parentheses validation, monotonic stack, Min Stack. How do you implement a queue using stacks?

---

## Ответ (RU)

**Теория стека и очереди:**
Стек (LIFO) - последний вошёл, первый вышел. Очередь (FIFO) - первый вошёл, первый вышел. Стек идеален для задач с вложенностью, отменой операций и обратным порядком.

**Валидация скобок:**
```kotlin
fun isValid(s: String): Boolean {
    val stack = ArrayDeque<Char>()
    val pairs = mapOf(')' to '(', '}' to '{', ']' to '[')

    for (c in s) {
        if (c in "({[") {
            stack.push(c)
        } else {
            // Закрывающая скобка
            if (stack.isEmpty() || stack.pop() != pairs[c]) {
                return false
            }
        }
    }

    return stack.isEmpty()
}
```

**Монотонный стек - Next Greater Element:**
```kotlin
// Для каждого элемента найти ближайший больший справа
fun nextGreaterElement(nums: IntArray): IntArray {
    val n = nums.size
    val result = IntArray(n) { -1 }
    val stack = ArrayDeque<Int>()  // Хранит индексы

    for (i in nums.indices) {
        // Пока текущий элемент больше вершины стека
        while (stack.isNotEmpty() && nums[i] > nums[stack.peek()]) {
            val idx = stack.pop()
            result[idx] = nums[i]
        }
        stack.push(i)
    }

    return result
}

// Пример: [2, 1, 2, 4, 3]
// i=0: stack=[0]
// i=1: 1 <= 2, stack=[0, 1]
// i=2: 2 > 1, result[1]=2, 2 == 2, stack=[0, 2]
// i=3: 4 > 2, result[2]=4, 4 > 2, result[0]=4, stack=[3]
// i=4: 3 < 4, stack=[3, 4]
// Результат: [4, 2, 4, -1, -1]
```

**Daily Temperatures (аналогичный паттерн):**
```kotlin
fun dailyTemperatures(temperatures: IntArray): IntArray {
    val n = temperatures.size
    val result = IntArray(n)
    val stack = ArrayDeque<Int>()

    for (i in temperatures.indices) {
        while (stack.isNotEmpty() &&
               temperatures[i] > temperatures[stack.peek()]) {
            val idx = stack.pop()
            result[idx] = i - idx  // Дни до более тёплого
        }
        stack.push(i)
    }

    return result
}
```

**Largest Rectangle in Histogram:**
```kotlin
fun largestRectangleArea(heights: IntArray): Int {
    val stack = ArrayDeque<Int>()
    var maxArea = 0
    var i = 0

    while (i <= heights.size) {
        val h = if (i == heights.size) 0 else heights[i]

        while (stack.isNotEmpty() && h < heights[stack.peek()]) {
            val height = heights[stack.pop()]
            val width = if (stack.isEmpty()) i else i - stack.peek() - 1
            maxArea = maxOf(maxArea, height * width)
        }

        stack.push(i)
        i++
    }

    return maxArea
}
```

**Min Stack:**
```kotlin
class MinStack {
    private val stack = ArrayDeque<Int>()
    private val minStack = ArrayDeque<Int>()

    fun push(x: Int) {
        stack.push(x)
        // Добавляем в minStack если новый минимум или равен текущему
        if (minStack.isEmpty() || x <= minStack.peek()) {
            minStack.push(x)
        }
    }

    fun pop() {
        val removed = stack.pop()
        if (removed == minStack.peek()) {
            minStack.pop()
        }
    }

    fun top(): Int = stack.peek()

    fun getMin(): Int = minStack.peek()
}
```

**Очередь с помощью двух стеков:**
```kotlin
class MyQueue {
    private val stackIn = ArrayDeque<Int>()
    private val stackOut = ArrayDeque<Int>()

    fun push(x: Int) {
        stackIn.push(x)
    }

    fun pop(): Int {
        peek()  // Гарантирует, что stackOut не пуст
        return stackOut.pop()
    }

    fun peek(): Int {
        if (stackOut.isEmpty()) {
            // Переливаем из stackIn в stackOut
            while (stackIn.isNotEmpty()) {
                stackOut.push(stackIn.pop())
            }
        }
        return stackOut.peek()
    }

    fun empty(): Boolean = stackIn.isEmpty() && stackOut.isEmpty()
}

// Амортизированная сложность O(1) для всех операций
```

**Стек с помощью двух очередей:**
```kotlin
class MyStack {
    private val queue = ArrayDeque<Int>()

    fun push(x: Int) {
        queue.add(x)
        // Переворачиваем очередь
        repeat(queue.size - 1) {
            queue.add(queue.removeFirst())
        }
    }

    fun pop(): Int = queue.removeFirst()

    fun top(): Int = queue.first()

    fun empty(): Boolean = queue.isEmpty()
}
```

**Evaluate Reverse Polish Notation:**
```kotlin
fun evalRPN(tokens: Array<String>): Int {
    val stack = ArrayDeque<Int>()

    for (token in tokens) {
        when (token) {
            "+", "-", "*", "/" -> {
                val b = stack.pop()
                val a = stack.pop()
                val result = when (token) {
                    "+" -> a + b
                    "-" -> a - b
                    "*" -> a * b
                    "/" -> a / b
                    else -> 0
                }
                stack.push(result)
            }
            else -> stack.push(token.toInt())
        }
    }

    return stack.pop()
}
```

**Simplify Path:**
```kotlin
fun simplifyPath(path: String): String {
    val stack = ArrayDeque<String>()

    for (part in path.split("/")) {
        when (part) {
            "", "." -> continue  // Пропускаем
            ".." -> if (stack.isNotEmpty()) stack.pop()
            else -> stack.push(part)
        }
    }

    return "/" + stack.reversed().joinToString("/")
}
```

## Answer (EN)

**Stack and Queue Theory:**
Stack (LIFO) - last in, first out. Queue (FIFO) - first in, first out. Stack is ideal for nesting problems, undo operations, and reverse order.

**Parentheses Validation:**
```kotlin
fun isValid(s: String): Boolean {
    val stack = ArrayDeque<Char>()
    val pairs = mapOf(')' to '(', '}' to '{', ']' to '[')

    for (c in s) {
        if (c in "({[") {
            stack.push(c)
        } else {
            // Closing bracket
            if (stack.isEmpty() || stack.pop() != pairs[c]) {
                return false
            }
        }
    }

    return stack.isEmpty()
}
```

**Monotonic Stack - Next Greater Element:**
```kotlin
// For each element find nearest greater to the right
fun nextGreaterElement(nums: IntArray): IntArray {
    val n = nums.size
    val result = IntArray(n) { -1 }
    val stack = ArrayDeque<Int>()  // Stores indices

    for (i in nums.indices) {
        // While current element is greater than stack top
        while (stack.isNotEmpty() && nums[i] > nums[stack.peek()]) {
            val idx = stack.pop()
            result[idx] = nums[i]
        }
        stack.push(i)
    }

    return result
}

// Example: [2, 1, 2, 4, 3]
// i=0: stack=[0]
// i=1: 1 <= 2, stack=[0, 1]
// i=2: 2 > 1, result[1]=2, 2 == 2, stack=[0, 2]
// i=3: 4 > 2, result[2]=4, 4 > 2, result[0]=4, stack=[3]
// i=4: 3 < 4, stack=[3, 4]
// Result: [4, 2, 4, -1, -1]
```

**Daily Temperatures (similar pattern):**
```kotlin
fun dailyTemperatures(temperatures: IntArray): IntArray {
    val n = temperatures.size
    val result = IntArray(n)
    val stack = ArrayDeque<Int>()

    for (i in temperatures.indices) {
        while (stack.isNotEmpty() &&
               temperatures[i] > temperatures[stack.peek()]) {
            val idx = stack.pop()
            result[idx] = i - idx  // Days until warmer
        }
        stack.push(i)
    }

    return result
}
```

**Largest Rectangle in Histogram:**
```kotlin
fun largestRectangleArea(heights: IntArray): Int {
    val stack = ArrayDeque<Int>()
    var maxArea = 0
    var i = 0

    while (i <= heights.size) {
        val h = if (i == heights.size) 0 else heights[i]

        while (stack.isNotEmpty() && h < heights[stack.peek()]) {
            val height = heights[stack.pop()]
            val width = if (stack.isEmpty()) i else i - stack.peek() - 1
            maxArea = maxOf(maxArea, height * width)
        }

        stack.push(i)
        i++
    }

    return maxArea
}
```

**Min Stack:**
```kotlin
class MinStack {
    private val stack = ArrayDeque<Int>()
    private val minStack = ArrayDeque<Int>()

    fun push(x: Int) {
        stack.push(x)
        // Add to minStack if new minimum or equal to current
        if (minStack.isEmpty() || x <= minStack.peek()) {
            minStack.push(x)
        }
    }

    fun pop() {
        val removed = stack.pop()
        if (removed == minStack.peek()) {
            minStack.pop()
        }
    }

    fun top(): Int = stack.peek()

    fun getMin(): Int = minStack.peek()
}
```

**Queue Using Two Stacks:**
```kotlin
class MyQueue {
    private val stackIn = ArrayDeque<Int>()
    private val stackOut = ArrayDeque<Int>()

    fun push(x: Int) {
        stackIn.push(x)
    }

    fun pop(): Int {
        peek()  // Ensures stackOut is not empty
        return stackOut.pop()
    }

    fun peek(): Int {
        if (stackOut.isEmpty()) {
            // Transfer from stackIn to stackOut
            while (stackIn.isNotEmpty()) {
                stackOut.push(stackIn.pop())
            }
        }
        return stackOut.peek()
    }

    fun empty(): Boolean = stackIn.isEmpty() && stackOut.isEmpty()
}

// Amortized O(1) for all operations
```

**Stack Using Two Queues:**
```kotlin
class MyStack {
    private val queue = ArrayDeque<Int>()

    fun push(x: Int) {
        queue.add(x)
        // Rotate queue
        repeat(queue.size - 1) {
            queue.add(queue.removeFirst())
        }
    }

    fun pop(): Int = queue.removeFirst()

    fun top(): Int = queue.first()

    fun empty(): Boolean = queue.isEmpty()
}
```

**Evaluate Reverse Polish Notation:**
```kotlin
fun evalRPN(tokens: Array<String>): Int {
    val stack = ArrayDeque<Int>()

    for (token in tokens) {
        when (token) {
            "+", "-", "*", "/" -> {
                val b = stack.pop()
                val a = stack.pop()
                val result = when (token) {
                    "+" -> a + b
                    "-" -> a - b
                    "*" -> a * b
                    "/" -> a / b
                    else -> 0
                }
                stack.push(result)
            }
            else -> stack.push(token.toInt())
        }
    }

    return stack.pop()
}
```

**Simplify Path:**
```kotlin
fun simplifyPath(path: String): String {
    val stack = ArrayDeque<String>()

    for (part in path.split("/")) {
        when (part) {
            "", "." -> continue  // Skip
            ".." -> if (stack.isNotEmpty()) stack.pop()
            else -> stack.push(part)
        }
    }

    return "/" + stack.reversed().joinToString("/")
}
```

---

## Follow-ups

- How would you implement a stack that supports getMax() in O(1)?
- What is the time complexity of monotonic stack algorithms?
- How do you use a stack for DFS vs a queue for BFS?

## Related Questions

### Prerequisites (Easier)
- [[q-data-structures-overview--algorithms--easy]] - Data structures basics
- [[q-hash-table-applications--algorithms--easy]] - Hash tables

### Related (Same Level)
- [[q-linked-list-algorithms--algorithms--medium]] - Linked lists
- [[q-tree-problems-traversals--algorithms--medium]] - Tree traversals

### Advanced (Harder)
- [[q-graph-algorithms-bfs-dfs--algorithms--hard]] - Graph traversals
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - DP problems
