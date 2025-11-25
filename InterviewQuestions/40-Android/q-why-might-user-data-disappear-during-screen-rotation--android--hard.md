---
id: android-096
title: Почему данные пользователя могут исчезать при повороте экрана? / Why might user data disappear during screen rotation?
aliases: [Configuration change data loss, Screen rotation data loss, Данные исчезают при повороте, Потеря данных при повороте]
topic: android
subtopics:
  - architecture-mvvm
  - lifecycle
  - ui-state
question_kind: android
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-compose-state
  - c-lifecycle
  - c-mvvm
  - q-compose-gesture-detection--android--medium
  - q-which-event-is-called-when-user-touches-screen--android--medium
  - q-which-event-is-triggered-when-user-presses-screen--android--medium
  - q-why-fragment-callbacks-differ-from-activity-callbacks--android--hard
  - q-why-user-data-may-disappear-on-screen-rotation--android--hard
created: 2025-10-13
updated: 2025-11-10
tags: [android/architecture-mvvm, android/lifecycle, android/ui-state, configuration-changes, difficulty/hard, lifecycle, state-management, viewmodel]
sources:
  - "https://developer.android.com/guide/topics/resources/runtime-changes"
  - "https://developer.android.com/topic/libraries/architecture/saving-states"

date created: Saturday, November 1st 2025, 12:47:11 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---

# Вопрос (RU)

> Почему данные пользователя могут исчезать при повороте экрана и как это предотвратить?

# Question (EN)

> Why might user data disappear during screen rotation and how can you prevent it?

---

## Ответ (RU)

### Краткая Версия
Данные исчезают, потому что при изменении конфигурации Android уничтожает и пересоздаёт `Activity`. Все поля и локальные переменные сбрасываются. Чтобы сохранить данные, нужно использовать:
- `onSaveInstanceState` для небольшого UI-состояния
- `ViewModel` для состояния, переживающего config changes
- `SavedStateHandle` для небольшого критичного состояния и восстановления после process death (через `SavedStateRegistry`)
- Автоматическое сохранение состояния поддерживаемых `View` по `android:id`

### Подробная Версия
Android по умолчанию уничтожает и пересоздает `Activity` при изменении конфигурации (поворот экрана). Поля активити и локальные переменные сбрасываются, и несохранённые данные теряются.

### Почему Android Пересоздаёт `Activity`

Система пересоздаёт `Activity` для:
1. Применения новых ресурсов (layout-land, values-sw600dp)
2. Загрузки ресурсов для новой ориентации
3. Пересчёта размеров layout
4. Применения изменений плотности/языка/темы

### Жизненный Цикл При Повороте

```
Поворот устройства
      ↓
onPause()
      ↓
onSaveInstanceState()  ← СОХРАНИТЬ СОСТОЯНИЕ
      ↓
onStop() → onDestroy()
      ↓
[Новый экземпляр Activity]
      ↓
onCreate(savedInstanceState)  ← ВОССТАНОВИТЬ СОСТОЯНИЕ
      ↓
onStart() → onRestoreInstanceState() → onResume()
```

### ❌ Проблема: Потеря Данных

```kotlin
// Данные будут потеряны при повороте
class FormActivity : AppCompatActivity() {
    private var userInput: String = ""
    private var selectedPosition: Int = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_form)

        findViewById<EditText>(R.id.editText).addTextChangedListener {
            userInput = it.toString()  // Потеряется при повороте!
        }
    }
    // После поворота: userInput = "" (сброшено)
}
```

### ✅ Решение 1: `onSaveInstanceState` (для UI-состояния)

```kotlin
class FormActivity : AppCompatActivity() {
    private lateinit var editText: EditText

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_form)

        editText = findViewById(R.id.editText)

        // Восстанавливаем состояние
        savedInstanceState?.let {
            editText.setText(it.getString(KEY_INPUT, ""))
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putString(KEY_INPUT, editText.text.toString())
    }

    companion object {
        private const val KEY_INPUT = "user_input"
    }
}
```

**Ограничения**:
- `Bundle` имеет лимит порядка сотен килобайт (слишком большие данные могут привести к `TransactionTooLargeException`)
- Только сериализуемые типы (`Parcelable`, `Serializable`, примитивы)

### ✅ Решение 2: `ViewModel` (для Сложных данных)

