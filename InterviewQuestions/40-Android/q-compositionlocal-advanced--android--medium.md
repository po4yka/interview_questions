---
id: android-467
title: CompositionLocal Advanced / CompositionLocal — продвинутый уровень
aliases:
- CompositionLocal — продвинутый уровень
- CompositionLocal Advanced
topic: android
subtopics:
- architecture-mvvm
- ui-compose
question_kind: android
difficulty: medium
original_language: ru
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- q-compose-core-components--android--medium
- q-compose-navigation-advanced--android--medium
- q-compose-performance-optimization--android--hard
- q-compose-remember-derived-state--android--medium
- q-compose-semantics--android--medium
- q-what-are-the-most-important-components-of-compose--android--medium
sources: []
anki_cards:
- slug: android-467-0-en
  language: en
  anki_id: 1768366347179
  synced_at: '2026-01-23T16:45:06.291658'
- slug: android-467-0-ru
  language: ru
  anki_id: 1768366347198
  synced_at: '2026-01-23T16:45:06.292471'
created: 2025-10-20
updated: 2025-10-30
tags:
- android/architecture-mvvm
- android/ui-compose
- difficulty/medium
---
# Вопрос (RU)
> Когда использовать `CompositionLocal`? Чем различаются `staticCompositionLocalOf` и `compositionLocalOf`?

# Question (EN)
> When to use `CompositionLocal`? What's the difference between `staticCompositionLocalOf` and `compositionLocalOf`?

---

## Ответ (RU)

### Назначение CompositionLocal
Передаёт контекстные данные (тема, локаль, DI-объекты) по дереву композиции без явных параметров. Применяйте для сквозных зависимостей, которые относятся к окружению и не должны обновляться слишком часто на больших поддеревьях.

**Когда использовать:**
- Тема, плотность, локаль
- Haptics, logger, imageLoader
- DI-корни (`Hilt`, `Koin`)

**Когда НЕ использовать:**
- Вместо явных параметров для бизнес-логики
- Для локальных данных с высокой частотой изменений, если можно ограничить область явными параметрами или состоянием
- Как скрытый глобальный стейт

### staticCompositionLocalOf Vs compositionLocalOf

**`compositionLocalOf` (динамический):**
- Отслеживает чтение `.current` — перекомпозируются только реальные читатели
- Подходит для значений, которые могут меняться относительно часто (scroll position, динамические флаги), при условии разумного выбора области провайдера
- Небольшие накладные расходы на каждое чтение

```kotlin
// ✅ Динамический Local для частых обновлений в ограниченной области
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
- Не отслеживает чтения — обновление инвалидирует всё поддерево провайдера
- Для редко меняющихся, широко читаемых значений (тема, локаль)
- Чтение дешевле, обновления дороже

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

### Производительность И Границы Инвалидации

**Динамический Local:**
- Инвалидирует только реальных читателей `.current`
- Хорош для значений, которые могут обновляться часто, при условии, что область действия провайдера не чрезмерно широка

**Статический Local:**
- Инвалидирует всё поддерево `CompositionLocalProvider`
- Используйте для значений, которые меняются редко относительно размера поддерева
- Размещайте провайдеры ближе к потребителям, чтобы ограничить область массовых рекомпозиций

```kotlin
// ❌ Провайдер слишком высоко для частых обновлений
@Composable
fun App(scrollY: Int) {
    CompositionLocalProvider(LocalScrollInfo provides scrollY) {
        // При изменении scrollY перекомпозируется всё дерево
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
        FeedList()  // только FeedList зависит от LocalScrollInfo и перекомпозируется
    }
    BottomNav()
}
```

### Безопасные Дефолты

```kotlin
// ❌ Валидный дефолт скрывает отсутствие провайдера
val LocalLogger = staticCompositionLocalOf { NoOpLogger }

// ✅ Крэш сразу показывает проблему
val LocalLogger = staticCompositionLocalOf<Logger> {
    error("Logger not provided")
}
```

### Неизменяемость И Стабильность

```kotlin
// ❌ Мутация невидима для Compose
data class Theme(var primaryColor: Color)
val theme = LocalTheme.current
theme.primaryColor = Color.Red  // не вызовет рекомпозицию

// ✅ Обновление через копирование
val updatedTheme = LocalTheme.current.copy(primaryColor = Color.Red)
CompositionLocalProvider(LocalTheme provides updatedTheme) { /* ... */ }
```

### Типичные Ошибки

```kotlin
// ⚠️ Потенциально устаревшее значение
@Composable
fun Screen() {
    val theme = LocalTheme.current
    LaunchedEffect(Unit) {
        delay(1000)
        // theme может быть устаревшим, если LocalTheme изменился за это время
        logger.log(theme.primaryColor)
    }
}

// ✅ Чтение Local в актуальном контексте внутри побочного эффекта
@Composable
fun Screen() {
    LaunchedEffect(LocalTheme.current) {
        val theme = LocalTheme.current  // значение соответствует текущему CompositionLocal
        logger.log(theme.primaryColor)
    }
}
```

## Answer (EN)

### Purpose of CompositionLocal
Passes contextual data (theme, locale, DI objects) through the composition tree without explicit parameters. Use for cross-cutting dependencies that are environmental and should not be driving frequent updates over large subtrees.

**When to use:**
- Theme, density, locale
- Haptics, logger, imageLoader
- DI roots (`Hilt`, `Koin`)

**When NOT to use:**
- Instead of explicit parameters for business logic
- For highly localized data with very frequent changes when it could be scoped better via parameters or state
- As hidden global state

### staticCompositionLocalOf Vs compositionLocalOf

**`compositionLocalOf` (dynamic):**
- Tracks `.current` reads — only actual readers recompose
- Suitable for values that may change relatively often (scroll position, dynamic flags), given a reasonable provider scope
- Small per-read overhead

```kotlin
// ✅ Dynamic Local for frequent updates within a limited scope
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
- No read tracking — updates invalidate the entire provider subtree
- For rarely changing, widely read values (theme, locale)
- Cheaper reads, more expensive updates

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
- Good for values that can update frequently, as long as the provider scope is not unnecessarily wide

**Static Local:**
- Invalidates the entire `CompositionLocalProvider` subtree
- Use for values that change infrequently relative to the size of the affected subtree
- Place providers close to consumers to limit large recomposition areas

```kotlin
// ❌ Provider too high for frequent updates
@Composable
fun App(scrollY: Int) {
    CompositionLocalProvider(LocalScrollInfo provides scrollY) {
        // When scrollY changes, the entire tree recomposes
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
        FeedList()  // only FeedList depends on LocalScrollInfo and recomposes
    }
    BottomNav()
}
```

### Safe Defaults

```kotlin
// ❌ Valid default hides missing provider
val LocalLogger = staticCompositionLocalOf { NoOpLogger }

// ✅ Crash immediately shows missing provider
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
val updatedTheme = LocalTheme.current.copy(primaryColor = Color.Red)
CompositionLocalProvider(LocalTheme provides updatedTheme) { /* ... */ }
```

### Common Pitfalls

```kotlin
// ⚠️ Potentially stale value
@Composable
fun Screen() {
    val theme = LocalTheme.current
    LaunchedEffect(Unit) {
        delay(1000)
        // theme may be stale if LocalTheme changed during this time
        logger.log(theme.primaryColor)
    }
}

// ✅ Read Local in an up-to-date context inside the effect
@Composable
fun Screen() {
    LaunchedEffect(LocalTheme.current) {
        val theme = LocalTheme.current  // value consistent with current CompositionLocal
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
