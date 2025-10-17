---
id: "20251015082237291"
title: "What Navigation Methods Do You Know / Какие методы навигации вы знаете"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [languages, difficulty/medium]
---

# Question (EN)

> What navigation methods do you know?

# Вопрос (RU)

> Какие способы навигации вы знаете?

---

## Answer (EN)

Android offers multiple navigation methods for moving between screens and managing app flow. Each method serves specific use cases and architectural patterns.

### 1. Activity Navigation via Intent

Traditional approach for navigating between activities.

```kotlin
class MainActivity : AppCompatActivity() {

    // Basic navigation
    private fun navigateToDetails() {
        val intent = Intent(this, DetailsActivity::class.java)
        intent.putExtra("ITEM_ID", 42)
        startActivity(intent)
    }

    // Navigation with result
    private val detailsLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == RESULT_OK) {
            val data = result.data?.getStringExtra("RESULT")
            Toast.makeText(this, "Result: $data", Toast.LENGTH_SHORT).show()
        }
    }

    private fun navigateForResult() {
        val intent = Intent(this, DetailsActivity::class.java)
        detailsLauncher.launch(intent)
    }

    // With animations
    private fun navigateWithAnimation() {
        val intent = Intent(this, DetailsActivity::class.java)
        startActivity(intent)
        overridePendingTransition(R.anim.slide_in_right, R.anim.slide_out_left)
    }
}
```

### 2. Fragment-Based Navigation with FragmentManager

Manual fragment management for flexible UI composition.

```kotlin
class ContainerActivity : AppCompatActivity() {

    private fun showHomeFragment() {
        supportFragmentManager.beginTransaction()
            .replace(R.id.fragment_container, HomeFragment())
            .commit()
    }

    private fun navigateToDetails(itemId: Int) {
        val fragment = DetailsFragment.newInstance(itemId)

        supportFragmentManager.beginTransaction()
            .setCustomAnimations(
                R.anim.slide_in_right,
                R.anim.slide_out_left,
                R.anim.slide_in_left,
                R.anim.slide_out_right
            )
            .replace(R.id.fragment_container, fragment)
            .addToBackStack("details")
            .commit()
    }

    override fun onBackPressed() {
        if (supportFragmentManager.backStackEntryCount > 0) {
            supportFragmentManager.popBackStack()
        } else {
            super.onBackPressed()
        }
    }
}
```

### 3. Navigation Component (Jetpack)

Modern, graph-based navigation with type-safe arguments.

```xml
<!-- res/navigation/nav_graph.xml -->
<navigation xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/nav_graph"
    app:startDestination="@id/homeFragment">

    <fragment
        android:id="@+id/homeFragment"
        android:name="com.example.HomeFragment">
        <action
            android:id="@+id/action_home_to_details"
            app:destination="@id/detailsFragment" />
    </fragment>

    <fragment
        android:id="@+id/detailsFragment"
        android:name="com.example.DetailsFragment">
        <argument
            android:name="itemId"
            app:argType="integer" />
    </fragment>
</navigation>
```

```kotlin
// In Activity
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val navController = findNavController(R.id.nav_host_fragment)
        NavigationUI.setupActionBarWithNavController(this, navController)
    }

    override fun onSupportNavigateUp(): Boolean {
        return findNavController(R.id.nav_host_fragment).navigateUp()
    }
}

// In Fragment
class HomeFragment : Fragment() {
    private fun navigateToDetails(itemId: Int) {
        val action = HomeFragmentDirections.actionHomeToDetails(itemId)
        findNavController().navigate(action)
    }
}
```

### 4. Bottom Navigation

Tab-based navigation at the bottom of the screen.

