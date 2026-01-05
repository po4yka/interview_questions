---
id: android-274
title: "How To Handle The Situation Where Activity Can Open Multiple Times Due To Deeplink / Как обработать ситуацию когда Activity может открыться несколько раз из-за deeplink"
aliases: ["How To Handle The Situation Where Activity Can Open Multiple Times Due To Deeplink", "Как обработать ситуацию когда Activity может открыться несколько раз из-за deeplink"]
topic: android
subtopics: [activity, intents-deeplinks, ui-navigation]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-activity-lifecycle, q-activity-navigation-how-it-works--android--medium, q-compose-navigation-advanced--android--medium, q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-15
tags: [android, android/activity, android/intents-deeplinks, android/ui-navigation, difficulty/medium]

---
# Вопрос (RU)

> Как обработать ситуацию, когда `Activity` может открыться несколько раз из-за deeplink?

# Question (EN)

> How to handle the situation where `Activity` can open multiple times due to deeplink?

---

## Ответ (RU)

При использовании deeplink `Activity` может запускаться многократно, создавая дубликаты в back stack. Существует несколько подходов для предотвращения этой проблемы.

### Проблема

```kotlin
// Пользователь кликает deeplink несколько раз
// www.example.com/product/123
// www.example.com/product/123  (снова)
// Результат: дубликаты ProductActivity в стеке
```

### Решение 1: Launch Mode singleTop

Самое распространенное решение для deeplink:

```xml
<activity
    android:name=".ProductActivity"
    android:launchMode="singleTop">
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data
            android:scheme="https"
            android:host="www.example.com"
            android:pathPrefix="/product" />
    </intent-filter>
</activity>
```

```kotlin
class ProductActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handleDeeplink(intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent) // ✅ Обновить текущий intent
        handleDeeplink(intent)
    }

    private fun handleDeeplink(intent: Intent) {
        val productId = intent.data?.lastPathSegment
        loadProduct(productId)
    }
}
```

**Поведение singleTop**:
- `Activity` на вершине стека → вызов `onNewIntent()` (без дубликата)
- `Activity` ниже в стеке → создание нового экземпляра
- `Activity` отсутствует → создание нового экземпляра

### Решение 2: `Intent` Flags

Программное управление через флаги:

```kotlin
val productIntent = Intent(this, ProductActivity::class.java).apply {
    // ✅ Часто используемая комбинация для deeplink-сценариев (при запуске из кода приложения)
    flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
    putExtra("product_id", productId)
}
startActivity(productIntent)
```

**Комбинации флагов**:
```kotlin
// CLEAR_TOP + SINGLE_TOP: найти существующую в текущем task, очистить выше, вызвать onNewIntent()
flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP

// CLEAR_TASK + NEW_TASK: полностью очистить текущий task и запустить новую задачу
flags = Intent.FLAG_ACTIVITY_CLEAR_TASK or Intent.FLAG_ACTIVITY_NEW_TASK

// REORDER_TO_FRONT: переместить существующую Activity в текущем task на вершину, если она там есть
flags = Intent.FLAG_ACTIVITY_REORDER_TO_FRONT
```

### Решение 3: Trampoline `Activity` Pattern

Промежуточная `Activity` для управления навигацией:

```xml
<!-- Trampoline получает все deeplink -->
<activity
    android:name=".DeeplinkActivity"
    android:theme="@android:style/Theme.NoDisplay"
    android:excludeFromRecents="true"
    android:noHistory="true">
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="https" android:host="www.example.com" />
    </intent-filter>
</activity>

<!-- Целевая Activity с singleTop -->
<activity
    android:name=".ProductActivity"
    android:launchMode="singleTop" />
```

```kotlin
class DeeplinkActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val data = intent.data ?: run {
            finish()
            return
        }

        val targetIntent = when {
            data.path?.startsWith("/product") == true -> {
                Intent(this, ProductActivity::class.java).apply {
                    // ✅ В типичном случае предотвращает создание дубликатов ProductActivity
                    // (если существующий экземпляр находится в том же task)
                    flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or
                            Intent.FLAG_ACTIVITY_SINGLE_TOP
                    putExtra("product_id", data.lastPathSegment)
                }
            }
            else -> Intent(this, MainActivity::class.java)
        }

        startActivity(targetIntent)
        finish() // ✅ Обязательно завершить trampoline
    }
}
```

(Учтите, что trampoline-подход дает гибкость, но добавляет накладные расходы и усложняет навигацию; его стоит применять только когда нужна централизованная сложная маршрутизация.)

