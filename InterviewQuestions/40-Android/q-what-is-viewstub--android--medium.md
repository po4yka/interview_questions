---\
id: android-228
title: What Is ViewStub / Что такое ViewStub
aliases: [ViewStub, ViewStub Android]
topic: android
subtopics: [performance-rendering, ui-views]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-performance, q-compose-core-components--android--medium, q-dagger-build-time-optimization--android--medium, q-data-sync-unstable-network--android--hard, q-recyclerview-sethasfixedsize--android--easy, q-what-is-known-about-methods-that-redraw-view--android--medium]
created: 2025-10-15
updated: 2025-11-11
sources: []
tags: [android/performance-rendering, android/ui-views, difficulty/medium, lazy-loading, optimization, viewstub]

---\
# Вопрос (RU)

> Что такое ViewStub и когда его следует использовать?

# Question (EN)

> What is ViewStub and when should you use it?

---

## Ответ (RU)

**ViewStub** — это невидимый `View` нулевого размера, который используется для ленивой инфляции layout-ресурсов во время выполнения.

### Основная Концепция

При вызове `inflate()` или `setVisibility(``View``.VISIBLE)` происходит:
1. Инфляция указанного layout-ресурса
2. ViewStub **заменяет себя** созданным `View` в родительской иерархии
3. ViewStub перестает существовать (повторная инфляция невозможна)

### Зачем Нужен ViewStub

ViewStub оптимизирует производительность для:
- Сложных layout, которые не всегда нужны
- Условно отображаемых UI элементов (ошибки, детали, премиум-функции)
- Тяжелых `View`, которые должны создаваться только при необходимости

**Преимущества**:
- Ускоряет startup приложения
- Экономит память до момента инфляции
- Уменьшает время начальной инфляции layout

### Базовый Пример

```xml
<!-- activity_main.xml -->
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <!-- Всегда видимый контент -->
    <TextView
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Main Content" />

    <!-- ViewStub - инфлятится только при необходимости -->
    <ViewStub
        android:id="@+id/detailsStub"
        android:inflatedId="@+id/detailsLayout"
        android:layout="@layout/details"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />
</LinearLayout>
```

**Ключевые атрибуты**:
- `android:id` — ID самого ViewStub (используется до инфляции)
- `android:inflatedId` — ID созданного view (используется после инфляции)
- `android:layout` — ресурс layout для инфляции

### Инфляция ViewStub

```kotlin
// ✅ Правильно - получаем ссылку на созданный view
val stub = findViewById<ViewStub>(R.id.detailsStub)
val inflatedView = stub.inflate()  // ViewStub заменяется, возвращается view

// Работаем с созданным view
inflatedView.findViewById<TextView>(R.id.detailsText).text = "Details loaded"
```

```kotlin
// ❌ Неправильно - попытка использовать ViewStub после инфляции
val stub = findViewById<ViewStub>(R.id.detailsStub)
stub.inflate()
stub.inflate()  // Crash! ViewStub уже удален
```

### Типичный Паттерн Использования

```kotlin
class ProductActivity : AppCompatActivity() {
    private var detailsView: View? = null

    private fun showDetails() {
        if (detailsView == null) {
            // ✅ Инфлятим один раз, кешируем ссылку
            val stub = findViewById<ViewStub>(R.id.detailsStub)
            detailsView = stub.inflate()
        }
        detailsView?.visibility = View.VISIBLE
    }

    private fun hideDetails() {
        detailsView?.visibility = View.GONE  // ✅ Скрываем, но не удаляем
    }
}
```

### Сценарии Использования

**1. Состояния ошибок**
```xml
<ViewStub
    android:id="@+id/errorStub"
    android:inflatedId="@+id/errorView"
    android:layout="@layout/error_state"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

**2. Раскрываемые секции**
```kotlin
// Показываем детали только когда пользователь нажал кнопку
binding.btnShowDetails.setOnClickListener {
    if (detailsView == null) {
        detailsView = binding.detailsStub.inflate()
    }
    detailsView?.visibility = View.VISIBLE
}
```

**3. Премиум-функции**
```kotlin
if (user.isPremium) {
    val premiumView = findViewById<ViewStub>(R.id.premiumStub).inflate()
    setupPremiumFeatures(premiumView)
}
```

### ViewStub Vs Include

| Критерий | ViewStub | Include |
|----------|----------|---------|
| Инфляция | Ленивая (по требованию) | Немедленная |
| Память до использования | Минимальная | Полная |
| Startup time | Быстрее | Медленнее |
| Повторная инфляция | Невозможна | — |
| Use case | Условные view | Переиспользуемые layout |

```xml
<!-- Include - инфлятится сразу, даже если скрыт -->
<include
    layout="@layout/details"
    android:visibility="gone" />  <!-- Все равно создан в памяти -->

