---
id: android-209
title: Unified Android Components / Объединение компонентов Android
aliases: [Unified Components, Объединение компонентов]
topic: android
subtopics:
  - activity
  - fragment
  - service
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
  - c-intent
  - c-lifecycle
  - q-android-components-besides-activity--android--easy
  - q-main-android-components--android--easy
  - q-what-unites-the-main-components-of-an-android-application--android--medium
created: 2025-10-15
updated: 2025-11-10
tags: [android/activity, android/fragment, android/intent, android/service, difficulty/easy]

date created: Saturday, November 1st 2025, 1:26:06 pm
date modified: Tuesday, November 25th 2025, 8:53:55 pm
---
# Вопрос (RU)
> Объединение компонентов Android

# Question (EN)
> Unified Android Components

---

## Ответ (RU)
Основные компоненты Android-приложения объединяют несколько общих принципов (с нюансами):

1. `Context` — доступ к ресурсам и системным сервисам.
2. Манифест — объявление и управление жизненным циклом (для четырёх основных компонентов).
3. `Intent` — единый механизм запуска и обмена сообщениями (там, где применимо).

**1. `Context` — доступ к ресурсам**

Все эти компоненты либо наследуют `Context`, либо получают его, чтобы обращаться к ресурсам и системным сервисам:

- `Activity` и `Service` наследуют `Context` (через обёртки).
- `BroadcastReceiver` получает `Context` в методе `onReceive`.
- `Fragment` не является `Context`, но всегда привязан к нему и использует `context`/`requireContext()`.

Примеры:

```kotlin
// Activity наследует ContextThemeWrapper (через ContextWrapper -> Context)
class MainActivity : AppCompatActivity() {
    fun accessResources() {
        val string = getString(R.string.app_name)
        val color = getColor(R.color.primary)
        val pm = packageManager
    }
}

// Service наследует ContextWrapper -> Context
class MusicService : Service() {
    fun accessSystemServices() {
        val notificationManager =
            getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val audioManager =
            getSystemService(Context.AUDIO_SERVICE) as AudioManager
    }
}

// BroadcastReceiver получает Context в onReceive
class NetworkReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val connectivityManager =
            context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
    }
}

// Fragment не является Context, но всегда ассоциирован с ним
class ProfileFragment : Fragment() {
    fun useContext() {
        val title = requireContext().getString(R.string.title)
    }
}
```

**2. AndroidManifest.xml — объявление основных компонентов**

Четыре основных компонента приложения — `Activity`, `Service`, `BroadcastReceiver` и `ContentProvider` — объявляются в `AndroidManifest.xml`, чтобы система могла их создавать и управлять ими. `Fragment` в манифесте не объявляется.

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <application>
        <!-- Activity -->
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- Service -->
        <service
            android:name=".MusicService"
            android:exported="false" />

        <!-- BroadcastReceiver -->
        <receiver
            android:name=".NetworkReceiver"
            android:exported="true">
            <intent-filter>
                <!-- Пример пользовательского широковещательного действия -->
                <action android:name="com.example.CUSTOM_ACTION" />
            </intent-filter>
        </receiver>

        <!-- ContentProvider -->
        <provider
            android:name=".NotesProvider"
            android:authorities="com.example.notes"
            android:exported="true" />
    </application>

</manifest>
```

**3. `Intent` — запуск и взаимодействие (там, где подходит)**

`Intent` обеспечивает единый механизм активации и коммуникации для части компонентов:

- запуск `Activity` при помощи явных или неявных `Intent` с соответствующими `IntentFilter`;
- запуск (или привязка) `Service`, включая современные foreground/background-паттерны с учётом ограничений платформы;
- отправка и приём широковещательных сообщений (`BroadcastReceiver`) как системных, так и пользовательских.

`ContentProvider` обычно вызывается через URI и `ContentResolver` (а не через `Intent`), а `Fragment` взаимодействует через `FragmentManager` и прямые вызовы методов.

```kotlin
// Запуск Activity
val activityIntent = Intent(this, ProfileActivity::class.java)
startActivity(activityIntent)

// Запуск Service (в современных приложениях предпочтительны foreground/work API по ситуации)
val serviceIntent = Intent(this, MusicService::class.java)
startService(serviceIntent)

// Отправка широковещательного сообщения (пользовательское действие)
val broadcastIntent = Intent("com.example.CUSTOM_ACTION")
sendBroadcast(broadcastIntent)