### Решение 4: Navigation Component

Современный подход с Jetpack Navigation:

```xml
<!-- nav_graph.xml -->
<navigation xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    app:startDestination="@id/homeFragment">

    <fragment
        android:id="@+id/productFragment"
        android:name=".ProductFragment">
        <deepLink app:uri="https://www.example.com/product/{productId}" />
    </fragment>
</navigation>
```

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main) // ✅ Должен содержать NavHostFragment с nav_host_fragment id

        val navController = findNavController(R.id.nav_host_fragment)
        // ✅ Обычно достаточно, когда Activity создается посредством deeplink.
        // Если Activity уже запущена и приходит новый intent, обрабатывайте его в onNewIntent().
        navController.handleDeepLink(intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        // ✅ Вызывайте handleDeepLink здесь для deeplink, приходящих в уже существующую Activity
        findNavController(R.id.nav_host_fragment).handleDeepLink(intent)
    }
}
```

**Преимущества Navigation Component**:
- Автоматическое управление back stack
- Паттерн Single-Activity
- Type-safe аргументы

### Сравнение Решений

| Решение | Плюсы | Минусы | Когда использовать |
|---------|-------|--------|-------------------|
| singleTop | Простота, предотвращает дубликаты на вершине | Разрешает дубликаты ниже в стеке | Большинство deeplink сценариев |
| `Intent` flags | Гибкость, программный контроль | Требует явного применения и понимания поведения task | Динамическая логика |
| Trampoline | Полный контроль маршрутизации | Дополнительная `Activity`, усложнение и накладные расходы | Сложная централизованная маршрутизация |
| Navigation Component | Современный, type-safe | Кривая обучения | Новые проекты, Single-Activity подход |

### Best Practices

1. Используйте **singleTop** для большинства deeplink целей (если это соответствует UX и навигации).
2. Реализуйте **onNewIntent()** для deeplink-целей, если вы ожидаете получать новые intents в уже существующую Activity (например, при `singleTop` или `FLAG_ACTIVITY_SINGLE_TOP`).
3. Вызывайте **setIntent()** в `onNewIntent()` для обновления текущего intent.
4. Используйте **Navigation Component** для новых проектов и сценариев с Single-Activity архитектурой.
5. Применяйте **Trampoline pattern** только при необходимости сложной маршрутизации и централизованной обработки deeplink.
6. Тщательно **тестируйте** с различными состояниями навигации, сценариями запуска приложения и конфигурациями task.

## Answer (EN)

When using deeplinks, an `Activity` can be launched multiple times creating duplicate instances in the back stack. Several approaches prevent this problem.

### Problem

```kotlin
// User clicks deeplink multiple times
// www.example.com/product/123
// www.example.com/product/123  (again)
// Result: duplicate ProductActivity instances in stack
```

### Solution 1: Launch Mode singleTop

Most common solution for deeplinks:

```xml
<activity
    android:name=".ProductActivity"
    android:launchMode="singleTop">
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data
            android:scheme="https"
            android:host="www.example.com"
            android:pathPrefix="/product" />
    </intent-filter>
</activity>
```

```kotlin
class ProductActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        handleDeeplink(intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent) // ✅ Update current intent
        handleDeeplink(intent)
    }

    private fun handleDeeplink(intent: Intent) {
        val productId = intent.data?.lastPathSegment
        loadProduct(productId)
    }
}
```

**singleTop behavior**:
- `Activity` at top of stack → calls `onNewIntent()` (no duplicate)
- `Activity` below in stack → creates new instance
- `Activity` not in stack → creates new instance

### Solution 2: `Intent` Flags

Programmatic control with flags:

```kotlin
val productIntent = Intent(this, ProductActivity::class.java).apply {
    // ✅ Commonly used combination for deeplink scenarios (when starting from within the app)
    flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
    putExtra("product_id", productId)
}
startActivity(productIntent)
```

**Flag combinations**:
```kotlin
// CLEAR_TOP + SINGLE_TOP: find existing in the current task, clear above, call onNewIntent()
flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP

// CLEAR_TASK + NEW_TASK: completely clear the current task and start a new one
flags = Intent.FLAG_ACTIVITY_CLEAR_TASK or Intent.FLAG_ACTIVITY_NEW_TASK