```kotlin
class FormViewModel : ViewModel() {
    val userInput = MutableLiveData<String>()
    val productList = MutableLiveData<List<Product>>()

    init {
        loadProducts()  // Загрузится только один раз для данного владельца
    }

    private fun loadProducts() {
        viewModelScope.launch {
            productList.value = repository.getProducts()
        }
    }
}

class FormActivity : AppCompatActivity() {
    private val viewModel: FormViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_form)

        // ViewModel переживает поворот
        viewModel.userInput.observe(this) { input ->
            updateUI(input)
        }

        // Данные не перезагружаются при повороте
        viewModel.productList.observe(this) { products ->
            updateList(products)
        }
    }
}
```

**Преимущества**:
- Переживает configuration changes
- Не имеет размерных ограничений `Bundle`
- Подходит для тяжёлых операций (сетевые запросы, БД)

**Ограничение**: не переживает process death (данные нужно уметь восстановить из надёжного источника: БД, кэш, сеть).

### ✅ Решение 3: `SavedStateHandle` (best Practice Для Небольшого Критичного состояния)

```kotlin
class FormViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // Может пережить и config changes, и process death для небольших сериализуемых данных,
    // если ViewModel создан через SavedStateViewModelFactory / Hilt / Navigation
    // и данные сохраняются через SavedStateRegistry
    var userInput: String
        get() = savedStateHandle["input"] ?: ""
        set(value) { savedStateHandle["input"] = value }

    // LiveData с автосохранением
    val isChecked: MutableLiveData<Boolean> =
        savedStateHandle.getLiveData("checked", false)
}

class FormActivity : AppCompatActivity() {
    // Требуется фабрика, поддерживающая SavedStateHandle (пример: Hilt, Navigation)
    private val viewModel: FormViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_form)

        findViewById<EditText>(R.id.editText).apply {
            setText(viewModel.userInput)  // Восстановлено из SavedStateHandle (если доступно)
            addTextChangedListener {
                viewModel.userInput = it.toString()
            }
        }
    }
}
```

Важно: `SavedStateHandle` использует тот же `Bundle`-механизм (`SavedStateRegistry`) и Binder-ограничения, что и `onSaveInstanceState`, поэтому подходит для компактного состояния. Для действительно критичных/крупных данных нужна стойкая персистентность (БД, файлы и т.п.).

### ❌ Решение 4: `android:configChanges` (не рекомендуется)

```xml
<!-- AndroidManifest.xml -->
<activity
    android:name=".MainActivity"
    android:configChanges="orientation|screenSize">
</activity>
```

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        // Нужно вручную обрабатывать изменения
        if (newConfig.orientation == ORIENTATION_LANDSCAPE) {
            // Обновить UI для landscape
        }
    }
}
```

**Почему плохо**:
- Нужно вручную обрабатывать соответствующие изменения конфигурации
- Ресурсы для новой конфигурации не будут применены автоматически так же прозрачно, как при пересоздании `Activity`
- Усложняет код
- Считается плохой практикой, за редкими, обоснованными исключениями

### Автоматическое Сохранение Состояния `View`

```xml
<!-- Поддерживаемые View с android:id автоматически сохраняют базовое состояние -->
<EditText
    android:id="@+id/editText"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />
    <!-- Текст сохраняется автоматически -->

<CheckBox
    android:id="@+id/checkBox"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content" />
    <!-- Состояние checked сохраняется автоматически -->
```

**Требует**:
- `View` должна иметь `android:id`
- `View` должна быть присоединена к window во время `onSaveInstanceState()`
- Виджет или кастомная `View` должны корректно реализовывать механизм сохранения/восстановления состояния (стандартные виджеты уже реализуют)

### Что Требует Ручного Сохранения

```kotlin
// ❌ НЕ сохраняется автоматически
private var userScore: Int = 0
private var currentLevel: Int = 1
private val selectedItems = mutableListOf<Int>()
private lateinit var gameState: GameState

override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)

    // Нужно сохранять вручную
    outState.putInt("score", userScore)
    outState.putInt("level", currentLevel)
    outState.putParcelable("state", gameState)
    outState.putIntegerArrayList("items", ArrayList(selectedItems))
}
```

### Распространённые Ошибки

```kotlin
// ❌ Ошибка 1: игнорирование savedInstanceState
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    var counter = 0  // Всегда 0, даже после восстановления!
}

