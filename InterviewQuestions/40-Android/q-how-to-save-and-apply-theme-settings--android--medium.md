---
id: android-231
title: "How to Save and Apply Theme Settings / Как сохранять и применять настройки темы"
aliases: ["How to Save and Apply Theme Settings", "Theme Settings", "Как сохранять и применять настройки темы", "Настройки темы"]
topic: android
subtopics: [datastore, ui-compose, ui-theming, ui-views]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-jetpack-compose, c-lifecycle, q-dark-theme-android--android--medium, q-datastore-preferences-proto--android--medium, q-how-to-save-activity-state--android--medium]
created: 2025-10-15
updated: 2025-10-30
tags: [android/datastore, android/ui-compose, android/ui-theming, android/ui-views, dark-mode, difficulty/medium, sharedpreferences, themes]
sources: []
---

# Вопрос (RU)

> Как сохранять и применять настройки темы в Android-приложении?

# Question (EN)

> How to save and apply theme settings in an Android application?

---

## Ответ (RU)

Сохранение и применение темы требует координации между хранением пользовательских предпочтений и их применением **до отрисовки UI**. Ключевой момент: тема должна применяться до `setContentView()` для традиционных Views или через `AppCompatDelegate` глобально для автоматического переключения.

### Основные Подходы

**1. SharedPreferences + AppCompatDelegate (Views)**

Применять через `Application.onCreate()` для глобального эффекта:

```kotlin
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        // ✅ Применить тему до создания Activity
        val prefs = getSharedPreferences("theme", MODE_PRIVATE)
        val mode = prefs.getInt("night_mode", MODE_NIGHT_FOLLOW_SYSTEM)
        AppCompatDelegate.setDefaultNightMode(mode)
    }
}

class SettingsActivity : AppCompatActivity() {
    private fun saveTheme(mode: Int) {
        getSharedPreferences("theme", MODE_PRIVATE)
            .edit()
            .putInt("night_mode", mode)
            .apply()

        // ✅ Применить без recreate() через AppCompatDelegate
        AppCompatDelegate.setDefaultNightMode(mode)
    }
}
```

**2. DataStore + `Flow` (Reactive)**

Использовать для реактивного обновления:

```kotlin
class ThemeRepository(context: Context) {
    private val dataStore = context.dataStore

    val themeMode: Flow<Int> = dataStore.data
        .map { it[THEME_KEY] ?: MODE_NIGHT_FOLLOW_SYSTEM }

    suspend fun setTheme(mode: Int) {
        dataStore.edit { it[THEME_KEY] = mode }
    }

    companion object {
        private val THEME_KEY = intPreferencesKey("theme_mode")
        private val Context.dataStore by preferencesDataStore("theme")
    }
}

class App : Application() {
    val themeRepo by lazy { ThemeRepository(this) }

    override fun onCreate() {
        super.onCreate()
        // ✅ Подписаться на изменения темы
        lifecycleScope.launch {
            themeRepo.themeMode.collect { mode ->
                AppCompatDelegate.setDefaultNightMode(mode)
            }
        }
    }
}
```

**3. Jetpack Compose**

```kotlin
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
    private val themeRepo by lazy { ThemeRepository(this) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            val themeMode by themeRepo.themeMode.collectAsState(ThemeMode.SYSTEM)
            AppTheme(themeMode = themeMode) {
                MainScreen()
            }
        }
    }
}
```

### Важные Детали

**Применение темы для Views:**
- Глобально: `Application.onCreate()` → `AppCompatDelegate.setDefaultNightMode()`
- Локально: `Activity.onCreate()` → `setTheme()` **до** `setContentView()`

**Режимы темы:**
- `MODE_NIGHT_NO` — светлая
- `MODE_NIGHT_YES` — тёмная
- `MODE_NIGHT_FOLLOW_SYSTEM` — следовать системе

**Обновление темы:**
- ❌ **НЕ** использовать `recreate()` при AppCompatDelegate — тема применится автоматически
- ✅ При локальном `setTheme()` требуется `recreate()`

