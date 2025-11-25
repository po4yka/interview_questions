---
id: android-009
title: Fragment Basics / Основы Fragment
aliases: [Fragment Basics, Основы Fragment]
topic: android
status: draft
created: 2025-10-05
updated: 2025-11-10
difficulty: easy
question_kind: android
original_language: en
language_tags:
  - en
  - ru
subtopics:
  - fragment
  - ui-navigation
sources:
  - "https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20is%20Fragment.md"
tags: [android/fragment, android/ui-navigation, difficulty/easy, ui-component]
moc: moc-android
related:
  - c-compose-navigation
  - c-fragments
  - q-android-build-optimization--android--medium
  - q-how-to-choose-layout-for-fragment--android--easy
  - q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium
  - q-save-data-outside-fragment--android--medium
  - q-what-each-android-component-represents--android--easy

date created: Saturday, November 1st 2025, 12:46:50 pm
date modified: Tuesday, November 25th 2025, 8:54:00 pm
---

# Вопрос (RU)
> Что такое `Fragment` в Android и для чего он используется?

# Question (EN)
> What is a `Fragment` in Android and what is it used for?

---

## Ответ (RU)

**`Fragment`** — это переиспользуемая часть пользовательского интерфейса и логики поведения в Android-приложении. `Fragment` определяет свой layout (если он есть), имеет собственный жизненный цикл и может обрабатывать события ввода.

### Ключевые Характеристики

- `Fragment` не может существовать сам по себе — он должен быть присоединен к `FragmentManager`, связанного с `Activity` или родительским `Fragment` (host)
- Иерархия `View` фрагмента присоединяется к иерархии `View` хоста (если фрагмент отображает UI)
- `Fragment` инкапсулирует `View` и связанную с ними логику для повторного использования

### Основные Способы Добавления

**1. Статическое добавление (устаревающий подход для `View`-based UI)** — через XML-разметку с использованием тега `<fragment>`:

```xml
<fragment
    android:id="@+id/music_fragment"
    android:name="com.example.app.MusicFragment"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

На практике сейчас чаще используется `FragmentContainerView` и/или Navigation Component.

**2. Динамическое добавление** — через `FragmentManager`:

```kotlin
// ✅ Правильно: использование replace для замены фрагмента в контейнере
supportFragmentManager.beginTransaction()
    .replace(R.id.container, ProfileFragment())
    .addToBackStack(null)  // добавить в back stack (опционально)
    .commit()

// ❌ Неправильно: забыли commit()
supportFragmentManager.beginTransaction()
    .replace(R.id.container, ProfileFragment())
```

**Разница между `add()` и `replace()`:**
- `add()` — добавляет новый фрагмент в указанный контейнер. Уже добавленные фрагменты в этом контейнере не удаляются автоматически; результат ("поверх" или нет) зависит от разметки и контейнеров
- `replace()` — удаляет (detach/remove) существующие фрагменты из указанного контейнера и добавляет новый

**3. Navigation Component** — современный подход для управления навигацией между фрагментами и экранами через `NavHostFragment` / `FragmentContainerView`, при котором навигация описывается в графе, а framework сам выполняет соответствующие транзакции.

### Основные Сценарии Использования

1. **Модульность UI** — разделение экрана на переиспользуемые компоненты
2. **Адаптивный дизайн** — комбинирование фрагментов для планшетов, разделение для телефонов
3. **Динамическое изменение UI** — добавление, замена, удаление во время выполнения
4. **Back stack** — управление историей навигации (через `FragmentManager` или Navigation Component)

### Пример Простого `Fragment`

```kotlin
class ProfileFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return inflater.inflate(R.layout.fragment_profile, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // ✅ Правильно: настройка UI после создания view
        setupViews(view)
    }
}
```

### Лучшие Практики

- Всегда предоставляйте конструктор без параметров: система должна иметь возможность пересоздать `Fragment`; данные передавайте через `arguments` (`newInstance`-фабричные методы), а не через нестандартные конструкторы
- Используйте `ViewModel` для связи с `Activity`/другими фрагментами вместо прямых жёстких ссылок
- Учитывайте жизненный цикл: экземпляр `Fragment` может переживать свою `View`; создавайте/очищайте `View` в `onCreateView`/`onDestroyView`, не держите утечки контекста или ссылок на `View`
- Избегайте глубокой вложенности фрагментов
- Для сложной навигации используйте Navigation Component поверх `NavHostFragment` / `FragmentContainerView`

---

## Answer (EN)

A **`Fragment`** is a reusable portion of UI and behavior in an Android app. A fragment defines its own layout (if it has UI), has its own lifecycle, and can handle input events.

### Key Characteristics

- A fragment cannot exist completely on its own — it must be attached to a `FragmentManager` associated with a host activity or parent fragment
- The fragment's view hierarchy is attached to the host view hierarchy (if the fragment displays UI)
- Fragments encapsulate views and related logic for reusability

### Main Usage Methods

**1. Static addition (legacy style for `View`-based UI)** — via XML layout using the `<fragment>` tag:

```xml
<fragment
    android:id="@+id/music_fragment"
    android:name="com.example.app.MusicFragment"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

