---
id: algo-010
title: Greedy Algorithms / Жадные алгоритмы
aliases:
- Greedy Algorithms
- Greedy Approach
- Жадные алгоритмы
- Жадный подход
topic: algorithms
subtopics:
- greedy
- optimization
- intervals
question_kind: coding
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-algorithms
related:
- c-greedy
- c-optimization
- q-dynamic-programming-fundamentals--algorithms--hard
created: 2026-01-23
updated: 2026-01-23
tags:
- algorithms
- greedy
- difficulty/medium
- optimization
- intervals
sources:
- https://en.wikipedia.org/wiki/Greedy_algorithm
anki_cards:
- slug: algo-010-0-en
  language: en
  anki_id: 1769168918219
  synced_at: '2026-01-23T15:48:41.075823'
- slug: algo-010-0-ru
  language: ru
  anki_id: 1769168918251
  synced_at: '2026-01-23T15:48:41.077594'
---
# Вопрос (RU)
> Что такое жадный алгоритм? Когда можно использовать жадный подход? Приведи примеры классических жадных задач.

# Question (EN)
> What is a greedy algorithm? When can you use a greedy approach? Give examples of classic greedy problems.

---

## Ответ (RU)

**Теория жадных алгоритмов:**
Жадный алгоритм на каждом шаге делает локально оптимальный выбор, надеясь получить глобальный оптимум. Он работает, когда задача обладает свойством жадного выбора и оптимальной подструктурой.

**Свойство жадного выбора:**
Глобальное оптимальное решение можно получить, делая локально оптимальные выборы на каждом шаге.

**Задача выбора активностей:**
```kotlin
// Выбор максимального числа непересекающихся активностей
data class Activity(val start: Int, val end: Int)

fun activitySelection(activities: List<Activity>): List<Activity> {
    // Сортировка по времени окончания
    val sorted = activities.sortedBy { it.end }
    val result = mutableListOf<Activity>()

    var lastEnd = Int.MIN_VALUE

    for (activity in sorted) {
        if (activity.start >= lastEnd) {
            result.add(activity)
            lastEnd = activity.end
        }
    }

    return result
}
```

**Задача о покрытии интервалов:**
```kotlin
// Минимальное число точек для покрытия всех интервалов
fun minArrowsToBurstBalloons(points: Array<IntArray>): Int {
    if (points.isEmpty()) return 0

    // Сортировка по правой границе
    points.sortBy { it[1] }

    var arrows = 1
    var arrowPos = points[0][1]

    for (i in 1 until points.size) {
        // Если интервал не покрыт текущей стрелой
        if (points[i][0] > arrowPos) {
            arrows++
            arrowPos = points[i][1]
        }
    }

    return arrows
}
```

**Jump Game - можно ли достичь конца:**
```kotlin
// Жадно отслеживаем максимальную достижимую позицию
fun canJump(nums: IntArray): Boolean {
    var maxReach = 0

    for (i in nums.indices) {
        // Если текущая позиция недостижима
        if (i > maxReach) return false

        // Обновляем максимальную достижимую позицию
        maxReach = maxOf(maxReach, i + nums[i])

        // Если можем достичь конца
        if (maxReach >= nums.size - 1) return true
    }

    return true
}
```

**Jump Game II - минимальное число прыжков:**
```kotlin
fun jump(nums: IntArray): Int {
    if (nums.size <= 1) return 0

    var jumps = 0
    var currentEnd = 0      // Конец текущего прыжка
    var farthest = 0        // Максимальная достижимая позиция

    for (i in 0 until nums.size - 1) {
        farthest = maxOf(farthest, i + nums[i])

        // Когда достигли конца текущего прыжка
        if (i == currentEnd) {
            jumps++
            currentEnd = farthest

            if (currentEnd >= nums.size - 1) break
        }
    }

    return jumps
}
```

**Задача о сдаче монет (при специальных номиналах):**
```kotlin
// Работает только для канонических систем монет (1, 5, 10, 25)
fun coinChangeGreedy(coins: IntArray, amount: Int): Int {
    val sortedCoins = coins.sortedDescending()
    var remaining = amount
    var count = 0

    for (coin in sortedCoins) {
        if (remaining >= coin) {
            count += remaining / coin
            remaining %= coin
        }
    }

    return if (remaining == 0) count else -1
}
```

