---
id: algo-012
title: String Pattern Matching / Поиск подстроки в строке
aliases:
- Pattern Matching
- KMP Algorithm
- Rabin-Karp
- Поиск подстроки
- Алгоритм КМП
topic: algorithms
subtopics:
- string
- pattern-matching
- kmp
- rabin-karp
question_kind: coding
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-algorithms
related:
- c-string
- c-pattern-matching
- q-string-algorithms--algorithms--medium
created: 2026-01-23
updated: 2026-01-23
tags:
- algorithms
- string
- difficulty/hard
- pattern-matching
- kmp
- rabin-karp
sources:
- https://en.wikipedia.org/wiki/Knuth%E2%80%93Morris%E2%80%93Pratt_algorithm
- https://en.wikipedia.org/wiki/Rabin%E2%80%93Karp_algorithm
anki_cards:
- slug: algo-012-0-en
  language: en
  anki_id: 1769168919971
  synced_at: '2026-01-26T09:10:14.517439'
- slug: algo-012-0-ru
  language: ru
  anki_id: 1769168919993
  synced_at: '2026-01-26T09:10:14.518625'
---
# Вопрос (RU)
> Объясни алгоритмы поиска подстроки: наивный, KMP (Кнута-Морриса-Пратта) и Рабина-Карпа. Когда использовать каждый из них?

# Question (EN)
> Explain substring search algorithms: naive, KMP (Knuth-Morris-Pratt), and Rabin-Karp. When should you use each?

---

## Ответ (RU)

**Теория поиска подстроки:**
Поиск подстроки (паттерна) в тексте - классическая задача. Наивный подход имеет сложность O(n*m), но KMP и Rabin-Karp достигают O(n+m).

**Наивный алгоритм - O(n*m):**
```kotlin
fun naiveSearch(text: String, pattern: String): Int {
    val n = text.length
    val m = pattern.length

    for (i in 0..n - m) {
        var j = 0

        while (j < m && text[i + j] == pattern[j]) {
            j++
        }

        if (j == m) return i  // Паттерн найден
    }

    return -1
}
```

**KMP (Кнут-Моррис-Пратт) - O(n+m):**
Идея: при несовпадении не начинаем заново, а используем информацию о совпавшей части.
```kotlin
// LPS (Longest Proper Prefix which is also Suffix)
// Для "AABAACAABAA": [0, 1, 0, 1, 2, 0, 1, 2, 3, 4, 5]
fun computeLPS(pattern: String): IntArray {
    val m = pattern.length
    val lps = IntArray(m)

    var length = 0  // Длина предыдущего LPS
    var i = 1

    while (i < m) {
        if (pattern[i] == pattern[length]) {
            length++
            lps[i] = length
            i++
        } else {
            if (length != 0) {
                // Не инкрементируем i
                length = lps[length - 1]
            } else {
                lps[i] = 0
                i++
            }
        }
    }

    return lps
}

fun kmpSearch(text: String, pattern: String): Int {
    val n = text.length
    val m = pattern.length

    if (m == 0) return 0

    val lps = computeLPS(pattern)

    var i = 0  // Индекс в тексте
    var j = 0  // Индекс в паттерне

    while (i < n) {
        if (text[i] == pattern[j]) {
            i++
            j++

            if (j == m) {
                return i - j  // Паттерн найден
                // Для всех вхождений: j = lps[j - 1]
            }
        } else {
            if (j != 0) {
                // Используем LPS для пропуска
                j = lps[j - 1]
            } else {
                i++
            }
        }
    }

    return -1
}

// Найти все вхождения
fun kmpSearchAll(text: String, pattern: String): List<Int> {
    val result = mutableListOf<Int>()
    val n = text.length
    val m = pattern.length

    if (m == 0) return result

    val lps = computeLPS(pattern)
    var i = 0
    var j = 0

    while (i < n) {
        if (text[i] == pattern[j]) {
            i++
            j++

            if (j == m) {
                result.add(i - j)
                j = lps[j - 1]  // Продолжаем искать
            }
        } else {
            if (j != 0) {
                j = lps[j - 1]
            } else {
                i++
            }
        }
    }

    return result
}
```

