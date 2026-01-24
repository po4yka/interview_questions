---
id: kotlin-249
title: Compose Compiler and Stability / Компилятор Compose и стабильность
aliases:
- Compose Stability
- Compose Compiler
- Стабильность в Compose
topic: kotlin
subtopics:
- compose
- compiler
- performance
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-compose
- c-performance
created: 2026-01-23
updated: 2026-01-23
tags:
- kotlin
- compose
- stability
- recomposition
- difficulty/hard
anki_cards:
- slug: kotlin-249-0-en
  language: en
  anki_id: 1769170315646
  synced_at: '2026-01-23T17:03:50.940056'
- slug: kotlin-249-0-ru
  language: ru
  anki_id: 1769170315671
  synced_at: '2026-01-23T17:03:50.942046'
---
# Вопрос (RU)
> Что такое стабильность в Jetpack Compose? Как работают аннотации @Stable и @Immutable?

# Question (EN)
> What is stability in Jetpack Compose? How do @Stable and @Immutable annotations work?

---

## Ответ (RU)

**Стабильность определяет, может ли Compose пропустить рекомпозицию:**
Compose сравнивает параметры composable-функций. Если все параметры "стабильны" и не изменились, рекомпозиция пропускается (skippable).

**Типы стабильности:**

| Тип | Описание | Пример |
|-----|----------|--------|
| **Immutable** | Свойства никогда не меняются | `String`, `Int`, data class с val |
| **Stable** | Изменения уведомляют Compose | `MutableState<T>` |
| **Unstable** | Compose не может отследить изменения | `List<T>`, классы из внешних модулей |

**Правила стабильности:**
```kotlin
// СТАБИЛЬНЫЙ: все свойства val примитивы/стабильные типы
data class User(
    val id: Int,
    val name: String
)

// НЕСТАБИЛЬНЫЙ: List считается нестабильным
data class UserList(
    val users: List<User>  // List - unstable!
)

// ИСПРАВЛЕНИЕ: явная аннотация
@Immutable
data class UserList(
    val users: List<User>
)
```

**Аннотации:**

**@Immutable** - обещание, что объект никогда не изменится:
```kotlin
@Immutable
data class Config(
    val apiUrl: String,
    val timeout: Int
)
```

**@Stable** - обещание, что Compose будет уведомлён об изменениях:
```kotlin
@Stable
class Counter {
    var value by mutableStateOf(0)
}
```

**Проверка стабильности:**
```bash
# Включить отчёты компилятора
kotlinOptions {
    freeCompilerArgs += listOf(
        "-P",
        "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=${buildDir}/compose_reports"
    )
}
```

**Распространённые проблемы:**
```kotlin
// ПРОБЛЕМА: лямбда создаётся при каждой рекомпозиции
@Composable
fun Parent() {
    Child(onClick = { doSomething() })  // новая лямбда каждый раз
}

// РЕШЕНИЕ: remember или вынести в переменную
@Composable
fun Parent() {
    val onClick = remember { { doSomething() } }
    Child(onClick = onClick)
}
```

## Answer (EN)

**Stability determines whether Compose can skip recomposition:**
Compose compares composable function parameters. If all parameters are "stable" and unchanged, recomposition is skipped (skippable).

**Stability Types:**

| Type | Description | Example |
|------|-------------|---------|
| **Immutable** | Properties never change | `String`, `Int`, data class with val |
| **Stable** | Changes notify Compose | `MutableState<T>` |
| **Unstable** | Compose can't track changes | `List<T>`, classes from external modules |

**Stability Rules:**
```kotlin
// STABLE: all properties are val primitives/stable types
data class User(
    val id: Int,
    val name: String
)

// UNSTABLE: List is considered unstable
data class UserList(
    val users: List<User>  // List - unstable!
)

// FIX: explicit annotation
@Immutable
data class UserList(
    val users: List<User>
)
```

**Annotations:**

**@Immutable** - promise that object will never change:
```kotlin
@Immutable
data class Config(
    val apiUrl: String,
    val timeout: Int
)
```

**@Stable** - promise that Compose will be notified of changes:
```kotlin
@Stable
class Counter {
    var value by mutableStateOf(0)
}
```

**Checking Stability:**
```bash
# Enable compiler reports
kotlinOptions {
    freeCompilerArgs += listOf(
        "-P",
        "plugin:androidx.compose.compiler.plugins.kotlin:reportsDestination=${buildDir}/compose_reports"
    )
}
```

**Common Issues:**
```kotlin
// PROBLEM: lambda created on every recomposition
@Composable
fun Parent() {
    Child(onClick = { doSomething() })  // new lambda every time
}

// SOLUTION: remember or extract to variable
@Composable
fun Parent() {
    val onClick = remember { { doSomething() } }
    Child(onClick = onClick)
}
```

---

## Follow-ups

- How do you read Compose compiler stability reports?
- What is the difference between @Stable and @Immutable?
- How does strong skipping mode affect stability requirements?