```xml
<!-- activity_main.xml -->
<androidx.constraintlayout.widget.ConstraintLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <androidx.fragment.app.FragmentContainerView
        android:id="@+id/nav_host_fragment"
        android:name="androidx.navigation.fragment.NavHostFragment"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        app:layout_constraintBottom_toTopOf="@id/bottom_nav"
        app:layout_constraintTop_toTopOf="parent"
        app:navGraph="@navigation/nav_graph" />

    <com.google.android.material.bottomnavigation.BottomNavigationView
        android:id="@+id/bottom_nav"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        app:layout_constraintBottom_toBottomOf="parent"
        app:menu="@menu/bottom_nav_menu" />
</androidx.constraintlayout.widget.ConstraintLayout>
```

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val navController = findNavController(R.id.nav_host_fragment)
        val bottomNav = findViewById<BottomNavigationView>(R.id.bottom_nav)

        // Connect bottom nav with navigation component
        NavigationUI.setupWithNavController(bottomNav, navController)
    }
}
```

### 5. Tab Navigation (ViewPager)

Swipeable tabs for navigation.

```kotlin
class TabActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_tab)

        val viewPager = findViewById<ViewPager2>(R.id.viewPager)
        val tabLayout = findViewById<TabLayout>(R.id.tabLayout)

        // Setup ViewPager
        viewPager.adapter = ViewPagerAdapter(this)

        // Connect TabLayout with ViewPager
        TabLayoutMediator(tabLayout, viewPager) { tab, position ->
            tab.text = when (position) {
                0 -> "Home"
                1 -> "Search"
                2 -> "Profile"
                else -> null
            }
        }.attach()
    }
}

class ViewPagerAdapter(activity: AppCompatActivity) : FragmentStateAdapter(activity) {
    override fun getItemCount() = 3

    override fun createFragment(position: Int): Fragment {
        return when (position) {
            0 -> HomeFragment()
            1 -> SearchFragment()
            2 -> ProfileFragment()
            else -> HomeFragment()
        }
    }
}
```

### 6. Drawer Navigation

Side menu navigation.

```xml
<!-- activity_main.xml -->
<androidx.drawerlayout.widget.DrawerLayout
    android:id="@+id/drawer_layout"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <!-- Main content -->
    <androidx.fragment.app.FragmentContainerView
        android:id="@+id/nav_host_fragment"
        android:name="androidx.navigation.fragment.NavHostFragment"
        android:layout_width="match_parent"
        android:layout_height="match_parent"
        app:navGraph="@navigation/nav_graph" />

    <!-- Navigation drawer -->
    <com.google.android.material.navigation.NavigationView
        android:id="@+id/nav_view"
        android:layout_width="wrap_content"
        android:layout_height="match_parent"
        android:layout_gravity="start"
        app:menu="@menu/drawer_menu" />
</androidx.drawerlayout.widget.DrawerLayout>
```

```kotlin
class MainActivity : AppCompatActivity() {

    private lateinit var drawerLayout: DrawerLayout
    private lateinit var navController: NavController

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        drawerLayout = findViewById(R.id.drawer_layout)
        navController = findNavController(R.id.nav_host_fragment)

        val navigationView = findViewById<NavigationView>(R.id.nav_view)

        // Setup navigation with drawer
        NavigationUI.setupWithNavController(navigationView, navController)

        // Setup toolbar with drawer
        val toolbar = findViewById<Toolbar>(R.id.toolbar)
        setSupportActionBar(toolbar)

        val appBarConfiguration = AppBarConfiguration(
            setOf(R.id.homeFragment, R.id.settingsFragment),
            drawerLayout
        )
        NavigationUI.setupActionBarWithNavController(this, navController, appBarConfiguration)
    }

    override fun onSupportNavigateUp(): Boolean {
        return NavigationUI.navigateUp(navController, drawerLayout)
    }
}
```

### 7. Deep Links and App Links

URL-based navigation from external sources.

```xml
<!-- In navigation graph -->
<fragment
    android:id="@+id/detailsFragment"
    android:name="com.example.DetailsFragment">
    <deepLink
        android:id="@+id/deep_link"
        app:uri="myapp://details/{itemId}"
        android:autoVerify="true" />
</fragment>

<!-- In AndroidManifest.xml -->
<activity android:name=".MainActivity">
    <intent-filter>
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data
            android:scheme="myapp"
            android:host="details" />
    </intent-filter>
</activity>
```

```kotlin
// Handle deep link
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val navController = findNavController(R.id.nav_host_fragment)
        navController.handleDeepLink(intent)
    }

    override fun onNewIntent(intent: Intent?) {
        super.onNewIntent(intent)
        findNavController(R.id.nav_host_fragment).handleDeepLink(intent)
    }
}