// ❌ Ошибка 2: не вызывается super
override fun onSaveInstanceState(outState: Bundle) {
    // super.onSaveInstanceState(outState)  // Забыли!
    outState.putString("key", "value")
}

// ❌ Ошибка 3: большие данные в Bundle
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putParcelableArrayList("list", ArrayList(millionItems))
    // Риск TransactionTooLargeException!
}

// ✅ Правильный подход
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    savedInstanceState?.let {
        // Восстановление состояния
    } ?: run {
        // Первоначальная инициализация
    }
}
```

### Матрица Решений

| Тип данных | Решение | Причина |
|------------|---------|---------|
| EditText (с ID) | Автоматически | Поддерживаемый `View` сохраняет сам |
| Кастомная переменная | `onSaveInstanceState` | Маленькие данные |
| Большой объект | `ViewModel` | Только config changes |
| Критические данные | `SavedStateHandle` +/или персистентное хранилище | Config changes + process death для малого состояния; крупное/важное — в БД/файлах |
| Сетевые данные | `ViewModel` + Repository | Не перезагружать |
| Ввод формы | `SavedStateHandle` (малый объём) + по необходимости персистентное хранилище | Должен пережить process death |

### Полный Пример (best practice)

```kotlin
class RegistrationViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // Критические компактные данные - могут пережить process death при корректном использовании SavedStateHandle
    var email: String
        get() = savedStateHandle["email"] ?: ""
        set(value) { savedStateHandle["email"] = value }

    // Некритические данные - только ViewModel (переживают только config changes)
    val countries = MutableLiveData<List<Country>>()

    init {
        if (countries.value == null) {
            loadCountries()
        }
    }
}

class RegistrationActivity : AppCompatActivity() {
    private val viewModel: RegistrationViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_registration)

        findViewById<EditText>(R.id.email).apply {
            setText(viewModel.email)
            addTextChangedListener {
                viewModel.email = it.toString()
            }
        }

        viewModel.countries.observe(this) { countries ->
            updateSpinner(countries)
        }
    }
}
```

### Резюме

Данные исчезают потому что:
1. `Activity` уничтожается и пересоздаётся
2. Переменные сбрасываются в начальные значения
3. Данные не сохранены в `onSaveInstanceState`
4. Не используется `ViewModel` / `SavedStateHandle` / персистентное хранилище для состояния

Решения:
- `onSaveInstanceState` — маленькое UI-состояние (учитывая лимит Binder)
- `ViewModel` — сложные данные, переживает только config changes
- `SavedStateHandle` — небольшие критичные данные (best practice, использует `Bundle`-механику и ограничения)
- `View` ID — автоматическое сохранение базового состояния поддерживаемых `View`
- Персистентное хранилище (БД/файлы) — для по-настоящему критичных или больших данных

## Answer (EN)

### Short Version
Data disappears because Android destroys and recreates the `Activity` on configuration change. All fields and locals are reset. To preserve data, use:
- `onSaveInstanceState` for small UI state
- `ViewModel` for state surviving config changes
- `SavedStateHandle` for small critical state and process-death restoration (via `SavedStateRegistry`)
- Automatic state saving for supported `View`s via `android:id`

### Detailed Version
Android destroys and recreates Activities by default during configuration changes (screen rotation). `Activity` fields and local variables are reset, and any unsaved data is lost.

### Why Android Recreates `Activity`

System recreates to:
1. Apply new resource configurations (layout-land, values-sw600dp)
2. Load orientation-specific resources
3. Recalculate layout dimensions
4. Apply density/language/theme changes

### Lifecycle During Rotation

```
Device rotated
      ↓
onPause()
      ↓
onSaveInstanceState()  ← SAVE STATE
      ↓
onStop() → onDestroy()
      ↓
[New Activity Instance]
      ↓
onCreate(savedInstanceState)  ← RESTORE STATE
      ↓
