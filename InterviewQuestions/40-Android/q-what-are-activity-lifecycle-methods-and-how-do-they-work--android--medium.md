---
id: android-343
title: Activity Lifecycle Methods / Методы жизненного цикла Activity
aliases: [Activity Lifecycle Methods, Методы жизненного цикла Activity]
topic: android
subtopics:
  - activity
  - lifecycle
question_kind: theory
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
status: reviewed
moc: moc-android
related:
  - c-activity-lifecycle
  - q-activity-lifecycle-methods--android--medium
  - q-fragment-vs-activity-lifecycle--android--medium
  - q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium
  - q-what-happens-to-the-old-activity-when-the-system-starts-a-new-one--android--hard
  - q-what-is-activity-and-what-is-it-used-for--android--medium
created: 2025-10-15
updated: 2025-11-10
tags: [android/activity, android/lifecycle, difficulty/medium, lifecycle, onCreate, onResume, onStart]

date created: Saturday, November 1st 2025, 12:47:06 pm
date modified: Tuesday, November 25th 2025, 8:53:56 pm
---

# Вопрос (RU)
> Методы жизненного цикла `Activity`

# Question (EN)
> `Activity` Lifecycle Methods

---

## Ответ (RU)
Методы жизненного цикла `Activity` — это колбэк-функции, которые система Android вызывает на разных этапах жизни `Activity`. Понимание этих методов критически важно для правильного управления ресурсами, сохранения состояния и обеспечения плавного пользовательского опыта.

### Жизненный Цикл `Activity`

```
   Activity запущена

           ↓

     onCreate() ← Activity создаётся

          ↓

     onStart()  ← Activity становится видимой

          ↓

     onResume()  ← Activity на переднем плане и интерактивна

          ↓

    Состояние Running

          ↓

     onPause()  ← Activity теряет фокус (другая Activity перекрывает её)

          ↓

     onStop()   ← Activity больше не видна

          ↓

     onDestroy()  ← Activity уничтожается
```

### Полный Набор Методов Жизненного Цикла (пример)

```kotlin
class MainActivity : AppCompatActivity() {

    // 1. onCreate() - Activity создаётся
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("Lifecycle", "onCreate called")

        // Устанавливаем layout
        setContentView(R.layout.activity_main)

        // Инициализируем UI
        setupViews()

        // Восстанавливаем состояние, если есть
        savedInstanceState?.let {
            restoreState(it)
        }

        // Одноразовая инициализация данных
        initializeData()
    }

    // 2. onStart() - Activity становится видимой
    override fun onStart() {
        super.onStart()
        Log.d("Lifecycle", "onStart called")

        // Запускаем анимации, регистрируем слушателей, завязанных на видимость
        startAnimations()
        registerReceivers()
    }

    // 3. onResume() - Activity на переднем плане и интерактивна
    override fun onResume() {
        super.onResume()
        Log.d("Lifecycle", "onResume called")

        // Возобновляем камеру, сенсоры, локацию
        startCamera()
        startLocationUpdates()

        // Обновляем данные при необходимости
        refreshData()
    }

    // 4. onPause() - Activity вот-вот потеряет фокус
    override fun onPause() {
        Log.d("Lifecycle", "onPause called")

        // Пауза камеры, сенсоров, видео
        pauseCamera()
        pauseVideo()

        // Сохраняем важные пользовательские данные (черновики и т.п.)
        saveDraft()

        // Останавливаем операции, завязанные на foreground
        stopLocationUpdates()

        super.onPause()
    }

    // 5. onStop() - Activity больше не видна
    override fun onStop() {
        Log.d("Lifecycle", "onStop called")

        // Останавливаем анимации
        stopAnimations()

        // Отписываемся от слушателей, ресиверов и т.п.
        unregisterReceivers()

        // Сохраняем состояние UI при необходимости
        saveState()

        super.onStop()
    }

    // 6. onDestroy() - Activity уничтожается
    override fun onDestroy() {
        Log.d("Lifecycle", "onDestroy called")

        // Освобождаем ресурсы
        cleanupResources()

        // Отменяем корутины / фоновые задачи, связанные с Activity
        cancelBackgroundTasks()

        // Освобождаем ссылки, если нужно
        releaseMemory()

        super.onDestroy()
    }

    // 7. onRestart() - Activity перезапускается после onStop()
    override fun onRestart() {
        super.onRestart()
        Log.d("Lifecycle", "onRestart called")

        // Вызывается перед onStart() при возврате из состояния Stopped
        reloadData()
    }

    // Вспомогательные методы
    private fun setupViews() { /* ... */ }
    private fun initializeData() { /* ... */ }
    private fun restoreState(savedInstanceState: Bundle) { /* ... */ }
    private fun startAnimations() { /* ... */ }
    private fun registerReceivers() { /* ... */ }
    private fun startCamera() { /* ... */ }
    private fun startLocationUpdates() { /* ... */ }
    private fun refreshData() { /* ... */ }
    private fun pauseCamera() { /* ... */ }
    private fun pauseVideo() { /* ... */ }
    private fun saveDraft() { /* ... */ }
    private fun stopLocationUpdates() { /* ... */ }
    private fun stopAnimations() { /* ... */ }
    private fun unregisterReceivers() { /* ... */ }
    private fun saveState() { /* ... */ }
    private fun cleanupResources() { /* ... */ }
    private fun cancelBackgroundTasks() { /* ... */ }
    private fun releaseMemory() { /* ... */ }
    private fun reloadData() { /* ... */ }
}
```

