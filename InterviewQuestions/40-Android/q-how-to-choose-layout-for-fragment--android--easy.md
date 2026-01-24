---
id: android-138
title: How To Choose Layout For Fragment / Как выбрать layout для Fragment
aliases:
- How To Choose Layout For Fragment
- Как выбрать layout для Fragment
topic: android
subtopics:
- fragment
- ui-views
question_kind: theory
difficulty: easy
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-fragments
- q-fragment-basics--android--easy
- q-is-fragment-lifecycle-connected-to-activity-or-independent--android--medium
- q-save-data-outside-fragment--android--medium
- q-what-is-layout-types-and-when-to-use--android--easy
- q-why-user-data-may-disappear-on-screen-rotation--android--hard
created: 2025-10-15
updated: 2025-11-10
sources: []
tags:
- android/fragment
- android/ui-views
- difficulty/easy
anki_cards:
- slug: android-138-0-en
  language: en
  anki_id: 1768378882671
  synced_at: '2026-01-23T16:45:05.335099'
- slug: android-138-0-ru
  language: ru
  anki_id: 1768378882694
  synced_at: '2026-01-23T16:45:05.337264'
---
# Вопрос (RU)

> Каким образом ты выбираешь layout для `Fragment`?

# Question (EN)

> How do you choose a layout for a `Fragment`?

## Ответ (RU)

В Android фрагментах выбор и подключение layout обычно выполняется в методе **onCreateView()** с использованием **LayoutInflater**. Это основной способ преобразования XML-разметки в `View`-объекты для конкретного фрагмента.

### Основные Подходы

**1. XML Inflation**

```kotlin
override fun onCreateView(
    inflater: LayoutInflater,
    container: ViewGroup?,
    savedInstanceState: Bundle?
): View {
    // ✅ attachToRoot = false для фрагментов
    // FragmentManager сам добавит корневой View во "fragment container"
    return inflater.inflate(R.layout.fragment_example, container, false)
}
```

**Ключевые параметры:**
- `inflater` — предоставляется системой
- `container` — предполагаемый родительский `ViewGroup` (например, `FrameLayout` в активности)
- `attachToRoot` — для фрагментов должен быть `false`, т.к. добавлением во view hierarchy занимается FragmentManager; установка `true` приведёт к попытке двойного добавления и `IllegalStateException` во время выполнения.

**2. `View` Binding** (рекомендуется)

```kotlin
private var _binding: FragmentExampleBinding? = null
private val binding get() = _binding!!

override fun onCreateView(
    inflater: LayoutInflater,
    container: ViewGroup?,
    savedInstanceState: Bundle?
): View {
    _binding = FragmentExampleBinding.inflate(inflater, container, false)
    return binding.root
}

override fun onDestroyView() {
    super.onDestroyView()
    _binding = null  // ✅ Предотвращение утечек памяти
}
```

**3. Jetpack Compose**

```kotlin
override fun onCreateView(
    inflater: LayoutInflater,
    container: ViewGroup?,
    savedInstanceState: Bundle?
): View {
    return ComposeView(requireContext()).apply {
        setContent {
            MaterialTheme {
                MyScreen()
            }
        }
    }
}
```

### Условный Выбор Layout

Основной выбор layout (телефон/планшет, портрет/ландшафт) делайте через **resource qualifiers** (`layout-land`, `layout-sw600dp` и т.д.), а не через проверки во время выполнения, чтобы система сама подбирала нужный ресурс по одному и тому же `layoutId`.

```kotlin
// ❌ Плохо — логика выбора layout во время выполнения
val layoutId = if (resources.getBoolean(R.bool.is_tablet)) {
    R.layout.fragment_tablet
} else {
    R.layout.fragment_phone
}

// ✅ Хорошо — один идентификатор, разные файлы по resource qualifiers
// layout/fragment_example.xml
// layout-sw600dp/fragment_example.xml
return inflater.inflate(R.layout.fragment_example, container, false)
```

### Типичные Ошибки

```kotlin
// ❌ attachToRoot = true приводит к двойному добавлению View и IllegalStateException
return inflater.inflate(R.layout.fragment, container, true)

// ❌ Утечка памяти через binding — хранение ссылки, не обнуляемой по уничтожению View
lateinit var binding: FragmentExampleBinding

override fun onCreateView(
    inflater: LayoutInflater,
    container: ViewGroup?,
    savedInstanceState: Bundle?
): View {
    binding = FragmentExampleBinding.inflate(inflater, container, false)
    return binding.root
}

// ✅ Правильная очистка с отдельным nullable-хранилищем
private var _binding: FragmentExampleBinding? = null
private val safeBinding get() = _binding!!

override fun onCreateView(
    inflater: LayoutInflater,
    container: ViewGroup?,
    savedInstanceState: Bundle?
): View {
    _binding = FragmentExampleBinding.inflate(inflater, container, false)
    return safeBinding.root
}

override fun onDestroyView() {
    super.onDestroyView()
    _binding = null
}
```

