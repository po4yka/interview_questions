---
id: 202510051234003
title: "Context in Android / Context в Android"
status: draft
created: 2025-10-05
updated: 2025-10-05
difficulty: medium
topics:
  - android
subtopics:
  - lifecycle
  - activity
  - app-startup
tags:
  - android
  - context
  - application-context
  - activity-context
  - difficulty/medium
language_tags:
  - en
  - ru
original_language: en
source: https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20is%20Context.md
author: null
related:
  - "[[moc-android]]"
  - "[[q-activity-lifecycle--android--easy]]"
  - "[[q-memory-leaks-android--android--medium]]"
moc:
  - "[[moc-android]]"
connections: []
---

# Context in Android / Context в Android

## English

### Definition

`Context` is the interface to global information about an application environment. This is an abstract class whose implementation is provided by the Android system. It allows access to application-specific resources and classes, as well as up-calls for application-level operations such as launching activities, broadcasting and receiving intents, etc.

### Context Hierarchy

In Android's class hierarchy, `Context` is the root class. Notably, `Activity` is a descendant of `Context`:

```
Context (abstract class)
    ├── ContextWrapper
    │   ├── Application
    │   ├── Service
    │   └── ContextThemeWrapper
    │       └── Activity
    └── ... other implementations
```

### Primary Context Implementations

The primary classes that implement `Context` (through inheritance) are:

1. **Application**
   - Provides access to application-wide resources and services
   - Used for global settings or shared data
   - Lives for the entire lifetime of the app

2. **Activity**
   - Typically used for UI-related tasks
   - Used for starting new activities (`startActivity()`)
   - Used for accessing resources and managing events
   - Tied to the activity lifecycle

3. **Service**
   - A context tied to the lifecycle of a service
   - Used for background operations

4. **ContextWrapper**
   - A base class for other context implementations that wrap an existing `Context`
   - Allows extending and customizing the behavior of an existing context

5. **ContextThemeWrapper**
   - Inherits from `ContextWrapper`
   - Provides a context with a specific theme
   - Often used in activities to apply UI themes with `setTheme()`

### What Context Can Do

Different types of Context have different capabilities:

| Action | Application | Activity | Service | ContentProvider | BroadcastReceiver |
|--------|------------|----------|---------|-----------------|-------------------|
| Show a Dialog | NO | YES | NO | NO | NO |
| Start an Activity | NO¹ | YES | NO¹ | NO¹ | NO¹ |
| Layout Inflation | NO² | YES | NO² | NO² | NO² |
| Start a Service | YES | YES | YES | YES | YES |
| Bind to a Service | YES | YES | YES | YES | NO |
| Send a Broadcast | YES | YES | YES | YES | YES |
| Register BroadcastReceiver | YES | YES | YES | YES | NO³ |
| Load Resource Values | YES | YES | YES | YES | YES |

**Notes:**
1. An application CAN start an Activity from here, but it requires that a new task be created. This may fit specific use cases, but can create non-standard back stack behaviors in your application and is generally not recommended or considered good practice
2. This is legal, but inflation will be done with the default theme for the system on which you are running, not what's defined in your application
3. Allowed if the receiver is null, which is used for obtaining the current value of a sticky broadcast, on Android 4.2 and above

### getApplication() vs getApplicationContext()

```kotlin
@Override
fun getApplicationContext(): Context {
    return if (mPackageInfo != null)
        mPackageInfo.getApplication()
    else
        mMainThread.getApplication()
}
```

Both functions return the application object since the application itself is a context. However, Android provides two functions because:

- **`getApplication()`** is only available in `Activity` and `Service`
- **`getApplicationContext()`** can be used in other components like `BroadcastReceiver` to get the application object

### Best Practices

#### When to use Application Context:
- For long-lived objects that need a context
- For singleton instances
- When you don't need UI-related functionality
- To avoid memory leaks