### Типичные Сценарии Жизненного Цикла

#### Сценарий 1: Запуск Приложения

```
onCreate() → onStart() → onResume() → [Running]
```

#### Сценарий 2: Пользователь Нажимает Home

```
[Running] → onPause() → onStop() → [Stopped]
```

#### Сценарий 3: Возврат В Приложение

```
[Stopped] → onRestart() → onStart() → onResume() → [Running]
```

#### Сценарий 4: Поворот Экрана

```
onPause() → onStop() → onDestroy() →
onCreate() → onStart() → onResume()
```

#### Сценарий 5: Диалог Поверх (`Activity` Частично видна)

```
[Running] → onPause() → [Paused, Activity может оставаться частично видимой]
```

Например, при показе диалоговой или прозрачной `Activity`/`Fragment` поверх.

#### Сценарий 6: Другая `Activity` Полностью Перекрывает

```
onPause() → onStop() → [Stopped]
```

### Сохранение И Восстановление Состояния

```kotlin
class DataActivity : AppCompatActivity() {

    private var userInput: String = ""
    private var counter: Int = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_data)

        // Восстановление состояния после конфигурационных изменений или пересоздания процесса
        savedInstanceState?.let {
            userInput = it.getString("USER_INPUT", "")
            counter = it.getInt("COUNTER", 0)
            Log.d("Lifecycle", "Restored: input=$userInput, counter=$counter")
        }

        updateUI()
    }

    // Сохраняем временное состояние UI до возможного уничтожения Activity
    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        outState.putString("USER_INPUT", userInput)
        outState.putInt("COUNTER", counter)

        Log.d("Lifecycle", "State saved: input=$userInput, counter=$counter")
    }

    // Вызывается только при наличии savedInstanceState и после onStart()
    override fun onRestoreInstanceState(savedInstanceState: Bundle) {
        super.onRestoreInstanceState(savedInstanceState)

        // Альтернативное место восстановления состояния вместо onCreate
        userInput = savedInstanceState.getString("USER_INPUT", "")
        counter = savedInstanceState.getInt("COUNTER", 0)

        Log.d("Lifecycle", "State restored in onRestoreInstanceState")
        updateUI()
    }

    private fun updateUI() {
        findViewById<TextView>(R.id.inputText).text = userInput
        findViewById<TextView>(R.id.counterText).text = "Count: $counter"
    }
}
```

