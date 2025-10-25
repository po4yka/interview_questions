---
id: 20251012-122711169
title: "What Is Viewstub / Что такое ViewStub"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-room-relations-embedded--room--medium, q-api-rate-limiting-throttling--android--medium, q-what-navigation-methods-exist-in-kotlin--programming-languages--medium]
created: 2025-10-15
tags: [viewstub, ui, performance, lazy-loading, optimization, difficulty/medium]
---
# What is ViewStub?

**Russian**: Что такое ViewStub?

## Answer (EN)
### Definition

A **ViewStub** is an **invisible, zero-sized View** that can be used to **lazily inflate layout resources at runtime**.

When a ViewStub is made visible, or when `inflate()` is invoked, the layout resource is inflated. The ViewStub then **replaces itself** in its parent with the inflated View or Views. Therefore, the ViewStub exists in the view hierarchy until `setVisibility(int)` or `inflate()` is invoked.

### Why Use ViewStub?

ViewStub is used for **performance optimization** when you have:
- Complex layouts that are **not always needed**
- UI elements that are **conditionally displayed**
- Heavy views that should only be created **when necessary**

**Benefits**:
- - Reduces initial layout inflation time
- - Saves memory (views not created until needed)
- - Improves app startup performance
- - Better for layouts with conditional sections

### Basic XML Example

```xml
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
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
        android:id="@+id/stub"
        android:inflatedId="@+id/subTree"
        android:layout="@layout/mySubTree"
        android:layout_width="120dp"
        android:layout_height="40dp" />

</LinearLayout>
```

The ViewStub defined above can be found using the id `"stub"`. After inflation of the layout resource `"mySubTree"`, the ViewStub is **removed from its parent**. The View created by inflating the layout resource `"mySubTree"` can be found using the id `"subTree"`, specified by the `inflatedId` property. The inflated View is finally assigned a width of **120dp** and a height of **40dp**.

### Layout to Inflate (mySubTree.xml)

```xml
<!-- res/layout/mySubTree.xml -->
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical"
    android:padding="16dp">

    <ImageView
        android:id="@+id/detailImage"
        android:layout_width="match_parent"
        android:layout_height="200dp"
        android:scaleType="centerCrop" />

    <TextView
        android:id="@+id/detailText"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:textSize="16sp" />

</LinearLayout>
```

### How to Inflate ViewStub

The preferred way to perform the inflation of the layout resource:

```kotlin
// Find the ViewStub
val stub: ViewStub = findViewById(R.id.stub)

// Inflate and get reference to inflated view
val inflated: View = stub.inflate()

// Now you can access views from the inflated layout
val detailImage = inflated.findViewById<ImageView>(R.id.detailImage)
val detailText = inflated.findViewById<TextView>(R.id.detailText)
```

When `inflate()` is invoked:
1. The ViewStub is **replaced** by the inflated View
2. The inflated View is **returned**
3. This lets applications get a reference to the inflated View without executing an extra `findViewById()`

### Alternative Inflation Method

You can also inflate by making the ViewStub visible:

```kotlin
val stub: ViewStub = findViewById(R.id.stub)

// Inflate by setting visibility to VISIBLE
stub.visibility = View.VISIBLE

// Access inflated content using inflatedId
val inflatedView: View = findViewById(R.id.subTree)
```

WARNING: **Important**: After inflation, you cannot use the ViewStub reference anymore. You must use the `inflatedId` to find the inflated view.

### ViewStub Attributes

```xml
<ViewStub
    android:id="@+id/stub"

    <!-- ID of the inflated view (used to find it after inflation) -->
    android:inflatedId="@+id/inflated_layout"

    <!-- Layout resource to inflate -->
    android:layout="@layout/details_layout"

    <!-- ViewStub dimensions (will be ignored, inflated view uses its own) -->
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />
```

**Key attributes**:
- `android:id` - ID of the ViewStub itself (used before inflation)
- `android:inflatedId` - ID of the inflated view (used after inflation)
- `android:layout` - Layout resource to inflate
- `android:layout_width/height` - Applied to the inflated view

### Practical Example: Expandable Details Section

```kotlin
class ProductActivity : AppCompatActivity() {

    private var isDetailsVisible = false
    private var inflatedDetailsView: View? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_product)

        // Show details button
        findViewById<Button>(R.id.btnShowDetails).setOnClickListener {
            toggleDetails()
        }
    }

    private fun toggleDetails() {
        if (isDetailsVisible) {
            // Hide details
            inflatedDetailsView?.visibility = View.GONE
            isDetailsVisible = false
        } else {
            // Show details
            if (inflatedDetailsView == null) {
                // First time - inflate ViewStub
                val stub = findViewById<ViewStub>(R.id.detailsStub)
                inflatedDetailsView = stub.inflate()

                // Setup inflated view
                setupDetailsView(inflatedDetailsView!!)
            } else {
                // Already inflated - just show it
                inflatedDetailsView?.visibility = View.VISIBLE
            }
            isDetailsVisible = true
        }
    }

    private fun setupDetailsView(view: View) {
        view.findViewById<TextView>(R.id.detailsTitle).text = "Product Details"
        view.findViewById<TextView>(R.id.detailsDescription).text = "Description..."
    }
}
```