<!-- ViewStub - не создан до вызова inflate() -->
<ViewStub
    android:id="@+id/detailsStub"
    android:layout="@layout/details" />  <!-- Нулевая стоимость -->
```

### Best Practices

**DO**:
- Используйте для сложных, условно отображаемых layout
- Кешируйте ссылку на созданный view для повторного показа/скрытия
- Применяйте для error/empty states, expandable sections, premium features

**DON'T**:
- Не используйте для всегда видимого контента
- Не пытайтесь инфлятить ViewStub дважды
- Не используйте для простых layout (overhead не оправдан)

### Резюме

ViewStub — легковесный механизм ленивой инфляции для оптимизации производительности и памяти:
- Инфлятится только при необходимости
- Удаляется из иерархии после инфляции
- Идеален для условного UI
- Однократная инфляция (требует кеширования ссылки)

---

## Answer (EN)

**ViewStub** is an invisible, zero-sized `View` used for lazy inflation of layout resources at runtime.

### Core Concept

When `inflate()` or `setVisibility(``View``.VISIBLE)` is called:
1. The specified layout resource is inflated
2. ViewStub **replaces itself** with the inflated `View` in the parent hierarchy
3. ViewStub ceases to exist (re-inflation is impossible)

### Why Use ViewStub

ViewStub optimizes performance for:
- Complex layouts that aren't always needed
- Conditionally displayed UI elements (errors, details, premium features)
- Heavy views that should only be created when necessary

**Benefits**:
- Improves app startup time
- Saves memory until inflation
- Reduces initial layout inflation time

### Basic Example

```xml
<!-- activity_main.xml -->
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <!-- Always visible content -->
    <TextView
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Main Content" />

    <!-- ViewStub - inflated only when needed -->
    <ViewStub
        android:id="@+id/detailsStub"
        android:inflatedId="@+id/detailsLayout"
        android:layout="@layout/details"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />
</LinearLayout>
```

**Key attributes**:
- `android:id` — ID of ViewStub itself (used before inflation)
- `android:inflatedId` — ID of inflated view (used after inflation)
- `android:layout` — Layout resource to inflate

### Inflating ViewStub

```kotlin
// ✅ Correct - get reference to inflated view
val stub = findViewById<ViewStub>(R.id.detailsStub)
val inflatedView = stub.inflate()  // ViewStub replaced, returns view

// Work with inflated view
inflatedView.findViewById<TextView>(R.id.detailsText).text = "Details loaded"
```

```kotlin
// ❌ Wrong - attempting to use ViewStub after inflation
val stub = findViewById<ViewStub>(R.id.detailsStub)
stub.inflate()
stub.inflate()  // Crash! ViewStub already removed
```

### Common Usage Pattern

```kotlin
class ProductActivity : AppCompatActivity() {
    private var detailsView: View? = null

    private fun showDetails() {
        if (detailsView == null) {
            // ✅ Inflate once, cache reference
            val stub = findViewById<ViewStub>(R.id.detailsStub)
            detailsView = stub.inflate()
        }
        detailsView?.visibility = View.VISIBLE
    }

    private fun hideDetails() {
        detailsView?.visibility = View.GONE  // ✅ Hide, don't remove
    }
}
```

### Use Cases

**1. Error States**
```xml
<ViewStub
    android:id="@+id/errorStub"
    android:inflatedId="@+id/errorView"
    android:layout="@layout/error_state"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

**2. Expandable Sections**
```kotlin
// Show details only when user clicks button
binding.btnShowDetails.setOnClickListener {
    if (detailsView == null) {
        detailsView = binding.detailsStub.inflate()
    }
    detailsView?.visibility = View.VISIBLE
}
```

