---
id: android-231
title: "How to Save and Apply Theme Settings / Как сохранять и применять настройки темы"
aliases: ["How to Save and Apply Theme Settings", "Theme Settings", "Как сохранять и применять настройки темы", "Настройки темы"]
topic: android
subtopics: [datastore, ui-compose, ui-theming]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-jetpack-compose, c-lifecycle, q-dark-theme-android--android--medium, q-datastore-preferences-proto--android--medium, q-how-to-save-activity-state--android--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [android/datastore, android/ui-compose, android/ui-theming, android/ui-views, dark-mode, difficulty/medium, sharedpreferences, themes]
sources: []

---

# Вопрос (RU)

> Как сохранять и применять настройки темы в Android-приложении?

# Question (EN)

> How to save and apply theme settings in an Android application?

---

## Ответ (RU)

Сохранение и применение темы требует координации между хранением пользовательских предпочтений и их применением **до отрисовки UI**. Ключевой момент: тема (особенно режим ночи DayNight) должна применяться до `setContentView()` для традиционных Views или через `AppCompatDelegate` глобально для автоматического переключения.

### Основные Подходы

**1. SharedPreferences + AppCompatDelegate (Views)**

Применять через `Application.onCreate()` для глобального эффекта:

```kotlin
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        // ✅ Применить режим ночи до создания Activity
        val prefs = getSharedPreferences("theme", MODE_PRIVATE)
        val mode = prefs.getInt("night_mode", AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM)
        AppCompatDelegate.setDefaultNightMode(mode)
    }
}

class SettingsActivity : AppCompatActivity() {
    private fun saveTheme(mode: Int) {
        getSharedPreferences("theme", MODE_PRIVATE)
            .edit()
            .putInt("night_mode", mode)
            .apply()

        // ✅ Установить глобальный режим; AppCompat сам инициирует пересоздание Activity при необходимости
        AppCompatDelegate.setDefaultNightMode(mode)
    }
}
```

**2. DataStore + `Flow` (Реактивный подход)**

Используйте DataStore для реактивного обновления сохранённого режима. Важно: чтение и применение значения для первоначальной темы нужно сделать до отрисовки UI (например, в `Application` или в стартовой `Activity` до `setContentView()`), иначе возможен заметный "мигающий" переход.

```kotlin
// Рекомендуется определить DataStore как top-level extension на Context
val Context.themeDataStore: DataStore<Preferences> by preferencesDataStore(name = "theme")

class ThemeRepository(private val context: Context) {

    val themeModeFlow: Flow<Int> = context.themeDataStore.data
        .map { prefs ->
            prefs[THEME_KEY] ?: AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM
        }

    suspend fun setTheme(mode: Int) {
        context.themeDataStore.edit { prefs ->
            prefs[THEME_KEY] = mode
        }
    }

    private companion object {
        val THEME_KEY = intPreferencesKey("theme_mode")
    }
}

class App : Application() {
    lateinit var themeRepo: ThemeRepository
        private set

    override fun onCreate() {
        super.onCreate()
        themeRepo = ThemeRepository(applicationContext)
        // ⚠️ Нельзя использовать lifecycleScope в Application (нет LifecycleOwner).
        // Для старта: можно прочитать сохранённый режим блокирующе до первой Activity
        // (например, в Splash/Launcher Activity до setContentView), применив
        // AppCompatDelegate.setDefaultNightMode(savedMode).
    }
}
```

Пример упрощённого применения в стартовой `Activity` (идея, без блокировки основного потока в продакшене):

