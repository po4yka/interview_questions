---
id: android-460
title: Factory Pattern Android / Паттерн Factory в Android
aliases: [Abstract Factory Pattern, Factory Method Pattern, Factory Pattern Android, Паттерн Factory в Android]
topic: android
subtopics:
  - architecture-clean
  - ui-views
question_kind: android
difficulty: medium
original_language: en
language_tags:
  - en
  - ru
sources:
  - https://developer.android.com/guide/topics/ui/declaring-layout
status: reviewed
moc: moc-android
related:
created: 2025-10-20
updated: 2025-11-03
tags: [android/architecture-clean, android/ui-views, design-patterns, difficulty/medium, factory-pattern, layout-inflater]
---

# Вопрос (RU)
> Можешь привести пример когда Android фреймворк использует паттерн Factory?

# Question (EN)
> Can you give an example of when the Android framework uses the Factory pattern?

---

## Ответ (RU)

Android фреймворк широко использует Factory паттерн. Основные примеры: **`LayoutInflater`** (создает Views из XML), **`Fragment.instantiate()`** (создает фрагменты), **`Intent.createChooser()`** (создает chooser dialogs), **`MediaPlayer.create()`** (создает pre-configured media players).

### Ключевые Примеры

**1. `LayoutInflater` - Factory Method Pattern**

`LayoutInflater` создает `View` объекты из XML деклараций без прямых вызовов конструкторов:

```kotlin
// ✅ Factory method создает Views из XML
val inflater = LayoutInflater.from(context)
val view = inflater.inflate(R.layout.activity_main, parent, false)

// Внутри: <TextView> → TextView(context, attrs)
//         <Button> → Button(context, attrs)
//         <RecyclerView> → RecyclerView(context, attrs)
```

Упрощенная реализация:

```kotlin
private fun createViewFromTag(name: String, ctx: Context, attrs: AttributeSet): View = when (name) {
    "TextView" -> TextView(ctx, attrs)
    "Button" -> Button(ctx, attrs)
    "ImageView" -> ImageView(ctx, attrs)
    else -> Class.forName(name)
        .getConstructor(Context::class.java, AttributeSet::class.java)
        .newInstance(ctx, attrs) as View
}
```

**2. `MediaPlayer.create()` - Static Factory Method**

Создает pre-configured MediaPlayer:

```kotlin
// ✅ Factory method с автоматической подготовкой
val mediaPlayer = MediaPlayer.create(context, R.raw.audio_file)
mediaPlayer.start() // готов к использованию

// ❌ Без factory требует ручной настройки
val mediaPlayer = MediaPlayer()
mediaPlayer.setDataSource(context, uri)
mediaPlayer.prepare() // дополнительный шаг
```

**3. `Intent.createChooser()` - Static Factory Method**

Создает `Intent` для выбора приложения:

```kotlin
val shareIntent = Intent(Intent.ACTION_SEND).apply {
    type = "text/plain"
    putExtra(Intent.EXTRA_TEXT, "Share this")
}
val chooser = Intent.createChooser(shareIntent, "Choose app")
startActivity(chooser)
```

### Custom Factory Implementation

Пример для `RecyclerView`:

```kotlin
class ViewHolderFactory {
    fun createViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        return when (viewType) {
            TYPE_TEXT -> TextViewHolder(
                LayoutInflater.from(parent.context).inflate(R.layout.item_text, parent, false)
            )
            TYPE_IMAGE -> ImageViewHolder(
                LayoutInflater.from(parent.context).inflate(R.layout.item_image, parent, false)
            )
            else -> throw IllegalArgumentException("Unknown viewType: $viewType")
        }
    }
}
```

### Преимущества Factory Pattern В Android

- **Декларативность**: XML описывает UI, factory создает объекты
- **Расширяемость**: легко добавлять новые типы Views/Fragments
- **Инкапсуляция**: скрывает сложность создания (reflection, инициализация)
- **Консистентность**: единообразный API для создания объектов

### Лучшие Практики
- Оборачивайте сложное создание в статические фабрики (`create()`)
- Возвращайте интерфейсы/абстракции, а не конкретные реализации
- Кэшируйте дорогие объекты внутри фабрик при необходимости
- Для `Fragment` используйте аргументы через `newInstance()`

