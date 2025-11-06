---
id: android-436
title: "Single Activity Approach / Подход Single Activity"
aliases: ["Single Activity Approach", "Подход Single Activity"]

# Classification
topic: android
subtopics: [activity, ui-navigation]
question_kind: theory
difficulty: medium

# Language & provenance
original_language: ru
language_tags: [en, ru]
sources: []

# Workflow & relations
status: draft
moc: moc-android
related: [c-lifecycle, q-activity-lifecycle-methods--android--medium, q-navigation-methods-android--android--medium]

# Timestamps
created: 2025-10-15
updated: 2025-10-28

# Tags (EN only; no leading #)
tags: [activity, android, android/activity, android/ui-navigation, difficulty/medium, fragment, jetpack-navigation]
---

# Вопрос (RU)
> Что означает в Android-разработке подход Single Activity?

# Question (EN)
> What does the Single Activity approach mean in Android development?

---

## Ответ (RU)

**Определение**: Подход Single Activity — архитектурный паттерн, при котором всё пользовательское взаимодействие происходит в рамках одной Activity, а различные экраны реализуются через Fragment'ы.

### Основные Преимущества

**Упрощённое управление состоянием**
- Один контекст Activity для всего приложения
- Передача данных между экранами через Navigation Component
- Централизованное восстановление состояния

**Производительность**
- Отсутствие накладных расходов на запуск новых Activity
- Быстрые переходы между Fragment'ами
- Меньшее потребление памяти

**Улучшенная навигация**
- Единый Navigation Graph описывает все переходы
- Встроенная поддержка Deep Links
- Предсказуемый BackStack

### Реализация С Navigation Component

```kotlin
// MainActivity.kt - единственная Activity
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

**Multi-Activity (традиционный)**
```kotlin
// ❌ Каждый экран — отдельная Activity
class ProductListActivity : AppCompatActivity() {
    fun openDetails(productId: String) {
        val intent = Intent(this, ProductDetailsActivity::class.java)
        intent.putExtra("PRODUCT_ID", productId) // ❌ Небезопасная передача данных
        startActivity(intent)
    }
}
```

**Single Activity (современный)**
```kotlin
// ✅ Один контейнер для всех экранов
class MainActivity : AppCompatActivity() {
    // Fragment'ы управляются Navigation Component
}
```

### Когда Использовать Multi-Activity

Несмотря на преимущества Single Activity, есть случаи для нескольких Activity:

- **Модульность**: Отдельные feature-модули с собственными входными точками
- **Различные UI режимы**: Fullscreen видео, picture-in-picture
- **Legacy интеграция**: Постепенная миграция старого кода

---

## Answer (EN)

**Definition**: The Single Activity approach is an architectural pattern where all user interaction occurs within one Activity, and different screens are implemented using Fragments.

### Key Benefits

**Simplified State Management**
- Single Activity context for the entire app
- Data passing between screens via Navigation Component
- Centralized state restoration

**Performance**
- No overhead from launching new Activities
- Fast transitions between Fragments
- Lower memory consumption

**Enhanced Navigation**
- Single Navigation Graph describes all transitions
- Built-in Deep Links support
- Predictable BackStack

### Implementation with Navigation Component

```kotlin
// MainActivity.kt - the only Activity
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

**Multi-Activity (traditional)**
```kotlin
// ❌ Each screen is a separate Activity
class ProductListActivity : AppCompatActivity() {
    fun openDetails(productId: String) {
        val intent = Intent(this, ProductDetailsActivity::class.java)
        intent.putExtra("PRODUCT_ID", productId) // ❌ Unsafe data passing
        startActivity(intent)
    }
}
```

**Single Activity (modern)**
```kotlin
// ✅ One container for all screens
class MainActivity : AppCompatActivity() {
    // Fragments managed by Navigation Component
}
```

### When to Use Multi-Activity

Despite Single Activity advantages, there are cases for multiple Activities:

- **Modularity**: Separate feature modules with their own entry points
- **Different UI modes**: Fullscreen video, picture-in-picture
- **Legacy integration**: Gradual migration of old code

---

## Follow-ups

- How does Single Activity handle configuration changes differently from Multi-Activity?
- What are the implications for Dependency Injection (Hilt/Koin) scoping?
- How do you share ViewModels between Fragments in Single Activity?
- What's the impact on app startup time and memory footprint?
- How do you handle different Activity launch modes (singleTask, singleInstance)?

## References

- [[c-lifecycle]] - Activity and Fragment lifecycle fundamentals
- [Navigation Component Guide](https://developer.android.com/guide/navigation)
- [Single Activity Architecture](https://www.youtube.com/watch?v=2k8x8V77CrU)
- [Fragments Guide](https://developer.android.com/guide/fragments)

## Related Questions

### Prerequisites (Easier)
- [[q-android-components-besides-activity--android--easy]] - Understanding Activity basics

### Related (Medium)
- [[q-activity-lifecycle-methods--android--medium]] - Activity lifecycle details
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Fragment-Activity relationship
- [[q-single-activity-pros-cons--android--medium]] - Detailed pros/cons analysis

### Advanced (Harder)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - Deep dive into Fragment necessity
