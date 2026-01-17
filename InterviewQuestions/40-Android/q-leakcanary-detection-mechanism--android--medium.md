---\
id: android-095
title: "LeakCanary Detection Mechanism / Механизм обнаружения LeakCanary"
aliases: ["How LeakCanary Detects Memory Leaks", "LeakCanary Detection Mechanism", "Как LeakCanary обнаруживает утечки памяти", "Механизм обнаружения LeakCanary"]
topic: android
subtopics: [performance-memory]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-13
updated: 2025-11-10
tags: [android/performance-memory, difficulty/medium, leakcanary, memory-leaks, weakreference]
moc: moc-android
related: [c-android-profiler, q-android-performance-measurement-tools--android--medium]
sources: ["https://square.github.io/leakcanary/"]
anki_cards:
  - slug: android-095-0-en
    front: "How does LeakCanary detect memory leaks?"
    back: |
      **Process:**
      1. **Lifecycle hooks** - tracks Activity/Fragment destruction
      2. **KeyedWeakReference** - creates weak ref to object
      3. **GC trigger** - waits, triggers GC, checks if ref cleared
      4. **Heap dump** - if still retained, creates dump
      5. **Shark** - analyzes dump, finds retention chain

      Key: WeakReference is cleared when no strong refs exist.
    tags:
      - android_general
      - difficulty::medium
  - slug: android-095-0-ru
    front: "Как LeakCanary обнаруживает утечки памяти?"
    back: |
      **Процесс:**
      1. **Хуки жизненного цикла** - отслеживает onDestroy Activity/Fragment
      2. **KeyedWeakReference** - создаёт слабую ссылку на объект
      3. **Триггер GC** - ждёт, вызывает GC, проверяет очистку ссылки
      4. **Heap dump** - если объект ещё удерживается, создаёт дамп
      5. **Shark** - анализирует дамп, находит цепочку удержания

      Ключ: WeakReference очищается при отсутствии сильных ссылок.
    tags:
      - android_general
      - difficulty::medium

---\
# Вопрос (RU)

> Как LeakCanary обнаруживает утечки памяти?

# Question (EN)

> How does LeakCanary detect memory leaks?

---

## Ответ (RU)

LeakCanary обнаруживает утечки памяти с помощью отслеживания жизненного цикла и механизма слабых ссылок (`WeakReference`) для контроля «удаляемости» объектов, а затем анализа heap dump библиотекой Shark. Он тесно связан с инструментами профилирования и анализом памяти в Android ([[c-android-profiler]]).

**Процесс обнаружения (упрощенно):**

**1. Интеграция с жизненным циклом**

LeakCanary автоматически отслеживает уничтожение `Activity` и `Fragment` (например, через `ActivityLifecycleCallbacks` и `FragmentLifecycleCallbacks`) и другие наблюдаемые точки. Когда компонент должен быть очищен (например, `Activity.onDestroy()`), он регистрируется в `ObjectWatcher`:

```kotlin
class LeakCanaryLifecycleObserver : LifecycleObserver {
    @OnLifecycleEvent(Lifecycle.Event.ON_DESTROY)
    fun onDestroy(owner: LifecycleOwner) {
        AppWatcher.objectWatcher.watch(owner)
    }
}
```

(Выше — иллюстративный пример на основе lifecycle observer; в актуальных версиях LeakCanary используется собственная интеграция без устаревшего `@OnLifecycleEvent`.)

**2. Регистрация объекта через WeakReference**

После того как объект должен быть собран GC, `ObjectWatcher` создает для него `KeyedWeakReference` и не хранит сильной ссылки на сам объект:

```kotlin
fun watch(watchedObject: Any) {
    val key = UUID.randomUUID().toString()
    val reference = KeyedWeakReference(
        watchedObject,
        key,
        referenceQueue
    )
    // Сохраняется только метадата по ключу (время, описание),
    // без сильной ссылки на watchedObject
    watchedObjects[key] = clock.uptimeMillis()
}
```

**3. Проверка после GC (retained objects)**

Через задержку (`retainedDelayMillis`, например около 5 секунд) LeakCanary инициирует GC (если возможно) и проверяет, были ли слабые ссылки очищены. Это упрощённый алгоритм:

```kotlin
fun checkForLeaks() {
    gcTrigger() // Может вызвать Runtime.getRuntime().gc(), но GC не гарантирован

    // Удаляем очищенные ссылки из очереди
    removeWeaklyReachableObjects()

    // Оставшиеся записи — объекты, которые всё ещё удерживаются (retained),
    // кандидаты на утечки
    val retained = watchedObjects.filter { (_, time) ->
        clock.uptimeMillis() - time >= retainedDelayMillis
    }

    if (retained.isNotEmpty()) {
        dumpHeap() // Создаем heap dump для анализа Shark
    }
}
```

