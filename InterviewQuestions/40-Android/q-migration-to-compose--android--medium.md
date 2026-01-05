---
id: android-262
title: "Migration To Compose / Миграция на Compose"
aliases: ["Migration To Compose", "Миграция на Compose"]
topic: android
subtopics: [architecture-mvvm, testing-unit, ui-compose]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-jetpack-compose, c-mvvm, q-recyclerview-explained--android--medium, q-what-does-viewgroup-inherit-from--android--easy, q-what-is-known-about-methods-that-redraw-view--android--medium]
sources: []
created: 2025-10-15
updated: 2025-11-11
tags: [android/architecture-mvvm, android/testing-unit, android/ui-compose, difficulty/medium, jetpack-compose, migration, xml-to-compose]

---
# Вопрос (RU)

> Какая стратегия миграции большого проекта на Jetpack Compose?

# Question (EN)

> What is the strategy for migrating a large project to Jetpack Compose?

---

## Ответ (RU)

Используйте **гибридный подход** с постепенной миграцией снизу вверх. Начинайте с конечных UI-компонентов, сохраняя оба стека (XML и Compose) во время перехода.

### Ключевые Этапы

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
    private val viewModel: MainViewModel by viewModels() // пример Activity-скоупа для стейта

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main) // XML layout

        findViewById<ComposeView>(R.id.composeView).setContent {
            MaterialTheme {
                val user by viewModel.currentUser.collectAsState()
                UserProfileCard(user = user)
            }
        }
    }
}
```

**Этап 3: AndroidView для legacy-компонентов**
Используйте XML views внутри Compose через `AndroidView` (пример упрощён — для production-MapView потребуется корректная привязка к lifecycle):

```kotlin
// ✅ Обратная интеграция - для сложных кастомных View (упрощённый пример)
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
    // В реальном проекте обеспечьте вызовы onStart/onResume/onPause/... через Lifecycle
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
Создавайте Compose-версии UI-компонентов параллельно с XML. В переходный период поддерживайте оба варианта и постепенно удаляйте неиспользуемые XML-компоненты.

### Общие Паттерны Миграции

- `RecyclerView` → `LazyColumn` / `LazyRow`
- `ViewPager2` → `HorizontalPager`
- `Fragment` → `@Composable` function
- `LiveData.observe()` → `collectAsState()` / `collectAsStateWithLifecycle()`
- `findViewById()` → State hoisting и передачa стейта через параметры

### Риски И Решения

**Риск 1: Снижение производительности**

```kotlin
// ❌ Плохо - пересортировка при каждой рекомпозиции
@Composable
fun HeavyList(items: List<Item>) {
    val sorted = items.sortedBy { it.name }
    LazyColumn { items(sorted) { ItemRow(it) } }
}

// ✅ Лучше - кешируем результат для неизменяемых входных данных
@Composable
fun HeavyList(items: List<Item>) {
    val sorted = remember(items) { items.sortedBy { it.name } }
    LazyColumn { items(sorted, key = { it.id }) { ItemRow(it) } }
}
// При использовании одного и того же list-объекта убедитесь, что изменения создают новый список,
// иначе remember не пересчитает результат.
```

**Риск 2: Увеличение APK**
Включите R8/ProGuard оптимизации: `minifyEnabled = true`, `shrinkResources = true`. По мере миграции удаляйте дублирующиеся XML-ресурсы и старые `View`-библиотеки, чтобы избежать роста размера.

**Риск 3: Сложные кастомные `View`**
Используйте Canvas API в Compose для полного контроля над отрисовкой.

### План Миграции (50+ экранов)

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
    private val viewModel: MainViewModel by viewModels() // example Activity-scoped state

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main) // XML layout

        findViewById<ComposeView>(R.id.composeView).setContent {
            MaterialTheme {
                val user by viewModel.currentUser.collectAsState()
                UserProfileCard(user = user)
            }
        }
    }
}
```

**Phase 3: AndroidView for Legacy Components**
Use XML views inside Compose via `AndroidView` (simplified example — production MapView requires proper lifecycle handling):

```kotlin
// ✅ Reverse integration - for complex custom Views (simplified)
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
    // In a real project, ensure onStart/onResume/onPause/... are forwarded via Lifecycle
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
Create Compose versions of UI components in parallel with XML. Support both during transition and gradually remove unused XML components.

### Common Migration Patterns

