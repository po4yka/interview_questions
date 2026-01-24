---
id: algo-013
title: Bit Manipulation / Битовые операции
aliases:
- Bit Manipulation
- Bitwise Operations
- Битовые операции
- Побитовые операции
topic: algorithms
subtopics:
- bit-manipulation
- bitwise
- xor
question_kind: coding
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-algorithms
related:
- c-bit-manipulation
- c-bitwise
created: 2026-01-23
updated: 2026-01-23
tags:
- algorithms
- bit-manipulation
- difficulty/medium
- xor
- bitwise
sources:
- https://en.wikipedia.org/wiki/Bitwise_operation
anki_cards:
- slug: algo-013-0-en
  language: en
  anki_id: 1769168919245
  synced_at: '2026-01-23T15:48:41.112099'
- slug: algo-013-0-ru
  language: ru
  anki_id: 1769168919280
  synced_at: '2026-01-23T15:48:41.114007'
---
# Вопрос (RU)
> Объясни основные битовые операции и трюки. Как решить задачу "Single Number"? Какие распространенные паттерны используют XOR?

# Question (EN)
> Explain basic bitwise operations and tricks. How do you solve the "Single Number" problem? What common patterns use XOR?

---

## Ответ (RU)

**Теория битовых операций:**
Битовые операции работают напрямую с двоичным представлением чисел. Они очень быстрые и часто используются для оптимизации.

**Основные операции:**
```kotlin
// AND (&) - 1 только если оба бита 1
5 and 3  // 0101 & 0011 = 0001 = 1

// OR (|) - 1 если хотя бы один бит 1
5 or 3   // 0101 | 0011 = 0111 = 7

// XOR (^) - 1 если биты разные
5 xor 3  // 0101 ^ 0011 = 0110 = 6

// NOT (~) - инверсия всех битов
5.inv()  // ~0101 = ...11111010 = -6

// Сдвиг влево (<<) - умножение на 2^n
5 shl 1  // 0101 << 1 = 1010 = 10

// Сдвиг вправо (>>) - деление на 2^n
5 shr 1  // 0101 >> 1 = 0010 = 2
```

**Свойства XOR:**
```kotlin
// a ^ a = 0 (число XOR себя = 0)
// a ^ 0 = a (число XOR 0 = само число)
// a ^ b ^ a = b (XOR коммутативен и ассоциативен)
```

**Single Number - найти число без пары:**
```kotlin
// Все числа, кроме одного, встречаются дважды
fun singleNumber(nums: IntArray): Int {
    var result = 0

    for (num in nums) {
        result = result xor num
    }

    return result
}

// Пример: [2, 1, 4, 2, 1]
// 0 ^ 2 = 2
// 2 ^ 1 = 3
// 3 ^ 4 = 7
// 7 ^ 2 = 5
// 5 ^ 1 = 4  <- ответ
```

**Single Number II - элемент встречается 1 раз, остальные 3:**
```kotlin
fun singleNumberII(nums: IntArray): Int {
    var result = 0

    // Для каждого бита считаем сумму
    for (i in 0 until 32) {
        var sum = 0

        for (num in nums) {
            if ((num shr i) and 1 == 1) {
                sum++
            }
        }

        // Если сумма не делится на 3, этот бит в ответе
        if (sum % 3 != 0) {
            result = result or (1 shl i)
        }
    }

    return result
}
```

**Single Number III - два числа без пары:**
```kotlin
fun singleNumberIII(nums: IntArray): IntArray {
    // Шаг 1: XOR всех чисел = xor двух уникальных
    var xorResult = 0
    for (num in nums) {
        xorResult = xorResult xor num
    }

    // Шаг 2: Найти любой установленный бит (различие между a и b)
    val diffBit = xorResult and (-xorResult)  // Самый правый установленный бит

    // Шаг 3: Разделить числа на две группы
    var a = 0
    var b = 0

    for (num in nums) {
        if ((num and diffBit) == 0) {
            a = a xor num
        } else {
            b = b xor num
        }
    }

    return intArrayOf(a, b)
}
```

