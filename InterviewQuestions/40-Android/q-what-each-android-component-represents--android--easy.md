---
id: android-382
title: Android Components / Компоненты Android
aliases:
- Android Components
- Компоненты Android
topic: android
subtopics:
- activity
- service
- broadcast-receiver
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-android-components
- c-broadcast-receiver
- q-what-is-activity-and-what-is-it-used-for--android--medium
- q-what-is-broadcastreceiver--android--easy
created: 2025-10-15
updated: 2025-11-10
tags:
- android/activity
- android/service
- android/broadcast-receiver
- components
- difficulty/easy
- intent

---

# Вопрос (RU)
> Компоненты Android

# Question (EN)
> Android Components

---

## Ответ (RU)
Android-приложения строятся из нескольких ключевых элементов. Исторически Android определяет четыре основных компонента приложения:
- `Activity` (Активность)
- `Service` (Служба)
- `BroadcastReceiver` (Широковещательный приёмник)
- `ContentProvider` (Поставщик контента)

Дополнительно широко используются связанные сущности: `Fragment`, `View` и `Intent`, которые помогают организовывать UI и взаимодействие между компонентами.

Эти компоненты взаимодействуют друг с другом и с операционной системой для создания функционального приложения.

**Основные компоненты приложения:**

**1. `Activity`** - Экран пользовательского интерфейса

Предоставляет пользовательский интерфейс. Каждая `Activity` представляет собой один отдельный экран, с которым взаимодействует пользователь.

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

**2. `Service`** - Фоновые операции

Выполняет работу в фоне без собственного UI, например воспроизведение музыки или синхронизацию данных. Важно:
- `Service` не создаёт свой UI.
- По умолчанию код `Service` выполняется в главном потоке (для тяжёлых задач нужно явно использовать отдельные потоки).
- В современных версиях Android действуют ограничения фонового выполнения; для длительных задач часто используется foreground service или WorkManager.

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Воспроизведение музыки в фоне (для длительной работы используйте foreground service)
        return START_STICKY
    }
}
```

**3. `BroadcastReceiver`** - Системные и приложенческие широковещательные сообщения

Принимает и обрабатывает широковещательные `Intent`-сообщения от системы или других приложений.

```kotlin
class NetworkReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Обработка изменения состояния сети
    }
}
```

**4. `ContentProvider`** - Обмен структурированными данными

Позволяет приложениям предоставлять и разделять структурированные данные с другими приложениями через стандартный интерфейс.

```kotlin
class MyContentProvider : ContentProvider() {
    override fun query(
        uri: Uri,
        projection: Array<String>?,
        selection: String?,
        selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? {
        // Предоставление данных другим приложениям
        return null
    }

    // Остальные обязательные методы (insert, update, delete, getType) должны быть реализованы
}
```

**Дополнительные часто используемые элементы:**

**5. `Fragment`** - Часть UI/поведения

Представляет переиспользуемую часть UI или поведения внутри `Activity`.

```kotlin
class ProfileFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_profile, container, false)
    }
}
```

**6. `View`** - Строительный блок UI

Базовый строительный блок для отрисовки и обработки событий на экране.

```kotlin
class CustomButton(context: Context, attrs: AttributeSet? = null) : View(context, attrs) {
    // Реализация пользовательского View
}
```

**7. `Intent`** - Сообщения между компонентами

Используется для связи между компонентами: запуска `Activity`, запуска `Service` и отправки широковещательных сообщений.

```kotlin
val intent = Intent(this, ProfileActivity::class.java)
startActivity(intent)
```

**Итоговая таблица:**

| Компонент         | Назначение                          | Есть UI | Пример                  |
|-------------------|--------------------------------------|---------|-------------------------|
| `Activity`        | Экран                               | Да      | Экран входа             |
| `Service`         | Фоновая работа                      | Нет     | Воспроизведение музыки  |
| `BroadcastReceiver` | Системные/приложенческие события  | Нет     | Изменение сети          |
| `ContentProvider` | Обмен структурированными данными    | Нет     | Контакты                |
| `Fragment`        | Часть UI в `Activity`               | Да      | Содержимое вкладки      |
| `View`            | Элемент UI                          | Да      | Button, TextView        |
| `Intent`          | Обмен сообщениями между компонентами| Нет     | Запуск `Activity`       |

---

## Answer (EN)
Android applications are built from several key building blocks. Historically, Android defines four main application components:
- `Activity`
- `Service`
- `BroadcastReceiver`
- `ContentProvider`

In addition, developers commonly use related concepts such as `Fragment`, `View`, and `Intent`, which help structure UI and communication between components.

These components interact with each other and with the operating system to create a functional application.

**Main `Application` Components:**

**1. `Activity`** - User Interface Screen

Provides a user interface. Each `Activity` represents a single, focused screen with which the user can interact.

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

**2. `Service`** - Background Operations

Performs work in the background without a UI, such as playing music or syncing data. A `Service`:
- Does not create its own UI.
- Runs on the main thread by default (you must create background threads yourself if needed).
- In modern Android, is subject to background execution limits and often should be a foreground service or replaced with WorkManager for deferrable tasks.

```kotlin
class MusicService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Play music in background (consider foreground service for long-running work)
        return START_STICKY
    }
}
```

**3. `BroadcastReceiver`** - System and App Broadcasts

Receives and responds to broadcast messages (intents) from the system or other apps.

```kotlin
class NetworkReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Handle network change
    }
}
```

**4. `ContentProvider`** - Data Sharing

Enables apps to expose and share structured data with other apps using a standard interface.

```kotlin
class MyContentProvider : ContentProvider() {
    override fun query(
        uri: Uri,
        projection: Array<String>?,
        selection: String?,
        selectionArgs: Array<String>?,
        sortOrder: String?
    ): Cursor? {
        // Provide data to other apps
        return null
    }

