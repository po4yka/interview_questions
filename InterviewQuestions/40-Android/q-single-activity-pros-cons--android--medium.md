---
id: 20251012-122711105
title: "Single Activity Pros Cons / Преимущества и недостатки Single Activity"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: [android, android/activity, android/fragment, android/performance-startup, fragment, fragments, performance, performance-startup, platform/android, single-activity, difficulty/medium]
---
# Какие у подхода Single Activity этого подхода + и - ?

**English**: What are the pros and cons of the Single Activity approach?

## Answer (EN)
The **Single Activity approach** means using **one main Activity** for the entire application, with all screens represented as **Fragments**. This contrasts with the traditional multi-Activity approach where each screen is a separate Activity.

### Architecture Comparison

**Traditional Multi-Activity:**
```
App
 MainActivity (Home screen)
 ProfileActivity (Profile screen)
 SettingsActivity (Settings screen)
 DetailActivity (Detail screen)
```

**Single Activity:**
```
App
 MainActivity
     HomeFragment
     ProfileFragment
     SettingsFragment
     DetailFragment
```

### Implementation Example

```kotlin
// Single Activity setup
class MainActivity : AppCompatActivity() {

    private lateinit var navController: NavController

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Setup Navigation Component
        val navHostFragment = supportFragmentManager
            .findFragmentById(R.id.nav_host_fragment) as NavHostFragment
        navController = navHostFragment.navController

        // All navigation happens via fragments
        setupBottomNavigation()
    }

    private fun setupBottomNavigation() {
        val bottomNav = findViewById<BottomNavigationView>(R.id.bottom_nav)
        bottomNav.setupWithNavController(navController)
    }
}
```

**Navigation Graph (nav_graph.xml):**
```xml
<navigation>
    <fragment
        android:id="@+id/homeFragment"
        android:name="com.example.HomeFragment">
        <action
            android:id="@+id/action_home_to_profile"
            app:destination="@id/profileFragment" />
    </fragment>

    <fragment
        android:id="@+id/profileFragment"
        android:name="com.example.ProfileFragment" />

    <fragment
        android:id="@+id/settingsFragment"
        android:name="com.example.SettingsFragment" />
</navigation>
```

---

## Advantages (Pros)

### 1. Simplified Navigation

**Single Activity:**
```kotlin
// Simple fragment navigation
navController.navigate(R.id.action_home_to_profile)

// With arguments
val bundle = bundleOf("userId" to userId)
navController.navigate(R.id.profileFragment, bundle)
```

**Multi-Activity (more complex):**
```kotlin
// Need to create Intent, pass extras, handle result
val intent = Intent(this, ProfileActivity::class.java)
intent.putExtra("userId", userId)
startActivityForResult(intent, REQUEST_CODE)

override fun onActivityResult(requestCode: Int, resultCode: Int, data: Intent?) {
    // Handle result
}
```

### 2. Shared ViewModel Across Screens

```kotlin
// ViewModel shared across fragments in same activity
class SharedViewModel : ViewModel() {
    val userData = MutableLiveData<User>()
}

// Fragment A
class FragmentA : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    fun updateUser(user: User) {
        sharedViewModel.userData.value = user
    }
}

// Fragment B (automatically gets the same ViewModel instance)
class FragmentB : Fragment() {
    private val sharedViewModel: SharedViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        sharedViewModel.userData.observe(viewLifecycleOwner) { user ->
            // Receives updates from Fragment A
        }
    }
}
```

**With multi-Activity, you'd need:**
- Static singletons (memory leaks)
- Persistent storage (slower)
- Passing data through Intents (limited size)

### 3. Shared UI Elements

```kotlin
// Persistent toolbar, bottom nav across all screens
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Toolbar stays visible during all fragment transitions
        setSupportActionBar(findViewById(R.id.toolbar))

        // Bottom navigation stays visible
        val bottomNav = findViewById<BottomNavigationView>(R.id.bottom_nav)
        bottomNav.setupWithNavController(navController)
    }
}
```