```kotlin
class MainActivity : AppCompatActivity() {

    private val themeRepo by lazy { (application as App).themeRepo }

    override fun onCreate(savedInstanceState: Bundle?) {
        // ✅ Перед super.onCreate() считываем сохранённый режим синхронно (например, из кеша/последнего значения)
        // и применяем глобально. В реальном приложении это можно сделать в Splash Activity.
        val savedMode = runBlocking {
            themeRepo.themeModeFlow.first()
        }
        AppCompatDelegate.setDefaultNightMode(savedMode)

        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

(На практике нужно избегать длительного `runBlocking` на главном потоке и использовать либо Splash/launch screen, либо предварительный кеш; для medium-уровня достаточно понимать, что `AppCompatDelegate.setDefaultNightMode` должен быть вызван до отрисовки.)

**3. Jetpack Compose**

```kotlin
enum class ThemeMode {
    LIGHT, DARK, SYSTEM
}

@Composable
fun AppTheme(
    themeMode: ThemeMode,
    content: @Composable () -> Unit
) {
    val isDark = when (themeMode) {
        ThemeMode.DARK -> true
        ThemeMode.LIGHT -> false
        ThemeMode.SYSTEM -> isSystemInDarkTheme()
    }

    MaterialTheme(
        colorScheme = if (isDark) darkColorScheme() else lightColorScheme(),
        content = content
    )
}

class MainActivity : ComponentActivity() {
    // ✅ Используем Application context / DI вместо создания репозитория на Activity context
    private val themeRepo by lazy { (application as App).themeRepo }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            // ThemeRepository предоставляет Flow<Int> с режимами AppCompat; здесь мапим в доменную модель ThemeMode
            val themeMode by themeRepo.themeModeFlow
                .map { modeInt ->
                    when (modeInt) {
                        AppCompatDelegate.MODE_NIGHT_YES -> ThemeMode.DARK
                        AppCompatDelegate.MODE_NIGHT_NO -> ThemeMode.LIGHT
                        else -> ThemeMode.SYSTEM
                    }
                }
                .collectAsState(initial = ThemeMode.SYSTEM)

            AppTheme(themeMode = themeMode) {
                MainScreen()
            }
        }
    }
}
```

### Важные Детали

**Применение темы для Views:**
- Глобально: `Application.onCreate()` → `AppCompatDelegate.setDefaultNightMode()` с DayNight-темой (`Theme.MaterialComponents.DayNight.*` или эквивалентной Material3-темой, поддерживающей ночной режим).
- Локально: `Activity.onCreate()` → `setTheme()` **до** `setContentView()`.

**Режимы темы (AppCompatDelegate):**
- `MODE_NIGHT_NO` — всегда светлая.
- `MODE_NIGHT_YES` — всегда тёмная.
- `MODE_NIGHT_FOLLOW_SYSTEM` — следовать системному режиму.
- `MODE_NIGHT_UNSPECIFIED` — поведение по умолчанию (делегирует системе/AppCompat).

**Обновление темы:**
- При `AppCompatDelegate.setDefaultNightMode(...)` фреймворк инициирует пересоздание затронутых `Activity` (явный `recreate()` обычно не нужен).
- При локальном `setTheme()` для смены темы текущей `Activity`, как правило, требуется вручную вызвать `recreate()`.

**Compose vs Views:**
- Compose: реактивно через `State`/`Flow`/`LiveData`, меняя параметры `MaterialTheme` (при этом DayNight режим системы можно учитывать через `isSystemInDarkTheme()`).
- Views: императивно через `AppCompatDelegate` или `setTheme()` и пересоздание `Activity`.

## Answer (EN)

Saving and applying theme settings requires coordinating user preference storage with applying the theme **before UI rendering**. The key point: the theme (especially DayNight mode) should be applied before `setContentView()` for classic Views or via `AppCompatDelegate` globally for automatic switching.

### Core Approaches

**1. SharedPreferences + AppCompatDelegate (Views)**

Apply through `Application.onCreate()` for a global effect:

```kotlin
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        // ✅ Apply night mode before any Activity is created
        val prefs = getSharedPreferences("theme", MODE_PRIVATE)
        val mode = prefs.getInt("night_mode", AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM)
        AppCompatDelegate.setDefaultNightMode(mode)
    }
}

