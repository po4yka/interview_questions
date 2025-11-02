---
id: android-141
title: "What Is Data Binding / Что такое Data Binding"
aliases: ["Android Data Binding", "Data Binding", "Что такое Data Binding"]
topic: android
subtopics: [architecture-mvvm, ui-views]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-what-is-known-about-recyclerview--android--easy, q-which-event-is-called-when-user-touches-screen--android--medium]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android/architecture-mvvm, android/ui-views, data-binding, difficulty/easy, ui]
date created: Saturday, November 1st 2025, 12:47:08 pm
date modified: Saturday, November 1st 2025, 5:43:31 pm
---

# Вопрос (RU)

> Что такое Data Binding в Android и как его использовать?

# Question (EN)

> What is Data Binding in Android and how to use it?

---

## Ответ (RU)

**Data Binding** — библиотека Android для прямой привязки UI-компонентов к источникам данных, устраняющая необходимость в `findViewById()` и синхронизации UI вручную.

### Ключевые Возможности

1. **Устраняет `findViewById()`** — прямой доступ к view
2. **Двусторонняя привязка** — автоматическое обновление при изменении данных
3. **Язык выражений** — логика прямо в XML
4. **Null-безопасность** — встроенные проверки

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

```kotlin
class User : BaseObservable() {
    @get:Bindable
    var name: String = ""
        set(value) {
            field = value
            notifyPropertyChanged(BR.name)  // ✅ Уведомление об изменении
        }
}

// UI автоматически обновляется
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
    // Изменения в EditText автоматически обновят query
}
```

### С LiveData

```kotlin
class UserViewModel : ViewModel() {
    val userName = MutableLiveData<String>()

    fun loadUser() {
        userName.value = "John"
    }
}

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = DataBindingUtil.setContentView(this, R.layout.activity_main)

        binding.lifecycleOwner = this  // ✅ ВАЖНО: для LiveData
        binding.viewModel = viewModel
    }
}
```

### Data Binding Vs View Binding

| Функция | Data Binding | View Binding |
|---------|--------------|--------------|
| Устраняет `findViewById()` | ✅ | ✅ |
| Null/Type safety | ✅ | ✅ |
| Двусторонняя привязка | ✅ | ❌ |
| Выражения в XML | ✅ | ❌ |
| Скорость сборки | Медленнее | Быстрее |
| Рекомендация Google | ❌ | ✅ |

### Когда Использовать

**Data Binding:**
- Нужна двусторонняя привязка
- Используется MVVM с LiveData
- Требуется сократить boilerplate

**View Binding (предпочтительно):**
- Простой проект
- Важна скорость сборки
- Команда предпочитает явность

## Answer (EN)

**Data Binding** is an Android library for direct binding of UI components to data sources, eliminating the need for `findViewById()` and manual UI synchronization.

### Key Features

1. **Eliminates `findViewById()`** — direct view access
2. **Two-way binding** — automatic updates on data changes
3. **Expression language** — logic directly in XML
4. **Null safety** — built-in null checks

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

### Observable Data

```kotlin
class User : BaseObservable() {
    @get:Bindable
    var name: String = ""
        set(value) {
            field = value
            notifyPropertyChanged(BR.name)  // ✅ Notify change
        }
}

// UI updates automatically
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
    // Changes in EditText automatically update query
}
```

### With LiveData

```kotlin
class UserViewModel : ViewModel() {
    val userName = MutableLiveData<String>()

    fun loadUser() {
        userName.value = "John"
    }
}

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        binding = DataBindingUtil.setContentView(this, R.layout.activity_main)

        binding.lifecycleOwner = this  // ✅ IMPORTANT: for LiveData
        binding.viewModel = viewModel
    }
}
```

### Data Binding Vs View Binding

| Feature | Data Binding | View Binding |
|---------|--------------|--------------|
| Eliminates `findViewById()` | ✅ | ✅ |
| Null/Type safety | ✅ | ✅ |
| Two-way binding | ✅ | ❌ |
| Expressions in XML | ✅ | ❌ |
| Build speed | Slower | Faster |
| Google recommendation | ❌ | ✅ |

### When to Use

**Data Binding:**
- Need two-way binding
- Using MVVM with LiveData
- Need to reduce boilerplate

**View Binding (preferred):**
- Simple project
- Build speed matters
- Team prefers explicitness

---

## Follow-ups

- How does Data Binding handle null safety internally?
- What is the performance impact of Data Binding expressions?
- How to debug Data Binding errors at compile time?
- When should you use BindingAdapters?
- How does Data Binding integrate with Compose migration?

## References

- [Android Data Binding Documentation](https://developer.android.com/topic/libraries/data-binding)
- [View Binding Documentation](https://developer.android.com/topic/libraries/view-binding)

## Related Questions

### Prerequisites
- [[q-what-is-known-about-recyclerview--android--easy]] — Understanding Android views first

### Related
- [[q-which-event-is-called-when-user-touches-screen--android--medium]] — UI event handling

### Advanced
- How to implement custom BindingAdapters for complex UI logic?
- How to optimize Data Binding performance in large lists?