XML Layout:

```xml
<!-- activity_product.xml -->
<LinearLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <!-- Always visible content -->
    <TextView
        android:id="@+id/productName"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Product Name"
        android:textSize="24sp" />

    <TextView
        android:id="@+id/productPrice"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="$99.99"
        android:textSize="18sp" />

    <Button
        android:id="@+id/btnShowDetails"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Show Details" />

    <!-- ViewStub - details inflated only when button clicked -->
    <ViewStub
        android:id="@+id/detailsStub"
        android:inflatedId="@+id/detailsLayout"
        android:layout="@layout/product_details"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />

</LinearLayout>
```

### Common Use Cases

**1. Error/Empty States**
```xml
<!-- Main content -->
<RecyclerView
    android:id="@+id/recyclerView"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />

<!-- Error state - only shown when error occurs -->
<ViewStub
    android:id="@+id/errorStub"
    android:inflatedId="@+id/errorView"
    android:layout="@layout/error_view"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

```kotlin
// Show error state
fun showError(message: String) {
    recyclerView.visibility = View.GONE

    if (errorView == null) {
        val stub = findViewById<ViewStub>(R.id.errorStub)
        errorView = stub.inflate()
    }

    errorView?.visibility = View.VISIBLE
    errorView?.findViewById<TextView>(R.id.errorMessage)?.text = message
}
```

**2. Advanced Options/Settings**
```xml
<!-- Basic settings always visible -->
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:orientation="vertical">

    <SwitchCompat
        android:id="@+id/notificationsSwitch"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:text="Enable Notifications" />

    <!-- Advanced settings - loaded only if user clicks "Advanced" -->
    <ViewStub
        android:id="@+id/advancedSettingsStub"
        android:inflatedId="@+id/advancedSettings"
        android:layout="@layout/advanced_settings"
        android:layout_width="match_parent"
        android:layout_height="wrap_content" />
</LinearLayout>
```

**3. Premium Features**
```kotlin
// Show premium features only for premium users
if (user.isPremium) {
    val premiumStub = findViewById<ViewStub>(R.id.premiumFeaturesStub)
    val premiumView = premiumStub.inflate()
    setupPremiumFeatures(premiumView)
}
```

### ViewStub vs Include vs Merge

| Feature | ViewStub | Include | Merge |
|---------|----------|---------|-------|
| **Inflation** | Lazy (on demand) | Immediate | Immediate |
| **Performance** | Better (if not always needed) | Standard | Better (flattens hierarchy) |
| **Runtime control** | - Yes | - No | - No |
| **Memory usage** | Lower (until inflated) | Higher | Higher |
| **Use case** | Conditional views | Reusable layouts | Reduce view hierarchy |

**Example comparison**:

```xml
<!-- Include - inflated immediately -->
<include
    layout="@layout/details_layout"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    android:visibility="gone" /> <!-- Still inflated, just hidden -->

<!-- ViewStub - not inflated until needed -->
<ViewStub
    android:id="@+id/detailsStub"
    android:layout="@layout/details_layout"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" /> <!-- Not inflated at all -->
```

### Best Practices

- **Do**:
- Use ViewStub for complex layouts that are conditionally shown
- Use for error states, empty states, loading indicators
- Use for premium/advanced features shown to subset of users
- Cache reference to inflated view if you need to show/hide multiple times

- **Don't**:
- Use for views that are always visible
- Try to inflate the same ViewStub twice (will crash)
- Keep reference to ViewStub after inflation
- Use if the layout is simple and quick to inflate

### Checking If ViewStub Is Inflated

```kotlin
class MyActivity : AppCompatActivity() {
    private var detailsView: View? = null

    private fun showDetails() {
        if (detailsView == null) {
            // Not inflated yet
            val stub = findViewById<ViewStub>(R.id.detailsStub)
            detailsView = stub.inflate()
            setupDetails(detailsView!!)
        }

        // Show inflated view
        detailsView?.visibility = View.VISIBLE
    }

    private fun hideDetails() {
        // Only hide if already inflated
        detailsView?.visibility = View.GONE
    }
}
```

### Advanced: Inflate with Custom LayoutInflater

```kotlin
val stub = findViewById<ViewStub>(R.id.stub)

// Set custom layout inflater
stub.layoutInflater = LayoutInflater.from(customContext)

// Inflate with custom inflater
val inflated = stub.inflate()
```

### Performance Impact Example

Without ViewStub:
```xml
<!-- All views created immediately, even if not visible -->
<LinearLayout>
    <TextView android:text="Main" />
    <include layout="@layout/complex_details" /> <!-- Inflated immediately -->
    <include layout="@layout/complex_settings" /> <!-- Inflated immediately -->
    <include layout="@layout/complex_help" /> <!-- Inflated immediately -->