onStart() → onRestoreInstanceState() → onResume()
```

### ❌ Problem: Data Loss

```kotlin
// Data will be lost on rotation
class FormActivity : AppCompatActivity() {
    private var userInput: String = ""
    private var selectedPosition: Int = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_form)

        findViewById<EditText>(R.id.editText).addTextChangedListener {
            userInput = it.toString()  // Lost on rotation!
        }
    }
    // After rotation: userInput = "" (reset)
}
```

### ✅ Solution 1: `onSaveInstanceState` (for UI state)

```kotlin
class FormActivity : AppCompatActivity() {
    private lateinit var editText: EditText

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_form)

        editText = findViewById(R.id.editText)

        // Restore state
        savedInstanceState?.let {
            editText.setText(it.getString(KEY_INPUT, ""))
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putString(KEY_INPUT, editText.text.toString())
    }

    companion object {
        private const val KEY_INPUT = "user_input"
    }
}
```

**Limitations**:
- `Bundle` is constrained by Binder transaction limits (too much data can cause `TransactionTooLargeException`)
- Only serializable types (`Parcelable`, `Serializable`, primitives)

### ✅ Solution 2: `ViewModel` (for Complex data)

```kotlin
class FormViewModel : ViewModel() {
    val userInput = MutableLiveData<String>()
    val productList = MutableLiveData<List<Product>>()

    init {
        loadProducts()  // Loads only once for the given owner
    }

    private fun loadProducts() {
        viewModelScope.launch {
            productList.value = repository.getProducts()
        }
    }
}

class FormActivity : AppCompatActivity() {
    private val viewModel: FormViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_form)

        // ViewModel survives rotation
        viewModel.userInput.observe(this) { input ->
            updateUI(input)
        }

        // Data not reloaded on rotation
        viewModel.productList.observe(this) { products ->
            updateList(products)
        }
    }
}
```

**Benefits**:
- Survives configuration changes
- No `Bundle` size limits
- Good for heavy operations (network, database)

**Limitation**: does not survive process death (state must be restorable from a reliable source such as DB, cache, or network).

### ✅ Solution 3: `SavedStateHandle` (best Practice for Small Critical state)

```kotlin
class FormViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // Can survive both config changes and process death for small serializable values
    // when ViewModel is created via SavedStateViewModelFactory / Hilt / Navigation
    // and values are wired through SavedStateRegistry
    var userInput: String
        get() = savedStateHandle["input"] ?: ""
        set(value) { savedStateHandle["input"] = value }

    // LiveData with auto-save
    val isChecked: MutableLiveData<Boolean> =
        savedStateHandle.getLiveData("checked", false)
}

class FormActivity : AppCompatActivity() {
    // Requires a factory that provides SavedStateHandle (e.g., Hilt, Navigation)
    private val viewModel: FormViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_form)

        findViewById<EditText>(R.id.editText).apply {
            setText(viewModel.userInput)  // Restored from SavedStateHandle (if available)
            addTextChangedListener {
                viewModel.userInput = it.toString()
            }
        }
    }
}
```

Note: `SavedStateHandle` relies on the same `Bundle`-based `SavedStateRegistry` mechanism and Binder limits as `onSaveInstanceState`, so it is intended for compact state. Truly critical or large data should be persisted (DB, files, etc.).

### ❌ Solution 4: `android:configChanges` (not recommended)

```xml
<!-- AndroidManifest.xml -->
<activity
    android:name=".MainActivity"
    android:configChanges="orientation|screenSize">
</activity>
```

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onConfigurationChanged(newConfig: Configuration) {
        super.onConfigurationChanged(newConfig)
        // Must manually handle changes
        if (newConfig.orientation == ORIENTATION_LANDSCAPE) {
            // Update UI for landscape
        }
    }
}
```

**Why bad**:
- You must manually handle all relevant configuration changes
- New configuration resources are not applied as seamlessly as with `Activity` recreation
- Complicates code
- Considered bad practice except for narrow, justified cases

### Automatic `View` State Saving

```xml
<!-- Supported Views with android:id automatically save basic state -->
<EditText
    android:id="@+id/editText"
    android:layout_width="match_parent"
    android:layout_height="wrap_content" />
    <!-- Text saved automatically -->

<CheckBox
    android:id="@+id/checkBox"
    android:layout_width="wrap_content"
    android:layout_height="wrap_content" />
    <!-- Checked state saved automatically -->
```

**Requirements**:
- `View` must have `android:id`
- `View` must be attached to window during `onSaveInstanceState()`
- The widget or custom `View` must properly implement state saving/restoration (standard widgets already do)

### What Needs Manual Saving