**Проверка степени двойки:**
```kotlin
fun isPowerOfTwo(n: Int): Boolean {
    return n > 0 && (n and (n - 1)) == 0
}

// n = 8     = 1000
// n - 1 = 7 = 0111
// n & (n-1) = 0000  <- степень двойки!

// n = 6     = 0110
// n - 1 = 5 = 0101
// n & (n-1) = 0100  <- не степень двойки
```

**Подсчет единичных битов (Hamming Weight):**
```kotlin
fun hammingWeight(n: Int): Int {
    var count = 0
    var num = n

    while (num != 0) {
        count++
        num = num and (num - 1)  // Убираем самый правый бит
    }

    return count
}

// Альтернатива с Kotlin
fun hammingWeightKotlin(n: Int) = n.countOneBits()
```

**Реверс битов:**
```kotlin
fun reverseBits(n: Int): Int {
    var result = 0
    var num = n

    for (i in 0 until 32) {
        result = result shl 1
        result = result or (num and 1)
        num = num shr 1
    }

    return result
}
```

**Битовые маски:**
```kotlin
// Установить i-й бит
fun setBit(n: Int, i: Int) = n or (1 shl i)

// Очистить i-й бит
fun clearBit(n: Int, i: Int) = n and (1 shl i).inv()

// Переключить i-й бит
fun toggleBit(n: Int, i: Int) = n xor (1 shl i)

// Проверить i-й бит
fun checkBit(n: Int, i: Int) = (n shr i) and 1 == 1

// Очистить все биты от MSB до i включительно
fun clearBitsMSBthroughI(n: Int, i: Int) = n and ((1 shl i) - 1)

// Очистить все биты от i до 0 включительно
fun clearBitsIthrough0(n: Int, i: Int) = n and ((-1 shl (i + 1)))
```

**Подмножества с помощью битовых масок:**
```kotlin
fun subsets(nums: IntArray): List<List<Int>> {
    val n = nums.size
    val result = mutableListOf<List<Int>>()

    // 2^n подмножеств
    for (mask in 0 until (1 shl n)) {
        val subset = mutableListOf<Int>()

        for (i in 0 until n) {
            if ((mask and (1 shl i)) != 0) {
                subset.add(nums[i])
            }
        }

        result.add(subset)
    }

    return result
}
```

## Answer (EN)

**Bit Manipulation Theory:**
Bitwise operations work directly with binary representation of numbers. They are very fast and often used for optimization.

**Basic Operations:**
```kotlin
// AND (&) - 1 only if both bits are 1
5 and 3  // 0101 & 0011 = 0001 = 1

// OR (|) - 1 if at least one bit is 1
5 or 3   // 0101 | 0011 = 0111 = 7

// XOR (^) - 1 if bits are different
5 xor 3  // 0101 ^ 0011 = 0110 = 6

// NOT (~) - invert all bits
5.inv()  // ~0101 = ...11111010 = -6

// Left shift (<<) - multiply by 2^n
5 shl 1  // 0101 << 1 = 1010 = 10

// Right shift (>>) - divide by 2^n
5 shr 1  // 0101 >> 1 = 0010 = 2
```

**XOR Properties:**
```kotlin
// a ^ a = 0 (number XOR itself = 0)
// a ^ 0 = a (number XOR 0 = same number)
// a ^ b ^ a = b (XOR is commutative and associative)
```

**Single Number - find number without pair:**
```kotlin
// All numbers except one appear twice
fun singleNumber(nums: IntArray): Int {
    var result = 0

    for (num in nums) {
        result = result xor num
    }

    return result
}

// Example: [2, 1, 4, 2, 1]
// 0 ^ 2 = 2
// 2 ^ 1 = 3
// 3 ^ 4 = 7
// 7 ^ 2 = 5
// 5 ^ 1 = 4  <- answer
```