Важно: на этом этапе LeakCanary находит именно «retained objects» (подозрение на утечку), а не подтвержденные утечки.

**Принцип работы `WeakReference` (упрощенно):**

```kotlin
// Нормальный случай (нет утечки):
// после потери всех сильных ссылок объект может быть собран.
var activity: Activity? = MyActivity()
val weakRef = WeakReference(activity)
activity = null
System.gc() // Может не сработать немедленно
val result = weakRef.get() // Часто будет null, когда GC реально соберет объект

// Потенциальная утечка памяти:
companion object {
    var staticRef: Activity? = null // Сильная ссылка удерживает Activity
}
var leakyActivity: Activity? = MyActivity()
staticRef = leakyActivity
val weakRefLeaky = WeakReference(leakyActivity)
leakyActivity = null
System.gc()
val stillThere = weakRefLeaky.get() // Может оставаться не-null, т.к. есть staticRef
```

Комментарий: наличие не-null в `weakRef` после вызова `System.gc()` само по себе не гарантирует утечку — GC не обязателен и не детерминирован. Пример иллюстрирует, что сильные ссылки предотвращают освобождение объектов, в то время как `ObjectWatcher` ожидает, что объект станет только слабо достижимым.

**Архитектура LeakCanary (основные компоненты):**

1. **ObjectWatcher** — регистрирует объекты через `KeyedWeakReference` и отслеживает retained objects.
2. **ReferenceQueue** — получает уведомления об очищенных слабых ссылках.
3. **HeapDumper** — создает heap dump при наличии retained objects сверх порога.
4. **Shark** — анализирует heap dump, строит граф ссылок и выявляет реальные причины утечек, фильтруя ожидаемые удержания.

**Кастомный мониторинг:**

```kotlin
class MyViewModel : ViewModel() {
    init {
        AppWatcher.objectWatcher.watch(
            this,
            "MyViewModel should be cleared"
        )
    }
}
```

Этот подход позволяет отслеживать не только `Activity`/`Fragment`, но и любые объекты, которые должны быть собраны после определенного события.

## Answer (EN)

LeakCanary detects memory leaks by observing lifecycle events, tracking objects via `WeakReference`, and then analyzing a heap dump with the Shark library. It is closely related to memory profiling and analysis tools on Android ([[c-android-profiler]]).

**Detection Process (simplified):**

**1. `Lifecycle` Integration**

LeakCanary automatically hooks into `Activity` and `Fragment` lifecycles (e.g., via `ActivityLifecycleCallbacks` and `FragmentLifecycleCallbacks`) and other relevant points. When a component is expected to be released (e.g., in `Activity.onDestroy()`), it is registered with `ObjectWatcher`:

```kotlin
class LeakCanaryLifecycleObserver : LifecycleObserver {
    @OnLifecycleEvent(Lifecycle.Event.ON_DESTROY)
    fun onDestroy(owner: LifecycleOwner) {
        AppWatcher.objectWatcher.watch(owner)
    }
}
```

(The snippet above is an illustrative lifecycle observer example; modern LeakCanary uses its own integration and does not rely on the deprecated `@OnLifecycleEvent` in production.)

**2. Registration Using WeakReference**

After an object should be eligible for GC, `ObjectWatcher` creates a `KeyedWeakReference` for it without keeping a strong reference:

```kotlin
fun watch(watchedObject: Any) {
    val key = UUID.randomUUID().toString()
    val reference = KeyedWeakReference(
        watchedObject,
        key,
        referenceQueue
    )
    // Only metadata (time, description) is stored by key,
    // no strong reference to watchedObject is kept
    watchedObjects[key] = clock.uptimeMillis()
}
```

**3. Post-GC Check (retained objects)**

After a delay (`retainedDelayMillis`, about a few seconds), LeakCanary triggers a GC (best-effort) and checks whether weak references were cleared. This is a simplified algorithm:

```kotlin
fun checkForLeaks() {
    gcTrigger() // May call Runtime.getRuntime().gc(), but GC is not guaranteed

    // Remove cleared references from queue
    removeWeaklyReachableObjects()

    // Remaining entries are still strongly held (retained),
    // i.e., candidates for leaks
    val retained = watchedObjects.filter { (_, time) ->
        clock.uptimeMillis() - time >= retainedDelayMillis
    }

    if (retained.isNotEmpty()) {
        dumpHeap() // Create heap dump for Shark analysis
    }
}
```