```kotlin
// ❌ NOT saved automatically
private var userScore: Int = 0
private var currentLevel: Int = 1
private val selectedItems = mutableListOf<Int>()
private lateinit var gameState: GameState

override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)

    // Save manually
    outState.putInt("score", userScore)
    outState.putInt("level", currentLevel)
    outState.putParcelable("state", gameState)
    outState.putIntegerArrayList("items", ArrayList(selectedItems))
}
```

### Common Mistakes

```kotlin
// ❌ Mistake 1: Ignoring savedInstanceState
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    var counter = 0  // Always 0, even after restore!
}

// ❌ Mistake 2: Not calling super
override fun onSaveInstanceState(outState: Bundle) {
    // super.onSaveInstanceState(outState)  // Forgot!
    outState.putString("key", "value")
}

// ❌ Mistake 3: Large data in Bundle
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    outState.putParcelableArrayList("list", ArrayList(millionItems))
    // Risk of TransactionTooLargeException!
}

// ✅ Correct approach
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    savedInstanceState?.let {
        // Restore state
    } ?: run {
        // Initial setup
    }
}
```

### Decision Matrix

| Data Type | Solution | Reason |
|-----------|----------|--------|
| EditText (with ID) | Automatic | Supported `View` saves itself |
| Custom variable | `onSaveInstanceState` | Small data |
| Large object | `ViewModel` | Config changes only |
| Critical data | `SavedStateHandle` and/or persistent storage | Config changes + process death for small state; large/critical -> DB/files |
| Network data | `ViewModel` + Repository | Avoid unnecessary reloads |
| Form input | `SavedStateHandle` (small size) + persistent storage if needed | Should survive process death |

### Complete Example (best practice)

```kotlin
class RegistrationViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // Critical compact data - can survive process death when using SavedStateHandle correctly
    var email: String
        get() = savedStateHandle["email"] ?: ""
        set(value) { savedStateHandle["email"] = value }

    // Non-critical data - ViewModel only (survives config changes)
    val countries = MutableLiveData<List<Country>>()

    init {
        if (countries.value == null) {
            loadCountries()
        }
    }
}

class RegistrationActivity : AppCompatActivity() {
    private val viewModel: RegistrationViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_registration)

        findViewById<EditText>(R.id.email).apply {
            setText(viewModel.email)
            addTextChangedListener {
                viewModel.email = it.toString()
            }
        }

        viewModel.countries.observe(this) { countries ->
            updateSpinner(countries)
        }
    }
}
```

### Summary

Data disappears because:
1. `Activity` is destroyed and recreated
2. Variables reset to initial values
3. Data is not saved in `onSaveInstanceState`
4. `ViewModel` / `SavedStateHandle` / persistent storage are not used for state management

Solutions:
- `onSaveInstanceState` — small UI state (respect Binder limits)
- `ViewModel` — complex data, survives config changes only
- `SavedStateHandle` — small critical data (best practice, uses `Bundle`-based mechanism and limitations)
- `View` ID — automatic basic state saving for supported `View`s
- Persistent storage (DB/files) — for truly critical or large data

---

## Follow-ups

1. What's the maximum safe size for data stored in the `onSaveInstanceState` `Bundle`, and how do Binder transaction limits affect this?
2. How does `SavedStateHandle` interact with `SavedStateRegistry` and `Bundle` under the hood?
3. What happens to a `ViewModel` during low-memory process death vs. a configuration change, and how should you design for both?
4. How would you persist complex form state across multiple `Fragment`s during rotation and process death?
5. In which rare scenarios is using `android:configChanges` justified, and what trade-offs does it introduce?

## References

- Official Android Documentation: [Handle configuration changes](https://developer.android.com/guide/topics/resources/runtime-changes)
- Official Android Documentation: [Saving UI States](https://developer.android.com/topic/libraries/architecture/saving-states)
- Official Android Documentation: [`ViewModel` Overview](https://developer.android.com/topic/libraries/architecture/viewmodel)

## Related Questions

### Prerequisites / Concepts

- [[c-compose-state]]
- [[c-lifecycle]]
- [[c-mvvm]]

### Prerequisites (Medium)

- [[q-how-to-display-svg-string-as-a-vector-file--android--medium]]
- [[q-compose-gesture-detection--android--medium]]

### Related (Hard)

- [[q-why-fragment-callbacks-differ-from-activity-callbacks--android--hard]]
