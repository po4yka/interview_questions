---
id: android-307
title: CompositionLocal in Compose / CompositionLocal в Compose
aliases: [CompositionLocal in Compose, CompositionLocal в Compose]
topic: android
subtopics:
  - ui-compose
  - ui-state
question_kind: android
difficulty: hard
original_language: ru
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - q-compose-performance-optimization--android--hard
  - q-compose-remember-derived-state--android--medium
  - q-compositionlocal-advanced--android--medium
created: 2025-10-15
updated: 2025-10-30
tags: [android/ui-compose, android/ui-state, difficulty/hard]
sources:
  - https://developer.android.com/jetpack/compose/compositionlocal
date created: Thursday, October 30th 2025, 11:56:59 am
date modified: Sunday, November 2nd 2025, 4:17:20 pm
---

# Вопрос (RU)
> Что такое CompositionLocal в Jetpack Compose и когда его использовать?

# Question (EN)
> What is CompositionLocal in Jetpack Compose and when should it be used?

---

## Ответ (RU)

CompositionLocal — механизм передачи данных через дерево композиций без явного пробрасывания параметров. Решает проблему "prop drilling" для окружающих зависимостей (тема, локаль, imageLoader).

### Назначение

**Используй для**:
- Окружающих зависимостей: theme, locale, density, haptics
- Cross-cutting concerns, избегающих многоуровневый prop drilling

**Не используй для**:
- Бизнес-логики и репозиториев (используй DI: Hilt/Koin)
- Локальных зависимостей с явным API
- Часто меняющихся данных на верхних уровнях

### Dynamic Vs Static

**compositionLocalOf** (динамический):
```kotlin
val LocalScrollY = compositionLocalOf { 0 }
// ✅ Отслеживает читателей — рекомпозирует только их
// ✅ Для часто меняющихся значений
// ❌ Небольшой overhead на каждое чтение
```

**staticCompositionLocalOf** (статический):
```kotlin
val LocalTheme = staticCompositionLocalOf<Theme> {
    error("No theme provided")
}
// ✅ Дешёвое чтение — нет отслеживания
// ✅ Для редко меняющихся, широко используемых значений
// ❌ Обновление инвалидирует всё поддерево Provider
```

**Правило выбора**: часто меняется + узкая рекомпозиция → `compositionLocalOf`; редко меняется + широкое использование → `staticCompositionLocalOf`.

### Границы Инвалидации

- **Dynamic**: инвалидирует только читателей
- **Static**: инвалидирует всё поддерево от Provider
- **Оптимизация**: размещай Provider близко к потребителям при частых обновлениях

### Безопасные Дефолты

```kotlin
// ✅ Падаем явно — обнаруживаем ошибку сразу
val LocalAuth = compositionLocalOf<Auth> {
    error("No Auth provided")
}

// ❌ Молчаливый null может скрыть ошибку
val LocalAuth = compositionLocalOf<Auth?> { null }
```

### Типичный Паттерн

```kotlin
// Статический контекст приложения
data class AppEnv(
    val locale: Locale,
    val haptics: Haptics,
    val imageLoader: ImageLoader
)

val LocalAppEnv = staticCompositionLocalOf<AppEnv> {
    error("No AppEnv provided")
}

@Composable
fun App(env: AppEnv) {
    CompositionLocalProvider(LocalAppEnv provides env) {
        AppContent()
    }
}

@Composable
fun SomeScreen() {
    val env = LocalAppEnv.current
    // Используй env.locale, env.haptics...
}
```

### Анти-паттерны

- Чтение Local вне композиции (в долгоживущих lambda)
- Использование для бизнес-логики вместо DI
- Provider слишком высоко для часто меняющихся значений
- Nullable дефолты вместо явных ошибок

## Answer (EN)

CompositionLocal is a mechanism for passing data through the composition tree without explicit parameter passing. Solves "prop drilling" for ambient dependencies (theme, locale, imageLoader).

### Purpose

**Use for**:
- Ambient dependencies: theme, locale, density, haptics
- Cross-cutting concerns avoiding multi-level prop drilling

**Don't use for**:
- Business logic and repositories (use DI: Hilt/Koin)
- Local dependencies with explicit API
- Frequently changing data at high levels

### Dynamic Vs Static

**compositionLocalOf** (dynamic):
```kotlin
val LocalScrollY = compositionLocalOf { 0 }
// ✅ Tracks readers — recomposes only them
// ✅ For frequently changing values
// ❌ Small overhead per read
```

**staticCompositionLocalOf** (static):
```kotlin
val LocalTheme = staticCompositionLocalOf<Theme> {
    error("No theme provided")
}
// ✅ Cheap reads — no tracking
// ✅ For rarely changing, widely used values
// ❌ Update invalidates entire Provider subtree
```

**Selection rule**: changes often + narrow recomposition → `compositionLocalOf`; rarely changes + wide readership → `staticCompositionLocalOf`.

### Invalidation Boundaries

- **Dynamic**: invalidates only readers
- **Static**: invalidates entire subtree from Provider
- **Optimization**: place Provider close to consumers for frequent updates

### Safe Defaults

```kotlin
// ✅ Fail explicitly — detect error immediately
val LocalAuth = compositionLocalOf<Auth> {
    error("No Auth provided")
}

// ❌ Silent null can hide bugs
val LocalAuth = compositionLocalOf<Auth?> { null }
```

### Typical Pattern

```kotlin
// Static application context
data class AppEnv(
    val locale: Locale,
    val haptics: Haptics,
    val imageLoader: ImageLoader
)

val LocalAppEnv = staticCompositionLocalOf<AppEnv> {
    error("No AppEnv provided")
}

@Composable
fun App(env: AppEnv) {
    CompositionLocalProvider(LocalAppEnv provides env) {
        AppContent()
    }
}

@Composable
fun SomeScreen() {
    val env = LocalAppEnv.current
    // Use env.locale, env.haptics...
}
```

### Anti-patterns

- Reading Local outside composition (in long-lived lambdas)
- Using for business logic instead of DI
- Provider too high for frequently changing values
- Nullable defaults instead of explicit errors

---

## Follow-ups

- How to test components that depend on CompositionLocal?
- When should you use parameters instead of CompositionLocal?
- How to scope providers across feature modules?
- How do nested CompositionLocalProviders affect performance?
- How to migrate from manual prop drilling to CompositionLocal?

## References

- [[c-compose-state]]
- [[c-dependency-injection]]
- [[c-recomposition]]
- [CompositionLocal (Official Docs)](https://developer.android.com/jetpack/compose/compositionlocal)
- [Compose Mental Model](https://developer.android.com/develop/ui/compose/mental-model)

## Related Questions

### Prerequisites
- [[q-compose-remember-derived-state--android--medium]] — State management fundamentals

### Related
- [[q-compositionlocal-advanced--android--medium]] — Advanced CompositionLocal patterns

### Advanced
- [[q-compose-performance-optimization--android--hard]] — Performance optimization strategies
