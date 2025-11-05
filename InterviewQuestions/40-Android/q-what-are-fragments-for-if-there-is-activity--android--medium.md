---
id: android-291
title: Fragments vs Activity / Фрагменты vs Activity
aliases:
- Fragments vs Activity
- Фрагменты vs Activity
topic: android
subtopics:
- activity
- fragment
- ui-navigation
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-activity-lifecycle
- c-fragments
- q-what-are-fragments-and-why-are-they-more-convenient-to-use-instead-of-multiple-activities--android--hard
- q-what-is-activity-and-what-is-it-used-for--android--medium
created: 2025-10-15
updated: 2025-10-31
tags:
- activity
- android/activity
- android/fragment
- android/ui-navigation
- difficulty/medium
- fragments
date created: Saturday, November 1st 2025, 12:47:07 pm
date modified: Saturday, November 1st 2025, 5:43:31 pm
---

# Вопрос (RU)

Для чего нужны фрагменты, если есть Activity

## Answer (EN)
# Question (EN)
> Fragments vs Activity

---

Fragments are used to create reusable UI components that can be embedded in different Activities. They allow more flexible interface management and separation into individual parts, improving app modularity. Fragments can be dynamically added or removed at runtime, simplifying interface adaptation for different devices. Unlike Activities, fragments can share resources within a single screen.

### Why Fragments When We Have Activities?

#### 1. Reusability

```kotlin
// Same fragment used in different contexts
class UserProfileFragment : Fragment() {
    companion object {
        fun newInstance(userId: String) = UserProfileFragment().apply {
            arguments = bundleOf("userId" to userId)
        }
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return inflater.inflate(R.layout.fragment_user_profile, container, false)
    }
}

// Used in phone (single pane)
class PhoneActivity : AppCompatActivity() {
    fun showProfile(userId: String) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, UserProfileFragment.newInstance(userId))
            .commit()
    }
}

// Used in tablet (dual pane)
class TabletActivity : AppCompatActivity() {
    fun showProfile(userId: String) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.detail_container, UserProfileFragment.newInstance(userId))
            .commit()
    }
}
```

#### 2. Modular UI Components

```kotlin
// Compose complex screens from fragments
class DashboardActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dashboard)

        // Add multiple fragments to single activity
        supportFragmentManager.beginTransaction()
            .add(R.id.header_container, HeaderFragment())
            .add(R.id.stats_container, StatsFragment())
            .add(R.id.chart_container, ChartFragment())
            .add(R.id.news_container, NewsFragment())
            .commit()
    }
}
```

#### 3. Better Lifecycle Management

```kotlin
class DataFragment : Fragment() {
    private lateinit var viewModel: DataViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Fragment has its own lifecycle
        viewModel = ViewModelProvider(this)[DataViewModel::class.java]
    }

    override fun onResume() {
        super.onResume()
        // Can pause/resume without recreating entire Activity
        viewModel.refreshData()
    }

    override fun onPause() {
        super.onPause()
        // Save state independent of Activity
        viewModel.saveState()
    }
}
```

#### 4. Navigation and Back Stack

```kotlin
class MainActivity : AppCompatActivity() {

    fun navigateToDetails(itemId: String) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, DetailsFragment.newInstance(itemId))
            .addToBackStack("details") // Automatic back navigation
            .commit()
    }

    // Back button automatically pops fragment
    // No need to manage multiple activities
}
```

#### 5. Tablet/Phone Adaptive Layouts

```kotlin
// res/layout/activity_main.xml (phone)
<FrameLayout
    android:id="@+id/container"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />

// res/layout-sw600dp/activity_main.xml (tablet)
<LinearLayout android:orientation="horizontal">
    <FrameLayout
        android:id="@+id/list_container"
        android:layout_width="0dp"
        android:layout_weight="1" />

    <FrameLayout
        android:id="@+id/detail_container"
        android:layout_width="0dp"
        android:layout_weight="2" />
</LinearLayout>

// Single codebase handles both
class MainActivity : AppCompatActivity() {
    private val isTwoPane: Boolean
        get() = findViewById<View>(R.id.detail_container) != null

    fun showDetails(item: Item) {
        val fragment = DetailsFragment.newInstance(item.id)

        if (isTwoPane) {
            // Tablet: show in detail pane
            supportFragmentManager.beginTransaction()
                .replace(R.id.detail_container, fragment)
                .commit()
        } else {
            // Phone: replace entire screen
            supportFragmentManager.beginTransaction()
                .replace(R.id.container, fragment)
                .addToBackStack(null)
                .commit()
        }
    }
}
```

#### 6. Memory Efficiency