Important: at this stage, LeakCanary has identified "retained objects" (suspected leaks), not confirmed leaks.

**`WeakReference` Behavior (simplified):**

```kotlin
// Normal case (no leak):
// once all strong references are gone, the object becomes eligible for GC.
var activity: Activity? = MyActivity()
val weakRef = WeakReference(activity)
activity = null
System.gc() // May not run immediately
val result = weakRef.get() // Often null once GC actually collects it

// Potential memory leak:
companion object {
    var staticRef: Activity? = null // Strong reference keeps Activity alive
}
var leakyActivity: Activity? = MyActivity()
staticRef = leakyActivity
val weakRefLeaky = WeakReference(leakyActivity)
leakyActivity = null
System.gc()
val stillThere = weakRefLeaky.get() // May remain non-null because of staticRef
```

Note: `weakRef.get()` being non-null after `System.gc()` does not by itself prove a leak—GC is non-deterministic. The example illustrates how strong references prevent collection, while `ObjectWatcher` expects the monitored object to become only weakly reachable.

**LeakCanary Architecture (key components):**

1. **ObjectWatcher** - registers objects via `KeyedWeakReference` and tracks retained objects.
2. **ReferenceQueue** - receives notifications when weak references are cleared.
3. **HeapDumper** - creates a heap dump when retained objects exceed the configured threshold.
4. **Shark** - analyzes the heap dump, builds a reference graph, and identifies actual leak causes while filtering expected/legitimate retentions.

**Custom Monitoring:**

```kotlin
class MyViewModel : ViewModel() {
    init {
        AppWatcher.objectWatcher.watch(
            this,
            "MyViewModel should be cleared"
        )
    }
}
```

This pattern can be used for any objects that are expected to be cleared after a certain lifecycle event.

---

## Дополнительные Вопросы (RU)

1. Что произойдет, если сборщик мусора не запустится после вызова `System.gc()`?
2. Как LeakCanary различает допустимые удерживаемые объекты и реальные утечки?
3. Каково влияние LeakCanary на производительность в debug-сборках?
4. Как библиотека Shark анализирует heap dump и находит причины утечек?
5. Может ли LeakCanary обнаруживать утечки в пользовательских объектах, помимо `Activity` и `Fragment`?

## Follow-ups

1. What happens if garbage collection doesn't run when `System.gc()` is called?
2. How does LeakCanary distinguish between legitimate retained objects and actual leaks?
3. What is the performance impact of LeakCanary in debug builds?
4. How does the Shark library analyze heap dumps to identify leak causes?
5. Can LeakCanary detect leaks in custom objects beyond `Activity` and `Fragment`?

## Ссылки (RU)

- Официальная документация LeakCanary: https://square.github.io/leakcanary/

## References

- https://square.github.io/leakcanary/ - Official LeakCanary documentation

## Связанные Вопросы (RU)

### Базовые (проще)
- [[q-leakcanary-library--android--easy]] - Введение в библиотеку LeakCanary
- [[q-memory-leaks-definition--android--easy]] - Основы утечек памяти
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Основы потоков выполнения

### Связанные (тот Же уровень)
- [[q-leakcanary-heap-dump-analysis--android--medium]] - Анализ heap dump с помощью LeakCanary
- [[q-memory-leak-detection--android--medium]] - Стратегии обнаружения утечек памяти
- [[q-android-performance-measurement-tools--android--medium]] - Инструменты профилирования

### Продвинутые (сложнее)
- [[q-android-runtime-internals--android--hard]] - Внутреннее устройство рантайма и управление памятью
- [[q-fix-slow-app-startup-legacy--android--hard]] - Оптимизация производительности запуска приложения
- [[q-observability-sdk--android--hard]] - Мониторинг и наблюдаемость в продакшене

## Related Questions

### Prerequisites (Easier)
- [[q-leakcanary-library--android--easy]] - LeakCanary library introduction
- [[q-memory-leaks-definition--android--easy]] - Memory leak fundamentals
- [[q-what-is-the-main-application-execution-thread--android--easy]] - Threading basics

### Related (Same Level)
- [[q-leakcanary-heap-dump-analysis--android--medium]] - Analyzing heap dumps
- [[q-memory-leak-detection--android--medium]] - Leak detection strategies
- [[q-android-performance-measurement-tools--android--medium]] - Profiling tools

### Advanced (Harder)
- [[q-android-runtime-internals--android--hard]] - Runtime memory management
- [[q-fix-slow-app-startup-legacy--android--hard]] - App performance tuning
- [[q-observability-sdk--android--hard]] - Production monitoring
