---
id: android-290
title: Activity Methods and Events / Методы Activity и события
aliases:
- Activity Methods Events
- Методы Activity
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
status: draft
moc: moc-android
related:
- c-activity-lifecycle
- q-what-are-activity-lifecycle-methods-and-how-do-they-work--android--medium
- q-what-is-activity-and-what-is-it-used-for--android--medium
created: 2025-10-15
updated: 2025-11-10
tags:
- android/activity
- android/lifecycle
- difficulty/medium
- events
- lifecycle

---

# Вопрос (RU)
> К каким событиям привязаны методы `Activity`?

# Question (EN)
> What events are `Activity` lifecycle methods tied to?

## Ответ (RU)

Методы жизненного цикла `Activity` привязаны к конкретным системным событиям, которые происходят в течение жизни `Activity`. Эти методы позволяют реагировать на изменения состояния и корректно управлять ресурсами.

### Основные события и методы жизненного цикла

```
         Activity Lifecycle Events


onCreate()   Activity создана
    ↓
onStart()   Activity становится видимой
    ↓
onResume()  Activity получает фокус, пользователь может взаимодействовать
    ↓
[Activity Running]
    ↓
onPause()   Другая Activity (или окно) частично/полностью перекрывает
    ↓
onStop()    Activity больше не видна
    ↓
onDestroy() Activity уничтожена
```

#### 1. onCreate() — событие создания `Activity`

Вызывается когда:
- `Activity` создаётся впервые;
- `Activity` пересоздаётся после убийства процесса системой;
- `Activity` пересоздаётся при конфигурационных изменениях (если не переопределено поведение через `configChanges`).

