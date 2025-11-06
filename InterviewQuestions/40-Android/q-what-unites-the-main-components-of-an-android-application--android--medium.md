---
id: android-206
title: Android Components Unity / Объединение основных компонентов
aliases:
- Android Components Unity
- Объединение компонентов
topic: android
subtopics:
- activity
- fragment
- service
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-android-components
- c-context
- c-manifest
- q-what-each-android-component-represents--android--easy
- q-what-unifies-android-components--android--easy
created: 2025-10-15
updated: 2025-10-31
tags:
- android/activity
- android/fragment
- android/service
- architecture
- components
- context
- difficulty/medium
---

# Вопрос (RU)
> Объединение основных компонентов

# Question (EN)
> Android Components Unity

---

## Answer (EN)
The main Android components (`Activity`, `Service`, `BroadcastReceiver`, `ContentProvider`) share several fundamental characteristics that unite them in the Android framework.

### Four Main Components

```
Android Application Components
 Activity        → UI screens
 Service         → Background operations
 BroadcastReceiver → System/app events
 ContentProvider   → Data sharing
```

### Common Characteristics

#### 1. AndroidManifest.xml Declaration

All components must be declared in the manifest:

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

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
            android:name=".MyService"
            android:exported="false" />

        <!-- BroadcastReceiver -->
        <receiver
            android:name=".MyReceiver"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
            </intent-filter>
        </receiver>

        <!-- ContentProvider -->
        <provider
            android:name=".MyContentProvider"
            android:authorities="com.example.app.provider"
            android:exported="false" />
    </application>
</manifest>
```

#### 2. System Management

All components are **created and managed by the Android system**, not by the developer:

```kotlin
// - You don't do this:
val activity = MainActivity()
activity.onCreate()

// - System does this:
// startActivity(Intent(this, MainActivity::class.java))
// System creates and calls lifecycle methods
```

**System responsibilities**:
- Component instantiation
- `Lifecycle` management
- Process allocation
- Memory management
- Component destruction

#### 3. `Intent` Communication

Components interact through **Intents**:

```kotlin
// Start Activity
val intent = Intent(this, DetailActivity::class.java)
startActivity(intent)

// Start Service
val serviceIntent = Intent(this, DownloadService::class.java)
startService(serviceIntent)

// Send Broadcast
val broadcastIntent = Intent("com.example.CUSTOM_ACTION")
sendBroadcast(broadcastIntent)

// Query ContentProvider (uses ContentResolver, not direct Intent)
val uri = Uri.parse("content://com.example.app.provider/users")
contentResolver.query(uri, null, null, null, null)
```

#### 4. `Context` Access

All components have access to **`Context`**:

```kotlin
class MainActivity : AppCompatActivity() {
    // Activity IS a Context
    fun example() {
        val context: Context = this
        val appContext = applicationContext
    }
}

class MyService : Service() {
    // Service IS a Context
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val context: Context = this
        return START_STICKY
    }
}

class MyReceiver : BroadcastReceiver() {
    // Receiver RECEIVES a Context
    override fun onReceive(context: Context, intent: Intent) {
        // Use context parameter
    }
}

class MyProvider : ContentProvider() {
    // Provider HAS context property
    override fun onCreate(): Boolean {
        val ctx = context
        return true
    }
}
```

#### 5. Defined Lifecycles

Each component has a **specific lifecycle** managed by the system:

```kotlin
// Activity Lifecycle
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) { }
    override fun onStart() { }
    override fun onResume() { }
    override fun onPause() { }
    override fun onStop() { }
    override fun onDestroy() { }
}

// Service Lifecycle
class MyService : Service() {
    override fun onCreate() { }
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int { }
    override fun onBind(intent: Intent?): IBinder? { }
    override fun onDestroy() { }
}

// BroadcastReceiver Lifecycle
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Short-lived: must complete within 10 seconds
    }
}

