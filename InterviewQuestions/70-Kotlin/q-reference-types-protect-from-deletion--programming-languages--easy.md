---
id: lang-052
title: "Reference Types Protect From Deletion / Типы ссылок защищают от удаления"
aliases: [Reference Types Protect From Deletion, Типы ссылок защищают от удаления]
topic: kotlin
subtopics: [garbage-collection, jvm, memory-management]
question_kind: theory
difficulty: easy
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-kotlin, c-garbage-collection, q-detect-unused-object--programming-languages--easy]
created: 2025-10-15
updated: 2025-11-09
tags: [difficulty/easy, garbage-collection, jvm, kotlin, memory-management, phantom-reference, programming-languages, references, soft-reference, strong-reference, weak-reference]
---
# Вопрос (RU)
> Все ли виды ссылок защищают объект от удаления (сборки мусора)?

# Question (EN)
> Do all types of references protect an object from deletion (garbage collection)?

## Ответ (RU)

Нет, не все типы ссылок предотвращают сборку мусора.

В контексте Java/Kotlin (JVM) используются следующие виды ссылок:

1. Strong reference (обычная сильная ссылка) — защищает объект, пока он сильно достижим.

```kotlin
val user = User("John")  // Сильная ссылка
// Пока существует хотя бы одна достижимая сильная ссылка на объект,
// он НЕ будет собран сборщиком мусора.
```

2. Weak reference — не защищает объект.

```kotlin
import java.lang.ref.WeakReference

val user = User("John")
val weakRef = WeakReference(user)

// user = null  // После удаления всех сильных ссылок
// объект МОЖЕТ быть собран, даже если weakRef все еще существует.
```

3. Soft reference — не дает жесткой гарантии сохранения объекта (эвристика GC).

```kotlin
import java.lang.ref.SoftReference

val softRef = SoftReference(Data())
// Объект, на который ссылается SoftReference, является кандидатом на сборку,
// но сборщик мусора обычно старается удерживать такие объекты дольше и
// очищает их преимущественно при нехватке памяти (например, для кэшей).
// Это НЕ жесткая гарантия и зависит от реализации JVM и настроек сборщика мусора.
```

4. Phantom reference — не защищает объект.

```kotlin
import java.lang.ref.PhantomReference
import java.lang.ref.ReferenceQueue

val queue = ReferenceQueue<User>()
val phantomRef = PhantomReference(User("John"), queue)
// PhantomReference не дает доступа к объекту (get() всегда возвращает null).
// Используется совместно с ReferenceQueue для уведомления ПОСЛЕ того,
// как объект стал phantom-reachable и подготовлен к освобождению,
// для выполнения действий по очистке после GC.
```

Сравнение (интерпретация JVM-зависима, конкретное поведение определяется реализацией GC):

- Strong reference:
  - Защищает от сборки, пока объект сильно достижим.
  - Типичный сценарий: обычное использование объектов.
- Soft reference:
  - Не дает строгой гарантии; обычно объекты сохраняются дольше и очищаются при давлении на память.
  - Сценарий: кэши, чувствительные к памяти.
- Weak reference:
  - Не защищает от GC; объект может быть немедленно собран, как только остается только слабая достижимость.
  - Сценарий: избежание утечек памяти, разрыв циклических ссылок, кэши, где данные можно легко восстановить.
- Phantom reference:
  - Не защищает от GC и не предоставляет доступ к объекту.
  - Сценарий: посмертная очистка, отслеживание момента фактического освобождения памяти через ReferenceQueue.

Примеры использования:

Strong reference:
```kotlin
class Cache {
    private val data = mutableListOf<Data>()  // Сильные ссылки

    fun add(item: Data) {
        data.add(item)  // Пока элемент в списке и список достижим, объект не будет собран GC.
    }
}
```

Weak reference (кэш):
```kotlin
import java.lang.ref.WeakReference

class WeakCache {
    private val cache = mutableMapOf<String, WeakReference<Data>>() 

    fun put(key: String, value: Data) {
        cache[key] = WeakReference(value)
    }

    fun get(key: String): Data? {
        return cache[key]?.get()  // Может вернуть null, если объект был собран GC.
    }
}
```

Soft reference (кэш картинок):
```kotlin
import java.lang.ref.SoftReference

class ImageCache {
    private val cache = mutableMapOf<String, SoftReference<Bitmap>>()

    fun get(url: String): Bitmap? {
        return cache[url]?.get()  // Может быть очищено при нехватке памяти.
    }
}
```

Поведение памяти (иллюстративно; зависит от реализации JVM и настроек GC):

```kotlin
fun example() {
    val strongData = Data()                    // Сильная ссылка
    val weakData = WeakReference(Data())       // Weak: может быть собран в любой момент
    val softData = SoftReference(Data())       // Soft: обычно удерживается дольше, но без гарантий

    System.gc()  // Лишь подсказка; фактическое поведение зависит от реализации JVM и настроек GC

    println(weakData.get())  // Может быть null, если объект собран
    println(softData.get())  // Может сохраниться, но может быть null при давлении на память
    println(strongData)      // Все еще доступен, так как сильно достижим в этой области видимости
}
```

Итог:

- Strong reference: предотвращает сборку, пока объект сильно достижим.
- Weak reference: не предотвращает сборку; объект может быть собран, как только остается только слабая достижимость.
- Soft reference: не гарантирует сохранения; подходит для кэшей, чувствительных к памяти; конкретное поведение зависит от реализации JVM и настроек сборщика мусора.
- Phantom reference: не предотвращает сборку; используется с ReferenceQueue для логики очистки после GC.