Типичные действия:
- вызвать `setContentView()`;
- инициализировать UI-компоненты;
- настроить `ViewModel`-ы;
- восстановить состояние из `savedInstanceState` (если есть);
- подписаться на данные.

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Initialize UI
        // Set up ViewModels
        // Bind views / observe LiveData

        if (savedInstanceState != null) {
            val counter = savedInstanceState.getInt("counter", 0)
            Log.d("Lifecycle", "Restored counter: $counter")
        } else {
            Log.d("Lifecycle", "First creation")
        }
    }
}
```

---

#### 2. onStart() — событие появления на экране

Вызывается когда:
- `Activity` вот-вот станет видимой пользователю;
- после `onCreate()` или `onRestart()`;
- при возвращении из фона перед `onResume()`.

Типичные действия:
- зарегистрировать `BroadcastReceiver` (если требуется, пока `Activity` видима);
- запустить анимации, зависящие от видимости;
- подготовить обновление UI.

```kotlin
override fun onStart() {
    super.onStart()

    // Пример для иллюстрации; CONNECTIVITY_ACTION устарел для сторонних приложений на новых версиях Android
    val intentFilter = IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION)
    registerReceiver(networkReceiver, intentFilter)

    Log.d("Lifecycle", "Activity is becoming visible")
}
```

---

#### 3. onResume() — событие получения фокуса

Вызывается когда:
- `Activity` готова к взаимодействию с пользователем;
- после `onStart()`;
- при возвращении из `onPause()`.

Типичные действия:
- запуск/возобновление камеры, сенсоров;
- старт или возобновление обновления местоположения;
- возобновление воспроизведения медиа или игры;
- захват эксклюзивных ресурсов (камера, микрофон) при необходимости.

```kotlin
override fun onResume() {
    super.onResume()

    cameraPreview.resume()
    locationManager.requestLocationUpdates()

    Log.d("Lifecycle", "Activity has focus - user can interact")
}
```

---

#### 4. onPause() — событие потери фокуса

Вызывается когда:
- другая `Activity` появляется на переднем плане (полностью или частично);
- поверх `Activity` показывается диалог/окно;
- в многооконном режиме фокус переходит к другому окну;
- начинается переход к другой `Activity`.

Важно:
- `onPause()` должен выполняться быстро;
- допускаются только лёгкие операции (например, запись небольших данных в память/БД);
- тяжёлые или долгие операции (сеть, большие запросы к БД) нужно выносить в фон и не блокировать UI.

```kotlin
override fun onPause() {
    super.onPause()

    cameraPreview.pause()
    locationManager.removeUpdates(locationListener)

    // Быстрое сохранение черновика / состояния
    saveDraft()

    Log.d("Lifecycle", "Activity losing focus")
}
```

Типичные действия:
- приостановить анимации, камеру, сенсоры;
- освободить эксклюзивные ресурсы, которые должны быть доступны другим;
- быстро сохранить несохранённые изменения.

---

#### 5. onStop() — событие потери видимости

Вызывается когда:
- `Activity` больше не видна пользователю;
- пользователь перешёл в другую `Activity`;
- приложение ушло в фон.

```kotlin
override fun onStop() {
    super.onStop()

    unregisterReceiver(networkReceiver)

    // Сохранить более тяжёлое состояние, если нужно
    viewModel.saveState()

    Log.d("Lifecycle", "Activity no longer visible")
}
```

Типичные действия:
- отмена регистрации `BroadcastReceiver`-ов;
- освобождение тяжёлых ресурсов (например, `Camera`, `MediaPlayer` при необходимости);
- сохранение устойчивых данных;
- остановка фоновых задач, связанных именно с этой `Activity`.

---

#### 6. onDestroy() — событие уничтожения `Activity`

Вызывается когда:
- `Activity` завершает работу (`finish()` или пользователь нажал Back);
- система уничтожает `Activity` (например, при конфигурационном изменении или для освобождения памяти).

На момент вызова:
- по флагу `isFinishing` можно отличить обычное завершение от пересоздания при конфигурации;
- не во всех сценариях уничтожения гарантированно вызывается `onDestroy()` (при убийстве процесса метод может не быть вызван).

```kotlin
override fun onDestroy() {
    super.onDestroy()

    // Очистка ресурсов, принадлежащих Activity
    // (listeners, adapters, non-shared MediaPlayer, etc.)

    if (isFinishing) {
        Log.d("Lifecycle", "Activity is finishing (user navigated away)")
    } else {
        Log.d("Lifecycle", "Activity destroyed for recreation (config change)")
    }
}
```

Типичные действия:
- освободить ресурсы, тесно связанные с UI и жизнью `Activity`;
- отписаться от коллбеков/листенеров;
- не закрывать в `onDestroy()` глобальные синглтоны/базы данных, если они не относятся к этой конкретной `Activity` (это должно делаться на уровне `Application`/репозиториев и других слоёв).

(Очистку `ViewModel` и общих ресурсов, БД и т.п. следует выполнять в соответствующих слоях, а не напрямую через `viewModelScope.cancel()` или `database.close()` внутри `Activity`.)

---

#### 7. onRestart() — событие возврата к остановленной `Activity`

Вызывается когда:
- `Activity` была остановлена (`onStop()`), но не уничтожена,
- и затем снова переходит в состояние запуска.

```kotlin
override fun onRestart() {
    super.onRestart()

    // Обновить данные / состояние при возврате
    viewModel.refreshData()

    Log.d("Lifecycle", "Activity restarting after being stopped")
}
```

Типичные действия:
- обновить данные или UI при повторном показе;
- восстановить соединения с сервисами при необходимости.

---

### Пример полного жизненного цикла (упрощённо)

```kotlin
class DetailActivity : AppCompatActivity() {

