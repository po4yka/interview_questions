---
id: android-341
title: Navigation Methods Android / Методы навигации Android
aliases: [Navigation Methods, Методы навигации]
topic: android
subtopics:
  - activity
  - ui-navigation
question_kind: theory
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-activity
  - q-navigation-methods-android--android--medium
  - q-navigation-methods-in-android--android--medium
  - q-tasks-back-stack--android--medium
  - q-what-is-activity-and-what-is-it-used-for--android--medium
  - q-what-navigation-methods-do-you-know--android--medium
created: 2025-10-15
updated: 2025-11-10
tags: [android/activity, android/ui-navigation, difficulty/medium, intent, navigation, startActivity]


date created: Saturday, November 1st 2025, 12:47:09 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---
# Вопрос (RU)

> Какие существуют способы навигации в Android-приложениях на Kotlin?

# Question (EN)

> What navigation methods exist in Kotlin for Android applications?

---

## Ответ (RU)

Навигация в Android-приложениях на Kotlin может быть реализована несколькими основными способами, в зависимости от архитектуры и требований приложения.

### 1. Jetpack Navigation Component (NavHostFragment + NavController)

Современный рекомендуемый подход, основанный на графах навигации и (опционально) типобезопасной передаче аргументов.

```xml
// XML-граф навигации (res/navigation/nav_graph.xml)
<navigation xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/nav_graph"
    app:startDestination="@id/homeFragment">

    <fragment
        android:id="@+id/homeFragment"
        android:name="com.example.HomeFragment"
        android:label="Home">
        <action
            android:id="@+id/action_home_to_details"
            app:destination="@id/detailsFragment" />
    </fragment>

    <fragment
        android:id="@+id/detailsFragment"
        android:name="com.example.DetailsFragment"
        android:label="Details">
        <argument
            android:name="itemId"
            app:argType="integer" />
    </fragment>
</navigation>
```

```kotlin
// Activity с NavController
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val navController = findNavController(R.id.nav_host_fragment)
        NavigationUI.setupActionBarWithNavController(this, navController)
    }

    override fun onSupportNavigateUp(): Boolean {
        val navController = findNavController(R.id.nav_host_fragment)
        return navController.navigateUp() || super.onSupportNavigateUp()
    }
}

// Переход из фрагмента с Safe Args
class HomeFragment : Fragment() {
    private fun navigateToDetails(itemId: Int) {
        val action = HomeFragmentDirections.actionHomeToDetails(itemId)
        findNavController().navigate(action)
    }
}
```

```xml
// NavHostFragment в разметке (activity_main.xml)
<androidx.fragment.app.FragmentContainerView
    android:id="@+id/nav_host_fragment"
    android:name="androidx.navigation.fragment.NavHostFragment"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    app:defaultNavHost="true"
    app:navGraph="@navigation/nav_graph" />
```

```kotlin
// Примеры программной навигации во фрагменте
class HomeFragment : Fragment() {
    private fun navigate() {
        // Простой переход
        findNavController().navigate(R.id.detailsFragment)

        // С аргументами через Bundle
        val bundle = bundleOf("itemId" to 42)
        findNavController().navigate(R.id.detailsFragment, bundle)

        // С использованием NavOptions
        val navOptions = NavOptions.Builder()
            .setEnterAnim(R.anim.slide_in_right)
            .setExitAnim(R.anim.slide_out_left)
            .setPopEnterAnim(R.anim.slide_in_left)
            .setPopExitAnim(R.anim.slide_out_right)
            .build()
        findNavController().navigate(R.id.detailsFragment, bundle, navOptions)

        // Управление back stack
        findNavController().popBackStack()
        findNavController().navigateUp()
    }
}
```

### 2. FragmentTransaction

Ручной способ добавления, замены и удаления фрагментов с явным управлением back stack.

```kotlin
class MainActivity : AppCompatActivity() {

    fun navigateToFragment(fragment: Fragment, addToBackStack: Boolean = true) {
        supportFragmentManager.beginTransaction().apply {
            replace(R.id.fragment_container, fragment)
            if (addToBackStack) {
                addToBackStack(null)
            }
            commit()
        }
    }

    fun addFragment(fragment: Fragment) {
        supportFragmentManager.beginTransaction()
            .add(R.id.fragment_container, fragment)
            .addToBackStack(null)
            .commit()
    }

    fun removeFragment(fragment: Fragment) {
        supportFragmentManager.beginTransaction()
            .remove(fragment)
            .commit()
    }
}

// Использование
val detailsFragment = DetailsFragment.newInstance(itemId)
(mainActivity as MainActivity).navigateToFragment(detailsFragment)
```