- `RecyclerView` → `LazyColumn` / `LazyRow`
- `ViewPager2` → `HorizontalPager`
- `Fragment` → `@Composable` function
- `LiveData.observe()` → `collectAsState()` / `collectAsStateWithLifecycle()`
- `findViewById()` → State hoisting and passing state via parameters

### Risks and Solutions

**Risk 1: Performance Degradation**

```kotlin
// ❌ Bad - re-sorts on every recomposition
@Composable
fun HeavyList(items: List<Item>) {
    val sorted = items.sortedBy { it.name }
    LazyColumn { items(sorted) { ItemRow(it) } }
}

// ✅ Better - cache result for immutable input lists
@Composable
fun HeavyList(items: List<Item>) {
    val sorted = remember(items) { items.sortedBy { it.name } }
    LazyColumn { items(sorted, key = { it.id }) { ItemRow(it) } }
}
// When reusing the same list instance, ensure mutations create a new list,
// otherwise remember will not recompute.
```

**Risk 2: APK Size Increase**
Enable R8/ProGuard optimizations: `minifyEnabled = true`, `shrinkResources = true`. As you migrate, remove duplicate XML resources and old `View`-based libraries to avoid unnecessary size growth.

**Risk 3: Complex Custom `Views`**
Use Canvas API in Compose for full drawing control.

### Migration Plan (50+ screens)

- **Phase 1 (1-2 months):** Infrastructure and training
- **Phase 2 (2-3 months):** New features Compose-only
- **Phase 3 (3-6 months):** Gradual migration (simple → complex)
- **Phase 4 (1-2 months):** Finalization, remove XML

**Total:** 9-13 months for full migration.

---

## Дополнительные Вопросы (RU)

- Как обрабатывать deep link-навигацию в гибридной Compose/XML архитектуре?
- Какие стратегии тестирования использовать во время миграции (UI-тесты для обоих стеков)?
- Как шарить состояние `ViewModel` между XML и Compose-экранами?
- Какие существуют инструменты для автоматизированной миграции XML в Compose?
- Как измерять и профилировать производительность во время миграции?

## Follow-ups

- How to handle deep link navigation in hybrid Compose/XML setup?
- What are the testing strategies during migration (UI tests for both stacks)?
- How to share `ViewModel` state between XML and Compose screens?
- What tools exist for automated XML-to-Compose conversion?
- How to measure and profile performance during migration?

## Ссылки (RU)

- [[c-jetpack-compose]] - основы Jetpack Compose
- [[c-mvvm]] - архитектурный паттерн MVVM
- [Compose и совместимость с `View`](https://developer.android.com/jetpack/compose/interop/interop-apis)
- [Гайд по стратегии миграции](https://developer.android.com/jetpack/compose/migrate/strategy)

## References

- [[c-jetpack-compose]] - Jetpack Compose fundamentals
- [[c-mvvm]] - MVVM architecture pattern
- [Compose and `Views` interoperability](https://developer.android.com/jetpack/compose/interop/interop-apis)
- [Migration strategy guide](https://developer.android.com/jetpack/compose/migrate/strategy)

## Связанные Вопросы (RU)

### Предпосылки
- [[q-jetpack-compose-basics--android--medium]] - основы Compose и ключевые концепции
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - основы отрисовки `View`

### Похожие
- [[q-how-does-jetpack-compose-work--android--medium]] - внутреннее устройство Compose
- [[q-recyclerview-explained--android--medium]] - паттерны использования RecyclerView
- [[q-mutable-state-compose--android--medium]] - управление состоянием в Compose
- [[q-remember-vs-remembersaveable-compose--android--medium]] - сохранение состояния

### Продвинутое
- [[q-compose-stability-skippability--android--hard]] - оптимизация производительности
- [[q-stable-classes-compose--android--hard]] - аннотации стабильности

## Related Questions

### Prerequisites
- [[q-jetpack-compose-basics--android--medium]] - Compose basics and core concepts
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - `View` rendering fundamentals

### Related
- [[q-how-does-jetpack-compose-work--android--medium]] - Compose internals
- [[q-recyclerview-explained--android--medium]] - RecyclerView patterns
- [[q-mutable-state-compose--android--medium]] - State management in Compose
- [[q-remember-vs-remembersaveable-compose--android--medium]] - State preservation

### Advanced
- [[q-compose-stability-skippability--android--hard]] - Performance optimization
- [[q-stable-classes-compose--android--hard]] - Stability annotations
