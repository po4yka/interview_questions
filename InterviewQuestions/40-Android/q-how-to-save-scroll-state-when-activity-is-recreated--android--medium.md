---\
id: android-423
title: "How To Save Scroll State When Activity Is Recreated / Как сохранить состояние скролла при пересоздании Activity"
aliases: [Save RecyclerView Position, Scroll State Persistence]
topic: android
subtopics: [lifecycle, ui-views]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-savedstatehandle, c-viewmodel, q-activity-lifecycle-methods--android--medium, q-diffutil-background-calculation-issues--android--medium]
created: 2025-10-15
updated: 2025-10-30
tags: [android, android/lifecycle, android/ui-views, difficulty/medium, recyclerview, scrollview, state-preservation]
anki_cards:
  - slug: android-423-0-en
    front: "How to save scroll state when Activity is recreated?"
    back: |
      **ScrollView:** Assign stable `android:id` - automatic save

      **RecyclerView:**
      ```kotlin
      override fun onSaveInstanceState(outState: Bundle) {
          super.onSaveInstanceState(outState)
          outState.putParcelable("state",
              layoutManager.onSaveInstanceState())
      }
      // Restore: layoutManager.onRestoreInstanceState(saved)
      ```

      **ViewModel approach:** Store `Parcelable` state in `SavedStateHandle`
    tags:
      - android_lifecycle
      - android_layouts
      - difficulty::medium
  - slug: android-423-0-ru
    front: "Как сохранить состояние скролла при пересоздании Activity?"
    back: |
      **ScrollView:** Назначить стабильный `android:id` - автосохранение

      **RecyclerView:**
      ```kotlin
      override fun onSaveInstanceState(outState: Bundle) {
          super.onSaveInstanceState(outState)
          outState.putParcelable("state",
              layoutManager.onSaveInstanceState())
      }
      // Восстановить: layoutManager.onRestoreInstanceState(saved)
      ```

      **ViewModel подход:** Хранить `Parcelable` состояние в `SavedStateHandle`
    tags:
      - android_lifecycle
      - android_layouts
      - difficulty::medium

---\
# Вопрос (RU)

> Как сохранить позицию скролла при пересоздании `Activity`?

# Question (EN)

> How to save scroll state when `Activity` is recreated?

---

## Ответ (RU)

При пересоздании `Activity` (rotation, process death) позиция скролла может сбрасываться. Для устойчивого сохранения состояния используются несколько подходов.

Важно: многие стандартные `View` (включая ScrollView и `RecyclerView` с корректно заданными id) умеют автоматически сохранять и восстанавливать своё состояние через механизм `onSaveInstanceState()` / `onRestoreInstanceState()`. Явное сохранение имеет смысл, когда:
- нужно полный контроль над логикой восстановления;
- состояние зависит от данных (например, список меняется);
- вы хотите пережить process death с помощью архитектурных компонентов.

### Подход 1: ScrollView C onSaveInstanceState (явное сохранение)

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var scrollView: ScrollView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        scrollView = findViewById(R.id.scrollView)

        // Если используете явное сохранение
        savedInstanceState?.let {
            val scrollY = it.getInt(KEY_SCROLL_Y, 0)
            scrollView.post { scrollView.scrollTo(0, scrollY) }
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putInt(KEY_SCROLL_Y, scrollView.scrollY)
    }

    companion object {
        private const val KEY_SCROLL_Y = "scroll_y"
    }
}
```

Примечание: при наличии стабильного `id` у `ScrollView` фреймворк и так сохранит позицию скролла через иерархию `View`. Явный код нужен только при кастомной логике.

### Подход 2: RecyclerView С Состоянием LayoutManager

Рекомендуемый базовый подход для `RecyclerView` - использовать встроенный механизм `LayoutManager.onSaveInstanceState()` / `onRestoreInstanceState()`.

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var recyclerView: RecyclerView
    private lateinit var layoutManager: LinearLayoutManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        recyclerView = findViewById(R.id.recyclerView)
        layoutManager = LinearLayoutManager(this)
        recyclerView.layoutManager = layoutManager

        savedInstanceState?.getParcelable<Parcelable>(KEY_STATE)?.let {
            layoutManager.onRestoreInstanceState(it)
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        layoutManager.onSaveInstanceState()?.let {
            outState.putParcelable(KEY_STATE, it)
        }
    }

    companion object {
        private const val KEY_STATE = "recycler_state"
    }
}
```

