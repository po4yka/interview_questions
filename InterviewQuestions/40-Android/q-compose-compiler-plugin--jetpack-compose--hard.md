---
id: 20251012-122803
title: Compose Compiler Plugin / Плагин компилятора Compose
aliases: [Compose Compiler Plugin, Плагин компилятора Compose]
topic: android
subtopics: [ui-compose, performance]
question_kind: android
difficulty: hard
status: reviewed
moc: moc-android
related: [q-animated-visibility-vs-content--jetpack-compose--medium, q-compose-canvas-graphics--jetpack-compose--hard, q-android-performance-measurement-tools--android--medium]
created: 2025-10-11
updated: 2025-10-20
original_language: en
language_tags: [en, ru]
tags: [android/ui-compose, compiler, performance, recomposition, difficulty/hard]
---

# Question (EN)
> How does the Compose Compiler plugin work (lowering, stability inference, skipping), and how do you use it to improve performance and diagnostics?

# Вопрос (RU)
> Как работает плагин компилятора Compose (lowering, вывод стабильности, skipping) и как использовать его для повышения производительности и диагностики?

---

## Answer (EN)

### What the plugin does (high level)
- Lowers `@Composable` functions to state machines; inserts composer parameters, keys, groups
- Infers parameter stability (Stable/Unstable) to decide if recomposition can be skipped
- Marks calls restartable/skippable; generates slot table read/write operations

### Stability & skipping (theory)
- Stable params that are referentially equal → call is skippable
- Unstable params or changed identity/content → recomposition executes
- Collections/MutableState wrappers impact stability; prefer stable immutable models

### Minimal examples
Stable model → fewer recompositions:
```kotlin
@Immutable data class User(val id: String, val name: String)
@Composable fun UserRow(user: User) { /* draw using stable fields */ }
```

Avoid unstable mutable props in parameters:
```kotlin
// BAD: passing mutable list triggers recomposition often
@Composable fun ListScreen(items: MutableList<Item>) { /* ... */ }

// GOOD: expose SnapshotStateList via stable facade or pass immutable List
@Composable fun ListScreen(items: List<Item>) { /* ... */ }
```

Hoist state and keep parameters stable:
```kotlin
@Composable fun Counter() {
  var count by remember { mutableStateOf(0) }
  Button(onClick = { count++ }) { Text("$count") } // only Text recomposes
}
```

### Diagnostics (reports)
- Enable compiler metrics/reports to inspect stability/skipping decisions and call graphs
- Review: which calls are restartable/skippable; which types are unstable; large group counts

Minimal Gradle flags (no versions):
```bash
# gradle.properties or CI flags
compose.compiler.report=true
compose.compiler.metrics=true
compose.compiler.reportDestination=build/compose-reports
compose.compiler.metricsDestination=build/compose-metrics
```

### Performance practices
- Prefer @Immutable/@Stable for domain models when semantics apply
- Keep large objects out of parameters; pass keys/ids instead
- Move heavy work off composition; use remember + derivedStateOf
- Avoid recomposition cascades: break trees with subcomposables, remember

## Ответ (RU)

### Что делает плагин (в общих чертах)
- Трансформирует `@Composable` в машины состояний; вставляет composer/keys/groups
- Выводит стабильность параметров (Stable/Unstable) для решения о пропуске
- Помечает вызовы restartable/skippable; генерирует операции со slot‑таблицей

### Стабильность и пропуски
- Стабильные параметры без изменений → вызов можно пропустить
- Нестабильные параметры или изменение идентичности/содержимого → выполняем рекомпозицию
- Коллекции/MutableState влияют на стабильность; предпочитать стабильные неизменяемые модели

### Минимальные примеры
Стабильная модель → меньше рекомпозиций:
```kotlin
@Immutable data class User(val id: String, val name: String)
@Composable fun UserRow(user: User) { /* рисуем stable поля */ }
```

Избегать нестабильных mutable‑параметров:
```kotlin
// ПЛОХО: mutable list в параметрах часто триггерит рекомпозицию
@Composable fun ListScreen(items: MutableList<Item>) { /* ... */ }

// ХОРОШО: SnapshotStateList через стабильную фасадную API или неизменяемый List
@Composable fun ListScreen(items: List<Item>) { /* ... */ }
```

Поднимать состояние и держать параметры стабильными:
```kotlin
@Composable fun Counter() {
  var count by remember { mutableStateOf(0) }
  Button(onClick = { count++ }) { Text("$count") } // меняется только Text
}
```

### Диагностика (отчёты)
- Включайте метрики/отчёты компилятора, чтобы видеть стабильность/skip и граф вызовов
- Анализ: какие вызовы restartable/skippable; какие типы нестабильны; большие group‑counts

Минимальные флаги Gradle (без версий):
```bash
# gradle.properties или флаги CI
compose.compiler.report=true
compose.compiler.metrics=true
compose.compiler.reportDestination=build/compose-reports
compose.compiler.metricsDestination=build/compose-metrics
```

### Практики производительности
- Предпочитать @Immutable/@Stable для доменных моделей по смыслу
- Не передавать большие объекты в параметры; передавать id/keys
- Убирать тяжёлую работу из композиции; использовать remember + derivedStateOf
- Избегать каскадных рекомпозиций: разбивать на подкомпоновки, использовать remember

---

## Follow-ups
- How to interpret compiler stability reports and fix unstable types?
- What are trade‑offs of @Stable/@Immutable annotations vs real immutability?
- How to validate recomposition counts (Macrobenchmark tracing)?

## References
- https://developer.android.com/jetpack/compose/performance
- https://developer.android.com/jetpack/compose/mental-model

## Related Questions

### Prerequisites (Easier)
- [[q-android-performance-measurement-tools--android--medium]]

### Related (Same Level)
- [[q-animated-visibility-vs-content--jetpack-compose--medium]]
- [[q-compose-canvas-graphics--jetpack-compose--hard]]

### Advanced (Harder)
- [[q-android-runtime-art--android--medium]]

