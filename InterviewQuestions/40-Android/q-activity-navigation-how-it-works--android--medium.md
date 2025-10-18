---
id: 20251012-122757
title: "Activity Navigation How It Works / Как работает навигация Activity"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-how-did-fragments-appear-and-why-were-they-started-to-be-used--android--hard, q-fast-chat-rendering--android--hard, q-how-to-create-animations-in-android--android--medium]
created: 2025-10-15
tags: [android, android/navigation, back-stack, intent, lifecycle, navigation, difficulty/medium]
---
# Как работает навигация по Activity?

# Question (EN)
> How does Activity navigation work in Android?

# Вопрос (RU)
> Как работает навигация по Activity в Android?

---

## Answer (EN)

Navigation between Activities in Android is managed through Intents, back stack, and task management.

**Main mechanisms:**
- **Explicit Intents**: Launch specific Activity by class name
- **Implicit Intents**: Declare general operation, system chooses appropriate component
- **Back Stack**: Manages Activity history (LIFO - last in, first out)
- **Task Management**: Groups related Activities together
- **Launch Modes**: Control how Activities are instantiated (standard, singleTop, singleTask, singleInstance)

---

## Ответ (RU)

Navigation between different **Activities** in an Android application is an important aspect of managing the user interface flow. Each Activity can be viewed as **a separate screen** with its own user interface. Navigation between them allows users to move from one task to another.

## Main Navigation Mechanisms

### 1. Intents (Explicit and Implicit)

**Explicit Intents** - Used when you know the specific Activity you want to launch. They directly point to the Activity class to open.

**Implicit Intents** - Don't directly specify the Activity class. Instead, they declare a general operation that the application should perform and let the system determine the most suitable component to handle it (e.g., opening a web page or sending data between apps).

**Explicit Intent Example:**

```kotlin
// Navigate to a specific Activity
val intent = Intent(this, SecondActivity::class.java)
startActivity(intent)

// With data
val intent = Intent(this, DetailActivity::class.java)
intent.putExtra("USER_ID", userId)
intent.putExtra("USER_NAME", userName)
startActivity(intent)

// Receiving data in SecondActivity
class SecondActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val userId = intent.getIntExtra("USER_ID", -1)
        val userName = intent.getStringExtra("USER_NAME")
    }
}
```

**Implicit Intent Example:**

```kotlin
// Open web page
val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://www.google.com"))
startActivity(intent)

// Send email
val intent = Intent(Intent.ACTION_SEND).apply {
    type = "text/plain"
    putExtra(Intent.EXTRA_EMAIL, arrayOf("user@example.com"))
    putExtra(Intent.EXTRA_SUBJECT, "Subject")
    putExtra(Intent.EXTRA_TEXT, "Email body")
}
startActivity(Intent.createChooser(intent, "Send Email"))

// Make phone call
val intent = Intent(Intent.ACTION_DIAL, Uri.parse("tel:+1234567890"))
startActivity(intent)

// Share content
val shareIntent = Intent(Intent.ACTION_SEND).apply {
    type = "text/plain"
    putExtra(Intent.EXTRA_TEXT, "Check out this content!")
}
startActivity(Intent.createChooser(shareIntent, "Share via"))
```

---

### 2. Activity Lifecycle and Transition Management

Each Activity has its own **lifecycle** which is critically important for proper implementation of navigation between Activities, especially when handling saving and restoring data.

**Lifecycle during navigation:**

```kotlin
// Activity A → Activity B

// Activity A:
onPause()     // A is partially visible
onStop()      // A is no longer visible (B now visible)

// Activity B:
onCreate()
onStart()
onResume()    // B is now active

// User presses Back:

// Activity B:
onPause()
onStop()
onDestroy()   // B is destroyed

// Activity A:
onRestart()
onStart()
onResume()    // A is active again
```

**Save and restore state:**

```kotlin
class MyActivity : AppCompatActivity() {
    private var counter = 0

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putInt("COUNTER", counter)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        if (savedInstanceState != null) {
            counter = savedInstanceState.getInt("COUNTER", 0)
        }
    }
}
```

---

### 3. Closing Activity

To return to the previous Activity, use `finish()`:

```kotlin
// Close current Activity
finish()

// Close and return result
val resultIntent = Intent()
resultIntent.putExtra("RESULT_DATA", resultValue)
setResult(RESULT_OK, resultIntent)
finish()
```

**Activity for result (modern approach):**

