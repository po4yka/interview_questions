---\
id: android-291
title: Fragments vs Activity / Фрагменты vs Activity
aliases: [Fragments vs Activity, Фрагменты vs Activity]
topic: android
subtopics: [activity, fragment, ui-navigation]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-activity-lifecycle, c-fragments, q-fragments-and-activity-relationship--android--hard, q-what-are-fragments-and-why-are-they-more-convenient-to-use-instead-of-multiple-activities--android--hard, q-what-is-activity-and-what-is-it-used-for--android--medium, q-why-are-fragments-needed-if-there-is-activity--android--hard, q-why-use-fragments-when-we-have-activities--android--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [android/activity, android/fragment, android/ui-navigation, difficulty/medium]
---\
# Вопрос (RU)

> Для чего нужны фрагменты, если есть `Activity`?

# Question (EN)

> What are fragments for if there is `Activity`?

## Ответ (RU)

Фрагменты используются для создания многоразовых компонентов UI, которые встраиваются в `Activity`. Они позволяют разбивать экран на независимые части, улучшая модульность, переиспользование и адаптацию интерфейса под разные устройства. Фрагменты можно динамически добавлять, удалять и заменять во время выполнения, управлять для них отдельным жизненным циклом (в рамках жизненного цикла `Activity`) и настраивать навигацию и back stack внутри одной `Activity`.

### 1. Переиспользуемость

Один и тот же `Fragment` может использоваться в разных `Activity` и разных конфигурациях (телефон/планшет), сохраняя общую логику и UI.

```kotlin
// Один и тот же фрагмент, переиспользуемый в разных контекстах
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

// Телефон (одна панель)
class PhoneActivity : AppCompatActivity() {
    fun showProfile(userId: String) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, UserProfileFragment.newInstance(userId))
            .commit()
    }
}

// Планшет (две панели)
class TabletActivity : AppCompatActivity() {
    fun showProfile(userId: String) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.detail_container, UserProfileFragment.newInstance(userId))
            .commit()
    }
}
```

### 2. Модульные UI-компоненты

Сложный экран можно собрать из нескольких фрагментов в одной `Activity`, не создавая отдельную `Activity` под каждый блок.

```kotlin
// Компоновка сложного экрана из нескольких фрагментов
class DashboardActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_dashboard)

        supportFragmentManager.beginTransaction()
            .add(R.id.header_container, HeaderFragment())
            .add(R.id.stats_container, StatsFragment())
            .add(R.id.chart_container, ChartFragment())
            .add(R.id.news_container, NewsFragment())
            .commit()
    }
}
```

### 3. Жизненный Цикл И Управление Состоянием

Фрагменты имеют собственные колбэки жизненного цикла, при этом они связаны с `Activity`, но позволяют инкапсулировать логику и состояние на уровне подкомпонента.

```kotlin
class DataFragment : Fragment() {
    private lateinit var viewModel: DataViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Жизненный цикл фрагмента и его ViewModel scoped к самому фрагменту
        viewModel = ViewModelProvider(this)[DataViewModel::class.java]
    }

    override fun onResume() {
        super.onResume()
        viewModel.refreshData()
    }

    override fun onPause() {
        super.onPause()
        viewModel.saveState()
    }
}
```

Фрагменты разрушаются вместе с `Activity`, но внутри этого жизненного цикла позволяют локально управлять своим состоянием и логикой.

### 4. Навигация И back Stack

Фрагменты позволяют организовать навигацию в рамках одной `Activity`, управляя внутренним back stack через `FragmentManager`.

```kotlin
class MainActivity : AppCompatActivity() {

    fun navigateToDetails(itemId: String) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, DetailsFragment.newInstance(itemId))
            .addToBackStack("details") // Добавляем транзакцию во внутренний back stack
            .commit()
    }
}
```

### 5. Адаптивные Макеты Для телефона/планшета

Те же фрагменты могут использоваться и для одноэкранной, и для двухпанельной раскладки.

