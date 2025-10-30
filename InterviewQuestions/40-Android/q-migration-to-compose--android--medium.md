---
id: 20251017-150243
title: "Migration To Compose / Миграция на Compose"
aliases: ["Migration To Compose", "Миграция на Compose"]
topic: android
subtopics: [ui-compose, architecture-mvvm, testing-unit]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-what-does-viewgroup-inherit-from--android--easy, q-what-is-known-about-methods-that-redraw-view--android--medium, q-recyclerview-explained--android--medium, c-jetpack-compose, c-mvvm]
sources: []
created: 2025-10-15
updated: 2025-10-28
tags: [android/ui-compose, android/architecture-mvvm, android/testing-unit, jetpack-compose, migration, xml-to-compose, difficulty/medium]
date created: Tuesday, October 28th 2025, 9:36:25 pm
date modified: Thursday, October 30th 2025, 3:13:23 pm
---

# Вопрос (RU)

> Какая стратегия миграции большого проекта на Jetpack Compose?

# Question (EN)

> What is the strategy for migrating a large project to Jetpack Compose?

---

## Ответ (RU)

Используйте **гибридный подход** с постепенной миграцией снизу вверх. Начинайте с конечных UI-компонентов, сохраняя оба стека (XML и Compose) во время перехода.

### Ключевые этапы

**Этап 1: Подготовка инфраструктуры**
- Добавьте зависимости Compose через BOM
- Настройте `buildFeatures { compose = true }`
- Создайте базовый Design System на Compose
- Обучите команду основам Compose

**Этап 2: ComposeView внутри XML**
Встраивайте Compose-компоненты в существующие экраны через `ComposeView`:

```kotlin
// ✅ Постепенная интеграция - минимальный риск
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main) // XML layout

        findViewById<ComposeView>(R.id.composeView).setContent {
            MaterialTheme {
                UserProfileCard(user = viewModel.currentUser.collectAsState().value)
            }
        }
    }
}
```

**Этап 3: AndroidView для legacy-компонентов**
Используйте XML views внутри Compose через `AndroidView`:

```kotlin
// ✅ Обратная интеграция - для сложных кастомных View
@Composable
fun LegacyMapView(location: Location) {
    AndroidView(
        factory = { context -> MapView(context).apply { onCreate(null) } },
        update = { mapView ->
            mapView.getMapAsync { map ->
                map.moveCamera(CameraUpdateFactory.newLatLngZoom(location.toLatLng(), 15f))
            }
        }
    )
}
```

**Этап 4: Модульная миграция**
Мигрируйте feature-модули один за другим, начиная с простых:

```text
app/
  feature-auth/      ← Мигрируйте первым (маленький модуль)
  feature-profile/   ← Мигрируйте вторым
  feature-messaging/ ← Оставьте на потом (сложный)
```

**Этап 5: Гибридная навигация**
- Navigation Component + ComposeFragment для постепенного перехода
- Или Compose Navigation с `AndroidViewBinding` для legacy-экранов

**Этап 6: Design System**
Создавайте Compose-версии UI-компонентов параллельно с XML. В переходный период поддерживайте оба варианта.

### Общие паттерны миграции

- `RecyclerView` → `LazyColumn` / `LazyRow`
- `ViewPager2` → `HorizontalPager`
- `Fragment` → `@Composable` function
- `LiveData.observe()` → `collectAsState()`
- `findViewById()` → State hoisting

### Риски и решения

**Риск 1: Снижение производительности**

```kotlin
// ❌ Плохо - пересортировка при каждой рекомпозиции
@Composable
fun HeavyList(items: List<Item>) {
    val sorted = items.sortedBy { it.name }
    LazyColumn { items(sorted) { ItemRow(it) } }
}

// ✅ Хорошо - кешируем результат
@Composable
fun HeavyList(items: List<Item>) {
    val sorted = remember(items) { items.sortedBy { it.name } }
    LazyColumn { items(sorted, key = { it.id }) { ItemRow(it) } }
}
```

**Риск 2: Увеличение APK**
Включите R8/ProGuard оптимизации: `minifyEnabled = true`, `shrinkResources = true`.

**Риск 3: Сложные кастомные View**
Используйте Canvas API в Compose для полного контроля над отрисовкой.

### План миграции (50+ экранов)

- **Фаза 1 (1-2 месяца):** Инфраструктура и обучение
- **Фаза 2 (2-3 месяца):** Новые фичи только на Compose
- **Фаза 3 (3-6 месяцев):** Постепенная миграция (простые → сложные)
- **Фаза 4 (1-2 месяца):** Финализация, удаление XML

