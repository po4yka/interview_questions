---
id: 20251012-1227196
title: "How To Save And Apply Theme Settings / How To Save и Apply Theme Settings"
topic: android
difficulty: medium
status: draft
moc: moc-android
related: [q-how-to-save-scroll-state-when-activity-is-recreated--android--medium, q-server-sent-events-sse--networking--medium, q-kmm-sqldelight--multiplatform--medium]
created: 2025-10-15
tags: [themes, dark-mode, sharedpreferences, datastore, ui, difficulty/medium]
---
# How to save and apply theme settings?

**Russian**: Как сохранять и применять настройки темы?

## Answer (EN)
Saving and applying theme settings in Android involves storing user preferences and applying them before the UI is rendered. The key is to apply the theme **before** `setContentView()` is called.

### 1. Basic Theme Switching with SharedPreferences

```kotlin
class MainActivity : AppCompatActivity() {

    companion object {
        private const val PREFS_NAME = "theme_prefs"
        private const val KEY_THEME = "selected_theme"

        const val THEME_LIGHT = "light"
        const val THEME_DARK = "dark"
        const val THEME_SYSTEM = "system"
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        // Apply theme BEFORE setContentView
        applyTheme()

        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        setupThemeSelector()
    }

    private fun applyTheme() {
        val prefs = getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
        val theme = prefs.getString(KEY_THEME, THEME_SYSTEM) ?: THEME_SYSTEM

        when (theme) {
            THEME_LIGHT -> setTheme(R.style.Theme_App_Light)
            THEME_DARK -> setTheme(R.style.Theme_App_Dark)
            THEME_SYSTEM -> {
                // Use system theme - handled by DayNight theme
                setTheme(R.style.Theme_App)
            }
        }
    }

    private fun saveTheme(theme: String) {
        getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .edit()
            .putString(KEY_THEME, theme)
            .apply()
    }

    private fun setupThemeSelector() {
        findViewById<Button>(R.id.btnLight).setOnClickListener {
            saveTheme(THEME_LIGHT)
            recreate() // Restart activity to apply theme
        }

        findViewById<Button>(R.id.btnDark).setOnClickListener {
            saveTheme(THEME_DARK)
            recreate()
        }

        findViewById<Button>(R.id.btnSystem).setOnClickListener {
            saveTheme(THEME_SYSTEM)
            recreate()
        }
    }
}
```

### 2. Using AppCompatDelegate for DayNight Theme

```kotlin
class ThemeManager(private val context: Context) {

    companion object {
        private const val PREFS_NAME = "theme_prefs"
        private const val KEY_NIGHT_MODE = "night_mode"
    }

    private val prefs = context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)

    fun applyTheme() {
        val nightMode = prefs.getInt(
            KEY_NIGHT_MODE,
            AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM
        )
        AppCompatDelegate.setDefaultNightMode(nightMode)
    }

    fun setTheme(mode: Int) {
        prefs.edit().putInt(KEY_NIGHT_MODE, mode).apply()
        AppCompatDelegate.setDefaultNightMode(mode)
    }

    fun getCurrentMode(): Int {
        return prefs.getInt(KEY_NIGHT_MODE, AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM)
    }
}

// In Application class
class MyApplication : Application() {

    lateinit var themeManager: ThemeManager

    override fun onCreate() {
        super.onCreate()

        themeManager = ThemeManager(this)
        themeManager.applyTheme()
    }
}

// In Activity
class MainActivity : AppCompatActivity() {

    private val themeManager by lazy {
        (application as MyApplication).themeManager
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        setupThemeButtons()
    }

    private fun setupThemeButtons() {
        findViewById<Button>(R.id.btnLightMode).setOnClickListener {
            themeManager.setTheme(AppCompatDelegate.MODE_NIGHT_NO)
        }

        findViewById<Button>(R.id.btnDarkMode).setOnClickListener {
            themeManager.setTheme(AppCompatDelegate.MODE_NIGHT_YES)
        }

        findViewById<Button>(R.id.btnSystemMode).setOnClickListener {
            themeManager.setTheme(AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM)
        }
    }
}
```

### 3. Theme Definitions (styles.xml)

