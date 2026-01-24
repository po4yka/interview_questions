---
id: algo-015
title: Linked List Algorithms / Алгоритмы связных списков
aliases:
- Linked List
- List Reversal
- Floyd's Algorithm
- Связный список
- Реверс списка
- Алгоритм Флойда
topic: algorithms
subtopics:
- linked-list
- reversal
- cycle-detection
question_kind: coding
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-algorithms
related:
- c-linked-list
- c-two-pointers
- q-two-pointers-sliding-window--algorithms--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- algorithms
- linked-list
- difficulty/medium
- cycle-detection
- reversal
sources:
- https://en.wikipedia.org/wiki/Linked_list
- https://en.wikipedia.org/wiki/Cycle_detection
anki_cards:
- slug: algo-015-0-en
  language: en
  anki_id: 1769168920844
  synced_at: '2026-01-23T15:48:41.179186'
- slug: algo-015-0-ru
  language: ru
  anki_id: 1769168920869
  synced_at: '2026-01-23T15:48:41.180485'
---
# Вопрос (RU)
> Объясни основные алгоритмы работы со связными списками: реверс, обнаружение цикла (алгоритм Флойда), нахождение середины и слияние списков.

# Question (EN)
> Explain basic linked list algorithms: reversal, cycle detection (Floyd's algorithm), finding middle, and merging lists.

---

## Ответ (RU)

**Определение узла списка:**
```kotlin
class ListNode(var `val`: Int) {
    var next: ListNode? = null
}
```

**Реверс связного списка (итеративно):**
```kotlin
fun reverseList(head: ListNode?): ListNode? {
    var prev: ListNode? = null
    var curr = head

    while (curr != null) {
        val next = curr.next  // Сохраняем следующий
        curr.next = prev      // Разворачиваем указатель
        prev = curr           // Сдвигаем prev
        curr = next           // Сдвигаем curr
    }

    return prev  // Новая голова
}

// Пример: 1 -> 2 -> 3 -> null
// prev=null, curr=1: next=2, 1.next=null, prev=1, curr=2
// prev=1, curr=2: next=3, 2.next=1, prev=2, curr=3
// prev=2, curr=3: next=null, 3.next=2, prev=3, curr=null
// Результат: 3 -> 2 -> 1 -> null
```

**Реверс связного списка (рекурсивно):**
```kotlin
fun reverseListRecursive(head: ListNode?): ListNode? {
    // Базовый случай
    if (head?.next == null) return head

    // Рекурсивно разворачиваем остаток
    val newHead = reverseListRecursive(head.next)

    // Разворачиваем связь текущего узла
    head.next?.next = head
    head.next = null

    return newHead
}
```

**Обнаружение цикла (Алгоритм Флойда - черепаха и заяц):**
```kotlin
fun hasCycle(head: ListNode?): Boolean {
    var slow = head
    var fast = head

    while (fast?.next != null) {
        slow = slow?.next          // Шаг 1
        fast = fast.next?.next     // Шаг 2

        if (slow == fast) return true
    }

    return false
}
```

**Найти начало цикла:**
```kotlin
fun detectCycle(head: ListNode?): ListNode? {
    var slow = head
    var fast = head

    // Шаг 1: Найти точку встречи
    while (fast?.next != null) {
        slow = slow?.next
        fast = fast.next?.next

        if (slow == fast) break
    }

    // Нет цикла
    if (fast?.next == null) return null

    // Шаг 2: Найти начало цикла
    slow = head
    while (slow != fast) {
        slow = slow?.next
        fast = fast?.next
    }

    return slow
}

// Математика: Если расстояние до цикла = a, длина цикла = c,
// при встрече: slow прошёл a + b, fast прошёл a + b + nc
// 2(a + b) = a + b + nc => a = nc - b = (n-1)c + (c-b)
// Значит, от головы и от точки встречи до начала цикла одинаково
```

**Нахождение середины списка:**
```kotlin
fun middleNode(head: ListNode?): ListNode? {
    var slow = head
    var fast = head

    while (fast?.next != null) {
        slow = slow?.next
        fast = fast.next?.next
    }

    return slow
}

// 1 -> 2 -> 3 -> 4 -> 5
// slow=1, fast=1
// slow=2, fast=3
// slow=3, fast=5
// fast.next=null -> return slow=3
```

**Слияние двух отсортированных списков:**
```kotlin
fun mergeTwoLists(l1: ListNode?, l2: ListNode?): ListNode? {
    val dummy = ListNode(0)
    var curr = dummy
    var p1 = l1
    var p2 = l2

    while (p1 != null && p2 != null) {
        if (p1.`val` <= p2.`val`) {
            curr.next = p1
            p1 = p1.next
        } else {
            curr.next = p2
            p2 = p2.next
        }
        curr = curr.next!!
    }

    curr.next = p1 ?: p2

    return dummy.next
}
```

**Удаление N-го узла с конца:**
```kotlin
fun removeNthFromEnd(head: ListNode?, n: Int): ListNode? {
    val dummy = ListNode(0).apply { next = head }

    var slow: ListNode? = dummy
    var fast: ListNode? = dummy

    // Сдвигаем fast на n+1 шагов
    for (i in 0..n) {
        fast = fast?.next
    }

    // Двигаем оба указателя до конца
    while (fast != null) {
        slow = slow?.next
        fast = fast.next
    }

    // Удаляем узел
    slow?.next = slow?.next?.next

    return dummy.next
}
```

**Определение точки пересечения двух списков:**
```kotlin
fun getIntersectionNode(headA: ListNode?, headB: ListNode?): ListNode? {
    var pA = headA
    var pB = headB

    // Когда оба пройдут lenA + lenB шагов, встретятся в точке пересечения
    while (pA != pB) {
        pA = if (pA == null) headB else pA.next
        pB = if (pB == null) headA else pB.next
    }

    return pA
}
```

**Проверка палиндрома:**
```kotlin
fun isPalindrome(head: ListNode?): Boolean {
    // 1. Найти середину
    var slow = head
    var fast = head

    while (fast?.next != null) {
        slow = slow?.next
        fast = fast.next?.next
    }

    // 2. Развернуть вторую половину
    var secondHalf = reverseList(slow)

    // 3. Сравнить две половины
    var firstHalf = head
    while (secondHalf != null) {
        if (firstHalf?.`val` != secondHalf.`val`) return false
        firstHalf = firstHalf.next
        secondHalf = secondHalf.next
    }

    return true
}
```

## Answer (EN)

**List Node Definition:**
```kotlin
class ListNode(var `val`: Int) {
    var next: ListNode? = null
}
```

**Reverse Linked List (Iterative):**
```kotlin
fun reverseList(head: ListNode?): ListNode? {
    var prev: ListNode? = null
    var curr = head

    while (curr != null) {
        val next = curr.next  // Save next
        curr.next = prev      // Reverse pointer
        prev = curr           // Move prev
        curr = next           // Move curr
    }

    return prev  // New head
}

// Example: 1 -> 2 -> 3 -> null
// prev=null, curr=1: next=2, 1.next=null, prev=1, curr=2
// prev=1, curr=2: next=3, 2.next=1, prev=2, curr=3
// prev=2, curr=3: next=null, 3.next=2, prev=3, curr=null
// Result: 3 -> 2 -> 1 -> null
```

**Reverse Linked List (Recursive):**
```kotlin
fun reverseListRecursive(head: ListNode?): ListNode? {
    // Base case
    if (head?.next == null) return head

    // Recursively reverse the rest
    val newHead = reverseListRecursive(head.next)

    // Reverse current node's link
    head.next?.next = head
    head.next = null

    return newHead
}
```

**Cycle Detection (Floyd's Tortoise and Hare):**
```kotlin
fun hasCycle(head: ListNode?): Boolean {
    var slow = head
    var fast = head

    while (fast?.next != null) {
        slow = slow?.next          // Step 1
        fast = fast.next?.next     // Step 2

        if (slow == fast) return true
    }

    return false
}
```

**Find Cycle Start:**
```kotlin
fun detectCycle(head: ListNode?): ListNode? {
    var slow = head
    var fast = head

    // Step 1: Find meeting point
    while (fast?.next != null) {
        slow = slow?.next
        fast = fast.next?.next

        if (slow == fast) break
    }

    // No cycle
    if (fast?.next == null) return null

    // Step 2: Find cycle start
    slow = head
    while (slow != fast) {
        slow = slow?.next
        fast = fast?.next
    }

    return slow
}

// Math: If distance to cycle = a, cycle length = c,
// at meeting: slow traveled a + b, fast traveled a + b + nc
// 2(a + b) = a + b + nc => a = nc - b = (n-1)c + (c-b)
// So from head and meeting point to cycle start is same distance
```

**Find Middle of List:**
```kotlin
fun middleNode(head: ListNode?): ListNode? {
    var slow = head
    var fast = head

    while (fast?.next != null) {
        slow = slow?.next
        fast = fast.next?.next
    }

    return slow
}

// 1 -> 2 -> 3 -> 4 -> 5
// slow=1, fast=1
// slow=2, fast=3
// slow=3, fast=5
// fast.next=null -> return slow=3
```

**Merge Two Sorted Lists:**
```kotlin
fun mergeTwoLists(l1: ListNode?, l2: ListNode?): ListNode? {
    val dummy = ListNode(0)
    var curr = dummy
    var p1 = l1
    var p2 = l2

    while (p1 != null && p2 != null) {
        if (p1.`val` <= p2.`val`) {
            curr.next = p1
            p1 = p1.next
        } else {
            curr.next = p2
            p2 = p2.next
        }
        curr = curr.next!!
    }

    curr.next = p1 ?: p2

    return dummy.next
}
```

**Remove Nth Node From End:**
```kotlin
fun removeNthFromEnd(head: ListNode?, n: Int): ListNode? {
    val dummy = ListNode(0).apply { next = head }

    var slow: ListNode? = dummy
    var fast: ListNode? = dummy

    // Move fast n+1 steps ahead
    for (i in 0..n) {
        fast = fast?.next
    }

    // Move both pointers until end
    while (fast != null) {
        slow = slow?.next
        fast = fast.next
    }

    // Remove node
    slow?.next = slow?.next?.next

    return dummy.next
}
```

**Find Intersection of Two Lists:**
```kotlin
fun getIntersectionNode(headA: ListNode?, headB: ListNode?): ListNode? {
    var pA = headA
    var pB = headB

    // When both travel lenA + lenB steps, they meet at intersection
    while (pA != pB) {
        pA = if (pA == null) headB else pA.next
        pB = if (pB == null) headA else pB.next
    }

    return pA
}
```

**Palindrome Check:**
```kotlin
fun isPalindrome(head: ListNode?): Boolean {
    // 1. Find middle
    var slow = head
    var fast = head

    while (fast?.next != null) {
        slow = slow?.next
        fast = fast.next?.next
    }

    // 2. Reverse second half
    var secondHalf = reverseList(slow)

    // 3. Compare two halves
    var firstHalf = head
    while (secondHalf != null) {
        if (firstHalf?.`val` != secondHalf.`val`) return false
        firstHalf = firstHalf.next
        secondHalf = secondHalf.next
    }

    return true
}
```

---

## Follow-ups

- How would you reverse a linked list in groups of k?
- What is the time complexity of Floyd's cycle detection?
- How would you sort a linked list (merge sort vs quick sort)?

## Related Questions

### Prerequisites (Easier)
- [[q-data-structures-overview--algorithms--easy]] - Data structures basics

### Related (Same Level)
- [[q-two-pointers-sliding-window--algorithms--medium]] - Two pointers pattern
- [[q-stack-queue-problems--algorithms--medium]] - Stack problems

### Advanced (Harder)
- [[q-heap-priority-queue--algorithms--medium]] - Merge K sorted lists
- [[q-sorting-algorithms-comparison--algorithms--medium]] - Sorting linked lists