**3. Premium Features**
```kotlin
if (user.isPremium) {
    val premiumView = findViewById<ViewStub>(R.id.premiumStub).inflate()
    setupPremiumFeatures(premiumView)
}
```

### ViewStub Vs Include

| Criterion | ViewStub | Include |
|-----------|----------|---------|
| Inflation | Lazy (on demand) | Immediate |
| Memory before use | Minimal | Full |
| Startup time | Faster | Slower |
| Re-inflation | Impossible | — |
| Use case | Conditional views | Reusable layouts |

```xml
<!-- Include - inflated immediately, even if hidden -->
<include
    layout="@layout/details"
    android:visibility="gone" />  <!-- Still created in memory -->

<!-- ViewStub - not created until inflate() called -->
<ViewStub
    android:id="@+id/detailsStub"
    android:layout="@layout/details" />  <!-- Zero cost -->
```

### Best Practices

**DO**:
- Use for complex, conditionally displayed layouts
- Cache reference to inflated view for repeated show/hide
- Apply for error/empty states, expandable sections, premium features

**DON'T**:
- Don't use for always-visible content
- Don't attempt to inflate ViewStub twice
- Don't use for simple layouts (overhead not justified)

### Summary

ViewStub is a lightweight lazy inflation mechanism for performance and memory optimization:
- Inflates only when needed
- Removed from hierarchy after inflation
- Ideal for conditional UI
- One-time inflation (requires caching reference)

---

## Дополнительные Вопросы (RU)

1. Что произойдет, если попытаться вызвать `inflate()` у одного и того же ViewStub дважды?
2. Чем использование ViewStub отличается от установки `visibility="gone"` для `<include>`?
3. Можно ли изменить layout-ресурс для ViewStub во время выполнения до инфляции?
4. Каковы различия по использованию памяти между ViewStub и `<include>` для редко отображаемого UI?
5. Как вы будете обрабатывать несколько условных секций, которые нужно многократно показывать и скрывать?

## Follow-ups

1. What happens if you try to inflate a ViewStub twice?
2. How does ViewStub differ from setting `visibility="gone"` on an `<include>`?
3. Can you change the layout resource of a ViewStub at runtime before inflation?
4. What are the memory implications of using ViewStub vs include for rarely-shown UI?
5. How would you handle multiple conditional sections that might need to be shown/hidden repeatedly?

## Ссылки (RU)

- [ViewStub - документация Android Developers](https://developer.android.com/reference/android/view/ViewStub)
- [Улучшение производительности разметки - документация Android](https://developer.android.com/training/improving-layouts/loading-ondemand)

## References

- [ViewStub - Android Developers](https://developer.android.com/reference/android/view/ViewStub)
- [Improving Layout Performance - Android Documentation](https://developer.android.com/training/improving-layouts/loading-ondemand)

## Связанные Вопросы (RU)

### Предпосылки / Концепции

- [[c-performance]]

### Предпосылки (проще)

- [[q-recyclerview-sethasfixedsize--android--easy]] - Базовая оптимизация работы с `View`
- Концепции жизненного цикла `View` и инфляции разметки

### Связанные (такой Же уровень)

- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - Методы отрисовки `View`
- Оптимизация производительности инфляции разметки
- Паттерны отображения состояний ошибок

### Продвинутые (сложнее)

- [[q-compose-custom-layout--android--hard]] - Современный декларативный UI-подход
- Кастомная реализация `ViewGroup` с ленивой инфляцией дочерних элементов
- Профилирование памяти для оптимизации разметки

## Related Questions

### Prerequisites / Concepts

- [[c-performance]]

### Prerequisites (Easier)

- [[q-recyclerview-sethasfixedsize--android--easy]] - Basic view optimization
- `View` lifecycle and inflation concepts

### Related (Same Level)

- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - `View` rendering methods
- Layout inflation performance optimization
- Error state handling patterns

### Advanced (Harder)

- [[q-compose-custom-layout--android--hard]] - Modern declarative UI approach
- Custom `ViewGroup` implementation with lazy child inflation
- Memory profiling for layout optimization
