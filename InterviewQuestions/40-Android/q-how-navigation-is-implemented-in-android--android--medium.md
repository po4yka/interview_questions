---
topic: android
tags:
  - android
  - android/navigation
  - android/ui
  - gestures
  - navigation
  - ui
difficulty: medium
status: reviewed
---

# Каким образом осуществляется навигация в Android?

**English**: How is navigation implemented in Android?

## Answer

Navigation in Android is implemented through several methods, both at the system level (user navigation between apps) and application level (in-app navigation). The approach depends on Android version and UI patterns.

### System-Level Navigation

#### 1. Gesture Navigation (Android 10+)

Modern navigation using swipe gestures:

```kotlin
// Handle gesture navigation in your app
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    // Make content edge-to-edge for gesture navigation
    WindowCompat.setDecorFitsSystemWindows(window, false)

    // Handle insets for gesture areas
    ViewCompat.setOnApplyWindowInsetsListener(binding.root) { view, insets ->
        val gestureInsets = insets.getInsets(WindowInsetsCompat.Type.systemGestures())
        view.updatePadding(
            left = gestureInsets.left,
            right = gestureInsets.right,
            bottom = gestureInsets.bottom
        )
        insets
    }
}

// Detect gesture navigation mode
fun isGestureNavigation(): Boolean {
    val resources = context.resources
    val resourceId = resources.getIdentifier(
        "config_navBarInteractionMode",
        "integer",
        "android"
    )
    return if (resourceId > 0) {
        resources.getInteger(resourceId) == 2
    } else {
        false
    }
}
```

#### 2. Button Navigation (Legacy)

Traditional three-button navigation:
- **Back button**: Navigate to previous screen
- **Home button**: Return to home screen
- **Recent apps**: View recent apps

```kotlin
// Handle back button
override fun onBackPressed() {
    if (fragmentManager.backStackEntryCount > 0) {
        fragmentManager.popBackStack()
    } else {
        super.onBackPressed()
    }
}

// Predictive back gesture (Android 13+)
@RequiresApi(Build.VERSION_CODES.TIRAMISU)
fun setupPredictiveBackGesture() {
    onBackPressedDispatcher.addCallback(this) {
        // Handle back with animation preview
        finish()
    }
}
```

### Application-Level Navigation

#### 1. Activity Navigation

```kotlin
// Start new activity
val intent = Intent(this, DetailActivity::class.java)
startActivity(intent)

// With animation
startActivity(intent)
overridePendingTransition(R.anim.slide_in_right, R.anim.slide_out_left)

// Finish current activity
finish()
```

#### 2. Fragment Navigation

```kotlin
// Replace fragment
supportFragmentManager.beginTransaction()
    .replace(R.id.container, DetailFragment())
    .addToBackStack(null)
    .commit()

// Navigate with Navigation Component
findNavController().navigate(R.id.action_home_to_detail)
```

#### 3. Task and Back Stack Management

```kotlin
// Create new task
val intent = Intent(this, MainActivity::class.java).apply {
    flags = Intent.FLAG_ACTIVITY_NEW_TASK or Intent.FLAG_ACTIVITY_CLEAR_TASK
}
startActivity(intent)

// Navigate up
override fun onSupportNavigateUp(): Boolean {
    return findNavController().navigateUp() || super.onSupportNavigateUp()
}

// Clear back stack
supportFragmentManager.popBackStack(null, FragmentManager.POP_BACK_STACK_INCLUSIVE)
```

### Navigation Patterns

#### Bottom Navigation

```xml
<com.google.android.material.bottomnavigation.BottomNavigationView
    android:id="@+id/bottom_nav"
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:menu="@menu/bottom_nav_menu" />
```

```kotlin
bottomNav.setOnItemSelectedListener { item ->
    when (item.itemId) {
        R.id.nav_home -> loadFragment(HomeFragment())
        R.id.nav_search -> loadFragment(SearchFragment())
        R.id.nav_profile -> loadFragment(ProfileFragment())
        else -> false
    }
}
```

#### Navigation Drawer

```kotlin
val drawerLayout: DrawerLayout = findViewById(R.id.drawer_layout)
val navView: NavigationView = findViewById(R.id.nav_view)

navView.setNavigationItemSelectedListener { menuItem ->
    when (menuItem.itemId) {
        R.id.nav_home -> navigateToHome()
        R.id.nav_settings -> navigateToSettings()
    }
    drawerLayout.closeDrawers()
    true
}
```

#### Tab Navigation

```kotlin
val tabLayout: TabLayout = findViewById(R.id.tab_layout)
val viewPager: ViewPager2 = findViewById(R.id.view_pager)

viewPager.adapter = ViewPagerAdapter(this)
TabLayoutMediator(tabLayout, viewPager) { tab, position ->
    tab.text = tabTitles[position]
}.attach()
```

### Handling System Navigation

#### Edge-to-Edge and Gesture Insets

```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    // Enable edge-to-edge
    WindowCompat.setDecorFitsSystemWindows(window, false)

    binding.root.setOnApplyWindowInsetsListener { view, windowInsets ->
        val insets = windowInsets.getInsets(
            WindowInsetsCompat.Type.systemBars() or
            WindowInsetsCompat.Type.displayCutout()
        )

        view.updatePadding(
            left = insets.left,
            top = insets.top,
            right = insets.right,
            bottom = insets.bottom
        )

        WindowInsetsCompat.CONSUMED
    }
}
```

#### Handling Different Navigation Modes

```kotlin
fun setupNavigationMode() {
    when (getNavigationMode()) {
        NavigationMode.GESTURE -> {
            // Adjust UI for gesture navigation
            binding.bottomContent.updatePadding(bottom = 0)
        }
        NavigationMode.BUTTON -> {
            // Adjust UI for button navigation
            binding.bottomContent.updatePadding(bottom = buttonNavBarHeight)
        }
        NavigationMode.THREE_BUTTON -> {
            // Adjust UI for three-button navigation
            binding.bottomContent.updatePadding(bottom = threeButtonNavBarHeight)
        }
    }
}

enum class NavigationMode {
    GESTURE, BUTTON, THREE_BUTTON
}
```

### Navigation Best Practices

1. **Respect system navigation**: Don't block back gestures
2. **Provide consistent navigation**: Follow platform conventions
3. **Handle configuration changes**: Preserve navigation state
4. **Support deep linking**: Allow direct navigation to screens
5. **Implement predictive back**: Show preview of previous screen (Android 13+)

```kotlin
// Predictive back example
@RequiresApi(Build.VERSION_CODES.TIRAMISU)
class MyActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        onBackPressedDispatcher.addCallback(
            this,
            object : OnBackPressedCallback(true) {
                override fun handleOnBackPressed() {
                    // Animate back gesture
                    finish()
                }

                override fun handleOnBackProgressed(backEvent: BackEventCompat) {
                    // Show progress of back gesture
                    val progress = backEvent.progress
                    binding.root.scaleX = 1 - (progress * 0.1f)
                    binding.root.scaleY = 1 - (progress * 0.1f)
                }

                override fun handleOnBackCancelled() {
                    // Restore view state
                    binding.root.animate().scaleX(1f).scaleY(1f).start()
                }
            }
        )
    }
}
```

## Ответ

Навигация в Android осуществляется несколькими способами, в зависимости от версии системы и используемых приложений. Основные методы включают жесты (свайпы, тапы), нажатия на экранные кнопки (на старых версиях), а также использование виртуальных или физических кнопок навигации (Домой, Назад, Последние приложения). Более современные версии Android полагаются преимущественно на жесты для навигации между приложениями и внутри них.

