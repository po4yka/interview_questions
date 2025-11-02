---
id: android-118
title: "Is LayoutInflater A Singleton And Why / Является ли LayoutInflater синглтоном и почему"
aliases: ["Is LayoutInflater A Singleton And Why", "Является ли LayoutInflater синглтоном и почему"]
topic: android
subtopics: [ui-views, architecture-mvvm]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-home-screen-widgets--android--medium, q-what-design-systems-in-android-have-you-worked-with--android--medium]
created: 2025-10-15
updated: 2025-01-27
tags: [android, android/ui-views, android/architecture-mvvm, difficulty/medium, context, system-services]
sources: []
date created: Monday, October 27th 2025, 3:32:43 pm
date modified: Thursday, October 30th 2025, 3:10:59 pm
---

# Вопрос (RU)

> Является ли LayoutInflater синглтоном и почему?

# Question (EN)

> Is LayoutInflater a singleton and why?

---

## Ответ (RU)

Нет, **LayoutInflater не является глобальным синглтоном**. Каждый Context кэширует свой экземпляр LayoutInflater, полученный через `getSystemService()`. Это паттерн «синглтон в пределах области видимости» (scope-bound singleton).

### Ключевые моменты

**Не глобальный синглтон**
- Разные Context (Activity, Application) имеют разные экземпляры LayoutInflater
- Каждый LayoutInflater привязан к своему Context и его теме

**Кэшируется в Context**
- `LayoutInflater.from(context)` и `getSystemService(LAYOUT_INFLATER_SERVICE)` возвращают один экземпляр для данного Context
- Внутренне Context хранит `mLayoutInflater` и переиспользует его

**Stateless для inflate операций**
- LayoutInflater не сохраняет состояние между вызовами `inflate()`
- Безопасно переиспользовать для множественных инфляций

### Пример: один экземпляр на Context

```kotlin
val inflater1 = getSystemService(Context.LAYOUT_INFLATER_SERVICE) as LayoutInflater
val inflater2 = LayoutInflater.from(this)
println(inflater1 === inflater2) // ✅ true - тот же экземпляр

val activityInflater = LayoutInflater.from(this)
val appInflater = LayoutInflater.from(applicationContext)
println(activityInflater === appInflater) // ❌ false - разные Context
```

### Лучшие практики

```kotlin
// ✅ ХОРОШО: передать в конструктор
class MyAdapter(
    private val inflater: LayoutInflater
) : RecyclerView.Adapter<ViewHolder>() {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = inflater.inflate(R.layout.item, parent, false)
        return ViewHolder(view)
    }
}

// ❌ ПЛОХО: вызывать from() каждый раз (хотя вернется кэшированный)
class BadAdapter : RecyclerView.Adapter<ViewHolder>() {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val inflater = LayoutInflater.from(parent.context) // ненужный повторный вызов
        return ViewHolder(inflater.inflate(R.layout.item, parent, false))
    }
}
```

## Answer (EN)

No, **LayoutInflater is not a global singleton**. Each Context caches its own LayoutInflater instance obtained via `getSystemService()`. This is a scope-bound singleton pattern.

### Key points

**Not a global singleton**
- Different Contexts (Activity, Application) have different LayoutInflater instances
- Each LayoutInflater is bound to its Context and theme

**Cached in Context**
- `LayoutInflater.from(context)` and `getSystemService(LAYOUT_INFLATER_SERVICE)` return the same instance for a given Context
- Internally, Context stores `mLayoutInflater` and reuses it

**Stateless for inflate operations**
- LayoutInflater doesn't preserve state between `inflate()` calls
- Safe to reuse for multiple inflations

### Example: one instance per Context

```kotlin
val inflater1 = getSystemService(Context.LAYOUT_INFLATER_SERVICE) as LayoutInflater
val inflater2 = LayoutInflater.from(this)
println(inflater1 === inflater2) // ✅ true - same instance

val activityInflater = LayoutInflater.from(this)
val appInflater = LayoutInflater.from(applicationContext)
println(activityInflater === appInflater) // ❌ false - different Contexts
```

### Best practices

```kotlin
// ✅ GOOD: pass in constructor
class MyAdapter(
    private val inflater: LayoutInflater
) : RecyclerView.Adapter<ViewHolder>() {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val view = inflater.inflate(R.layout.item, parent, false)
        return ViewHolder(view)
    }
}

// ❌ BAD: call from() every time (though returns cached instance)
class BadAdapter : RecyclerView.Adapter<ViewHolder>() {
    override fun onCreateViewHolder(parent: ViewGroup, viewType: Int): ViewHolder {
        val inflater = LayoutInflater.from(parent.context) // unnecessary repeated call
        return ViewHolder(inflater.inflate(R.layout.item, parent, false))
    }
}
```

---

## Follow-ups

- What are the performance implications of creating LayoutInflater instances repeatedly?
- How does LayoutInflater handle custom views and attributes?
- When should you use Activity context vs Application context for LayoutInflater?
- How does View Binding compare to direct inflation?

## References

- Android Developer Documentation: System Services and Context

## Related Questions

### Prerequisites
- [[q-viewmodel-pattern--android--easy]]

### Related
- [[q-home-screen-widgets--android--medium]]
- [[q-what-design-systems-in-android-have-you-worked-with--android--medium]]

### Advanced
- [[q-compose-custom-layout--android--hard]]
