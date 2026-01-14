---
id: android-245
title: How To Display Two Identical Fragments On The Screen At The Same Time / Как отобразить два одинаковых Fragment на экране одновременно
aliases: [Display Two Identical Fragments, Multiple Fragment Instances, Два одинаковых фрагмента, Несколько экземпляров Fragment]
topic: android
subtopics: [fragment, ui-views]
question_kind: android
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-compose-recomposition, c-fragments, c-lifecycle, c-recomposition, c-wear-compose, q-dagger-build-time-optimization--android--medium, q-fragment-basics--android--easy, q-how-to-choose-layout-for-fragment--android--easy, q-save-data-outside-fragment--android--medium, q-why-are-fragments-needed-if-there-is-activity--android--hard, q-why-use-fragments-when-we-have-activities--android--medium]
created: 2025-10-15
updated: 2025-11-11
sources: []
tags: [android/fragment, android/ui-views, difficulty/easy, fragments, ui]
anki_cards:
  - slug: android-245-0-en
    front: "How to display two identical fragments on the screen at the same time?"
    back: |
      Add **two separate instances** of the same Fragment class to different containers.

      **Key steps**:
      1. Create layout with two `FrameLayout` containers
      2. Use `newInstance()` factory method for each fragment
      3. Add with unique tags in `FragmentTransaction`

      ```kotlin
      if (savedInstanceState == null) {
          supportFragmentManager.beginTransaction()
              .add(R.id.container_1, MyFragment.newInstance("A"), "frag_1")
              .add(R.id.container_2, MyFragment.newInstance("B"), "frag_2")
              .commit()
      }
      ```

      **Key rule**: One Fragment instance per container. Never reuse the same object.
    tags:
      - android_fragments
      - difficulty::easy
  - slug: android-245-0-ru
    front: "Как отобразить два одинаковых Fragment на экране одновременно?"
    back: |
      Добавьте **два отдельных экземпляра** одного класса Fragment в разные контейнеры.

      **Ключевые шаги**:
      1. Создайте макет с двумя `FrameLayout` контейнерами
      2. Используйте factory-метод `newInstance()` для каждого фрагмента
      3. Добавляйте с уникальными тегами в `FragmentTransaction`

      ```kotlin
      if (savedInstanceState == null) {
          supportFragmentManager.beginTransaction()
              .add(R.id.container_1, MyFragment.newInstance("A"), "frag_1")
              .add(R.id.container_2, MyFragment.newInstance("B"), "frag_2")
              .commit()
      }
      ```

      **Ключевое правило**: один экземпляр Fragment на контейнер. Никогда не переиспользуйте один объект.
    tags:
      - android_fragments
      - difficulty::easy

---
# Вопрос (RU)

> Как на экране одновременно отобразить два одинаковых `Fragment`?

# Question (EN)

> How to display two identical fragments on the screen at the same time?

---

## Ответ (RU)

Добавьте два независимых экземпляра одного и того же класса `Fragment` в разные контейнеры макета `Activity`. Класс и разметка могут быть одинаковыми, но каждый `Fragment` — это отдельный объект со своим состоянием. Нельзя добавлять один и тот же экземпляр `Fragment` (один и тот же объект) в несколько контейнеров — для каждого контейнера нужен свой экземпляр.

### Основной Подход

**1. Макет `Activity` с двумя контейнерами**

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

**2. `Fragment` с factory-методом**

```kotlin
class CounterFragment : Fragment() {
    private var count = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // В реальном коде восстанавливайте состояние здесь или в onViewStateRestored,
        // а не в onCreateView
        count = savedInstanceState?.getInt(KEY_COUNT, 0) ?: 0
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val title = arguments?.getString(ARG_TITLE) ?: "Counter"

        // Пример простого UI (важно вернуть View)
        return TextView(requireContext()).apply {
            text = "$title: $count"
        }
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

**3. Добавление в `Activity`**

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        if (savedInstanceState == null) {
            supportFragmentManager.beginTransaction()
                .add(
                    R.id.fragment_container_1,
                    CounterFragment.newInstance("Counter 1"),
                    "fragment_1"
                )
                .add(
                    R.id.fragment_container_2,
                    CounterFragment.newInstance("Counter 2"),
                    "fragment_2"
                )
                .commit()
        }
    }
}
```

### Ключевые Принципы

- Отдельный экземпляр на контейнер: один и тот же объект `Fragment` нельзя добавить в несколько контейнеров.
- Используйте уникальные теги (при необходимости): помогают идентифицировать экземпляры через FragmentManager.
- Проверяйте `savedInstanceState`: чтобы не создавать дубликаты при пересоздании `Activity`.
- Сохраняйте состояние по отдельности: каждый `Fragment` независимо сохраняет и восстанавливает своё состояние.
- Используйте factory-метод `newInstance()`: стандартный паттерн для передачи аргументов и создания отдельных экземпляров.

Анти-примеры:

- Не создавайте фрагменты повторно при каждом `onCreate()` без проверки `savedInstanceState`.
- Не используйте один тег для разных экземпляров.
- Не пытайтесь переиспользовать один и тот же объект `Fragment` для нескольких контейнеров.

---

## Answer (EN)