// Create deep link programmatically
fun createDeepLink(itemId: Int): PendingIntent {
    return findNavController().createDeepLink()
        .setDestination(R.id.detailsFragment)
        .setArguments(bundleOf("itemId" to itemId))
        .createPendingIntent()
}
```

### 8. Navigation in Jetpack Compose

Declarative navigation using NavHost and NavController.

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = "home") {
        composable("home") {
            HomeScreen(
                onNavigateToDetails = { itemId ->
                    navController.navigate("details/$itemId")
                }
            )
        }

        composable(
            route = "details/{itemId}",
            arguments = listOf(navArgument("itemId") { type = NavType.IntType })
        ) { backStackEntry ->
            val itemId = backStackEntry.arguments?.getInt("itemId") ?: 0
            DetailsScreen(
                itemId = itemId,
                onBack = { navController.navigateUp() }
            )
        }

        composable("profile") {
            ProfileScreen()
        }
    }
}

@Composable
fun HomeScreen(onNavigateToDetails: (Int) -> Unit) {
    Column {
        Text("Home Screen")
        Button(onClick = { onNavigateToDetails(42) }) {
            Text("Go to Details")
        }
    }
}

@Composable
fun DetailsScreen(itemId: Int, onBack: () -> Unit) {
    Column {
        Text("Details Screen - Item $itemId")
        Button(onClick = onBack) {
            Text("Back")
        }
    }
}
```

### 9. Bottom Navigation in Compose

```kotlin
@Composable
fun MainScreen() {
    val navController = rememberNavController()

    Scaffold(
        bottomBar = {
            BottomNavigation {
                val navBackStackEntry by navController.currentBackStackEntryAsState()
                val currentRoute = navBackStackEntry?.destination?.route

                listOf(
                    Screen.Home,
                    Screen.Search,
                    Screen.Profile
                ).forEach { screen ->
                    BottomNavigationItem(
                        icon = { Icon(screen.icon, contentDescription = null) },
                        label = { Text(screen.label) },
                        selected = currentRoute == screen.route,
                        onClick = {
                            navController.navigate(screen.route) {
                                popUpTo(navController.graph.findStartDestination().id) {
                                    saveState = true
                                }
                                launchSingleTop = true
                                restoreState = true
                            }
                        }
                    )
                }
            }
        }
    ) { paddingValues ->
        NavHost(
            navController = navController,
            startDestination = Screen.Home.route,
            modifier = Modifier.padding(paddingValues)
        ) {
            composable(Screen.Home.route) { HomeScreen() }
            composable(Screen.Search.route) { SearchScreen() }
            composable(Screen.Profile.route) { ProfileScreen() }
        }
    }
}

sealed class Screen(val route: String, val label: String, val icon: ImageVector) {
    object Home : Screen("home", "Home", Icons.Default.Home)
    object Search : Screen("search", "Search", Icons.Default.Search)
    object Profile : Screen("profile", "Profile", Icons.Default.Person)
}
```

### Comparison Table

| Method               | Use Case                | Pros                    | Cons                   |
| -------------------- | ----------------------- | ----------------------- | ---------------------- |
| Activity Intent      | Simple app flows        | Easy, well-known        | Memory overhead        |
| FragmentManager      | Complex single-activity | Flexible, reusable      | Manual management      |
| Navigation Component | Modern apps             | Type-safe, visual graph | Learning curve         |
| Bottom Navigation    | 3-5 main sections       | Familiar UX             | Limited items          |
| Tab Navigation       | Related content         | Swipeable               | Limited to linear flow |
| Drawer Navigation    | Many sections           | Organized               | Hidden initially       |
| Deep Links           | External navigation     | Sharable URLs           | Configuration needed   |
| Compose Navigation   | Compose apps            | Declarative, type-safe  | Compose-only           |

### Best Practices

1. **Use Navigation Component** for new projects
2. **Single-Activity architecture** with fragments or Compose
3. **Type-safe arguments** with Safe Args plugin
4. **Handle deep links** for better UX
5. **Proper back stack management**
6. **Use appropriate navigation pattern** for your use case

---

# Какие способы навигации знаешь

## Ответ (RU)

Android предлагает множество способов навигации для перемещения между экранами и управления потоком приложения. Каждый метод подходит для определённых случаев использования и архитектурных паттернов.