```xml
<!-- res/values/themes.xml -->
<resources>
    <!-- Base theme -->
    <style name="Theme.App" parent="Theme.MaterialComponents.DayNight.DarkActionBar">
        <item name="colorPrimary">@color/purple_500</item>
        <item name="colorPrimaryVariant">@color/purple_700</item>
        <item name="colorOnPrimary">@color/white</item>
        <item name="colorSecondary">@color/teal_200</item>
        <item name="android:statusBarColor">?attr/colorPrimaryVariant</item>
    </style>

    <!-- Light theme -->
    <style name="Theme.App.Light" parent="Theme.MaterialComponents.Light.DarkActionBar">
        <item name="colorPrimary">@color/purple_500</item>
        <item name="colorPrimaryVariant">@color/purple_700</item>
        <item name="android:windowBackground">@color/white</item>
        <item name="android:textColorPrimary">@color/black</item>
    </style>

    <!-- Dark theme -->
    <style name="Theme.App.Dark" parent="Theme.MaterialComponents.NoActionBar">
        <item name="colorPrimary">@color/purple_200</item>
        <item name="colorPrimaryVariant">@color/purple_700</item>
        <item name="android:windowBackground">@color/dark_background</item>
        <item name="android:textColorPrimary">@color/white</item>
    </style>
</resources>
```

### 4. DataStore Implementation (Modern Approach)

```kotlin
// Add dependency: implementation "androidx.datastore:datastore-preferences:1.0.0"

class ThemePreferences(context: Context) {

    private val dataStore = context.createDataStore(name = "theme_settings")

    companion object {
        val THEME_KEY = intPreferencesKey("theme_mode")
    }

    val themeMode: Flow<Int> = dataStore.data
        .map { preferences ->
            preferences[THEME_KEY] ?: AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM
        }

    suspend fun setThemeMode(mode: Int) {
        dataStore.edit { preferences ->
            preferences[THEME_KEY] = mode
        }
    }
}

// In Application
class MyApplication : Application() {

    lateinit var themePreferences: ThemePreferences

    override fun onCreate() {
        super.onCreate()

        themePreferences = ThemePreferences(this)

        lifecycleScope.launch {
            themePreferences.themeMode.collect { mode ->
                AppCompatDelegate.setDefaultNightMode(mode)
            }
        }
    }
}

// In Activity
class MainActivity : AppCompatActivity() {

    private val themePrefs by lazy {
        (application as MyApplication).themePreferences
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        lifecycleScope.launch {
            themePrefs.themeMode.collect { mode ->
                // Update UI based on current theme
                updateThemeButtons(mode)
            }
        }

        setupThemeButtons()
    }

    private fun setupThemeButtons() {
        findViewById<Button>(R.id.btnLight).setOnClickListener {
            lifecycleScope.launch {
                themePrefs.setThemeMode(AppCompatDelegate.MODE_NIGHT_NO)
            }
        }

        findViewById<Button>(R.id.btnDark).setOnClickListener {
            lifecycleScope.launch {
                themePrefs.setThemeMode(AppCompatDelegate.MODE_NIGHT_YES)
            }
        }

        findViewById<Button>(R.id.btnSystem).setOnClickListener {
            lifecycleScope.launch {
                themePrefs.setThemeMode(AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM)
            }
        }
    }

    private fun updateThemeButtons(mode: Int) {
        // Update UI to show which theme is selected
        // ... implementation
    }
}
```

### 5. Jetpack Compose Theme Switching

```kotlin
// Theme preference repository
class ThemeRepository(context: Context) {

    private val dataStore = context.dataStore

    companion object {
        private val THEME_KEY = booleanPreferencesKey("is_dark_theme")
        private val Context.dataStore by preferencesDataStore("theme_settings")
    }

    val isDarkTheme: Flow<Boolean> = dataStore.data
        .map { preferences ->
            preferences[THEME_KEY] ?: isSystemInDarkTheme()
        }

    suspend fun setDarkTheme(isDark: Boolean) {
        dataStore.edit { preferences ->
            preferences[THEME_KEY] = isDark
        }
    }
}

// Theme composable
@Composable
fun AppTheme(
    themeRepository: ThemeRepository,
    content: @Composable () -> Unit
) {
    val isDarkTheme by themeRepository.isDarkTheme.collectAsState(initial = false)

    MaterialTheme(
        colors = if (isDarkTheme) DarkColorScheme else LightColorScheme,
        content = content
    )
}

// Color schemes
private val LightColorScheme = lightColorScheme(
    primary = Purple500,
    secondary = Teal200,
    background = Color.White
)

private val DarkColorScheme = darkColorScheme(
    primary = Purple200,
    secondary = Teal200,
    background = Color(0xFF121212)
)

// Usage in Activity
class MainActivity : ComponentActivity() {

    private val themeRepository by lazy { ThemeRepository(this) }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            AppTheme(themeRepository = themeRepository) {
                MainScreen(
                    onThemeToggle = { isDark ->
                        lifecycleScope.launch {
                            themeRepository.setDarkTheme(isDark)
                        }
                    }
                )
            }
        }
    }
}

@Composable
fun MainScreen(onThemeToggle: (Boolean) -> Unit) {
    val isSystemInDarkTheme = isSystemInDarkTheme()
    var isDarkTheme by remember { mutableStateOf(isSystemInDarkTheme) }

    Column {
        Text("Theme Settings")

        Switch(
            checked = isDarkTheme,
            onCheckedChange = { isDark ->
                isDarkTheme = isDark
                onThemeToggle(isDark)
            }
        )
    }
}
```