All fragments share the same toolbar and bottom navigation - no recreation needed.

### 4. Better Animations

```kotlin
// Smooth shared element transitions between fragments
val extras = FragmentNavigatorExtras(
    imageView to "image_transition"
)
navController.navigate(
    R.id.detailFragment,
    bundle,
    null,
    extras
)

// Fragment transition animations
navController.navigate(
    R.id.profileFragment,
    null,
    NavOptions.Builder()
        .setEnterAnim(R.anim.slide_in_right)
        .setExitAnim(R.anim.slide_out_left)
        .setPopEnterAnim(R.anim.slide_in_left)
        .setPopExitAnim(R.anim.slide_out_right)
        .build()
)
```

### 5. Faster Screen Transitions

No Activity recreation overhead:
- No new Activity lifecycle
- No new Window creation
- No theme reapplication
- Just fragment transaction (much faster)

### 6. Easier Deep Linking

```kotlin
// Navigation Component handles deep links automatically
<navigation>
    <fragment
        android:id="@+id/productDetailFragment"
        android:name="com.example.ProductDetailFragment">
        <deepLink
            app:uri="myapp://product/{productId}" />
    </fragment>
</navigation>

// Deep link automatically navigates to correct fragment
// No need to determine which Activity to launch
```

### 7. Simplified State Management

```kotlin
// Single SavedStateHandle for entire app
class AppViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {

    // State persists across configuration changes
    val currentScreen: LiveData<String> = savedStateHandle.getLiveData("current_screen")

    fun navigateTo(screen: String) {
        savedStateHandle["current_screen"] = screen
    }
}
```

---

## Disadvantages (Cons)

### 1. Fragment Complexity

Fragments have more complex lifecycle than Activities:

```kotlin
// Fragment lifecycle callbacks (more than Activity)
override fun onAttach(context: Context)
override fun onCreate(savedInstanceState: Bundle?)
override fun onCreateView(inflater: LayoutInflater, container: ViewGroup?, savedInstanceState: Bundle?): View?
override fun onViewCreated(view: View, savedInstanceState: Bundle?)
override fun onStart()
override fun onResume()
override fun onPause()
override fun onStop()
override fun onDestroyView()  // Fragment-specific
override fun onDestroy()
override fun onDetach()  // Fragment-specific
```

Must understand two lifecycles:
- Fragment lifecycle
- View lifecycle (viewLifecycleOwner)

### 2. Memory Leaks with ViewBinding

```kotlin
// Common mistake - memory leak!
class MyFragment : Fragment() {
    private val binding: FragmentMyBinding? = null  // Wrong!

    override fun onCreateView(...): View {
        binding = FragmentMyBinding.inflate(inflater, container, false)
        return binding.root
    }

    // View is destroyed, but binding still references it = LEAK
}

// Correct approach
class MyFragment : Fragment() {
    private var _binding: FragmentMyBinding? = null
    private val binding get() = _binding!!

    override fun onCreateView(...): View {
        _binding = FragmentMyBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onDestroyView() {
        super.onDestroyView()
        _binding = null  // Must clean up!
    }
}
```

### 3. FragmentManager Complexity

```kotlin
// Complex fragment transactions
supportFragmentManager.beginTransaction()
    .setReorderingAllowed(true)
    .replace(R.id.container, FragmentA())
    .addToBackStack("A")
    .commit()

supportFragmentManager.beginTransaction()
    .setReorderingAllowed(true)
    .add(R.id.container, FragmentB())
    .addToBackStack("B")
    .commit()

// Back stack management can get complex
supportFragmentManager.popBackStack("A", FragmentManager.POP_BACK_STACK_INCLUSIVE)
```

### 4. State Loss Issues