**Когда жадность работает:**
- Задача выбора активностей
- Код Хаффмана
- Алгоритмы Краскала и Прима (MST)
- Задача о рюкзаке с дробными предметами

**Когда жадность НЕ работает:**
- 0/1 задача о рюкзаке
- Задача коммивояжера
- Задача о сдаче с произвольными монетами

## Answer (EN)

**Greedy Algorithms Theory:**
A greedy algorithm makes locally optimal choices at each step, hoping to reach a global optimum. It works when the problem has the greedy choice property and optimal substructure.

**Greedy Choice Property:**
A globally optimal solution can be achieved by making locally optimal choices at each step.

**Activity Selection Problem:**
```kotlin
// Select maximum number of non-overlapping activities
data class Activity(val start: Int, val end: Int)

fun activitySelection(activities: List<Activity>): List<Activity> {
    // Sort by end time
    val sorted = activities.sortedBy { it.end }
    val result = mutableListOf<Activity>()

    var lastEnd = Int.MIN_VALUE

    for (activity in sorted) {
        if (activity.start >= lastEnd) {
            result.add(activity)
            lastEnd = activity.end
        }
    }

    return result
}
```

**Interval Coverage Problem:**
```kotlin
// Minimum number of points to cover all intervals
fun minArrowsToBurstBalloons(points: Array<IntArray>): Int {
    if (points.isEmpty()) return 0

    // Sort by right boundary
    points.sortBy { it[1] }

    var arrows = 1
    var arrowPos = points[0][1]

    for (i in 1 until points.size) {
        // If interval not covered by current arrow
        if (points[i][0] > arrowPos) {
            arrows++
            arrowPos = points[i][1]
        }
    }

    return arrows
}
```

**Jump Game - can reach end:**
```kotlin
// Greedily track maximum reachable position
fun canJump(nums: IntArray): Boolean {
    var maxReach = 0

    for (i in nums.indices) {
        // If current position unreachable
        if (i > maxReach) return false

        // Update maximum reachable position
        maxReach = maxOf(maxReach, i + nums[i])

        // If can reach end
        if (maxReach >= nums.size - 1) return true
    }

    return true
}
```

**Jump Game II - minimum jumps:**
```kotlin
fun jump(nums: IntArray): Int {
    if (nums.size <= 1) return 0

    var jumps = 0
    var currentEnd = 0      // End of current jump
    var farthest = 0        // Maximum reachable position

    for (i in 0 until nums.size - 1) {
        farthest = maxOf(farthest, i + nums[i])

        // When reached end of current jump
        if (i == currentEnd) {
            jumps++
            currentEnd = farthest

            if (currentEnd >= nums.size - 1) break
        }
    }

    return jumps
}
```

**Coin Change Problem (for special denominations):**
```kotlin
// Only works for canonical coin systems (1, 5, 10, 25)
fun coinChangeGreedy(coins: IntArray, amount: Int): Int {
    val sortedCoins = coins.sortedDescending()
    var remaining = amount
    var count = 0

    for (coin in sortedCoins) {
        if (remaining >= coin) {
            count += remaining / coin
            remaining %= coin
        }
    }

    return if (remaining == 0) count else -1
}
```

**When Greedy Works:**
- Activity selection problem
- Huffman coding
- Kruskal's and Prim's algorithms (MST)
- Fractional knapsack problem

**When Greedy Does NOT Work:**
- 0/1 Knapsack problem
- Traveling salesman problem
- Coin change with arbitrary denominations

---

## Follow-ups

- How do you prove a greedy algorithm is correct?
- What is the difference between greedy and dynamic programming?
- How would you solve meeting rooms II (minimum rooms needed)?

## Related Questions

### Prerequisites (Easier)
- [[q-data-structures-overview--algorithms--easy]] - Data structures basics
- [[q-sorting-algorithms-comparison--algorithms--medium]] - Sorting algorithms

### Related (Same Level)
- [[q-interval-problems--algorithms--medium]] - Interval problems
- [[q-two-pointers-sliding-window--algorithms--medium]] - Array techniques

### Advanced (Harder)
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - Dynamic programming
- [[q-advanced-graph-algorithms--algorithms--hard]] - Graph algorithms (MST)
