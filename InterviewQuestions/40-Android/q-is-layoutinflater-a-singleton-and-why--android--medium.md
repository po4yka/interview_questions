---
id: android-118
title: Is LayoutInflater A Singleton And Why / Является ли LayoutInflater синглтоном и почему
aliases: [Is LayoutInflater A Singleton And Why, Является ли LayoutInflater синглтоном и почему]
topic: android
subtopics: [architecture-mvvm, ui-views]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-dagger-build-time-optimization--android--medium, q-data-sync-unstable-network--android--hard, q-home-screen-widgets--android--medium, q-singleton-scope-binding--android--medium, q-what-design-systems-in-android-have-you-worked-with--android--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [android, android/architecture-mvvm, android/ui-views, context, difficulty/medium, system-services]
anki_cards:
  - slug: android-118-0-en
    front: "Is LayoutInflater a singleton and why?"
    back: |
      **No**, LayoutInflater is **not a singleton**.

      **Each Context has its own instance:**
      - Different theme/configuration per Context
      - `LayoutInflater.from(context)` returns context-bound instance

      **Why not singleton:**
      - Theme affects inflated views
      - Activity context != Application context
      - Cloning creates new instance for different factory

      ```kotlin
      val inflater = LayoutInflater.from(context) // Context-specific
      ```
    tags:
      - android_views
      - difficulty::medium
  - slug: android-118-0-ru
    front: "Является ли LayoutInflater синглтоном и почему?"
    back: |
      **Нет**, LayoutInflater **не является синглтоном**.

      **У каждого Context свой экземпляр:**
      - Разная тема/конфигурация для каждого Context
      - `LayoutInflater.from(context)` возвращает экземпляр, привязанный к контексту

      **Почему не синглтон:**
      - Тема влияет на инфлейтящиеся view
      - Activity context != Application context
      - Клонирование создаёт новый экземпляр для другой фабрики

      ```kotlin
      val inflater = LayoutInflater.from(context) // Привязан к контексту
      ```
    tags:
      - android_views
      - difficulty::medium

---
# Вопрос (RU)

> Является ли LayoutInflater синглтоном и почему?

# Question (EN)

> Is LayoutInflater a singleton and why?

---

## Ответ (RU)

Нет, **LayoutInflater не является глобальным синглтоном**. Вместо этого используемые в фреймворке реализации `Context` (например, `Activity`, `ContextThemeWrapper`) обычно кэшируют свой экземпляр `LayoutInflater`, полученный через `getSystemService()`. То есть это «синглтон в пределах конкретного `Context`/темы», а не один глобальный объект на все приложение.

### Ключевые Моменты

**Не глобальный синглтон**
- Разные `Context` (разные `Activity`, `Application`, разные обёртки `ContextThemeWrapper`) имеют разные экземпляры `LayoutInflater`.
- Каждый `LayoutInflater` привязан к своему `Context` и его теме; менять контекст «на лету» нельзя.

**Кэшируется на уровне реализации `Context`**
- `LayoutInflater.from(context)` и `getSystemService(LAYOUT_INFLATER_SERVICE)` возвращают один и тот же экземпляр для данной реализации `Context`, которая его кэширует.
- На практике, например `ContextThemeWrapper`/`Activity` хранят `LayoutInflater` и переиспользуют его; это деталь реализации, но важно понимать, что повторные вызовы не создают новый объект каждый раз.

**Безопасен для повторного использования**
- `LayoutInflater` не хранит изменяемое состояние, зависящее от конкретных вызовов `inflate()` (нет накопления состояния между инфляциями), хотя содержит конфигурацию: `Context`, тему, фабрику и пр.
- Поэтому один и тот же экземпляр можно безопасно использовать для множественных инфляций в рамках того же `Context`/темы.

### Пример: Один Экземпляр На `Context`

```kotlin
val inflater1 = getSystemService(Context.LAYOUT_INFLATER_SERVICE) as LayoutInflater
val inflater2 = LayoutInflater.from(this)
println(inflater1 === inflater2) // true - тот же экземпляр для данного Activity

val activityInflater = LayoutInflater.from(this)
val appInflater = LayoutInflater.from(applicationContext)
println(activityInflater === appInflater) // false - разные Context -> разные экземпляры
```

