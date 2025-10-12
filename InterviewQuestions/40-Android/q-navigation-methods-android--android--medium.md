---
topic: android
tags:
  - activity
  - android
  - android/navigation
  - architecture
  - compose
  - fragment
  - jetpack
  - navigation
  - navigation-component
  - ui-patterns
difficulty: medium
status: draft
---

# Какие способы навигации знаешь?

**English**: What navigation methods do you know?

## Answer (EN)
Android provides **several navigation methods** for moving between screens. The main methods include **Activity navigation**, **Fragment navigation**, **Navigation Component**, **Bottom/Tab Navigation**, **Drawer Navigation**, **Deep Links**, and **Jetpack Compose Navigation**.

## 1. Activity Navigation (Intent-based)

Navigate between Activities using **Intent**.

```kotlin
// Navigate to another Activity
val intent = Intent(this, SecondActivity::class.java)
startActivity(intent)

// With data
val intent = Intent(this, DetailActivity::class.java)
intent.putExtra("USER_ID", userId)
intent.putExtra("USER_NAME", userName)
startActivity(intent)

// With result (modern way)
private val launcher = registerForActivityResult(
    ActivityResultContracts.StartActivityForResult()
) { result ->
    if (result.resultCode == RESULT_OK) {
        val data = result.data?.getStringExtra("RESULT")
        // Handle result
    }
}

fun launchActivity() {
    val intent = Intent(this, SecondActivity::class.java)
    launcher.launch(intent)
}
```

**Use cases:**
- - Different app sections (Login → Main → Settings)
- - External app integration
- - Not recommended for in-app navigation (use Fragments instead)

---

## 2. Fragment Navigation (FragmentManager)

Navigate between Fragments using **FragmentManager**.

```kotlin
// Replace fragment
supportFragmentManager.beginTransaction()
    .replace(R.id.container, SecondFragment())
    .addToBackStack(null)  // Add to back stack
    .commit()

// Add fragment on top
supportFragmentManager.beginTransaction()
    .add(R.id.container, OverlayFragment())
    .addToBackStack("overlay")
    .commit()

// Remove fragment
supportFragmentManager.beginTransaction()
    .remove(fragment)
    .commit()

// Pop back stack
supportFragmentManager.popBackStack()

// Find fragment
val fragment = supportFragmentManager.findFragmentById(R.id.container)
val fragmentByTag = supportFragmentManager.findFragmentByTag("MyFragment")
```

**Fragment transactions with animations:**

```kotlin
supportFragmentManager.beginTransaction()
    .setCustomAnimations(
        R.anim.slide_in_right,  // enter
        R.anim.slide_out_left,  // exit
        R.anim.slide_in_left,   // popEnter
        R.anim.slide_out_right  // popExit
    )
    .replace(R.id.container, SecondFragment())
    .addToBackStack(null)
    .commit()
```

**Use cases:**
- - In-app navigation within single Activity
- - Master-detail layouts
- - Tab content switching

---

## 3. Navigation Component (Jetpack)

Modern **declarative navigation** using a navigation graph.

**Setup:**

```kotlin
// build.gradle
dependencies {
    implementation "androidx.navigation:navigation-fragment-ktx:2.7.0"
    implementation "androidx.navigation:navigation-ui-ktx:2.7.0"
}
```

**Navigation Graph (res/navigation/nav_graph.xml):**

```xml
<navigation xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:id="@+id/nav_graph"
    app:startDestination="@id/homeFragment">

    <fragment
        android:id="@+id/homeFragment"
        android:name="com.example.HomeFragment">
        <action
            android:id="@+id/action_home_to_detail"
            app:destination="@id/detailFragment" />
    </fragment>

    <fragment
        android:id="@+id/detailFragment"
        android:name="com.example.DetailFragment">
        <argument
            android:name="itemId"
            app:argType="integer" />
    </fragment>
</navigation>
```

**Usage:**

```kotlin
// Navigate
findNavController().navigate(R.id.action_home_to_detail)

// With arguments
val bundle = bundleOf("itemId" to itemId)
findNavController().navigate(R.id.action_home_to_detail, bundle)

// Navigate back
findNavController().navigateUp()
findNavController().popBackStack()

// Get arguments
class DetailFragment : Fragment() {
    private val args: DetailFragmentArgs by navArgs()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        val itemId = args.itemId
    }
}
```

**Benefits:**
- - Visual navigation graph
- - Type-safe arguments (with Safe Args plugin)
- - Automatic back stack management
- - Deep link support
- - Transition animations

---

## 4. Bottom Navigation / Tab Navigation