### Типичные Ошибки
- Протаскивание `Context` повсюду вместо явной зависимости
- Отсутствие валидизации входов в фабрике
- "Божественная" фабрика с избыточной ответственностью

## Answer (EN)

Android framework extensively uses Factory pattern. Main examples: **`LayoutInflater`** (creates Views from XML), **`Fragment.instantiate()`** (creates fragments), **`Intent.createChooser()`** (creates chooser dialogs), **`MediaPlayer.create()`** (creates pre-configured media players).

### Key Examples

**1. `LayoutInflater` - Factory Method Pattern**

`LayoutInflater` creates `View` objects from XML declarations without direct constructor calls:

```kotlin
// ✅ Factory method creates Views from XML
val inflater = LayoutInflater.from(context)
val view = inflater.inflate(R.layout.activity_main, parent, false)

// Internally: <TextView> → TextView(context, attrs)
//             <Button> → Button(context, attrs)
//             <RecyclerView> → RecyclerView(context, attrs)
```

Simplified implementation:

```kotlin
private fun createViewFromTag(name: String, ctx: Context, attrs: AttributeSet): View = when (name) {
    "TextView" -> TextView(ctx, attrs)
    "Button" -> Button(ctx, attrs)
    "ImageView" -> ImageView(ctx, attrs)
    else -> Class.forName(name)
        .getConstructor(Context::class.java, AttributeSet::class.java)
        .newInstance(ctx, attrs) as View
}
```

**2. `MediaPlayer.create()` - Static Factory Method**

Creates pre-configured MediaPlayer:

```kotlin
// ✅ Factory method with automatic preparation
val mediaPlayer = MediaPlayer.create(context, R.raw.audio_file)
mediaPlayer.start() // ready to use

// ❌ Without factory requires manual setup
val mediaPlayer = MediaPlayer()
mediaPlayer.setDataSource(context, uri)
mediaPlayer.prepare() // additional step
```

**3. `Intent.createChooser()` - Static Factory Method**

Creates `Intent` for app selection:

```kotlin
val shareIntent = Intent(Intent.ACTION_SEND).apply {
    type = "text/plain"
    putExtra(Intent.EXTRA_TEXT, "Share this")
}
val chooser = Intent.createChooser(shareIntent, "Choose app")
startActivity(chooser)
```

### Custom Factory Implementation

Example for `RecyclerView`:

```kotlin
class ViewHolderFactory {
    fun createViewHolder(parent: ViewGroup, viewType: Int): RecyclerView.ViewHolder {
        return when (viewType) {
            TYPE_TEXT -> TextViewHolder(
                LayoutInflater.from(parent.context).inflate(R.layout.item_text, parent, false)
            )
            TYPE_IMAGE -> ImageViewHolder(
                LayoutInflater.from(parent.context).inflate(R.layout.item_image, parent, false)
            )
            else -> throw IllegalArgumentException("Unknown viewType: $viewType")
        }
    }
}
```

### Factory Pattern Benefits in Android

- **Declarative**: XML describes UI, factory creates objects
- **Extensible**: easy to add new `View`/`Fragment` types
- **Encapsulation**: hides creation complexity (reflection, initialization)
- **Consistency**: uniform API for object creation

### Best Practices
- Hide complex construction behind static factories (`create()`)
- Return interfaces/abstractions, not concrete types
- Cache expensive objects inside factories when appropriate
- For `Fragment` use `newInstance()` with `arguments`

### Common Pitfalls
- Passing `Context` everywhere instead of explicit dependency
- Missing input validation inside factory
- "God" factory doing too much

---

## Follow-ups

- What's the difference between Factory Method and Abstract Factory patterns?
- When to use Factory pattern vs Builder pattern (AlertDialog.Builder)?
- How does FragmentFactory work in modern Android?
- How to implement thread-safe Factory for singletons?

## References

- [[c-software-design-patterns]]
- https://developer.android.com/guide/topics/ui/declaring-layout
- https://developer.android.com/guide/fragments/fragmentmanager#factory

## Related Questions

### Prerequisites (Easier)

### Related (Same Level)
- [[q-usecase-pattern-android--android--medium]]
