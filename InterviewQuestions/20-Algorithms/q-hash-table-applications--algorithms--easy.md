---
id: algo-014
title: Hash Table Applications / Применение хеш-таблиц
aliases:
- Hash Table
- HashMap Patterns
- Хеш-таблица
- Паттерны HashMap
topic: algorithms
subtopics:
- hash-table
- hashmap
- frequency
question_kind: coding
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-algorithms
related:
- c-hash-table
- c-hashmap
- q-data-structures-overview--algorithms--easy
created: 2026-01-23
updated: 2026-01-23
tags:
- algorithms
- hash-table
- difficulty/easy
- frequency
- two-sum
sources:
- https://en.wikipedia.org/wiki/Hash_table
anki_cards:
- slug: algo-014-0-en
  language: en
  anki_id: 1769168919620
  synced_at: '2026-01-26T09:10:14.500295'
- slug: algo-014-0-ru
  language: ru
  anki_id: 1769168919644
  synced_at: '2026-01-26T09:10:14.501532'
---
# Вопрос (RU)
> Какие типичные задачи решаются с помощью хеш-таблиц? Объясни паттерн Two Sum, подсчет частот и группировку элементов.

# Question (EN)
> What typical problems are solved using hash tables? Explain the Two Sum pattern, frequency counting, and element grouping.

---

## Ответ (RU)

**Теория хеш-таблиц:**
Хеш-таблица обеспечивает O(1) среднее время для вставки, поиска и удаления. Это делает её идеальной для задач, где нужно быстро проверять наличие элемента или хранить пары ключ-значение.

**Two Sum - классический паттерн:**
```kotlin
// Найти два числа, дающие в сумме target
fun twoSum(nums: IntArray, target: Int): IntArray {
    val map = mutableMapOf<Int, Int>()  // value -> index

    for ((i, num) in nums.withIndex()) {
        val complement = target - num

        if (complement in map) {
            return intArrayOf(map[complement]!!, i)
        }

        map[num] = i
    }

    return intArrayOf()
}

// Пример: nums = [2, 7, 11, 15], target = 9
// i=0: num=2, complement=7, map={2:0}
// i=1: num=7, complement=2, 2 in map! -> [0, 1]
```

**Two Sum II - отсортированный массив:**
```kotlin
// Когда массив отсортирован, используем два указателя
fun twoSumSorted(numbers: IntArray, target: Int): IntArray {
    var left = 0
    var right = numbers.size - 1

    while (left < right) {
        val sum = numbers[left] + numbers[right]

        when {
            sum == target -> return intArrayOf(left + 1, right + 1)
            sum < target -> left++
            else -> right--
        }
    }

    return intArrayOf()
}
```

**Подсчет частот:**
```kotlin
// Найти наиболее частый элемент
fun majorityElement(nums: IntArray): Int {
    val count = mutableMapOf<Int, Int>()

    for (num in nums) {
        count[num] = count.getOrDefault(num, 0) + 1

        if (count[num]!! > nums.size / 2) {
            return num
        }
    }

    return -1
}

// Top K частых элементов
fun topKFrequent(nums: IntArray, k: Int): IntArray {
    val count = mutableMapOf<Int, Int>()

    for (num in nums) {
        count[num] = count.getOrDefault(num, 0) + 1
    }

    // Bucket sort: частота -> список чисел
    val buckets = Array<MutableList<Int>>(nums.size + 1) { mutableListOf() }

    for ((num, freq) in count) {
        buckets[freq].add(num)
    }

    val result = mutableListOf<Int>()

    // Собираем сверху вниз
    for (i in buckets.size - 1 downTo 0) {
        for (num in buckets[i]) {
            result.add(num)
            if (result.size == k) return result.toIntArray()
        }
    }

    return result.toIntArray()
}
```

**Проверка дубликатов:**
```kotlin
// Есть ли дубликаты?
fun containsDuplicate(nums: IntArray): Boolean {
    val seen = mutableSetOf<Int>()

    for (num in nums) {
        if (num in seen) return true
        seen.add(num)
    }

    return false
}

// Дубликаты в пределах k позиций
fun containsNearbyDuplicate(nums: IntArray, k: Int): Boolean {
    val window = mutableSetOf<Int>()

    for (i in nums.indices) {
        // Поддерживаем окно размера k
        if (i > k) {
            window.remove(nums[i - k - 1])
        }

        if (nums[i] in window) return true
        window.add(nums[i])
    }

    return false
}
```