Navigate between top-level destinations using **BottomNavigationView** or **TabLayout**.

### Bottom Navigation

```kotlin
// Setup
val navController = findNavController(R.id.nav_host_fragment)
bottomNavigationView.setupWithNavController(navController)

// Or manual setup
bottomNavigationView.setOnItemSelectedListener { item ->
    when (item.itemId) {
        R.id.nav_home -> {
            navController.navigate(R.id.homeFragment)
            true
        }
        R.id.nav_search -> {
            navController.navigate(R.id.searchFragment)
            true
        }
        R.id.nav_profile -> {
            navController.navigate(R.id.profileFragment)
            true
        }
        else -> false
    }
}
```

**menu/bottom_nav_menu.xml:**

```xml
<menu xmlns:android="http://schemas.android.com/apk/res/android">
    <item
        android:id="@+id/nav_home"
        android:icon="@drawable/ic_home"
        android:title="Home" />
    <item
        android:id="@+id/nav_search"
        android:icon="@drawable/ic_search"
        android:title="Search" />
    <item
        android:id="@+id/nav_profile"
        android:icon="@drawable/ic_profile"
        android:title="Profile" />
</menu>
```

### Tab Navigation

```kotlin
// With ViewPager2
class PagerAdapter(fragment: Fragment) : FragmentStateAdapter(fragment) {
    override fun getItemCount() = 3

    override fun createFragment(position: Int): Fragment {
        return when (position) {
            0 -> FirstTabFragment()
            1 -> SecondTabFragment()
            2 -> ThirdTabFragment()
            else -> FirstTabFragment()
        }
    }
}

// Setup
val adapter = PagerAdapter(this)
viewPager.adapter = adapter

TabLayoutMediator(tabLayout, viewPager) { tab, position ->
    tab.text = when (position) {
        0 -> "Tab 1"
        1 -> "Tab 2"
        2 -> "Tab 3"
        else -> null
    }
}.attach()
```

**Use cases:**
- - Top-level app sections
- - Tab-based content
- - Quick access navigation

---

## 5. Drawer Navigation (Navigation Drawer)

Side menu navigation using **DrawerLayout**.

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var drawerLayout: DrawerLayout
    private lateinit var navController: NavController

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        drawerLayout = findViewById(R.id.drawer_layout)
        val navView: NavigationView = findViewById(R.id.nav_view)
        navController = findNavController(R.id.nav_host_fragment)

        // Setup with Navigation Component
        navView.setupWithNavController(navController)

        // Setup ActionBar with drawer
        val appBarConfiguration = AppBarConfiguration(
            setOf(R.id.homeFragment, R.id.settingsFragment),
            drawerLayout
        )
        setupActionBarWithNavController(navController, appBarConfiguration)
    }

    // Open drawer programmatically
    fun openDrawer() {
        drawerLayout.openDrawer(GravityCompat.START)
    }

    // Close drawer
    fun closeDrawer() {
        drawerLayout.closeDrawer(GravityCompat.START)
    }

    override fun onSupportNavigateUp(): Boolean {
        return navController.navigateUp(drawerLayout) || super.onSupportNavigateUp()
    }
}
```

**layout/activity_main.xml:**

```xml
<androidx.drawerlayout.widget.DrawerLayout
    android:id="@+id/drawer_layout"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <!-- Main content -->
    <androidx.fragment.app.FragmentContainerView
        android:id="@+id/nav_host_fragment"
        android:layout_width="match_parent"
        android:layout_height="match_parent" />

    <!-- Navigation drawer -->
    <com.google.android.material.navigation.NavigationView
        android:id="@+id/nav_view"
        android:layout_width="wrap_content"
        android:layout_height="match_parent"
        android:layout_gravity="start"
        app:menu="@menu/drawer_menu" />
</androidx.drawerlayout.widget.DrawerLayout>
```

**Use cases:**
- - Many navigation destinations
- - Secondary features
- - Settings, about, help

---

## 6. Deep Links and App Links

Navigate using **URIs** (internal and external).

### Deep Links

```xml
<fragment
    android:id="@+id/detailFragment"
    android:name="com.example.DetailFragment">
    <argument
        android:name="itemId"
        app:argType="integer" />
    <deepLink
        app:uri="myapp://item/{itemId}" />
</fragment>
```

**Navigate via URI:**

```kotlin
val uri = Uri.parse("myapp://item/$itemId")
findNavController().navigate(uri)
```

### App Links (verified HTTPS links)

**AndroidManifest.xml:**

```xml
<activity android:name=".MainActivity">
    <intent-filter android:autoVerify="true">
        <action android:name="android.intent.action.VIEW" />
        <category android:name="android.intent.category.DEFAULT" />
        <category android:name="android.intent.category.BROWSABLE" />
        <data
            android:scheme="https"
            android:host="www.example.com"
            android:pathPrefix="/item" />
    </intent-filter>
