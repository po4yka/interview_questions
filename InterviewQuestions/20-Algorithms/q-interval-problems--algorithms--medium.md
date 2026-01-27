---
id: algo-022
title: Interval Problems / Задачи на интервалы
aliases:
- Interval Problems
- Merge Intervals
- Meeting Rooms
- Задачи на интервалы
- Слияние интервалов
topic: algorithms
subtopics:
- intervals
- merge
- scheduling
question_kind: coding
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-algorithms
related:
- c-intervals
- c-scheduling
- q-greedy-algorithms--algorithms--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- algorithms
- intervals
- difficulty/medium
- merge
- scheduling
sources:
- https://en.wikipedia.org/wiki/Interval_(mathematics)
anki_cards:
- slug: algo-022-0-en
  language: en
  anki_id: 1769168919922
  synced_at: '2026-01-26T09:10:14.510801'
- slug: algo-022-0-ru
  language: ru
  anki_id: 1769168919949
  synced_at: '2026-01-26T09:10:14.512584'
---
# Вопрос (RU)
> Какие типичные задачи решаются на интервалах? Объясни слияние интервалов, вставку интервала и задачу Meeting Rooms.

# Question (EN)
> What typical problems are solved with intervals? Explain merge intervals, insert interval, and Meeting Rooms problem.

---

## Ответ (RU)

**Теория работы с интервалами:**
Интервальные задачи обычно требуют сортировки по началу или концу интервала. Ключ - определить перекрытия: два интервала [a,b] и [c,d] пересекаются, если a <= d и c <= b.

**Merge Intervals:**
```kotlin
fun merge(intervals: Array<IntArray>): Array<IntArray> {
    if (intervals.isEmpty()) return arrayOf()

    // Сортировка по началу интервала
    intervals.sortBy { it[0] }

    val result = mutableListOf<IntArray>()
    var current = intervals[0]

    for (i in 1 until intervals.size) {
        val next = intervals[i]

        if (current[1] >= next[0]) {
            // Перекрытие - объединяем
            current[1] = maxOf(current[1], next[1])
        } else {
            // Нет перекрытия - добавляем текущий
            result.add(current)
            current = next
        }
    }

    result.add(current)
    return result.toTypedArray()
}

// Пример: [[1,3],[2,6],[8,10],[15,18]]
// Сортировка: [[1,3],[2,6],[8,10],[15,18]]
// [1,3] + [2,6] -> [1,6] (перекрытие)
// [1,6] + [8,10] -> добавляем [1,6], current=[8,10]
// [8,10] + [15,18] -> добавляем [8,10], current=[15,18]
// Результат: [[1,6],[8,10],[15,18]]
```

**Insert Interval:**
```kotlin
fun insert(intervals: Array<IntArray>, newInterval: IntArray): Array<IntArray> {
    val result = mutableListOf<IntArray>()
    var i = 0
    val n = intervals.size

    // Добавляем все интервалы, которые заканчиваются до нового
    while (i < n && intervals[i][1] < newInterval[0]) {
        result.add(intervals[i])
        i++
    }

    // Объединяем перекрывающиеся интервалы
    var merged = newInterval
    while (i < n && intervals[i][0] <= merged[1]) {
        merged = intArrayOf(
            minOf(merged[0], intervals[i][0]),
            maxOf(merged[1], intervals[i][1])
        )
        i++
    }
    result.add(merged)

    // Добавляем оставшиеся интервалы
    while (i < n) {
        result.add(intervals[i])
        i++
    }

    return result.toTypedArray()
}
```

**Meeting Rooms I - можно ли посетить все встречи:**
```kotlin
fun canAttendMeetings(intervals: Array<IntArray>): Boolean {
    // Сортировка по началу
    intervals.sortBy { it[0] }

    for (i in 1 until intervals.size) {
        // Если начало следующей раньше конца предыдущей
        if (intervals[i][0] < intervals[i - 1][1]) {
            return false
        }
    }

    return true
}
```

**Meeting Rooms II - минимум комнат:**
```kotlin
fun minMeetingRooms(intervals: Array<IntArray>): Int {
    if (intervals.isEmpty()) return 0

    // Разделяем начала и концы
    val starts = intervals.map { it[0] }.sorted()
    val ends = intervals.map { it[1] }.sorted()

    var rooms = 0
    var maxRooms = 0
    var s = 0
    var e = 0

    while (s < intervals.size) {
        if (starts[s] < ends[e]) {
            // Новая встреча начинается до окончания предыдущей
            rooms++
            s++
        } else {
            // Встреча закончилась
            rooms--
            e++
        }
        maxRooms = maxOf(maxRooms, rooms)
    }

    return maxRooms
}

// Альтернатива с PriorityQueue
fun minMeetingRoomsHeap(intervals: Array<IntArray>): Int {
    if (intervals.isEmpty()) return 0

    intervals.sortBy { it[0] }

    // Min-heap по времени окончания
    val heap = java.util.PriorityQueue<Int>()

    for (interval in intervals) {
        // Если комната освободилась
        if (heap.isNotEmpty() && heap.peek() <= interval[0]) {
            heap.poll()
        }

        heap.offer(interval[1])
    }

    return heap.size
}
```

