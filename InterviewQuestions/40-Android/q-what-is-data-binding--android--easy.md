---
id: android-141
title: What Is Data Binding / Что такое Data Binding
aliases:
- Android Data Binding
- Data Binding
- Что такое Data Binding
topic: android
subtopics:
- architecture-mvvm
- ui-views
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-mvvm
- q-what-is-known-about-recyclerview--android--easy
- q-which-event-is-called-when-user-touches-screen--android--medium
created: 2025-10-15
updated: 2025-11-10
sources: []
tags:
- android/architecture-mvvm
- android/ui-views
- data-binding
- difficulty/easy
- ui

---

# Вопрос (RU)

> Что такое Data Binding в Android и как его использовать?

# Question (EN)

> What is Data Binding in Android and how to use it?

---

## Ответ (RU)

**Data Binding** — библиотека Android для прямой привязки UI-компонентов к источникам данных, устраняющая необходимость в `findViewById()` во многих случаях и упрощающая синхронизацию UI с данными за счёт генерации binding-классов на основе layout-файлов.

### Ключевые Возможности

1. **Устраняет `findViewById()`** — прямой доступ к view через сгенерированные binding-классы
2. **Двусторонняя привязка** — автоматическое обновление при изменении данных
3. **Язык выражений** — логика прямо в XML
4. **Null-безопасность** — типобезопасные ссылки на view

### Настройка

```gradle
android {
    buildFeatures {
        dataBinding = true  // ✅ Включение Data Binding
    }
}
```

### Базовое Использование

```xml
<!-- activity_main.xml -->
<layout xmlns:android="http://schemas.android.com/apk/res/android">
    <data>
        <variable
            name="user"
            type="com.example.User" />
    </data>

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="@{user.name}" />  <!-- ✅ Прямая привязка -->
</layout>
```

```kotlin
data class User(val name: String, val age: Int)

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val binding: ActivityMainBinding =
            DataBindingUtil.setContentView(this, R.layout.activity_main)

        binding.user = User("John Doe", 30)  // ✅ Установка данных
    }
}
```

### Наблюдаемые Данные

Альтернативный вариант — сделать модель наблюдаемой:

```kotlin
class ObservableUser : BaseObservable() {
    @get:Bindable
    var name: String = ""
        set(value) {
            field = value
            notifyPropertyChanged(BR.name)  // ✅ Уведомление об изменении
        }
}

// UI автоматически обновляется
val user = ObservableUser()
user.name = "Jane"  // TextView обновится автоматически
```

### Двусторонняя Привязка

```xml
<!-- ✅ @= вместо @ для двусторонней привязки -->
<EditText
    android:text="@={viewModel.query}" />
```

```kotlin
class SearchViewModel : ViewModel() {
    val query = MutableLiveData("")
    // Изменения в EditText автоматически обновят query и наоборот
}
```

### С `LiveData`

```kotlin
class UserViewModel : ViewModel() {
    val userName = MutableLiveData<String>()

    fun loadUser() {
        userName.value = "John"
    }
}

class MainActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = DataBindingUtil.setContentView(this, R.layout.activity_main)

        binding.lifecycleOwner = this  // ✅ ВАЖНО: для LiveData
        binding.viewModel = viewModel
    }
}
```

### Data Binding Vs `View` Binding

| Функция | Data Binding | `View` Binding |
|---------|--------------|--------------|
| Устраняет `findViewById()` | ✅ | ✅ |
| Null/Type safety | ✅ | ✅ |
| Двусторонняя привязка | ✅ | ❌ |
| Выражения в XML | ✅ | ❌ |
| Скорость сборки | Медленнее | Быстрее |
| Рекомендация Google | Рекомендуется при необходимости выражений/двусторонней привязки | Рекомендуется по умолчанию для безопасного доступа к view |

### Когда Использовать

**Data Binding:**
- Нужна двусторонняя привязка
- Используется MVVM с `LiveData` / `Observable`-типами
- Требуется сократить boilerplate и вынести простую логику отображения в XML

