---
id: android-182
title: View Binding / Привязка View
aliases: [View Binding, Привязка View]
topic: android
subtopics:
  - ui-views
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
sources:
  - "https://developer.android.com/topic/libraries/view-binding"
status: draft
moc: moc-android
related:
  - c-gradle
  - q-reduce-apk-size-techniques--android--medium
  - q-what-is-a-view-and-what-is-responsible-for-its-visual-part--android--medium
  - q-what-is-data-binding--android--easy
  - q-what-is-known-about-methods-that-redraw-view--android--medium
  - q-what-is-viewmodel--android--medium
created: 2025-10-15
updated: 2025-11-10
tags: [android/ui-views, difficulty/medium, view-binding]

date created: Saturday, November 1st 2025, 12:47:06 pm
date modified: Tuesday, November 25th 2025, 8:53:56 pm
---

# Вопрос (RU)

> Что вы знаете о `View` Binding?

# Question (EN)

> What do you know about `View` Binding?

---

## Ответ (RU)

`View` Binding генерирует типобезопасные классы привязки для XML-макетов. Для каждого layout-файла создается класс с прямыми ссылками на все view с ID, заменяя рутинные вызовы `findViewById` и устраняя большую часть связанных с ними ошибок.

### Настройка

```gradle
// ✅ Включить в build.gradle модуля
android {
    buildFeatures {
        viewBinding = true
    }
}
```

### Использование В `Activity`

```kotlin
private lateinit var binding: ResultProfileBinding

override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    binding = ResultProfileBinding.inflate(layoutInflater)
    setContentView(binding.root)

    binding.nameText.text = viewModel.name  // ✅ Типобезопасный доступ
}
```

### Использование Во `Fragment`

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

Binding во `Fragment` считается валидным только между `onCreateView` и `onDestroyView`; за пределами этого диапазона к нему обращаться нельзя.

### Преимущества

- **Null-безопасность**: Генерируемый класс учитывает разные конфигурации layout'ов и помечает view как nullable, если они не гарантированно присутствуют во всех вариантах.
- **Типобезопасность**: Компилятор гарантирует соответствие типов вместо ручных кастов при `findViewById`.
- **Упрощение и снижение количества ошибок**: Меньше boilerplate-кода, исключаются опечатки в ID и неправильные приведения типов.

(Замечание: выигрыш по производительности минимален; преимущество в основном в безопасности и удобстве, а не в существенном ускорении исполнения.)

### Генерация Классов

`result_profile.xml` → `ResultProfileBinding` (PascalCase имени файла + "Binding")

```xml
<LinearLayout>
    <TextView android:id="@+id/name" />        <!-- ✅ Будет в классе -->
    <ImageView android:cropToPadding="true" /> <!-- ❌ Без ID - пропущено -->
</LinearLayout>
```

Классы `View` Binding генерируются для обычных layout-файлов; элементы без `id` не попадают в класс. Отдельные layout'ы можно исключить из генерации с помощью `tools:viewBindingIgnore="true"`.

## Answer (EN)

`View` Binding generates type-safe binding classes for XML layouts. Each layout file produces a class with direct references to all views with IDs, replacing repetitive `findViewById` calls and eliminating most related errors.

### Setup

```gradle
// ✅ Enable in module build.gradle
android {
    buildFeatures {
        viewBinding = true
    }
}
```

### `Activity` Usage

```kotlin
private lateinit var binding: ResultProfileBinding

override fun onCreate(savedInstanceState: Bundle?) {
    super.onCreate(savedInstanceState)
    binding = ResultProfileBinding.inflate(layoutInflater)
    setContentView(binding.root)

    binding.nameText.text = viewModel.name  // ✅ Type-safe access
}
```

### `Fragment` Usage

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

The `Fragment` binding is only valid between `onCreateView` and `onDestroyView`; accessing it outside this range is incorrect.

### Advantages

- **Null safety**: The generated class reflects different layout configurations and marks views as nullable if they are not guaranteed to exist in all variants.
- **Type safety**: The compiler enforces correct types, avoiding manual casts from `findViewById`.
- **Reduced boilerplate and fewer bugs**: Less manual code, no ID string typos or invalid casts.

(Note: Any performance gain is minor; the main benefits are safety and convenience, not significant runtime speed improvements.)

### Class Generation

`result_profile.xml` → `ResultProfileBinding` (PascalCase of file name + "Binding")

```xml
<LinearLayout>
    <TextView android:id="@+id/name" />        <!-- ✅ Included in class -->
    <ImageView android:cropToPadding="true" /> <!-- ❌ No ID - skipped -->
</LinearLayout>
```

`View` Binding classes are generated for regular layout files; elements without an `id` are not exposed. You can opt out individual layouts from generation using `tools:viewBindingIgnore="true"`.

---

## Дополнительные Вопросы (RU)

- Как `View` Binding сравнивается с Data Binding по возможностям и накладным расходам?
- Что произойдет, если забыть очистить binding в `onDestroyView` `Fragment`?
- Можно ли выборочно исключать layout-файлы из генерации `View` Binding?
- Каковы особенности использования `lateinit` против nullable-подхода для binding с точки зрения памяти?
- Как `View` Binding обрабатывает теги include/merge?

## Follow-ups

- How does `View` Binding compare to Data Binding in terms of features and overhead?
- What happens if you forget to clean up binding in `Fragment`'s onDestroyView?
- Can you selectively exclude layouts from `View` Binding generation?
- What are the memory implications of lateinit vs nullable binding patterns?
- How does `View` Binding handle include/merge tags?

## Ссылки (RU)

- [Официальное руководство по `View` Binding](https://developer.android.com/topic/libraries/view-binding)
- [Миграция с findViewById](https://medium.com/androiddevelopers/use-view-binding-to-replace-findviewbyid-c83942471fc)

## References

- [Official `View` Binding Guide](https://developer.android.com/topic/libraries/view-binding)
- [Migrating from findViewById](https://medium.com/androiddevelopers/use-view-binding-to-replace-findviewbyid-c83942471fc)

## Связанные Вопросы (RU)

### Предварительные Знания / Концепции

- [[c-gradle]]

### Предварительные (проще)

- [[q-recyclerview-sethasfixedsize--android--easy]] - Оптимизация иерархии `View`
- [[q-viewmodel-pattern--android--easy]] - Разделение ответственности

### Связанные (средней сложности)

- [[q-what-is-viewmodel--android--medium]] - Интеграция с `ViewModel`
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - Перерисовка `View`

### Продвинутые (сложнее)

- [[q-compose-custom-layout--android--hard]] - Декларативная альтернатива UI

## Related Questions

### Prerequisites / Concepts

- [[c-gradle]]

### Prerequisites (Easier)

- [[q-recyclerview-sethasfixedsize--android--easy]] - `View` hierarchy optimization
- [[q-viewmodel-pattern--android--easy]] - Separation of concerns

### Related (Medium)

- [[q-what-is-viewmodel--android--medium]] - `ViewModel` integration
- [[q-what-is-known-about-methods-that-redraw-view--android--medium]] - `View` rendering

### Advanced (Harder)

- [[q-compose-custom-layout--android--hard]] - Declarative UI alternative
