---
id: 20251021-170000
title: Custom View Attributes / Атрибуты Custom View
aliases: [Custom View Attributes, Атрибуты Custom View]
topic: android
subtopics:
  - ui-theming
  - ui-views
question_kind: android
difficulty: medium
original_language: ru
language_tags:
  - en
  - ru
status: draft
moc: moc-android
related:
  - c-custom-views
  - q-custom-view-lifecycle--android--medium
created: 2025-10-21
updated: 2025-01-27
tags: [android/ui-theming, android/ui-views, difficulty/medium]
sources: [https://developer.android.com/guide/topics/ui/themes]
---
# Вопрос (RU)
> Как работают кастомные атрибуты в Custom View и как их правильно объявлять и считывать?

# Question (EN)
> How do custom attributes work in Custom Views, and how to properly declare and read them?

---

## Ответ (RU)

**Кастомные XML-атрибуты** позволяют настраивать Custom View прямо в XML-разметке. Android предоставляет **TypedArray** для типобезопасного чтения атрибутов с поддержкой стилей, тем и значений по умолчанию.

**Основные принципы**:
- **AttributeSet** содержит все XML-атрибуты
- **TypedArray** обеспечивает типобезопасный доступ к значениям
- **Стили и темы** поддерживают переиспользование конфигурации
- **Значения по умолчанию** обеспечивают fallback

### Объявление атрибутов

```xml
<!-- res/values/attrs.xml -->
<resources>
    <declare-styleable name="CustomProgressBar">
        <attr name="progress" format="float" />
        <attr name="progressColor" format="color" />
        <attr name="barHeight" format="dimension" />
        <!-- ✅ Группировка связанных атрибутов -->
    </declare-styleable>
</resources>
```

### Чтение атрибутов

```kotlin
class CustomProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    init {
        context.theme.obtainStyledAttributes(
            attrs, R.styleable.CustomProgressBar, defStyleAttr, 0
        ).apply {
            try {
                // ✅ Всегда указывайте значения по умолчанию
                val progress = getFloat(R.styleable.CustomProgressBar_progress, 0f)
                val color = getColor(R.styleable.CustomProgressBar_progressColor, Color.BLUE)
            } finally {
                recycle()  // ✅ ОБЯЗАТЕЛЬНО освобождайте ресурсы
            }
        }
    }
}
```

### Использование в XML

```xml
<CustomProgressBar
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:progress="75"
    app:progressColor="@color/primary"
    app:barHeight="12dp" />
```

### Ключевые моменты

**Типы атрибутов**:
- `color`, `dimension`, `string`, `boolean`, `integer`, `float`
- `reference` для ссылок на ресурсы
- `enum` для ограниченного набора значений
- `flags` для битовых масок

**Best practices**:
1. Всегда вызывайте `recycle()` на TypedArray
2. Указывайте значения по умолчанию
3. Используйте `enum` вместо magic numbers
4. Группируйте связанные атрибуты в одном `declare-styleable`

**Важные параметры конструктора**:
- `attrs` — набор XML-атрибутов
- `defStyleAttr` — атрибут темы со стилем по умолчанию
- `defStyleRes` — стиль по умолчанию

## Answer (EN)

**Custom XML attributes** enable configuring Custom Views directly in XML layouts. Android provides **TypedArray** for type-safe attribute reading with support for styles, themes, and default values.

**Key principles**:
- **AttributeSet** contains all XML attributes
- **TypedArray** provides type-safe value access
- **Styles and themes** enable configuration reuse
- **Default values** provide fallback behavior

### Declaring Attributes

```xml
<!-- res/values/attrs.xml -->
<resources>
    <declare-styleable name="CustomProgressBar">
        <attr name="progress" format="float" />
        <attr name="progressColor" format="color" />
        <attr name="barHeight" format="dimension" />
        <!-- ✅ Group related attributes -->
    </declare-styleable>
</resources>
```

### Reading Attributes

```kotlin
class CustomProgressBar @JvmOverloads constructor(
    context: Context,
    attrs: AttributeSet? = null,
    defStyleAttr: Int = 0
) : View(context, attrs, defStyleAttr) {

    init {
        context.theme.obtainStyledAttributes(
            attrs, R.styleable.CustomProgressBar, defStyleAttr, 0
        ).apply {
            try {
                // ✅ Always provide default values
                val progress = getFloat(R.styleable.CustomProgressBar_progress, 0f)
                val color = getColor(R.styleable.CustomProgressBar_progressColor, Color.BLUE)
            } finally {
                recycle()  // ✅ MUST release resources
            }
        }
    }
}
```

### XML Usage

```xml
<CustomProgressBar
    android:layout_width="match_parent"
    android:layout_height="wrap_content"
    app:progress="75"
    app:progressColor="@color/primary"
    app:barHeight="12dp" />
```

### Key Concepts

**Attribute formats**:
- `color`, `dimension`, `string`, `boolean`, `integer`, `float`
- `reference` for resource references
- `enum` for limited value sets
- `flags` for bit masks

**Best practices**:
1. Always call `recycle()` on TypedArray
2. Provide default values
3. Use `enum` instead of magic numbers
4. Group related attributes in one `declare-styleable`

**Constructor parameters**:
- `attrs` — set of XML attributes
- `defStyleAttr` — theme attribute with default style
- `defStyleRes` — default style resource

---

## Follow-ups

- How does attribute resolution work through style and theme hierarchy?
- What's the performance impact of TypedArray allocation and why must it be recycled?
- How to implement attribute validation for enum and flag types?
- When should you use defStyleAttr vs defStyleRes parameter?

## References

- [[c-custom-views]]
- https://developer.android.com/guide/topics/ui/custom-components
- https://developer.android.com/guide/topics/ui/themes

## Related Questions

### Prerequisites
- [[q-custom-view-lifecycle--android--medium]]

### Related
- Custom view state management
- Theme attribute resolution patterns

### Advanced
- Dynamic attribute updates during runtime
- Attribute animation and interpolation