Этот подход хорошо работает, пока:
- данные адаптера уже загружены к моменту восстановления;
- порядок и количество элементов не меняются радикально.

### Подход 3: SavedStateHandle В ViewModel (контролируемое сохранение)

Подход с `SavedStateHandle` - хороший выбор, если:
- нужно пережить process death;
- нужно восстановить позицию относительно данных доменной модели (например, по item-id),
  а не полагаться только на внутреннее состояние `LayoutManager`;
- список или порядок элементов может меняться.

```kotlin
class ScrollViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    var scrollPosition: Int
        get() = savedStateHandle[KEY_POSITION] ?: 0
        set(value) { savedStateHandle[KEY_POSITION] = value }

    var scrollOffset: Int
        get() = savedStateHandle[KEY_OFFSET] ?: 0
        set(value) { savedStateHandle[KEY_OFFSET] = value }

    companion object {
        private const val KEY_POSITION = "scroll_position"
        private const val KEY_OFFSET = "scroll_offset"
    }
}

class MainActivity : AppCompatActivity() {
    private lateinit var recyclerView: RecyclerView
    private val viewModel: ScrollViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        setupRecyclerView()
        restoreScrollPosition()
    }

    private fun setupRecyclerView() {
        recyclerView = findViewById(R.id.recyclerView)
        recyclerView.layoutManager = LinearLayoutManager(this)

        recyclerView.addOnScrollListener(object : RecyclerView.OnScrollListener() {
            override fun onScrollStateChanged(rv: RecyclerView, state: Int) {
                if (state == RecyclerView.SCROLL_STATE_IDLE) {
                    saveScrollPosition()
                }
            }
        })
    }

    private fun saveScrollPosition() {
        val layoutManager = recyclerView.layoutManager as LinearLayoutManager
        val firstVisible = layoutManager.findFirstVisibleItemPosition()
        if (firstVisible != RecyclerView.NO_POSITION) {
            viewModel.scrollPosition = firstVisible
            layoutManager.findViewByPosition(firstVisible)?.let {
                viewModel.scrollOffset = it.top
            }
        }
    }

    private fun restoreScrollPosition() {
        if (viewModel.scrollPosition >= 0) {
            recyclerView.post {
                (recyclerView.layoutManager as LinearLayoutManager)
                    .scrollToPositionWithOffset(
                        viewModel.scrollPosition,
                        viewModel.scrollOffset
                    )
            }
        }
    }
}
```

Здесь `SavedStateHandle` обеспечивает сохранение нужных значений в `SavedStateRegistry`, так что они доступны после process death. Этот подход дополняет встроенное состояние `RecyclerView`, а не заменяет его.

### Сравнение Подходов

| Подход                         | Config Changes | Process Death | Точность                          | Сложность |
|--------------------------------|----------------|---------------|-----------------------------------|-----------|
| onSaveInstanceState (`Bundle`)   | Yes            | Yes           | Высокая (при корректной логике)   | Низкая    |
| `LayoutManager` state (RV)       | Yes            | Yes           | Точная (при стабильных данных)    | Низкая    |
| `ViewModel` + SavedStateHandle   | Yes            | Yes           | Точная и гибкая (данные-зависимая)| Средняя   |

(Отдельный вариант "чистый `ViewModel` без SavedStateHandle" намеренно не рекомендуется для критичного состояния, т.к. не переживает process death.)

### Best Practices

DO:
- Используйте `LayoutManager.onSaveInstanceState()` для стандартного восстановления скролла `RecyclerView`.
- Используйте `SavedStateHandle` (через `ViewModel`) для критичных UI-состояний, которые должны пережить process death или зависят от данных.
- Вызывайте операции скролла через `post()` / после layout, чтобы избежать восстановления до отрисовки.
- Тестируйте с включенной опцией "Don't keep activities".