```xml
<!-- res/layout/activity_main.xml (телефон) -->
<FrameLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/container"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />

<!-- res/layout-sw600dp/activity_main.xml (планшет) -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:orientation="horizontal"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <FrameLayout
        android:id="@+id/list_container"
        android:layout_width="0dp"
        android:layout_height="match_parent"
        android:layout_weight="1" />

    <FrameLayout
        android:id="@+id/detail_container"
        android:layout_width="0dp"
        android:layout_height="match_parent"
        android:layout_weight="2" />
</LinearLayout>
```

```kotlin
// Одна кодовая база для обеих конфигураций
class MainActivity : AppCompatActivity() {
    private val isTwoPane: Boolean
        get() = findViewById<View?>(R.id.detail_container) != null

    fun showDetails(item: Item) {
        val fragment = DetailsFragment.newInstance(item.id)

        if (isTwoPane) {
            // Планшет: показываем во втором контейнере
            supportFragmentManager.beginTransaction()
                .replace(R.id.detail_container, fragment)
                .commit()
        } else {
            // Телефон: заменяем весь экран
            supportFragmentManager.beginTransaction()
                .replace(R.id.container, fragment)
                .addToBackStack(null)
                .commit()
        }
    }
}
```

### 6. Память И Ресурсы

Фрагменты:
- разделяют окно и ресурсы хост-`Activity`;
- позволяют избежать избыточного количества `Activity` для близких по смыслу экранов.

Важно: нет фиксированных «5MB на `Activity`» или подобных цифр, это зависит от реализации и устройства. Фрагменты не являются «просто `View`» — это UI плюс собственный жизненный цикл и логика в рамках `Activity`.

### 7. Взаимодействие Между Компонентами

Фрагменты удобно связывать через общий `ViewModel`, интерфейсы, реализуемые `Activity`, или Navigation `Component`.

```kotlin
// Общий ViewModel между фрагментами
class SharedDataViewModel : ViewModel() {
    private val _selectedItem = MutableLiveData<Item>()
    val selectedItem: LiveData<Item> = _selectedItem

    fun selectItem(item: Item) {
        _selectedItem.value = item
    }
}

// Фрагмент 1: список
class ListFragment : Fragment() {
    private val viewModel: SharedDataViewModel by activityViewModels()

    private fun onItemClick(item: Item) {
        viewModel.selectItem(item)
    }
}

// Фрагмент 2: детали
class DetailsFragment : Fragment() {
    private val viewModel: SharedDataViewModel by activityViewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        viewModel.selectedItem.observe(viewLifecycleOwner) { item ->
            updateUI(item)
        }
    }
}
```

### 8. Пример С Bottom Navigation