### Компоненты, Учитывающие Жизненный Цикл

Современный подход — использовать lifecycle-aware компоненты (`ViewModel`, `SavedStateHandle`, `LiveData`, `Flow` с `lifecycleScope`, `LifecycleObserver`).

```kotlin
class ModernActivity : AppCompatActivity() {

    private val viewModel: MyViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_modern)

        // Наблюдение за LiveData — автоматически учитывает жизненный цикл Activity
        viewModel.userData.observe(this) { user ->
            updateUI(user)
        }

        // Запуск корутины с учётом жизненного цикла
        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                handleState(state)
            }
        }

        // Наблюдение за событиями жизненного цикла через LifecycleObserver
        lifecycle.addObserver(MyLifecycleObserver())
    }

    private fun updateUI(user: User) { /* ... */ }
    private fun handleState(state: UiState) { /* ... */ }
}

// Пользовательский наблюдатель жизненного цикла
class MyLifecycleObserver : DefaultLifecycleObserver {

    override fun onCreate(owner: LifecycleOwner) {
        Log.d("Observer", "onCreate")
    }

    override fun onStart(owner: LifecycleOwner) {
        Log.d("Observer", "onStart")
    }

    override fun onResume(owner: LifecycleOwner) {
        Log.d("Observer", "onResume")
    }

    override fun onPause(owner: LifecycleOwner) {
        Log.d("Observer", "onPause")
    }

    override fun onStop(owner: LifecycleOwner) {
        Log.d("Observer", "onStop")
    }

    override fun onDestroy(owner: LifecycleOwner) {
        Log.d("Observer", "onDestroy")
    }
}
```

### Конфигурационные Изменения

```kotlin
class ConfigActivity : AppCompatActivity() {

    private var expensiveData: LargeData? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_config)

        // Проверяем, не сохранены ли данные между пересозданиями (устаревший подход)
        @Suppress("DEPRECATION")
        val retained = lastCustomNonConfigurationInstance as? LargeData

        expensiveData = retained ?: loadExpensiveData()
    }

    // Устаревший способ удержания данных при конфигурационных изменениях
    @Deprecated("Use ViewModel instead")
    override fun onRetainCustomNonConfigurationInstance(): Any? {
        return expensiveData
    }

    private fun loadExpensiveData(): LargeData {
        // Дорогая операция
        return LargeData()
    }
}

// Современный подход: использовать ViewModel
class ModernConfigActivity : AppCompatActivity() {

    private val viewModel: DataViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_config)

        // ViewModel переживает конфигурационные изменения
        val data = viewModel.expensiveData
    }
}

class DataViewModel : ViewModel() {
    // Переживает конфигурационные изменения
    val expensiveData = loadExpensiveData()

    private fun loadExpensiveData(): LargeData {
        return LargeData()
    }
}

data class LargeData(val items: List<String> = emptyList())
```

### Обработка Кнопки Назад

```kotlin
class BackHandlingActivity : AppCompatActivity() {

    private val onBackPressedCallback = object : OnBackPressedCallback(true) {
        override fun handleOnBackPressed() {
            // Кастомная обработка "Назад"
            if (hasUnsavedChanges()) {
                showSaveDialog()
            } else {
                // Разрешаем стандартное поведение
                isEnabled = false
                onBackPressedDispatcher.onBackPressed()
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_back)

        // Современный способ перехвата кнопки "Назад"
        onBackPressedDispatcher.addCallback(this, onBackPressedCallback)
    }

    private fun hasUnsavedChanges(): Boolean = false
    private fun showSaveDialog() { /* ... */ }
}
```

### Тайминг Вызова Методов Жизненного Цикла