Также важно: точное время сборки мусора и стратегия обработки soft/weak/phantom ссылок зависят от конкретной реализации JVM и настроек сборщика мусора.

## Answer (EN)

No, not all reference types protect objects from garbage collection.

Java/Kotlin (JVM) provide these reference types:

1. Strong Reference (Normal) — protects while strongly reachable

```kotlin
val user = User("John")  // Strong reference
// As long as at least one strong reference to this object exists and is reachable,
// the object will NOT be garbage collected.
```

2. Weak Reference — does NOT protect

```kotlin
import java.lang.ref.WeakReference

val user = User("John")
val weakRef = WeakReference(user)

// user = null  // After removing all strong references,
// the object CAN be garbage collected even though weakRef exists.
```

3. Soft Reference — does NOT strictly protect (hinted retention)

```kotlin
import java.lang.ref.SoftReference

val softRef = SoftReference(Data())
// The referent is eligible for GC, but collectors typically try to keep
// soft-referenced objects longer and clear them preferentially under
// memory pressure (e.g., for caches). This is NOT a hard guarantee and is
// dependent on the specific JVM and GC configuration.
```

4. Phantom Reference — does NOT protect

```kotlin
import java.lang.ref.PhantomReference
import java.lang.ref.ReferenceQueue

val queue = ReferenceQueue<User>()
val phantomRef = PhantomReference(User("John"), queue)
// PhantomReference does not provide access to the referent (get() always returns null).
// It is used together with ReferenceQueue to be notified AFTER the object
// becomes phantom reachable and is prepared for reclamation, for post-GC cleanup logic.
```

Comparison (implementation-dependent across JVMs/GCs; concrete behavior is determined by the GC implementation):

| Reference Type | Protects from GC?                                | Use Case                          |
|----------------|--------------------------------------------------|-----------------------------------|
| Strong         | Yes, while strongly reachable                    | Normal object usage               |
| Soft           | No hard guarantee; usually kept until low memory | Caches with memory sensitivity    |
| Weak           | No                                               | Avoid leaks, break cycles, caches |
| Phantom        | No                                               | Post-GC cleanup via queue         |

Examples:

Strong Reference:
```kotlin
class Cache {
    private val data = mutableListOf<Data>()  // Strong refs

    fun add(item: Data) {
        data.add(item)  // While in this list and reachable, item will not be GC'd
    }
}
```

Weak Reference (Cache):
```kotlin
import java.lang.ref.WeakReference

class WeakCache {
    private val cache = mutableMapOf<String, WeakReference<Data>>() 

    fun put(key: String, value: Data) {
        cache[key] = WeakReference(value)
    }

    fun get(key: String): Data? {
        return cache[key]?.get()  // May return null if GC collected the value
    }
}
```

Soft Reference (Image Cache):
```kotlin
import java.lang.ref.SoftReference

class ImageCache {
    private val cache = mutableMapOf<String, SoftReference<Bitmap>>()

    fun get(url: String): Bitmap? {
        return cache[url]?.get()  // May be cleared under memory pressure
    }
}
```

Memory Behavior (illustrative only; depends on JVM implementation and GC settings):

```kotlin
fun example() {
    val strongData = Data()                    // Strong reference
    val weakData = WeakReference(Data())       // Weak: eligible for GC at any time
    val softData = SoftReference(Data())       // Soft: typically retained longer, but no guarantee

    System.gc()  // Only a hint; actual behavior depends on the JVM implementation and GC configuration

    println(weakData.get())  // May be null if collected
    println(softData.get())  // May still be there; may be null under memory pressure
    println(strongData)      // Still there, as it's strongly reachable in this scope
}
```

Summary:

- Strong Reference: prevents GC while the object is strongly reachable.
- Weak Reference: does NOT prevent GC; referent may be collected at any time once only weakly reachable.
- Soft Reference: does NOT strictly prevent GC; intended for memory-sensitive caches; exact behavior depends on JVM implementation and GC settings.
- Phantom Reference: does NOT prevent GC; used with ReferenceQueue for post-mortem cleanup.

---

## Дополнительные вопросы (RU)

- Как эти типы ссылок ведут себя на JVM, и как Kotlin использует те же механизмы, что и Java? 
- Когда на практике стоит использовать weak/soft/phantom ссылки?
- Каковы типичные ошибки и заблуждения (например, полагаться на SoftReference как на строгую гарантию кэширования или считать, что System.gc() принудительно запускает сборку)?

## Follow-ups (EN)

- How do these reference types behave on the JVM, and how does Kotlin use the same mechanisms as Java?
- When would you use weak/soft/phantom references in practice?
- What are common pitfalls and misconceptions (e.g., relying on SoftReference for strict cache guarantees, assuming System.gc() forces collection)?

## Ссылки (RU)

- [[c-kotlin]]
- Java SE документация: пакет java.lang.ref (описание семантики ссылок и поведения GC)
- Документация Kotlin: https://kotlinlang.org/docs/home.html

## References (EN)

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)
- Java SE documentation: java.lang.ref package (for reference semantics)

## Связанные вопросы (RU)

- [[q-detect-unused-object--programming-languages--easy]]

## Related Questions (EN)

- [[q-detect-unused-object--programming-languages--easy]]
