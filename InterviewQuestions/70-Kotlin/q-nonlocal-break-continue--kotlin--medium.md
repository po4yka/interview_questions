---
anki_cards:
- slug: q-nonlocal-break-continue--kotlin--medium-0-en
  language: en
  anki_id: 1769173375638
  synced_at: '2026-01-23T17:03:50.450106'
- slug: q-nonlocal-break-continue--kotlin--medium-0-ru
  language: ru
  anki_id: 1769173375658
  synced_at: '2026-01-23T17:03:50.452124'
---
# Вопрос (RU)
> Объясните non-local break и continue в Kotlin. Как они работают с inline-лямбдами? Приведите практические примеры.

# Question (EN)
> Explain non-local break and continue in Kotlin. How do they work with inline lambdas? Provide practical examples.

## Ответ (RU)

**Введено в Kotlin 2.1, стабильно с 2.2**

**Non-local break и continue** позволяют использовать `break` и `continue` внутри inline-лямбд для управления внешним циклом. Раньше это было невозможно, и приходилось использовать метки или обходные пути.

---

### Синтаксис

```kotlin
for (item in collection) {
    collection.forEach { element ->
        if (condition) break    // выходит из for
        if (other) continue     // переходит к следующей итерации for
    }
}
```

---

### До Kotlin 2.1 (обходные пути)

```kotlin
// Использование меток
outer@ for (row in matrix) {
    row.forEach { cell ->
        if (cell == target) {
            // Нужно использовать return с меткой
            return@outer  // но это не break!
        }
    }
}

// Или использовать run с меткой
for (item in items) {
    run breaking@ {
        items.forEach {
            if (condition) return@breaking
        }
    }
}
```

---

### С Non-local Break/Continue (Kotlin 2.1+)

```kotlin
for (row in matrix) {
    row.forEach { cell ->
        if (cell == target) break      // выходит из for
        if (cell < 0) continue         // следующая итерация for
    }
}
```

---

### Практические примеры

**Поиск в матрице:**

```kotlin
fun findInMatrix(matrix: List<List<Int>>, target: Int): Pair<Int, Int>? {
    var result: Pair<Int, Int>? = null

    for ((rowIdx, row) in matrix.withIndex()) {
        row.forEachIndexed { colIdx, value ->
            if (value == target) {
                result = rowIdx to colIdx
                break  // выходим из внешнего for
            }
        }
    }

    return result
}
```

**Валидация с пропуском:**

```kotlin
data class Order(val items: List<Item>)
data class Item(val name: String, val price: Double, val valid: Boolean)

fun processOrders(orders: List<Order>) {
    for (order in orders) {
        var hasInvalidItem = false

        order.items.forEach { item ->
            if (!item.valid) {
                hasInvalidItem = true
                break  // прекращаем проверку этого заказа
            }
            if (item.price <= 0) {
                continue  // пропускаем товары с нулевой ценой
            }
            processItem(item)
        }

        if (hasInvalidItem) {
            println("Order skipped due to invalid items")
        }
    }
}
```

**Обработка вложенных структур:**

```kotlin
data class Category(val name: String, val products: List<Product>)
data class Product(val id: Int, val inStock: Boolean)

fun findFirstAvailable(categories: List<Category>): Product? {
    for (category in categories) {
        category.products.forEach { product ->
            if (product.inStock) {
                return product  // return работает как раньше
            }
        }
    }
    return null
}

fun checkAllCategories(categories: List<Category>): Boolean {
    for (category in categories) {
        var hasStock = false
        category.products.forEach { product ->
            if (product.inStock) {
                hasStock = true
                break  // нашли товар в наличии, переходим к следующей категории
            }
        }
        if (!hasStock) return false
    }
    return true
}
```

---

### Ограничения

Non-local break/continue работает только с **inline**-функциями:

```kotlin
// Работает: forEach - inline функция
for (x in list1) {
    list2.forEach { y ->
        if (condition) break  // OK
    }
}

// НЕ работает: обычная функция
fun <T> List<T>.customForEach(action: (T) -> Unit) {
    for (item in this) action(item)
}

for (x in list1) {
    list2.customForEach { y ->
        // if (condition) break  // Compile error!
    }
}
```

---

### Включение функции

Для Kotlin 2.1:

```kotlin
// build.gradle.kts
kotlin {
    compilerOptions {
        freeCompilerArgs.add("-Xnon-local-break-continue")
    }
}
```

