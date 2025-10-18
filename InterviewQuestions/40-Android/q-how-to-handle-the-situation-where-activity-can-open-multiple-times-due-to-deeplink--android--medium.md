---
id: 20251012-1227184
title: "How To Handle The Situation Where Activity Can Open Multiple Times Due To Deeplink / Как обработать ситуацию когда Activity может открыться несколько раз из-за deeplink"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-dagger-component-dependencies--di--hard, q-biometric-authentication--android--medium, q-how-mutablestate-notifies--android--medium]
created: 2025-10-15
tags:
  - android
---
# How to handle the situation where Activity can open multiple times due to deeplink?

## Answer (EN)
When using deeplinks, an Activity can be launched multiple times creating duplicate instances in the back stack. This can be prevented using launch modes, Intent flags, and proper deeplink configuration.

### Problem Scenario

```kotlin
// User clicks deeplink multiple times or from different sources
// www.example.com/product/123
// www.example.com/product/123  (again)
// www.example.com/product/456

// Result: Multiple instances of ProductActivity in stack
// ProductActivity (123)
// ProductActivity (123)
// ProductActivity (456)
```

### Solution 1: Launch Mode in Manifest

#### singleTop

Prevents duplicate if Activity is already on top:

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
        // Called when Activity already exists at top of stack
        setIntent(intent) // Update current intent
        handleDeeplink(intent)
    }

    private fun handleDeeplink(intent: Intent) {
        val data = intent.data
        val productId = data?.lastPathSegment
        loadProduct(productId)
    }
}
```

**Behavior**:
- If ProductActivity is **at top**: `onNewIntent()` called (no duplicate)
- If ProductActivity is **below**: New instance created
- If ProductActivity is **not in stack**: New instance created

#### singleTask

Creates single instance in task:

```xml
<activity
    android:name=".ProductActivity"
    android:launchMode="singleTask">
    <!-- Intent filter for deeplink -->
</activity>
```

**Behavior**:
- Only **one instance** exists in the task
- If exists: Brings to front and clears activities above it
- Calls `onNewIntent()` with new data

#### singleInstance

Isolated instance in separate task:

```xml
<activity
    android:name=".ProductActivity"
    android:launchMode="singleInstance">
    <!-- Intent filter for deeplink -->
</activity>
```

**Behavior**:
- Activity is **only member** of its task
- No other activities in same task
- Useful for special launchers

### Solution 2: Intent Flags

Use flags programmatically in deeplink handling:

```kotlin
class DeeplinkHandler : Activity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val data = intent.data

        val productIntent = Intent(this, ProductActivity::class.java).apply {
            // Prevent multiple instances
            flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
            putExtra("product_id", data?.lastPathSegment)
        }

        startActivity(productIntent)
        finish() // Important: finish handler activity
    }
}
```

**Common Flag Combinations**:

```kotlin
// Combination 1: Clear top + Single top
// If Activity exists: bring to front, clear above, call onNewIntent()
flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP

// Combination 2: Clear task + New task
// Clear entire task and start fresh
flags = Intent.FLAG_ACTIVITY_CLEAR_TASK or Intent.FLAG_ACTIVITY_NEW_TASK

// Combination 3: Reorder to front
// Bring existing Activity to front without recreating
flags = Intent.FLAG_ACTIVITY_REORDER_TO_FRONT
```

### Solution 3: Deeplink with Navigation Component

Modern approach using Jetpack Navigation:

```xml
<!-- nav_graph.xml -->
<navigation xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/nav_graph"
    app:startDestination="@id/homeFragment">

    <fragment
        android:id="@+id/productFragment"
        android:name=".ProductFragment">
        <deepLink
            app:uri="https://www.example.com/product/{productId}" />
    </fragment>
</navigation>
```

```xml
<!-- AndroidManifest.xml -->
<activity
    android:name=".MainActivity"
    android:launchMode="singleTop">
    <nav-graph android:value="@navigation/nav_graph" />
</activity>
```

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val navController = findNavController(R.id.nav_host_fragment)

        // Handle deeplinks automatically
        navController.handleDeepLink(intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        findNavController(R.id.nav_host_fragment).handleDeepLink(intent)
    }
}
```

**Benefits**:
- Automatic back stack management
- Single Activity pattern
- Type-safe arguments

### Solution 4: Check Task Stack Before Launch

Manually check if Activity already exists:

```kotlin
class DeeplinkManager {

    fun handleDeeplink(context: Context, uri: Uri) {
        val productId = uri.lastPathSegment

        if (isProductActivityRunning(context, productId)) {
            // Activity already running - bring to front
            val intent = Intent(context, ProductActivity::class.java).apply {
                flags = Intent.FLAG_ACTIVITY_REORDER_TO_FRONT
                putExtra("product_id", productId)
            }
            context.startActivity(intent)
        } else {
            // Activity not running - create new
            val intent = Intent(context, ProductActivity::class.java).apply {
                putExtra("product_id", productId)
            }
            context.startActivity(intent)
        }
    }

    private fun isProductActivityRunning(context: Context, productId: String?): Boolean {
        val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
        val tasks = activityManager.appTasks

        for (task in tasks) {
            val taskInfo = task.taskInfo
            if (taskInfo.topActivity?.className == ProductActivity::class.java.name) {
                // Check if same product
                // This is simplified - actual implementation would need IPC
                return true
            }
        }
        return false
    }
}
```

### Solution 5: Trampoline Activity Pattern

Use intermediate activity to control navigation:

```xml
<!-- Trampoline activity receives all deeplinks -->
<activity
    android:name=".DeeplinkActivity"
    android:theme="@android:style/Theme.NoDisplay"
    android:excludeFromRecents="true"
    android:noHistory="true">
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data
            android:scheme="https"
            android:host="www.example.com" />
    </intent-filter>
</activity>

<!-- Actual activity with singleTop -->
<activity
    android:name=".ProductActivity"
    android:launchMode="singleTop" />
```

```kotlin
class DeeplinkActivity : Activity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val data = intent.data

        when (data?.pathSegments?.firstOrNull()) {
            "product" -> {
                val intent = Intent(this, ProductActivity::class.java).apply {
                    flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
                    putExtra("product_id", data.lastPathSegment)
                }
                startActivity(intent)
            }
            "category" -> {
                // Handle other routes
            }
        }

        finish() // Always finish trampoline
    }
}
```

### Comparison of Solutions

| Solution | Pros | Cons | Use Case |
|----------|------|------|----------|
| singleTop | Simple, handles top duplicates | Allows duplicates if not on top | Most deeplinks |
| singleTask | Single instance, clears above | Aggressive clearing | Main/Home activity |
| Intent flags | Flexible, programmatic | Must remember to apply | Dynamic control |
| Navigation Component | Modern, type-safe | Learning curve | New projects |
| Trampoline | Full control | Extra activity | Complex routing |

### Complete Example

```kotlin
// DeeplinkActivity.kt
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
                    flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or
                            Intent.FLAG_ACTIVITY_SINGLE_TOP
                    putExtra("product_id", data.lastPathSegment)
                }
            }
            data.path?.startsWith("/user") == true -> {
                Intent(this, ProfileActivity::class.java).apply {
                    flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or
                            Intent.FLAG_ACTIVITY_SINGLE_TOP
                    putExtra("user_id", data.lastPathSegment)
                }
            }
            else -> {
                Intent(this, MainActivity::class.java).apply {
                    flags = Intent.FLAG_ACTIVITY_CLEAR_TOP
                }
            }
        }

        startActivity(targetIntent)
        finish()
    }
}

// ProductActivity.kt
class ProductActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_product)

        handleIntent(intent)
    }

    override fun onNewIntent(intent: Intent) {
        super.onNewIntent(intent)
        setIntent(intent)
        handleIntent(intent)
    }

    private fun handleIntent(intent: Intent) {
        val productId = intent.getStringExtra("product_id")
        loadProduct(productId)
    }

    private fun loadProduct(id: String?) {
        // Load and display product
    }
}
```

### Best Practices

1. **Use singleTop** for most deeplink targets
2. **Implement onNewIntent()** to handle updates
3. **Call setIntent()** in onNewIntent to update current intent
4. **Use Navigation Component** for new projects
5. **Test thoroughly** with different navigation states
6. **Consider Trampoline pattern** for complex routing
7. **Log deeplink handling** for debugging

## Ответ (RU)
Чтобы избежать множественного открытия одного и того же Activity при использовании deeplink, можно настроить launchMode в AndroidManifest.xml. Например, установите launchMode="singleTop" или "singleTask", чтобы предотвратить создание новых экземпляров. Также используйте флаги в интентах, такие как FLAG_ACTIVITY_CLEAR_TOP и FLAG_ACTIVITY_SINGLE_TOP. Переопределяйте метод onNewIntent() для обработки новых данных, если Activity уже существует в стеке задач.

## Related Topics
- Launch modes
- Intent flags
- Deep linking
- Navigation Component
- onNewIntent()

---

## Related Questions

### Related (Medium)
- [[q-activity-navigation-how-it-works--android--medium]] - Navigation, Activity
- [[q-compose-navigation-advanced--jetpack-compose--medium]] - Navigation
- [[q-compose-navigation-advanced--android--medium]] - Navigation
- [[q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]] - Activity
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Activity

### Advanced (Harder)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - Activity