**Rabin-Karp - O(n+m) в среднем:**
Идея: используем хеширование для быстрого сравнения.
```kotlin
fun rabinKarp(text: String, pattern: String): Int {
    val n = text.length
    val m = pattern.length

    if (m > n) return -1
    if (m == 0) return 0

    val base = 256          // Размер алфавита
    val prime = 101L        // Простое число для модуля

    var patternHash = 0L
    var textHash = 0L
    var h = 1L              // base^(m-1) % prime

    // Вычисляем h = base^(m-1) % prime
    for (i in 0 until m - 1) {
        h = (h * base) % prime
    }

    // Вычисляем начальные хеши
    for (i in 0 until m) {
        patternHash = (patternHash * base + pattern[i].code) % prime
        textHash = (textHash * base + text[i].code) % prime
    }

    // Скользящее окно
    for (i in 0..n - m) {
        // Если хеши совпадают, проверяем посимвольно
        if (patternHash == textHash) {
            var match = true
            for (j in 0 until m) {
                if (text[i + j] != pattern[j]) {
                    match = false
                    break
                }
            }
            if (match) return i
        }

        // Вычисляем хеш для следующего окна
        if (i < n - m) {
            textHash = ((textHash - text[i].code * h) * base + text[i + m].code) % prime

            // Обработка отрицательного хеша
            if (textHash < 0) {
                textHash += prime
            }
        }
    }

    return -1
}
```

**Z-алгоритм - O(n+m):**
```kotlin
// Z[i] = длина наибольшей подстроки, начинающейся с i,
// которая совпадает с префиксом строки
fun zFunction(s: String): IntArray {
    val n = s.length
    val z = IntArray(n)

    var l = 0
    var r = 0

    for (i in 1 until n) {
        if (i < r) {
            z[i] = minOf(r - i, z[i - l])
        }

        while (i + z[i] < n && s[z[i]] == s[i + z[i]]) {
            z[i]++
        }

        if (i + z[i] > r) {
            l = i
            r = i + z[i]
        }
    }

    return z
}

// Поиск паттерна с помощью Z-функции
fun zSearch(text: String, pattern: String): List<Int> {
    val combined = "$pattern$$text"  // $ - разделитель
    val z = zFunction(combined)

    val result = mutableListOf<Int>()
    val m = pattern.length

    for (i in m + 1 until combined.length) {
        if (z[i] == m) {
            result.add(i - m - 1)
        }
    }

    return result
}
```

**Сравнение алгоритмов:**
| Алгоритм | Время | Память | Когда использовать |
|----------|-------|--------|-------------------|
| Наивный | O(nm) | O(1) | Короткие строки |
| KMP | O(n+m) | O(m) | Один паттерн, много текста |
| Rabin-Karp | O(n+m) avg | O(1) | Множественные паттерны |
| Z-функция | O(n+m) | O(n+m) | Альтернатива KMP |

## Answer (EN)

**Substring Search Theory:**
Searching for a pattern in text is a classic problem. Naive approach is O(n*m), but KMP and Rabin-Karp achieve O(n+m).

**Naive Algorithm - O(n*m):**
```kotlin
fun naiveSearch(text: String, pattern: String): Int {
    val n = text.length
    val m = pattern.length

    for (i in 0..n - m) {
        var j = 0

        while (j < m && text[i + j] == pattern[j]) {
            j++
        }

        if (j == m) return i  // Pattern found
    }

    return -1
}
```

**KMP (Knuth-Morris-Pratt) - O(n+m):**
Idea: on mismatch, don't restart, use info about matched portion.
```kotlin
// LPS (Longest Proper Prefix which is also Suffix)
// For "AABAACAABAA": [0, 1, 0, 1, 2, 0, 1, 2, 3, 4, 5]
fun computeLPS(pattern: String): IntArray {
    val m = pattern.length
    val lps = IntArray(m)

    var length = 0  // Length of previous LPS
    var i = 1

    while (i < m) {
        if (pattern[i] == pattern[length]) {
            length++
            lps[i] = length
            i++
        } else {
            if (length != 0) {
                // Don't increment i
                length = lps[length - 1]
            } else {
                lps[i] = 0
                i++
            }
        }
    }

    return lps
}

fun kmpSearch(text: String, pattern: String): Int {
    val n = text.length
    val m = pattern.length

    if (m == 0) return 0

    val lps = computeLPS(pattern)

    var i = 0  // Index in text
    var j = 0  // Index in pattern

    while (i < n) {
        if (text[i] == pattern[j]) {
            i++
            j++

            if (j == m) {
                return i - j  // Pattern found
                // For all occurrences: j = lps[j - 1]
            }
        } else {
            if (j != 0) {
                // Use LPS to skip
                j = lps[j - 1]
            } else {
                i++
            }
        }
    }

    return -1
}

// Find all occurrences
fun kmpSearchAll(text: String, pattern: String): List<Int> {
    val result = mutableListOf<Int>()
    val n = text.length
    val m = pattern.length

    if (m == 0) return result

    val lps = computeLPS(pattern)
    var i = 0
    var j = 0

    while (i < n) {
        if (text[i] == pattern[j]) {
            i++
            j++

            if (j == m) {
                result.add(i - j)
                j = lps[j - 1]  // Continue searching
            }
        } else {
            if (j != 0) {
                j = lps[j - 1]
            } else {
                i++
            }
        }
    }

    return result
}
```

