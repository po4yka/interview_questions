---
id: 20251020-211200
title: CompositionLocal Advanced / CompositionLocal — продвинутый уровень
aliases: [CompositionLocal Advanced, CompositionLocal — продвинутый уровень]
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
updated: 2025-10-27
tags: [android/ui-compose, android/architecture-mvvm, difficulty/medium]
---
# Вопрос (RU)
> CompositionLocal — продвинутый уровень?

# Question (EN)
> CompositionLocal Advanced?

---

## Ответ (RU)

### Зачем CompositionLocal
- Контекст для поддерева: тема, локаль, плотность, DI-объекты
- Избавляет от передачи параметров через многие слои, когда явные параметры снижают читаемость
- Не замена параметрам: используйте, когда зависимость действительно относится к окружению

См. также [[c-dependency-injection]] и c-compose-state для понимания управления зависимостями в Compose.

### Параметры vs Local
- Параметры — когда зависимость локальная, часто меняется, и важна ясность API
- CompositionLocal — когда зависимость сквозная, редко меняется, и относится к окружению (тема, haptics, logger, imageLoader)

### staticCompositionLocalOf vs compositionLocalOf
- `compositionLocalOf` (динамический)
  - Отслеживание чтения: перекомпозируются только читатели `.current`
  - Подходит для часто меняющихся значений (позиция скролла, динамические флаги)
  - Небольшие затраты на чтение
- `staticCompositionLocalOf` (статический)
  - Без отслеживания: обновление значения инвалидирует всё поддерево провайдера
  - Подходит для редко меняющихся, широко используемых значений (тема, локаль)
  - Дешевле чтение, дороже обновления (широкая инвалидация)

Правило: если часто меняется и нужна узкая рекомпозиция — `compositionLocalOf`; если редко меняется и широко читается — `staticCompositionLocalOf`.

### Границы инвалидации и производительность
- Граница — блок `CompositionLocalProvider`
- Динамический Local: инвалидация распространяется только на реальных читателей
- Статический Local: инвалидируется всё поддерево провайдера
- Размещайте провайдеры близко к потребителям, если обновления широкие

### Безопасные дефолты
- Риск: валидный дефолт скрывает отсутствие провайдера
- Предпочитайте `error("No Foo provided")` или явный noop с понятной семантикой

### Неизменяемость и стабильность
- Значения должны быть неизменяемыми или явно стабильными
- Обновляйте ссылку (копирование) вместо невидимых для Compose мутаций
- Улучшает предсказуемость и возможность пропуска

### Типичные ошибки
- Чтение Local вне композиции (в лямбдах, переживающих фрейм)
- Использование Local как скрытого глобального для бизнес-логики
- Провайдер слишком высоко для часто меняющихся значений (избыточная рекомпозиция)
- Слишком много мелких провайдеров в горячих путях (накладные расходы)

### Паттерны
- Тонкий провайдер: оборачивайте только поддерево, которому действительно нужно значение
- Комбинированный провайдер: группируйте редко меняющиеся значения в один статический Local
- Тестируемость: переопределяйте Local в тестах внутри сцены

### Минимальные примеры

Создание и предоставление:
```kotlin
// Редко меняющийся глобальный контекст
data class AppEnv(val locale: Locale, val haptics: Haptics)
val LocalAppEnv = staticCompositionLocalOf<AppEnv> { error("No AppEnv provided") }

@Composable
fun App(env: AppEnv, content: @Composable () -> Unit) {
    CompositionLocalProvider(LocalAppEnv provides env) {
        content()
    }
}
```

Динамический Local с узкой рекомпозицией:
```kotlin
val LocalScrollInfo = compositionLocalOf { 0 }

@Composable
fun Screen(scrollY: Int) {
    CompositionLocalProvider(LocalScrollInfo provides scrollY) {
        Header()              // не читает Local → нет рекомпозиции
        StickyToolbar()       // читает Local → рекомпозируется при изменении
    }
}
```