### 3. Навигация Через `Intent`

Используется для переходов между `Activity` внутри приложения или между приложениями.

#### Явный (`Explicit`) `Intent` (внутри приложения)

```kotlin
// Переход к конкретной Activity
class MainActivity : AppCompatActivity() {
    private fun navigateToDetails(itemId: Int) {
        val intent = Intent(this, DetailsActivity::class.java).apply {
            putExtra("ITEM_ID", itemId)
            putExtra("ITEM_NAME", "Example Item")
        }
        startActivity(intent)
    }

    // С получением результата (Activity Result API)
    private val detailsLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == RESULT_OK) {
            val data = result.data?.getStringExtra("RESULT_DATA")
            // Обработка результата
        }
    }

    private fun navigateForResult() {
        val intent = Intent(this, DetailsActivity::class.java)
        detailsLauncher.launch(intent)
    }
}

// Получение данных в целевой Activity
class DetailsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val itemId = intent.getIntExtra("ITEM_ID", -1)
        val itemName = intent.getStringExtra("ITEM_NAME")
    }
}
```

#### Неявный (`Implicit`) `Intent` (система Или Другие приложения)

```kotlin
// Открыть веб-страницу
fun openWebPage(url: String) {
    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
    startActivity(intent)
}

// Поделиться текстом
fun shareContent(text: String) {
    val intent = Intent(Intent.ACTION_SEND).apply {
        type = "text/plain"
        putExtra(Intent.EXTRA_TEXT, text)
    }
    startActivity(Intent.createChooser(intent, "Share via"))
}

// Совершить звонок (через dialer)
fun makePhoneCall(phoneNumber: String) {
    val intent = Intent(Intent.ACTION_DIAL).apply {
        data = Uri.parse("tel:$phoneNumber")
    }
    startActivity(intent)
}

// Отправить email
fun sendEmail(email: String, subject: String, body: String) {
    val intent = Intent(Intent.ACTION_SENDTO).apply {
        data = Uri.parse("mailto:")
        putExtra(Intent.EXTRA_EMAIL, arrayOf(email))
        putExtra(Intent.EXTRA_SUBJECT, subject)
        putExtra(Intent.EXTRA_TEXT, body)
    }
    startActivity(intent)
}
```

Важно: `Intent` используется для навигации между компонентами (`Activity`, `Service`, `BroadcastReceiver`), но не для прямой навигации к `Fragment`.

### 4. Deep Links

Deep links позволяют открывать конкретные экраны из уведомлений, браузера или других приложений. В связке с Navigation Component:

```xml
// Deep link в навигационном графе
<fragment
    android:id="@+id/detailsFragment"
    android:name="com.example.DetailsFragment">
    <deepLink
        app:uri="myapp://details/{itemId}" />
</fragment>
```

```xml
<!-- AndroidManifest.xml: intent-filter с autoVerify -->
<intent-filter android:autoVerify="true">
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data
        android:scheme="https"
        android:host="myapp.example.com"
        android:pathPrefix="/details" />
</intent-filter>
```

```kotlin
// Обработка deep link в Activity через NavController
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val navController = findNavController(R.id.nav_host_fragment)
        navController.handleDeepLink(intent)
    }
}

// Создание PendingIntent с deep link (например, для уведомления)
fun createDeepLink(itemId: Int): PendingIntent {
    return findNavController().createDeepLink()
        .setDestination(R.id.detailsFragment)
        .setArguments(bundleOf("itemId" to itemId))
        .createPendingIntent()
}
```

### Сравнение Методов Навигации

| Метод                                      | Когда использовать                               | Плюсы                                              | Минусы                                          |
| ------------------------------------------ | ------------------------------------------------ | -------------------------------------------------- | ----------------------------------------------- |
| Jetpack Navigation (NavHostFragment/NavController) | Современные приложения со сложной навигацией      | Типобезопасные аргументы (Safe Args), визуальный граф, встроенное управление back stack | Нужна настройка графа, дополнительное изучение |
| FragmentTransaction                        | Простые кейсы или высоко кастомные сценарии с фрагментами | Полный контроль без зависимостей Navigation        | Ручное управление back stack и состоянием      |
| Явный `Intent`                             | Навигация между `Activity` внутри приложения     | Простота и прозрачность                           | Создает новые `Activity`, дополнительная нагрузка |
| Неявный `Intent`                           | Переход в другие приложения/системные компоненты | Интеграция с системой и внешними сервисами        | Зависимость от внешних обработчиков            |

### Рекомендации (Best Practices)