```kotlin
class FirstActivity : AppCompatActivity() {
    private val launcher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == RESULT_OK) {
            val data = result.data?.getStringExtra("RESULT_DATA")
            // Handle result
        }
    }

    fun launchSecondActivity() {
        val intent = Intent(this, SecondActivity::class.java)
        launcher.launch(intent)
    }
}

class SecondActivity : AppCompatActivity() {
    private fun returnResult() {
        val resultIntent = Intent()
        resultIntent.putExtra("RESULT_DATA", "Some result")
        setResult(RESULT_OK, resultIntent)
        finish()
    }
}
```

---

### 4. Intent Flags for Managing Activity Stack

Intents can include various **flags** to manage activity history and transition behavior:

**FLAG_ACTIVITY_CLEAR_TOP:**

```kotlin
// If Activity already running, bring it to top and destroy all above it
val intent = Intent(this, MainActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP
startActivity(intent)
```

**FLAG_ACTIVITY_SINGLE_TOP:**

```kotlin
// If Activity already at top, don't create new instance
val intent = Intent(this, MainActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_SINGLE_TOP
startActivity(intent)

// Handle new intent in existing Activity
override fun onNewIntent(intent: Intent?) {
    super.onNewIntent(intent)
    // Handle new intent data
}
```

**FLAG_ACTIVITY_NEW_TASK:**

```kotlin
// Start Activity in a new task
val intent = Intent(this, MainActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
startActivity(intent)
```

**FLAG_ACTIVITY_CLEAR_TASK:**

```kotlin
// Clear entire task and start fresh
val intent = Intent(this, MainActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
startActivity(intent)
```

**Common combinations:**

```kotlin
// Logout - clear everything and go to login
val intent = Intent(this, LoginActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
startActivity(intent)
finish()

// Deep link - clear top and use single top
val intent = Intent(this, MainActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
startActivity(intent)
```

---

### 5. Back Stack Management

Android maintains a **back stack** of Activities:

```
User Flow:
A → B → C → D

Back Stack:
[A, B, C, D]  ← D is on top (visible)

User presses Back:
[A, B, C]     ← C is now visible, D destroyed

User presses Back:
[A, B]        ← B is now visible, C destroyed
```

**Control back stack behavior:**

```kotlin
// Add to back stack (default)
startActivity(intent)

// Clear back stack
val intent = Intent(this, MainActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TASK or Intent.FLAG_ACTIVITY_NEW_TASK
startActivity(intent)

// Don't add to history
val intent = Intent(this, SplashActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_NO_HISTORY
startActivity(intent)
```

---

### 6. Navigation Component (Modern Approach)

Modern Android applications often use **Navigation Component** which simplifies navigation between Fragments and Activities, ensures correct back stack management, and improves UI flow visualization.

**Setup:**

```kotlin
// build.gradle
dependencies {
    implementation "androidx.navigation:navigation-fragment-ktx:2.7.0"
    implementation "androidx.navigation:navigation-ui-ktx:2.7.0"
}
```

**Navigation Graph (res/navigation/nav_graph.xml):**

```xml
<navigation
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/nav_graph"
    app:startDestination="@id/homeFragment">

    <fragment
        android:id="@+id/homeFragment"
        android:name="com.example.HomeFragment">
        <action
            android:id="@+id/action_home_to_detail"
            app:destination="@id/detailFragment" />
    </fragment>

    <fragment
        android:id="@+id/detailFragment"
        android:name="com.example.DetailFragment" />
</navigation>
```

**Usage:**

```kotlin
// Navigate
findNavController().navigate(R.id.action_home_to_detail)

// With arguments
val bundle = bundleOf("userId" to userId)
findNavController().navigate(R.id.action_home_to_detail, bundle)

// Navigate back
findNavController().navigateUp()
```

---

## Summary

**Activity navigation in Android involves:**

1. **Intents** - Explicit (specific Activity) and Implicit (system chooses)
2. **Lifecycle management** - Save/restore state during transitions
3. **finish()** - Close Activity and return to previous
4. **Intent flags** - Control back stack behavior (CLEAR_TOP, SINGLE_TOP, etc.)
5. **Back stack** - Managed by Android, tracks Activity history
6. **Navigation Component** - Modern approach for Fragment/Activity navigation

**Best Practices:**
- Use Navigation Component for complex navigation flows
- Always save state in `onSaveInstanceState()`
- Use appropriate flags to control back stack
- Prefer Fragments over Activities for in-app navigation
- Handle `onNewIntent()` when using SINGLE_TOP

## Ответ (RU)

Навигация между Activity в Android управляется через Intent, стек возврата (back stack) и управление задачами (task management).

