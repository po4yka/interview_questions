---
id: android-009
title: Fragment Basics / Основы Fragment
aliases: [Fragment Basics, Основы Fragment]
topic: android
status: reviewed
created: 2025-10-05
updated: 2025-10-28
difficulty: easy
question_kind: android
original_language: en
language_tags:
  - en
  - ru
subtopics:
  - fragment
  - lifecycle
  - ui-navigation
sources:
  - https://github.com/Kirchhoff-/Android-Interview-Questions/blob/master/Android/What%20is%20Fragment.md
tags: [android/fragment, android/lifecycle, android/ui-navigation, difficulty/easy, fragment, lifecycle, ui-component]
moc: moc-android
related:
  - q-android-build-optimization--android--medium
  - q-what-each-android-component-represents--android--easy
date created: Tuesday, October 28th 2025, 7:38:56 am
date modified: Tuesday, November 4th 2025, 11:46:09 am
---

# Вопрос (RU)
> Что такое Fragment в Android и для чего он используется?

# Question (EN)
> What is a Fragment in Android and what is it used for?

---

## Ответ (RU)

**Fragment** — это переиспользуемая часть пользовательского интерфейса в Android-приложении. Fragment определяет свой layout, имеет собственный жизненный цикл и обрабатывает события ввода независимо.

### Ключевые Характеристики

- Fragment не может существовать сам по себе — он должен быть размещен в Activity или другом Fragment
- Иерархия View фрагмента присоединяется к иерархии View хоста
- Fragment инкапсулирует View и логику для повторного использования

### Основные Способы Добавления

**1. Статическое добавление** — через XML-разметку:

```xml
<fragment
    android:id="@+id/music_fragment"
    android:name="com.example.app.MusicFragment"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

**2. Динамическое добавление** — через `FragmentManager`:

```kotlin
// ✅ Правильно: использование replace для замены фрагмента
supportFragmentManager.beginTransaction()
    .replace(R.id.container, ProfileFragment())
    .addToBackStack(null)  // добавить в back stack
    .commit()

// ❌ Неправильно: забыли commit()
supportFragmentManager.beginTransaction()
    .replace(R.id.container, ProfileFragment())
```

**Разница между `add()` и `replace()`:**
- `add()` — добавляет фрагмент поверх существующих (они остаются в памяти)
- `replace()` — удаляет предыдущие фрагменты из контейнера и добавляет новый

**3. Navigation Component** — современный подход для управления навигацией и транзакциями.

### Основные Сценарии Использования

1. **Модульность UI** — разделение экрана на переиспользуемые компоненты
2. **Адаптивный дизайн** — комбинирование фрагментов для планшетов, разделение для телефонов
3. **Динамическое изменение UI** — добавление, замена, удаление в runtime
4. **Back stack** — управление историей навигации

### Пример Простого Fragment

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

- Всегда предоставляйте конструктор без параметров
- Используйте ViewModel для связи с Activity вместо прямых ссылок
- Учитывайте жизненный цикл — view создаются и уничтожаются независимо от Fragment
- Избегайте глубокой вложенности фрагментов
- Для сложной навигации используйте Navigation Component

---

## Answer (EN)

A **Fragment** is a reusable portion of your app's UI in Android. A fragment defines its own layout, has its own lifecycle, and handles input events independently.

### Key Characteristics

- Fragments cannot exist on their own — they must be hosted by an activity or another fragment
- The fragment's view hierarchy attaches to the host's view hierarchy
- Fragments encapsulate views and logic for reusability

### Main Usage Methods

**1. Static addition** — via XML layout:

```xml
<fragment
    android:id="@+id/music_fragment"
    android:name="com.example.app.MusicFragment"
    android:layout_width="match_parent"
    android:layout_height="match_parent" />
```

**2. Dynamic addition** — via `FragmentManager`:

```kotlin
// ✅ Correct: using replace to swap fragment
supportFragmentManager.beginTransaction()
    .replace(R.id.container, ProfileFragment())
    .addToBackStack(null)  // add to back stack
    .commit()

// ❌ Wrong: forgot commit()
supportFragmentManager.beginTransaction()
    .replace(R.id.container, ProfileFragment())
```

**Difference between `add()` and `replace()`:**
- `add()` — adds fragment on top of existing ones (they remain in memory)
- `replace()` — removes previous fragments from container and adds new one

**3. Navigation Component** — modern approach for managing navigation and transactions.

### Main Use Cases

1. **UI Modularity** — dividing screen into reusable components
2. **Adaptive Design** — combining fragments for tablets, separating for phones
3. **Dynamic UI Changes** — adding, replacing, removing at runtime
4. **Back Stack** — managing navigation history

### Simple Fragment Example

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

- Always provide a no-argument constructor
- Use ViewModel for Activity communication instead of direct references
- Be lifecycle-aware — views are created and destroyed independently from Fragment
- Avoid deep fragment nesting
- Use Navigation Component for complex navigation

---

## Follow-ups

- What is the Fragment lifecycle and how does it relate to Activity lifecycle?
- How does FragmentManager handle back stack navigation?
- When should you use childFragmentManager vs parentFragmentManager?
- What are the differences between Fragment and Jetpack Compose navigation?
- How do you handle configuration changes in Fragments?

## References

- [Android Developer Docs: Fragments](https://developer.android.com/guide/fragments)
- [Android Developer Docs: Fragment Lifecycle](https://developer.android.com/guide/fragments/lifecycle)
- [Android Developer Docs: Navigation Component](https://developer.android.com/guide/navigation)

---

## Related Questions

### Prerequisites
- [[q-what-each-android-component-represents--android--easy]] - Understanding Android components

### Related
- [[q-how-to-choose-layout-for-fragment--android--easy]] - Fragment layouts and design
- Activity lifecycle and how it relates to Fragments

### Advanced
- [[q-save-data-outside-fragment--android--medium]] - Fragment data persistence
- [[q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium]] - Fragment lifecycle details
- [[q-can-state-loss-be-related-to-a-fragment--android--medium]] - Fragment state loss handling
- [[q-android-build-optimization--android--medium]] - Build optimization techniques