1. Использовать Jetpack Navigation Component для новых проектов, когда это уместно.
2. Избегать чрезмерно вложенных фрагментов и сложных стеков навигации.
3. При ручной работе через `FragmentTransaction` явно управлять back stack и состоянием.
4. Применять Safe Args для типобезопасной передачи аргументов.
5. Настраивать deep links для прямого доступа к важным экранам (уведомления, веб-ссылки).
6. Отдавать предпочтение архитектуре с одной `Activity` и фрагментами + Navigation Component, если это упрощает навигацию.

---

## Answer (EN)

Navigation in Android/Kotlin applications can be implemented using several approaches, each suitable for different use cases and architectures.

### 1. Jetpack Navigation Component (NavHostFragment + NavController)

The modern, recommended approach based on navigation graphs and (optionally) type-safe arguments.

```xml
// Define navigation graph in XML (res/navigation/nav_graph.xml)
<navigation xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/nav_graph"
    app:startDestination="@id/homeFragment">

    <fragment
        android:id="@+id/homeFragment"
        android:name="com.example.HomeFragment"
        android:label="Home">
        <action
            android:id="@+id/action_home_to_details"
            app:destination="@id/detailsFragment" />
    </fragment>

    <fragment
        android:id="@+id/detailsFragment"
        android:name="com.example.DetailsFragment"
        android:label="Details">
        <argument
            android:name="itemId"
            app:argType="integer" />
    </fragment>
</navigation>
```

```kotlin
// In Activity
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val navController = findNavController(R.id.nav_host_fragment)
        NavigationUI.setupActionBarWithNavController(this, navController)
    }

    override fun onSupportNavigateUp(): Boolean {
        val navController = findNavController(R.id.nav_host_fragment)
        return navController.navigateUp() || super.onSupportNavigateUp()
    }
}

// Navigate from Fragment using Safe Args
class HomeFragment : Fragment() {
    private fun navigateToDetails(itemId: Int) {
        val action = HomeFragmentDirections.actionHomeToDetails(itemId)
        findNavController().navigate(action)
    }
}
```

```xml
// Setup NavHostFragment in Activity layout (activity_main.xml)
<androidx.fragment.app.FragmentContainerView
    android:id="@+id/nav_host_fragment"
    android:name="androidx.navigation.fragment.NavHostFragment"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    app:defaultNavHost="true"
    app:navGraph="@navigation/nav_graph" />
```

```kotlin
// Programmatic navigation examples in Fragment
class HomeFragment : Fragment() {
    private fun navigate() {
        // Simple navigation
        findNavController().navigate(R.id.detailsFragment)

        // With arguments using Bundle
        val bundle = bundleOf("itemId" to 42)
        findNavController().navigate(R.id.detailsFragment, bundle)

        // With NavOptions
        val navOptions = NavOptions.Builder()
            .setEnterAnim(R.anim.slide_in_right)
            .setExitAnim(R.anim.slide_out_left)
            .setPopEnterAnim(R.anim.slide_in_left)
            .setPopExitAnim(R.anim.slide_out_right)
            .build()
        findNavController().navigate(R.id.detailsFragment, bundle, navOptions)

        // Pop back stack
        findNavController().popBackStack()

        // Navigate up
        findNavController().navigateUp()
    }
}
```

### 2. FragmentTransaction

Manual method for adding, replacing, and removing fragments. Gives full control but requires you to manage the back stack yourself.

```kotlin
class MainActivity : AppCompatActivity() {

    fun navigateToFragment(fragment: Fragment, addToBackStack: Boolean = true) {
        supportFragmentManager.beginTransaction().apply {
            replace(R.id.fragment_container, fragment)
            if (addToBackStack) {
                addToBackStack(null)
            }
            commit()
        }
    }

    fun addFragment(fragment: Fragment) {
        supportFragmentManager.beginTransaction()
            .add(R.id.fragment_container, fragment)
            .addToBackStack(null)
            .commit()
    }

    fun removeFragment(fragment: Fragment) {
        supportFragmentManager.beginTransaction()
            .remove(fragment)
            .commit()
    }
}

// Usage
val detailsFragment = DetailsFragment.newInstance(itemId)
(mainActivity as MainActivity).navigateToFragment(detailsFragment)
```

### 3. Navigation via `Intent`

Used for switching between activities or navigating between apps.

#### Explicit `Intent` (within app)