```kotlin
// IllegalStateException: Can not perform this action after onSaveInstanceState
supportFragmentManager.beginTransaction()
    .replace(R.id.container, MyFragment())
    .commit()  // Can crash if called after onSaveInstanceState

// Must use commitAllowingStateLoss() or lifecycle-aware approach
lifecycleScope.launch {
    whenResumed {
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, MyFragment())
            .commit()
    }
}
```

### 5. Nested Fragment Complexity

```kotlin
// Fragments within fragments can get confusing
class ParentFragment : Fragment() {
    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // childFragmentManager vs parentFragmentManager
        childFragmentManager.beginTransaction()
            .replace(R.id.child_container, ChildFragment())
            .commit()
    }
}

class ChildFragment : Fragment() {
    fun navigateUp() {
        // Which FragmentManager? Child or parent?
        parentFragmentManager.popBackStack()  // Or requireActivity().supportFragmentManager?
    }
}
```

### 6. Testing Complexity

```kotlin
// Testing fragments requires more setup than Activities
@Test
fun testFragment() {
    // Need to create scenario with Activity
    val scenario = launchFragmentInContainer<MyFragment>(
        themeResId = R.style.AppTheme
    )

    scenario.onFragment { fragment ->
        // Test fragment
    }

    // vs Activity test (simpler)
    val activityScenario = launch<MyActivity>()
}
```

### 7. Back Button Handling

```kotlin
// Must intercept back button manually
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        onBackPressedDispatcher.addCallback(this) {
            val fragment = supportFragmentManager.findFragmentById(R.id.nav_host_fragment)

            if (fragment is OnBackPressedHandler && fragment.onBackPressed()) {
                // Fragment handled it
                return@addCallback
            }

            // Default behavior
            if (!navController.popBackStack()) {
                finish()
            }
        }
    }
}
```

---

## Comparison Table

| Aspect | Single Activity | Multi-Activity |
|--------|----------------|----------------|
| **Navigation** | Fragment transactions (fast) | Activity intents (slower) |
| **Data sharing** | Shared ViewModel (easy) | Intent extras / static (complex) |
| **Transitions** | Smooth, customizable | Activity transitions (limited) |
| **Memory** | Lower (one Activity) | Higher (multiple Activities) |
| **State management** | Simpler (one state) | Complex (multiple states) |
| **Deep links** | Navigation Component (easy) | Manual routing (complex) |
| **Learning curve** | Fragment lifecycle (steep) | Activity lifecycle (simpler) |
| **Memory leaks** | ViewBinding cleanup needed | Less prone |
| **Back stack** | Fragment back stack (complex) | Activity back stack (simpler) |
| **Testing** | More setup required | Simpler |

---

## When to Use Single Activity

**Good fit for:**
- Apps with shared UI elements (toolbar, bottom nav)
- Apps needing smooth transitions
- Apps with complex navigation flows
- Modern apps using Jetpack Navigation
- Apps needing shared state across screens

**Example: Social media app**
```kotlin
// All screens share bottom navigation
MainActivity
 FeedFragment (bottom nav: Home)
 SearchFragment (bottom nav: Search)
 NotificationsFragment (bottom nav: Notifications)
 ProfileFragment (bottom nav: Profile)
 DetailFragments (no bottom nav, but same Activity)
```

**Not ideal for:**
- Simple apps with few screens
- Apps with completely independent flows
- Legacy codebases (migration cost)
- Teams unfamiliar with Fragments

---

## Modern Recommendation: Jetpack Compose

Jetpack Compose further simplifies Single Activity:

```kotlin
class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setContent {
            val navController = rememberNavController()

            MyAppTheme {
                NavHost(navController, startDestination = "home") {
                    composable("home") { HomeScreen(navController) }
                    composable("profile/{userId}") { backStackEntry ->
                        val userId = backStackEntry.arguments?.getString("userId")
                        ProfileScreen(userId)
                    }
                    composable("settings") { SettingsScreen() }
                }
            }
        }
    }
}
```

No Fragments needed - just composable functions!

---

## Summary