    private lateinit var viewModel: DetailViewModel
    private lateinit var networkReceiver: BroadcastReceiver
    private lateinit var player: MediaPlayer

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_detail)

        Log.d("Lifecycle", "onCreate - Activity created")

        viewModel = ViewModelProvider(this)[DetailViewModel::class.java]

        setupViews()

        savedInstanceState?.let { bundle ->
            val position = bundle.getInt("player_position", 0)
            Log.d("Lifecycle", "Restored player position: $position")
        }
    }

    override fun onStart() {
        super.onStart()
        Log.d("Lifecycle", "onStart - Activity becoming visible")

        networkReceiver = NetworkChangeReceiver()
        val filter = IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION)
        // Пример; CONNECTIVITY_ACTION устарел для сторонних приложений на новых версиях Android
        registerReceiver(networkReceiver, filter)
    }

    override fun onResume() {
        super.onResume()
        Log.d("Lifecycle", "onResume - Activity has focus")

        if (::player.isInitialized) {
            player.start()
        }

        viewModel.loadData()
    }

    override fun onPause() {
        super.onPause()
        Log.d("Lifecycle", "onPause - Activity losing focus")

        if (::player.isInitialized && player.isPlaying) {
            player.pause()
        }

        viewModel.saveDraft()
    }

    override fun onStop() {
        super.onStop()
        Log.d("Lifecycle", "onStop - Activity no longer visible")

        unregisterReceiver(networkReceiver)

        viewModel.saveToDatabase()
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d("Lifecycle", "onDestroy - Activity destroyed")

        if (::player.isInitialized) {
            player.release()
        }

        if (isFinishing) {
            Log.d("Lifecycle", "User navigated away - cleanup completely")
        } else {
            Log.d("Lifecycle", "Configuration change - will be recreated")
        }
    }

    override fun onRestart() {
        super.onRestart()
        Log.d("Lifecycle", "onRestart - Returning to activity")

        viewModel.refreshData()
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        if (::player.isInitialized) {
            outState.putInt("player_position", player.currentPosition)
        }

        Log.d("Lifecycle", "onSaveInstanceState - Saving state")
    }

    override fun onRestoreInstanceState(savedInstanceState: Bundle) {
        super.onRestoreInstanceState(savedInstanceState)

        val position = savedInstanceState.getInt("player_position", 0)
        if (::player.isInitialized) {
            player.seekTo(position)
        }

        Log.d("Lifecycle", "onRestoreInstanceState - Restored state")
    }
}
```

---

### Конфигурационные изменения

Типичные события:
- поворот экрана;
- смена языка;
- переключение светлой/тёмной темы;
- изменение размера шрифта и др.

При стандартном поведении (без переопределения `configChanges`) `Activity` уничтожается и пересоздаётся. В типичном сценарии при конфигурационном изменении последовательность колбэков выглядит так:

```
onPause()
onSaveInstanceState()
onStop()
onDestroy()
// процесс может быть убит между этими этапами
onCreate()
onStart()
onRestoreInstanceState()
onResume()
```

Важно:
- `onSaveInstanceState()` обычно вызывается до `onStop()` при конфигурационных изменениях и большинстве фоновых переходов;
- `onSaveInstanceState()` и `onDestroy()` не гарантируются при убийстве процесса системой или при некоторых сценариях завершения (`finish()`, нажатие Back) — критичные данные должны быть сохранены заранее.

```kotlin
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)

    outState.putInt("counter", counter)
    outState.putString("text", editText.text.toString())

    Log.d("Lifecycle", "Saving state before config change")
}

override fun onRestoreInstanceState(savedInstanceState: Bundle) {
    super.onRestoreInstanceState(savedInstanceState)

    counter = savedInstanceState.getInt("counter", 0)
    val text = savedInstanceState.getString("text", "")
    editText.setText(text)

    Log.d("Lifecycle", "Restored state after config change")
}
```

---

### Многооконный режим (Android 7.0+)

`onMultiWindowModeChanged(isInMultiWindowMode: `Boolean`)` вызывается при входе/выходе из многооконного режима и дополняет основные методы жизненного цикла.

```kotlin
override fun onMultiWindowModeChanged(isInMultiWindowMode: Boolean) {
    super.onMultiWindowModeChanged(isInMultiWindowMode)

    if (isInMultiWindowMode) {
        Log.d("Lifecycle", "Entered multi-window mode")
        adjustLayoutForSplitScreen()
    } else {
        Log.d("Lifecycle", "Exited multi-window mode")
        restoreFullScreenLayout()
    }
}
```

---

### Режим "картинка-в-картинке" (Android 8.0+)

`onPictureInPictureModeChanged(...)` вызывается при входе/выходе из PiP и также работает вместе с основным жизненным циклом.

```kotlin
override fun onPictureInPictureModeChanged(
    isInPictureInPictureMode: Boolean,
    newConfig: Configuration
) {
    super.onPictureInPictureModeChanged(isInPictureInPictureMode, newConfig)

    if (isInPictureInPictureMode) {
        Log.d("Lifecycle", "Entered PiP mode")
        hideControls()
    } else {
        Log.d("Lifecycle", "Exited PiP mode")
        showControls()
    }
}
```

---

### Типичные сценарии

- Сценарий 1: Открытие приложения
  - `onCreate()` → `onStart()` → `onResume()`

- Сценарий 2: Нажатие кнопки Home (`Activity` уходит в фон)
  - `onPause()` → `onStop()` (обычно также вызывается `onSaveInstanceState()` перед `onStop()`, но это не строго гарантируется для всех сценариев)

- Сценарий 3: Возврат в приложение
  - `onRestart()` → `onStart()` → `onResume()`

- Сценарий 4: Поворот экрана (по умолчанию)
  - `onPause()` → `onSaveInstanceState()` → `onStop()` → `onDestroy()` → `onCreate()` → `onStart()` → `onRestoreInstanceState()` → `onResume()`

- Сценарий 5: Нажатие кнопки Back
  - `onPause()` → `onStop()` → `onDestroy()` (без гарантированного вызова `onSaveInstanceState()`)

- Сценарий 6: Временное прерывание (например, входящий звонок / системное окно)
  - Обычно: `onPause()` при прерывании → затем `onResume()` при возврате

(В случае принудительного убийства процесса последовательность может отличаться, некоторые методы не будут вызваны.)

---

### Рекомендуемые практики (Best Practices)

1. Держите `onPause()` быстрым

```kotlin
// ПЛОХО — тяжёлая работа в onPause
override fun onPause() {
    super.onPause()
    database.saveAllData() // может блокировать UI
    uploadToServer()       // долгий сетевой вызов
}