DON'T:
- Не рассчитывайте на обычный `ViewModel` без `SavedStateHandle` для состояния, которое должно пережить process death.
- Не игнорируйте сценарии process death и задержки загрузки данных.
- Не сохраняйте слишком много данных в `Bundle` (приблизительный лимит для `onSaveInstanceState()` около 1MB; превышение может вызвать TransactionTooLargeException).

## Answer (EN)

When `Activity` is recreated (rotation, process death), scroll position may reset. There are several approaches to robust state preservation.

Important: many standard Views (including ScrollView and `RecyclerView` with stable ids) automatically save and restore their state via `onSaveInstanceState()` / `onRestoreInstanceState()`. Manual handling is useful when:
- you need full control over restore logic;
- state depends on your data (e.g., list changes);
- you want process-death resilience via architecture components.

### Approach 1: ScrollView with onSaveInstanceState (explicit saving)

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var scrollView: ScrollView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        scrollView = findViewById(R.id.scrollView)

        // If you use explicit saving
        savedInstanceState?.let {
            val scrollY = it.getInt(KEY_SCROLL_Y, 0)
            scrollView.post { scrollView.scrollTo(0, scrollY) }
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putInt(KEY_SCROLL_Y, scrollView.scrollY)
    }

    companion object {
        private const val KEY_SCROLL_Y = "scroll_y"
    }
}
```

Note: if `ScrollView` has a stable id and default behavior is kept, the framework will save its scroll position automatically as part of the view hierarchy state. Custom code is needed only for specialized behavior.

### Approach 2: RecyclerView with LayoutManager State

Recommended baseline for `RecyclerView` - use the built-in `LayoutManager.onSaveInstanceState()` / `onRestoreInstanceState()`.

```kotlin
class MainActivity : AppCompatActivity() {
    private lateinit var recyclerView: RecyclerView
    private lateinit var layoutManager: LinearLayoutManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        recyclerView = findViewById(R.id.recyclerView)
        layoutManager = LinearLayoutManager(this)
        recyclerView.layoutManager = layoutManager

        savedInstanceState?.getParcelable<Parcelable>(KEY_STATE)?.let {
            layoutManager.onRestoreInstanceState(it)
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        layoutManager.onSaveInstanceState()?.let {
            outState.putParcelable(KEY_STATE, it)
        }
    }

    companion object {
        private const val KEY_STATE = "recycler_state"
    }
}
```

This works well when:
- adapter data is ready by the time you restore;
- item order/count are not significantly changed.

### Approach 3: SavedStateHandle in ViewModel (controlled saving)

Using `SavedStateHandle` is a strong option when:
- you must survive process death;
- you want to restore position relative to your domain data (e.g., by item-id),
  not only rely on `LayoutManager`'s internal state;
- list contents or ordering can change.

```kotlin
class ScrollViewModel(
    private val savedStateHandle: SavedStateHandle
) : ViewModel() {
    var scrollPosition: Int
        get() = savedStateHandle[KEY_POSITION] ?: 0
        set(value) { savedStateHandle[KEY_POSITION] = value }

    var scrollOffset: Int
        get() = savedStateHandle[KEY_OFFSET] ?: 0
        set(value) { savedStateHandle[KEY_OFFSET] = value }

    companion object {
        private const val KEY_POSITION = "scroll_position"
        private const val KEY_OFFSET = "scroll_offset"
    }
}