```kotlin
// Navigate to specific Activity
class MainActivity : AppCompatActivity() {
    private fun navigateToDetails(itemId: Int) {
        val intent = Intent(this, DetailsActivity::class.java).apply {
            putExtra("ITEM_ID", itemId)
            putExtra("ITEM_NAME", "Example Item")
        }
        startActivity(intent)
    }

    // With result
    private val detailsLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == RESULT_OK) {
            val data = result.data?.getStringExtra("RESULT_DATA")
            // Handle result
        }
    }

    private fun navigateForResult() {
        val intent = Intent(this, DetailsActivity::class.java)
        detailsLauncher.launch(intent)
    }
}

// Receive data in target Activity
class DetailsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val itemId = intent.getIntExtra("ITEM_ID", -1)
        val itemName = intent.getStringExtra("ITEM_NAME")
    }
}
```

#### Implicit `Intent` (system or other apps)

```kotlin
// Open web browser
fun openWebPage(url: String) {
    val intent = Intent(Intent.ACTION_VIEW, Uri.parse(url))
    startActivity(intent)
}

// Share content
fun shareContent(text: String) {
    val intent = Intent(Intent.ACTION_SEND).apply {
        type = "text/plain"
        putExtra(Intent.EXTRA_TEXT, text)
    }
    startActivity(Intent.createChooser(intent, "Share via"))
}

// Make phone call
fun makePhoneCall(phoneNumber: String) {
    val intent = Intent(Intent.ACTION_DIAL).apply {
        data = Uri.parse("tel:$phoneNumber")
    }
    startActivity(intent)
}

// Open email app
fun sendEmail(email: String, subject: String, body: String) {
    val intent = Intent(Intent.ACTION_SENDTO).apply {
        data = Uri.parse("mailto:")
        putExtra(Intent.EXTRA_EMAIL, arrayOf(email))
        putExtra(Intent.EXTRA_SUBJECT, subject)
        putExtra(Intent.EXTRA_TEXT, body)
    }
    startActivity(intent)
}
```

### 4. Deep Links Navigation

Deep links allow navigation to a specific screen from outside or inside the app. With the Navigation Component, you declare them in the navigation graph and configure intent-filters in the manifest.

```xml
// Define deep link in navigation graph
<fragment
    android:id="@+id/detailsFragment"
    android:name="com.example.DetailsFragment">
    <deepLink
        app:uri="myapp://details/{itemId}" />
</fragment>
```

```xml
<!-- AndroidManifest.xml: verify host (autoVerify on intent-filter, not in nav graph) -->
<intent-filter android:autoVerify="true">
    <action android:name="android.intent.action.VIEW" />
    <category android:name="android.intent.category.DEFAULT" />
    <category android:name="android.intent.category.BROWSABLE" />
    <data
        android:scheme="https"
        android:host="myapp.example.com"
        android:pathPrefix="/details" />
</intent-filter>
```

```kotlin
// Handle deep link in Activity with NavController
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val navController = findNavController(R.id.nav_host_fragment)
        navController.handleDeepLink(intent)
    }
}

// Create deep link PendingIntent (e.g., for notification)
fun createDeepLink(itemId: Int): PendingIntent {
    return findNavController().createDeepLink()
        .setDestination(R.id.detailsFragment)
        .setArguments(bundleOf("itemId" to itemId))
        .createPendingIntent()
}
```

### Comparison of Navigation Methods

| Method                                      | Use Case                            | Pros                                     | Cons                                    |
| ------------------------------------------- | ----------------------------------- | ---------------------------------------- | --------------------------------------- |
| Jetpack Navigation (NavHostFragment/NavController) | Modern apps with complex navigation | Type-safe (with Safe Args), visual graph, integrated back stack | Learning curve, setup/graph configuration |
| FragmentTransaction                         | Simple or highly custom fragment operations | Full control, no Navigation dependency  | Manual back stack and state management  |
| Explicit `Intent`                           | `Activity` navigation within app    | Simple, clear                           | Creates new activities, more overhead   |
| Implicit `Intent`                           | Cross-app or system navigation      | System integration                      | Depends on external apps/handlers       |

### Best Practices

1. Use Jetpack Navigation Component for new projects where appropriate.
2. Avoid deep nesting of fragments and overly complex back stacks.
3. Handle the back stack explicitly when using FragmentTransactions.
4. Use Safe Args for type-safe argument passing with the Navigation Component.
5. Implement deep links for a better user experience and direct navigation.
6. Prefer a single-`Activity` architecture with fragments + Navigation Component where it simplifies navigation.

---

## Follow-ups

- How does the back stack differ between activities and fragments when using the Navigation Component?
- When would you choose FragmentTransactions over the Navigation Component?
- How do you handle up navigation vs back navigation in a multi-activity app?

## References

- [[c-activity]]

## Related Questions

- [[q-tasks-back-stack--android--medium]]
- [[q-what-is-activity-and-what-is-it-used-for--android--medium]]