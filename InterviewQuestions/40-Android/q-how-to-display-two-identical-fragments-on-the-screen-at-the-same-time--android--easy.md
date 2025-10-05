---
tags:
  - fragments
  - ui
  - easy_kotlin
  - android/fragments
  - android
difficulty: easy
---

# Как на экране одновременно отобразить два одинаковых фрагмента?

**English**: How to display two identical fragments on the screen at the same time?

## Answer

To simultaneously display two identical fragments on one screen in an Android application, you need to add two instances of the fragment to different containers in the activity layout. In this case, each fragment will work independently, even if they use the same class.

### Steps to Display Two Identical Fragments

#### 1. Create Activity Layout with Two Containers

Create a layout for the activity that will contain two containers for fragments. This is typically done using `FrameLayout` or `LinearLayout`.

```xml
<!-- activity_main.xml -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <!-- First fragment container -->
    <FrameLayout
        android:id="@+id/fragment_container_1"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"
        android:background="@color/container_1_bg" />

    <!-- Divider -->
    <View
        android:layout_width="match_parent"
        android:layout_height="1dp"
        android:background="@color/divider" />

    <!-- Second fragment container -->
    <FrameLayout
        android:id="@+id/fragment_container_2"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"
        android:background="@color/container_2_bg" />

</LinearLayout>
```

#### Alternative: Horizontal Layout

```xml
<!-- activity_main_horizontal.xml -->
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="horizontal">

    <!-- Left fragment container -->
    <FrameLayout
        android:id="@+id/fragment_container_left"
        android:layout_width="0dp"
        android:layout_height="match_parent"
        android:layout_weight="1" />

    <!-- Vertical divider -->
    <View
        android:layout_width="1dp"
        android:layout_height="match_parent"
        android:background="@color/divider" />

    <!-- Right fragment container -->
    <FrameLayout
        android:id="@+id/fragment_container_right"
        android:layout_width="0dp"
        android:layout_height="match_parent"
        android:layout_weight="1" />

</LinearLayout>
```

#### 2. Create Fragment Class

Create the fragment class that will be used for displaying both instances.

```kotlin
class CounterFragment : Fragment() {

    private var count = 0
    private lateinit var binding: FragmentCounterBinding

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        binding = FragmentCounterBinding.inflate(inflater, container, false)
        return binding.root
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        // Get title from arguments
        val title = arguments?.getString(ARG_TITLE) ?: "Counter"
        binding.titleText.text = title

        // Restore count from saved state
        savedInstanceState?.let {
            count = it.getInt(KEY_COUNT, 0)
        }

        updateCountText()

        binding.incrementButton.setOnClickListener {
            count++
            updateCountText()
        }

        binding.decrementButton.setOnClickListener {
            count--
            updateCountText()
        }
    }

    private fun updateCountText() {
        binding.countText.text = count.toString()
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putInt(KEY_COUNT, count)
    }

    companion object {
        private const val ARG_TITLE = "title"
        private const val KEY_COUNT = "count"

        fun newInstance(title: String): CounterFragment {
            return CounterFragment().apply {
                arguments = Bundle().apply {
                    putString(ARG_TITLE, title)
                }
            }
        }
    }
}
```

#### 3. Fragment Layout

```xml
<!-- fragment_counter.xml -->
<androidx.constraintlayout.widget.ConstraintLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:padding="16dp">

    <TextView
        android:id="@+id/titleText"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="Counter"
        android:textSize="24sp"
        android:textStyle="bold"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent" />

    <TextView
        android:id="@+id/countText"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="0"
        android:textSize="48sp"
        android:textStyle="bold"
        app:layout_constraintTop_toBottomOf="@id/titleText"
        app:layout_constraintBottom_toTopOf="@id/incrementButton"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent" />

    <Button
        android:id="@+id/incrementButton"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="+"
        android:textSize="24sp"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintEnd_toStartOf="@id/decrementButton"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintHorizontal_chainStyle="packed" />

    <Button
        android:id="@+id/decrementButton"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:text="-"
        android:textSize="24sp"
        android:layout_marginStart="16dp"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintStart_toEndOf="@id/incrementButton"
        app:layout_constraintEnd_toEndOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
```

#### 4. Add Fragments to Activity

Add two instances of the fragment to your activity.

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        // Only add fragments if this is the first creation
        if (savedInstanceState == null) {
            addFragments()
        }
    }

    private fun addFragments() {
        // Create two instances of the same fragment
        val fragment1 = CounterFragment.newInstance("Counter 1")
        val fragment2 = CounterFragment.newInstance("Counter 2")

        // Add both fragments to their respective containers
        supportFragmentManager.beginTransaction()
            .add(R.id.fragment_container_1, fragment1, "fragment_1")
            .add(R.id.fragment_container_2, fragment2, "fragment_2")
            .commit()
    }
}
```

### Alternative: Using replace() Instead of add()

```kotlin
private fun replaceFragments() {
    val fragment1 = CounterFragment.newInstance("First")
    val fragment2 = CounterFragment.newInstance("Second")

    supportFragmentManager.beginTransaction()
        .replace(R.id.fragment_container_1, fragment1)
        .replace(R.id.fragment_container_2, fragment2)
        .commit()
}
```

### Advanced: Dynamic Fragment Management

```kotlin
class MultiFragmentActivity : AppCompatActivity() {

