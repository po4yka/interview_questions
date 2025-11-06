---
id: android-245
title: How To Display Two Identical Fragments On The Screen At The Same Time / Как
  отобразить два одинаковых Fragment на экране одновременно
aliases:
- Display Two Identical Fragments
- Multiple Fragment Instances
- Два одинаковых фрагмента
- Несколько экземпляров Fragment
topic: android
subtopics:
- fragment
- lifecycle
- ui-views
question_kind: android
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-fragments
- c-lifecycle
- q-fragment-basics--android--easy
- q-how-to-choose-layout-for-fragment--android--easy
- q-save-data-outside-fragment--android--medium
created: 2025-10-15
updated: 2025-10-28
sources: []
tags:
- android/fragment
- android/lifecycle
- android/ui-views
- difficulty/easy
- fragments
- ui
---

# Вопрос (RU)

> Как на экране одновременно отобразить два одинаковых Fragment?

# Question (EN)

> How to display two identical fragments on the screen at the same time?

---

## Ответ (RU)

Добавьте два экземпляра одного класса Fragment в разные контейнеры макета Activity. Каждый экземпляр работает независимо с собственным состоянием.

### Основной Подход

**1. Макет Activity с двумя контейнерами**

```xml
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <FrameLayout
        android:id="@+id/fragment_container_1"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1" />

    <FrameLayout
        android:id="@+id/fragment_container_2"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1" />
</LinearLayout>
```

**2. Fragment с factory-методом**

```kotlin
class CounterFragment : Fragment() {
    private var count = 0

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val title = arguments?.getString(ARG_TITLE) ?: "Counter"
        savedInstanceState?.let { count = it.getInt(KEY_COUNT, 0) }
        // Setup UI
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putInt(KEY_COUNT, count)
    }

    companion object {
        private const val ARG_TITLE = "title"
        private const val KEY_COUNT = "count"

        fun newInstance(title: String) = CounterFragment().apply {
            arguments = Bundle().apply { putString(ARG_TITLE, title) }
        }
    }
}
```

**3. Добавление в Activity**

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        if (savedInstanceState == null) {
            supportFragmentManager.beginTransaction()
                .add(R.id.fragment_container_1,
                     CounterFragment.newInstance("Counter 1"), "fragment_1")
                .add(R.id.fragment_container_2,
                     CounterFragment.newInstance("Counter 2"), "fragment_2")
                .commit()
        }
    }
}
```

### Ключевые Принципы

✅ **Используйте уникальные теги** - для идентификации экземпляров
✅ **Проверяйте savedInstanceState** - чтобы не создавать дубликаты при пересоздании Activity
✅ **Сохраняйте состояние** - каждый Fragment независимо сохраняет свое состояние
✅ **Factory-метод newInstance()** - стандартный паттерн для передачи аргументов

❌ Не создавайте фрагменты повторно при каждом onCreate()
❌ Не используйте один тег для разных экземпляров

---

## Answer (EN)

Add two instances of the same Fragment class to separate container views in the Activity layout. Each instance maintains independent state.

### Basic Approach

**1. Activity Layout with Two Containers**

```xml
<LinearLayout
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical">

    <FrameLayout
        android:id="@+id/fragment_container_1"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1" />

    <FrameLayout
        android:id="@+id/fragment_container_2"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1" />
</LinearLayout>
```

**2. Fragment with Factory Method**

```kotlin
class CounterFragment : Fragment() {
    private var count = 0

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val title = arguments?.getString(ARG_TITLE) ?: "Counter"
        savedInstanceState?.let { count = it.getInt(KEY_COUNT, 0) }
        // Setup UI
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putInt(KEY_COUNT, count)
    }

    companion object {
        private const val ARG_TITLE = "title"
        private const val KEY_COUNT = "count"

        fun newInstance(title: String) = CounterFragment().apply {
            arguments = Bundle().apply { putString(ARG_TITLE, title) }
        }
    }
}
```

**3. Adding to Activity**

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        if (savedInstanceState == null) {
            supportFragmentManager.beginTransaction()
                .add(R.id.fragment_container_1,
                     CounterFragment.newInstance("Counter 1"), "fragment_1")
                .add(R.id.fragment_container_2,
                     CounterFragment.newInstance("Counter 2"), "fragment_2")
                .commit()
        }
    }
}
```

### Key Principles

✅ **Use unique tags** - to identify fragment instances
✅ **Check savedInstanceState** - to avoid creating duplicates on Activity recreation
✅ **Save state independently** - each Fragment manages its own state
✅ **Factory method newInstance()** - standard pattern for passing arguments

❌ Don't recreate fragments on every onCreate()
❌ Don't use the same tag for different instances

---

## Follow-ups

- What happens if you don't check savedInstanceState before adding fragments?
- How can fragments communicate with each other through the parent Activity?
- What's the difference between add() and replace() for fragment transactions?
- How do you handle configuration changes with multiple fragment instances?
- Can you use the same Fragment instance in multiple containers?

## References

- [Android Fragments Documentation](https://developer.android.com/guide/fragments)
- [FragmentTransaction API](https://developer.android.com/reference/androidx/fragment/app/FragmentTransaction)
- [Fragment Lifecycle](https://developer.android.com/guide/fragments/lifecycle)
- [Best Practices for Fragments](https://developer.android.com/guide/fragments/best-practices)

## Related Questions

### Prerequisites / Concepts

- [[c-fragments]]
- [[c-lifecycle]]


### Prerequisites (Easier)
- [[q-fragment-basics--android--easy]] - Fragment basics
- [[q-how-to-choose-layout-for-fragment--android--easy]] - Fragment layouts

### Related (Same Level)
- [[q-how-to-implement-view-behavior-when-it-is-added-to-the-tree--android--easy]] - View lifecycle
- [[q-which-class-to-catch-gestures--android--easy]] - Touch handling

### Advanced (Harder)
- [[q-save-data-outside-fragment--android--medium]] - Fragment data persistence
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]] - Fragment use cases
- [[q-why-use-fragments-when-we-have-activities--android--medium]] - Fragment vs Activity
