---
id: android-396
title: "Fragments and Multiple Activities / Фрагменты и несколько Activity"
aliases: [Fragments and Activities, Фрагменты и Activities]
topic: android
subtopics: [activity, fragment, ui-navigation]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-activity-fragments-relationship, c-fragments, q-what-are-fragments-for-if-there-is-activity--android--medium, q-what-is-activity-and-what-is-it-used-for--android--medium]
created: 2025-10-15
updated: 2025-10-31
tags: [android/activity, android/fragment, android/ui-navigation, difficulty/hard, fragments, ui-navigation]
date created: Saturday, November 1st 2025, 12:47:07 pm
date modified: Saturday, November 1st 2025, 5:43:31 pm
---

# Что Такое Фрагменты И Почему Их Удобнее Использовать Вместо Множества Activity?

**English**: What are fragments and why are they more convenient to use instead of multiple activities?

## Answer (EN)
Fragments are modular UI components that can be embedded in Activities. They represent a portion of the user interface or behavior that can be inserted into an activity. Fragments have their own lifecycle, receive their own input events, and can be added or removed while the activity is running.

### Why Fragments Are More Convenient Than Multiple Activities

#### 1. Modularity

Fragments promote a more modular application design and allow separating different functions into independent components for reuse in different activities.

**Example:** A date picker fragment can be used in both a booking form and a user profile.

```kotlin
// Reusable DatePickerFragment
class DatePickerFragment : DialogFragment() {
    private var onDateSelectedListener: ((LocalDate) -> Unit)? = null

    fun setOnDateSelectedListener(listener: (LocalDate) -> Unit) {
        onDateSelectedListener = listener
    }

    override fun onCreateDialog(savedInstanceState: Bundle?): Dialog {
        val calendar = Calendar.getInstance()
        return DatePickerDialog(
            requireContext(),
            { _, year, month, day ->
                val date = LocalDate.of(year, month + 1, day)
                onDateSelectedListener?.invoke(date)
            },
            calendar.get(Calendar.YEAR),
            calendar.get(Calendar.MONTH),
            calendar.get(Calendar.DAY_OF_MONTH)
        )
    }
}

// Use in BookingActivity
class BookingActivity : AppCompatActivity() {
    private fun showDatePicker() {
        val datePicker = DatePickerFragment()
        datePicker.setOnDateSelectedListener { date ->
            binding.dateTextView.text = date.toString()
        }
        datePicker.show(supportFragmentManager, "datePicker")
    }
}

// Use in ProfileActivity
class ProfileActivity : AppCompatActivity() {
    private fun showBirthdayPicker() {
        val datePicker = DatePickerFragment()
        datePicker.setOnDateSelectedListener { date ->
            viewModel.updateBirthday(date)
        }
        datePicker.show(supportFragmentManager, "datePicker")
    }
}
```

#### 2. Adaptivity

Fragments are ideal for creating adaptive user interfaces for different devices. On a tablet, multiple fragments can be displayed simultaneously, while on a phone they are displayed sequentially.

```kotlin
// Adaptive layout based on screen size
class MainActivity : AppCompatActivity() {
    private var isTwoPane = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Check if we have two pane layout (tablet)
        isTwoPane = findViewById<View>(R.id.detail_container) != null

        if (savedInstanceState == null) {
            supportFragmentManager.beginTransaction()
                .replace(R.id.list_container, ItemListFragment())
                .commit()

            if (isTwoPane) {
                // Tablet: show detail fragment alongside list
                supportFragmentManager.beginTransaction()
                    .replace(R.id.detail_container, ItemDetailFragment())
                    .commit()
            }
        }
    }

    fun showDetail(itemId: String) {
        val fragment = ItemDetailFragment.newInstance(itemId)

        if (isTwoPane) {
            // Tablet: replace detail fragment
            supportFragmentManager.beginTransaction()
                .replace(R.id.detail_container, fragment)
                .commit()
        } else {
            // Phone: navigate to detail fragment
            supportFragmentManager.beginTransaction()
                .replace(R.id.list_container, fragment)
                .addToBackStack(null)
                .commit()
        }
    }
}
```

```xml
<!-- layout/activity_main.xml (phone) -->
<FrameLayout
    android:id="@+id/list_container"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />

<!-- layout-sw600dp/activity_main.xml (tablet) -->
<LinearLayout
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

#### 3. Lifecycle Management

Fragments allow independent management of their state and behavior, simplifying work with complex interfaces.

```kotlin
class VideoPlayerFragment : Fragment() {
    private var player: ExoPlayer? = null

    override fun onStart() {
        super.onStart()
        // Initialize player when fragment becomes visible
        player = ExoPlayer.Builder(requireContext()).build()
    }

    override fun onStop() {
        super.onStop()
        // Release player when fragment is no longer visible
        player?.release()
        player = null
    }
}
```

#### 4. Code Reusability

Increases development and maintenance efficiency by reusing code in different parts or even applications.

```kotlin
// Reusable SettingsFragment
class SettingsFragment : PreferenceFragmentCompat() {
    override fun onCreatePreferences(savedInstanceState: Bundle?, rootKey: String?) {
        setPreferencesFromResource(R.xml.preferences, rootKey)
    }
}

