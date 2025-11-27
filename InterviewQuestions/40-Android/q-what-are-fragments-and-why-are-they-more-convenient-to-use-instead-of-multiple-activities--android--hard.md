---
id: android-396
title: Fragments and Multiple Activities / Фрагменты и несколько Activity
aliases: [Fragments and Activities, Фрагменты и Activities]
topic: android
subtopics:
  - activity
  - fragment
  - ui-navigation
question_kind: theory
difficulty: hard
original_language: en
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-activity
  - q-how-to-handle-the-situation-where-activity-can-open-multiple-times-due-to-deeplink--android--medium
  - q-what-are-fragments-for-if-there-is-activity--android--medium
  - q-what-is-activity-and-what-is-it-used-for--android--medium
  - q-why-are-fragments-needed-if-there-is-activity--android--hard
  - q-why-use-fragments-when-we-have-activities--android--medium
created: 2025-10-15
updated: 2025-11-10
tags: [android/activity, android/fragment, android/ui-navigation, difficulty/hard, fragments, ui-navigation]

date created: Saturday, November 1st 2025, 12:47:07 pm
date modified: Tuesday, November 25th 2025, 8:53:56 pm
---
# Вопрос (RU)
> Фрагменты и несколько `Activity`

# Question (EN)
> Fragments and Multiple Activities

---

## Ответ (RU)
Фрагменты — это модульные компоненты пользовательского интерфейса, которые встраиваются в `Activity`. Они представляют собой часть интерфейса или поведения, имеют собственный жизненный цикл, обрабатывают свои события ввода и могут добавляться или удаляться во время работы активности.

Во многих случаях использование фрагментов вместо множества мелких `Activity` удобнее, потому что фрагменты:
- позволяют строить модульный и переиспользуемый интерфейс,
- поддерживают адаптивные макеты (телефон/планшет),
- дают более гибкое управление жизненным циклом и состоянием внутри одной `Activity`,
- упрощают реализацию навигации в рамках single-activity подхода,
- в ряде сценариев снижают накладные расходы по сравнению с постоянным созданием новых `Activity`.

### Почему Фрагменты Могут Быть Удобнее, Чем Несколько `Activity`

#### 1. Модульность

Фрагменты способствуют модульному дизайну и позволяют выносить отдельные функции в независимые компоненты, переиспользуемые в разных активностях.

Пример: фрагмент выбора даты может использоваться и в форме бронирования, и в профиле пользователя.

```kotlin
// Переиспользуемый DatePickerFragment
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

// Использование в BookingActivity
class BookingActivity : AppCompatActivity() {
    private fun showDatePicker() {
        val datePicker = DatePickerFragment()
        datePicker.setOnDateSelectedListener { date ->
            binding.dateTextView.text = date.toString()
        }
        datePicker.show(supportFragmentManager, "datePicker")
    }
}

// Использование в ProfileActivity
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

#### 2. Адаптивность

Фрагменты хорошо подходят для адаптивных интерфейсов. На планшете можно отображать несколько фрагментов сразу, на телефоне — показывать их последовательно в рамках одной `Activity`.

```kotlin
// Адаптивный layout в зависимости от размера экрана
class MainActivity : AppCompatActivity() {
    private var isTwoPane = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Проверяем, есть ли контейнер для деталей (планшет)
        isTwoPane = findViewById<View>(R.id.detail_container) != null

        if (savedInstanceState == null) {
            supportFragmentManager.beginTransaction()
                .replace(R.id.list_container, ItemListFragment())
                .commit()

            if (isTwoPane) {
                // Планшет: показываем список и детали рядом
                supportFragmentManager.beginTransaction()
                    .replace(R.id.detail_container, ItemDetailFragment())
                    .commit()
            }
        }
    }

    fun showDetail(itemId: String) {
        val fragment = ItemDetailFragment.newInstance(itemId)

        if (isTwoPane) {
            // Планшет: обновляем панель деталей
            supportFragmentManager.beginTransaction()
                .replace(R.id.detail_container, fragment)
                .commit()
        } else {
            // Телефон: открываем детали вместо списка
            supportFragmentManager.beginTransaction()
                .replace(R.id.list_container, fragment)
                .addToBackStack(null)
                .commit()
        }
    }
}
```

```xml
<!-- layout/activity_main.xml (телефон) -->
<FrameLayout
    android:id="@+id/list_container"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />

<!-- layout-sw600dp/activity_main.xml (планшет) -->
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

#### 3. Управление Жизненным Циклом