Для нижней навигации обычно не создают отдельную `Activity` на каждый таб, а переключают фрагменты в рамках одной `Activity`.

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val bottomNav = findViewById<BottomNavigationView>(R.id.bottom_nav)

        bottomNav.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_home -> showFragment(HomeFragment())
                R.id.nav_search -> showFragment(SearchFragment())
                R.id.nav_profile -> showFragment(ProfileFragment())
            }
            true
        }

        if (savedInstanceState == null) {
            showFragment(HomeFragment())
        }
    }

    private fun showFragment(fragment: Fragment) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.fragment_container, fragment)
            .commit()
    }
}
```

В продакшене обычно сохраняют экземпляры фрагментов или используют Navigation `Component`, чтобы не пересоздавать их при каждом переключении.

### Ключевые Преимущества Фрагментов (сравнение)

| Возможность           | Activities                                   | Fragments                                                         |
|-----------------------|----------------------------------------------|-------------------------------------------------------------------|
| Переиспользуемость    | Ограничена, экран целиком                   | Высокая, можно встраивать в разные `Activity` и макеты            |
| Память/ресурсы        | Отдельные окна, больший оверхед             | Делят ресурсы `Activity`, эффективны для близких экранов          |
| Жизненный цикл        | Независимый компонент                       | Привязан к `Activity`, но со своими колбэками                     |
| Навигация             | Переключение между `Activity`               | Замена/добавление внутри одной `Activity`                        |
| Back stack            | Системный стек `Activity`                   | Внутренний стек фрагментов через `FragmentManager`                |
| Модульность UI        | Целиком экран                               | Часть экрана, композиция блоков                                  |
| Взаимодействие        | Intents/результаты                          | Общие `ViewModel`, интерфейсы, аргументы навигации                |
| Адаптация макетов     | Часто отдельные `Activity` и макеты         | Те же фрагменты для разных конфигураций (телефон/планшет и т.п.) |

### Когда Использовать Фрагменты

Используйте фрагменты для:
- нижней/таба навигации внутри одной секции;
- master-detail интерфейсов;
- многоразовых UI-компонентов на разных экранах/устройствах;
- адаптивных макетов (телефон/планшет);
- страниц `ViewPager`;
- диалогов через `DialogFragment`.

Используйте отдельные `Activity` для:
- независимых секций приложения;
- разных сценариев/тасков;
- внешних точек входа (deep links, лаунчеры);
- полностью разных контекстов (например, авторизация vs основное приложение).

### Современный Подход: Single-`Activity` Архитектура

Распространённая модель: одна главная `Activity` + набор фрагментов в `NavHostFragment`, навигация через Navigation `Component`.

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val navController = findNavController(R.id.nav_host_fragment)
        findViewById<BottomNavigationView>(R.id.bottom_nav)
            .setupWithNavController(navController)
    }
}
```

## Answer (EN)

Fragments are used to create reusable UI components that can be embedded in different Activities. They allow more flexible interface management and separation into individual parts, improving app modularity. Fragments can be dynamically added or removed at runtime, simplifying interface adaptation for different devices. Unlike Activities, fragments can more easily share data and logic within a single screen (via shared ViewModels, interfaces, etc.).

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

#### 3. Lifecycle and State Management

```kotlin
class DataFragment : Fragment() {
    private lateinit var viewModel: DataViewModel

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // Fragment has its own lifecycle callbacks, ViewModel scoped to the fragment itself
        viewModel = ViewModelProvider(this)[DataViewModel::class.java]
    }

    override fun onResume() {
        super.onResume()
        // Handle its own UI updates within the Activity lifecycle
        viewModel.refreshData()
    }

    override fun onPause() {
        super.onPause()
        // Manage its own state within the Activity lifecycle
        viewModel.saveState()
    }
}
```

Fragments have dedicated lifecycle methods and can encapsulate their own UI logic, but their lifecycle is still tied to the parent `Activity` (if the `Activity` is destroyed, so are its fragments).

#### 4. Navigation and Back `Stack`

```kotlin
class MainActivity : AppCompatActivity() {

    fun navigateToDetails(itemId: String) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.container, DetailsFragment.newInstance(itemId))
            .addToBackStack("details") // Enables back navigation for this transaction
            .commit()
    }
}
```

#### 5. Tablet/Phone Adaptive Layouts

```xml
<!-- res/layout/activity_main.xml (phone) -->
<FrameLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    android:id="@+id/container"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />

<!-- res/layout-sw600dp/activity_main.xml (tablet) -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:orientation="horizontal"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <FrameLayout
        android:id="@+id/list_container"
        android:layout_width="0dp"
        android:layout_height="match_parent"
        android:layout_weight="1" />

    <FrameLayout
        android:id="@+id/detail_container"
        android:layout_width="0dp"
        android:layout_height="match_parent"
        android:layout_weight="2" />
</LinearLayout>
```

