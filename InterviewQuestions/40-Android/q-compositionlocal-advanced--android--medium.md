---
id: 20251020-211200
title: CompositionLocal Advanced / CompositionLocal — продвинутый уровень
aliases: ["CompositionLocal Advanced", "CompositionLocal — продвинутый уровень"]
topic: android
subtopics: [ui-compose, architecture-mvvm]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-compose-performance-optimization--android--hard, q-compose-remember-derived-state--android--medium, q-compose-semantics--android--medium]
sources: []
created: 2025-10-20
updated: 2025-10-30
tags: [android/ui-compose, android/architecture-mvvm, difficulty/medium]
---

# Вопрос (RU)
> Когда использовать CompositionLocal? Чем различаются staticCompositionLocalOf и compositionLocalOf?

# Question (EN)
> When to use CompositionLocal? What's the difference between staticCompositionLocalOf and compositionLocalOf?

---

## Ответ (RU)

### Назначение CompositionLocal
Передаёт контекстные данные (тема, локаль, DI-объекты) по дереву композиции без явных параметров. Применяйте для сквозных зависимостей, которые относятся к окружению и редко меняются.

**Когда использовать:**
- Тема, плотность, локаль
- Haptics, logger, imageLoader
- DI-корни (Hilt, Koin)

**Когда НЕ использовать:**
- Вместо явных параметров для бизнес-логики
- Для часто меняющихся локальных данных
- Как скрытый глобальный стейт

### staticCompositionLocalOf vs compositionLocalOf

**`compositionLocalOf` (динамический):**
- Отслеживает чтение `.current` — перекомпозируются только читатели
- Для часто меняющихся значений (scroll position, dynamic flags)
- Небольшие затраты на каждое чтение

```kotlin
// ✅ Динамический Local для частых обновлений
val LocalScrollInfo = compositionLocalOf { 0 }

@Composable
fun Screen(scrollY: Int) {
    CompositionLocalProvider(LocalScrollInfo provides scrollY) {
        Header()         // не читает → не перекомпозируется
        StickyToolbar()  // читает .current → перекомпозируется
    }
}
```

**`staticCompositionLocalOf` (статический):**
- Без отслеживания — обновление инвалидирует всё поддерево
- Для редко меняющихся, широко читаемых значений (тема, локаль)
- Дешевле чтение, дороже обновления

```kotlin
// ✅ Статический Local для редких обновлений
data class AppEnv(val locale: Locale, val haptics: Haptics)
val LocalAppEnv = staticCompositionLocalOf<AppEnv> {
    error("No AppEnv")
}

@Composable
fun App(env: AppEnv, content: @Composable () -> Unit) {
    CompositionLocalProvider(LocalAppEnv provides env) {
        content()
    }
}
```

### Производительность и границы инвалидации

**Динамический Local:**
- Инвалидирует только реальных читателей `.current`
- Идеален для значений, меняющихся чаще 1 раза в минуту

**Статический Local:**
- Инвалидирует всё поддерево `CompositionLocalProvider`
- Используйте для значений, меняющихся реже 1 раза в минуту
- Размещайте провайдеры близко к потребителям

```kotlin
// ❌ Провайдер слишком высоко для частых обновлений
@Composable
fun App() {
    CompositionLocalProvider(LocalScrollInfo provides scrollY) {
        // Всё дерево перекомпозируется
        Navigation()
        Settings()
        Profile()
    }
}

// ✅ Тонкий провайдер — только нужное поддерево
@Composable
fun FeedScreen(scrollY: Int) {
    Header()
    CompositionLocalProvider(LocalScrollInfo provides scrollY) {
        FeedList()  // только FeedList перекомпозируется
    }
    BottomNav()
}
```

### Безопасные дефолты

```kotlin
// ❌ Валидный дефолт скрывает отсутствие провайдера
val LocalLogger = staticCompositionLocalOf { NoOpLogger }

// ✅ Крэш сразу показывает проблему
val LocalLogger = staticCompositionLocalOf<Logger> {
    error("Logger not provided")
}
```

### Неизменяемость и стабильность

```kotlin
// ❌ Мутация невидима для Compose
data class Theme(var primaryColor: Color)
val theme = LocalTheme.current
theme.primaryColor = Color.Red  // не вызовет рекомпозицию

// ✅ Обновление через копирование
val theme = LocalTheme.current.copy(primaryColor = Color.Red)
CompositionLocalProvider(LocalTheme provides theme) { ... }
```

### Типичные ошибки

```kotlin
// ❌ Чтение Local вне композиции
@Composable
fun Screen() {
    val theme = LocalTheme.current
    LaunchedEffect(Unit) {
        delay(1000)
        // theme может быть устаревшим
        logger.log(theme.primaryColor)
    }
}

// ✅ Читайте Local внутри композиции
@Composable
fun Screen() {
    LaunchedEffect(Unit) {
        val theme = LocalTheme.current  // актуальное значение
        logger.log(theme.primaryColor)
    }
}
```

