---
id: "20251015082237330"
title: "Activity Lifecycle Methods / Методы жизненного цикла Activity"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [activity, lifecycle, difficulty/medium]
---
# Какие есть методы жизненного цикла Activity и как они отрабатывают?

# Question (EN)
> What Activity lifecycle methods exist and how do they work?

# Вопрос (RU)
> Какие есть методы жизненного цикла Activity и как они отрабатывают?

---

## Answer (EN)

Activity lifecycle methods are a set of callbacks called by Android when Activity state changes. They provide control over app behavior during creation, stopping, resuming, or destruction.

**Main lifecycle methods:**
- `onCreate()`: Initialize Activity (create UI, bind data) - called ONCE
- `onStart()`: Activity becomes visible - called MULTIPLE times
- `onResume()`: Activity in foreground, user can interact
- `onPause()`: Activity losing focus, user leaving
- `onStop()`: Activity no longer visible
- `onDestroy()`: Activity being destroyed
- `onRestart()`: Activity restarting from stopped state

---

## Ответ (RU)

Методы жизненного цикла Activity представляют собой набор коллбэков, которые вызываются системой Android при изменении состояния Activity. Эти методы предоставляют возможность управлять поведением приложения при создании, остановке, восстановлении или уничтожении.

### Основные методы жизненного цикла

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        // Инициализация Activity: создание UI, привязка данных
        // Вызывается ОДИН раз при создании
    }

    override fun onStart() {
        super.onStart()
        // Activity становится видимой пользователю
        // Может вызываться МНОГО раз
    }

    override fun onResume() {
        super.onResume()
        // Activity на переднем плане, пользователь может взаимодействовать
        // Начать анимации, получить фокус
    }

    override fun onPause() {
        super.onPause()
        // Activity теряет фокус (например, открылся диалог)
        // Сохранить важные данные, остановить анимации
        // БЫСТРО! Не более 1-2 секунд
    }

    override fun onStop() {
        super.onStop()
        // Activity больше не видна
        // Освободить ресурсы, остановить обновления
    }

    override fun onRestart() {
        super.onRestart()
        // Activity возобновляется после onStop()
        // Далее вызывается onStart()
    }

    override fun onDestroy() {
        super.onDestroy()
        // Activity уничтожается
        // Финальная очистка ресурсов
    }
}
```

### Диаграмма жизненного цикла

```

   Created   

       
       ↓
   onCreate()
       
       ↓
   onStart() ←
                       
       ↓                
   onResume()      onRestart()
                       
       ↓                
            
    RUNNING          
            
                      
        ↓              
   onPause()           
                      
        ↓              
   onStop() 
        
        ↓
   onDestroy()
        
        ↓
   
   Destroyed
   
```

### Сценарии использования

#### Сценарий 1: Первый запуск приложения

```
onCreate() → onStart() → onResume()
```

```kotlin
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_my)
        Log.d("Lifecycle", "onCreate called")

        // Инициализация
        initViews()
        loadInitialData()
    }

    override fun onStart() {
        super.onStart()
        Log.d("Lifecycle", "onStart called")
        // Activity становится видимой
    }

    override fun onResume() {
        super.onResume()
        Log.d("Lifecycle", "onResume called")
        // Начать обновления UI
        startLocationUpdates()
    }
}
```

#### Сценарий 2: Нажатие кнопки Home

```
onPause() → onStop()
```

```kotlin
override fun onPause() {
    super.onPause()
    // Сохранить черновик
    saveDraft()
}

override fun onStop() {
    super.onStop()
    // Остановить фоновые обновления
    stopLocationUpdates()
}
```

#### Сценарий 3: Возврат в приложение

```
onRestart() → onStart() → onResume()
```

```kotlin
override fun onRestart() {
    super.onRestart()
    Log.d("Lifecycle", "Activity restarting")
    // Подготовка к возобновлению
}

override fun onStart() {
    super.onStart()
    // Обновить данные, если нужно
    refreshData()
}
```

#### Сценарий 4: Поворот экрана

```
onPause() → onStop() → onDestroy() → onCreate() → onStart() → onResume()
```

```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    // Восстановление состояния после поворота
    if (savedInstanceState != null) {
        val savedText = savedInstanceState.getString("user_input")
        editText.setText(savedText)
    }
}