```kotlin
// Activities are heavy - full window, system resources
// Fragments are lightweight - just views

// Bad: Multiple activities
class ListActivity : AppCompatActivity() // ~5MB
class DetailActivity : AppCompatActivity() // ~5MB
class SettingsActivity : AppCompatActivity() // ~5MB
// Total: ~15MB

// Good: Single activity + fragments
class MainActivity : AppCompatActivity() { // ~5MB
    // ListFragment, DetailFragment, SettingsFragment
    // Total: ~6-7MB (fragments share activity resources)
}
```

#### 7. Communication Between Components

```kotlin
// Shared ViewModel between fragments
class SharedDataViewModel : ViewModel() {
    private val _selectedItem = MutableLiveData<Item>()
    val selectedItem: LiveData<Item> = _selectedItem

    fun selectItem(item: Item) {
        _selectedItem.value = item
    }
}

// Fragment 1: List
class ListFragment : Fragment() {
    private val viewModel: SharedDataViewModel by activityViewModels()

    private fun onItemClick(item: Item) {
        viewModel.selectItem(item)
    }
}

// Fragment 2: Details
class DetailsFragment : Fragment() {
    private val viewModel: SharedDataViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel.selectedItem.observe(viewLifecycleOwner) { item ->
            updateUI(item)
        }
    }
}
```

#### 8. Bottom Navigation Example

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val bottomNav = findViewById<BottomNavigationView>(R.id.bottom_nav)

        // Switch fragments, not activities
        bottomNav.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_home -> showFragment(HomeFragment())
                R.id.nav_search -> showFragment(SearchFragment())
                R.id.nav_profile -> showFragment(ProfileFragment())
            }
            true
        }

        // Show initial fragment
        showFragment(HomeFragment())
    }

    private fun showFragment(fragment: Fragment) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.fragment_container, fragment)
            .commit()
    }
}
```

### Key Advantages of Fragments

| Feature | Activities | Fragments |
|---------|-----------|-----------|
| **Reusability** | Limited | High - reuse in different contexts |
| **Memory** | Heavy (~5MB each) | Light - share parent resources |
| **Lifecycle** | Independent | Tied to Activity but separate |
| **Navigation** | New window | In-place replacement |
| **Back Stack** | System managed | FragmentManager managed |
| **UI Modularity** | Full screen | Portion of screen |
| **Communication** | Intents/Results | Shared ViewModel/Interface |
| **Adaptation** | Separate activities | Same fragments, different layouts |

### When to Use Fragments

- **Use Fragments for:**
- Bottom/Tab navigation
- Master-detail layouts
- Reusable UI components
- Adaptive layouts (phone/tablet)
- ViewPager content
- Dialog-like components

- **Use Activities for:**
- Independent app sections
- Different task flows
- External entry points (deep links)
- Completely different context

### Modern Alternative: Single-Activity Architecture

```kotlin
// Modern approach: One Activity + Navigation Component
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // All screens are fragments
        val navController = findNavController(R.id.nav_host_fragment)
        findViewById<BottomNavigationView>(R.id.bottom_nav)
            .setupWithNavController(navController)
    }
}
```

## Ответ (RU)

Фрагменты используются для создания многоразовых компонентов пользовательского интерфейса, которые могут быть встроены в различные Activity. Они позволяют более гибко управлять интерфейсом и разделять его на отдельные части, что улучшает модульность приложения. Фрагменты могут быть динамически добавлены или удалены во время выполнения, что упрощает адаптацию интерфейса под разные устройства. В отличие от Activity, фрагменты могут совместно использовать ресурсы внутри одного экрана.

---


## Follow-ups

- [[c-activity-lifecycle]]
- [[c-fragments]]
- [[q-what-are-fragments-and-why-are-they-more-convenient-to-use-instead-of-multiple-activities--android--hard]]


## References

- [Navigation](https://developer.android.com/guide/navigation)
- [Activities](https://developer.android.com/guide/components/activities)


## Related Questions

### Related (Medium)
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Activity, Fragment
- [[q-fragment-vs-activity-lifecycle--android--medium]] - Activity, Fragment
- [[q-how-does-fragment-lifecycle-differ-from-activity-v2--android--medium]] - Activity, Fragment
- [[q-why-use-fragments-when-we-have-activities--android--medium]] - Activity, Fragment
- [[q-fragments-vs-activity--android--medium]] - Activity, Fragment

### Advanced (Harder)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - Activity, Fragment
- [[q-fragments-and-activity-relationship--android--hard]] - Activity, Fragment
- [[q-what-are-fragments-and-why-are-they-more-convenient-to-use-instead-of-multiple-activities--android--hard]] - Activity, Fragment
