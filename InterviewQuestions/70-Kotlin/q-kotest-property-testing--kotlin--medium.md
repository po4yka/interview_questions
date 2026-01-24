---
id: kotlin-254
title: Kotest and Property-Based Testing / Kotest и property-based тестирование
aliases:
- Kotest
- Property Based Testing
- Kotest и property-based тестирование
topic: kotlin
subtopics:
- testing
- kotest
- property-testing
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-kotlin
- c-testing
created: 2026-01-23
updated: 2026-01-23
tags:
- kotlin
- kotest
- testing
- property-based
- difficulty/medium
anki_cards:
- slug: kotlin-254-0-en
  language: en
  anki_id: 1769170334196
  synced_at: '2026-01-23T17:03:51.347622'
- slug: kotlin-254-0-ru
  language: ru
  anki_id: 1769170334221
  synced_at: '2026-01-23T17:03:51.349123'
---
# Вопрос (RU)
> Что такое Kotest? Чем property-based тестирование отличается от обычных unit тестов?

# Question (EN)
> What is Kotest? How does property-based testing differ from regular unit tests?

---

## Ответ (RU)

**Kotest** - Kotlin-native тестовый фреймворк с множеством стилей написания тестов и встроенной поддержкой property-based testing.

**Стили тестов Kotest:**
```kotlin
// StringSpec - простой стиль
class MyTest : StringSpec({
    "string length should be correct" {
        "hello".length shouldBe 5
    }
})

// BehaviorSpec - BDD стиль
class UserTest : BehaviorSpec({
    Given("a user") {
        val user = User("John")
        When("name is accessed") {
            Then("it should return the name") {
                user.name shouldBe "John"
            }
        }
    }
})

// FunSpec - похож на JUnit
class MathTest : FunSpec({
    test("addition works") {
        1 + 1 shouldBe 2
    }
})
```

**Property-Based Testing:**
Вместо конкретных примеров проверяем свойства, которые должны быть истинны для ВСЕХ входных данных.

```kotlin
class PropertyTest : StringSpec({
    "string reverse twice returns original" {
        checkAll<String> { str ->
            str.reversed().reversed() shouldBe str
        }
    }

    "list sort is idempotent" {
        checkAll<List<Int>> { list ->
            list.sorted().sorted() shouldBe list.sorted()
        }
    }

    // Генератор с ограничениями
    "positive numbers stay positive after abs" {
        checkAll(Arb.positiveInt()) { n ->
            abs(n) shouldBe n
        }
    }
})
```

**Пользовательские генераторы:**
```kotlin
// Генератор для доменных объектов
val userArb = arbitrary {
    User(
        name = Arb.string(1..50).bind(),
        age = Arb.int(18..100).bind(),
        email = Arb.email().bind()
    )
}

class UserPropertyTest : StringSpec({
    "user validation" {
        checkAll(userArb) { user ->
            user.isValid() shouldBe true
        }
    }
})
```

**Сравнение:**

| Аспект | Unit Tests | Property Tests |
|--------|------------|----------------|
| Примеры | Конкретные | Генерируются |
| Покрытие | Выбранные случаи | Тысячи случаев |
| Edge cases | Вручную | Автоматически |
| Читаемость | Высокая | Средняя |

**Когда использовать Property-Based:**
- Математические функции
- Сериализация/десериализация
- Инварианты данных
- Парсеры

## Answer (EN)

**Kotest** - Kotlin-native testing framework with multiple test styles and built-in property-based testing support.

**Kotest Test Styles:**
```kotlin
// StringSpec - simple style
class MyTest : StringSpec({
    "string length should be correct" {
        "hello".length shouldBe 5
    }
})

// BehaviorSpec - BDD style
class UserTest : BehaviorSpec({
    Given("a user") {
        val user = User("John")
        When("name is accessed") {
            Then("it should return the name") {
                user.name shouldBe "John"
            }
        }
    }
})

// FunSpec - similar to JUnit
class MathTest : FunSpec({
    test("addition works") {
        1 + 1 shouldBe 2
    }
})
```

**Property-Based Testing:**
Instead of specific examples, verify properties that should hold for ALL inputs.

```kotlin
class PropertyTest : StringSpec({
    "string reverse twice returns original" {
        checkAll<String> { str ->
            str.reversed().reversed() shouldBe str
        }
    }

    "list sort is idempotent" {
        checkAll<List<Int>> { list ->
            list.sorted().sorted() shouldBe list.sorted()
        }
    }

    // Generator with constraints
    "positive numbers stay positive after abs" {
        checkAll(Arb.positiveInt()) { n ->
            abs(n) shouldBe n
        }
    }
})
```

**Custom Generators:**
```kotlin
// Generator for domain objects
val userArb = arbitrary {
    User(
        name = Arb.string(1..50).bind(),
        age = Arb.int(18..100).bind(),
        email = Arb.email().bind()
    )
}

class UserPropertyTest : StringSpec({
    "user validation" {
        checkAll(userArb) { user ->
            user.isValid() shouldBe true
        }
    }
})
```

**Comparison:**

| Aspect | Unit Tests | Property Tests |
|--------|------------|----------------|
| Examples | Specific | Generated |
| Coverage | Selected cases | Thousands of cases |
| Edge cases | Manual | Automatic |
| Readability | High | Medium |

**When to Use Property-Based:**
- Mathematical functions
- Serialization/deserialization
- Data invariants
- Parsers

---

## Follow-ups

- How do you debug a failing property test?
- What is shrinking in property-based testing?
- How do you integrate Kotest with existing JUnit tests?
