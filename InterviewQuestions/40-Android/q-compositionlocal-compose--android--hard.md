---
id: 20251021-120500
title: CompositionLocal in Compose / CompositionLocal в Compose
aliases: ["CompositionLocal in Compose", "CompositionLocal в Compose"]
topic: android
subtopics: [ui-compose, ui-state]
question_kind: android
difficulty: hard
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-compose-performance-optimization--android--hard, q-compose-remember-derived-state--android--medium, q-compositionlocal-advanced--android--medium]
created: 2025-10-15
updated: 2025-10-27
tags: [android/ui-compose, android/ui-state, difficulty/hard]
sources: ["https://developer.android.com/jetpack/compose/compositionlocal"]
---

# Вопрос (RU)
> Что такое CompositionLocal в Jetpack Compose и когда его использовать?

# Question (EN)
> What is CompositionLocal in Jetpack Compose and when should it be used?

---

## Ответ (RU)

CompositionLocal — механизм передачи данных через дерево композиций без явного пробрасывания параметров. Решает проблему "prop drilling" для окружающих зависимостей (тема, локаль, imageLoader).

### Назначение
- Окружающие зависимости: theme, locale, density, haptics
- Альтернатива явным параметрам для cross-cutting concerns
- НЕ замена DI: бизнес-логику и репозитории передавать через DI

### Параметры vs CompositionLocal
- **Параметры**: локальные зависимости, частые изменения, ясность API
- **CompositionLocal**: сквозные зависимости, редкие изменения, окружение

### Dynamic vs Static

**compositionLocalOf** (динамический):
```kotlin
val LocalScrollY = compositionLocalOf { 0 }
// ✅ Отслеживает читателей — рекомпозирует только их
// ✅ Для часто меняющихся значений
// ❌ Небольшой overhead на каждое чтение
```

**staticCompositionLocalOf** (статический):
```kotlin
val LocalTheme = staticCompositionLocalOf<Theme> { error("No theme") }
// ✅ Дешёвое чтение — нет отслеживания
// ✅ Для редко меняющихся, широко используемых значений
// ❌ Обновление инвалидирует всё поддерево Provider
```

**Правило**: часто меняется + узкая рекомпозиция → `compositionLocalOf`; редко меняется + широкое использование → `staticCompositionLocalOf`.

### Границы инвалидации
- Граница — `CompositionLocalProvider`
- Dynamic: инвалидирует только читателей
- Static: инвалидирует всё поддерево
- Размещать Provider близко к потребителям при частых обновлениях

### Безопасные дефолты
```kotlin
// ✅ Падаем явно
val LocalAuth = compositionLocalOf<Auth> { error("No Auth") }

// ❌ Молчаливый null может скрыть ошибку
val LocalAuth = compositionLocalOf<Auth?> { null }
```

### Паттерны
```kotlin
// Статический контекст приложения
data class AppEnv(val locale: Locale, val haptics: Haptics)
val LocalAppEnv = staticCompositionLocalOf<AppEnv> {
    error("No AppEnv")
}

@Composable
fun App(env: AppEnv) {
    CompositionLocalProvider(LocalAppEnv provides env) {
        AppContent()
    }
}
```

### Типичные ошибки
- Чтение Local вне композиции (долгоживущие lambda)
- Использование для бизнес-логики вместо DI
- Provider слишком высоко для часто меняющихся значений

## Answer (EN)

CompositionLocal is a mechanism for passing data through the composition tree without explicit parameter passing. Solves "prop drilling" for ambient dependencies (theme, locale, imageLoader).

### Purpose
- Ambient dependencies: theme, locale, density, haptics
- Alternative to explicit parameters for cross-cutting concerns
- NOT a DI replacement: business logic and repositories go through DI

### Parameters vs CompositionLocal
- **Parameters**: local dependencies, frequent changes, API clarity
- **CompositionLocal**: cross-cutting dependencies, rare changes, environment

### Dynamic vs Static

**compositionLocalOf** (dynamic):
```kotlin
val LocalScrollY = compositionLocalOf { 0 }
// ✅ Tracks readers — recomposes only them
// ✅ For frequently changing values
// ❌ Small overhead per read
```

**staticCompositionLocalOf** (static):
```kotlin
val LocalTheme = staticCompositionLocalOf<Theme> { error("No theme") }
// ✅ Cheap reads — no tracking
// ✅ For rarely changing, widely used values
// ❌ Update invalidates entire Provider subtree
```

**Rule**: changes often + narrow recomposition → `compositionLocalOf`; rarely changes + wide readership → `staticCompositionLocalOf`.

### Invalidation Boundaries
- Boundary is `CompositionLocalProvider`
- Dynamic: invalidates only readers
- Static: invalidates entire subtree
- Place Provider close to consumers for frequent updates

### Safe Defaults
```kotlin
// ✅ Fail explicitly
val LocalAuth = compositionLocalOf<Auth> { error("No Auth") }

// ❌ Silent null can hide bugs
val LocalAuth = compositionLocalOf<Auth?> { null }
```

### Patterns
```kotlin
// Static application context
data class AppEnv(val locale: Locale, val haptics: Haptics)
val LocalAppEnv = staticCompositionLocalOf<AppEnv> {
    error("No AppEnv")
}

@Composable
fun App(env: AppEnv) {
    CompositionLocalProvider(LocalAppEnv provides env) {
        AppContent()
    }
}
```

### Common Pitfalls
- Reading Local outside composition (long-lived lambdas)
- Using for business logic instead of DI
- Provider too high for frequently changing values

---

## Follow-ups
- How to test components that depend on CompositionLocal?
- When should you use parameters instead of CompositionLocal?
- How to scope providers across feature modules?
- How to debug recomposition issues caused by Local updates?
- What are the performance implications of nested CompositionLocalProviders?

## References
- [CompositionLocal (Official Docs)](https://developer.android.com/jetpack/compose/compositionlocal)
- [Compose Mental Model](https://developer.android.com/develop/ui/compose/mental-model)
- [[c-dependency-injection]]

## Related Questions

### Prerequisites
- [[q-compose-remember-derived-state--android--medium]] — State management fundamentals
- [[q-compose-recomposition--android--medium]] — Understanding recomposition

### Related
- [[q-compositionlocal-advanced--android--medium]] — Advanced CompositionLocal patterns
- [[q-compose-state-hoisting--android--medium]] — State management alternatives

### Advanced
- [[q-compose-performance-optimization--android--hard]] — Performance optimization strategies
- [[q-compose-stability--android--hard]] — Stability and skippability