**Interval List Intersections:**
```kotlin
fun intervalIntersection(
    firstList: Array<IntArray>,
    secondList: Array<IntArray>
): Array<IntArray> {
    val result = mutableListOf<IntArray>()
    var i = 0
    var j = 0

    while (i < firstList.size && j < secondList.size) {
        val a = firstList[i]
        val b = secondList[j]

        // Находим пересечение
        val start = maxOf(a[0], b[0])
        val end = minOf(a[1], b[1])

        if (start <= end) {
            result.add(intArrayOf(start, end))
        }

        // Двигаем указатель с меньшим концом
        if (a[1] < b[1]) i++ else j++
    }

    return result.toTypedArray()
}
```

**Non-overlapping Intervals - минимум удалений:**
```kotlin
fun eraseOverlapIntervals(intervals: Array<IntArray>): Int {
    if (intervals.isEmpty()) return 0

    // Сортировка по концу интервала (жадный подход)
    intervals.sortBy { it[1] }

    var count = 0
    var prevEnd = Int.MIN_VALUE

    for (interval in intervals) {
        if (interval[0] >= prevEnd) {
            // Нет перекрытия
            prevEnd = interval[1]
        } else {
            // Перекрытие - удаляем текущий
            count++
        }
    }

    return count
}
```

**Minimum Number of Arrows to Burst Balloons:**
```kotlin
fun findMinArrowShots(points: Array<IntArray>): Int {
    if (points.isEmpty()) return 0

    // Сортировка по концу интервала
    points.sortBy { it[1] }

    var arrows = 1
    var arrowPos = points[0][1]

    for (i in 1 until points.size) {
        // Если шарик не пробит текущей стрелой
        if (points[i][0] > arrowPos) {
            arrows++
            arrowPos = points[i][1]
        }
    }

    return arrows
}
```

**Remove Covered Intervals:**
```kotlin
fun removeCoveredIntervals(intervals: Array<IntArray>): Int {
    // Сортировка: по началу (возр.), при равенстве по концу (убыв.)
    intervals.sortWith(compareBy({ it[0] }, { -it[1] }))

    var count = 0
    var maxEnd = 0

    for (interval in intervals) {
        if (interval[1] > maxEnd) {
            count++
            maxEnd = interval[1]
        }
        // Иначе интервал покрыт предыдущим
    }

    return count
}
```

**Паттерны сортировки интервалов:**
| Задача | Сортировка |
|--------|------------|
| Merge intervals | По началу |
| Activity selection | По концу |
| Non-overlapping | По концу |
| Meeting rooms | Раздельно начала/концы |

## Answer (EN)

**Interval Theory:**
Interval problems usually require sorting by start or end. Key is determining overlaps: two intervals [a,b] and [c,d] overlap if a <= d and c <= b.

**Merge Intervals:**
```kotlin
fun merge(intervals: Array<IntArray>): Array<IntArray> {
    if (intervals.isEmpty()) return arrayOf()

    // Sort by start
    intervals.sortBy { it[0] }

    val result = mutableListOf<IntArray>()
    var current = intervals[0]

    for (i in 1 until intervals.size) {
        val next = intervals[i]

        if (current[1] >= next[0]) {
            // Overlap - merge
            current[1] = maxOf(current[1], next[1])
        } else {
            // No overlap - add current
            result.add(current)
            current = next
        }
    }

    result.add(current)
    return result.toTypedArray()
}

// Example: [[1,3],[2,6],[8,10],[15,18]]
// Sorted: [[1,3],[2,6],[8,10],[15,18]]
// [1,3] + [2,6] -> [1,6] (overlap)
// [1,6] + [8,10] -> add [1,6], current=[8,10]
// [8,10] + [15,18] -> add [8,10], current=[15,18]
// Result: [[1,6],[8,10],[15,18]]
```

**Insert Interval:**
```kotlin
fun insert(intervals: Array<IntArray>, newInterval: IntArray): Array<IntArray> {
    val result = mutableListOf<IntArray>()
    var i = 0
    val n = intervals.size

    // Add all intervals ending before new one
    while (i < n && intervals[i][1] < newInterval[0]) {
        result.add(intervals[i])
        i++
    }

    // Merge overlapping intervals
    var merged = newInterval
    while (i < n && intervals[i][0] <= merged[1]) {
        merged = intArrayOf(
            minOf(merged[0], intervals[i][0]),
            maxOf(merged[1], intervals[i][1])
        )
        i++
    }
    result.add(merged)

    // Add remaining intervals
    while (i < n) {
        result.add(intervals[i])
        i++
    }

    return result.toTypedArray()
}
```

