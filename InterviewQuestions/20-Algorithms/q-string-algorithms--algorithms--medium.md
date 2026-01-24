---
id: algo-011
title: String Algorithms / Строковые алгоритмы
aliases:
- String Algorithms
- String Manipulation
- Строковые алгоритмы
- Работа со строками
topic: algorithms
subtopics:
- string
- manipulation
- palindrome
question_kind: coding
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-algorithms
related:
- c-string
- c-palindrome
- q-two-pointers-sliding-window--algorithms--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- algorithms
- string
- difficulty/medium
- palindrome
- manipulation
sources:
- https://en.wikipedia.org/wiki/String_(computer_science)
anki_cards:
- slug: algo-011-0-en
  language: en
  anki_id: 1769168918271
  synced_at: '2026-01-23T15:48:41.078978'
- slug: algo-011-0-ru
  language: ru
  anki_id: 1769168918293
  synced_at: '2026-01-23T15:48:41.080285'
---
# Вопрос (RU)
> Какие основные алгоритмы работы со строками используются на интервью? Объясни проверку палиндрома, проверку анаграмм и другие распространенные паттерны.

# Question (EN)
> What are the main string algorithms used in interviews? Explain palindrome checking, anagram checking, and other common patterns.

---

## Ответ (RU)

**Теория строковых алгоритмов:**
Строковые задачи часто используют два указателя, хеш-таблицы для подсчета символов и скользящее окно. Ключ к успеху - выбор правильной структуры данных.

**Проверка палиндрома:**
```kotlin
// Два указателя с противоположных концов
fun isPalindrome(s: String): Boolean {
    var left = 0
    var right = s.length - 1

    while (left < right) {
        // Пропуск не-буквенно-цифровых символов
        while (left < right && !s[left].isLetterOrDigit()) left++
        while (left < right && !s[right].isLetterOrDigit()) right--

        if (s[left].lowercaseChar() != s[right].lowercaseChar()) {
            return false
        }

        left++
        right--
    }

    return true
}
```

**Проверка анаграмм:**
```kotlin
// Использование массива частот (для ASCII)
fun isAnagram(s: String, t: String): Boolean {
    if (s.length != t.length) return false

    val count = IntArray(26)

    for (i in s.indices) {
        count[s[i] - 'a']++
        count[t[i] - 'a']--
    }

    return count.all { it == 0 }
}

// Группировка анаграмм
fun groupAnagrams(strs: Array<String>): List<List<String>> {
    val map = mutableMapOf<String, MutableList<String>>()

    for (s in strs) {
        // Используем отсортированную строку как ключ
        val key = s.toCharArray().sorted().joinToString("")
        map.getOrPut(key) { mutableListOf() }.add(s)
    }

    return map.values.toList()
}
```

**Самая длинная палиндромная подстрока:**
```kotlin
// Расширение от центра
fun longestPalindrome(s: String): String {
    if (s.isEmpty()) return ""

    var start = 0
    var maxLen = 1

    fun expandFromCenter(left: Int, right: Int): Int {
        var l = left
        var r = right

        while (l >= 0 && r < s.length && s[l] == s[r]) {
            l--
            r++
        }

        return r - l - 1  // Длина палиндрома
    }

    for (i in s.indices) {
        // Нечетная длина (центр - один символ)
        val len1 = expandFromCenter(i, i)
        // Четная длина (центр - между символами)
        val len2 = expandFromCenter(i, i + 1)

        val len = maxOf(len1, len2)

        if (len > maxLen) {
            maxLen = len
            start = i - (len - 1) / 2
        }
    }

    return s.substring(start, start + maxLen)
}
```

**Реверс слов в строке:**
```kotlin
fun reverseWords(s: String): String {
    return s.trim()
        .split("\\s+".toRegex())
        .reversed()
        .joinToString(" ")
}

// In-place версия (через массив символов)
fun reverseWordsInPlace(s: CharArray) {
    // 1. Реверс всей строки
    reverse(s, 0, s.size - 1)

    // 2. Реверс каждого слова
    var start = 0
    for (end in s.indices) {
        if (s[end] == ' ') {
            reverse(s, start, end - 1)
            start = end + 1
        }
    }

    // 3. Реверс последнего слова
    reverse(s, start, s.size - 1)
}

fun reverse(s: CharArray, start: Int, end: Int) {
    var l = start
    var r = end
    while (l < r) {
        val temp = s[l]
        s[l] = s[r]
        s[r] = temp
        l++
        r--
    }
}
```

**Сжатие строки (Run-Length Encoding):**
```kotlin
fun compress(chars: CharArray): Int {
    var write = 0
    var read = 0

    while (read < chars.size) {
        val char = chars[read]
        var count = 0

        // Считаем повторения
        while (read < chars.size && chars[read] == char) {
            read++
            count++
        }

        // Записываем символ
        chars[write++] = char

        // Записываем число, если > 1
        if (count > 1) {
            for (c in count.toString()) {
                chars[write++] = c
            }
        }
    }

    return write
}
```