**Группировка анаграмм:**
```kotlin
fun groupAnagrams(strs: Array<String>): List<List<String>> {
    val map = mutableMapOf<String, MutableList<String>>()

    for (s in strs) {
        // Ключ - отсортированная строка
        val key = s.toCharArray().sorted().joinToString("")
        map.getOrPut(key) { mutableListOf() }.add(s)
    }

    return map.values.toList()
}

// Альтернатива: ключ = массив частот
fun groupAnagramsFreq(strs: Array<String>): List<List<String>> {
    val map = mutableMapOf<String, MutableList<String>>()

    for (s in strs) {
        val count = IntArray(26)
        for (c in s) count[c - 'a']++

        val key = count.joinToString("#")
        map.getOrPut(key) { mutableListOf() }.add(s)
    }

    return map.values.toList()
}
```

**Подмассив с суммой K:**
```kotlin
// Количество подмассивов с суммой равной k
fun subarraySum(nums: IntArray, k: Int): Int {
    val prefixCount = mutableMapOf<Int, Int>()
    prefixCount[0] = 1  // Пустой префикс

    var sum = 0
    var count = 0

    for (num in nums) {
        sum += num

        // Если есть prefix = sum - k, то есть подмассив с суммой k
        if ((sum - k) in prefixCount) {
            count += prefixCount[sum - k]!!
        }

        prefixCount[sum] = prefixCount.getOrDefault(sum, 0) + 1
    }

    return count
}
```

**Longest Consecutive Sequence:**
```kotlin
// Самая длинная последовательность подряд идущих чисел
fun longestConsecutive(nums: IntArray): Int {
    val set = nums.toHashSet()
    var longest = 0

    for (num in set) {
        // Начинаем только если num - начало последовательности
        if ((num - 1) !in set) {
            var currentNum = num
            var currentLength = 1

            while ((currentNum + 1) in set) {
                currentNum++
                currentLength++
            }

            longest = maxOf(longest, currentLength)
        }
    }

    return longest
}
```

**HashMap vs HashSet:**
| Структура | Хранит | Использование |
|-----------|--------|---------------|
| HashMap | ключ-значение | Two Sum, частоты |
| HashSet | только ключи | проверка наличия |

## Answer (EN)

**Hash Table Theory:**
Hash table provides O(1) average time for insert, lookup, and delete. This makes it ideal for problems requiring fast element existence checks or key-value storage.

**Two Sum - Classic Pattern:**
```kotlin
// Find two numbers that sum to target
fun twoSum(nums: IntArray, target: Int): IntArray {
    val map = mutableMapOf<Int, Int>()  // value -> index

    for ((i, num) in nums.withIndex()) {
        val complement = target - num

        if (complement in map) {
            return intArrayOf(map[complement]!!, i)
        }

        map[num] = i
    }

    return intArrayOf()
}

// Example: nums = [2, 7, 11, 15], target = 9
// i=0: num=2, complement=7, map={2:0}
// i=1: num=7, complement=2, 2 in map! -> [0, 1]
```

**Two Sum II - Sorted Array:**
```kotlin
// When array is sorted, use two pointers
fun twoSumSorted(numbers: IntArray, target: Int): IntArray {
    var left = 0
    var right = numbers.size - 1

    while (left < right) {
        val sum = numbers[left] + numbers[right]

        when {
            sum == target -> return intArrayOf(left + 1, right + 1)
            sum < target -> left++
            else -> right--
        }
    }

    return intArrayOf()
}
```