Add two independent instances of the same `Fragment` class to separate container views in the `Activity` layout. The class and layout can be identical, but each `Fragment` is a separate object with its own state. You cannot attach the same `Fragment` instance (same object) to multiple containers — each container must get its own instance.

### Basic Approach

**1. `Activity` Layout with Two Containers**

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

**2. `Fragment` with Factory Method**

```kotlin
class CounterFragment : Fragment() {
    private var count = 0

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        // In real code, restore state here or in onViewStateRestored,
        // not inside onCreateView
        count = savedInstanceState?.getInt(KEY_COUNT, 0) ?: 0
    }

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        val title = arguments?.getString(ARG_TITLE) ?: "Counter"

        // Simple example UI (must return a View)
        return TextView(requireContext()).apply {
            text = "$title: $count"
        }
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

**3. Adding to `Activity`**

```kotlin
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContentView(R.layout.activity_main)

        if (savedInstanceState == null) {
            supportFragmentManager.beginTransaction()
                .add(
                    R.id.fragment_container_1,
                    CounterFragment.newInstance("Counter 1"),
                    "fragment_1"
                )
                .add(
                    R.id.fragment_container_2,
                    CounterFragment.newInstance("Counter 2"),
                    "fragment_2"
                )
                .commit()
        }
    }
}
```

### Key Principles

- One instance per container: you cannot add the same `Fragment` object to multiple containers.
- Use unique tags (when needed): helpful for identifying instances via FragmentManager.
- Check `savedInstanceState`: to avoid creating duplicates on `Activity` recreation.
- Save state independently: each `Fragment` manages its own state separately.
- Use a `newInstance()` factory method: standard pattern for passing arguments and creating separate instances.

Anti-patterns:

- Don't recreate fragments on every `onCreate()` without checking `savedInstanceState`.
- Don't use the same tag for different instances.
- Don't try to reuse a single `Fragment` object for multiple containers.

---

## Дополнительные Вопросы (RU)

- Что произойдёт, если не проверять `savedInstanceState` перед добавлением фрагментов?
- Как фрагменты могут взаимодействовать друг с другом через родительскую `Activity`?
- В чём разница между `add()` и `replace()` в транзакциях фрагментов?
- Как обрабатывать изменения конфигурации при наличии нескольких экземпляров `Fragment`?
- Можно ли использовать один и тот же экземпляр `Fragment` в нескольких контейнерах?

## Follow-ups

- What happens if you don't check `savedInstanceState` before adding fragments?
- How can fragments communicate with each other through the parent `Activity`?
- What's the difference between `add()` and `replace()` for fragment transactions?
- How do you handle configuration changes with multiple fragment instances?
- Can you use the same `Fragment` instance in multiple containers?

## Ссылки (RU)

- [Документация по фрагментам (`Fragments`)](https://developer.android.com/guide/fragments)
- [API `FragmentTransaction`](https://developer.android.com/reference/androidx/fragment/app/FragmentTransaction)
- [Жизненный цикл `Fragment`](https://developer.android.com/guide/fragments/lifecycle)
- [Рекомендации по работе с `Fragments`](https://developer.android.com/guide/fragments/best-practices)

## References

- [Android `Fragments` Documentation](https://developer.android.com/guide/fragments)
- [FragmentTransaction API](https://developer.android.com/reference/androidx/fragment/app/FragmentTransaction)
- [`Fragment` Lifecycle](https://developer.android.com/guide/fragments/lifecycle)
- [Best Practices for `Fragments`](https://developer.android.com/guide/fragments/best-practices)

## Связанные Вопросы (RU)

### Предварительные Знания / Концепции

- [[c-fragments]]
- [[c-lifecycle]]

### Предварительные Вопросы (проще)

- [[q-fragment-basics--android--easy]] — основы `Fragment`
- [[q-how-to-choose-layout-for-fragment--android--easy]] — выбор разметки для `Fragment`

### Похожие Вопросы (тот Же уровень)

- [[q-how-to-implement-view-behavior-when-it-is-added-to-the-tree--android--easy]] — жизненный цикл `View`
- [[q-which-class-to-catch-gestures--android--easy]] — обработка касаний

### Продвинутые (сложнее)

- [[q-save-data-outside-fragment--android--medium]] — сохранение данных `Fragment`
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]] — назначение `Fragment`
- [[q-why-use-fragments-when-we-have-activities--android--medium]] — `Fragment` vs `Activity`

## Related Questions

### Prerequisites / Concepts

- [[c-fragments]]
- [[c-lifecycle]]

### Prerequisites (Easier)

- [[q-fragment-basics--android--easy]] - `Fragment` basics
- [[q-how-to-choose-layout-for-fragment--android--easy]] - `Fragment` layouts

### Related (Same Level)

- [[q-how-to-implement-view-behavior-when-it-is-added-to-the-tree--android--easy]] - `View` lifecycle
- [[q-which-class-to-catch-gestures--android--easy]] - Touch handling

### Advanced (Harder)

- [[q-save-data-outside-fragment--android--medium]] - `Fragment` data persistence
- [[q-what-are-fragments-for-if-there-is-activity--android--medium]] - `Fragment` use cases
- [[q-why-use-fragments-when-we-have-activities--android--medium]] - `Fragment` vs `Activity`
