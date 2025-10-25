---
id: 20251020-200500
title: Factory Pattern Android / Паттерн Factory в Android
aliases: [Factory Pattern Android, Паттерн Factory в Android]
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
source: https://developer.android.com/guide/topics/ui/declaring-layout
source_note: Android layout inflation documentation
status: draft
moc: moc-android
related:
  - q-android-architecture-patterns--architecture-patterns--medium
  - q-fragment-lifecycle--android--medium
  - q-view-lifecycle--android--medium
created: 2025-10-20
updated: 2025-10-20
tags: [android/architecture-clean, android/ui-views, design-patterns, difficulty/medium, factory-pattern, layout-inflater]
date created: Saturday, October 25th 2025, 1:26:30 pm
date modified: Saturday, October 25th 2025, 4:52:03 pm
---

# Вопрос (RU)
> Можешь привести пример когда Android фреймворк использует паттерн Factory?

# Question (EN)
> Can you give an example of when the Android framework uses the Factory pattern?

---
## Ответ (RU)

Android фреймворк широко использует Factory паттерн в своих API. Основные примеры: LayoutInflater, Fragment.instantiate(), Intent.createChooser(), MediaPlayer.create().

### Основные Примеры

**1. LayoutInflater (Factory Method Pattern)**
- Проблема: создание View объектов из XML без прямого вызова конструкторов
- Результат: декларативное создание UI, поддержка custom views
- Решение: factory method создает View по XML тегам

```kotlin
// Factory method создает View объекты
val inflater = LayoutInflater.from(context)
val view = inflater.inflate(R.layout.custom_layout, parent, false)

// Внутри LayoutInflater использует reflection и factory methods
// для создания соответствующих View подклассов по XML тегам:
// <TextView> → new TextView(context)
// <Button> → new Button(context)
// <RecyclerView> → new RecyclerView(context)
```

```kotlin
// Упрощенная реализация LayoutInflater
class LayoutInflater {
    fun inflate(resource: Int, parent: ViewGroup?, attachToRoot: Boolean): View {
        val parser = resources.getLayout(resource)
        return createViewFromTag(parser.name, context, attrs)
    }

    private fun createViewFromTag(name: String, context: Context, attrs: AttributeSet): View {
        // Factory pattern: создает разные типы View
        return when (name) {
            "TextView" -> TextView(context, attrs)
            "Button" -> Button(context, attrs)
            "ImageView" -> ImageView(context, attrs)
            "LinearLayout" -> LinearLayout(context, attrs)
            else -> Class.forName(name).getConstructor(Context::class.java, AttributeSet::class.java)
                .newInstance(context, attrs) as View
        }
    }
}
```

**2. Fragment.instantiate() (Factory Pattern)**
- Проблема: создание Fragment без прямого вызова конструкторов
- Результат: поддержка аргументов, восстановление состояния
- Решение: factory method с Bundle аргументами

```kotlin
// Factory method для создания fragments
val fragment = Fragment.instantiate(context, MyFragment::class.java.name)

// С аргументами
val args = Bundle().apply {
    putString("key", "value")
}
val fragment = Fragment.instantiate(context, MyFragment::class.java.name, args)
```

**3. Intent.createChooser() (Factory Pattern)**
- Проблема: создание Intent для выбора приложения
- Результат: унифицированный интерфейс для share/chooser
- Решение: factory method создает настроенный Intent

```kotlin
// Factory method для создания chooser Intent
val shareIntent = Intent(Intent.ACTION_SEND).apply {
    type = "text/plain"
    putExtra(Intent.EXTRA_TEXT, "Share this text")
}

val chooserIntent = Intent.createChooser(shareIntent, "Choose app")
startActivity(chooserIntent)
```

**4. MediaPlayer.create() (Factory Pattern)**
- Проблема: создание MediaPlayer с предварительной настройкой
- Результат: упрощенное создание media объектов
- Решение: factory method с автоматической настройкой

```kotlin
// Factory method для создания MediaPlayer
val mediaPlayer = MediaPlayer.create(context, R.raw.audio_file)
mediaPlayer.start() // Готов к использованию

// Альтернативно без factory
val mediaPlayer = MediaPlayer()
mediaPlayer.setDataSource(context, Uri.parse("file://..."))
mediaPlayer.prepare() // Требует ручной подготовки
```