**Single Activity Pros:**
1. Simplified navigation (NavController)
2. Shared ViewModel across screens
3. Shared UI elements (toolbar, bottom nav)
4. Better animations and transitions
5. Faster screen transitions
6. Easier deep linking
7. Simpler state management

**Single Activity Cons:**
1. Fragment lifecycle complexity
2. Memory leaks if ViewBinding not cleaned
3. FragmentManager complexity
4. State loss issues (commit after onSaveInstanceState)
5. Nested fragment challenges
6. More complex testing
7. Manual back button handling

**Verdict:**
Single Activity is the **modern Android standard** (especially with Navigation Component and Compose), but requires understanding Fragment lifecycle and best practices.

## Ответ (RU)
**Подход Single Activity** означает использование **одной основной Activity** для всего приложения, где все экраны представлены как **Fragment**. Это противоположность традиционному подходу с множеством Activity, где каждый экран - отдельная Activity.

### Плюсы (Advantages)

1. **Упрощенная навигация** - использование NavController вместо Intent
2. **Общий ViewModel** - легко делиться данными между экранами
3. **Общие UI элементы** - toolbar и bottom navigation не пересоздаются
4. **Лучшие анимации** - плавные переходы между фрагментами
5. **Быстрые переходы** - нет overhead создания новой Activity
6. **Легкие deep links** - Navigation Component автоматически обрабатывает
7. **Проще state management** - одно состояние на всё приложение

### Минусы (Disadvantages)

1. **Сложность Fragment lifecycle** - больше callback методов чем у Activity
2. **Утечки памяти** - ViewBinding нужно очищать в onDestroyView
3. **Сложность FragmentManager** - управление back stack может запутать
4. **State loss проблемы** - IllegalStateException при commit после onSaveInstanceState
5. **Вложенные фрагменты** - childFragmentManager vs parentFragmentManager
6. **Сложность тестирования** - больше setup чем для Activity
7. **Обработка кнопки назад** - нужно перехватывать вручную

### Таблица сравнения

| Аспект | Single Activity | Multi-Activity |
|--------|----------------|----------------|
| Навигация | Fragment transactions (быстрая) | Activity intents (медленная) |
| Обмен данными | Shared ViewModel (легко) | Intent extras (сложно) |
| Переходы | Плавные, настраиваемые | Ограниченные |
| Память | Меньше (одна Activity) | Больше (много Activity) |
| State management | Проще (одно состояние) | Сложнее |
| Deep links | Navigation Component | Ручная маршрутизация |
| Кривая обучения | Fragment lifecycle (крутая) | Activity lifecycle (проще) |
| Утечки памяти | ViewBinding cleanup нужен | Менее подвержено |
| Back stack | Fragment (сложный) | Activity (простой) |
| Тестирование | Больше setup | Проще |

### Когда использовать Single Activity

**Хорошо подходит для:**
- Приложений с общими UI элементами (toolbar, bottom nav)
- Приложений с плавными переходами
- Сложной навигации
- Современных приложений с Jetpack Navigation
- Приложений с общим состоянием между экранами

**Не идеально для:**
- Простых приложений с малым количеством экранов
- Приложений с полностью независимыми flow
- Legacy кодовых баз (дорогая миграция)
- Команд незнакомых с Fragment

### Вердикт

Single Activity - это **современный Android стандарт** (особенно с Navigation Component и Compose), но требует понимания Fragment lifecycle и best practices.


---

## Related Questions

### Prerequisites (Easier)
- [[q-android-components-besides-activity--android--easy]] - Activity

### Related (Medium)
- [[q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]] - Activity
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Activity
- [[q-if-activity-starts-after-a-service-can-you-connect-to-this-service--android--medium]] - Activity
- [[q-activity-lifecycle-methods--android--medium]] - Activity
- [[q-what-is-activity-and-what-is-it-used-for--android--medium]] - Activity

### Advanced (Harder)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - Activity
