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
related: [q-activity-navigation-how-it-works--android--medium, q-compose-navigation-advanced--android--medium, q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]
sources: []
created: 2025-10-15
updated: 2025-10-31
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
// www.example.com/product/123 (снова)
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
 // ✅ Лучшая комбинация для deeplink
 flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
 putExtra("product_id", productId)
}
startActivity(productIntent)
```

**Комбинации флагов**:
```kotlin
// CLEAR_TOP + SINGLE_TOP: найти существующую, очистить выше, вызвать onNewIntent()
flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP

// CLEAR_TASK + NEW_TASK: полностью очистить task
flags = Intent.FLAG_ACTIVITY_CLEAR_TASK or Intent.FLAG_ACTIVITY_NEW_TASK

// REORDER_TO_FRONT: переместить существующую на вершину
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
 // ✅ Гарантирует отсутствие дубликатов
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
 val navController = findNavController(R.id.nav_host_fragment)
 navController.handleDeepLink(intent)
 }

 override fun onNewIntent(intent: Intent) {
 super.onNewIntent(intent)
 findNavController(R.id.nav_host_fragment).handleDeepLink(intent)
 }
}
```

**Преимущества Navigation Component**:
- Автоматическое управление back stack
- Single `Activity` pattern
- Type-safe аргументы

### Сравнение Решений

| Решение | Плюсы | Минусы | Когда использовать |
|---------|-------|--------|-------------------|
| singleTop | Простота, предотвращает дубликаты на вершине | Разрешает дубликаты ниже в стеке | Большинство deeplink сценариев |
| `Intent` flags | Гибкость, программный контроль | Требует явного применения | Динамическая логика |
| Trampoline | Полный контроль маршрутизации | Дополнительная `Activity` | Сложная маршрутизация |
| Navigation Component | Современный, type-safe | Кривая обучения | Новые проекты |

### Best Practices

1. Используйте **singleTop** для большинства deeplink целей
2. Всегда реализуйте **onNewIntent()** для обработки обновлений
3. Вызывайте **setIntent()** в onNewIntent для обновления текущего intent
4. Используйте **Navigation Component** для новых проектов
5. Применяйте **Trampoline pattern** для сложной маршрутизации
6. Тщательно **тестируйте** с различными состояниями навигации

## Answer (EN)

When using deeplinks, an `Activity` can be launched multiple times creating duplicate instances in the back stack. Several approaches prevent this problem.

### Problem

```kotlin
// User clicks deeplink multiple times
// www.example.com/product/123
// www.example.com/product/123 (again)
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
 // ✅ Best combination for deeplinks
 flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
 putExtra("product_id", productId)
}
startActivity(productIntent)
```

**Flag combinations**:
```kotlin
// CLEAR_TOP + SINGLE_TOP: find existing, clear above, call onNewIntent()
flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP

// CLEAR_TASK + NEW_TASK: completely clear task
flags = Intent.FLAG_ACTIVITY_CLEAR_TASK or Intent.FLAG_ACTIVITY_NEW_TASK

// REORDER_TO_FRONT: move existing to front
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
 // ✅ Guarantees no duplicates
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
 val navController = findNavController(R.id.nav_host_fragment)
 navController.handleDeepLink(intent)
 }

 override fun onNewIntent(intent: Intent) {
 super.onNewIntent(intent)
 findNavController(R.id.nav_host_fragment).handleDeepLink(intent)
 }
}
```

**Navigation Component benefits**:
- Automatic back stack management
- Single `Activity` pattern
- Type-safe arguments

### Solution Comparison

| Solution | Pros | Cons | When to use |
|----------|------|------|-------------|
| singleTop | Simple, prevents top duplicates | Allows duplicates below in stack | Most deeplink scenarios |
| `Intent` flags | Flexible, programmatic | Requires explicit application | Dynamic logic |
| Trampoline | Full routing control | Extra activity | Complex routing |
| Navigation Component | Modern, type-safe | Learning curve | New projects |

### Best Practices

1. Use **singleTop** for most deeplink targets
2. Always implement **onNewIntent()** to handle updates
3. Call **setIntent()** in onNewIntent to update current intent
4. Use **Navigation Component** for new projects
5. Apply **Trampoline pattern** for complex routing
6. Thoroughly **test** with different navigation states

---

## Follow-ups

- How to handle deeplinks when the app is not running?
- What happens to the back stack with singleTask vs singleTop?
- How to test deeplink handling in different navigation states?
- Can you combine multiple launch modes in the same application?
- How does Navigation Component handle deeplink conflicts?

## References

- [[c-activity-lifecycle]] - Understanding `Activity` lifecycle
- - `Intent` flags reference
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