Фрагменты позволяют независимо управлять своим состоянием и поведением в рамках жизненного цикла родительской `Activity`, что упрощает работу со сложными интерфейсами.

```kotlin
class VideoPlayerFragment : Fragment() {
    private var player: ExoPlayer? = null

    override fun onStart() {
        super.onStart()
        // Инициализируем плеер, когда фрагмент становится видимым
        player = ExoPlayer.Builder(requireContext()).build()
    }

    override fun onStop() {
        super.onStop()
        // Освобождаем ресурсы, когда фрагмент больше не виден
        player?.release()
        player = null
    }
}
```

#### 4. Переиспользование Кода

Фрагменты повышают эффективность разработки и сопровождения за счет переиспользования логики и интерфейса в разных частях приложения.

```kotlin
// Переиспользуемый SettingsFragment
class SettingsFragment : PreferenceFragmentCompat() {
    override fun onCreatePreferences(savedInstanceState: Bundle?, rootKey: String?) {
        setPreferencesFromResource(R.xml.preferences, rootKey)
    }
}

// Использование в отдельной SettingsActivity
class SettingsActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        supportFragmentManager.beginTransaction()
            .replace(android.R.id.content, SettingsFragment())
            .commit()
    }
}

// Использование как часть основного экрана
class MainActivity : AppCompatActivity() {
    private fun showSettings() {
        supportFragmentManager.beginTransaction()
            .replace(R.id.main_container, SettingsFragment())
            .addToBackStack("settings")
            .commit()
    }
}
```

#### 5. Использование Ресурсов По Сравнению С Несколькими `Activity`

Навигация внутри одной `Activity` с помощью фрагментов может уменьшать накладные расходы по сравнению с частым запуском новых `Activity` (создание нового экземпляра, полный цикл callbacks, отдельное раздувание layout). Замена фрагментов в существующей `Activity`, как правило, требует меньше работы от системы.

Однако выигрыш зависит от конкретного дизайна приложения: фрагменты не являются гарантированно "более производительным" решением во всех случаях и сами добавляют свою сложность.

```kotlin
// Переход в новую Activity
fun navigateToDetailActivity(itemId: String) {
    val intent = Intent(this, DetailActivity::class.java)
    intent.putExtra("ITEM_ID", itemId)
    startActivity(intent)
    // Накладные расходы: новый экземпляр Activity, callbacks, свой layout
}

// Переключение фрагмента в рамках одной Activity
fun navigateToDetailFragment(itemId: String) {
    supportFragmentManager.beginTransaction()
        .replace(R.id.container, DetailFragment.newInstance(itemId))
        .addToBackStack(null)
        .commit()
    // Переиспользуется существующая Activity и окно, меняется только фрагмент и его View
}
```

Ключевые моменты:
- Не нужно создавать отдельную `Activity` для каждого экрана.
- Можно переиспользовать одно окно/Surface.
- Можно управлять back stack на уровне фрагментов внутри одной `Activity`.

#### 6. Переходы И Анимации

Фрагменты предоставляют API для настройки анимаций и shared element-переходов между фрагментами, что помогает делать навигацию более плавной.

```kotlin
// Кастомные анимации фрагментов
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

// Shared element-переход
fun navigateWithSharedElement(imageView: ImageView) {
    val fragment = DetailFragment()
    supportFragmentManager.beginTransaction()
        .addSharedElement(imageView, "image_transition")
        .replace(R.id.container, fragment)
        .addToBackStack(null)
        .commit()
}
```

Замечание: фрагменты сами по себе добавляют сложность (FragmentManager, вложенные жизненные циклы, управление back stack). В современных приложениях их обычно используют вместе с single-activity архитектурой и Jetpack Navigation, а в Compose-интерфейсах их роль может уменьшаться.

### Пример Реализации

