---
id: 20251003141824
title: "How to save scroll state when Activity is recreated (duplicate)"
date: 2025-10-03
tags:
  - android
  - activity
  - state-management
  - recyclerview
difficulty: medium
topic: android
moc: moc-android
status: draft
source: https://t.me/easy_kotlin/1064
---

# How to save scroll state when Activity is recreated

## Question (RU)
Как сохранить состояние скролла при пересоздании Activity?

## Question (EN)
How to save scroll state when Activity is recreated

## Answer (EN)

When an Activity is recreated due to configuration changes or process death, the scroll state of ScrollView or RecyclerView is reset. To preserve the scroll position, you can save and restore it using onSaveInstanceState() or ViewModel.

### Using onSaveInstanceState for ScrollView

```kotlin
class ScrollActivity : AppCompatActivity() {

    private lateinit var scrollView: ScrollView

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_scroll)

        scrollView = findViewById(R.id.scrollView)

        savedInstanceState?.let {
            val scrollPosition = it.getInt(KEY_SCROLL_POSITION, 0)
            scrollView.post {
                scrollView.scrollTo(0, scrollPosition)
            }
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)
        outState.putInt(KEY_SCROLL_POSITION, scrollView.scrollY)
    }

    companion object {
        private const val KEY_SCROLL_POSITION = "scroll_position"
    }
}
```

### Using LinearLayoutManager State for RecyclerView

RecyclerView's LayoutManager has built-in state management:

```kotlin
class ListActivity : AppCompatActivity() {

    private lateinit var recyclerView: RecyclerView
    private lateinit var layoutManager: LinearLayoutManager

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_list)

        layoutManager = LinearLayoutManager(this)
        recyclerView = findViewById(R.id.recyclerView)
        recyclerView.layoutManager = layoutManager

        savedInstanceState?.let {
            val state = it.getParcelable<Parcelable>(KEY_LAYOUT_STATE)
            layoutManager.onRestoreInstanceState(state)
        }
    }

    override fun onSaveInstanceState(outState: Bundle) {
        super.onSaveInstanceState(outState)

        val state = layoutManager.onSaveInstanceState()
        outState.putParcelable(KEY_LAYOUT_STATE, state)
    }

    companion object {
        private const val KEY_LAYOUT_STATE = "layout_state"
    }
}
```

## Answer (RU)
При пересоздании Activity состояние ScrollView или RecyclerView сбрасывается. Чтобы этого избежать, можно сохранить и восстановить позицию скролла. Использование onSaveInstanceState() позволяет сохранять данные в Bundle перед уничтожением Activity и восстанавливать их. Для RecyclerView можно использовать LinearLayoutManager, который имеет встроенный механизм сохранения состояния.

## Related Topics
- onSaveInstanceState
- RecyclerView state
- LayoutManager
- Configuration changes
