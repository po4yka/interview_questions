---
id: android-138
title: "How To Choose Layout For Fragment / Как выбрать layout для Fragment"
aliases: ["How To Choose Layout For Fragment", "Как выбрать layout для Fragment"]
topic: android
subtopics: [fragment, ui-views]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-fragment-basics--android--easy, q-why-user-data-may-disappear-on-screen-rotation--android--hard]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android/fragment, android/ui-views, difficulty/easy]
date created: Monday, October 27th 2025, 3:47:26 pm
date modified: Saturday, November 1st 2025, 5:43:35 pm
---

# Вопрос (RU)

Каким образом ты выбираешь layout для Fragment?

# Question (EN)

How do you choose a layout for a Fragment?

## Ответ (RU)

В Android фрагментах выбор layout выполняется в методе **onCreateView()** с использованием **LayoutInflater**. Это основной способ преобразования XML-разметки в View объекты.

### Основные Подходы

**1. XML Inflation**

```kotlin
override fun onCreateView(
    inflater: LayoutInflater,
    container: ViewGroup?,
    savedInstanceState: Bundle?
): View {
    // ✅ attachToRoot = false для фрагментов
    return inflater.inflate(R.layout.fragment_example, container, false)
}
```

**Ключевые параметры:**
- `inflater` — предоставляется системой
- `container` — родительская ViewGroup
- `attachToRoot` — **обязательно false** (FragmentManager сам управляет добавлением)

**2. View Binding** (рекомендуется)

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

Используйте **resource qualifiers** (layout-land, layout-sw600dp) вместо runtime проверок:

```kotlin
// ❌ Плохо — проверка во время выполнения
val layoutId = if (resources.getBoolean(R.bool.is_tablet)) {
    R.layout.fragment_tablet
} else {
    R.layout.fragment_phone
}

// ✅ Хорошо — resource qualifiers
// layout/fragment_example.xml
// layout-sw600dp/fragment_example.xml
return inflater.inflate(R.layout.fragment_example, container, false)
```

### Типичные Ошибки

```kotlin
// ❌ attachToRoot = true вызовет IllegalStateException
return inflater.inflate(R.layout.fragment, container, true)

// ❌ Утечка памяти через binding
private val binding: FragmentExampleBinding? = null

// ✅ Правильная очистка
override fun onDestroyView() {
    super.onDestroyView()
    _binding = null
}
```

## Answer (EN)

In Android fragments, layout selection is performed in the **onCreateView()** method using **LayoutInflater**. This is the primary way to inflate XML layouts into View objects.

### Main Approaches

**1. XML Inflation**

```kotlin
override fun onCreateView(
    inflater: LayoutInflater,
    container: ViewGroup?,
    savedInstanceState: Bundle?
): View {
    // ✅ attachToRoot = false for fragments
    return inflater.inflate(R.layout.fragment_example, container, false)
}
```

**Key parameters:**
- `inflater` — provided by the system
- `container` — parent ViewGroup
- `attachToRoot` — **must be false** (FragmentManager handles attachment)

**2. View Binding** (recommended)

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

Use **resource qualifiers** (layout-land, layout-sw600dp) instead of runtime checks:

```kotlin
// ❌ Bad — runtime check
val layoutId = if (resources.getBoolean(R.bool.is_tablet)) {
    R.layout.fragment_tablet
} else {
    R.layout.fragment_phone
}

// ✅ Good — resource qualifiers
// layout/fragment_example.xml
// layout-sw600dp/fragment_example.xml
return inflater.inflate(R.layout.fragment_example, container, false)
```

### Common Mistakes

```kotlin
// ❌ attachToRoot = true will throw IllegalStateException
return inflater.inflate(R.layout.fragment, container, true)

// ❌ Memory leak via binding
private val binding: FragmentExampleBinding? = null

// ✅ Proper cleanup
override fun onDestroyView() {
    super.onDestroyView()
    _binding = null
}
```

---

## Follow-ups

- Why must `attachToRoot` be false for fragments?
- What happens if you don't clean up View Binding references in `onDestroyView()`?
- When should you prefer Jetpack Compose over traditional XML layouts?
- How do resource qualifiers work for different screen sizes and orientations?

## References

- Official Android documentation: Fragment lifecycle
- Official Android documentation: View Binding
- Official Android documentation: LayoutInflater API reference

## Related Questions

### Prerequisites
- [[q-fragment-basics--android--easy|Fragment Basics]]

### Related
- [[q-why-user-data-may-disappear-on-screen-rotation--android--hard|Why User Data May Disappear on Screen Rotation]]

### Advanced
- Advanced fragment transaction management
- Fragment result API and communication patterns