// ХОРОШО — быстрые, неблокирующие операции в onPause
override fun onPause() {
    super.onPause()
    player.pause()
    saveDraftLocally() // маленькое, быстрое сохранение
}
```

2. Используйте `ViewModel` для данных UI, переживающих поворот

```kotlin
// ПЛОХО — данные теряются / всё перезагружается при каждом повороте
class MainActivity : AppCompatActivity() {
    private var userData: List<User> = emptyList()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        loadUserData()
    }
}

// ХОРОШО — ViewModel переживает конфигурационные изменения
class MainActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel.users.observe(this) { users ->
            updateUI(users)
        }
    }
}
```

3. Освобождайте ресурсы в `onStop()` / `onDestroy()`

```kotlin
override fun onStop() {
    super.onStop()

    unregisterReceiver(receiver)
    stopLocationUpdates()
    releaseCamera()
}
```

- Тяжёлые ресурсы (камера, плеер, подписки на сервисы) отвязывайте от `Activity` при потере видимости.
- Глобальные синглтоны, базы данных и т.п. не должны закрываться внутри конкретной `Activity`, если только они реально не принадлежат её жизненному циклу.

---

## Answer (EN)

`Activity` lifecycle methods are tied to specific system events that occur during an `Activity`'s lifetime. These callbacks allow developers to respond to state changes and manage resources correctly.

### `Activity` Lifecycle Events and Methods

```
         Activity Lifecycle Events


onCreate()   Activity is created
    ↓
onStart()   Activity becomes visible
    ↓
onResume()  Activity gains focus, user can interact
    ↓
[Activity Running]
    ↓
onPause()   Another activity/window partially or fully covers it
    ↓
onStop()    Activity no longer visible
    ↓
onDestroy() Activity is destroyed
```

### Detailed Event Mapping

#### 1. onCreate() - `Activity` Creation Event

Called when:
- the `Activity` is first created;
- the `Activity` is recreated after process death;
- the `Activity` is recreated due to a configuration change (unless handled via `configChanges`).

Use for:
- calling `setContentView()`;
- initializing UI components;
- setting up ViewModels and observers;
- restoring state from `savedInstanceState` when available.

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Initialize UI, ViewModels, observers

        if (savedInstanceState != null) {
            val counter = savedInstanceState.getInt("counter", 0)
            Log.d("Lifecycle", "Restored counter: $counter")
        } else {
            Log.d("Lifecycle", "First creation")
        }
    }
}
```

---

#### 2. onStart() - Visibility Event

Called when:
- the `Activity` is about to become visible to the user;
- after `onCreate()` or `onRestart()`;
- when coming back from the background, before `onResume()`.