class SettingsActivity : AppCompatActivity() {
    private fun saveTheme(mode: Int) {
        getSharedPreferences("theme", MODE_PRIVATE)
            .edit()
            .putInt("night_mode", mode)
            .apply()

        // ✅ Set global mode; AppCompat will trigger Activity recreation when needed
        AppCompatDelegate.setDefaultNightMode(mode)
    }
}
```

**2. DataStore + `Flow` (Reactive)**

Use DataStore for reactive updates of the saved mode. Important: for the initial theme, read and apply the stored value before drawing UI (e.g., in `Application` or in the launcher Activity before `setContentView()`), otherwise a visible "flicker" may occur.

```kotlin
// Recommended: define DataStore as a top-level extension on Context
val Context.themeDataStore: DataStore<Preferences> by preferencesDataStore(name = "theme")

class ThemeRepository(private val context: Context) {

    val themeModeFlow: Flow<Int> = context.themeDataStore.data
        .map { prefs ->
            prefs[THEME_KEY] ?: AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM
        }

    suspend fun setTheme(mode: Int) {
        context.themeDataStore.edit { prefs ->
            prefs[THEME_KEY] = mode
        }
    }

    private companion object {
        val THEME_KEY = intPreferencesKey("theme_mode")
    }
}

class App : Application() {
    lateinit var themeRepo: ThemeRepository
        private set

    override fun onCreate() {
        super.onCreate()
        themeRepo = ThemeRepository(applicationContext)
        // ⚠️ Do NOT use lifecycleScope in Application (it is not a LifecycleOwner).
        // For startup: read the saved mode before the first Activity draws UI
        // (e.g., in a splash/launcher Activity before setContentView) and apply
        // AppCompatDelegate.setDefaultNightMode(savedMode).
    }
}
```

Simplified example in a launcher `Activity` (conceptual; avoid blocking the main thread in real apps):

```kotlin
class MainActivity : AppCompatActivity() {

    private val themeRepo by lazy { (application as App).themeRepo }