```kotlin
class TimingActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("Timing", "onCreate: Activity ещё не видна")
        // Здесь безопасно создавать и настраивать UI, но пользователь его ещё не видит
    }

    override fun onStart() {
        super.onStart()
        Log.d("Timing", "onStart: Activity становится видимой")
        // Окно становится видимым, но сложное взаимодействие лучше отложить до onResume()
    }

    override fun onResume() {
        super.onResume()
        Log.d("Timing", "onResume: Activity интерактивна")
        // Окно видно и доступно для ввода
    }

    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        Log.d("Timing", "onWindowFocusChanged: hasFocus=$hasFocus")
        // Часто вызывается после onResume(), когда окно получает фокус
        // Подходящее место для анимаций, завязанных на фокус
        if (hasFocus) {
            startAnimations()
        }
    }

    private fun startAnimations() { /* ... */ }
}
```

### Сводная Таблица Методов Жизненного Цикла

| Метод | Когда вызывается | Видимость | Интерактивность | Что делать |
|-------|------------------|-----------|-----------------|------------|
| onCreate() | `Activity` создана | Нет | Нет | Инициализация UI, `setContentView`, начальное восстановление состояния |
| onStart() | Становится видимой | Да (начинает) | Ещё нет полностью | Регистрировать приёмники, запускать лёгкие анимации |
| onResume() | На переднем плане | Да | Да | Начать/возобновить взаимодействие, камеру, сенсоры, обновить данные |
| onPause() | Теряет фокус | Да (перекрывается) | Частично/завершается | Поставить на паузу работу, сохранить черновики, освободить foreground-ресурсы |
| onStop() | Не видна | Нет | Нет | Остановить анимации, отписаться от слушателей, при необходимости сохранить состояние |
| onDestroy() | Уничтожается | Нет | Нет | Финальная очистка ресурсов, отмена задач |
| onRestart() | Перед возвратом из Stopped | Нет | Нет | Подготовка к повторному входу перед `onStart()` |

### Лучшие Практики

1. Корректно вызывать `super` в методах жизненного цикла:
   - Обычно в начале: `onCreate`, `onStart`, `onResume`, `onRestart`.
   - В `onPause`, `onStop` нередко выполняют свою логику до вызова `super`, чтобы гарантировать освобождение ресурсов до продолжения потока жизненного цикла.
   - Всегда вызывать `super.onSaveInstanceState()` (до или после записи своих данных — в зависимости от требований).
2. Использовать `onCreate()` для одноразовой инициализации (view, адаптеры, DI).
3. Привязанные к foreground ресурсы (камера, сенсоры, слушатели) — в `onResume()`/`onPause()`.
4. Временное состояние UI — в `onSaveInstanceState()` (для конфигурационных изменений и убийства процесса).
5. Для долгоживущих данных и конфигурационных изменений — `ViewModel` и `SavedStateHandle`.
6. Использовать lifecycle-aware компоненты (`LiveData`, `Flow` с `lifecycleScope`, `LifecycleObserver`).
7. Освобождать ресурсы в `onDestroy()`, учитывая, что при убийстве процесса метод может не вызваться.
8. Не выполнять долгих/блокирующих операций в колбэках жизненного цикла на главном потоке.
9. Корректно обрабатывать конфигурационные изменения (ротация, multi-window, locale и т.д.).
10. Тестировать все распространённые сценарии: навигация, ротация, возврат/выход, multi-window, убийство процесса.

### Типичные Ошибки

```kotlin
// НЕПРАВИЛЬНО: Долгая операция в onCreate
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    Thread.sleep(5000) // Блокирует UI!
}

// ПРАВИЛЬНО: Использовать фоновый поток / корутину
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    lifecycleScope.launch {
        withContext(Dispatchers.IO) {
            loadData()
        }
    }
}

// НЕПРАВИЛЬНО: Не сохраняем состояние, которое должно пережить ротацию
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    counter = 0 // Потеряется при конфигурационных изменениях
}

// ПРАВИЛЬНО: Сохранить и восстановить состояние
private var counter: Int = 0

override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putInt("counter", counter)
}

override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    counter = savedInstanceState?.getInt("counter") ?: 0
}
```