Use for:
- registering `BroadcastReceiver`s bound to `Activity` visibility;
- starting animations that should run while visible;
- preparing UI updates.

```kotlin
override fun onStart() {
    super.onStart()

    // Example for illustration; CONNECTIVITY_ACTION is deprecated for third-party apps on recent Android versions
    val intentFilter = IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION)
    registerReceiver(networkReceiver, intentFilter)

    Log.d("Lifecycle", "Activity is becoming visible")
}
```

---

#### 3. onResume() - Focus Gained Event

Called when:
- the `Activity` is ready for user interaction;
- after `onStart()`;
- when returning from `onPause()`.

Use for:
- resuming camera/sensors;
- starting location updates;
- resuming media playback or game loops;
- acquiring exclusive resources when needed.

```kotlin
override fun onResume() {
    super.onResume()

    cameraPreview.resume()
    locationManager.requestLocationUpdates()

    Log.d("Lifecycle", "Activity has focus - user can interact")
}
```

---

#### 4. onPause() - Focus Lost Event

Called when:
- another `Activity` comes to the foreground (partially or fully);
- a dialog or another window obscures the `Activity`;
- in multi-window mode, focus moves away;
- the system is about to start another `Activity`.

Key points:
- `onPause()` must be fast;
- it's acceptable to do small, non-blocking work (e.g., lightweight local/DB writes);
- avoid long-running or blocking operations (e.g., network calls, heavy DB I/O) here.

```kotlin
override fun onPause() {
    super.onPause()

    cameraPreview.pause()
    locationManager.removeUpdates(locationListener)

    // Fast save (e.g., draft/state)
    saveDraft()

    Log.d("Lifecycle", "Activity losing focus")
}
```

Use for:
- pausing animations, camera, sensors;
- releasing exclusive resources so others can use them;
- quickly persisting in-progress user input.

---

#### 5. onStop() - Visibility Lost Event

Called when:
- the `Activity` is no longer visible to the user;
- the user navigates to another `Activity`;
- the app goes to the background.

```kotlin
override fun onStop() {
    super.onStop()

    unregisterReceiver(networkReceiver)

    // Persist state if needed
    viewModel.saveState()

    Log.d("Lifecycle", "Activity no longer visible")
}
```

Use for:
- unregistering `BroadcastReceiver`s;
- releasing heavier resources associated with UI visibility;
- persisting data more reliably;
- stopping background work tied to this `Activity`.

---

#### 6. onDestroy() - Destruction Event

Called when:
- the `Activity` is finishing (`finish()` or Back pressed);
- the system is destroying the `Activity` (e.g., for a configuration change or to reclaim memory).

Notes:
- `isFinishing` distinguishes user-initiated finish from destruction for recreation;
- in some destruction scenarios (e.g., process kill) `onDestroy()` may not be called.

```kotlin
override fun onDestroy() {
    super.onDestroy()

    // Clean up resources owned by this Activity

    if (isFinishing) {
        Log.d("Lifecycle", "Activity is finishing (user navigated away)")
    } else {
        Log.d("Lifecycle", "Activity destroyed for recreation (config change)")
    }
}
```

Use for:
- cleaning up `Activity`-owned resources (listeners, adapters, non-shared MediaPlayer, etc.);
- not for closing app-wide singletons/databases unless they are truly `Activity`-scoped.

---

#### 7. onRestart() - Visibility Regained Event

Called when:
- the `Activity` has been stopped and is about to start again.

```kotlin
override fun onRestart() {
    super.onRestart()

    viewModel.refreshData()

    Log.d("Lifecycle", "Activity restarting after being stopped")
}
```

Use for:
- refreshing data or UI when returning from the stopped state;
- re-establishing connections as appropriate.

---

### Complete Lifecycle Example (Simplified)