    private val fragmentCount = 2

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_multi_fragment)

        if (savedInstanceState == null) {
            addMultipleFragments()
        }
    }

    private fun addMultipleFragments() {
        val transaction = supportFragmentManager.beginTransaction()

        repeat(fragmentCount) { index ->
            val fragment = CounterFragment.newInstance("Counter ${index + 1}")
            val containerId = when (index) {
                0 -> R.id.fragment_container_1
                1 -> R.id.fragment_container_2
                else -> return@repeat
            }
            transaction.add(containerId, fragment, "fragment_$index")
        }

        transaction.commit()
    }

    // Accessing specific fragment
    fun updateFragmentTitle(fragmentIndex: Int, newTitle: String) {
        val fragment = supportFragmentManager.findFragmentByTag("fragment_$fragmentIndex") as? CounterFragment
        fragment?.updateTitle(newTitle)
    }
}

// Update fragment to support title updates
class CounterFragment : Fragment() {
    // ... existing code ...

    fun updateTitle(newTitle: String) {
        binding.titleText.text = newTitle
    }
}
```

### Using ConstraintLayout for More Complex Layouts

```xml
<!-- activity_main_constraint.xml -->
<androidx.constraintlayout.widget.ConstraintLayout
    xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent"
    android:layout_height="match_parent">

    <!-- Top fragment container -->
    <FrameLayout
        android:id="@+id/fragment_container_top"
        android:layout_width="0dp"
        android:layout_height="0dp"
        app:layout_constraintTop_toTopOf="parent"
        app:layout_constraintBottom_toTopOf="@id/guideline"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent" />

    <androidx.constraintlayout.widget.Guideline
        android:id="@+id/guideline"
        android:layout_width="wrap_content"
        android:layout_height="wrap_content"
        android:orientation="horizontal"
        app:layout_constraintGuide_percent="0.5" />

    <!-- Bottom fragment container -->
    <FrameLayout
        android:id="@+id/fragment_container_bottom"
        android:layout_width="0dp"
        android:layout_height="0dp"
        app:layout_constraintTop_toBottomOf="@id/guideline"
        app:layout_constraintBottom_toBottomOf="parent"
        app:layout_constraintStart_toStartOf="parent"
        app:layout_constraintEnd_toEndOf="parent" />

</androidx.constraintlayout.widget.ConstraintLayout>
```

### Communication Between Fragment Instances

```kotlin
class MainActivity : AppCompatActivity() {

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        if (savedInstanceState == null) {
            val fragment1 = CounterFragment.newInstance("Counter 1")
            val fragment2 = CounterFragment.newInstance("Counter 2")

            supportFragmentManager.beginTransaction()
                .add(R.id.fragment_container_1, fragment1, "fragment_1")
                .add(R.id.fragment_container_2, fragment2, "fragment_2")
                .commit()
        }
    }

    // Synchronize fragments
    fun syncFragmentCounts() {
        val fragment1 = supportFragmentManager.findFragmentByTag("fragment_1") as? CounterFragment
        val fragment2 = supportFragmentManager.findFragmentByTag("fragment_2") as? CounterFragment

        val count1 = fragment1?.getCount() ?: 0
        fragment2?.setCount(count1)
    }
}

// Update CounterFragment with getCount and setCount methods
class CounterFragment : Fragment() {
    // ... existing code ...

    fun getCount(): Int = count

    fun setCount(newCount: Int) {
        count = newCount
        updateCountText()
    }
}
```

### Key Points

1. **Each fragment is an independent instance** - They maintain separate state even though they use the same class

2. **Use unique container IDs** - Each fragment needs its own container in the layout

3. **Use unique tags** - Tags help identify and retrieve specific fragment instances

4. **State is preserved independently** - Each fragment saves and restores its own state

5. **Communication through Activity** - Fragments can communicate via the parent activity

## Ответ

Чтобы одновременно отобразить два одинаковых фрагмента на одном экране в Android-приложении, вам нужно добавить два экземпляра фрагмента в разные контейнеры в макете активности. В этом случае каждый фрагмент будет работать независимо, даже если они используют один и тот же класс. 1. Создайте макет для активности который будет содержать два контейнера для фрагментов. Обычно это делается с помощью FrameLayout или LinearLayout. 2. Создайте класс фрагмента который будет использоваться для отображения обоих экземпляров. 3. Добавьте фрагменты в активность Теперь добавьте два экземпляра фрагмента в вашу активность. 4. Создайте макет для фрагмента Это может быть любой макет, который вы хотите использовать.