    override fun onCreate(savedInstanceState: Bundle?) {
        // ✅ Before super.onCreate(), synchronously read the saved mode (e.g., from cache/last value)
        // and apply it globally. In real apps, this is typically done in a dedicated splash Activity.
        val savedMode = runBlocking {
            themeRepo.themeModeFlow.first()
        }
        AppCompatDelegate.setDefaultNightMode(savedMode)

        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

(Practically, you should avoid long `runBlocking` on the main thread and instead use a splash/launch screen or cached value. For medium level, it's enough to understand `AppCompatDelegate.setDefaultNightMode` must be called before rendering.)

**3. Jetpack Compose**

```kotlin
enum class ThemeMode {
    LIGHT, DARK, SYSTEM
}

@Composable
fun AppTheme(
    themeMode: ThemeMode,
    content: @Composable () -> Unit
) {
    val isDark = when (themeMode) {
        ThemeMode.DARK -> true
        ThemeMode.LIGHT -> false
        ThemeMode.SYSTEM -> isSystemInDarkTheme()
    }

    MaterialTheme(
        colorScheme = if (isDark) darkColorScheme() else lightColorScheme(),
        content = content
    )
}

class MainActivity : ComponentActivity() {
    // ✅ Use Application context / DI instead of constructing repository with Activity context
    private val themeRepo by lazy { (application as App).themeRepo }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            // ThemeRepository exposes Flow<Int> with AppCompat modes; map Int -> ThemeMode here
            val themeMode by themeRepo.themeModeFlow
                .map { modeInt ->
                    when (modeInt) {
                        AppCompatDelegate.MODE_NIGHT_YES -> ThemeMode.DARK
                        AppCompatDelegate.MODE_NIGHT_NO -> ThemeMode.LIGHT
                        else -> ThemeMode.SYSTEM
                    }
                }
                .collectAsState(initial = ThemeMode.SYSTEM)

            AppTheme(themeMode = themeMode) {
                MainScreen()
            }
        }
    }
}
```

### Key Details

**Theme application for Views:**
- Global: `Application.onCreate()` → `AppCompatDelegate.setDefaultNightMode()` with a DayNight-capable theme (`Theme.MaterialComponents.DayNight.*` or a Material3 theme supporting dark mode).
- Local: `Activity.onCreate()` → `setTheme()` **before** `setContentView()`.

**Theme Modes (AppCompatDelegate):**
- `MODE_NIGHT_NO` — always light.
- `MODE_NIGHT_YES` — always dark.
- `MODE_NIGHT_FOLLOW_SYSTEM` — follow system setting.
- `MODE_NIGHT_UNSPECIFIED` — default behavior (delegates to system/AppCompat).

**Theme Updates:**
- Calling `AppCompatDelegate.setDefaultNightMode(...)` triggers configuration changes / recreation for affected Activities; explicit `recreate()` is usually not required.
- When changing only a local `setTheme()` for the current `Activity`, you typically need to call `recreate()` to re-inflate views with the new theme.

**Compose vs Views:**
- Compose: reactive via `State`/`Flow`/`LiveData`, by changing `MaterialTheme` parameters (and using `isSystemInDarkTheme()` to respect system dark mode).
- Views: imperative via `AppCompatDelegate` or `setTheme()` plus `Activity` recreation.

---

## Дополнительные вопросы (RU)

- Что произойдет, если вызвать `setTheme()` после `setContentView()`?
- Как обрабатывать динамическую смену темы без перезапуска `Activity`?
- В чем разница между `Theme.MaterialComponents.DayNight` и наследованием от кастомной темы?
- Как реализовать несколько вариантов темы (не только светлая/темная)?
- Как протестировать сохранение темы при перезапуске приложения?

## Follow-ups

- What happens if `setTheme()` is called after `setContentView()`?
- How to handle dynamic theme changes without restarting `Activity`?
- What's the difference between `Theme.MaterialComponents.DayNight` and custom theme inheritance?
- How to implement multiple theme variants (not just light/dark)?
- How to test theme persistence across app restarts?

## Ссылки (RU)

- [[c-jetpack-compose]]
- [[c-lifecycle]]
- [[c-activity]]
- [Material Design 3 темизация](https://m3.material.io/styles/color/dynamic-color/overview)
- [Документация AppCompatDelegate](https://developer.android.com/reference/androidx/appcompat/app/AppCompatDelegate)

## References

- [[c-jetpack-compose]]
- [[c-lifecycle]]
- [[c-activity]]
- [Material Design 3 theming](https://m3.material.io/styles/color/dynamic-color/overview)
- [AppCompatDelegate documentation](https://developer.android.com/reference/androidx/appcompat/app/AppCompatDelegate)

## Связанные вопросы (RU)

### Предпосылки (проще)
- [[q-sharedpreferences-definition--android--easy]]
- [[q-what-is-activity-and-what-is-it-used-for--android--medium]]

### Связанные (того же уровня)
- [[q-datastore-preferences-proto--android--medium]]
- [[q-dark-theme-android--android--medium]]
- [[q-how-to-save-activity-state--android--medium]]
- [[q-jetpack-compose-basics--android--medium]]

### Продвинутые (сложнее)
- [[q-multi-module-best-practices--android--hard]]

## Related Questions

### Prerequisites (Easier)
- [[q-sharedpreferences-definition--android--easy]]
- [[q-what-is-activity-and-what-is-it-used-for--android--medium]]

### Related (Same Level)
- [[q-datastore-preferences-proto--android--medium]]
- [[q-dark-theme-android--android--medium]]
- [[q-how-to-save-activity-state--android--medium]]
- [[q-jetpack-compose-basics--android--medium]]

### Advanced (Harder)
- [[q-multi-module-best-practices--android--hard]]
