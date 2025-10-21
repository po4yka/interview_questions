---
id: 20251021-120500
title: "CompositionLocal in Compose / CompositionLocal в Compose"
aliases: [CompositionLocal in Compose, CompositionLocal в Compose]
topic: android
subtopics: [ui-compose, ui-state]
question_kind: android
difficulty: hard
original_language: ru
language_tags: [ru, en]
status: reviewed
moc: moc-android
related: [q-compositionlocal-advanced--jetpack-compose--medium, q-compose-remember-derived-state--jetpack-compose--medium, q-compose-performance-optimization--android--hard]
created: 2025-10-15
updated: 2025-10-21
tags: [android/ui-compose, android/ui-state, compose, compositionlocal, ui-context, best-practices, difficulty/hard]
source: https://developer.android.com/jetpack/compose/compositionlocal
source_note: Official docs on CompositionLocal
---
# Вопрос (RU)
> Что такое CompositionLocal в Jetpack Compose, когда использовать его вместо параметров, и чем отличаются `compositionLocalOf` и `staticCompositionLocalOf` с точки зрения рекомпозиции и производительности?

# Question (EN)
> What is CompositionLocal in Jetpack Compose, when should you use it instead of parameters, and what are the differences between `compositionLocalOf` and `staticCompositionLocalOf` in terms of recomposition and performance?

---

## Ответ (RU)

### Назначение
- Локальный «контекст» для поддерева: тема, локаль, плотность, хаптика, DI‑объекты UI‑уровня
- Избавляет от «прокидывания» параметров через много уровней, когда зависимость действительно относится к окружению
- Не замена параметрам: бизнес‑данные и состояние не прячьте в Local

### Параметры vs CompositionLocal
- Параметры: локальная зависимость, часто меняется, важна явность API
- Local: кросс‑каттинговая зависимость, редко меняется, относится к среде (theme, locale, hаптика, imageLoader)

### dynamic vs static
- `compositionLocalOf` (динамический)
  - Трекинг чтений: рекомпозируются только реальные читатели `.current`
  - Подходит для часто меняющихся значений (позиция скролла, runtime‑флаги)
  - Небольшой накладной расход на чтение
- `staticCompositionLocalOf` (статический)
  - Без трекинга чтений: апдейт инвалидирует всё поддерево провайдера
  - Подходит для редко меняющихся, широко читаемых значений (тема, локаль)
  - Чтение дешевле, обновление дороже (широкая инвалидация)

Практика: часто меняется и нужна узкая область рекомпозиции → `compositionLocalOf`; редко меняется и читается везде → `staticCompositionLocalOf`.

### Границы инвалидации
- Граница — блок `CompositionLocalProvider`
- Динамический Local инвалидирует только читателей; статический — всё поддерево
- Размещайте провайдер ближе к потребителям, если обновления частые и «широкие»

### Безопасные значения по умолчанию
- Избегайте «валидного» silent‑default: может скрыть отсутствие провайдера
- Предпочтительно бросать ошибку в фабрике Local или давать явный noop со строгой семантикой

### Иммутабельность и стабильность
- Значения должны быть неизменяемыми или явно стабильными
- Меняйте ссылку целиком (copy), а не внутренние `var` без уведомления Compose

### Подводные камни
- Чтение Local вне композиции (в долгоживущих лямбдах)
- Использование Local для бизнес‑логики/репозиториев вместо DI
- Провайдер слишком высоко для часто меняющегося значения → лишняя рекомпозиция

### Паттерны
- Тонкий провайдер: оборачивайте только нужное поддерево
- Комбинация статических значений в один провайдер для редких обновлений
- Тестируемость: переопределяйте Local локально в тестах

### Минимальные примеры

Создание и провайдинг (статический контекст):
```kotlin
// Глобальный редко меняющийся контекст
data class AppEnv(val locale: Locale, val haptics: Haptics)
val LocalAppEnv = staticCompositionLocalOf<AppEnv> { error("No AppEnv provided") }

@Composable
fun App(env: AppEnv, content: @Composable () -> Unit) {
    CompositionLocalProvider(LocalAppEnv provides env) { content() }
}
```

Динамический Local с узкой рекомпозицией:
```kotlin
val LocalScrollY = compositionLocalOf { 0 }

@Composable
fun Screen(scrollY: Int) {
    CompositionLocalProvider(LocalScrollY provides scrollY) {
        Header()              // не читает Local → не рекомпозируется
        StickyToolbar()       // читает Local → рекомпозируется на изменение
    }
}
```

---

## Answer (EN)

### Purpose
- Local "context" for a subtree: theme, locale, density, haptics, UI‑level DI objects
- Avoids over‑plumbing parameters when the dependency is environmental
- Not a replacement for parameters: do not hide business data/state in Locals

### Parameters vs CompositionLocal
- Parameters: local dependency, changes frequently, API clarity
- Local: cross‑cutting, rarely changing, environmental (theme, locale, imageLoader)

### dynamic vs static
- `compositionLocalOf` (dynamic)
  - Read tracking: only actual `.current` readers recompose
  - Fits frequently changing values (scroll position, runtime flags)
  - Small per‑read overhead
- `staticCompositionLocalOf` (static)
  - No read tracking: update invalidates entire provider subtree
  - Fits rarely changing, widely read values (theme, locale)
  - Cheaper reads, more expensive updates (wide invalidation)

Rule of thumb: changes often + narrow recomposition → `compositionLocalOf`; rarely changes + wide readership → `staticCompositionLocalOf`.

### Invalidation boundaries
- Boundary is `CompositionLocalProvider`
- Dynamic: invalidates only readers; static: whole subtree
- Place providers close to consumers if updates are wide/frequent

### Safe defaults
- Avoid silent valid defaults; prefer throwing in factory or explicit noop

### Immutability & stability
- Prefer immutable or explicitly stable values
- Update the reference (copy) vs mutating internals invisibly to Compose

### Pitfalls
- Reading Local outside composition (long‑lived lambdas)
- Using Local for business logic/repos instead of DI
- Provider too high for frequently changing value → extra recomposition

### Patterns
- Thin provider over only the necessary subtree
- Combine rare static values under one provider
- Override Locals in tests within the scene

### Minimal examples

Create & provide (static context):
```kotlin
// Rarely changing global context
data class AppEnv(val locale: Locale, val haptics: Haptics)
val LocalAppEnv = staticCompositionLocalOf<AppEnv> { error("No AppEnv provided") }

@Composable
fun App(env: AppEnv, content: @Composable () -> Unit) {
    CompositionLocalProvider(LocalAppEnv provides env) { content() }
}
```

Dynamic Local with narrow recomposition:
```kotlin
val LocalScrollY = compositionLocalOf { 0 }

@Composable
fun Screen(scrollY: Int) {
    CompositionLocalProvider(LocalScrollY provides scrollY) {
        Header()              // does not read → no recomposition
        StickyToolbar()       // reads Local → recomposes on change
    }
}
```

---

## Follow-ups
- How to scope providers across feature modules?
- When are parameters still preferable despite deep trees?
- How to profile invalidation caused by Local updates?
- Strategies for testing and overriding chains of providers?

## References
- [CompositionLocal (Docs)](https://developer.android.com/jetpack/compose/compositionlocal)
- [Compose Mental Model](https://developer.android.com/develop/ui/compose/mental-model)

## Related Questions

### Prerequisites (Easier)
- [[q-compose-semantics--android--medium]]

### Related (Same Level)
- [[q-compositionlocal-advanced--jetpack-compose--medium]]
- [[q-compose-remember-derived-state--jetpack-compose--medium]]

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]]