### Теория Factory Pattern

**Factory Method Pattern:**
- Создает объекты без указания точного класса
- Инкапсулирует логику создания объектов
- Позволяет подклассам изменять тип создаваемых объектов
- Упрощает добавление новых типов продуктов

**Abstract Factory Pattern:**
- Создает семейства связанных объектов
- Обеспечивает совместимость объектов
- Изолирует конкретные классы от клиента
- Легко расширяется новыми семействами

**Builder Pattern (связанный):**
- Пошаговое создание сложных объектов
- Разделение процесса создания и представления
- Переиспользование кода для различных представлений
- Валидация параметров перед созданием

**Android Framework Benefits:**
- **Декларативность**: XML описывает структуру, factory создает объекты
- **Расширяемость**: легко добавлять новые View типы
- **Инкапсуляция**: скрывает сложность создания объектов
- **Консистентность**: единообразный интерфейс создания

**Implementation Patterns:**
- **Static Factory Methods**: MediaPlayer.create(), Intent.createChooser()
- **Instance Factory Methods**: LayoutInflater.inflate()
- **Builder Pattern**: AlertDialog.Builder, Notification.Builder
- **Reflection-based**: LayoutInflater для custom views

**Best Practices:**
- Использовать factory methods для сложных объектов
- Предпочитать composition над inheritance
- Обеспечивать thread safety в factory methods
- Документировать создаваемые типы объектов

### Custom Factory Implementation

**View Factory для RecyclerView:**
```kotlin
class ViewTypeFactory {
    fun createView(parent: ViewGroup, viewType: Int): View {
        return when (viewType) {
            TYPE_TEXT -> LayoutInflater.from(parent.context)
                .inflate(R.layout.item_text, parent, false)
            TYPE_IMAGE -> LayoutInflater.from(parent.context)
                .inflate(R.layout.item_image, parent, false)
            TYPE_CUSTOM -> CustomView(parent.context)
            else -> throw IllegalArgumentException("Unknown view type: $viewType")
        }
    }
}
```

**Fragment Factory:**
```kotlin
class FragmentFactory {
    fun createFragment(type: String, args: Bundle? = null): Fragment {
        return when (type) {
            "profile" -> ProfileFragment().apply { arguments = args }
            "settings" -> SettingsFragment().apply { arguments = args }
            "about" -> AboutFragment().apply { arguments = args }
            else -> throw IllegalArgumentException("Unknown fragment type: $type")
        }
    }
}
```

## Answer (EN)

Android framework extensively uses Factory pattern in its APIs. Main examples: LayoutInflater, Fragment.instantiate(), Intent.createChooser(), MediaPlayer.create().

### Key Examples

**1. LayoutInflater (Factory Method Pattern)**
- Problem: creating View objects from XML without direct constructor calls
- Result: declarative UI creation, custom view support
- Solution: factory method creates View by XML tags

```kotlin
// Factory method creates View objects
val inflater = LayoutInflater.from(context)
val view = inflater.inflate(R.layout.custom_layout, parent, false)

// LayoutInflater uses reflection and factory methods
// to create appropriate View subclasses based on XML tags:
// <TextView> → new TextView(context)
// <Button> → new Button(context)
// <RecyclerView> → new RecyclerView(context)
```

```kotlin
// Simplified LayoutInflater implementation
class LayoutInflater {
    fun inflate(resource: Int, parent: ViewGroup?, attachToRoot: Boolean): View {
        val parser = resources.getLayout(resource)
        return createViewFromTag(parser.name, context, attrs)
    }

    private fun createViewFromTag(name: String, context: Context, attrs: AttributeSet): View {
        // Factory pattern: creates different View types
        return when (name) {
            "TextView" -> TextView(context, attrs)
            "Button" -> Button(context, attrs)
            "ImageView" -> ImageView(context, attrs)
            "LinearLayout" -> LinearLayout(context, attrs)
            else -> Class.forName(name).getConstructor(Context::class.java, AttributeSet::class.java)
                .newInstance(context, attrs) as View
        }
    }
}
```

