---
id: android-423
title: "How To Save Scroll State When Activity Is Recreated / Как сохранить состояние скролла при пересоздании Activity"
aliases: [Save RecyclerView Position, Scroll State Persistence, Восстановление состояния RecyclerView, Сохранение позиции скролла]
topic: android
subtopics: [lifecycle, ui-views]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-viewmodel, q-activity-lifecycle-methods--android--medium, q-diffutil-background-calculation-issues--android--medium]
created: 2025-10-15
updated: 2025-10-30
tags: [android, android/lifecycle, android/ui-views, difficulty/medium, recyclerview, scrollview, state-preservation]
---

# Вопрос (RU)

> Как сохранить позицию скролла при пересоздании `Activity`?

# Question (EN)

> How to save scroll state when `Activity` is recreated?

---

## Ответ (RU)

При пересоздании `Activity` (rotation, process death) позиция скролла сбрасывается. Существует несколько подходов для сохранения состояния.

### Подход 1: `ScrollView` С onSaveInstanceState

```kotlin
class MainActivity : AppCompatActivity() {
 private lateinit var scrollView: ScrollView

 override fun onCreate(savedInstanceState: Bundle?) {
 super.onCreate(savedInstanceState)
 setContentView(R.layout.activity_main)

 scrollView = findViewById(R.id.scrollView)

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

### Подход 2: `RecyclerView` С LayoutManager State

✅ **Рекомендуемый подход** - использует встроенный механизм:

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

### Подход 3: SavedStateHandle В `ViewModel`

✅ **Best Practice** - переживает process death:

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
 viewModel.scrollPosition = layoutManager.findFirstVisibleItemPosition()

 layoutManager.findViewByPosition(viewModel.scrollPosition)?.let {
 viewModel.scrollOffset = it.top
 }
 }

 private fun restoreScrollPosition() {
 if (viewModel.scrollPosition > 0) {
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

### Сравнение Подходов

| Подход | Config Changes | Process Death | Точность | Сложность |
|--------|----------------|---------------|----------|-----------|
| onSaveInstanceState | ✅ | ✅ | Высокая | Низкая |
| LayoutManager state | ✅ | ✅ | Точная | Низкая |
| `ViewModel` | ✅ | ❌ | Точная | Средняя |
| SavedStateHandle | ✅ | ✅ | Точная | Средняя |

### Best Practices

✅ **DO:**
- Используйте `LayoutManager.onSaveInstanceState()` для `RecyclerView`
- Используйте `SavedStateHandle` в production
- Вызывайте scroll операции через `post()` после layout
- Тестируйте с включенной опцией "Don't keep activities"

❌ **DON'T:**
- Не используйте простой `ViewModel` без SavedStateHandle для критичного состояния
- Не забывайте про process death сценарии
- Не сохраняйте слишком много данных в `Bundle` (лимит ~1MB)

## Answer (EN)

When `Activity` is recreated (rotation, process death), scroll position resets. Several approaches exist for state preservation.

### Approach 1: `ScrollView` with onSaveInstanceState

```kotlin
class MainActivity : AppCompatActivity() {
 private lateinit var scrollView: ScrollView

 override fun onCreate(savedInstanceState: Bundle?) {
 super.onCreate(savedInstanceState)
 setContentView(R.layout.activity_main)

 scrollView = findViewById(R.id.scrollView)

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

### Approach 2: `RecyclerView` with LayoutManager State

✅ **Recommended approach** - uses built-in mechanism:

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

### Approach 3: SavedStateHandle in `ViewModel`

✅ **Best Practice** - survives process death:

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
 viewModel.scrollPosition = layoutManager.findFirstVisibleItemPosition()

 layoutManager.findViewByPosition(viewModel.scrollPosition)?.let {
 viewModel.scrollOffset = it.top
 }
 }

 private fun restoreScrollPosition() {
 if (viewModel.scrollPosition > 0) {
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

### Comparison of Approaches

| Approach | Config Changes | Process Death | Precision | Complexity |
|----------|----------------|---------------|-----------|------------|
| onSaveInstanceState | ✅ | ✅ | High | Low |
| LayoutManager state | ✅ | ✅ | Exact | Low |
| `ViewModel` | ✅ | ❌ | Exact | Medium |
| SavedStateHandle | ✅ | ✅ | Exact | Medium |

### Best Practices

✅ **DO:**
- Use `LayoutManager.onSaveInstanceState()` for `RecyclerView`
- Use `SavedStateHandle` in production
- Post scroll operations after layout pass
- Test with "Don't keep activities" enabled

❌ **DON'T:**
- Don't use plain `ViewModel` without SavedStateHandle for critical state
- Don't forget process death scenarios
- Don't save too much data in `Bundle` (limit ~1MB)

---

## Follow-ups

- How does SavedStateHandle survive process death internally?
- What's the `Bundle` size limit for onSaveInstanceState()?
- Can you save `RecyclerView` scroll state for StaggeredGridLayoutManager?
- How to handle scroll restoration when adapter data changes during recreation?
- What happens if you restore scroll position before adapter data is loaded?

## References

- - SavedStateHandle concept
- [[c-viewmodel]] - `ViewModel` lifecycle
- [[q-activity-lifecycle-methods--android--medium]] - `Activity` lifecycle
- [Saving UI States](https://developer.android.com/topic/libraries/architecture/saving-states)
- [`RecyclerView` state management](https://developer.android.com/reference/androidx/recyclerview/widget/`RecyclerView`)

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
