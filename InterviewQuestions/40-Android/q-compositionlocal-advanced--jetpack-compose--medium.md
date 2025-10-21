---
id: 20251020-211200
title: "CompositionLocal Advanced / CompositionLocal — продвинутый уровень"
aliases: [CompositionLocal Advanced, CompositionLocal — продвинутый уровень]
topic: android
subtopics: [ui-compose, architecture-mvvm]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [ru, en]
status: reviewed
moc: moc-android
related: [q-compose-remember-derived-state--jetpack-compose--medium, q-compose-semantics--android--medium, q-compose-performance-optimization--android--hard]
created: 2025-10-20
updated: 2025-10-20
tags: [android/ui-compose, android/architecture-mvvm, compose, compositionlocal, dependency-injection, best-practices, difficulty/medium]
---

# Вопрос (RU)
> Когда использовать CompositionLocal вместо передачи параметров? В чём разница между `staticCompositionLocalOf` и `compositionLocalOf`, как это влияет на рекомпозицию и производительность? Какие подводные камни и лучшие практики?

# Question (EN)
> When should you use CompositionLocal vs passing parameters? What’s the difference between `staticCompositionLocalOf` and `compositionLocalOf`, and how does it affect recomposition and performance? What are pitfalls and best practices?

---

## Ответ (RU)

### Зачем CompositionLocal
- "Контекст" для поддерева: тема, локаль, плотность, DI-объекты
- Избавляет от «прокидывания через 10 уровней», где явные параметры мешают чтению
- Не замена параметрам: используйте там, где зависимость действительно «среда», а не бизнес‑данные

### Когда параметры, а когда Local
- Параметры — когда зависимость локальна, часто меняется, важна явность API
- CompositionLocal — когда зависимость кросс‑каттинговая, редко меняется, относится к окружению (theme, haptics, logger, imageLoader)

### staticCompositionLocalOf vs compositionLocalOf
- `compositionLocalOf` (динамический)
  - Трекинг чтений: рекомпозируются только те потребители, которые читают `.current`
  - Хорош для часто меняющихся значений (скролл‑позиция, динамические флаги)
  - Небольшой накладной расход на каждое чтение
- `staticCompositionLocalOf` (статический)
  - Нет трекинга чтений: изменение значения приводит к рекомпозиции всего поддерева провайдера
  - Хорош для редко меняющихся «глобальных» параметров (тема, локаль)
  - Чтение дешевле, зато апдейт дороже (широкая инвалидация)

Практика: если значение меняется часто и важно сузить область рекомпозиции — используйте `compositionLocalOf`; если почти не меняется и читается много где — `staticCompositionLocalOf`.

### Границы инвалидации и производительность
- Граница — блок `CompositionLocalProvider`
- Для динамического Local инвалидация идёт до конкретных читателей
- Для статического — всё под деревом провайдера
- Дробите дерево провайдеров ближе к потребителям, если обновление широкое

### Безопасные значения по умолчанию
- Опасно: давать «валидный» silent‑default → маскирует отсутствие провайдера
- Рекомендация: `error("No Foo provided")` в фабрике Local, либо безопасный noop‑объект с явной семантикой

### Иммутабельность и стабильность
- Значения в Local должны быть неизменяемыми или явно стабильными
- Изменяйте целиком ссылку (copy), а не внутренние `var` без уведомления Compose
- Это повышает предсказуемость и шансы на пропуск рекомпозиций

### Типичные ошибки
- Чтение Local вне композиции (в лямбдах, сохраняемых дольше жизни кадра)
- Использование Local как «глобальной» скрытой зависимости бизнес‑логики
- Слишком «высокий» провайдер для часто меняющегося значения (лишняя рекомпозиция)
- Слишком много маленьких провайдеров в горячих ветках (накладные расходы)

### Паттерны
- "Тонкий провайдер": оборачивайте лишь ту часть поддерева, которая реально использует значение
- "Комбинированный провайдер": группируйте редко меняющиеся значения в один статический Local
- "Тестируемость": в тестах переопределяйте Local внутри сцены — просто и надёжно

### Минимальные примеры

Создание и провайдинг:
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

Динамический Local с узкой рекомпозицией:
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

## Answer (EN)

### Why CompositionLocal
- Context for a subtree: theme, locale, density, DI objects
- Removes over‑plumbing through many layers when explicit params hurt readability
- Not a replacement for parameters: use when the dependency is truly environmental

### Parameters vs Local
- Parameters — when the dependency is local, frequently changing, and API clarity matters
- CompositionLocal — when the dependency is cross‑cutting, rarely changing, and environmental (theme, haptics, logger, imageLoader)

### staticCompositionLocalOf vs compositionLocalOf
- `compositionLocalOf` (dynamic)
  - Read tracking: only readers of `.current` recompose
  - Fits frequently changing values (scroll position, dynamic flags)
  - Small per‑read overhead
- `staticCompositionLocalOf` (static)
  - No read tracking: updating value invalidates the entire provider subtree
  - Fits rarely changing, widely read values (theme, locale)
  - Cheaper reads, more expensive updates (wide invalidation)

Guideline: if it changes often and you need narrow recomposition — use `compositionLocalOf`; if it rarely changes and is read widely — use `staticCompositionLocalOf`.

### Invalidation boundaries & performance
- Boundary is the `CompositionLocalProvider` block
- Dynamic Local: invalidation propagates only to actual readers
- Static Local: the entire provider subtree is invalidated
- Place providers close to consumers if updates are wide

### Safe defaults
- Risk: silent valid default hides missing provider
- Prefer `error("No Foo provided")` or an explicit noop with clear semantics

### Immutability & stability
- Values should be immutable or explicitly stable
- Update the reference (copy) rather than mutating internals invisibly to Compose
- Improves predictability and skippability

### Common pitfalls
- Reading Local outside composition (in lambdas outliving a frame)
- Using Local as hidden global for business logic
- Provider too high for frequently changing values (excess recomposition)
- Too many tiny providers in hot paths (overhead)

### Patterns
- Thin provider: wrap only the subtree that actually needs the value
- Combined provider: group rarely changing values into a single static Local
- Testability: override Local in tests inside the scene

### Minimal examples

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
- How to scope providers in multi-module apps?
- When to prefer parameters even if many layers are involved?
- Can CompositionLocal carry mutable state safely?
- How to test provider chains and overrides?

## References
- [CompositionLocal (Docs)](https://developer.android.com/jetpack/compose/compositionlocal)
- [Compose Mental Model](https://developer.android.com/develop/ui/compose/mental-model)

## Related Questions

### Prerequisites (Easier)
- [[q-compose-semantics--android--medium]]

### Related (Same Level)
- [[q-compose-remember-derived-state--jetpack-compose--medium]]

### Advanced (Harder)
- [[q-compose-performance-optimization--android--hard]]