**Основные механизмы:**
- **Явные Intent**: Запускают конкретную Activity по имени класса
- **Неявные Intent**: Объявляют общую операцию, система выбирает подходящий компонент
- **Back Stack**: Управляет историей Activity (LIFO - последним пришел, первым вышел)
- **Task Management**: Группирует связанные Activity вместе
- **Launch Modes**: Контролируют создание экземпляров Activity (standard, singleTop, singleTask, singleInstance)

### Основные механизмы навигации

#### 1. Intent (Явные и Неявные)

**Явные Intent** - используются когда вы знаете конкретную Activity, которую хотите запустить. Они напрямую указывают на класс Activity для открытия.

**Неявные Intent** - не указывают напрямую класс Activity. Вместо этого они объявляют общую операцию, которую должно выполнить приложение, и позволяют системе определить наиболее подходящий компонент для её обработки (например, открытие веб-страницы или отправка данных между приложениями).

**Пример явного Intent:**

```kotlin
// Переход к конкретной Activity
val intent = Intent(this, SecondActivity::class.java)
startActivity(intent)

// С данными
val intent = Intent(this, DetailActivity::class.java)
intent.putExtra("USER_ID", userId)
intent.putExtra("USER_NAME", userName)
startActivity(intent)

// Получение данных в SecondActivity
class SecondActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        val userId = intent.getIntExtra("USER_ID", -1)
        val userName = intent.getStringExtra("USER_NAME")
    }
}
```

**Пример неявного Intent:**

```kotlin
// Открыть веб-страницу
val intent = Intent(Intent.ACTION_VIEW, Uri.parse("https://www.google.com"))
startActivity(intent)

// Отправить email
val intent = Intent(Intent.ACTION_SEND).apply {
    type = "text/plain"
    putExtra(Intent.EXTRA_EMAIL, arrayOf("user@example.com"))
    putExtra(Intent.EXTRA_SUBJECT, "Тема")
    putExtra(Intent.EXTRA_TEXT, "Текст письма")
}
startActivity(Intent.createChooser(intent, "Отправить Email"))

// Совершить звонок
val intent = Intent(Intent.ACTION_DIAL, Uri.parse("tel:+1234567890"))
startActivity(intent)

// Поделиться контентом
val shareIntent = Intent(Intent.ACTION_SEND).apply {
    type = "text/plain"
    putExtra(Intent.EXTRA_TEXT, "Посмотрите на этот контент!")
}
startActivity(Intent.createChooser(shareIntent, "Поделиться через"))
```

#### 2. Жизненный цикл Activity и управление переходами

Каждая Activity имеет свой **жизненный цикл**, который критически важен для правильной реализации навигации между Activity, особенно при обработке сохранения и восстановления данных.

**Жизненный цикл при навигации:**

```kotlin
// Activity A → Activity B

// Activity A:
onPause()     // A частично видима
onStop()      // A больше не видна (B теперь видна)

// Activity B:
onCreate()
onStart()
onResume()    // B теперь активна

// Пользователь нажимает Назад:

// Activity B:
onPause()
onStop()
onDestroy()   // B уничтожена

// Activity A:
onRestart()
onStart()
onResume()    // A снова активна
```

**Сохранение и восстановление состояния:**

```kotlin
class MyActivity : AppCompatActivity() {
    private var counter = 0

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putInt("COUNTER", counter)
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        if (savedInstanceState != null) {
            counter = savedInstanceState.getInt("COUNTER", 0)
        }
    }
}
```

#### 3. Закрытие Activity

Для возврата к предыдущей Activity используйте `finish()`:

```kotlin
// Закрыть текущую Activity
finish()

// Закрыть и вернуть результат
val resultIntent = Intent()
resultIntent.putExtra("RESULT_DATA", resultValue)
setResult(RESULT_OK, resultIntent)
finish()
```

**Activity для результата (современный подход):**

```kotlin
class FirstActivity : AppCompatActivity() {
    private val launcher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == RESULT_OK) {
            val data = result.data?.getStringExtra("RESULT_DATA")
            // Обработать результат
        }
    }

    fun launchSecondActivity() {
        val intent = Intent(this, SecondActivity::class.java)
        launcher.launch(intent)
    }
}

class SecondActivity : AppCompatActivity() {
    private fun returnResult() {
        val resultIntent = Intent()
        resultIntent.putExtra("RESULT_DATA", "Какой-то результат")
        setResult(RESULT_OK, resultIntent)
        finish()
    }
}
```

#### 4. Флаги Intent для управления стеком Activity

Intent могут включать различные **флаги** для управления историей активностей и поведением переходов:

**FLAG_ACTIVITY_CLEAR_TOP:**

```kotlin
// Если Activity уже запущена, поднять её наверх и уничтожить все над ней
val intent = Intent(this, MainActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP
startActivity(intent)
```

