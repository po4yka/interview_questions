---
id: android-182
title: "View Binding / Привязка View"
aliases: ["View Binding", "Привязка View"]

# Classification
topic: android
subtopics: [gradle, ui-views]
question_kind: android
difficulty: medium

# Language & provenance
original_language: en
language_tags: [en, ru]
sources: [https://developer.android.com/topic/libraries/view-binding]

# Workflow & relations
status: draft
moc: moc-android
related: [q-reduce-apk-size-techniques--android--medium, q-what-is-viewmodel--android--medium]

# Timestamps
created: 2025-10-15
updated: 2025-10-28

# Tags (EN only; no leading #)
tags: [android/gradle, android/ui-views, difficulty/medium, type-safety, view-binding]
date created: Saturday, November 1st 2025, 12:47:06 pm
date modified: Saturday, November 1st 2025, 5:43:31 pm
---

# Вопрос (RU)

Что вы знаете о View Binding?

# Question (EN)

What do you know about View Binding?

---

## Ответ (RU)

View Binding генерирует типобезопасные классы привязки для XML-макетов. Для каждого layout-файла создается класс с прямыми ссылками на все view с ID, заменяя `findViewById`.

### Настройка

```gradle
// ✅ Включить в build.gradle модуля
android {
    buildFeatures {
        viewBinding = true
    }
}
```

### Использование В Activity

```kotlin
private lateinit var binding: ResultProfileBinding

override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    binding = ResultProfileBinding.inflate(layoutInflater)
    setContentView(binding.root)

    binding.nameText.text = viewModel.name  // ✅ Типобезопасный доступ
}
```

### Использование Во Fragment

```kotlin
private var _binding: ResultProfileBinding? = null
private val binding get() = _binding!!

override fun onCreateView(
    inflater: LayoutInflater,
    container: ViewGroup?,
    savedInstanceState: Bundle?
): View {
    _binding = ResultProfileBinding.inflate(inflater, container, false)
    return binding.root
}

override fun onDestroyView() {
    super.onDestroyView()
    _binding = null  // ✅ Критично для предотвращения утечек
}
```

### Преимущества

**Null-безопасность**: View в определенных конфигурациях помечены `@Nullable`

**Типобезопасность**: Компилятор гарантирует соответствие типов

**Производительность**: Прямые ссылки вместо поиска по ID

### Генерация Классов

`result_profile.xml` → `ResultProfileBinding` (Pascal case + "Binding")

```xml
<LinearLayout>
    <TextView android:id="@+id/name" />        <!-- ✅ Будет в классе -->
    <ImageView android:cropToPadding="true" /> <!-- ❌ Без ID - пропущено -->
</LinearLayout>
```

## Answer (EN)

View Binding generates type-safe binding classes for XML layouts. Each layout file produces a class with direct references to all views with IDs, replacing `findViewById`.

### Setup

```gradle
// ✅ Enable in module build.gradle
android {
    buildFeatures {
        viewBinding = true
    }
}
```

### Activity Usage

```kotlin
private lateinit var binding: ResultProfileBinding

override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    binding = ResultProfileBinding.inflate(layoutInflater)
    setContentView(binding.root)

    binding.nameText.text = viewModel.name  // ✅ Type-safe access
}
```

### Fragment Usage

```kotlin
private var _binding: ResultProfileBinding? = null
private val binding get() = _binding!!

override fun onCreateView(
    inflater: LayoutInflater,
    container: ViewGroup?,
    savedInstanceState: Bundle?
): View {
    _binding = ResultProfileBinding.inflate(inflater, container, false)
    return binding.root
}

override fun onDestroyView() {
    super.onDestroyView()
    _binding = null  // ✅ Critical for preventing leaks
}
```

### Advantages

**Null safety**: Views in specific configurations marked `@Nullable`

**Type safety**: Compiler guarantees type matching

**Performance**: Direct references instead of ID lookups

### Class Generation

`result_profile.xml` → `ResultProfileBinding` (Pascal case + "Binding")

```xml
<LinearLayout>
    <TextView android:id="@+id/name" />        <!-- ✅ Included in class -->
    <ImageView android:cropToPadding="true" /> <!-- ❌ No ID - skipped -->
</LinearLayout>
```

---

## Follow-ups

- How does View Binding compare to Data Binding in terms of features and overhead?
- What happens if you forget to clean up binding in Fragment's onDestroyView?
- Can you selectively exclude layouts from View Binding generation?
- What are the memory implications of lateinit vs nullable binding patterns?
- How does View Binding handle include/merge tags?

## References

- [Official View Binding Guide](https://developer.android.com/topic/libraries/view-binding)
- [Migrating from findViewById](https://medium.com/androiddevelopers/use-view-binding-to-replace-findviewbyid-c83942471fc)

## Related Questions

### Prerequisites (Easier)
- [[q-recyclerview-sethasfixedsize--android--easy]] - View hierarchy optimization
- [[q-viewmodel-pattern--android--easy]] - Separation of concerns

### Related (Medium)
- [[q-what-is-viewmodel--android--medium]] - ViewModel integration
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - View rendering

### Advanced (Harder)
- [[q-compose-custom-layout--android--hard]] - Declarative UI alternative