**Single Number II - element appears once, others 3 times:**
```kotlin
fun singleNumberII(nums: IntArray): Int {
    var result = 0

    // For each bit position, count sum
    for (i in 0 until 32) {
        var sum = 0

        for (num in nums) {
            if ((num shr i) and 1 == 1) {
                sum++
            }
        }

        // If sum not divisible by 3, this bit is in answer
        if (sum % 3 != 0) {
            result = result or (1 shl i)
        }
    }

    return result
}
```

**Single Number III - two numbers without pairs:**
```kotlin
fun singleNumberIII(nums: IntArray): IntArray {
    // Step 1: XOR all numbers = xor of two unique
    var xorResult = 0
    for (num in nums) {
        xorResult = xorResult xor num
    }

    // Step 2: Find any set bit (difference between a and b)
    val diffBit = xorResult and (-xorResult)  // Rightmost set bit

    // Step 3: Partition numbers into two groups
    var a = 0
    var b = 0

    for (num in nums) {
        if ((num and diffBit) == 0) {
            a = a xor num
        } else {
            b = b xor num
        }
    }

    return intArrayOf(a, b)
}
```

**Check Power of Two:**
```kotlin
fun isPowerOfTwo(n: Int): Boolean {
    return n > 0 && (n and (n - 1)) == 0
}

// n = 8     = 1000
// n - 1 = 7 = 0111
// n & (n-1) = 0000  <- power of two!

// n = 6     = 0110
// n - 1 = 5 = 0101
// n & (n-1) = 0100  <- not power of two
```

**Count Set Bits (Hamming Weight):**
```kotlin
fun hammingWeight(n: Int): Int {
    var count = 0
    var num = n

    while (num != 0) {
        count++
        num = num and (num - 1)  // Remove rightmost bit
    }

    return count
}

// Alternative with Kotlin
fun hammingWeightKotlin(n: Int) = n.countOneBits()
```

**Reverse Bits:**
```kotlin
fun reverseBits(n: Int): Int {
    var result = 0
    var num = n

    for (i in 0 until 32) {
        result = result shl 1
        result = result or (num and 1)
        num = num shr 1
    }

    return result
}
```

**Bit Masks:**
```kotlin
// Set i-th bit
fun setBit(n: Int, i: Int) = n or (1 shl i)

// Clear i-th bit
fun clearBit(n: Int, i: Int) = n and (1 shl i).inv()

// Toggle i-th bit
fun toggleBit(n: Int, i: Int) = n xor (1 shl i)

// Check i-th bit
fun checkBit(n: Int, i: Int) = (n shr i) and 1 == 1

// Clear all bits from MSB through i inclusive
fun clearBitsMSBthroughI(n: Int, i: Int) = n and ((1 shl i) - 1)

// Clear all bits from i through 0 inclusive
fun clearBitsIthrough0(n: Int, i: Int) = n and ((-1 shl (i + 1)))
```

**Subsets Using Bitmasks:**
```kotlin
fun subsets(nums: IntArray): List<List<Int>> {
    val n = nums.size
    val result = mutableListOf<List<Int>>()

    // 2^n subsets
    for (mask in 0 until (1 shl n)) {
        val subset = mutableListOf<Int>()

        for (i in 0 until n) {
            if ((mask and (1 shl i)) != 0) {
                subset.add(nums[i])
            }
        }

        result.add(subset)
    }

    return result
}
```

---

## Follow-ups

- How do you find missing number in array [0..n]?
- How do you swap two numbers without temp variable?
- What is the difference between arithmetic and logical shift?

## Related Questions

### Prerequisites (Easier)
- [[q-data-structures-overview--algorithms--easy]] - Data structures basics

### Related (Same Level)
- [[q-hash-table-applications--algorithms--easy]] - Hash tables
- [[q-string-algorithms--algorithms--medium]] - String algorithms

### Advanced (Harder)
- [[q-dynamic-programming-fundamentals--algorithms--hard]] - DP with bitmasks
- [[q-backtracking-algorithms--algorithms--hard]] - Backtracking subsets