// REORDER_TO_FRONT: move existing Activity in the current task to the front if it exists
flags = Intent.FLAG_ACTIVITY_REORDER_TO_FRONT
```

### Solution 3: Trampoline `Activity` Pattern

Intermediate activity to control navigation:

```xml
<!-- Trampoline receives all deeplinks -->
<activity
    android:name=".DeeplinkActivity"
    android:theme="@android:style/Theme.NoDisplay"
    android:excludeFromRecents="true"
    android:noHistory="true">
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data android:scheme="https" android:host="www.example.com" />
    </intent-filter>
</activity>

<!-- Target activity with singleTop -->
<activity
    android:name=".ProductActivity"
    android:launchMode="singleTop" />
```

```kotlin
class DeeplinkActivity : Activity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val data = intent.data ?: run {
            finish()
            return
        }

        val targetIntent = when {
            data.path?.startsWith("/product") == true -> {
                Intent(this, ProductActivity::class.java).apply {
                    // ✅ In typical cases prevents creating duplicate ProductActivity instances
                    // (provided the existing instance is in the same task)
                    flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or
                            Intent.FLAG_ACTIVITY_SINGLE_TOP
                    putExtra("product_id", data.lastPathSegment)
                }
            }
            else -> Intent(this, MainActivity::class.java)
        }

        startActivity(targetIntent)
        finish() // ✅ Always finish trampoline
    }
}
```

(Note that while the trampoline approach gives flexibility, it adds overhead and complexity; use it only when you truly need centralized, complex routing.)

### Solution 4: Navigation Component

Modern approach with Jetpack Navigation:

```xml
<!-- nav_graph.xml -->
<navigation xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    app:startDestination="@id/homeFragment">

    <fragment
        android:id="@+id/productFragment"
        android:name=".ProductFragment">
        <deepLink app:uri="https://www.example.com/product/{productId}" />
    </fragment>
</navigation>
```

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main) // ✅ Must contain NavHostFragment with nav_host_fragment id

        val navController = findNavController(R.id.nav_host_fragment)
        // ✅ Typically sufficient when the Activity is created via the deeplink.
        // If the Activity is already running and a new intent arrives, handle it in onNewIntent().
        navController.handleDeepLink(intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        // ✅ Call handleDeepLink here for deeplinks delivered to an existing Activity
        findNavController(R.id.nav_host_fragment).handleDeepLink(intent)
    }
}
```

**Navigation Component benefits**:
- Automatic back stack management
- Single-Activity pattern
- Type-safe arguments

### Solution Comparison

| Solution | Pros | Cons | When to use |
|----------|------|------|-------------|
| singleTop | Simple, prevents top duplicates | Allows duplicates below in stack | Most deeplink scenarios |
| `Intent` flags | Flexible, programmatic control | Requires explicit use and understanding of task behavior | Dynamic logic |
| Trampoline | Full routing control | Extra activity, overhead and complexity | Complex centralized routing |
| Navigation Component | Modern, type-safe | Learning curve | New projects, Single-Activity setups |

### Best Practices

1. Use **singleTop** for most deeplink targets (when aligned with UX and navigation design).
2. Implement **onNewIntent()** for deeplink targets when you expect to receive new intents in an existing Activity (e.g., with `singleTop` or `FLAG_ACTIVITY_SINGLE_TOP`).
3. Call **setIntent()** in `onNewIntent()` to update the current intent.
4. Use **Navigation Component** for new projects and Single-Activity style navigation.
5. Apply the **Trampoline pattern** only when you need complex routing and centralized deeplink handling.
6. Thoroughly **test** across different navigation states, app launch modes, and task configurations.

---

## Follow-ups

- How to handle deeplinks when the app is not running?
- What happens to the back stack with singleTask vs singleTop?
- How to test deeplink handling in different navigation states?
- Can you combine multiple launch modes in the same application?
- How does Navigation Component handle deeplink conflicts?

## References

- [[c-activity-lifecycle]] - Understanding `Activity` lifecycle
- Android Documentation: [Tasks and Back `Stack`](https://developer.android.com/guide/components/activities/tasks-and-back-stack)
- Android Documentation: [Deep Links](https://developer.android.com/training/app-links/deep-linking)
- Jetpack Navigation: [Navigation Deeplinks](https://developer.android.com/guide/navigation/navigation-deep-link)

## Related Questions

### Prerequisites
- [[q-activity-navigation-how-it-works--android--medium]] - Understanding `Activity` navigation fundamentals

### Related (Same Level)
- [[q-compose-navigation-advanced--android--medium]] - Navigation in Compose
- [[q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]] - `Activity` lifecycle and memory

### Advanced (Harder)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - `Fragment` vs `Activity` architecture decisions