### 1. Навигация между Activity через Intent

Традиционный подход для навигации между активностями.

```kotlin
class MainActivity : AppCompatActivity() {
    // Базовая навигация
    private fun navigateToDetails() {
        val intent = Intent(this, DetailsActivity::class.java)
        intent.putExtra("ITEM_ID", 42)
        startActivity(intent)
    }

    // Навигация с результатом
    private val detailsLauncher = registerForActivityResult(
        ActivityResultContracts.StartActivityForResult()
    ) { result ->
        if (result.resultCode == RESULT_OK) {
            val data = result.data?.getStringExtra("RESULT")
        }
    }
}
```

### 2. Navigation Component (Jetpack)

Современная навигация на основе графа с типобезопасными аргументами.

```kotlin
// В Activity
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val navController = findNavController(R.id.nav_host_fragment)
        NavigationUI.setupActionBarWithNavController(this, navController)
    }
}

// Во Fragment
class HomeFragment : Fragment() {
    private fun navigateToDetails(itemId: Int) {
        val action = HomeFragmentDirections.actionHomeToDetails(itemId)
        findNavController().navigate(action)
    }
}
```

### 3. Bottom Navigation

Навигация через вкладки внизу экрана.

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val navController = findNavController(R.id.nav_host_fragment)
        val bottomNav = findViewById<BottomNavigationView>(R.id.bottom_nav)
        NavigationUI.setupWithNavController(bottomNav, navController)
    }
}
```

### 4. Drawer Navigation

Боковое меню навигации.

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var drawerLayout: DrawerLayout

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        drawerLayout = findViewById(R.id.drawer_layout)
        val navController = findNavController(R.id.nav_host_fragment)
        val navigationView = findViewById<NavigationView>(R.id.nav_view)
        NavigationUI.setupWithNavController(navigationView, navController)
    }
}
```

### 5. Deep Links и App Links

Навигация на основе URL из внешних источников.

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        val navController = findNavController(R.id.nav_host_fragment)
        navController.handleDeepLink(intent)
    }
}
```

### 6. Navigation в Jetpack Compose

Декларативная навигация с использованием NavHost и NavController.

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = "home") {
        composable("home") {
            HomeScreen(
                onNavigateToDetails = { itemId ->
                    navController.navigate("details/$itemId")
                }
            )
        }

        composable("details/{itemId}") { backStackEntry ->
            val itemId = backStackEntry.arguments?.getInt("itemId") ?: 0
            DetailsScreen(itemId = itemId)
        }
    }
}
```

### Таблица сравнения

| Метод | Случай использования | Плюсы | Минусы |
|-------|---------------------|-------|--------|
| Activity Intent | Простые потоки | Просто, хорошо известно | Overhead памяти |
| FragmentManager | Сложные single-activity | Гибкий, переиспользуемый | Ручное управление |
| Navigation Component | Современные приложения | Типобезопасный, визуальный граф | Кривая обучения |
| Bottom Navigation | 3-5 основных разделов | Знакомый UX | Ограничено элементами |
| Drawer Navigation | Много разделов | Организован | Скрыт изначально |
| Deep Links | Внешняя навигация | Делимые URL | Требуется конфигурация |
| Compose Navigation | Compose приложения | Декларативный, типобезопасный | Только для Compose |

### Лучшие практики

1. **Используйте Navigation Component** для новых проектов
2. **Single-Activity архитектура** с фрагментами или Compose
3. **Типобезопасные аргументы** с плагином Safe Args
4. **Обрабатывайте deep links** для лучшего UX
5. **Правильное управление back stack**
6. **Используйте подходящий паттерн навигации** для вашего случая

---

## Related Questions

### Related (Medium)

-   [[q-compose-navigation-advanced--jetpack-compose--medium]] - Navigation
-   [[q-compose-navigation-advanced--android--medium]] - Navigation
-   [[q-activity-navigation-how-it-works--android--medium]] - Navigation
-   [[q-how-to-handle-the-situation-where-activity-can-open-multiple-times-due-to-deeplink--android--medium]] - Navigation
-   [[q-how-navigation-is-implemented-in-android--android--medium]] - Navigation