// ContentProvider Lifecycle
class MyProvider : ContentProvider() {
    override fun onCreate(): Boolean { }
    // No explicit destroy - lives with application process
}
```

#### 6. Run in `Application` Process

All components run in the **same process** by default:

```xml
<!-- Default: all components in same process -->
<application android:process=":main">
    <activity android:name=".MainActivity" />
    <service android:name=".MyService" />
</application>

<!-- Can specify separate process -->
<service
    android:name=".HeavyService"
    android:process=":background" />
```

#### 7. Permission Requirements

Components can require **permissions**:

```xml
<!-- Activity requiring permission -->
<activity
    android:name=".AdminActivity"
    android:permission="android.permission.ADMIN_PRIVILEGES" />

<!-- Service requiring permission to bind -->
<service
    android:name=".SecureService"
    android:permission="com.example.app.BIND_SERVICE" />

<!-- BroadcastReceiver requiring permission to send -->
<receiver
    android:name=".SecureReceiver"
    android:permission="android.permission.RECEIVE_BOOT_COMPLETED" />

<!-- ContentProvider requiring permissions -->
<provider
    android:name=".SecureProvider"
    android:readPermission="com.example.app.READ_DATA"
    android:writePermission="com.example.app.WRITE_DATA" />
```

### Component Comparison Table

| Characteristic | `Activity` | `Service` | `BroadcastReceiver` | `ContentProvider` |
|----------------|----------|---------|-------------------|-----------------|
| Purpose | UI screen | Background work | Event handling | Data sharing |
| Has UI | Yes | No | No | No |
| `Lifecycle` | Complex (7 states) | Medium (4 states) | Simple (1 method) | Minimal |
| Created by | System | System | System | System |
| Manifest required | Yes | Yes | Yes (for static) | Yes |
| `Intent` interaction | Yes | Yes | Yes | No (uses ContentResolver) |
| `Context` access | IS `Context` | IS `Context` | RECEIVES `Context` | HAS context |
| Process | App process | App/separate | App process | App process |
| Max runtime | User-controlled | Indefinite | 10 seconds | Process lifetime |

### Unified Architecture Pattern

```kotlin
// All components follow similar patterns:

// 1. Manifest declaration
// 2. Extend base class
// 3. Override lifecycle methods
// 4. Access Context
// 5. Interact via Intent/ContentResolver