class MainActivity : AppCompatActivity() {
    private lateinit var recyclerView: RecyclerView
    private val viewModel: ScrollViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        setupRecyclerView()
        restoreScrollPosition()
    }

    private fun setupRecyclerView() {
        recyclerView = findViewById(R.id.recyclerView)
        recyclerView.layoutManager = LinearLayoutManager(this)

        recyclerView.addOnScrollListener(object : RecyclerView.OnScrollListener() {
            override fun onScrollStateChanged(rv: RecyclerView, state: Int) {
                if (state == RecyclerView.SCROLL_STATE_IDLE) {
                    saveScrollPosition()
                }
            }
        })
    }

    private fun saveScrollPosition() {
        val layoutManager = recyclerView.layoutManager as LinearLayoutManager
        val firstVisible = layoutManager.findFirstVisibleItemPosition()
        if (firstVisible != RecyclerView.NO_POSITION) {
            viewModel.scrollPosition = firstVisible
            layoutManager.findViewByPosition(firstVisible)?.let {
                viewModel.scrollOffset = it.top
            }
        }
    }

    private fun restoreScrollPosition() {
        if (viewModel.scrollPosition >= 0) {
            recyclerView.post {
                (recyclerView.layoutManager as LinearLayoutManager)
                    .scrollToPositionWithOffset(
                        viewModel.scrollPosition,
                        viewModel.scrollOffset
                    )
            }
        }
    }
}
```

Here, `SavedStateHandle` integrates with the `SavedStateRegistry` so values are preserved across process death. This approach complements the built-in `RecyclerView` state rather than replacing it.

### Comparison of Approaches

| Approach                       | Config Changes | Process Death | Precision                              | Complexity |
|--------------------------------|----------------|---------------|-----------------------------------------|------------|
| onSaveInstanceState (`Bundle`)   | Yes            | Yes           | High (with correct logic)               | Low        |
| `LayoutManager` state (RV)       | Yes            | Yes           | Exact (with stable/compatible data)     | Low        |
| `ViewModel` + SavedStateHandle   | Yes            | Yes           | Exact, flexible, data-aware             | Medium     |

(A "plain `ViewModel` without SavedStateHandle" variant is intentionally not recommended for critical scroll state because it does not survive process death.)

### Best Practices

DO:
- Use `LayoutManager.onSaveInstanceState()` for standard `RecyclerView` scroll restore.
- Use `SavedStateHandle` (via `ViewModel`) for critical UI state that must survive process death and/or depends on your data model.
- Post scroll operations (`post {}` / after layout) to avoid restoring before the view is laid out.
- Test with "Don't keep activities" enabled.

DON'T:
- Don't rely on plain `ViewModel` without `SavedStateHandle` for state that must survive process death.
- Don't ignore process death and delayed-data scenarios when designing scroll restoration.
- Don't put excessive data into the `Bundle` (`onSaveInstanceState()` is effectively limited to about 1MB; exceeding it risks `TransactionTooLargeException`).

---

## Follow-ups

- How does SavedStateHandle survive process death internally?
- What's the `Bundle` size limit for onSaveInstanceState()?
- Can you save `RecyclerView` scroll state for StaggeredGridLayoutManager?
- How to handle scroll restoration when adapter data changes during recreation?
- What happens if you restore scroll position before adapter data is loaded?

## References

- [[c-savedstatehandle]] - SavedStateHandle concept
- [[c-viewmodel]] - `ViewModel` lifecycle
- [[q-activity-lifecycle-methods--android--medium]] - `Activity` lifecycle
- [Saving UI States](https://developer.android.com/topic/libraries/architecture/saving-states)
- [RecyclerView state management](https://developer.android.com/reference/androidx/recyclerview/widget/RecyclerView)

## Related Questions

### Prerequisites (Easier)
- [[q-android-components-besides-activity--android--easy]] - `Activity` basics

### Related (Same Level)
- [[q-activity-lifecycle-methods--android--medium]] - `Activity` lifecycle
- [[q-what-happens-when-a-new-activity-is-called-is-memory-from-the-old-one-freed--android--medium]] - Memory management
- [[q-single-activity-pros-cons--android--medium]] - Architecture patterns
- [[q-diffutil-background-calculation-issues--android--medium]] - `RecyclerView` optimization

### Advanced (Harder)
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - `Fragment` lifecycle
- [[q-why-are-fragments-needed-if-there-is-activity--android--hard]] - Architecture decisions