---

## Answer (EN)
`Activity` lifecycle methods are callback functions that the Android system calls at different stages of an `Activity`'s life. Understanding these methods is crucial for proper resource management, state preservation, and creating a smooth user experience.

### The `Activity` Lifecycle

```
   Activity Launched

           ↓

     onCreate() ← Activity is being created

          ↓

     onStart()  ← Activity is becoming visible

          ↓

     onResume()  ← Activity is in foreground and interactive

          ↓

    Running State

          ↓

     onPause()  ← Activity is about to lose focus (another activity is coming in front)

          ↓

     onStop()   ← Activity is no longer visible

          ↓

     onDestroy()  ← Activity is being destroyed
```

### Complete Lifecycle Methods

```kotlin
class MainActivity : AppCompatActivity() {

    // 1. onCreate() - Activity is being created
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("Lifecycle", "onCreate called")

        // Set content view
        setContentView(R.layout.activity_main)

        // Initialize UI components
        setupViews()

        // Restore saved state if exists
        savedInstanceState?.let {
            restoreState(it)
        }

        // One-time initialization
        initializeData()
    }

    // 2. onStart() - Activity is becoming visible
    override fun onStart() {
        super.onStart()
        Log.d("Lifecycle", "onStart called")

        // Start animations, register listeners that affect visibility
        startAnimations()
        registerReceivers()
    }

    // 3. onResume() - Activity is in foreground and interactive
    override fun onResume() {
        super.onResume()
        Log.d("Lifecycle", "onResume called")

        // Resume camera, sensors, location updates
        startCamera()
        startLocationUpdates()

        // Refresh data if needed
        refreshData()
    }

    // 4. onPause() - Activity is about to lose focus
    override fun onPause() {
        Log.d("Lifecycle", "onPause called")

        // Pause camera, sensors, video playback
        pauseCamera()
        pauseVideo()

        // Save critical user data
        saveDraft()

        // Stop expensive operations that shouldn't run when not in foreground
        stopLocationUpdates()

        super.onPause()
    }

    // 5. onStop() - Activity is no longer visible
    override fun onStop() {
        Log.d("Lifecycle", "onStop called")

        // Stop animations
        stopAnimations()

        // Unregister listeners, receivers, etc.
        unregisterReceivers()

        // Save UI-related state if needed
        saveState()

        super.onStop()
    }

    // 6. onDestroy() - Activity is being destroyed
    override fun onDestroy() {
        Log.d("Lifecycle", "onDestroy called")

        // Clean up resources
        cleanupResources()

        // Cancel coroutines / background tasks tied to this Activity
        cancelBackgroundTasks()

        // Release other references if needed
        releaseMemory()

        super.onDestroy()
    }

    // 7. onRestart() - Activity is restarting after being stopped
    override fun onRestart() {
        super.onRestart()
        Log.d("Lifecycle", "onRestart called")

        // Called before onStart() when returning from stopped state
        reloadData()
    }

    // Helper methods
    private fun setupViews() { /* ... */ }
    private fun initializeData() { /* ... */ }
    private fun restoreState(savedInstanceState: Bundle) { /* ... */ }
    private fun startAnimations() { /* ... */ }
    private fun registerReceivers() { /* ... */ }
    private fun startCamera() { /* ... */ }
    private fun startLocationUpdates() { /* ... */ }
    private fun refreshData() { /* ... */ }
    private fun pauseCamera() { /* ... */ }
    private fun pauseVideo() { /* ... */ }
    private fun saveDraft() { /* ... */ }
    private fun stopLocationUpdates() { /* ... */ }
    private fun stopAnimations() { /* ... */ }
    private fun unregisterReceivers() { /* ... */ }
    private fun saveState() { /* ... */ }
    private fun cleanupResources() { /* ... */ }
    private fun cancelBackgroundTasks() { /* ... */ }
    private fun releaseMemory() { /* ... */ }
    private fun reloadData() { /* ... */ }
}
```