```kotlin
// Single codebase handles both
class MainActivity : AppCompatActivity() {
    private val isTwoPane: Boolean
        get() = findViewById<View?>(R.id.detail_container) != null

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

#### 6. Memory and Resource Efficiency

Fragments:
- share the hosting `Activity`'s window and many resources;
- can reduce overhead compared to running many separate Activities for closely related screens.

However, concrete memory numbers depend on implementation and device; it's incorrect to assume fixed sizes like "5MB per `Activity`". Fragments are not "just views"; they wrap UI plus their own lifecycle and logic.

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

Fragments can communicate via shared ViewModels, interfaces implemented by the host `Activity`, or the Navigation `Component`, which is often cleaner than passing data between Activities via Intents for tightly coupled UI parts.

#### 8. Bottom Navigation Example

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        val bottomNav = findViewById<BottomNavigationView>(R.id.bottom_nav)

        // Switch fragments instead of multiple Activities
        bottomNav.setOnItemSelectedListener { item ->
            when (item.itemId) {
                R.id.nav_home -> showFragment(HomeFragment())
                R.id.nav_search -> showFragment(SearchFragment())
                R.id.nav_profile -> showFragment(ProfileFragment())
            }
            true
        }

        // Show initial fragment
        if (savedInstanceState == null) {
            showFragment(HomeFragment())
        }
    }

    private fun showFragment(fragment: Fragment) {
        supportFragmentManager.beginTransaction()
            .replace(R.id.fragment_container, fragment)
            .commit()
    }
}
```

Note: In production, you may want to retain and show/hide existing fragments or use the Navigation `Component` to avoid recreating fragments on each tab selection.

### Key Advantages of Fragments

| Feature | Activities | Fragments |
|---------|-----------|-----------|
| **Reusability** | Limited, whole-screen units | High - can be reused in different Activities/layouts |
| **Memory/Resources** | Separate windows, more overhead per screen | Share `Activity` resources; can be more efficient for related screens |
| **`Lifecycle`** | Independent component lifecycle | `Lifecycle` tied to `Activity` but with dedicated callbacks |
| **Navigation** | Typically involves switching Activities | In-place replacement within one `Activity` |
| **Back `Stack`** | Managed by system `Activity` stack | Managed via FragmentManager within `Activity` |
| **UI Modularity** | Full-screen scope | Portion of screen / composable blocks |
| **Communication** | Intents/Results | Shared `ViewModel`, interfaces, Navigation arguments |
| **Adaptation** | Often separate Activities/layouts | Same fragments used in different layouts (phone/tablet) |

### When to Use Fragments

- Use Fragments for:
  - Bottom/Tab navigation within a section
  - Master-detail layouts
  - Reusable UI components across screens/devices
  - Adaptive layouts (phone/tablet)
  - ViewPager pages
  - Dialog-like components (DialogFragment)

- Use Activities for:
  - Independent app sections or tasks
  - Different task flows
  - External entry points (deep links, launchers)
  - Completely different contexts (e.g., auth vs main app)

### Modern Alternative: Single-`Activity` Architecture

```kotlin
// Modern approach: often one Activity + Navigation Component
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // All primary destinations are Fragments managed by NavHostFragment
        val navController = findNavController(R.id.nav_host_fragment)
        findViewById<BottomNavigationView>(R.id.bottom_nav)
            .setupWithNavController(navController)
    }
}
```

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
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - `Activity`, `Fragment`
- [[q-fragment-vs-activity-lifecycle--android--medium]] - `Activity`, `Fragment`
- [[q-how-does-fragment-lifecycle-differ-from-activity-v2--android--medium]] - `Activity`, `Fragment`
- [[q-why-use-fragments-when-we-have-activities--android--medium]] - `Activity`, `Fragment`
- [[q-fragments-vs-activity--android--medium]] - `Activity`, `Fragment`

### Advanced (Harder)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - `Activity`, `Fragment`
- [[q-fragments-and-activity-relationship--android--hard]] - `Activity`, `Fragment`
- [[q-what-are-fragments-and-why-are-they-more-convenient-to-use-instead-of-multiple-activities--android--hard]] - `Activity`, `Fragment`