**Meeting Rooms I - can attend all meetings:**
```kotlin
fun canAttendMeetings(intervals: Array<IntArray>): Boolean {
    // Sort by start
    intervals.sortBy { it[0] }

    for (i in 1 until intervals.size) {
        // If next starts before previous ends
        if (intervals[i][0] < intervals[i - 1][1]) {
            return false
        }
    }

    return true
}
```

**Meeting Rooms II - minimum rooms:**
```kotlin
fun minMeetingRooms(intervals: Array<IntArray>): Int {
    if (intervals.isEmpty()) return 0

    // Separate starts and ends
    val starts = intervals.map { it[0] }.sorted()
    val ends = intervals.map { it[1] }.sorted()

    var rooms = 0
    var maxRooms = 0
    var s = 0
    var e = 0

    while (s < intervals.size) {
        if (starts[s] < ends[e]) {
            // New meeting starts before previous ends
            rooms++
            s++
        } else {
            // Meeting ended
            rooms--
            e++
        }
        maxRooms = maxOf(maxRooms, rooms)
    }

    return maxRooms
}

// Alternative with PriorityQueue
fun minMeetingRoomsHeap(intervals: Array<IntArray>): Int {
    if (intervals.isEmpty()) return 0

    intervals.sortBy { it[0] }

    // Min-heap by end time
    val heap = java.util.PriorityQueue<Int>()

    for (interval in intervals) {
        // If a room is free
        if (heap.isNotEmpty() && heap.peek() <= interval[0]) {
            heap.poll()
        }

        heap.offer(interval[1])
    }

    return heap.size
}
```

**Interval List Intersections:**
```kotlin
fun intervalIntersection(
    firstList: Array<IntArray>,
    secondList: Array<IntArray>
): Array<IntArray> {
    val result = mutableListOf<IntArray>()
    var i = 0
    var j = 0

    while (i < firstList.size && j < secondList.size) {
        val a = firstList[i]
        val b = secondList[j]

        // Find intersection
        val start = maxOf(a[0], b[0])
        val end = minOf(a[1], b[1])

        if (start <= end) {
            result.add(intArrayOf(start, end))
        }

        // Move pointer with smaller end
        if (a[1] < b[1]) i++ else j++
    }

    return result.toTypedArray()
}
```

**Non-overlapping Intervals - minimum removals:**
```kotlin
fun eraseOverlapIntervals(intervals: Array<IntArray>): Int {
    if (intervals.isEmpty()) return 0

    // Sort by end (greedy approach)
    intervals.sortBy { it[1] }

    var count = 0
    var prevEnd = Int.MIN_VALUE

    for (interval in intervals) {
        if (interval[0] >= prevEnd) {
            // No overlap
            prevEnd = interval[1]
        } else {
            // Overlap - remove current
            count++
        }
    }

    return count
}
```

**Minimum Number of Arrows to Burst Balloons:**
```kotlin
fun findMinArrowShots(points: Array<IntArray>): Int {
    if (points.isEmpty()) return 0

    // Sort by end
    points.sortBy { it[1] }

    var arrows = 1
    var arrowPos = points[0][1]

    for (i in 1 until points.size) {
        // If balloon not burst by current arrow
        if (points[i][0] > arrowPos) {
            arrows++
            arrowPos = points[i][1]
        }
    }

    return arrows
}
```

**Remove Covered Intervals:**
```kotlin
fun removeCoveredIntervals(intervals: Array<IntArray>): Int {
    // Sort: by start (asc), on tie by end (desc)
    intervals.sortWith(compareBy({ it[0] }, { -it[1] }))

    var count = 0
    var maxEnd = 0

    for (interval in intervals) {
        if (interval[1] > maxEnd) {
            count++
            maxEnd = interval[1]
        }
        // Otherwise interval is covered by previous
    }

    return count
}
```

**Interval Sorting Patterns:**
| Problem | Sorting |
|---------|---------|
| Merge intervals | By start |
| Activity selection | By end |
| Non-overlapping | By end |
| Meeting rooms | Separate starts/ends |

---

## Follow-ups

- How do you find the maximum number of overlapping intervals at any point?
- What is an Interval Tree and when would you use it?
- How do you handle open vs closed intervals?

## Related Questions

### Prerequisites (Easier)
- [[q-sorting-algorithms-comparison--algorithms--medium]] - Sorting
- [[q-hash-table-applications--algorithms--easy]] - Hash tables

### Related (Same Level)
- [[q-greedy-algorithms--algorithms--medium]] - Greedy approach
- [[q-heap-priority-queue--algorithms--medium]] - Priority queue

### Advanced (Harder)
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - DP
- [[q-advanced-graph-algorithms--algorithms--hard]] - Graph algorithms