## Answer (EN)

In Android fragments, choosing and attaching a layout is typically done in the **onCreateView()** method using **LayoutInflater**. This is the primary way to inflate XML into `View` objects for that fragment.

### Main Approaches

**1. XML Inflation**

```kotlin
override fun onCreateView(
    inflater: LayoutInflater,
    container: ViewGroup?,
    savedInstanceState: Bundle?
): View {
    // ✅ attachToRoot = false for fragments
    // FragmentManager will attach the root view to the container
    return inflater.inflate(R.layout.fragment_example, container, false)
}
```

**Key parameters:**
- `inflater` — provided by the system
- `container` — the expected parent `ViewGroup` (e.g., the `FrameLayout` in the `Activity`)
- `attachToRoot` — for fragments should be `false` because FragmentManager handles adding the view to the hierarchy; passing `true` causes double attachment and an `IllegalStateException` at runtime.

**2. `View` Binding** (recommended)

```kotlin
private var _binding: FragmentExampleBinding? = null
private val binding get() = _binding!!

override fun onCreateView(
    inflater: LayoutInflater,
    container: ViewGroup?,
    savedInstanceState: Bundle?
): View {
    _binding = FragmentExampleBinding.inflate(inflater, container, false)
    return binding.root
}

override fun onDestroyView() {
    super.onDestroyView()
    _binding = null  // ✅ Prevent memory leaks
}
```

**3. Jetpack Compose**

```kotlin
override fun onCreateView(
    inflater: LayoutInflater,
    container: ViewGroup?,
    savedInstanceState: Bundle?
): View {
    return ComposeView(requireContext()).apply {
        setContent {
            MaterialTheme {
                MyScreen()
            }
        }
    }
}
```

### Conditional Layout Selection

Prefer **resource qualifiers** (`layout-land`, `layout-sw600dp`, etc.) over runtime checks so the system selects the appropriate layout variant for a single `layoutId`.

```kotlin
// ❌ Bad — choosing layout at runtime with manual logic
val layoutId = if (resources.getBoolean(R.bool.is_tablet)) {
    R.layout.fragment_tablet
} else {
    R.layout.fragment_phone
}

// ✅ Good — single ID, multiple files via resource qualifiers
// layout/fragment_example.xml
// layout-sw600dp/fragment_example.xml
return inflater.inflate(R.layout.fragment_example, container, false)
```

### Common Mistakes

```kotlin
// ❌ attachToRoot = true leads to double-adding the view and IllegalStateException
return inflater.inflate(R.layout.fragment, container, true)

// ❌ Memory leak via binding — keeping a long-lived reference that is never cleared
lateinit var binding: FragmentExampleBinding

override fun onCreateView(
    inflater: LayoutInflater,
    container: ViewGroup?,
    savedInstanceState: Bundle?
): View {
    binding = FragmentExampleBinding.inflate(inflater, container, false)
    return binding.root
}

// ✅ Proper cleanup with nullable backing field
private var _binding: FragmentExampleBinding? = null
private val safeBinding get() = _binding!!

override fun onCreateView(
    inflater: LayoutInflater,
    container: ViewGroup?,
    savedInstanceState: Bundle?
): View {
    _binding = FragmentExampleBinding.inflate(inflater, container, false)
    return safeBinding.root
}

override fun onDestroyView() {
    super.onDestroyView()
    _binding = null
}
```

---

## Follow-ups

- Why must `attachToRoot` be false for fragments?
- What happens if you don't clean up `View` Binding references in `onDestroyView()`?
- When should you prefer Jetpack Compose over traditional XML layouts?
- How do resource qualifiers work for different screen sizes and orientations?

## References

- Official Android documentation: `Fragment` lifecycle
- Official Android documentation: `View` Binding
- Official Android documentation: LayoutInflater API reference

## Related Questions

### Prerequisites / Concepts

- [[c-fragments]]

### Prerequisites

- [[q-fragment-basics--android--easy|`Fragment` Basics]]

### Related

- [[q-why-user-data-may-disappear-on-screen-rotation--android--hard|Why User Data May Disappear on Screen Rotation]]

### Advanced

- Advanced fragment transaction management
- `Fragment` result API and communication patterns