```kotlin
class DetailActivity : AppCompatActivity() {

    private lateinit var viewModel: DetailViewModel
    private lateinit var networkReceiver: BroadcastReceiver
    private lateinit var player: MediaPlayer

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_detail)

        Log.d("Lifecycle", "onCreate - Activity created")

        viewModel = ViewModelProvider(this)[DetailViewModel::class.java]

        setupViews()

        savedInstanceState?.let { bundle ->
            val position = bundle.getInt("player_position", 0)
            Log.d("Lifecycle", "Restored player position: $position")
        }
    }

    override fun onStart() {
        super.onStart()
        Log.d("Lifecycle", "onStart - Activity becoming visible")

        networkReceiver = NetworkChangeReceiver()
        val filter = IntentFilter(ConnectivityManager.CONNECTIVITY_ACTION)
        // Example; CONNECTIVITY_ACTION is deprecated for third-party apps on recent Android versions
        registerReceiver(networkReceiver, filter)
    }

    override fun onResume() {
        super.onResume()
        Log.d("Lifecycle", "onResume - Activity has focus")

        if (::player.isInitialized) {
            player.start()
        }

        viewModel.loadData()
    }

    override fun onPause() {
        super.onPause()
        Log.d("Lifecycle", "onPause - Activity losing focus")

        if (::player.isInitialized && player.isPlaying) {
            player.pause()
        }

        viewModel.saveDraft()
    }

    override fun onStop() {
        super.onStop()
        Log.d("Lifecycle", "onStop - Activity no longer visible")

        unregisterReceiver(networkReceiver)

        viewModel.saveToDatabase()
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d("Lifecycle", "onDestroy - Activity destroyed")

        if (::player.isInitialized) {
            player.release()
        }

        if (isFinishing) {
            Log.d("Lifecycle", "User navigated away - cleanup completely")
        } else {
            Log.d("Lifecycle", "Configuration change - will be recreated")
        }
    }

    override fun onRestart() {
        super.onRestart()
        Log.d("Lifecycle", "onRestart - Returning to activity")

        viewModel.refreshData()
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        if (::player.isInitialized) {
            outState.putInt("player_position", player.currentPosition)
        }

        Log.d("Lifecycle", "onSaveInstanceState - Saving state")
    }

    override fun onRestoreInstanceState(savedInstanceState: Bundle) {
        super.onRestoreInstanceState(savedInstanceState)

        val position = savedInstanceState.getInt("player_position", 0)
        if (::player.isInitialized) {
            player.seekTo(position)
        }

        Log.d("Lifecycle", "onRestoreInstanceState - Restored state")
    }
}
```

---

### Configuration Change Events

Common triggers:
- screen rotation;
- language change;
- dark mode toggle;
- font size change;
- other configuration changes.

With default behavior (no custom `configChanges`), the `Activity` is destroyed and recreated. A typical callback sequence on a configuration change is:

```
onPause()
onSaveInstanceState()
onStop()
onDestroy()
// process may be killed between these steps
onCreate()
onStart()
onRestoreInstanceState()
onResume()
```

Important:
- `onSaveInstanceState()` is typically called before `onStop()` for configuration changes and many background transitions;
- `onSaveInstanceState()` and `onDestroy()` are not guaranteed if the process is killed abruptly or for some finish/back scenarios, so critical data should be saved proactively.

```kotlin
override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)

    outState.putInt("counter", counter)
    outState.putString("text", editText.text.toString())

    Log.d("Lifecycle", "Saving state before config change")
}

override fun onRestoreInstanceState(savedInstanceState: Bundle) {
    super.onRestoreInstanceState(savedInstanceState)

    counter = savedInstanceState.getInt("counter", 0)
    val text = savedInstanceState.getString("text", "")
    editText.setText(text)

    Log.d("Lifecycle", "Restored state after config change")
}
```

---

### Multi-Window Events (Android 7.0+)

`onMultiWindowModeChanged(isInMultiWindowMode: `Boolean`)` is called when the `Activity` enters or exits multi-window mode. It complements (does not replace) the core lifecycle.

```kotlin
override fun onMultiWindowModeChanged(isInMultiWindowMode: Boolean) {
    super.onMultiWindowModeChanged(isInMultiWindowMode)

    if (isInMultiWindowMode) {
        Log.d("Lifecycle", "Entered multi-window mode")
        adjustLayoutForSplitScreen()
    } else {
        Log.d("Lifecycle", "Exited multi-window mode")
        restoreFullScreenLayout()
    }
}
```

---

### Picture-in-Picture Events (Android 8.0+)