    // Other required methods (insert, update, delete, getType) would be implemented here
}
```

**Additional Common Building Blocks:**

**5. `Fragment`** - Portion of UI/Behavior

Represents a reusable portion of UI or behavior inside an `Activity`.

```kotlin
class ProfileFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_profile, container, false)
    }
}
```

**6. `View`** - UI Building Block

Basic building block for drawing and event handling on the screen.

```kotlin
class CustomButton(context: Context, attrs: AttributeSet? = null) : View(context, attrs) {
    // Custom view implementation
}
```

**7. `Intent`** - Messaging Between Components

Used for communication between components: starting activities, starting services, and sending broadcasts.

```kotlin
val intent = Intent(this, ProfileActivity::class.java)
startActivity(intent)
```

**Summary:**

| Component          | Purpose                         | Has UI | Example            |
|--------------------|---------------------------------|--------|--------------------|
| `Activity`         | Screen                          | Yes    | Login screen       |
| `Service`          | Background work                 | No     | Music playback     |
| `BroadcastReceiver`| System/app broadcasts           | No     | Network change     |
| `ContentProvider`  | Data sharing                    | No     | Contacts           |
| `Fragment`         | Portion of UI in `Activity`     | Yes    | Tab content        |
| `View`             | UI element                      | Yes    | Button, TextView   |
| `Intent`           | Messaging between components    | No     | Start `Activity`   |

---

## Дополнительные вопросы (RU)

- [[c-android-components]]
- [[c-broadcast-receiver]]
- [[q-what-is-activity-and-what-is-it-used-for--android--medium]]

## Follow-ups

- [[c-android-components]]
- [[c-broadcast-receiver]]
- [[q-what-is-activity-and-what-is-it-used-for--android--medium]]

## Ссылки (RU)

- [Services](https://developer.android.com/develop/background-work/services)
- [Activities](https://developer.android.com/guide/components/activities)

## References

- [Services](https://developer.android.com/develop/background-work/services)
- [Activities](https://developer.android.com/guide/components/activities)

## Связанные вопросы (RU)

- [[q-rss-feed-aggregator--android--medium]]
- [[q-android-build-optimization--android--medium]]
- [[q-how-does-activity-lifecycle-work--android--medium]]

## Related Questions

- [[q-rss-feed-aggregator--android--medium]]
- [[q-android-build-optimization--android--medium]]
- [[q-how-does-activity-lifecycle-work--android--medium]]
