---
id: android-436
anki_cards:
- slug: android-436-0-en
  language: en
  anki_id: 1768447086584
  synced_at: '2026-01-23T16:45:06.431988'
- slug: android-436-0-ru
  language: ru
  anki_id: 1768447086606
  synced_at: '2026-01-23T16:45:06.432839'
- slug: android-725-0-en
  language: en
- slug: android-725-0-ru
  language: ru
title: Single Activity Approach / Подход Single Activity
aliases:
- Single Activity Approach
- Подход Single Activity
topic: android
subtopics:
- activity
- ui-navigation
question_kind: theory
difficulty: medium
original_language: ru
language_tags:
- en
- ru
sources: []
status: draft
moc: moc-android
related:
- c-lifecycle
- q-activity-lifecycle-methods--android--medium
- q-navigation-methods-android--android--medium
created: 2025-10-15
updated: 2025-11-10
tags:
- activity
- android
- android/activity
- android/ui-navigation
- difficulty/medium
- fragment
- jetpack-navigation
---
# Вопрос (RU)
> Что означает в Android-разработке подход Single `Activity`?

# Question (EN)
> What does the Single `Activity` approach mean in Android development?

---

## Ответ (RU)

**Определение**: Подход Single `Activity` — архитектурный подход, при котором навигация и основной UI-хостинг централизованы в одной корневой `Activity`, а различные экраны реализуются преимущественно через `Fragment`'ы (или другие вью-хосты), вместо множества отдельных `Activity`.

### Основные Преимущества

**Упрощённое управление состоянием**
- Один корневой lifecycle-хост (`Activity`) для навигации
- Удобная передача данных между экранами через Navigation `Component` (Safe Args) или общий `ViewModel`
- Централизованное восстановление состояния навигации и UI

**Производительность и согласованность поведения**
- Снижение накладных расходов именно на частые переключения между `Activity`
- Быстрые переходы между `Fragment`'ами внутри одной `Activity`
- Более предсказуемое поведение back stack по сравнению с множеством разрозненных `Activity` (при корректной конфигурации)

**Улучшенная навигация**
- Навигация описывается Navigation Graph'ами; возможны один или несколько графов и nested graphs для разных feature-модулей
- Встроенная поддержка Deep Links через Navigation `Component`
- Единая точка управления BackStack и обработкой системной кнопки "Назад"

Важно: Single `Activity` подход не является строго обязательным только с `Fragment`'ами или только с одним navigation graph — это про централизованный хостинг и навигацию. Реализация возможна без Navigation `Component`, но библиотека заметно упрощает паттерн.

### Реализация С Navigation Component

```kotlin
// MainActivity.kt - единственная Activity-хост
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val navController = findNavController(R.id.nav_host_fragment) // ✅ Единая точка навигации
        setupActionBarWithNavController(navController)
    }
}

// ProductListFragment.kt - экран списка
class ProductListFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        recyclerView.adapter = ProductAdapter { productId ->
            // ✅ Type-safe навигация через Safe Args
            val action = ProductListFragmentDirections
                .actionProductListToProductDetails(productId)
            findNavController().navigate(action)
        }
    }
}

// Navigation Graph (nav_graph.xml)
<navigation>
    <fragment
        android:id="@+id/productListFragment"
        android:name="com.example.ProductListFragment">
        <action
            android:id="@+id/action_productList_to_productDetails"
            app:destination="@id/productDetailsFragment" />
    </fragment>

    <fragment
        android:id="@+id/productDetailsFragment"
        android:name="com.example.ProductDetailsFragment">
        <argument
            android:name="productId"
            app:argType="string" />
    </fragment>
</navigation>
```

### Сравнение Подходов

**Multi-`Activity` (традиционный)**
```kotlin
// Каждый экран — отдельная Activity
class ProductListActivity : AppCompatActivity() {
    fun openDetails(productId: String) {
        val intent = Intent(this, ProductDetailsActivity::class.java)
        // Стандартный способ передачи данных, но без compile-time type-safety
        intent.putExtra("PRODUCT_ID", productId)
        startActivity(intent)
    }
}
```

**Single `Activity` (современный подход)**
```kotlin
// ✅ Один контейнер для большинства экранов
class MainActivity : AppCompatActivity() {
    // Fragment'ы управляются Navigation Component или вручную через FragmentManager
}
```

### Когда Использовать Multi-`Activity`

Несмотря на преимущества Single `Activity`, есть случаи, когда несколько `Activity` оправданы:

- **Модульность и независимые entry points**: Например, отдельные feature-модули или deep link-и, которые логично вести в разные `Activity`
- **Различные UI режимы / отдельные хосты**: Fullscreen видео, picture-in-picture, отдельный task и т.п.
- **Legacy интеграция**: Постепенная миграция старого кода, где часть экранов остаётся `Activity`-ориентированной

---

## Answer (EN)

**Definition**: The Single `Activity` approach is an architectural pattern where navigation and primary UI hosting are centralized in one root `Activity`, and most screens are implemented via Fragments (or other view hosts) instead of many separate Activities.

### Key Benefits

**Simplified State Management**
- A single root lifecycle host (`Activity`) for navigation
- Convenient data passing between screens via Navigation `Component` (Safe Args) or shared ViewModels
- Centralized restoration of navigation and UI state

**Performance and Behavioral Consistency**
- Reduced overhead specifically from frequent `Activity` switches
- Fast transitions between Fragments within one `Activity`
- More predictable back stack behavior compared to many separate Activities (when configured correctly)