// Доступ к ContentProvider (URI-основанный доступ через ContentResolver)
contentResolver.query(
    ContactsContract.Contacts.CONTENT_URI,
    null,
    null,
    null,
    null
)
```

**Единая схема компонентов (концептуально):**

```text

        AndroidManifest.xml
  (основные компоненты объявлены здесь)




    Activity   Service  Receiver  Provider


            Все используют / получают Context


       Context и Intent (где применимо)
  Единый доступ к ресурсам и обмену сообщениями

```

**Основные включённые компоненты:**

- `Activity` — экран(ы) UI, объявляется в манифесте, запускается через `Intent`.
- `Fragment` — части UI/поведения, хостятся в `Activity`, не объявляются в манифесте, используют `Context` хоста.
- `Service` — фоновая / длительная работа, объявляется в манифесте, запускается/привязывается через `Intent`.
- `BroadcastReceiver` — обработчик событий/широковещательных сообщений, объявляется в манифесте или регистрируется во время выполнения, вызывается через `Intent`.
- `ContentProvider` — доступ к структурированным данным, объявляется в манифесте, используется через URI/`ContentResolver`, с жизненным циклом, управляемым фреймворком.

**Краткий вывод (RU):**

Что объединяет основные компоненты Android-приложения:

1. Все так или иначе работают с `Context` для доступа к ресурсам и системным сервисам (часть наследует его, часть получает).
2. Четыре основных компонента (`Activity`, `Service`, `BroadcastReceiver`, `ContentProvider`) объявляются в `AndroidManifest.xml`, и их создание/жизненный цикл управляются системой.
3. `Intent` даёт общий механизм запуска и коммуникации для `Activity`, `Service` и `BroadcastReceiver`; `ContentProvider` и `Fragment` интегрируются в эту экосистему через `Context`, URI и жизненные циклы, управляемые фреймворком.

---

## Answer (EN)
Main Android application components are unified by three recurring aspects (with some nuances):

1. `Context` — resource and system access
2. Manifest — lifecycle ownership and visibility (for the four core components)
3. `Intent` — messaging and activation (where applicable)

**1. `Context` — Resource Access**

All these components either extend `Context` or receive a `Context` to access resources and system services:

```kotlin
// Activity extends ContextThemeWrapper (which extends ContextWrapper -> Context)
class MainActivity : AppCompatActivity() {
    fun accessResources() {
        val string = getString(R.string.app_name)
        val color = getColor(R.color.primary)
        val pm = packageManager
    }
}

// Service extends ContextWrapper -> Context
class MusicService : Service() {
    fun accessSystemServices() {
        val notificationManager =
            getSystemService(Context.NOTIFICATION_SERVICE) as NotificationManager
        val audioManager =
            getSystemService(Context.AUDIO_SERVICE) as AudioManager
    }
}

// BroadcastReceiver receives Context in onReceive
class NetworkReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        val connectivityManager =
            context.getSystemService(Context.CONNECTIVITY_SERVICE) as ConnectivityManager
    }
}

// Fragment is not a Context but is always associated with one
class ProfileFragment : Fragment() {
    fun useContext() {
        val title = requireContext().getString(R.string.title)
    }
}
```

**2. AndroidManifest.xml — Declaration of Core Components**

The four core application components — `Activity`, `Service`, `BroadcastReceiver`, `ContentProvider` — are declared in the manifest so the system can create and manage them. Fragments are NOT declared in the manifest.

```xml
<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <application>
        <!-- Activity -->
        <activity
            android:name=".MainActivity"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- Service -->
        <service
            android:name=".MusicService"
            android:exported="false" />

        <!-- BroadcastReceiver -->
        <receiver
            android:name=".NetworkReceiver"
            android:exported="true">
            <intent-filter>
                <!-- Example custom broadcast action -->
                <action android:name="com.example.CUSTOM_ACTION" />
            </intent-filter>
        </receiver>

        <!-- ContentProvider -->
        <provider
            android:name=".NotesProvider"
            android:authorities="com.example.notes"
            android:exported="true" />
    </application>