#### When to use Activity Context:
- When you need to show dialogs
- When inflating layouts with custom themes
- When starting activities
- For UI-related operations

#### Common Pitfalls:
- **Memory Leaks**: Using Activity context in long-lived objects can cause memory leaks
- **Theme Issues**: Using Application context for layout inflation won't apply your app's theme
- **Dialog Crashes**: Trying to show a dialog with Application context will crash

### Code Examples

#### Correct Usage - Application Context:
```kotlin
class MyRepository(private val context: Context) {
    // Use application context to avoid memory leaks
    private val appContext = context.applicationContext

    fun saveData(data: String) {
        val sharedPrefs = appContext.getSharedPreferences("prefs", Context.MODE_PRIVATE)
        sharedPrefs.edit().putString("data", data).apply()
    }
}
```

#### Correct Usage - Activity Context:
```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Use activity context for dialogs
        AlertDialog.Builder(this)
            .setTitle("Welcome")
            .setMessage("Hello, Android!")
            .show()
    }
}
```

#### Incorrect Usage - Memory Leak:
```kotlin
// DON'T DO THIS - causes memory leak
class MyRepository(private val activityContext: Activity) {
    // This keeps a reference to the activity even after it's destroyed
}
```

---

## Русский

### Определение

`Context` - это интерфейс к глобальной информации о среде приложения. Это абстрактный класс, реализация которого предоставляется системой Android. Он позволяет получить доступ к ресурсам и классам, специфичным для приложения, а также к операциям уровня приложения, таким как запуск активностей, отправка и получение интентов и т.д.

### Иерархия Context

В иерархии классов Android `Context` является корневым классом. Примечательно, что `Activity` является потомком `Context`:

```
Context (абстрактный класс)
    ├── ContextWrapper
    │   ├── Application
    │   ├── Service
    │   └── ContextThemeWrapper
    │       └── Activity
    └── ... другие реализации
```

### Основные реализации Context

Основные классы, которые реализуют `Context` (через наследование):

1. **Application**
   - Предоставляет доступ к ресурсам и сервисам на уровне приложения
   - Используется для глобальных настроек или общих данных
   - Живет в течение всего времени работы приложения

2. **Activity**
   - Обычно используется для задач, связанных с UI
   - Используется для запуска новых активностей (`startActivity()`)
   - Используется для доступа к ресурсам и управления событиями
   - Связан с жизненным циклом активности

3. **Service**
   - Контекст, связанный с жизненным циклом сервиса
   - Используется для фоновых операций

4. **ContextWrapper**
   - Базовый класс для других реализаций контекста, которые оборачивают существующий `Context`
   - Позволяет расширять и настраивать поведение существующего контекста

5. **ContextThemeWrapper**
   - Наследуется от `ContextWrapper`
   - Предоставляет контекст с определенной темой
   - Часто используется в активностях для применения UI-тем с помощью `setTheme()`

### Возможности Context

Разные типы Context имеют разные возможности:

| Действие | Application | Activity | Service | ContentProvider | BroadcastReceiver |
|---------|------------|----------|---------|-----------------|-------------------|
| Показать диалог | НЕТ | ДА | НЕТ | НЕТ | НЕТ |
| Запустить Activity | НЕТ¹ | ДА | НЕТ¹ | НЕТ¹ | НЕТ¹ |
| Инфлейт макета | НЕТ² | ДА | НЕТ² | НЕТ² | НЕТ² |
| Запустить Service | ДА | ДА | ДА | ДА | ДА |
| Привязаться к Service | ДА | ДА | ДА | ДА | НЕТ |
| Отправить Broadcast | ДА | ДА | ДА | ДА | ДА |
| Зарегистрировать BroadcastReceiver | ДА | ДА | ДА | ДА | НЕТ³ |
| Загрузить значения ресурсов | ДА | ДА | ДА | ДА | ДА |