**FLAG_ACTIVITY_SINGLE_TOP:**

```kotlin
// Если Activity уже наверху, не создавать новый экземпляр
val intent = Intent(this, MainActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_SINGLE_TOP
startActivity(intent)

// Обработать новый intent в существующей Activity
override fun onNewIntent(intent: Intent?) {
    super.onNewIntent(intent)
    // Обработать данные нового intent
}
```

**FLAG_ACTIVITY_NEW_TASK:**

```kotlin
// Запустить Activity в новой задаче
val intent = Intent(this, MainActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK
startActivity(intent)
```

**FLAG_ACTIVITY_CLEAR_TASK:**

```kotlin
// Очистить всю задачу и начать заново
val intent = Intent(this, MainActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
startActivity(intent)
```

**Распространенные комбинации:**

```kotlin
// Выход - очистить всё и перейти к логину
val intent = Intent(this, LoginActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
startActivity(intent)
finish()

// Deep link - очистить верх и использовать single top
val intent = Intent(this, MainActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TOP or Intent.FLAG_ACTIVITY_SINGLE_TOP
startActivity(intent)
```

#### 5. Управление стеком возврата

Android поддерживает **back stack** из Activity:

```
Поток пользователя:
A → B → C → D

Back Stack:
[A, B, C, D]  ← D наверху (видна)

Пользователь нажимает Назад:
[A, B, C]     ← C теперь видна, D уничтожена

Пользователь нажимает Назад:
[A, B]        ← B теперь видна, C уничтожена
```

**Контроль поведения back stack:**

```kotlin
// Добавить в back stack (по умолчанию)
startActivity(intent)

// Очистить back stack
val intent = Intent(this, MainActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_CLEAR_TASK or Intent.FLAG_ACTIVITY_NEW_TASK
startActivity(intent)

// Не добавлять в историю
val intent = Intent(this, SplashActivity::class.java)
intent.flags = Intent.FLAG_ACTIVITY_NO_HISTORY
startActivity(intent)
```

#### 6. Navigation Component (Современный подход)

Современные Android приложения часто используют **Navigation Component**, который упрощает навигацию между Fragment и Activity, обеспечивает корректное управление back stack и улучшает визуализацию потока UI.

**Настройка:**

```kotlin
// build.gradle
dependencies {
    implementation "androidx.navigation:navigation-fragment-ktx:2.7.0"
    implementation "androidx.navigation:navigation-ui-ktx:2.7.0"
}
```

**Navigation Graph (res/navigation/nav_graph.xml):**

```xml
<navigation
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/nav_graph"
    app:startDestination="@id/homeFragment">

    <fragment
        android:id="@+id/homeFragment"
        android:name="com.example.HomeFragment">
        <action
            android:id="@+id/action_home_to_detail"
            app:destination="@id/detailFragment" />
    </fragment>

    <fragment
        android:id="@+id/detailFragment"
        android:name="com.example.DetailFragment" />
</navigation>
```

**Использование:**

```kotlin
// Навигация
findNavController().navigate(R.id.action_home_to_detail)

// С аргументами
val bundle = bundleOf("userId" to userId)
findNavController().navigate(R.id.action_home_to_detail, bundle)

// Навигация назад
findNavController().navigateUp()
```

### Резюме

**Навигация Activity в Android включает:**

1. **Intent** - Явные (конкретная Activity) и Неявные (система выбирает)
2. **Управление жизненным циклом** - Сохранение/восстановление состояния при переходах
3. **finish()** - Закрытие Activity и возврат к предыдущей
4. **Флаги Intent** - Контроль поведения back stack (CLEAR_TOP, SINGLE_TOP и т.д.)
5. **Back stack** - Управляется Android, отслеживает историю Activity
6. **Navigation Component** - Современный подход для навигации Fragment/Activity

**Лучшие практики:**
- Используйте Navigation Component для сложных потоков навигации
- Всегда сохраняйте состояние в `onSaveInstanceState()`
- Используйте соответствующие флаги для контроля back stack
- Предпочитайте Fragment вместо Activity для внутриприложенческой навигации
- Обрабатывайте `onNewIntent()` при использовании SINGLE_TOP


---

## Related Questions

### Related (Medium)
- [[q-how-to-handle-the-situation-where-activity-can-open-multiple-times-due-to-deeplink--android--medium]] - Navigation, Activity
- [[q-compose-navigation-advanced--jetpack-compose--medium]] - Navigation
- [[q-compose-navigation-advanced--android--medium]] - Navigation
- [[q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]] - Activity
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Activity

### Advanced (Harder)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - Activity