**Frequency Counting:**
```kotlin
// Find most frequent element
fun majorityElement(nums: IntArray): Int {
    val count = mutableMapOf<Int, Int>()

    for (num in nums) {
        count[num] = count.getOrDefault(num, 0) + 1

        if (count[num]!! > nums.size / 2) {
            return num
        }
    }

    return -1
}

// Top K frequent elements
fun topKFrequent(nums: IntArray, k: Int): IntArray {
    val count = mutableMapOf<Int, Int>()

    for (num in nums) {
        count[num] = count.getOrDefault(num, 0) + 1
    }

    // Bucket sort: frequency -> list of numbers
    val buckets = Array<MutableList<Int>>(nums.size + 1) { mutableListOf() }

    for ((num, freq) in count) {
        buckets[freq].add(num)
    }

    val result = mutableListOf<Int>()

    // Collect from top to bottom
    for (i in buckets.size - 1 downTo 0) {
        for (num in buckets[i]) {
            result.add(num)
            if (result.size == k) return result.toIntArray()
        }
    }

    return result.toIntArray()
}
```

**Duplicate Detection:**
```kotlin
// Are there duplicates?
fun containsDuplicate(nums: IntArray): Boolean {
    val seen = mutableSetOf<Int>()

    for (num in nums) {
        if (num in seen) return true
        seen.add(num)
    }

    return false
}

// Duplicates within k positions
fun containsNearbyDuplicate(nums: IntArray, k: Int): Boolean {
    val window = mutableSetOf<Int>()

    for (i in nums.indices) {
        // Maintain window of size k
        if (i > k) {
            window.remove(nums[i - k - 1])
        }

        if (nums[i] in window) return true
        window.add(nums[i])
    }

    return false
}
```

**Group Anagrams:**
```kotlin
fun groupAnagrams(strs: Array<String>): List<List<String>> {
    val map = mutableMapOf<String, MutableList<String>>()

    for (s in strs) {
        // Key is sorted string
        val key = s.toCharArray().sorted().joinToString("")
        map.getOrPut(key) { mutableListOf() }.add(s)
    }

    return map.values.toList()
}

// Alternative: key = frequency array
fun groupAnagramsFreq(strs: Array<String>): List<List<String>> {
    val map = mutableMapOf<String, MutableList<String>>()

    for (s in strs) {
        val count = IntArray(26)
        for (c in s) count[c - 'a']++

        val key = count.joinToString("#")
        map.getOrPut(key) { mutableListOf() }.add(s)
    }

    return map.values.toList()
}
```

**Subarray Sum Equals K:**
```kotlin
// Count subarrays with sum equal to k
fun subarraySum(nums: IntArray, k: Int): Int {
    val prefixCount = mutableMapOf<Int, Int>()
    prefixCount[0] = 1  // Empty prefix

    var sum = 0
    var count = 0

    for (num in nums) {
        sum += num

        // If prefix = sum - k exists, there's a subarray with sum k
        if ((sum - k) in prefixCount) {
            count += prefixCount[sum - k]!!
        }

        prefixCount[sum] = prefixCount.getOrDefault(sum, 0) + 1
    }

    return count
}
```

**Longest Consecutive Sequence:**
```kotlin
// Longest sequence of consecutive numbers
fun longestConsecutive(nums: IntArray): Int {
    val set = nums.toHashSet()
    var longest = 0

    for (num in set) {
        // Start only if num is sequence start
        if ((num - 1) !in set) {
            var currentNum = num
            var currentLength = 1

            while ((currentNum + 1) in set) {
                currentNum++
                currentLength++
            }

            longest = maxOf(longest, currentLength)
        }
    }

    return longest
}
```

**HashMap vs HashSet:**
| Structure | Stores | Use Case |
|-----------|--------|----------|
| HashMap | key-value | Two Sum, frequencies |
| HashSet | keys only | existence checks |

---

## Follow-ups

- What is the time complexity of hash table operations?
- How do you handle hash collisions?
- When would you use TreeMap instead of HashMap?

## Related Questions

### Prerequisites (Easier)
- [[q-data-structures-overview--algorithms--easy]] - Data structures basics

### Related (Same Level)
- [[q-string-algorithms--algorithms--medium]] - String manipulation
- [[q-two-pointers-sliding-window--algorithms--medium]] - Two pointers

### Advanced (Harder)
- [[q-prefix-sum-range-queries--algorithms--medium]] - Prefix sums
- [[q-heap-priority-queue--algorithms--medium]] - Top K problems