**Compose vs Views:**
- Compose: реактивно через `State` и `Flow`
- Views: императивно через `AppCompatDelegate` или `setTheme()`

## Answer (EN)

Saving and applying themes requires coordination between storing user preferences and applying them **before UI rendering**. Key insight: themes must be applied before `setContentView()` for traditional Views or via `AppCompatDelegate` globally for automatic switching.

### Core Approaches

**1. SharedPreferences + AppCompatDelegate (Views)**

Apply through `Application.onCreate()` for global effect:

```kotlin
class App : Application() {
    override fun onCreate() {
        super.onCreate()
        // ✅ Apply theme before Activity creation
        val prefs = getSharedPreferences("theme", MODE_PRIVATE)
        val mode = prefs.getInt("night_mode", MODE_NIGHT_FOLLOW_SYSTEM)
        AppCompatDelegate.setDefaultNightMode(mode)
    }
}

class SettingsActivity : AppCompatActivity() {
    private fun saveTheme(mode: Int) {
        getSharedPreferences("theme", MODE_PRIVATE)
            .edit()
            .putInt("night_mode", mode)
            .apply()

        // ✅ Apply without recreate() via AppCompatDelegate
        AppCompatDelegate.setDefaultNightMode(mode)
    }
}
```

**2. DataStore + `Flow` (Reactive)**

Use for reactive updates:

```kotlin
class ThemeRepository(context: Context) {
    private val dataStore = context.dataStore

    val themeMode: Flow<Int> = dataStore.data
        .map { it[THEME_KEY] ?: MODE_NIGHT_FOLLOW_SYSTEM }

    suspend fun setTheme(mode: Int) {
        dataStore.edit { it[THEME_KEY] = mode }
    }

    companion object {
        private val THEME_KEY = intPreferencesKey("theme_mode")
        private val Context.dataStore by preferencesDataStore("theme")
    }
}

class App : Application() {
    val themeRepo by lazy { ThemeRepository(this) }

    override fun onCreate() {
        super.onCreate()
        // ✅ Subscribe to theme changes
        lifecycleScope.launch {
            themeRepo.themeMode.collect { mode ->
                AppCompatDelegate.setDefaultNightMode(mode)
            }
        }
    }
}
```

**3. Jetpack Compose**

```kotlin
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
    private val themeRepo by lazy { ThemeRepository(this) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            val themeMode by themeRepo.themeMode.collectAsState(ThemeMode.SYSTEM)
            AppTheme(themeMode = themeMode) {
                MainScreen()
            }
        }
    }
}
```

### Key Details

**Theme `Application` for Views:**
- Global: `Application.onCreate()` → `AppCompatDelegate.setDefaultNightMode()`
- Local: `Activity.onCreate()` → `setTheme()` **before** `setContentView()`

**Theme Modes:**
- `MODE_NIGHT_NO` — light theme
- `MODE_NIGHT_YES` — dark theme
- `MODE_NIGHT_FOLLOW_SYSTEM` — follow system

**Theme Updates:**
- ❌ **DON'T** use `recreate()` with AppCompatDelegate — theme applies automatically
- ✅ With local `setTheme()` requires `recreate()`

**Compose vs Views:**
- Compose: reactive via `State` and `Flow`
- Views: imperative via `AppCompatDelegate` or `setTheme()`

---

## Follow-ups

- What happens if `setTheme()` is called after `setContentView()`?
- How to handle dynamic theme changes without restarting `Activity`?
- What's the difference between `Theme.MaterialComponents.DayNight` and custom theme inheritance?
- How to implement multiple theme variants (not just light/dark)?
- How to test theme persistence across app restarts?

## References

- [[c-jetpack-compose]]
- [[c-lifecycle]]
- [[c-activity]]
- [Material Design 3 theming](https://m3.material.io/styles/color/dynamic-color/overview)
- [AppCompatDelegate documentation](https://developer.android.com/reference/androidx/appcompat/app/AppCompatDelegate)

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