### Common Lifecycle Scenarios

#### Scenario 1: App Launch

```
onCreate() → onStart() → onResume() → [Running]
```

#### Scenario 2: User Presses Home Button

```
[Running] → onPause() → onStop() → [Stopped]
```

#### Scenario 3: User Returns to App

```
[Stopped] → onRestart() → onStart() → onResume() → [Running]
```

#### Scenario 4: Screen Rotation

```
onPause() → onStop() → onDestroy() →
onCreate() → onStart() → onResume()
```

#### Scenario 5: Dialog Appears (`Activity` Still Visible)

```
[Running] → onPause() → [Paused but underlying activity may remain partially visible]
```

(For example, when a dialog-themed or transparent activity/fragment appears on top.)

#### Scenario 6: Another `Activity` Fully Covers It

```
onPause() → onStop() → [Stopped]
```

### State Saving and Restoration

```kotlin
class DataActivity : AppCompatActivity() {

    private var userInput: String = ""
    private var counter: Int = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_data)

        // Restore state after configuration change or process recreation
        savedInstanceState?.let {
            userInput = it.getString("USER_INPUT", "")
            counter = it.getInt("COUNTER", 0)
            Log.d("Lifecycle", "Restored: input=$userInput, counter=$counter")
        }

        updateUI()
    }

    // Save transient UI state before Activity may be destroyed
    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        outState.putString("USER_INPUT", userInput)
        outState.putInt("COUNTER", counter)

        Log.d("Lifecycle", "State saved: input=$userInput, counter=$counter")
    }

    // Called only if there is a savedInstanceState and after onStart()
    override fun onRestoreInstanceState(savedInstanceState: Bundle) {
        super.onRestoreInstanceState(savedInstanceState)

        // Alternative to onCreate restoration
        userInput = savedInstanceState.getString("USER_INPUT", "")
        counter = savedInstanceState.getInt("COUNTER", 0)

        Log.d("Lifecycle", "State restored in onRestoreInstanceState")
        updateUI()
    }

    private fun updateUI() {
        findViewById<TextView>(R.id.inputText).text = userInput
        findViewById<TextView>(R.id.counterText).text = "Count: $counter"
    }
}
```

### Lifecycle-Aware Components

Modern Android development uses lifecycle-aware components:

```kotlin
class ModernActivity : AppCompatActivity() {

    private val viewModel: MyViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_modern)

        // Observe LiveData - automatically respects the Activity's lifecycle
        viewModel.userData.observe(this) { user ->
            updateUI(user)
        }

        // Launch coroutine scoped to lifecycle
        lifecycleScope.launch {
            viewModel.uiState.collect { state ->
                handleState(state)
            }
        }

        // Observe lifecycle events with a LifecycleObserver
        lifecycle.addObserver(MyLifecycleObserver())
    }

    private fun updateUI(user: User) { /* ... */ }
    private fun handleState(state: UiState) { /* ... */ }
}

// Custom lifecycle observer
class MyLifecycleObserver : DefaultLifecycleObserver {

    override fun onCreate(owner: LifecycleOwner) {
        Log.d("Observer", "onCreate")
    }

    override fun onStart(owner: LifecycleOwner) {
        Log.d("Observer", "onStart")
    }

    override fun onResume(owner: LifecycleOwner) {
        Log.d("Observer", "onResume")
    }

    override fun onPause(owner: LifecycleOwner) {
        Log.d("Observer", "onPause")
    }

    override fun onStop(owner: LifecycleOwner) {
        Log.d("Observer", "onStop")
    }

    override fun onDestroy(owner: LifecycleOwner) {
        Log.d("Observer", "onDestroy")
    }
}
```

### Configuration Changes