**Поиск всех анаграмм в строке:**
```kotlin
fun findAnagrams(s: String, p: String): List<Int> {
    if (s.length < p.length) return emptyList()

    val result = mutableListOf<Int>()
    val pCount = IntArray(26)
    val sCount = IntArray(26)

    // Заполняем частоты паттерна
    for (c in p) pCount[c - 'a']++

    for (i in s.indices) {
        // Добавляем правый символ
        sCount[s[i] - 'a']++

        // Удаляем левый символ (когда окно больше паттерна)
        if (i >= p.length) {
            sCount[s[i - p.length] - 'a']--
        }

        // Сравниваем частоты
        if (pCount.contentEquals(sCount)) {
            result.add(i - p.length + 1)
        }
    }

    return result
}
```

## Answer (EN)

**String Algorithms Theory:**
String problems often use two pointers, hash tables for character counting, and sliding window. The key to success is choosing the right data structure.

**Palindrome Check:**
```kotlin
// Two pointers from opposite ends
fun isPalindrome(s: String): Boolean {
    var left = 0
    var right = s.length - 1

    while (left < right) {
        // Skip non-alphanumeric characters
        while (left < right && !s[left].isLetterOrDigit()) left++
        while (left < right && !s[right].isLetterOrDigit()) right--

        if (s[left].lowercaseChar() != s[right].lowercaseChar()) {
            return false
        }

        left++
        right--
    }

    return true
}
```

**Anagram Check:**
```kotlin
// Using frequency array (for ASCII)
fun isAnagram(s: String, t: String): Boolean {
    if (s.length != t.length) return false

    val count = IntArray(26)

    for (i in s.indices) {
        count[s[i] - 'a']++
        count[t[i] - 'a']--
    }

    return count.all { it == 0 }
}

// Group anagrams
fun groupAnagrams(strs: Array<String>): List<List<String>> {
    val map = mutableMapOf<String, MutableList<String>>()

    for (s in strs) {
        // Use sorted string as key
        val key = s.toCharArray().sorted().joinToString("")
        map.getOrPut(key) { mutableListOf() }.add(s)
    }

    return map.values.toList()
}
```

**Longest Palindromic Substring:**
```kotlin
// Expand from center
fun longestPalindrome(s: String): String {
    if (s.isEmpty()) return ""

    var start = 0
    var maxLen = 1

    fun expandFromCenter(left: Int, right: Int): Int {
        var l = left
        var r = right

        while (l >= 0 && r < s.length && s[l] == s[r]) {
            l--
            r++
        }

        return r - l - 1  // Palindrome length
    }

    for (i in s.indices) {
        // Odd length (single char center)
        val len1 = expandFromCenter(i, i)
        // Even length (center between chars)
        val len2 = expandFromCenter(i, i + 1)

        val len = maxOf(len1, len2)

        if (len > maxLen) {
            maxLen = len
            start = i - (len - 1) / 2
        }
    }

    return s.substring(start, start + maxLen)
}
```

**Reverse Words in String:**
```kotlin
fun reverseWords(s: String): String {
    return s.trim()
        .split("\\s+".toRegex())
        .reversed()
        .joinToString(" ")
}

// In-place version (using char array)
fun reverseWordsInPlace(s: CharArray) {
    // 1. Reverse entire string
    reverse(s, 0, s.size - 1)

    // 2. Reverse each word
    var start = 0
    for (end in s.indices) {
        if (s[end] == ' ') {
            reverse(s, start, end - 1)
            start = end + 1
        }
    }

    // 3. Reverse last word
    reverse(s, start, s.size - 1)
}

fun reverse(s: CharArray, start: Int, end: Int) {
    var l = start
    var r = end
    while (l < r) {
        val temp = s[l]
        s[l] = s[r]
        s[r] = temp
        l++
        r--
    }
}
```

**String Compression (Run-Length Encoding):**
```kotlin
fun compress(chars: CharArray): Int {
    var write = 0
    var read = 0

    while (read < chars.size) {
        val char = chars[read]
        var count = 0

        // Count repetitions
        while (read < chars.size && chars[read] == char) {
            read++
            count++
        }

        // Write character
        chars[write++] = char

        // Write count if > 1
        if (count > 1) {
            for (c in count.toString()) {
                chars[write++] = c
            }
        }
    }

    return write
}
```

**Find All Anagrams in String:**
```kotlin
fun findAnagrams(s: String, p: String): List<Int> {
    if (s.length < p.length) return emptyList()

    val result = mutableListOf<Int>()
    val pCount = IntArray(26)
    val sCount = IntArray(26)

    // Fill pattern frequencies
    for (c in p) pCount[c - 'a']++

    for (i in s.indices) {
        // Add right character
        sCount[s[i] - 'a']++

        // Remove left character (when window larger than pattern)
        if (i >= p.length) {
            sCount[s[i - p.length] - 'a']--
        }

        // Compare frequencies
        if (pCount.contentEquals(sCount)) {
            result.add(i - p.length + 1)
        }
    }

    return result
}
```

---

## Follow-ups

- How would you check if one string is a rotation of another?
- What is the time complexity of longest palindromic substring?
- How do you handle Unicode strings vs ASCII?

## Related Questions

### Prerequisites (Easier)
- [[q-hash-table-applications--algorithms--easy]] - Hash table patterns
- [[q-data-structures-overview--algorithms--easy]] - Data structures basics

### Related (Same Level)
- [[q-two-pointers-sliding-window--algorithms--medium]] - Sliding window
- [[q-bit-manipulation--algorithms--medium]] - Bit manipulation

### Advanced (Harder)
- [[q-string-pattern-matching--algorithms--hard]] - KMP, Rabin-Karp
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - DP for strings
