---
id: android-096
title: Почему данные пользователя могут исчезать при повороте экрана? / Why might
  user data disappear during screen rotation?
aliases:
- Configuration change data loss
- Screen rotation data loss
- Данные исчезают при повороте
- Потеря данных при повороте
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
- q-why-fragment-callbacks-differ-from-activity-callbacks--android--hard
created: 2025-10-13
updated: 2025-10-30
tags:
- android/architecture-mvvm
- android/lifecycle
- android/ui-state
- configuration-changes
- difficulty/hard
- lifecycle
- state-management
- viewmodel
sources:
- https://developer.android.com/guide/topics/resources/runtime-changes
- https://developer.android.com/topic/libraries/architecture/saving-states
---

# Вопрос (RU)

> Почему данные пользователя могут исчезать при повороте экрана и как это предотвратить?

# Question (EN)

> Why might user data disappear during screen rotation and how can you prevent it?

---

## Ответ (RU)

Android по умолчанию уничтожает и пересоздает `Activity` при изменении конфигурации (поворот экрана). Непонятые переменные сбрасываются, и данные теряются.

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

### ✅ Решение 1: onSaveInstanceState (для UI-состояния)

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
- `Bundle` имеет лимит ~500KB (TransactionTooLargeException)
- Только сериализуемые типы (`Parcelable`, `Serializable`, примитивы)

### ✅ Решение 2: `ViewModel` (для Сложных данных)

```kotlin
class FormViewModel : ViewModel() {
    val userInput = MutableLiveData<String>()
    val productList = MutableLiveData<List<Product>>()

    init {
        loadProducts()  // Загрузится только один раз
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
- Идеально для тяжёлых операций (сетевые запросы, БД)

**Ограничение**: НЕ переживает process death

### ✅ Решение 3: SavedStateHandle (best practice)

```kotlin
class FormViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // Переживает и config changes, и process death
    var userInput: String
        get() = savedStateHandle["input"] ?: ""
        set(value) { savedStateHandle["input"] = value }

    // LiveData с автосохранением
    val isChecked: MutableLiveData<Boolean> =
        savedStateHandle.getLiveData("checked", false)
}

class FormActivity : AppCompatActivity() {
    private val viewModel: FormViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        findViewById<EditText>(R.id.editText).apply {
            setText(viewModel.userInput)  // Автоматически восстановлено
            addTextChangedListener {
                viewModel.userInput = it.toString()
            }
        }
    }
}
```

### ❌ Решение 4: android:configChanges (не рекомендуется)

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
- Нужно вручную обрабатывать все изменения конфигурации
- Не загружаются ресурсы для новой ориентации автоматически
- Усложняет код
- Считается bad practice

### Автоматическое Сохранение `View`

```xml
<!-- View с android:id автоматически сохраняют базовое состояние -->
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
    // TransactionTooLargeException!
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
| `EditText` (с ID) | Автоматически | `View` сохраняет сам |
| Кастомная переменная | onSaveInstanceState | Маленькие данные |
| Большой объект | `ViewModel` | Только config changes |
| Критические данные | SavedStateHandle | Config changes + process death |
| Сетевые данные | `ViewModel` + `Repository` | Не перезагружать |
| Ввод формы | SavedStateHandle | Должен пережить process death |

### Полный Пример (best practice)

```kotlin
class RegistrationViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // Критические данные - переживают process death
    var email: String
        get() = savedStateHandle["email"] ?: ""
        set(value) { savedStateHandle["email"] = value }

    // Некритические данные - только ViewModel
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
3. Данные не сохранены в onSaveInstanceState
4. `ViewModel` не используется для сложных данных

**Решения**:
- **onSaveInstanceState** - маленькое UI-состояние (< 500KB)
- **`ViewModel`** - сложные данные, config changes
- **SavedStateHandle** - критические данные (best practice)
- **`View` ID** - автоматическое сохранение базового состояния `View`

## Answer (EN)

Android destroys and recreates Activities by default during configuration changes (screen rotation). Unsaved variables reset, causing data loss.

### Why Android Recreates `Activity`

System recreates to:
1. Apply new resource configurations (layout-land, values-sw600dp)
2. Load orientation-specific resources
3. Recalculate layout dimensions
4. Apply density/language/theme changes

### `Lifecycle` During Rotation

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

### ✅ Solution 1: onSaveInstanceState (for UI state)

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
- `Bundle` has ~500KB limit (TransactionTooLargeException)
- Only serializable types (`Parcelable`, `Serializable`, primitives)

### ✅ Solution 2: `ViewModel` (for Complex data)

```kotlin
class FormViewModel : ViewModel() {
    val userInput = MutableLiveData<String>()
    val productList = MutableLiveData<List<Product>>()

    init {
        loadProducts()  // Loads only once
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
- Perfect for heavy operations (network, database)

**Limitation**: Does NOT survive process death

### ✅ Solution 3: SavedStateHandle (best practice)

```kotlin
class FormViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // Survives both config changes AND process death
    var userInput: String
        get() = savedStateHandle["input"] ?: ""
        set(value) { savedStateHandle["input"] = value }

    // LiveData with auto-save
    val isChecked: MutableLiveData<Boolean> =
        savedStateHandle.getLiveData("checked", false)
}

class FormActivity : AppCompatActivity() {
    private val viewModel: FormViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        findViewById<EditText>(R.id.editText).apply {
            setText(viewModel.userInput)  // Auto-restored
            addTextChangedListener {
                viewModel.userInput = it.toString()
            }
        }
    }
}
```

### ❌ Solution 4: android:configChanges (not recommended)

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
- Must manually handle all configuration changes
- Orientation-specific resources won't load automatically
- Complicates code
- Considered bad practice

### Automatic `View` State Saving

```xml
<!-- Views with android:id automatically save basic state -->
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
    // TransactionTooLargeException!
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
| `EditText` (with ID) | Automatic | `View` saves itself |
| Custom variable | onSaveInstanceState | Small data |
| Large object | `ViewModel` | Config changes only |
| Critical data | SavedStateHandle | Config changes + process death |
| Network data | `ViewModel` + `Repository` | Don't reload |
| Form input | SavedStateHandle | Must survive process death |

### Complete Example (best practice)

```kotlin
class RegistrationViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    // Critical data - survives process death
    var email: String
        get() = savedStateHandle["email"] ?: ""
        set(value) { savedStateHandle["email"] = value }

    // Non-critical data - ViewModel only
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
1. `Activity` destroyed and recreated
2. Variables reset to initial values
3. Data not saved in onSaveInstanceState
4. `ViewModel` not used for complex data

**Solutions**:
- **onSaveInstanceState** - small UI state (< 500KB)
- **`ViewModel`** - complex data, config changes
- **SavedStateHandle** - critical data (best practice)
- **`View` ID** - automatic basic `View` state saving

---

## Follow-ups

1. What's the maximum size for data in onSaveInstanceState `Bundle` and what happens if exceeded?
2. How does SavedStateHandle internally combine `ViewModel` persistence with `Bundle` serialization?
3. What happens to `ViewModel` when process is killed (low memory) vs configuration change?
4. How to handle state restoration for custom Views that don't extend standard Android Views?
5. What advanced patterns exist for managing complex multi-fragment state during configuration changes?

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