### Замечания По Практике

```kotlin
// Хорошо: передать inflater в конструктор (явная зависимость, удобно для тестирования)
class MyAdapter(
    private val inflater: LayoutInflater
) : RecyclerView.Adapter<ViewHolder>() {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = inflater.inflate(R.layout.item, parent, false)
        return ViewHolder(view)
    }
}

// Тоже допустимо: получать inflater при необходимости — вызов дешёвый и кэшированный
class OkAdapter : RecyclerView.Adapter<ViewHolder>() {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val inflater = LayoutInflater.from(parent.context) // вернётся кэшированный экземпляр
        return ViewHolder(inflater.inflate(R.layout.item, parent, false))
    }
}
```

## Answer (EN)

No, **LayoutInflater is not a global singleton**. Instead, framework `Context` implementations (such as `Activity`, `ContextThemeWrapper`) typically cache their own `LayoutInflater` instance obtained via `getSystemService()`. This behaves like a "singleton within a given `Context`/theme" rather than a single global object for the whole app.

### Key Points

**Not a global singleton**
- Different `Context`s (different `Activity` instances, `Application`, different `ContextThemeWrapper`s) have different `LayoutInflater` instances.
- Each `LayoutInflater` is bound to its `Context` and theme; you cannot switch its context on the fly.

**Cached at `Context` implementation level**
- `LayoutInflater.from(context)` and `getSystemService(LAYOUT_INFLATER_SERVICE)` return the same instance for a given `Context` implementation that caches it.
- In practice, e.g. `ContextThemeWrapper`/`Activity` store and reuse their `LayoutInflater`; this is an implementation detail, but it means repeated calls are cheap and do not create new instances each time.

**Safe to reuse**
- `LayoutInflater` does not keep mutable, per-`inflate()` call state between inflations (though it holds configuration such as `Context`, theme, factory, etc.).
- Therefore, reusing the same `LayoutInflater` for multiple inflations within the same `Context`/theme is safe.

### Example: One Instance per `Context`

```kotlin
val inflater1 = getSystemService(Context.LAYOUT_INFLATER_SERVICE) as LayoutInflater
val inflater2 = LayoutInflater.from(this)
println(inflater1 === inflater2) // true - same instance for this Activity

val activityInflater = LayoutInflater.from(this)
val appInflater = LayoutInflater.from(applicationContext)
println(activityInflater === appInflater) // false - different Contexts -> different instances
```

### Practical Notes

```kotlin
// GOOD: inject inflater via constructor (explicit dependency, convenient for testing)
class MyAdapter(
    private val inflater: LayoutInflater
) : RecyclerView.Adapter<ViewHolder>() {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = inflater.inflate(R.layout.item, parent, false)
        return ViewHolder(view)
    }
}

// ALSO FINE: obtain inflater when needed — call is cheap and returns cached instance
class OkAdapter : RecyclerView.Adapter<ViewHolder>() {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val inflater = LayoutInflater.from(parent.context) // cached instance for this Context
        return ViewHolder(inflater.inflate(R.layout.item, parent, false))
    }
}
```

---

## Дополнительные Вопросы (RU)

- Каковы последствия для производительности при многократном создании экземпляров `LayoutInflater`?
- Как `LayoutInflater` обрабатывает кастомные вью и атрибуты?
- Когда стоит использовать контекст `Activity` против контекста `Application` для `LayoutInflater`?
- Как `View Binding` соотносится с прямой инфляцией layout-файлов?

## Follow-ups

- What are the performance implications of creating LayoutInflater instances repeatedly?
- How does LayoutInflater handle custom views and attributes?
- When should you use `Activity` context vs `Application` context for LayoutInflater?
- How does `View` Binding compare to direct inflation?

## Ссылки (RU)

- Android Developer Documentation: System Services and `Context`

## References

- Android Developer Documentation: System Services and `Context`

## Related Questions

### Prerequisites / Concepts

### Prerequisites
- [[q-viewmodel-pattern--android--easy]]

### Related
- [[q-home-screen-widgets--android--medium]]
- [[q-what-design-systems-in-android-have-you-worked-with--android--medium]]

### Advanced
- [[q-compose-custom-layout--android--hard]]