В Kotlin 2.2+ функция стабильна и флаг не нужен.

---

### Сравнение с метками

| Подход | Синтаксис | Читаемость |
|--------|-----------|------------|
| Метки | `return@label` | Сложнее |
| Non-local | `break`, `continue` | Естественнее |

---

## Answer (EN)

**Introduced in Kotlin 2.1, stable since 2.2**

**Non-local break and continue** allow using `break` and `continue` inside inline lambdas to control the enclosing loop. Previously this was impossible, requiring labels or workarounds.

---

### Syntax

```kotlin
for (item in collection) {
    collection.forEach { element ->
        if (condition) break    // exits the for loop
        if (other) continue     // jumps to next for iteration
    }
}
```

---

### Before Kotlin 2.1 (Workarounds)

```kotlin
// Using labels
outer@ for (row in matrix) {
    row.forEach { cell ->
        if (cell == target) {
            // Need to use labeled return
            return@outer  // but this is not break!
        }
    }
}

// Or using run with label
for (item in items) {
    run breaking@ {
        items.forEach {
            if (condition) return@breaking
        }
    }
}
```

---

### With Non-local Break/Continue (Kotlin 2.1+)

```kotlin
for (row in matrix) {
    row.forEach { cell ->
        if (cell == target) break      // exits for loop
        if (cell < 0) continue         // next for iteration
    }
}
```

---

### Practical Examples

**Matrix Search:**

```kotlin
fun findInMatrix(matrix: List<List<Int>>, target: Int): Pair<Int, Int>? {
    var result: Pair<Int, Int>? = null

    for ((rowIdx, row) in matrix.withIndex()) {
        row.forEachIndexed { colIdx, value ->
            if (value == target) {
                result = rowIdx to colIdx
                break  // exit outer for
            }
        }
    }

    return result
}
```

**Validation with Skipping:**

```kotlin
data class Order(val items: List<Item>)
data class Item(val name: String, val price: Double, val valid: Boolean)

fun processOrders(orders: List<Order>) {
    for (order in orders) {
        var hasInvalidItem = false

        order.items.forEach { item ->
            if (!item.valid) {
                hasInvalidItem = true
                break  // stop checking this order
            }
            if (item.price <= 0) {
                continue  // skip zero-price items
            }
            processItem(item)
        }

        if (hasInvalidItem) {
            println("Order skipped due to invalid items")
        }
    }
}
```

**Processing Nested Structures:**

```kotlin
data class Category(val name: String, val products: List<Product>)
data class Product(val id: Int, val inStock: Boolean)

fun findFirstAvailable(categories: List<Category>): Product? {
    for (category in categories) {
        category.products.forEach { product ->
            if (product.inStock) {
                return product  // return works as before
            }
        }
    }
    return null
}

fun checkAllCategories(categories: List<Category>): Boolean {
    for (category in categories) {
        var hasStock = false
        category.products.forEach { product ->
            if (product.inStock) {
                hasStock = true
                break  // found in-stock item, check next category
            }
        }
        if (!hasStock) return false
    }
    return true
}
```

---

### Limitations

Non-local break/continue only works with **inline** functions:

```kotlin
// Works: forEach is inline
for (x in list1) {
    list2.forEach { y ->
        if (condition) break  // OK
    }
}

// Does NOT work: regular function
fun <T> List<T>.customForEach(action: (T) -> Unit) {
    for (item in this) action(item)
}

for (x in list1) {
    list2.customForEach { y ->
        // if (condition) break  // Compile error!
    }
}
```

---

### Enabling the Feature

For Kotlin 2.1:

```kotlin
// build.gradle.kts
kotlin {
    compilerOptions {
        freeCompilerArgs.add("-Xnon-local-break-continue")
    }
}
```

In Kotlin 2.2+, the feature is stable and requires no flag.

---

### Comparison with Labels

| Approach | Syntax | Readability |
|----------|--------|-------------|
| Labels | `return@label` | More complex |
| Non-local | `break`, `continue` | More natural |

---

## Follow-ups

- What happens if you use break/continue in a non-inline lambda?
- Can non-local break/continue cross function boundaries?
- How does this feature interact with nested loops?

## Related Questions

- [[q-inline-function-limitations--kotlin--medium]]
- [[q-crossinline-keyword--kotlin--medium]]

## References

- https://kotlinlang.org/docs/whatsnew21.html#non-local-break-and-continue
- https://kotlinlang.org/docs/inline-functions.html