</manifest>
```

**3. `Intent` — Activation and Communication (for suitable components)**

Intents provide a unified mechanism to activate and communicate with certain components:

- Start activities using explicit or implicit `Intent` with corresponding `IntentFilter`.
- Start (or bind) services, including modern foreground/background patterns within platform constraints.
- Send and receive broadcasts for both system and custom actions.

`ContentProvider` is typically accessed via URIs through `ContentResolver` (not via `Intent`), and Fragments usually interact via `FragmentManager` and direct method calls.

```kotlin
// Start Activity
val activityIntent = Intent(this, ProfileActivity::class.java)
startActivity(activityIntent)

// Start Service (for modern apps prefer foreground or work APIs as appropriate)
val serviceIntent = Intent(this, MusicService::class.java)
startService(serviceIntent)

// Send Broadcast (custom action)
val broadcastIntent = Intent("com.example.CUSTOM_ACTION")
sendBroadcast(broadcastIntent)

// Access ContentProvider (URI-based access via ContentResolver)
contentResolver.query(
    ContactsContract.Contacts.CONTENT_URI,
    null,
    null,
    null,
    null
)
```

**Unified Component Diagram (Conceptual):**

```text

        AndroidManifest.xml
  (Core components declared here)




    Activity   Service  Receiver  Provider


            All use / receive Context


       Context & Intents (where applicable)
   Unified access to resources + messaging

```

**Main Components Included:**

- `Activity` — UI screens, manifest-declared, started via `Intent`.
- `Fragment` — UI portions / behavior hosted by activities, not manifest-declared, uses host's `Context`.
- `Service` — Background / long-running work, manifest-declared, started/bound via `Intent`.
- `BroadcastReceiver` — Event/broadcast handler, manifest-declared or registered at runtime, triggered by `Intent`.
- `ContentProvider` — Structured data access, manifest-declared, accessed via URIs/`ContentResolver`.

**Summary (EN):**

What unifies the main Android components:

1. All of them work with a `Context` to access resources and system services (some extend it, some receive it).
2. The four core components (`Activity`, `Service`, `BroadcastReceiver`, `ContentProvider`) are defined in AndroidManifest.xml so the system can instantiate and manage them.
3. Intents provide a common mechanism to start and communicate with Activities, Services, and BroadcastReceivers; ContentProviders and Fragments integrate into this ecosystem via `Context` and framework-managed lifecycles.

---

## Дополнительные Вопросы (RU)

- [[c-android-components]] — Уточнить роли и взаимодействие отдельных компонентов.
- [[c-intent]] — Подробнее об типах `Intent`, фильтрах и разрешении.
- Как система выбирает компонент по неявному `Intent` и что влияет на приоритет?
- Как ограничения фоновой работы влияют на выбор между `Service`, WorkManager и JobScheduler?
- Как безопасно использовать `BroadcastReceiver` и `ContentProvider` с точки зрения безопасности и приватности?

## Follow-ups

- [[c-android-components]] — Clarify roles and interactions of individual components.
- [[c-intent]] — Deep dive into intent types, filters, and resolution.
- How does the system resolve implicit intents between multiple matching components?
- How do background execution limits influence the choice between Service, WorkManager, and JobScheduler?
- How do you secure BroadcastReceivers and ContentProviders to avoid leaking sensitive data?

## Ссылки (RU)

- [Services](https://developer.android.com/develop/background-work/services)
- [Activities](https://developer.android.com/guide/components/activities)

## References

- [Services](https://developer.android.com/develop/background-work/services)
- [Activities](https://developer.android.com/guide/components/activities)

## Связанные Вопросы (RU)

### Базовый Уровень (Easy)
- [[q-architecture-components-libraries--android--easy]] - Основы
- [[q-android-components-besides-activity--android--easy]] - Основы
- [[q-main-android-components--android--easy]] - Основы
- [[q-android-app-components--android--easy]] - Основы

### Продвинутый Уровень (Harder)
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Основы
- [[q-what-unites-the-main-components-of-an-android-application--android--medium]] - Основы
- [[q-hilt-components-scope--android--medium]] - Основы

## Related Questions

### Related (Easy)
- [[q-architecture-components-libraries--android--easy]] - Fundamentals
- [[q-android-components-besides-activity--android--easy]] - Fundamentals
- [[q-main-android-components--android--easy]] - Fundamentals
- [[q-android-app-components--android--easy]] - Fundamentals

### Advanced (Harder)
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Fundamentals
- [[q-what-unites-the-main-components-of-an-android-application--android--medium]] - Fundamentals
- [[q-hilt-components-scope--android--medium]] - Fundamentals