`onPictureInPictureModeChanged(...)` is called when the `Activity` enters or exits Picture-in-Picture mode and also works together with the normal lifecycle callbacks.

```kotlin
override fun onPictureInPictureModeChanged(
    isInPictureInPictureMode: Boolean,
    newConfig: Configuration
) {
    super.onPictureInPictureModeChanged(isInPictureInPictureMode, newConfig)

    if (isInPictureInPictureMode) {
        Log.d("Lifecycle", "Entered PiP mode")
        hideControls()
    } else {
        Log.d("Lifecycle", "Exited PiP mode")
        showControls()
    }
}
```

---

### Common Event Scenarios

- Scenario 1: User Opens App
  - `onCreate()` → `onStart()` → `onResume()` → [User interacts]

- Scenario 2: User Presses Home Button
  - `onPause()` → `onStop()` (often with `onSaveInstanceState()` before `onStop()`, but this is not strictly guaranteed for all cases)

- Scenario 3: User Returns to App
  - `onRestart()` → `onStart()` → `onResume()`

- Scenario 4: User Rotates Screen (default)
  - `onPause()` → `onSaveInstanceState()` → `onStop()` → `onDestroy()` → `onCreate()` → `onStart()` → `onRestoreInstanceState()` → `onResume()`

- Scenario 5: User Presses Back Button
  - `onPause()` → `onStop()` → `onDestroy()` (without guaranteed `onSaveInstanceState()`)

- Scenario 6: Temporary Interruption (e.g., phone call UI)
  - Often: `onPause()` when interrupted → later `onResume()` when returning

(If the process is killed, some callbacks (e.g., `onDestroy()`) may not run.)

---

### Best Practices

1. Keep onPause() Fast

```kotlin
// BAD - heavy work in onPause
override fun onPause() {
    super.onPause()
    database.saveAllData() // may block UI
    uploadToServer()       // long-running network call
}

// GOOD - fast, non-blocking work in onPause
override fun onPause() {
    super.onPause()
    player.pause()
    saveDraftLocally() // small, quick save only
}
```

2. Use `ViewModel` for UI Data

```kotlin
// BAD - reloads data on every rotation
class MainActivity : AppCompatActivity() {
    private var userData: List<User> = emptyList()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        loadUserData()
    }
}

// GOOD - ViewModel survives configuration changes
class MainActivity : AppCompatActivity() {
    private val viewModel: UserViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        viewModel.users.observe(this) { users ->
            updateUI(users)
        }
    }
}
```

3. Release Resources in onStop() / onDestroy()

```kotlin
override fun onStop() {
    super.onStop()

    unregisterReceiver(receiver)
    stopLocationUpdates()
    releaseCamera()
}
```

- Heavy resources (camera, media player, service bindings) should be cleaned up when the `Activity` is no longer visible.
- Do not close global singletons/databases in an `Activity` unless they are truly scoped to it.

---

## Follow-ups

- [[c-activity-lifecycle]]
- [[q-what-are-activity-lifecycle-methods-and-how-do-they-work--android--medium]]
- Как методы жизненного цикла `Activity` работают вместе с `ViewModel` и `LiveData`?/How do `Activity` lifecycle methods work with `ViewModel` and `LiveData`?
- Как конфигурационные изменения влияют на вызовы методов жизненного цикла `Activity`?/How do configuration changes affect `Activity` lifecycle callbacks?
- Как правильно тестировать обработку событий жизненного цикла `Activity`?/How do you properly test `Activity` lifecycle event handling?

## References

- [Android Documentation](https://developer.android.com/docs)
- [Lifecycle](https://developer.android.com/topic/libraries/architecture/lifecycle)

## Related Questions

### Prerequisites (Easier)
- [[q-android-components-besides-activity--android--easy]] - `Activity`

### Related (Medium)
- [[q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]] - `Activity`
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - `Activity`
- [[q-single-activity-pros-cons--android--medium]] - `Activity`
- [[q-if-activity-starts-after-a-service-can-you-connect-to-this-service--android--medium]] - `Activity`
- [[q-activity-lifecycle-methods--android--medium]] - `Activity`

### Advanced (Harder)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - `Activity`