## Answer (EN)

### Why CompositionLocal
- Context for a subtree: theme, locale, density, DI objects
- Removes over-plumbing through many layers when explicit params hurt readability
- Not a replacement for parameters: use when the dependency is truly environmental

See also [[c-dependency-injection]] and c-compose-state for understanding dependency management in Compose.

### Parameters vs Local
- Parameters — when the dependency is local, frequently changing, and API clarity matters
- CompositionLocal — when the dependency is cross-cutting, rarely changing, and environmental (theme, haptics, logger, imageLoader)

### staticCompositionLocalOf vs compositionLocalOf
- `compositionLocalOf` (dynamic)
  - Read tracking: only readers of `.current` recompose
  - Fits frequently changing values (scroll position, dynamic flags)
  - Small per-read overhead
- `staticCompositionLocalOf` (static)
  - No read tracking: updating value invalidates the entire provider subtree
  - Fits rarely changing, widely read values (theme, locale)
  - Cheaper reads, more expensive updates (wide invalidation)

Guideline: if it changes often and you need narrow recomposition — use `compositionLocalOf`; if it rarely changes and is read widely — use `staticCompositionLocalOf`.

### Invalidation Boundaries & Performance
- Boundary is the `CompositionLocalProvider` block
- Dynamic Local: invalidation propagates only to actual readers
- Static Local: the entire provider subtree is invalidated
- Place providers close to consumers if updates are wide

### Safe Defaults
- Risk: silent valid default hides missing provider
- Prefer `error("No Foo provided")` or an explicit noop with clear semantics

### Immutability & Stability
- Values should be immutable or explicitly stable
- Update the reference (copy) rather than mutating internals invisibly to Compose
- Improves predictability and skippability

### Common Pitfalls
- Reading Local outside composition (in lambdas outliving a frame)
- Using Local as hidden global for business logic
- Provider too high for frequently changing values (excess recomposition)
- Too many tiny providers in hot paths (overhead)

### Patterns
- Thin provider: wrap only the subtree that actually needs the value
- Combined provider: group rarely changing values into a single static Local
- Testability: override Local in tests inside the scene

### Minimal Examples

Create and provide:
```kotlin
// Rarely changing global context
data class AppEnv(val locale: Locale, val haptics: Haptics)
val LocalAppEnv = staticCompositionLocalOf<AppEnv> { error("No AppEnv provided") }

@Composable
fun App(env: AppEnv, content: @Composable () -> Unit) {
    CompositionLocalProvider(LocalAppEnv provides env) {
        content()
    }
}
```

Dynamic Local with narrow recomposition:
```kotlin
val LocalScrollInfo = compositionLocalOf { 0 }

@Composable
fun Screen(scrollY: Int) {
    CompositionLocalProvider(LocalScrollInfo provides scrollY) {
        Header()              // does not read Local → no recomposition
        StickyToolbar()       // reads Local → recomposes on change
    }
}
```

---

## Follow-ups
- How to scope providers in multi-module apps with feature modules?
- When to prefer explicit parameters over CompositionLocal despite depth?
- Can CompositionLocal safely carry mutable state objects?
- How to test provider chains and mock overrides in unit tests?
- What is the performance cost of nested CompositionLocalProvider blocks?

## References
- [CompositionLocal Official Docs](https://developer.android.com/jetpack/compose/compositionlocal)
- [Compose Mental Model](https://developer.android.com/develop/ui/compose/mental-model)
- [[c-dependency-injection]]

## Related Questions

### Prerequisites
- [[q-compose-semantics--android--medium]] — Understanding semantic properties
- Basic Compose state and recomposition concepts

### Related
- [[q-compose-remember-derived-state--android--medium]] — State management patterns
- Side effects and CompositionLocal lifecycle

### Advanced
- [[q-compose-performance-optimization--android--hard]] — Performance tuning strategies
- Custom CompositionLocal implementations for complex DI