**`View` Binding (часто предпочтительнее по умолчанию):**
- Простой проект
- Важна скорость сборки
- Команда предпочитает явный код без логики в XML

## Answer (EN)

**Data Binding** is an Android library for directly binding UI components to data sources, eliminating the need for `findViewById()` in many cases and simplifying UI synchronization by generating binding classes based on layout files.

### Key Features

1. **Eliminates `findViewById()`** — direct view access via generated binding classes
2. **Two-way binding** — automatic updates when data changes
3. **Expression language** — logic directly in XML
4. **Null safety** — type-safe view references

### Setup

```gradle
android {
    buildFeatures {
        dataBinding = true  // ✅ Enable Data Binding
    }
}
```

### Basic Usage

```xml
<!-- activity_main.xml -->
<layout xmlns:android="http://schemas.android.com/apk/res/android">
    <data>
        <variable
            name="user"
            type="com.example.User" />
    </data>

    <TextView
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="@{user.name}" />  <!-- ✅ Direct binding -->
</layout>
```

```kotlin
data class User(val name: String, val age: Int)

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val binding: ActivityMainBinding =
            DataBindingUtil.setContentView(this, R.layout.activity_main)

        binding.user = User("John Doe", 30)  // ✅ Set data
    }
}
```

### `Observable` Data

An alternative is to make the model observable:

```kotlin
class ObservableUser : BaseObservable() {
    @get:Bindable
    var name: String = ""
        set(value) {
            field = value
            notifyPropertyChanged(BR.name)  // ✅ Notify change
        }
}

// UI updates automatically
val user = ObservableUser()
user.name = "Jane"  // TextView updates automatically
```

### Two-Way Binding

```xml
<!-- ✅ @= instead of @ for two-way binding -->
<EditText
    android:text="@={viewModel.query}" />
```

```kotlin
class SearchViewModel : ViewModel() {
    val query = MutableLiveData("")
    // Changes in EditText automatically update query and vice versa
}
```

### With `LiveData`

```kotlin
class UserViewModel : ViewModel() {
    val userName = MutableLiveData<String>()

    fun loadUser() {
        userName.value = "John"
    }
}

class MainActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = DataBindingUtil.setContentView(this, R.layout.activity_main)

        binding.lifecycleOwner = this  // ✅ IMPORTANT: for LiveData
        binding.viewModel = viewModel
    }
}
```

### Data Binding Vs `View` Binding

| Feature | Data Binding | `View` Binding |
|---------|--------------|--------------|
| Eliminates `findViewById()` | ✅ | ✅ |
| Null/Type safety | ✅ | ✅ |
| Two-way binding | ✅ | ❌ |
| Expressions in XML | ✅ | ❌ |
| Build speed | Slower | Faster |
| Google recommendation | Recommended when you need expressions/two-way binding | Recommended by default for safe view access |

### When to Use

**Data Binding:**
- Need two-way binding
- Using MVVM with `LiveData` / observable types
- Want to reduce boilerplate and move simple UI logic into XML

**`View` Binding (often preferred by default):**
- Simple project
- Build speed matters
- Team prefers explicit code without logic in XML

---

## Follow-ups

- How does Data Binding handle null safety internally?
- What is the performance impact of Data Binding expressions?
- How to debug Data Binding errors at compile time?
- When should you use BindingAdapters?
- How does Data Binding integrate with Compose migration?

## References

- [Android Data Binding Documentation](https://developer.android.com/topic/libraries/data-binding)
- [`View` Binding Documentation](https://developer.android.com/topic/libraries/view-binding)

## Related Questions

### Prerequisites / Concepts

- [[c-mvvm]]

### Prerequisites
- [[q-what-is-known-about-recyclerview--android--easy]] — Understanding Android views first

### Related
- [[q-which-event-is-called-when-user-touches-screen--android--medium]] — UI event handling

### Advanced
- How to implement custom BindingAdapters for complex UI logic?
- How to optimize Data Binding performance in large lists?