override fun onSaveInstanceState(outState: Bundle) {
    super.onSaveInstanceState(outState)
    // Сохранить состояние перед уничтожением
    outState.putString("user_input", editText.text.toString())
}
```

### Практические примеры

#### Управление ресурсами

```kotlin
class VideoPlayerActivity : AppCompatActivity() {
    private lateinit var player: MediaPlayer

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_video)
        player = MediaPlayer.create(this, R.raw.video)
    }

    override fun onResume() {
        super.onResume()
        player.start()  // Начать воспроизведение
    }

    override fun onPause() {
        super.onPause()
        player.pause()  // Приостановить при потере фокуса
    }

    override fun onDestroy() {
        super.onDestroy()
        player.release()  // Освободить ресурсы
    }
}
```

#### Регистрация/отмена слушателей

```kotlin
class LocationActivity : AppCompatActivity() {
    private lateinit var locationManager: LocationManager
    private val locationListener = object : LocationListener {
        override fun onLocationChanged(location: Location) {
            updateUI(location)
        }
    }

    override fun onStart() {
        super.onStart()
        // Начать получать обновления локации
        locationManager.requestLocationUpdates(
            LocationManager.GPS_PROVIDER,
            1000L,
            10f,
            locationListener
        )
    }

    override fun onStop() {
        super.onStop()
        // Остановить обновления при невидимости
        locationManager.removeUpdates(locationListener)
    }
}
```

#### Сохранение состояния

```kotlin
class FormActivity : AppCompatActivity() {
    private lateinit var nameInput: EditText
    private lateinit var emailInput: EditText

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putString("name", nameInput.text.toString())
        outState.putString("email", emailInput.text.toString())
    }

    override fun onRestoreInstanceState(savedInstanceState: Bundle) {
        super.onRestoreInstanceState(savedInstanceState)
        nameInput.setText(savedInstanceState.getString("name"))
        emailInput.setText(savedInstanceState.getString("email"))
    }
}
```

### Важные правила

**onCreate():**
-  Инициализация UI (setContentView)
-  Создание объектов
-  Привязка данных
-  Длительные операции (использовать фоновые потоки)

**onPause():**
-  Сохранение критичных данных
-  Остановка анимаций
-  Длительные операции (метод должен выполниться быстро!)

**onStop():**
-  Освобождение ресурсов
-  Отмена регистрации слушателей
-  Остановка фоновых задач

**onDestroy():**
-  Финальная очистка
-  Освобождение всех ресурсов
-  Может не вызваться (system kill)

### Современный подход с Lifecycle

```kotlin
class ModernActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Lifecycle-aware компоненты
        lifecycle.addObserver(MyLifecycleObserver())

        // ViewModel переживает изменения конфигурации
        val viewModel: MyViewModel by viewModels()
    }
}

// Modern approach: Use DefaultLifecycleObserver instead of deprecated @OnLifecycleEvent
class MyLifecycleObserver : DefaultLifecycleObserver {
    override fun onResume(owner: LifecycleOwner) {
        super.onResume(owner)
        // Автоматически вызывается при onResume()
    }

    override fun onPause(owner: LifecycleOwner) {
        super.onPause(owner)
        // Автоматически вызывается при onPause()
    }
}

// Note: @OnLifecycleEvent annotation is deprecated since Lifecycle 2.4.0
// Use DefaultLifecycleObserver interface for better type safety
```

**English**: Activity lifecycle methods are callbacks invoked by Android system during state changes: `onCreate()` (initialization, called once), `onStart()` (becomes visible), `onResume()` (foreground, interactive), `onPause()` (loses focus, save data quickly), `onStop()` (no longer visible, release resources), `onRestart()` (resuming after stop), `onDestroy()` (final cleanup). Proper management prevents resource leaks and ensures smooth UX. **Important:** `onDestroy()` may not be called if system kills process - use `onSaveInstanceState()` for critical data. Modern approach: use `DefaultLifecycleObserver` (not deprecated `@OnLifecycleEvent`).

---

## Related Questions

### Prerequisites (Easier)
- [[q-viewmodel-pattern--android--easy]] - Lifecycle

### Related (Medium)
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Lifecycle, Activity
- [[q-fragment-vs-activity-lifecycle--android--medium]] - Lifecycle, Activity
- [[q-how-does-fragment-lifecycle-differ-from-activity-v2--android--medium]] - Lifecycle, Activity
- [[q-what-are-activity-lifecycle-methods-and-how-do-they-work--android--medium]] - Lifecycle, Activity
- [[q-how-does-activity-lifecycle-work--android--medium]] - Lifecycle, Activity