</LinearLayout>
```
**Result**: Slower startup, higher memory usage

With ViewStub:
```xml
<!-- Only main content inflated initially -->
<LinearLayout>
    <TextView android:text="Main" />
    <ViewStub android:id="@+id/detailsStub" android:layout="@layout/complex_details" />
    <ViewStub android:id="@+id/settingsStub" android:layout="@layout/complex_settings" />
    <ViewStub android:id="@+id/helpStub" android:layout="@layout/complex_help" />
</LinearLayout>
```
**Result**: Faster startup, lower initial memory usage

### Summary

**ViewStub** is a lightweight, invisible, zero-sized view used for **lazy inflation** of layouts:

- - **Performance**: Only inflates when needed
- - **Memory**: Saves memory for unused views
- - **Use cases**: Error states, conditional features, expandable sections
- WARNING: **One-time**: Can only be inflated once
- WARNING: **Replacement**: ViewStub is removed after inflation
-  **Best practice**: Cache inflated view reference for show/hide

**When to use**:
- Complex layouts shown conditionally
- Error/empty/loading states
- Advanced settings or premium features
- Any UI that isn't always needed

**When NOT to use**:
- Always-visible content
- Simple layouts (overhead not worth it)
- Views you need to inflate multiple times

## Ответ (Russian)

**ViewStub** — это **невидимый View нулевого размера**, который используется для **ленивой инфляции layout ресурсов во время выполнения**.

Когда ViewStub становится видимым или вызывается `inflate()`, layout ресурс инфлятится (создается). ViewStub затем **заменяет себя** в родительском контейнере созданными View. Таким образом, ViewStub существует в иерархии представлений до тех пор, пока не будет вызван `setVisibility(int)` или `inflate()`.

### Зачем использовать ViewStub?

ViewStub используется для **оптимизации производительности**, когда у вас есть:
- Сложные layouts, которые **не всегда нужны**
- UI элементы, которые **отображаются условно**
- Тяжелые представления, которые должны создаваться **только при необходимости**

**Преимущества**:
- Сокращает время начальной инфляции layout
- Экономит память (views не создаются до необходимости)
- Улучшает производительность запуска приложения
- Лучше для layouts с условными секциями

### Базовый пример

```xml
<ViewStub
    android:id="@+id/stub"
    android:inflatedId="@+id/subTree"
    android:layout="@layout/mySubTree"
    android:layout_width="120dp"
    android:layout_height="40dp" />
```

### Инфляция ViewStub

Предпочтительный способ инфляции layout ресурса:

```kotlin
val stub: ViewStub = findViewById(R.id.stub)
val inflated: View = stub.inflate()
```

Когда вызывается `inflate()`:
1. ViewStub **заменяется** созданным View
2. Созданный View **возвращается**
3. Это позволяет получить ссылку на созданный View без дополнительного `findViewById()`

### Ключевые атрибуты

- `android:id` - ID самого ViewStub (используется до инфляции)
- `android:inflatedId` - ID созданного view (используется после инфляции)
- `android:layout` - Layout ресурс для инфляции
- `android:layout_width/height` - Применяются к созданному view

### Типичные случаи использования

1. **Состояния ошибок/пустые состояния**
2. **Расширенные опции/настройки**
3. **Премиум функции**
4. **Раскрываемые секции деталей**

### ViewStub vs Include vs Merge

| Особенность | ViewStub | Include | Merge |
|-------------|----------|---------|-------|
| **Инфляция** | Ленивая (по требованию) | Немедленная | Немедленная |
| **Производительность** | Лучше (если не всегда нужен) | Стандартная | Лучше (уплощает иерархию) |
| **Управление в runtime** | - Да | - Нет | - Нет |
| **Использование памяти** | Ниже (до инфляции) | Выше | Выше |

### Важные моменты

- - Можно инфлятить только **один раз**
- WARNING: ViewStub **удаляется** после инфляции
-  Кешируйте ссылку на созданный view для многократного показа/скрытия
- - Используйте для сложных layouts, показываемых условно
- - Не используйте для всегда видимого контента

### Резюме

ViewStub — это легковесный, невидимый view нулевого размера для ленивой инфляции layouts. Улучшает производительность и экономит память за счет создания views только при необходимости. Идеален для состояний ошибок, условных функций и раскрываемых секций.

---

**Source**: [Kirchhoff Android Interview Questions](https://github.com/Kirchhoff-/Android-Interview-Questions)

## Links

- [ViewStub - Android Developers](https://developer.android.com/reference/android/view/ViewStub)
- [How to use View Stub in Android - Stack Overflow](https://stackoverflow.com/questions/11577777/how-to-use-view-stub-in-android)
- [ViewStub: On-Demand Inflate View - ProAndroidDev](https://proandroiddev.com/viewstub-on-demand-inflate-view-or-inflate-lazily-layout-resource-e56b8c39398b)

---

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - View
- [[q-viewmodel-pattern--android--easy]] - View

### Related (Medium)
- [[q-testing-viewmodels-turbine--android--medium]] - View
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - View
- q-rxjava-pagination-recyclerview--android--medium - View
- [[q-what-is-viewmodel--android--medium]] - View
- [[q-how-to-create-list-like-recyclerview-in-compose--android--medium]] - View

### Advanced (Harder)
- [[q-compose-custom-layout--android--hard]] - View