**Enhanced Navigation**
- Navigation is described via Navigation Graphs; you can have one or multiple (including nested graphs) for different feature modules
- Built-in Deep Links support via Navigation `Component`
- Single place to control the back stack and system Back button handling

Note: Single `Activity` does not strictly require using only Fragments or a single navigation graph. It is about centralized hosting and navigation. It can be implemented without Navigation `Component`, though that library greatly simplifies the pattern.

### Implementation with Navigation Component

```kotlin
// MainActivity.kt - the single host Activity
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val navController = findNavController(R.id.nav_host_fragment) // ✅ Single navigation point
        setupActionBarWithNavController(navController)
    }
}

// ProductListFragment.kt - list screen
class ProductListFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        recyclerView.adapter = ProductAdapter { productId ->
            // ✅ Type-safe navigation via Safe Args
            val action = ProductListFragmentDirections
                .actionProductListToProductDetails(productId)
            findNavController().navigate(action)
        }
    }
}

// Navigation Graph (nav_graph.xml)
<navigation>
    <fragment
        android:id="@+id/productListFragment"
        android:name="com.example.ProductListFragment">
        <action
            android:id="@+id/action_productList_to_productDetails"
            app:destination="@id/productDetailsFragment" />
    </fragment>

    <fragment
        android:id="@+id/productDetailsFragment"
        android:name="com.example.ProductDetailsFragment">
        <argument
            android:name="productId"
            app:argType="string" />
    </fragment>
</navigation>
```

### Approach Comparison

**Multi-`Activity` (traditional)**
```kotlin
// Each screen is a separate Activity
class ProductListActivity : AppCompatActivity() {
    fun openDetails(productId: String) {
        val intent = Intent(this, ProductDetailsActivity::class.java)
        // Standard data passing mechanism, but without compile-time type safety
        intent.putExtra("PRODUCT_ID", productId)
        startActivity(intent)
    }
}
```

**Single `Activity` (modern approach)**
```kotlin
// ✅ One container for most screens
class MainActivity : AppCompatActivity() {
    // Fragments managed by Navigation Component or manually via FragmentManager
}
```

### When to Use Multi-`Activity`

Despite Single `Activity` advantages, there are valid cases for multiple Activities:

- **Modularity and independent entry points**: For example, separate feature modules or deep links that logically map to different Activities
- **Different UI modes / separate hosts**: Fullscreen video, picture-in-picture, separate task behavior, etc.
- **Legacy integration**: Gradual migration of legacy code where some screens remain `Activity`-based

---

## Дополнительные Вопросы (RU)

- Как подход Single `Activity` влияет на обработку изменений конфигурации по сравнению с Multi-`Activity` архитектурой?
- Каковы последствия для области видимости Dependency Injection (Hilt/Koin) (`Activity` vs `Fragment` vs scope навигационного графа)?
- Как делиться `ViewModel` между `Fragment`-ами в архитектуре Single `Activity`?
- Как влияет консолидация экранов в одну `Activity` на время запуска приложения и потребление памяти?
- Как подход Single `Activity` влияет на необходимость и использование различных launch modes `Activity` (singleTask, singleInstance и др.)?

## Follow-ups

- How does Single `Activity` affect handling of configuration changes compared to a Multi-`Activity` setup?
- What are the implications for Dependency Injection (Hilt/Koin) scoping (`Activity` vs `Fragment` vs navigation graph scope)?
- How do you share ViewModels between Fragments in a Single `Activity` architecture?
- What is the impact on app startup time and memory footprint when consolidating screens into one `Activity`?
- How does Single `Activity` influence the need for and usage of different `Activity` launch modes (singleTask, singleInstance, etc.)?

## Ссылки (RU)

- [[c-lifecycle]] - основы жизненного цикла `Activity` и `Fragment`
- [Navigation `Component` Guide](https://developer.android.com/guide/navigation)
- [Single `Activity` Architecture](https://www.youtube.com/watch?v=2k8x8V77CrU)
- [Fragments Guide](https://developer.android.com/guide/fragments)

## References

- [[c-lifecycle]] - `Activity` and `Fragment` lifecycle fundamentals
- [Navigation `Component` Guide](https://developer.android.com/guide/navigation)
- [Single `Activity` Architecture](https://www.youtube.com/watch?v=2k8x8V77CrU)
- [Fragments Guide](https://developer.android.com/guide/fragments)

## Связанные Вопросы (RU)

### База (проще)
- [[q-android-components-besides-activity--android--easy]] - понимание основ `Activity`

### Связанные (Medium)
- [[q-activity-lifecycle-methods--android--medium]] - детали жизненного цикла `Activity`
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - связь жизненных циклов `Fragment` и `Activity`
- [[q-single-activity-pros-cons--android--medium]] - подробный разбор преимуществ и недостатков

### Продвинутые (сложнее)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - глубокое обоснование необходимости `Fragment`

## Related Questions

### Prerequisites (Easier)
- [[q-android-components-besides-activity--android--easy]] - Understanding `Activity` basics

### Related (Medium)
- [[q-activity-lifecycle-methods--android--medium]] - `Activity` lifecycle details
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - `Fragment`-`Activity` relationship
- [[q-single-activity-pros-cons--android--medium]] - Detailed pros/cons analysis

### Advanced (Harder)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - Deep dive into `Fragment` necessity
