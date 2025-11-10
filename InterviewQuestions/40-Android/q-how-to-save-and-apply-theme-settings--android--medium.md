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

        // ✅ Установить глобальный режим; AppCompat сам переразметит/пересоздаст активити при необходимости
        AppCompatDelegate.setDefaultNightMode(mode)
    }
}
```

**2. DataStore + `Flow` (Реактивный подход)**

Используйте DataStore для реактивного обновления сохранённого режима:

```kotlin
// Рекомендуется определить DataStore как top-level extension
val Context.themeDataStore: DataStore<Preferences> by preferencesDataStore(name = "theme")

class ThemeRepository(private val context: Context) {

    val themeMode: Flow<Int> = context.themeDataStore.data
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
        themeRepo = ThemeRepository(this)
        // ⚠️ Нельзя использовать lifecycleScope в Application (нет LifecycleOwner).
        // Обычно режим читают синхронно из кеша или применяют при старте Activity,
        // подписываясь в её scope.
    }
}
```

Пример применения в `Activity`:

```kotlin
class MainActivity : AppCompatActivity() {

    private val themeRepo by lazy {
        (application as App).themeRepo
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        // ✅ Сначала применяем сохранённый режим (например, последнее значение или FOLLOW_SYSTEM), затем вызываем super
        lifecycleScope.launch {
            themeRepo.themeMode.firstOrNull()?.let { mode ->
                AppCompatDelegate.setDefaultNightMode(mode)
            }
        }
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

(На практике нужно аккуратно выбирать момент чтения, чтобы не было заметного "мигания" темы; для medium-уровня достаточно понимать, что `AppCompatDelegate.setDefaultNightMode` должен вызываться до отрисовки.)

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
    private val themeRepo by lazy { ThemeRepository(this) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            // Предполагается, что ThemeRepository возвращает уже не Int, а доменную модель ThemeMode
            val themeMode by themeRepo.themeMode
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
- Глобально: `Application.onCreate()` → `AppCompatDelegate.setDefaultNightMode()` с DayNight-темой (`Theme.MaterialComponents.DayNight.*` или эквивалентной Material3-темой).
- Локально: `Activity.onCreate()` → `setTheme()` **до** `setContentView()`.

**Режимы темы (AppCompatDelegate):**
- `MODE_NIGHT_NO` — всегда светлая.
- `MODE_NIGHT_YES` — всегда тёмная.
- `MODE_NIGHT_FOLLOW_SYSTEM` — следовать системному режиму.
- `MODE_NIGHT_UNSPECIFIED` — поведение по умолчанию (делегирует системе/AppCompat).

**Обновление темы:**
- При `AppCompatDelegate.setDefaultNightMode(...)` фреймворк сам инициирует пересоздание соответствующих `Activity` (явный `recreate()` обычно не нужен).
- При локальном `setTheme()` для смены темы текущей `Activity`, как правило, требуется вручную вызвать `recreate()`.

**Compose vs Views:**
- Compose: реактивно через `State`/`Flow`/`LiveData`, меняя параметры `MaterialTheme`.
- Views: императивно через `AppCompatDelegate` или `setTheme()` и пересоздание `Activity`.

## Answer (EN)

Saving and applying theme settings requires coordinating user preference storage with applying the theme **before UI rendering**. The key point: the theme (especially DayNight mode) should be applied before `setContentView()` for traditional Views or via `AppCompatDelegate` globally for automatic switching.

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

        // ✅ Set global mode; AppCompat will handle recreating activities as needed
        AppCompatDelegate.setDefaultNightMode(mode)
    }
}
```

**2. DataStore + `Flow` (Reactive)**

Use DataStore for reactive updates of the saved mode:

```kotlin
// Recommended: define DataStore as a top-level extension
val Context.themeDataStore: DataStore<Preferences> by preferencesDataStore(name = "theme")

class ThemeRepository(private val context: Context) {

    val themeMode: Flow<Int> = context.themeDataStore.data
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
        themeRepo = ThemeRepository(this)
        // ⚠️ Do NOT use lifecycleScope in Application (it is not a LifecycleOwner).
        // Typically you either read a cached value synchronously or apply the mode
        // from an Activity, subscribing there.
    }
}
```

Example usage in an `Activity`:

```kotlin
class MainActivity : AppCompatActivity() {

    private val themeRepo by lazy {
        (application as App).themeRepo
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        // ✅ Apply saved mode (e.g., last value or FOLLOW_SYSTEM) before drawing content
        lifecycleScope.launch {
            themeRepo.themeMode.firstOrNull()?.let { mode ->
                AppCompatDelegate.setDefaultNightMode(mode)
            }
        }
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)
    }
}
```

(Practically, you must choose the read/apply point carefully to avoid visible theme flicker; at medium level it's enough to understand `AppCompatDelegate.setDefaultNightMode` should be called before rendering.)

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
    private val themeRepo by lazy { ThemeRepository(this) }

    override fun onCreate() {
        super.onCreate()
        setContent {
            // Assume ThemeRepository ultimately exposes ThemeMode or we map Int -> ThemeMode here
            val themeMode by themeRepo.themeMode
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

**Theme `Application` for Views:**
- Global: `Application.onCreate()` → `AppCompatDelegate.setDefaultNightMode()` with a DayNight-capable theme (`Theme.MaterialComponents.DayNight.*` or Material3 equivalent).
- Local: `Activity.onCreate()` → `setTheme()` **before** `setContentView()`.

**Theme Modes (AppCompatDelegate):**
- `MODE_NIGHT_NO` — always light.
- `MODE_NIGHT_YES` — always dark.
- `MODE_NIGHT_FOLLOW_SYSTEM` — follow system setting.
- `MODE_NIGHT_UNSPECIFIED` — default behavior (delegates to system/AppCompat).

**Theme Updates:**
- Calling `AppCompatDelegate.setDefaultNightMode(...)` will cause configuration changes / recreation for affected Activities; an explicit `recreate()` is usually not required.
- When changing only a local `setTheme()` for the current `Activity`, you typically need to call `recreate()` to re-inflate views with the new theme.

**Compose vs Views:**
- Compose: reactive via `State`/`Flow`/`LiveData`, by changing `MaterialTheme` parameters.
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