## Answer (EN)

### Purpose of CompositionLocal
Passes contextual data (theme, locale, DI objects) through composition tree without explicit parameters. Use for cross-cutting dependencies that are environmental and change rarely.

**When to use:**
- Theme, density, locale
- Haptics, logger, imageLoader
- DI roots (Hilt, Koin)

**When NOT to use:**
- Instead of explicit parameters for business logic
- For frequently changing local data
- As hidden global state

### staticCompositionLocalOf vs compositionLocalOf

**`compositionLocalOf` (dynamic):**
- Tracks `.current` reads — only readers recompose
- For frequently changing values (scroll position, dynamic flags)
- Small per-read overhead

```kotlin
// ✅ Dynamic Local for frequent updates
val LocalScrollInfo = compositionLocalOf { 0 }

@Composable
fun Screen(scrollY: Int) {
    CompositionLocalProvider(LocalScrollInfo provides scrollY) {
        Header()         // doesn't read → no recomposition
        StickyToolbar()  // reads .current → recomposes
    }
}
```

**`staticCompositionLocalOf` (static):**
- No read tracking — update invalidates entire subtree
- For rarely changing, widely read values (theme, locale)
- Cheaper reads, expensive updates

```kotlin
// ✅ Static Local for rare updates
data class AppEnv(val locale: Locale, val haptics: Haptics)
val LocalAppEnv = staticCompositionLocalOf<AppEnv> {
    error("No AppEnv")
}

@Composable
fun App(env: AppEnv, content: @Composable () -> Unit) {
    CompositionLocalProvider(LocalAppEnv provides env) {
        content()
    }
}
```

### Performance and Invalidation Boundaries

**Dynamic Local:**
- Invalidates only actual `.current` readers
- Ideal for values changing more than once per minute

**Static Local:**
- Invalidates entire `CompositionLocalProvider` subtree
- Use for values changing less than once per minute
- Place providers close to consumers

```kotlin
// ❌ Provider too high for frequent updates
@Composable
fun App() {
    CompositionLocalProvider(LocalScrollInfo provides scrollY) {
        // Entire tree recomposes
        Navigation()
        Settings()
        Profile()
    }
}

// ✅ Thin provider — only needed subtree
@Composable
fun FeedScreen(scrollY: Int) {
    Header()
    CompositionLocalProvider(LocalScrollInfo provides scrollY) {
        FeedList()  // only FeedList recomposes
    }
    BottomNav()
}
```

### Safe Defaults

```kotlin
// ❌ Valid default hides missing provider
val LocalLogger = staticCompositionLocalOf { NoOpLogger }

// ✅ Crash immediately shows problem
val LocalLogger = staticCompositionLocalOf<Logger> {
    error("Logger not provided")
}
```

### Immutability and Stability

```kotlin
// ❌ Mutation invisible to Compose
data class Theme(var primaryColor: Color)
val theme = LocalTheme.current
theme.primaryColor = Color.Red  // won't trigger recomposition

// ✅ Update via copying
val theme = LocalTheme.current.copy(primaryColor = Color.Red)
CompositionLocalProvider(LocalTheme provides theme) { ... }
```

### Common Pitfalls

```kotlin
// ❌ Reading Local outside composition
@Composable
fun Screen() {
    val theme = LocalTheme.current
    LaunchedEffect(Unit) {
        delay(1000)
        // theme may be stale
        logger.log(theme.primaryColor)
    }
}

// ✅ Read Local inside composition
@Composable
fun Screen() {
    LaunchedEffect(Unit) {
        val theme = LocalTheme.current  // current value
        logger.log(theme.primaryColor)
    }
}
```

---

## Follow-ups
- How to scope CompositionLocal providers in multi-module apps?
- How does CompositionLocal interact with navigation and back stack?
- Can CompositionLocal safely carry mutable state objects?
- How to test code that depends on CompositionLocal values?
- What's the performance cost of nested CompositionLocalProvider blocks?

## References
- [CompositionLocal Official Docs](https://developer.android.com/jetpack/compose/compositionlocal)
- [Compose Mental Model](https://developer.android.com/develop/ui/compose/mental-model)
- [[c-dependency-injection]]
- [[c-compose-state]]

## Related Questions

### Prerequisites
- [[q-compose-semantics--android--medium]] — Semantic properties in Compose
- Basic Compose state and recomposition

### Related
- [[q-compose-remember-derived-state--android--medium]] — State derivation patterns
- CompositionLocal lifecycle and side effects

### Advanced
- [[q-compose-performance-optimization--android--hard]] — Performance tuning
- Custom CompositionLocal implementations for complex DI scenarios