</activity>
```

**Handle in Activity:**

```kotlin
override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)

    // Handle incoming URI
    intent?.data?.let { uri ->
        val itemId = uri.lastPathSegment
        // Navigate to detail
    }
}
```

**Use cases:**
- - External navigation (from web, emails, notifications)
- - Shareable content
- - Marketing campaigns

---

## 7. Jetpack Compose Navigation

Navigate in **Compose** using **NavHost** and **NavController**.

```kotlin
@Composable
fun AppNavigation() {
    val navController = rememberNavController()

    NavHost(navController = navController, startDestination = "home") {
        composable("home") {
            HomeScreen(
                onNavigateToDetail = { itemId ->
                    navController.navigate("detail/$itemId")
                }
            )
        }

        composable(
            route = "detail/{itemId}",
            arguments = listOf(navArgument("itemId") { type = NavType.IntType })
        ) { backStackEntry ->
            val itemId = backStackEntry.arguments?.getInt("itemId")
            DetailScreen(
                itemId = itemId,
                onNavigateBack = { navController.navigateUp() }
            )
        }

        composable("settings") {
            SettingsScreen()
        }
    }
}

@Composable
fun HomeScreen(onNavigateToDetail: (Int) -> Unit) {
    Column {
        Button(onClick = { onNavigateToDetail(123) }) {
            Text("Go to Detail")
        }
    }
}

@Composable
fun DetailScreen(itemId: Int?, onNavigateBack: () -> Unit) {
    Column {
        Text("Detail for item: $itemId")
        Button(onClick = onNavigateBack) {
            Text("Back")
        }
    }
}
```

**Bottom Navigation in Compose:**

```kotlin
@Composable
fun MainScreen() {
    val navController = rememberNavController()

    Scaffold(
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    icon = { Icon(Icons.Filled.Home, contentDescription = null) },
                    label = { Text("Home") },
                    selected = false,
                    onClick = { navController.navigate("home") }
                )
                NavigationBarItem(
                    icon = { Icon(Icons.Filled.Search, contentDescription = null) },
                    label = { Text("Search") },
                    selected = false,
                    onClick = { navController.navigate("search") }
                )
            }
        }
    ) { paddingValues ->
        NavHost(
            navController = navController,
            startDestination = "home",
            modifier = Modifier.padding(paddingValues)
        ) {
            composable("home") { HomeScreen() }
            composable("search") { SearchScreen() }
        }
    }
}
```

---

## Comparison Table

| Method | Use Case | Complexity | Modern? |
|--------|----------|------------|---------|
| **Activity (Intent)** | App sections, external | Low | - Legacy |
| **Fragment (FragmentManager)** | In-app navigation | Medium | WARNING: Manual |
| **Navigation Component** | Fragment navigation | Medium | - Recommended |
| **Bottom Navigation** | Top-level tabs | Low | - Common |
| **Tab Navigation** | Swipeable sections | Low | - Common |
| **Drawer Navigation** | Many destinations | Medium | - Common |
| **Deep Links** | External/shareable | High | - Modern |
| **Compose Navigation** | Compose UI | Medium | - Modern |

---

## Summary

**7 main navigation methods in Android:**

1. **Activity Navigation** - Intent-based, for app sections
2. **Fragment Navigation** - FragmentManager, in-app navigation
3. **Navigation Component** - Declarative, type-safe, visual graph ⭐
4. **Bottom/Tab Navigation** - Quick access to top-level destinations
5. **Drawer Navigation** - Side menu for many destinations
6. **Deep Links/App Links** - URI-based, external navigation
7. **Jetpack Compose Navigation** - Compose UI navigation

**Recommended approach:**
- **Single Activity + Navigation Component** for modern apps
- **Compose Navigation** for Compose-based apps
- **Fragments over Activities** for in-app navigation

## Ответ (RU)
В Android есть несколько способов навигации между экранами. Основные методы включают: 1) Activity-навигация с использованием Intent. 2) Fragment-навигация через FragmentManager. 3) Navigation Component (Jetpack). 4) Bottom Navigation / Tab Navigation с использованием BottomNavigationView или TabLayout. 5) Drawer Navigation (Navigation Drawer) через DrawerLayout. 6) Deep Links и App Links для навигации через ссылки. 7) Navigation в Jetpack Compose с использованием NavHost и NavController.