// Used in SettingsActivity
class SettingsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        supportFragmentManager.beginTransaction()
            .replace(android.R.id.content, SettingsFragment())
            .commit()
    }
}

// Also used as part of main app with navigation drawer
class MainActivity : AppCompatActivity() {
    private fun showSettings() {
        supportFragmentManager.beginTransaction()
            .replace(R.id.main_container, SettingsFragment())
            .addToBackStack("settings")
            .commit()
    }
}
```

#### 5. Improved Performance

Managing one activity with fragments is more efficient than switching between multiple activities. **Switching fragments requires fewer resources than launching a new activity.**

**Performance comparison:**

```kotlin
// Launching new activity - expensive operation
fun navigateToDetailActivity(itemId: String) {
    val intent = Intent(this, DetailActivity::class.java)
    intent.putExtra("ITEM_ID", itemId)
    startActivity(intent)
    // Overhead: creating new activity, inflating layout, lifecycle callbacks
}

// Switching fragment - lightweight operation
fun navigateToDetailFragment(itemId: String) {
    supportFragmentManager.beginTransaction()
        .replace(R.id.container, DetailFragment.newInstance(itemId))
        .addToBackStack(null)
        .commit()
    // Less overhead: reusing existing activity context
}
```

**Why fragments are more performant:**
- No need to create new Activity context
- Single window/surface reused
- Faster transitions
- Less memory overhead
- Simpler back stack management

#### 6. Better Transition and Animation Management

Fragments provide tools for complex animations between fragments, creating a smooth user experience.

```kotlin
// Custom fragment transitions
fun navigateWithAnimation() {
    supportFragmentManager.beginTransaction()
        .setCustomAnimations(
            R.anim.slide_in_right,  // enter
            R.anim.slide_out_left,  // exit
            R.anim.slide_in_left,   // popEnter
            R.anim.slide_out_right  // popExit
        )
        .replace(R.id.container, DetailFragment())
        .addToBackStack(null)
        .commit()
}

// Shared element transitions
fun navigateWithSharedElement(imageView: ImageView) {
    val fragment = DetailFragment()
    supportFragmentManager.beginTransaction()
        .addSharedElement(imageView, "image_transition")
        .replace(R.id.container, fragment)
        .addToBackStack(null)
        .commit()
}
```

### Example Implementation

```kotlin
// Fragment definition
class ProfileFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View? {
        return inflater.inflate(R.layout.fragment_profile, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // Setup UI
    }
}

// Using fragment in activity
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        if (savedInstanceState == null) {
            supportFragmentManager.beginTransaction()
                .add(R.id.fragment_container, ProfileFragment())
                .commit()
        }
    }
}
```

### Summary

Using fragments allows creating **flexible, modular, and efficient applications** that:
- Better adapt to different devices
- Simplify component reuse
- Improve application state management
- Provide better performance than multiple activities
- Enable smoother transitions and animations

## Ответ (RU)
Фрагменты — это модули в пользовательском интерфейсе, которые могут быть вложены в активности (Activity). Представляют собой часть пользовательского интерфейса или поведения, которые можно вставить в активность. Они обладают собственным жизненным циклом, получают собственные входные события и могут быть добавлены или удалены при работе активности. Использование фрагментов удобнее, чем использование множества активностей: 1. Модульность способствует более модульному дизайну приложения и позволяет разделить различные функции на независимые компоненты для повторного использования в разных активностях. Например, фрагмент для выбора даты можно использовать как в форме бронирования, так и в профиле пользователя. 2. Адаптивность идеально подходит для создания адаптивных пользовательских интерфейсов на разных устройствах. На планшете можно одновременно отображать несколько фрагментов, а на телефоне — поочередно. 3. Управление жизненным циклом позволяет фрагментам независимо управлять своим состоянием и поведением, что упрощает работу со сложными интерфейсами. 4. Повторное использование кода повышает эффективность разработки и поддержки приложений за счет переиспользования кода в разных частях или даже приложениях. 5. Улучшенная производительность достигается за счет того что управление одной активностью с фрагментами эффективнее чем переключение между множеством активностей. Переключение фрагментов требует меньше ресурсов чем запуск новой активности. 6. Лучшее управление переходами и анимациями предоставляет инструменты для сложных анимаций между фрагментами, создавая плавный пользовательский опыт. Пример: Файл FragmentExample.java и fragment_example.xml показывают как создать фрагмент. Использование фрагментов позволяет создавать гибкие модульные и эффективные приложения, которые лучше адаптируются к разным устройствам упрощают повторное использование компонентов и улучшают управление состоянием приложения.


---


## Follow-ups

- [[c-activity-fragments-relationship]]
- [[c-fragments]]
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]]


## References

- https://developer.android.com/docs


## Related Questions

### Prerequisites (Easier)
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]] - Activity, Fragment
- [[q-why-use-fragments-when-we-have-activities--android--medium]] - Activity, Fragment
- [[q-fragments-vs-activity--android--medium]] - Activity, Fragment

### Related (Medium)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - Activity, Fragment
- [[q-fragments-and-activity-relationship--android--hard]] - Activity, Fragment
- [[q-why-fragment-callbacks-differ-from-activity-callbacks--android--hard]] - Activity, Fragment