```kotlin
class ConfigActivity : AppCompatActivity() {

    private var expensiveData: LargeData? = null

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_config)

        // Check if data was retained (deprecated approach)
        @Suppress("DEPRECATION")
        val retained = lastCustomNonConfigurationInstance as? LargeData

        expensiveData = retained ?: loadExpensiveData()
    }

    // Deprecated but shows the concept of retaining data across configuration changes
    @Deprecated("Use ViewModel instead")
    override fun onRetainCustomNonConfigurationInstance(): Any? {
        return expensiveData
    }

    private fun loadExpensiveData(): LargeData {
        // Expensive operation
        return LargeData()
    }
}

// Modern approach: Use ViewModel
class ModernConfigActivity : AppCompatActivity() {

    private val viewModel: DataViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_config)

        // ViewModel survives configuration changes automatically
        val data = viewModel.expensiveData
    }
}

class DataViewModel : ViewModel() {
    // Survives configuration changes
    val expensiveData = loadExpensiveData()

    private fun loadExpensiveData(): LargeData {
        return LargeData()
    }
}

data class LargeData(val items: List<String> = emptyList())
```

### Handling Back Button

```kotlin
class BackHandlingActivity : AppCompatActivity() {

    private val onBackPressedCallback = object : OnBackPressedCallback(true) {
        override fun handleOnBackPressed() {
            // Custom back handling
            if (hasUnsavedChanges()) {
                showSaveDialog()
            } else {
                // Let default back behavior happen
                isEnabled = false
                onBackPressedDispatcher.onBackPressed()
            }
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_back)

        // Modern back handling
        onBackPressedDispatcher.addCallback(this, onBackPressedCallback)
    }

    private fun hasUnsavedChanges(): Boolean = false
    private fun showSaveDialog() { /* ... */ }
}
```

### Lifecycle Method Timing

```kotlin
class TimingActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        Log.d("Timing", "onCreate: Activity not visible yet")
        // Window not visible yet
        // Safe to inflate and configure UI, but user cannot see or interact with it
    }

    override fun onStart() {
        super.onStart()
        Log.d("Timing", "onStart: Activity becoming visible")
        // Window is becoming visible
        // Heavy interaction logic should still wait until onResume()
    }

    override fun onResume() {
        super.onResume()
        Log.d("Timing", "onResume: Activity is interactive")
        // Window visible and interactive
        // Can safely handle user input
    }

    override fun onWindowFocusChanged(hasFocus: Boolean) {
        super.onWindowFocusChanged(hasFocus)
        Log.d("Timing", "onWindowFocusChanged: hasFocus=$hasFocus")
        // Often called after onResume() when window gains focus
        // Good place to start certain animations tied to focus
        if (hasFocus) {
            startAnimations()
        }
    }

    private fun startAnimations() { /* ... */ }
}
```

### Lifecycle Summary Table

| Method | When Called | Visibility | Interactive | What to Do |
|--------|-------------|------------|-------------|------------|
| onCreate() | `Activity` created | No | No | Initialize UI, set content view, restore initial state |
| onStart() | Becoming visible | Yes (becoming) | Not yet fully | Register receivers, start lightweight animations |
| onResume() | In foreground | Yes | Yes | Start/restore UI interactions, resume camera, sensors, refresh data |
| onPause() | About to lose focus | Yes (another window on top) | Partially / ending | Pause ongoing work, commit edits, save drafts, release foreground-only resources |
| onStop() | No longer visible | No | No | Stop animations, unregister listeners, persist state if needed |
| onDestroy() | Being destroyed | No | No | Final cleanup of resources, cancel tasks |
| onRestart() | Restarting after stop | No | No | Prepare to re-enter foreground before onStart() |

### Best Practices

1. Prefer calling `super` at the appropriate point in lifecycle methods:
   - Usually at the beginning for `onCreate`, `onStart`, `onResume`, `onRestart`.
   - For `onPause`, `onStop`, some cases may call `super` after custom logic to ensure cleanup runs before the system continues; be consistent with official samples.
   - Always call `super.onSaveInstanceState()` (can be before or after putting your data, according to your needs).