### 6. Advanced Theme Manager

```kotlin
sealed class ThemeMode {
    object Light : ThemeMode()
    object Dark : ThemeMode()
    object System : ThemeMode()

    fun toNightMode(): Int = when (this) {
        Light -> AppCompatDelegate.MODE_NIGHT_NO
        Dark -> AppCompatDelegate.MODE_NIGHT_YES
        System -> AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM
    }
}

class AdvancedThemeManager(context: Context) {

    private val prefs = context.getSharedPreferences("theme_prefs", Context.MODE_PRIVATE)

    fun getCurrentTheme(): ThemeMode {
        return when (prefs.getString("theme", "system")) {
            "light" -> ThemeMode.Light
            "dark" -> ThemeMode.Dark
            else -> ThemeMode.System
        }
    }

    fun setTheme(theme: ThemeMode) {
        val themeString = when (theme) {
            ThemeMode.Light -> "light"
            ThemeMode.Dark -> "dark"
            ThemeMode.System -> "system"
        }

        prefs.edit().putString("theme", themeString).apply()
        AppCompatDelegate.setDefaultNightMode(theme.toNightMode())
    }

    fun applyTheme() {
        AppCompatDelegate.setDefaultNightMode(getCurrentTheme().toNightMode())
    }
}
```

### 7. Theme Persistence Across App Restart

```kotlin
// In Application class
class MyApp : Application() {

    override fun onCreate() {
        super.onCreate()

        // Apply saved theme before any Activity is created
        val prefs = getSharedPreferences("theme_prefs", Context.MODE_PRIVATE)
        val nightMode = prefs.getInt(
            "night_mode",
            AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM
        )

        AppCompatDelegate.setDefaultNightMode(nightMode)
    }
}

// Don't forget to register in AndroidManifest.xml
<application
    android:name=".MyApp"
    ...>
```

### 8. Dynamic Theme Colors (Material 3)

```kotlin
@Composable
fun DynamicThemeApp() {
    val context = LocalContext.current
    val isDarkTheme = isSystemInDarkTheme()

    val dynamicColors = if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.S) {
        if (isDarkTheme) dynamicDarkColorScheme(context)
        else dynamicLightColorScheme(context)
    } else {
        if (isDarkTheme) DarkColorScheme else LightColorScheme
    }

    MaterialTheme(
        colorScheme = dynamicColors,
        content = { /* Your content */ }
    )
}
```

### Best Practices

1. **Apply theme in Application class** for app-wide consistency
2. **Save theme before setContentView()** in Activities
3. **Use AppCompatDelegate** for DayNight themes
4. **Use DataStore** instead of SharedPreferences for new projects
5. **Handle system theme changes** gracefully
6. **Provide smooth transitions** when changing themes
7. **Test both light and dark themes** thoroughly

### Common Patterns

```kotlin
// Theme selection dialog
class ThemeDialog : DialogFragment() {

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return inflater.inflate(R.layout.dialog_theme, container, false).apply {
            findViewById<RadioButton>(R.id.rbLight).setOnClickListener {
                setTheme(AppCompatDelegate.MODE_NIGHT_NO)
            }
            findViewById<RadioButton>(R.id.rbDark).setOnClickListener {
                setTheme(AppCompatDelegate.MODE_NIGHT_YES)
            }
            findViewById<RadioButton>(R.id.rbSystem).setOnClickListener {
                setTheme(AppCompatDelegate.MODE_NIGHT_FOLLOW_SYSTEM)
            }
        }
    }

    private fun setTheme(mode: Int) {
        AppCompatDelegate.setDefaultNightMode(mode)
        // Save to preferences
        dismiss()
    }
}
```

---

# Как сохранять и применять настройки темы

## Ответ (RU)
Хранить выбранную тему в SharedPreferences. При старте приложения или Activity применять тему до setContentView. В случае использования DayNight можно использовать AppCompatDelegate.setDefaultNightMode.

## Related Questions

- [[q-how-to-save-scroll-state-when-activity-is-recreated--android--medium]]
- [[q-server-sent-events-sse--networking--medium]]
- [[q-kmm-sqldelight--android--medium]]