**Итого:** 9-13 месяцев для полной миграции.

---

## Answer (EN)

Use a **hybrid approach** with gradual bottom-up migration. Start with leaf UI components, keeping both stacks (XML and Compose) during the transition.

### Key Phases

**Phase 1: Infrastructure Setup**
- Add Compose dependencies via BOM
- Configure `buildFeatures { compose = true }`
- Create base Compose Design System
- Train team on Compose basics

**Phase 2: ComposeView Inside XML**
Embed Compose components in existing screens via `ComposeView`:

```kotlin
// ✅ Gradual integration - minimal risk
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main) // XML layout

        findViewById<ComposeView>(R.id.composeView).setContent {
            MaterialTheme {
                UserProfileCard(user = viewModel.currentUser.collectAsState().value)
            }
        }
    }
}
```

**Phase 3: AndroidView for Legacy Components**
Use XML views inside Compose via `AndroidView`:

```kotlin
// ✅ Reverse integration - for complex custom Views
@Composable
fun LegacyMapView(location: Location) {
    AndroidView(
        factory = { context -> MapView(context).apply { onCreate(null) } },
        update = { mapView ->
            mapView.getMapAsync { map ->
                map.moveCamera(CameraUpdateFactory.newLatLngZoom(location.toLatLng(), 15f))
            }
        }
    )
}
```

**Phase 4: Modular Migration**
Migrate feature modules one by one, starting with simple ones:

```text
app/
  feature-auth/      ← Migrate first (small module)
  feature-profile/   ← Migrate second
  feature-messaging/ ← Leave for later (complex)
```

**Phase 5: Hybrid Navigation**
- Navigation Component + ComposeFragment for gradual transition
- Or Compose Navigation with `AndroidViewBinding` for legacy screens

**Phase 6: Design System**
Create Compose versions of UI components in parallel with XML. Support both during transition period.

### Common Migration Patterns

- `RecyclerView` → `LazyColumn` / `LazyRow`
- `ViewPager2` → `HorizontalPager`
- `Fragment` → `@Composable` function
- `LiveData.observe()` → `collectAsState()`
- `findViewById()` → State hoisting

### Risks and Solutions

**Risk 1: Performance Degradation**

```kotlin
// ❌ Bad - re-sorts on every recomposition
@Composable
fun HeavyList(items: List<Item>) {
    val sorted = items.sortedBy { it.name }
    LazyColumn { items(sorted) { ItemRow(it) } }
}

// ✅ Good - caches result
@Composable
fun HeavyList(items: List<Item>) {
    val sorted = remember(items) { items.sortedBy { it.name } }
    LazyColumn { items(sorted, key = { it.id }) { ItemRow(it) } }
}
```

**Risk 2: APK Size Increase**
Enable R8/ProGuard optimizations: `minifyEnabled = true`, `shrinkResources = true`.

**Risk 3: Complex Custom Views**
Use Canvas API in Compose for full control over drawing.

### Migration Plan (50+ screens)

- **Phase 1 (1-2 months):** Infrastructure and training
- **Phase 2 (2-3 months):** New features Compose-only
- **Phase 3 (3-6 months):** Gradual migration (simple → complex)
- **Phase 4 (1-2 months):** Finalization, remove XML

**Total:** 9-13 months for full migration.

---

## Follow-ups

- How to handle deep link navigation in hybrid Compose/XML setup?
- What are the testing strategies during migration (UI tests for both stacks)?
- How to share ViewModel state between XML and Compose screens?
- What tools exist for automated XML-to-Compose conversion?
- How to measure and profile performance during migration?

## References

- [[c-jetpack-compose]] - Jetpack Compose fundamentals
- [[c-mvvm]] - MVVM architecture pattern
- [Compose and Views interoperability](https://developer.android.com/jetpack/compose/interop/interop-apis)
- [Migration strategy guide](https://developer.android.com/jetpack/compose/migrate/strategy)

## Related Questions

### Prerequisites
- [[q-jetpack-compose-basics--android--medium]] - Compose basics and core concepts
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - View rendering fundamentals

### Related
- [[q-how-does-jetpack-compose-work--android--medium]] - Compose internals
- [[q-recyclerview-explained--android--medium]] - RecyclerView patterns
- [[q-mutable-state-compose--android--medium]] - State management in Compose
- [[q-remember-vs-remembersaveable-compose--android--medium]] - State preservation

### Advanced
- [[q-compose-stability-skippability--android--hard]] - Performance optimization
- [[q-stable-classes-compose--android--hard]] - Stability annotations