```kotlin
// Определение фрагмента
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
        // Инициализация UI
    }
}

// Использование фрагмента в Activity
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

### Итог

Использование фрагментов помогает строить гибкие и модульные Android-приложения, которые:
- лучше адаптируются к различным устройствам и конфигурациям экранов,
- упрощают повторное использование компонентов,
- улучшают управление состоянием и жизненным циклом внутри одной `Activity`,
- в ряде случаев уменьшают накладные расходы по сравнению с большим количеством `Activity`,
- позволяют реализовывать более плавные переходы и анимации.

Выбор между несколькими `Activity`, фрагментами и другими подходами навигации должен основываться на архитектуре приложения, удобстве сопровождения и UX-требованиях, а не только на вопросах производительности.

## Answer (EN)
Fragments are modular UI components that can be embedded in Activities. They represent a portion of the user interface or behavior that can be inserted into an activity. Fragments have their own lifecycle, receive their own input events, and can be added or removed while the activity is running.

They are often preferable to having many small Activities because they:
- enable modular and reusable UI components,
- support adaptive layouts (e.g., phone vs tablet),
- allow more fine-grained lifecycle and state management inside a single host `Activity`,
- simplify implementing in-app navigation patterns (especially with a single-activity approach),
- can reduce overhead compared to constantly creating new Activities, when used appropriately.

### Why Fragments Can Be More Convenient Than Multiple Activities

#### 1. Modularity

Fragments promote a more modular application design and allow separating different functions into independent components for reuse in different activities.

Example: a date picker fragment can be used in both a booking form and a user profile.

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

Fragments are well-suited for creating adaptive user interfaces for different devices. On a tablet, multiple fragments can be displayed simultaneously, while on a phone they are typically displayed sequentially within the same `Activity`.

```kotlin
// Adaptive layout based on screen size
class MainActivity : AppCompatActivity() {
    private var isTwoPane = false

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Check if we have two-pane layout (tablet)
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

Fragments allow independent management of their state and behavior within the host `Activity` lifecycle, which helps with complex interfaces.

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

Fragments increase development and maintenance efficiency by allowing reuse of UI and behavior across different screens and even different apps.

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

#### 5. Resource Usage Compared to Multiple Activities

Managing navigation within a single `Activity` using fragments can avoid some overhead associated with frequently launching new Activities (e.g., creating a new `Activity` instance, running its full lifecycle, inflating a new layout tree each time). Swapping fragments inside an existing `Activity` typically involves less system work.

However, the actual performance difference depends on the specific app design; fragments are not a universal performance silver bullet, and additional fragment complexity can also have a cost.

```kotlin
// Launching new activity
fun navigateToDetailActivity(itemId: String) {
    val intent = Intent(this, DetailActivity::class.java)
    intent.putExtra("ITEM_ID", itemId)
    startActivity(intent)
    // Overhead: new Activity instance, lifecycle callbacks, separate layout inflation
}

// Switching fragment within the same Activity
fun navigateToDetailFragment(itemId: String) {
    supportFragmentManager.beginTransaction()
        .replace(R.id.container, DetailFragment.newInstance(itemId))
        .addToBackStack(null)
        .commit()
    // Reuses the existing Activity and window; only fragment lifecycle and view hierarchy change
}
```

Key points:
- No need to create a new `Activity` component for each screen.
- Single window/surface can be reused.
- Back stack can be controlled at the fragment level inside one host `Activity`.

#### 6. Better Transition and Animation Management

Fragments provide APIs for custom transitions and shared element animations between fragments, enabling smoother in-app navigation within a single `Activity`.

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

Note: Fragments also introduce their own complexity (fragment manager, nested lifecycles, back stack nuances). In modern Android apps, they are commonly used together with a single-activity architecture and Jetpack Navigation, and in newer UI stacks (e.g., Jetpack Compose) their role can be reduced.

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

Using fragments allows creating flexible, modular applications that:
- adapt better to different devices and layouts,
- simplify component reuse,
- improve state and lifecycle management inside a single host `Activity`,
- can reduce overhead compared to many small Activities when used appropriately,
- enable smoother in-app transitions and animations.

Fragments are a tool; the choice between multiple Activities and fragments (or other navigation approaches) should be based on app architecture, maintainability, and UX requirements, not solely on performance.

---

## Follow-ups

- [[c-activity]]
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]]
- How would you design navigation for a large app using a single-activity + fragments approach?
- What are the main pitfalls and common bugs when working with `FragmentManager` and the fragment back stack?
- How does fragment-based navigation compare to Jetpack Compose Navigation in modern Android apps?

## References

- [Navigation](https://developer.android.com/guide/navigation)
- [Activities](https://developer.android.com/guide/components/activities)

## Related Questions

### Prerequisites (Easier)
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]] - `Activity`, `Fragment`
- [[q-why-use-fragments-when-we-have-activities--android--medium]] - `Activity`, `Fragment`
- [[q-fragments-vs-activity--android--medium]] - `Activity`, `Fragment`

### Related (Medium)
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - `Activity`, `Fragment`
- [[q-fragments-and-activity-relationship--android--hard]] - `Activity`, `Fragment`
- [[q-why-fragment-callbacks-differ-from-activity-callbacks--android--hard]] - `Activity`, `Fragment`