**Примечания:**
1. Приложение МОЖЕТ запустить Activity отсюда, но это требует создания новой задачи. Это может соответствовать конкретным случаям использования, но может создать нестандартное поведение стека возврата в вашем приложении и обычно не рекомендуется или не считается хорошей практикой
2. Это допустимо, но инфлейт будет выполнен с темой по умолчанию для системы, на которой вы работаете, а не с темой, определенной в вашем приложении
3. Разрешено, если приемник равен null, что используется для получения текущего значения sticky broadcast, на Android 4.2 и выше

### getApplication() против getApplicationContext()

```kotlin
@Override
fun getApplicationContext(): Context {
    return if (mPackageInfo != null)
        mPackageInfo.getApplication()
    else
        mMainThread.getApplication()
}
```

Обе функции возвращают объект приложения, поскольку само приложение является контекстом. Однако Android предоставляет две функции, потому что:

- **`getApplication()`** доступен только в `Activity` и `Service`
- **`getApplicationContext()`** можно использовать в других компонентах, таких как `BroadcastReceiver`, для получения объекта приложения

### Лучшие практики

#### Когда использовать Application Context:
- Для долгоживущих объектов, которым нужен контекст
- Для экземпляров синглтонов
- Когда вам не нужна функциональность, связанная с UI
- Чтобы избежать утечек памяти

#### Когда использовать Activity Context:
- Когда нужно показывать диалоги
- При инфлейте макетов с пользовательскими темами
- При запуске активностей
- Для операций, связанных с UI

#### Распространенные ошибки:
- **Утечки памяти**: Использование контекста Activity в долгоживущих объектах может вызвать утечки памяти
- **Проблемы с темами**: Использование контекста Application для инфлейта макета не применит тему вашего приложения
- **Краши диалогов**: Попытка показать диалог с контекстом Application приведет к крашу

### Примеры кода

#### Правильное использование - Application Context:
```kotlin
class MyRepository(private val context: Context) {
    // Используем application context, чтобы избежать утечек памяти
    private val appContext = context.applicationContext

    fun saveData(data: String) {
        val sharedPrefs = appContext.getSharedPreferences("prefs", Context.MODE_PRIVATE)
        sharedPrefs.edit().putString("data", data).apply()
    }
}
```

#### Правильное использование - Activity Context:
```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Используем activity context для диалогов
        AlertDialog.Builder(this)
            .setTitle("Добро пожаловать")
            .setMessage("Привет, Android!")
            .show()
    }
}
```

#### Неправильное использование - Утечка памяти:
```kotlin
// НЕ ДЕЛАЙТЕ ТАК - вызывает утечку памяти
class MyRepository(private val activityContext: Activity) {
    // Это сохраняет ссылку на активность даже после её уничтожения
}
```

---

## References

- [Android Developer Docs: Context](https://developer.android.com/reference/android/content/Context)
- [Fully understand Context in Android](https://ericyang505.github.io/android/Context.html)
- [StackOverflow: Difference between Activity Context and Application Context](https://stackoverflow.com/questions/4128589/difference-between-activity-context-and-application-context)
- [StackOverflow: What is Context on Android?](https://stackoverflow.com/questions/3572463/what-is-context-on-android)
- [Medium: Context and memory leaks in Android](https://medium.com/swlh/context-and-memory-leaks-in-android-82a39ed33002)
- [Medium: Which Context should I use in Android?](https://medium.com/@ali.muzaffar/which-context-should-i-use-in-android-e3133d00772c)
- [Android Context Needs Isolation](https://www.techyourchance.com/android-context-needs-isolation/)
- [Using Context Theme Wrapper on Android](https://ataulm.com/2019/11/20/using-context-theme-wrapper.html)
- [Medium: Activity Context vs Application Context: A Deep Dive](https://medium.com/@mahmoud.alkateb22/activity-context-vs-application-context-a-deep-dive-into-android-development-94fc41233de7)