**Rabin-Karp - O(n+m) average:**
Idea: use hashing for fast comparison.
```kotlin
fun rabinKarp(text: String, pattern: String): Int {
    val n = text.length
    val m = pattern.length

    if (m > n) return -1
    if (m == 0) return 0

    val base = 256          // Alphabet size
    val prime = 101L        // Prime for modulo

    var patternHash = 0L
    var textHash = 0L
    var h = 1L              // base^(m-1) % prime

    // Calculate h = base^(m-1) % prime
    for (i in 0 until m - 1) {
        h = (h * base) % prime
    }

    // Calculate initial hashes
    for (i in 0 until m) {
        patternHash = (patternHash * base + pattern[i].code) % prime
        textHash = (textHash * base + text[i].code) % prime
    }

    // Sliding window
    for (i in 0..n - m) {
        // If hashes match, verify character by character
        if (patternHash == textHash) {
            var match = true
            for (j in 0 until m) {
                if (text[i + j] != pattern[j]) {
                    match = false
                    break
                }
            }
            if (match) return i
        }

        // Calculate hash for next window
        if (i < n - m) {
            textHash = ((textHash - text[i].code * h) * base + text[i + m].code) % prime

            // Handle negative hash
            if (textHash < 0) {
                textHash += prime
            }
        }
    }

    return -1
}
```

**Z-Algorithm - O(n+m):**
```kotlin
// Z[i] = length of longest substring starting at i
// that matches a prefix of the string
fun zFunction(s: String): IntArray {
    val n = s.length
    val z = IntArray(n)

    var l = 0
    var r = 0

    for (i in 1 until n) {
        if (i < r) {
            z[i] = minOf(r - i, z[i - l])
        }

        while (i + z[i] < n && s[z[i]] == s[i + z[i]]) {
            z[i]++
        }

        if (i + z[i] > r) {
            l = i
            r = i + z[i]
        }
    }

    return z
}

// Pattern search using Z-function
fun zSearch(text: String, pattern: String): List<Int> {
    val combined = "$pattern$$text"  // $ is separator
    val z = zFunction(combined)

    val result = mutableListOf<Int>()
    val m = pattern.length

    for (i in m + 1 until combined.length) {
        if (z[i] == m) {
            result.add(i - m - 1)
        }
    }

    return result
}
```

**Algorithm Comparison:**
| Algorithm | Time | Space | When to Use |
|-----------|------|-------|-------------|
| Naive | O(nm) | O(1) | Short strings |
| KMP | O(n+m) | O(m) | Single pattern, lots of text |
| Rabin-Karp | O(n+m) avg | O(1) | Multiple patterns |
| Z-function | O(n+m) | O(n+m) | Alternative to KMP |

---

## Follow-ups

- How does KMP handle patterns with many repeated characters?
- What happens with hash collisions in Rabin-Karp?
- When would you use Aho-Corasick algorithm?

## Related Questions

### Prerequisites (Easier)
- [[q-string-algorithms--algorithms--medium]] - Basic string algorithms
- [[q-hash-table-applications--algorithms--easy]] - Hash tables

### Related (Same Level)
- [[q-trie-data-structure--algorithms--hard]] - Trie for prefix search
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - DP strings

### Advanced (Harder)
- [[q-advanced-graph-algorithms--algorithms--hard]] - Graph algorithms
