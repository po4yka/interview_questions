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
original_language: ru
language_tags:
- en
- ru
sources:
- "https://developer.android.com/guide/topics/ui/declaring-layout"
status: draft
moc: moc-android
related:
- c-design-patterns
- q-usecase-pattern-android--android--medium
created: 2025-10-20
updated: 2025-10-20
tags: [android/architecture-clean, android/ui-views, design-patterns, difficulty/medium, factory-pattern, layout-inflater]

---

# Вопрос (RU)
> Можешь привести пример когда Android фреймворк использует паттерн Factory?

# Question (EN)
> Can you give an example of when the Android framework uses the Factory pattern?

---

## Ответ (RU)

Android фреймворк широко использует Factory / Factory Method паттерн. Основные примеры: **`LayoutInflater`** (создает Views из XML), **`Fragment.instantiate()` / `FragmentFactory`** (создают фрагменты), **`Intent.createChooser()`** (создает Intent-обертку для chooser UI), **`MediaPlayer.create()`** (создает pre-configured media players).

См. также: [[c-android-basics]]

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

**2. `Fragment.instantiate()` / `FragmentFactory` - Factory Method**

Фреймворк создает экземпляры `Fragment` через фабричные методы, не требуя прямых вызовов конструкторов в клиентском коде:

```kotlin
// Пример использования FragmentFactory (современный подход)
class CustomFragmentFactory : FragmentFactory() {
    override fun instantiate(classLoader: ClassLoader, className: String): Fragment {
        return when (className) {
            MyFragment::class.java.name -> MyFragment(dependency)
            else -> super.instantiate(classLoader, className)
        }
    }
}

// Регистрация фабрики
supportFragmentManager.fragmentFactory = CustomFragmentFactory()
```

В собственных фрагментах часто используют статический фабричный метод `newInstance(...)` с `arguments` вместо прямого вызова конструктора:

```kotlin
class DetailsFragment : Fragment() {

    companion object {
        fun newInstance(id: Long): DetailsFragment = DetailsFragment().apply {
            arguments = bundleOf("id" to id)
        }
    }
}
```

**3. `MediaPlayer.create()` - Static Factory Method**

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

**4. `Intent.createChooser()` - Static Factory Method**

Создает специальный chooser `Intent` для выбора приложения (chooser UI будет показан при передаче этого Intent в `startActivity()`):

```kotlin
val shareIntent = Intent(Intent.ACTION_SEND).apply {
    type = "text/plain"
    putExtra(Intent.EXTRA_TEXT, "Share this")
}
val chooser = Intent.createChooser(shareIntent, "Choose app")
startActivity(chooser)
```

### Custom Factory Implementation

Пример для RecyclerView (viewType — это константы адаптера, например `TYPE_TEXT = 1`, `TYPE_IMAGE = 2`):

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
- Оборачивайте сложное создание в статические фабрики (`create()` / `newInstance()`), особенно для компонентов фреймворка
- Возвращайте интерфейсы/абстракции, а не конкретные реализации
- Кэшируйте дорогие объекты внутри фабрик при необходимости
- Для `Fragment` используйте фабричные методы (`newInstance()` или `FragmentFactory`) вместо публичных конструкторов с параметрами

### Типичные Ошибки
- Протаскивание `Context` повсюду вместо явной зависимости
- Отсутствие валидизации входов в фабрике
- "Божественная" фабрика с избыточной ответственностью

## Answer (EN)

Android framework extensively uses Factory / Factory Method pattern. Main examples: **`LayoutInflater`** (creates Views from XML), **`Fragment.instantiate()` / `FragmentFactory`** (create fragments), **`Intent.createChooser()`** (creates a chooser Intent that triggers chooser UI), **`MediaPlayer.create()`** (creates pre-configured media players).

See also: [[c-android-basics]]

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

**2. `Fragment.instantiate()` / `FragmentFactory` - Factory Method**

The framework creates `Fragment` instances via factory methods instead of clients directly invoking constructors in most cases:

```kotlin
// Example using FragmentFactory (modern approach)
class CustomFragmentFactory : FragmentFactory() {
    override fun instantiate(classLoader: ClassLoader, className: String): Fragment {
        return when (className) {
            MyFragment::class.java.name -> MyFragment(dependency)
            else -> super.instantiate(classLoader, className)
        }
    }
}

// Register the factory
supportFragmentManager.fragmentFactory = CustomFragmentFactory()
```

In your own fragments, a common pattern is to expose a static factory method `newInstance(...)` that configures `arguments` instead of using public constructors with parameters:

```kotlin
class DetailsFragment : Fragment() {

    companion object {
        fun newInstance(id: Long): DetailsFragment = DetailsFragment().apply {
            arguments = bundleOf("id" to id)
        }
    }
}
```

**3. `MediaPlayer.create()` - Static Factory Method**

Creates a pre-configured MediaPlayer:

```kotlin
// ✅ Factory method with automatic preparation
val mediaPlayer = MediaPlayer.create(context, R.raw.audio_file)
mediaPlayer.start() // ready to use

// ❌ Without factory requires manual setup
val mediaPlayer = MediaPlayer()
mediaPlayer.setDataSource(context, uri)
mediaPlayer.prepare() // additional step
```

**4. `Intent.createChooser()` - Static Factory Method**

Creates a special chooser `Intent` used for app selection (chooser UI is shown when this Intent is passed to `startActivity()`):

```kotlin
val shareIntent = Intent(Intent.ACTION_SEND).apply {
    type = "text/plain"
    putExtra(Intent.EXTRA_TEXT, "Share this")
}
val chooser = Intent.createChooser(shareIntent, "Choose app")
startActivity(chooser)
```

### Custom Factory Implementation

Example for RecyclerView (viewType here refers to adapter-defined constants like `TYPE_TEXT = 1`, `TYPE_IMAGE = 2`):

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
- Hide complex construction behind static factories (`create()` / `newInstance()`), especially for framework components
- Return interfaces/abstractions, not concrete types
- Cache expensive objects inside factories when appropriate
- For `Fragment`, prefer factory methods (`newInstance()` or `FragmentFactory`) over public constructors with parameters

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

- https://developer.android.com/guide/topics/ui/declaring-layout
- https://developer.android.com/guide/fragments/fragmentmanager#factory

## Related Questions

### Prerequisites (Easier)

### Related (Same Level)
- [[q-usecase-pattern-android--android--medium]]