In modern projects, `FragmentContainerView` and/or Navigation Component are generally preferred.

**2. Dynamic addition** — via `FragmentManager`:

```kotlin
// ✅ Correct: using replace to swap fragment in the container
supportFragmentManager.beginTransaction()
    .replace(R.id.container, ProfileFragment())
    .addToBackStack(null)  // add to back stack (optional)
    .commit()

// ❌ Wrong: forgot commit()
supportFragmentManager.beginTransaction()
    .replace(R.id.container, ProfileFragment())
```

**Difference between `add()` and `replace()`:**
- `add()` — adds a new fragment into the specified container. Existing fragments in that container are not automatically removed; whether it visually appears "on top" depends on your layout/containers
- `replace()` — removes (detach/remove) existing fragments from the specified container and adds the new one

**3. Navigation Component** — a modern approach for managing navigation between fragments and screens via `NavHostFragment` / `FragmentContainerView`, where navigation is defined in a graph and the framework performs the underlying fragment transactions.

### Main Use Cases

1. **UI Modularity** — dividing screens into reusable components
2. **Adaptive Design** — combining fragments for tablets, separating for phones
3. **Dynamic UI Changes** — adding, replacing, removing at runtime
4. **Back stack** — managing navigation history (via `FragmentManager` or Navigation Component)

### Simple `Fragment` Example

```kotlin
class ProfileFragment : Fragment() {
    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        return inflater.inflate(R.layout.fragment_profile, container, false)
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        // ✅ Correct: set up UI after view creation
        setupViews(view)
    }
}
```

### Best Practices

- Always provide a no-argument constructor so the system can recreate the fragment; pass data via `arguments` (`newInstance` factory methods) instead of custom constructors
- Use `ViewModel` for communication with the `Activity`/other fragments instead of holding strong direct references
- Be lifecycle-aware: the `Fragment` instance may outlive its view hierarchy; create/clean up views in `onCreateView`/`onDestroyView` and avoid leaking `Context` or `View` references
- Avoid deep fragment nesting
- Use Navigation Component with `NavHostFragment` / `FragmentContainerView` for complex navigation

---

## Follow-ups

- What is the `Fragment` lifecycle and how does it relate to `Activity` lifecycle?
- How does FragmentManager handle back stack navigation?
- When should you use childFragmentManager vs parentFragmentManager?
- What are the differences between `Fragment` and Jetpack Compose navigation?
- How do you handle configuration changes in Fragments?

## References

- [Android Developer Docs: Fragments](https://developer.android.com/guide/fragments)
- [Android Developer Docs: `Fragment` Lifecycle](https://developer.android.com/guide/fragments/lifecycle)
- [Android Developer Docs: Navigation Component](https://developer.android.com/guide/navigation)

---

## Related Questions

### Prerequisites / Concepts

- [[c-compose-navigation]]
- [[c-fragments]]

### Prerequisites
- [[q-what-each-android-component-represents--android--easy]] - Understanding Android components

### Related
- [[q-how-to-choose-layout-for-fragment--android--easy]] - `Fragment` layouts and design
- `Activity` lifecycle and how it relates to Fragments

### Advanced
- [[q-save-data-outside-fragment--android--medium]] - `Fragment` data persistence
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - `Fragment` lifecycle details
- [[q-can-state-loss-be-related-to-a-fragment--android--medium]] - `Fragment` state loss handling
- [[q-android-build-optimization--android--medium]] - Build optimization techniques