2. Use `onCreate()` for one-time initialization (views, adapters, dependency wiring).
3. Use `onResume()`/`onPause()` for resources directly tied to foreground visibility (camera, sensors, listeners).
4. Save transient UI state in `onSaveInstanceState()` for configuration changes / process death.
5. Use `ViewModel` (and `SavedStateHandle` when needed) for configuration changes and longer-lived data.
6. Use lifecycle-aware components (`LiveData`, `Flow` with lifecycleScope, LifecycleObserver).
7. Clean up in `onDestroy()` for resources not already released (keeping in mind it may not always be called on process kill).
8. Avoid long/blocking operations in lifecycle callbacks; use background threads / coroutines.
9. Handle configuration changes properly (rotation, multi-window, locale, etc.).
10. Test common lifecycle scenarios (navigation, rotation, process death, multi-window).

### Common Mistakes

```kotlin
// WRONG: Long operation in onCreate
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    Thread.sleep(5000) // Blocks UI!
}

// CORRECT: Use background thread / coroutine
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    lifecycleScope.launch {
        withContext(Dispatchers.IO) {
            loadData()
        }
    }
}

// WRONG: Not saving state that should survive rotation
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    counter = 0 // Lost on configuration change
}

// CORRECT: Save and restore state
private var counter: Int = 0

override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putInt("counter", counter)
}

override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    counter = savedInstanceState?.getInt("counter") ?: 0
}
```

---

## Связанные Темы (RU)
- Жизненный цикл `Fragment`
- `ViewModel`
- `SavedStateHandle`
- Конфигурационные изменения
- Компоненты, учитывающие жизненный цикл
- Завершение процесса и восстановление состояния

---

## Related Topics
- `Fragment` lifecycle
- `ViewModel`
- SavedStateHandle
- Configuration changes
- Lifecycle-aware components
- Process death

---

## Дополнительные Вопросы (RU)

- [[c-activity-lifecycle]]
- [[q-what-happens-to-the-old-activity-when-the-system-starts-a-new-one--android--hard]]
- [[q-what-is-activity-and-what-is-it-used-for--android--medium]]

## Follow-ups

- [[c-activity-lifecycle]]
- [[q-what-happens-to-the-old-activity-when-the-system-starts-a-new-one--android--hard]]
- [[q-what-is-activity-and-what-is-it-used-for--android--medium]]

---

## Ссылки (RU)

- [Android Documentation]("https://developer.android.com/docs")
- [Lifecycle]("https://developer.android.com/topic/libraries/architecture/lifecycle")

## References

- [Android Documentation]("https://developer.android.com/docs")
- [Lifecycle]("https://developer.android.com/topic/libraries/architecture/lifecycle")

---

## Связанные Вопросы (RU)

### Базовые (проще)
- [[q-viewmodel-pattern--android--easy]] - Жизненный цикл

### Связанные (средний уровень)
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Жизненный цикл, `Activity`
- [[q-activity-lifecycle-methods--android--medium]] - Жизненный цикл, `Activity`
- [[q-fragment-vs-activity-lifecycle--android--medium]] - Жизненный цикл, `Activity`
- [[q-how-does-fragment-lifecycle-differ-from-activity-v2--android--medium]] - Жизненный цикл, `Activity`
- [[q-how-does-activity-lifecycle-work--android--medium]] - Жизненный цикл, `Activity`

## Related Questions

### Prerequisites (Easier)
- [[q-viewmodel-pattern--android--easy]] - Lifecycle

### Related (Medium)
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Lifecycle, `Activity`
- [[q-activity-lifecycle-methods--android--medium]] - Lifecycle, `Activity`
- [[q-fragment-vs-activity-lifecycle--android--medium]] - Lifecycle, `Activity`
- [[q-how-does-fragment-lifecycle-differ-from-activity-v2--android--medium]] - Lifecycle, `Activity`
- [[q-how-does-activity-lifecycle-work--android--medium]] - Lifecycle, `Activity`