**2. Fragment.instantiate() (Factory Pattern)**
- Problem: creating Fragment without direct constructor calls
- Result: argument support, state restoration
- Solution: factory method with Bundle arguments

```kotlin
// Factory method for creating fragments
val fragment = Fragment.instantiate(context, MyFragment::class.java.name)

// With arguments
val args = Bundle().apply {
    putString("key", "value")
}
val fragment = Fragment.instantiate(context, MyFragment::class.java.name, args)
```

**3. Intent.createChooser() (Factory Pattern)**
- Problem: creating Intent for app selection
- Result: unified interface for share/chooser
- Solution: factory method creates configured Intent

```kotlin
// Factory method for creating chooser Intent
val shareIntent = Intent(Intent.ACTION_SEND).apply {
    type = "text/plain"
    putExtra(Intent.EXTRA_TEXT, "Share this text")
}

val chooserIntent = Intent.createChooser(shareIntent, "Choose app")
startActivity(chooserIntent)
```

**4. MediaPlayer.create() (Factory Pattern)**
- Problem: creating MediaPlayer with pre-configuration
- Result: simplified media object creation
- Solution: factory method with automatic setup

```kotlin
// Factory method for creating MediaPlayer
val mediaPlayer = MediaPlayer.create(context, R.raw.audio_file)
mediaPlayer.start() // Ready to use

// Alternative without factory
val mediaPlayer = MediaPlayer()
mediaPlayer.setDataSource(context, Uri.parse("file://..."))
mediaPlayer.prepare() // Requires manual preparation
```

### Factory Pattern Theory

**Factory Method Pattern:**
- Creates objects without specifying exact class
- Encapsulates object creation logic
- Allows subclasses to change type of created objects
- Simplifies adding new product types

**Abstract Factory Pattern:**
- Creates families of related objects
- Ensures object compatibility
- Isolates concrete classes from client
- Easy to extend with new families

**Builder Pattern (related):**
- Step-by-step creation of complex objects
- Separates construction and representation
- Reuses code for different representations
- Validates parameters before creation

**Android Framework Benefits:**
- **Declarative**: XML describes structure, factory creates objects
- **Extensible**: easy to add new View types
- **Encapsulation**: hides object creation complexity
- **Consistency**: uniform creation interface

**Implementation Patterns:**
- **Static Factory Methods**: MediaPlayer.create(), Intent.createChooser()
- **Instance Factory Methods**: LayoutInflater.inflate()
- **Builder Pattern**: AlertDialog.Builder, Notification.Builder
- **Reflection-based**: LayoutInflater for custom views

**Best Practices:**
- Use factory methods for complex objects
- Prefer composition over inheritance
- Ensure thread safety in factory methods
- Document created object types

### Custom Factory Implementation

**View Factory for RecyclerView:**
```kotlin
class ViewTypeFactory {
    fun createView(parent: ViewGroup, viewType: Int): View {
        return when (viewType) {
            TYPE_TEXT -> LayoutInflater.from(parent.context)
                .inflate(R.layout.item_text, parent, false)
            TYPE_IMAGE -> LayoutInflater.from(parent.context)
                .inflate(R.layout.item_image, parent, false)
            TYPE_CUSTOM -> CustomView(parent.context)
            else -> throw IllegalArgumentException("Unknown view type: $viewType")
        }
    }
}
```

**Fragment Factory:**
```kotlin
class FragmentFactory {
    fun createFragment(type: String, args: Bundle? = null): Fragment {
        return when (type) {
            "profile" -> ProfileFragment().apply { arguments = args }
            "settings" -> SettingsFragment().apply { arguments = args }
            "about" -> AboutFragment().apply { arguments = args }
            else -> throw IllegalArgumentException("Unknown fragment type: $type")
        }
    }
}
```

**See also:** c-factory-pattern, [[c-software-design-patterns]]


## Follow-ups
- What's the difference between Factory Method and Abstract Factory patterns?
- How to implement Builder pattern in Android?
- When to use Factory vs Dependency Injection?
