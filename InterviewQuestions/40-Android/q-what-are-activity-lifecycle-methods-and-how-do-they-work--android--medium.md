---
id: 202510031417001
title: "What are Activity lifecycle methods and how do they work"
question_ru: "Какие есть методы жизненного цикла Activity и как они отрабатывают"
question_en: "What are Activity lifecycle methods and how do they work"
topic: android
moc: moc-android
status: draft
difficulty: medium
tags:
  - activity lifecycle
  - lifecycle methods
  - android/activity
  - lifecycle
  - easy_kotlin
  - lang/ru
source: https://t.me/easy_kotlin/8
---

# What are Activity lifecycle methods and how do they work

## English Answer

Activity lifecycle methods are a set of callbacks invoked by the Android system when the state of an Activity changes. These methods provide opportunities to manage application behavior during creation, stopping, resumption, or destruction. Understanding and properly using these methods is critical for creating reliable and efficient applications.

### Main Lifecycle Methods

#### 1. onCreate(Bundle savedInstanceState)
- **When**: Called when the Activity is first created
- **Purpose**: Initial setup and configuration
- **Example**: `setContentView(R.layout.activity_main)` sets the user interface layout for the Activity
- **Use for**: Initializing variables, setting up UI, binding data

```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    setContentView(R.layout.activity_main)
    // Initialize variables
    // Set up UI components
}
```

#### 2. onStart()
- **When**: Called when the Activity becomes visible to the user
- **Invoked after**: `onCreate()` or `onRestart()`
- **Purpose**: Prepare the Activity to enter the foreground and become interactive

```kotlin
override fun onStart() {
    super.onStart()
    // Activity is becoming visible
    // Start animations or update UI
}
```

#### 3. onResume()
- **When**: Called before the Activity starts interacting with the user
- **Purpose**: Activity is in the foreground and receiving user input
- **This is the last method**: Before the Activity can receive user input

```kotlin
override fun onResume() {
    super.onResume()
    // Start foreground-only behaviors
    // Register sensors or location updates
}
```

#### 4. onPause()
- **When**: Called when the system is about to resume another Activity
- **Purpose**: Stop dynamic elements and release resources
- **Use for**: Pausing animations, saving draft data, committing unsaved changes

```kotlin
override fun onPause() {
    super.onPause()
    // Pause ongoing tasks
    // Save draft data
    // Stop animations
}
```

#### 5. onStop()
- **When**: Called when the Activity is no longer visible to the user
- **Purpose**: Perform "heavier" resource cleanup
- **Use for**: Releasing resources, stopping network calls, unregistering receivers

```kotlin
override fun onStop() {
    super.onStop()
    // Release heavy resources
    // Stop background tasks
    // Unregister receivers
}
```

#### 6. onRestart()
- **When**: Called after the Activity has been stopped
- **Purpose**: Restore Activity state before starting
- **Followed by**: `onStart()` and `onResume()`

```kotlin
override fun onRestart() {
    super.onRestart()
    // Restore state after being stopped
}
```

#### 7. onDestroy()
- **When**: Called before the Activity is destroyed
- **Purpose**: Release all resources
- **Use for**: Final cleanup, releasing static resources

```kotlin
override fun onDestroy() {
    super.onDestroy()
    // Final cleanup
    // Release all resources
}
```

### Lifecycle Flow Diagram

```
onCreate() → onStart() → onResume() → [Running]
                                         ↓
                                      onPause()
                                         ↓
                                      onStop()
                                         ↓
                                    onDestroy()

When Activity is restarted:
onStop() → onRestart() → onStart() → onResume()
```

### Complete Lifecycle Example

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
        Log.d("Lifecycle", "onCreate called")
    }

    override fun onStart() {
        super.onStart()
        Log.d("Lifecycle", "onStart called - Activity visible")
    }

    override fun onResume() {
        super.onResume()
        Log.d("Lifecycle", "onResume called - Activity interactive")
    }

    override fun onPause() {
        super.onPause()
        Log.d("Lifecycle", "onPause called - Losing focus")
    }

    override fun onStop() {
        super.onStop()
        Log.d("Lifecycle", "onStop called - No longer visible")
    }

    override fun onRestart() {
        super.onRestart()
        Log.d("Lifecycle", "onRestart called - Restarting")
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d("Lifecycle", "onDestroy called - Being destroyed")
    }
}
```

### Key Scenarios

1. **App Launch**: `onCreate()` → `onStart()` → `onResume()`
2. **User presses Home**: `onPause()` → `onStop()`
3. **Return to app**: `onRestart()` → `onStart()` → `onResume()`
4. **Back button**: `onPause()` → `onStop()` → `onDestroy()`
5. **Screen rotation**: Full destruction and recreation cycle

## Russian Answer

Методы жизненного цикла Activity представляют собой набор коллбэков, которые вызываются системой при изменении состояния Activity. Эти методы предоставляют возможность управлять поведением приложения при создании, остановке, восстановлении или уничтожении. Понимание и правильное использование этих методов критически важно для создания надежных и эффективных приложений.

### Основные методы жизненного цикла

1. **`onCreate(Bundle savedInstanceState)`** - вызывается при первом создании Activity для начальной настройки. Пример: `setContentView(R.layout.activity_main)` устанавливает разметку пользовательского интерфейса для Activity.

2. **`onStart()`** - вызывается, когда Activity становится видимым для пользователя после `onCreate()` или `onRestart()`.

3. **`onResume()`** - вызывается перед началом взаимодействия с пользователем, когда Activity находится на переднем плане. Это последний метод перед получением ввода данных от пользователя.

4. **`onPause()`** - вызывается, когда система собирается продолжить или возобновить другую Activity для остановки динамических элементов и освобождения ресурсов.

5. **`onStop()`** - вызывается, когда Activity больше не видимо пользователю для выполнения более "тяжеловесной" очистки ресурсов.

6. **`onRestart()`** - вызывается после остановки Activity для восстановления его состояния перед запуском.

7. **`onDestroy()`** - вызывается перед уничтожением Activity для освобождения всех ресурсов.

Жизненный цикл начинается с `onCreate()` и проходит через стадии `onStart()`, `onResume()`, `onPause()`, `onStop()`, `onDestroy()`. Если Activity останавливается и восстанавливается, вызывается `onRestart()`, за которым следуют `onStart()` и `onResume()`.