// Example Service
class DownloadService : Service() {  // 2. Extend base
    override fun onCreate() {         // 3. Lifecycle
        super.onCreate()
        val ctx: Context = this       // 4. Context access
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Intent received                  5. Intent interaction
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}

// 1. Manifest:
// <service android:name=".DownloadService" />
```

### Communication Between Components

```kotlin
// Activity → Service
val intent = Intent(this, MyService::class.java)
startService(intent)

// Activity → BroadcastReceiver
val intent = Intent("com.example.ACTION")
sendBroadcast(intent)

// Service → Activity (via notification)
val notificationIntent = Intent(this, MainActivity::class.java)
val pendingIntent = PendingIntent.getActivity(this, 0, notificationIntent, 0)

// Any component → ContentProvider
val uri = Uri.parse("content://authority/path")
contentResolver.query(uri, null, null, null, null)

// BroadcastReceiver → Service
override fun onReceive(context: Context, intent: Intent) {
    val serviceIntent = Intent(context, MyService::class.java)
    context.startService(serviceIntent)
}
```

### Summary

Main Android components are united by:
1. **Manifest declaration** - all must be declared
2. **System management** - lifecycle controlled by OS
3. **`Intent`/ContentResolver communication** - standard interaction pattern
4. **`Context` access** - all have access to Android context
5. **Defined lifecycles** - predictable state transitions
6. **Process execution** - run in application process
7. **Permission system** - consistent security model


# Question (EN)
> Android Components Unity

---


---


## Answer (EN)
The main Android components (`Activity`, `Service`, `BroadcastReceiver`, `ContentProvider`) share several fundamental characteristics that unite them in the Android framework.

### Four Main Components

```
Android Application Components
 Activity        → UI screens
 Service         → Background operations
 BroadcastReceiver → System/app events
 ContentProvider   → Data sharing
```

### Common Characteristics

#### 1. AndroidManifest.xml Declaration

All components must be declared in the manifest:

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android"
    package="com.example.app">

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
            android:name=".MyService"
            android:exported="false" />

        <!-- BroadcastReceiver -->
        <receiver
            android:name=".MyReceiver"
            android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
            </intent-filter>
        </receiver>

        <!-- ContentProvider -->
        <provider
            android:name=".MyContentProvider"
            android:authorities="com.example.app.provider"
            android:exported="false" />
    </application>
</manifest>
```

#### 2. System Management

All components are **created and managed by the Android system**, not by the developer:

```kotlin
// - You don't do this:
val activity = MainActivity()
activity.onCreate()

// - System does this:
// startActivity(Intent(this, MainActivity::class.java))
// System creates and calls lifecycle methods
```

**System responsibilities**:
- Component instantiation
- `Lifecycle` management
- Process allocation
- Memory management
- Component destruction

#### 3. `Intent` Communication

Components interact through **Intents**:

```kotlin
// Start Activity
val intent = Intent(this, DetailActivity::class.java)
startActivity(intent)

// Start Service
val serviceIntent = Intent(this, DownloadService::class.java)
startService(serviceIntent)

// Send Broadcast
val broadcastIntent = Intent("com.example.CUSTOM_ACTION")
sendBroadcast(broadcastIntent)

// Query ContentProvider (uses ContentResolver, not direct Intent)
val uri = Uri.parse("content://com.example.app.provider/users")
contentResolver.query(uri, null, null, null, null)
```

#### 4. `Context` Access

All components have access to **`Context`**:

```kotlin
class MainActivity : AppCompatActivity() {
    // Activity IS a Context
    fun example() {
        val context: Context = this
        val appContext = applicationContext
    }
}

class MyService : Service() {
    // Service IS a Context
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val context: Context = this
        return START_STICKY
    }
}

class MyReceiver : BroadcastReceiver() {
    // Receiver RECEIVES a Context
    override fun onReceive(context: Context, intent: Intent) {
        // Use context parameter
    }
}

class MyProvider : ContentProvider() {
    // Provider HAS context property
    override fun onCreate(): Boolean {
        val ctx = context
        return true
    }
}
```

#### 5. Defined Lifecycles

Each component has a **specific lifecycle** managed by the system:

```kotlin
// Activity Lifecycle
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) { }
    override fun onStart() { }
    override fun onResume() { }
    override fun onPause() { }
    override fun onStop() { }
    override fun onDestroy() { }
}

// Service Lifecycle
class MyService : Service() {
    override fun onCreate() { }
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int { }
    override fun onBind(intent: Intent?): IBinder? { }
    override fun onDestroy() { }
}

// BroadcastReceiver Lifecycle
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Short-lived: must complete within 10 seconds
    }
}

// ContentProvider Lifecycle
class MyProvider : ContentProvider() {
    override fun onCreate(): Boolean { }
    // No explicit destroy - lives with application process
}
```

#### 6. Run in `Application` Process

All components run in the **same process** by default:

```xml
<!-- Default: all components in same process -->
<application android:process=":main">
    <activity android:name=".MainActivity" />
    <service android:name=".MyService" />
</application>

<!-- Can specify separate process -->
<service
    android:name=".HeavyService"
    android:process=":background" />
```

#### 7. Permission Requirements

Components can require **permissions**:

```xml
<!-- Activity requiring permission -->
<activity
    android:name=".AdminActivity"
    android:permission="android.permission.ADMIN_PRIVILEGES" />

<!-- Service requiring permission to bind -->
<service
    android:name=".SecureService"
    android:permission="com.example.app.BIND_SERVICE" />

<!-- BroadcastReceiver requiring permission to send -->
<receiver
    android:name=".SecureReceiver"
    android:permission="android.permission.RECEIVE_BOOT_COMPLETED" />

<!-- ContentProvider requiring permissions -->
<provider
    android:name=".SecureProvider"
    android:readPermission="com.example.app.READ_DATA"
    android:writePermission="com.example.app.WRITE_DATA" />
```

### Component Comparison Table

| Characteristic | `Activity` | `Service` | `BroadcastReceiver` | `ContentProvider` |
|----------------|----------|---------|-------------------|-----------------|
| Purpose | UI screen | Background work | Event handling | Data sharing |
| Has UI | Yes | No | No | No |
| `Lifecycle` | Complex (7 states) | Medium (4 states) | Simple (1 method) | Minimal |
| Created by | System | System | System | System |
| Manifest required | Yes | Yes | Yes (for static) | Yes |
| `Intent` interaction | Yes | Yes | Yes | No (uses ContentResolver) |
| `Context` access | IS `Context` | IS `Context` | RECEIVES `Context` | HAS context |
| Process | App process | App/separate | App process | App process |
| Max runtime | User-controlled | Indefinite | 10 seconds | Process lifetime |

### Unified Architecture Pattern

```kotlin
// All components follow similar patterns:

// 1. Manifest declaration
// 2. Extend base class
// 3. Override lifecycle methods
// 4. Access Context
// 5. Interact via Intent/ContentResolver

// Example Service
class DownloadService : Service() {  // 2. Extend base
    override fun onCreate() {         // 3. Lifecycle
        super.onCreate()
        val ctx: Context = this       // 4. Context access
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // Intent received                  5. Intent interaction
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null
}

// 1. Manifest:
// <service android:name=".DownloadService" />
```

### Communication Between Components

```kotlin
// Activity → Service
val intent = Intent(this, MyService::class.java)
startService(intent)

// Activity → BroadcastReceiver
val intent = Intent("com.example.ACTION")
sendBroadcast(intent)

// Service → Activity (via notification)
val notificationIntent = Intent(this, MainActivity::class.java)
val pendingIntent = PendingIntent.getActivity(this, 0, notificationIntent, 0)

// Any component → ContentProvider
val uri = Uri.parse("content://authority/path")
contentResolver.query(uri, null, null, null, null)

// BroadcastReceiver → Service
override fun onReceive(context: Context, intent: Intent) {
    val serviceIntent = Intent(context, MyService::class.java)
    context.startService(serviceIntent)
}
```

### Summary

Main Android components are united by:
1. **Manifest declaration** - all must be declared
2. **System management** - lifecycle controlled by OS
3. **`Intent`/ContentResolver communication** - standard interaction pattern
4. **`Context` access** - all have access to Android context
5. **Defined lifecycles** - predictable state transitions
6. **Process execution** - run in application process
7. **Permission system** - consistent security model

## Ответ (RU)

Основные компоненты Android (`Activity`, `Service`, `BroadcastReceiver`, `ContentProvider`) разделяют несколько фундаментальных характеристик, которые объединяют их в Android framework.

### Четыре Основных Компонента

```
Компоненты Android приложения
 Activity        → UI экраны
 Service         → Фоновые операции
 BroadcastReceiver → Системные/приложенческие события
 ContentProvider   → Обмен данными
```

### Общие Характеристики

#### 1. Объявление В AndroidManifest.xml

Все компоненты должны быть объявлены в манифесте:

```xml
<manifest>
    <application>
        <!-- Activity -->
        <activity android:name=".MainActivity" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <!-- Service -->
        <service android:name=".MyService" android:exported="false" />

        <!-- BroadcastReceiver -->
        <receiver android:name=".MyReceiver" android:exported="true">
            <intent-filter>
                <action android:name="android.intent.action.BOOT_COMPLETED" />
            </intent-filter>
        </receiver>

        <!-- ContentProvider -->
        <provider
            android:name=".MyContentProvider"
            android:authorities="com.example.app.provider"
            android:exported="false" />
    </application>
</manifest>
```

#### 2. Управление Системой

Все компоненты **создаются и управляются системой Android**, а не разработчиком:

```kotlin
// Вы НЕ делаете это:
val activity = MainActivity()
activity.onCreate()

// Система делает это:
// startActivity(Intent(this, MainActivity::class.java))
// Система создает и вызывает lifecycle методы
```

**Обязанности системы**:
- Создание экземпляров компонентов
- Управление жизненным циклом
- Выделение процессов
- Управление памятью
- Уничтожение компонентов

#### 3. Взаимодействие Через `Intent`

Компоненты взаимодействуют через **Intents**:

```kotlin
// Запуск Activity
val intent = Intent(this, DetailActivity::class.java)
startActivity(intent)

// Запуск Service
val serviceIntent = Intent(this, DownloadService::class.java)
startService(serviceIntent)

// Отправка Broadcast
val broadcastIntent = Intent("com.example.CUSTOM_ACTION")
sendBroadcast(broadcastIntent)

// Запрос к ContentProvider (использует ContentResolver, не прямой Intent)
val uri = Uri.parse("content://com.example.app.provider/users")
contentResolver.query(uri, null, null, null, null)
```

#### 4. Доступ К `Context`

Все компоненты имеют доступ к **`Context`**:

```kotlin
class MainActivity : AppCompatActivity() {
    // Activity ЯВЛЯЕТСЯ Context
    fun example() {
        val context: Context = this
        val appContext = applicationContext
    }
}

class MyService : Service() {
    // Service ЯВЛЯЕТСЯ Context
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val context: Context = this
        return START_STICKY
    }
}

class MyReceiver : BroadcastReceiver() {
    // Receiver ПОЛУЧАЕТ Context
    override fun onReceive(context: Context, intent: Intent) {
        // Используем параметр context
    }
}

class MyProvider : ContentProvider() {
    // Provider ИМЕЕТ свойство context
    override fun onCreate(): Boolean {
        val ctx = context
        return true
    }
}
```

#### 5. Определенные Жизненные Циклы

Каждый компонент имеет **специфический жизненный цикл**, управляемый системой:

```kotlin
// Жизненный цикл Activity
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) { }
    override fun onStart() { }
    override fun onResume() { }
    override fun onPause() { }
    override fun onStop() { }
    override fun onDestroy() { }
}

// Жизненный цикл Service
class MyService : Service() {
    override fun onCreate() { }
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int { }
    override fun onDestroy() { }
}

// Жизненный цикл BroadcastReceiver
class MyReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        // Короткоживущий: должен завершиться в течение 10 секунд
    }
}

// Жизненный цикл ContentProvider
class MyProvider : ContentProvider() {
    override fun onCreate(): Boolean { }
    // Нет явного destroy - живет с процессом приложения
}
```

#### 6. Выполнение В Процессе Приложения

Все компоненты по умолчанию выполняются в **одном процессе**:

```xml
<!-- По умолчанию: все компоненты в одном процессе -->
<application android:process=":main">
    <activity android:name=".MainActivity" />
    <service android:name=".MyService" />
</application>

<!-- Можно указать отдельный процесс -->
<service
    android:name=".HeavyService"
    android:process=":background" />
```

#### 7. Требования Разрешений

Компоненты могут требовать **разрешения**:

```xml
<!-- Activity требующий разрешение -->
<activity
    android:name=".AdminActivity"
    android:permission="android.permission.ADMIN_PRIVILEGES" />

<!-- Service требующий разрешение для bind -->
<service
    android:name=".SecureService"
    android:permission="com.example.app.BIND_SERVICE" />

<!-- BroadcastReceiver требующий разрешение для отправки -->
<receiver
    android:name=".SecureReceiver"
    android:permission="android.permission.RECEIVE_BOOT_COMPLETED" />

<!-- ContentProvider требующий разрешения -->
<provider
    android:name=".SecureProvider"
    android:readPermission="com.example.app.READ_DATA"
    android:writePermission="com.example.app.WRITE_DATA" />
```

### Таблица Сравнения Компонентов

| Характеристика | `Activity` | `Service` | `BroadcastReceiver` | `ContentProvider` |
|----------------|----------|---------|-------------------|-----------------|
| Назначение | UI экран | Фоновая работа | Обработка событий | Обмен данными |
| Имеет UI | Да | Нет | Нет | Нет |
| Жизненный цикл | Сложный (7 состояний) | Средний (4 состояния) | Простой (1 метод) | Минимальный |
| Создается | Системой | Системой | Системой | Системой |
| Манифест обязателен | Да | Да | Да (для статических) | Да |
| `Intent` взаимодействие | Да | Да | Да | Нет (использует ContentResolver) |
| Доступ к `Context` | ЯВЛЯЕТСЯ `Context` | ЯВЛЯЕТСЯ `Context` | ПОЛУЧАЕТ `Context` | ИМЕЕТ context |
| Процесс | Процесс приложения | Приложения/отдельный | Процесс приложения | Процесс приложения |
| Макс. время работы | Контролируется пользователем | Неограниченное | 10 секунд | Время жизни процесса |

### Унифицированная Архитектура

Все компоненты следуют схожим паттернам:

1. Объявление в манифесте
2. Расширение базового класса
3. Переопределение методов жизненного цикла
4. Доступ к `Context`
5. Взаимодействие через `Intent`/ContentResolver

**Пример `Service`:**
```kotlin
// 1. Объявление в манифесте:
// <service android:name=".DownloadService" />

// 2. Расширение базового класса
class DownloadService : Service() {

    // 3. Переопределение методов жизненного цикла
    override fun onCreate() {
        super.onCreate()
        val ctx: Context = this  // 4. Доступ к Context
        Log.d("Service", "Сервис создан")
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        // 5. Intent взаимодействие
        val url = intent?.getStringExtra("url")
        // Начать загрузку файла
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        Log.d("Service", "Сервис уничтожен")
    }
}
```

### Коммуникация Между Компонентами

```kotlin
// Activity → Service
val intent = Intent(this, MyService::class.java)
startService(intent)

// Activity → BroadcastReceiver
val intent = Intent("com.example.ACTION")
sendBroadcast(intent)

// Service → Activity (через уведомление)
val notificationIntent = Intent(this, MainActivity::class.java)
val pendingIntent = PendingIntent.getActivity(this, 0, notificationIntent, 0)

// Любой компонент → ContentProvider
val uri = Uri.parse("content://authority/path")
contentResolver.query(uri, null, null, null, null)

// BroadcastReceiver → Service
override fun onReceive(context: Context, intent: Intent) {
    val serviceIntent = Intent(context, MyService::class.java)
    context.startService(serviceIntent)
}
```

### Практические Сценарии Использования

**Сценарий 1: Скачивание файла с уведомлением**
```kotlin
// Activity запускает Service
class MainActivity : AppCompatActivity() {
    fun downloadFile(url: String) {
        val intent = Intent(this, DownloadService::class.java)
        intent.putExtra("url", url)
        startService(intent)
    }
}

// Service выполняет загрузку и показывает уведомление
class DownloadService : Service() {
    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        val url = intent?.getStringExtra("url") ?: return START_NOT_STICKY

        // Скачивание файла в фоне
        thread {
            downloadFileFromUrl(url)
            showNotification("Загрузка завершена")
            stopSelf()
        }

        return START_NOT_STICKY
    }

    private fun showNotification(message: String) {
        // При нажатии откроет Activity
        val intent = Intent(this, MainActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent, PendingIntent.FLAG_IMMUTABLE
        )

        val notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Загрузка")
            .setContentText(message)
            .setContentIntent(pendingIntent)
            .build()

        val notificationManager = getSystemService<NotificationManager>()
        notificationManager?.notify(1, notification)
    }

    override fun onBind(intent: Intent?): IBinder? = null
}
```

**Сценарий 2: Получение системных событий**
```kotlin
// BroadcastReceiver для системных событий
class NetworkChangeReceiver : BroadcastReceiver() {
    override fun onReceive(context: Context, intent: Intent) {
        when (intent.action) {
            ConnectivityManager.CONNECTIVITY_ACTION -> {
                val isConnected = isNetworkAvailable(context)

                if (isConnected) {
                    // Запустить Service для синхронизации
                    val serviceIntent = Intent(context, SyncService::class.java)
                    context.startService(serviceIntent)
                }

                // Отправить результат в Activity через LocalBroadcast
                val broadcastIntent = Intent("NETWORK_STATUS_CHANGED")
                broadcastIntent.putExtra("isConnected", isConnected)
                LocalBroadcastManager.getInstance(context)
                    .sendBroadcast(broadcastIntent)
            }
        }
    }

    private fun isNetworkAvailable(context: Context): Boolean {
        val cm = context.getSystemService<ConnectivityManager>()
        val network = cm?.activeNetwork ?: return false
        val capabilities = cm.getNetworkCapabilities(network) ?: return false
        return capabilities.hasCapability(NetworkCapabilities.NET_CAPABILITY_INTERNET)
    }
}

// Регистрация в манифесте
// <receiver android:name=".NetworkChangeReceiver" android:exported="false">
//     <intent-filter>
//         <action android:name="android.net.conn.CONNECTIVITY_ACTION"/>
//     </intent-filter>
// </receiver>
```

**Сценарий 3: Обмен данными через `ContentProvider`**
```kotlin
// ContentProvider для обмена данными между приложениями
class ContactsProvider : ContentProvider() {
    private lateinit var database: SQLiteDatabase

    companion object {
        const val AUTHORITY = "com.example.app.contacts"
        val CONTENT_URI: Uri = Uri.parse("content://$AUTHORITY/contacts")
    }

    override fun onCreate(): Boolean {
        val dbHelper = DatabaseHelper(context!!)
        database = dbHelper.writableDatabase
        return true
    }

    override fun query(
        uri: Uri, projection: Array<String>?, selection: String?,
        selectionArgs: Array<String>?, sortOrder: String?
    ): Cursor? {
        return database.query(
            "contacts", projection, selection,
            selectionArgs, null, null, sortOrder
        )
    }

    override fun insert(uri: Uri, values: ContentValues?): Uri? {
        val id = database.insert("contacts", null, values)
        return ContentUris.withAppendedId(CONTENT_URI, id)
    }

    override fun update(
        uri: Uri, values: ContentValues?,
        selection: String?, selectionArgs: Array<String>?
    ): Int {
        return database.update("contacts", values, selection, selectionArgs)
    }

    override fun delete(
        uri: Uri, selection: String?,
        selectionArgs: Array<String>?
    ): Int {
        return database.delete("contacts", selection, selectionArgs)
    }

    override fun getType(uri: Uri): String {
        return "vnd.android.cursor.dir/vnd.example.contacts"
    }
}

// Использование из другого приложения
class AnotherActivity : AppCompatActivity() {
    fun readContacts() {
        val uri = Uri.parse("content://com.example.app.contacts/contacts")
        val cursor = contentResolver.query(uri, null, null, null, null)

        cursor?.use {
            while (it.moveToNext()) {
                val name = it.getString(it.getColumnIndexOrThrow("name"))
                val phone = it.getString(it.getColumnIndexOrThrow("phone"))
                Log.d("Contact", "Name: $name, Phone: $phone")
            }
        }
    }
}
```

**Сценарий 4: Foreground `Service` для музыкального плеера**
```kotlin
class MusicPlayerService : Service() {
    private lateinit var mediaPlayer: MediaPlayer
    private val binder = MusicBinder()

    inner class MusicBinder : Binder() {
        fun getService(): MusicPlayerService = this@MusicPlayerService
    }

    override fun onCreate() {
        super.onCreate()
        mediaPlayer = MediaPlayer()
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        when (intent?.action) {
            "PLAY" -> playMusic()
            "PAUSE" -> pauseMusic()
            "STOP" -> stopMusic()
        }

        // Foreground service требует уведомление
        val notification = createNotification()
        startForeground(1, notification)

        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder = binder

    private fun playMusic() {
        if (!mediaPlayer.isPlaying) {
            mediaPlayer.start()
        }
    }

    private fun pauseMusic() {
        if (mediaPlayer.isPlaying) {
            mediaPlayer.pause()
        }
    }

    private fun stopMusic() {
        mediaPlayer.stop()
        stopForeground(true)
        stopSelf()
    }

    private fun createNotification(): Notification {
        val intent = Intent(this, MusicActivity::class.java)
        val pendingIntent = PendingIntent.getActivity(
            this, 0, intent, PendingIntent.FLAG_IMMUTABLE
        )

        return NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Музыкальный плеер")
            .setContentText("Воспроизведение...")
            .setSmallIcon(R.drawable.ic_music)
            .setContentIntent(pendingIntent)
            .addAction(R.drawable.ic_pause, "Пауза",
                createPendingIntent("PAUSE"))
            .addAction(R.drawable.ic_stop, "Стоп",
                createPendingIntent("STOP"))
            .build()
    }

    private fun createPendingIntent(action: String): PendingIntent {
        val intent = Intent(this, MusicPlayerService::class.java)
        intent.action = action
        return PendingIntent.getService(
            this, 0, intent, PendingIntent.FLAG_IMMUTABLE
        )
    }

    override fun onDestroy() {
        mediaPlayer.release()
        super.onDestroy()
    }
}
```

### Резюме

Основные компоненты Android объединены:
1. **Объявлением в манифесте** - все должны быть объявлены
2. **Управлением системой** - жизненный цикл контролируется ОС
3. **`Intent`/ContentResolver коммуникацией** - стандартный паттерн взаимодействия
4. **Доступом к `Context`** - все имеют доступ к Android context
5. **Определенными жизненными циклами** - предсказуемые переходы состояний
6. **Выполнением в процессе** - выполняются в процессе приложения
7. **Системой разрешений** - последовательная модель безопасности

### Ключевые Моменты Для Интервью

**Что спросят:**
- Какие основные компоненты Android?
- Что их объединяет?
- Как они взаимодействуют?

**Правильный ответ должен включать:**
1. Четыре компонента: `Activity`, `Service`, `BroadcastReceiver`, `ContentProvider`
2. Все объявляются в манифесте
3. Управляются системой, не разработчиком
4. Взаимодействуют через `Intent` (кроме `ContentProvider` - через ContentResolver)
5. Имеют доступ к `Context`
6. Имеют определенные жизненные циклы
7. Выполняются в процессе приложения (с возможностью указать отдельный процесс)

## Related Topics
- AndroidManifest.xml
- `Intent` system
- `Context` and `Application`
- Component lifecycles
- Process management

---


## Follow-ups

- [[c-android-components]]
- [[c-context]]
- [[c-manifest]]


## References

- [Services](https://developer.android.com/develop/background-work/services)
- [Activities](https://developer.android.com/guide/components/activities)


## Related Questions

### Prerequisites (Easier)
- [[q-architecture-components-libraries--android--easy]] - Fundamentals
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Fundamentals
- [[q-what-unifies-android-components--android--easy]] - Fundamentals

### Related (Medium)
- [[q-what-are-the-most-important-components-of-compose--android--medium]] - Fundamentals
- [[q-anr-application-not-responding--android--medium]] - Fundamentals
- [[q-how-to-catch-the-earliest-entry-point-into-the-application--android--medium]] - Fundamentals

### Advanced (Harder)
- [[q-how-application-priority-is-determined-by-the-system--android--hard]] - Fundamentals
