---
id: kotlin-090
title: "Coroutine Memory Leaks and Prevention / Утечки памяти в корутинах и их предотвращение"
aliases: ["Coroutine Memory Leaks and Prevention", "Утечки памяти в корутинах и их предотвращение"]

# Classification
topic: kotlin
subtopics: [coroutines]
question_kind: theory
difficulty: hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: internal
source_note: Comprehensive Kotlin Coroutines Guide - Question 140024

# Workflow & relations
status: draft
moc: moc-kotlin
related: [c-coroutines, c-kotlin, q-kotlin-sam-interfaces--kotlin--medium, q-visibility-modifiers-kotlin--kotlin--medium]

# Timestamps
created: 2025-10-12
updated: 2025-11-09

tags: [coroutines, difficulty/hard, kotlin]
---
# Вопрос (RU)
> Продвинутая тема корутин Kotlin 140024

---

# Question (EN)
> Kotlin Coroutines advanced topic 140024

## Ответ (RU)

Утечки памяти в корутинах обычно происходят, когда корутины не привязаны к корректному жизненному циклу или не отменяются должным образом, из-за чего удерживаются ссылки и продолжается расход ресурсов. Также утечки возможны, если долгие операции внутри корутин не учитывают отмену (игнорируют `isActive`/`ensureActive()` и выполняют блокирующий код), из-за чего корутины продолжают работать и сохранять ссылки дольше необходимого.

### Распространенные Причины Утечек

**1. Неправильно управляемые scopes (антипаттерн)**
```kotlin
class MyViewModel {
    private val scope = CoroutineScope(Dispatchers.Main)
    
    fun loadData() {
        scope.launch { /* work */ }
    }
    
    // Если onCleared не будет вызван или не отменит scope,
    // корутины могут удерживать ссылки дольше, чем нужно.
    fun onCleared() {
        scope.cancel()
    }
}
```

Без привязки scope к жизненному циклу (например, через `viewModelScope`) легко получить корутины, переживающие нужный срок жизни объекта.

```kotlin
// Рекомендуемый подход (Android ViewModel)
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            /* work */
        }
    }
}
```

**2. Использование GlobalScope без учета жизненного цикла**
```kotlin
// Потенциальная утечка: корутина может жить дольше `Activity`/`Fragment`,
// пока не завершится или пока жив процесс приложения.
GlobalScope.launch {
    // Это может выполняться даже после уничтожения Activity,
    // удерживая её ссылки при их захвате внутри корутины.
}

// Исправление (Android): использовать lifecycleScope для компонентов,
// имеющих Lifecycle.
lifecycleScope.launch {
    // Автоматически отменяется при уничтожении LifecycleOwner.
}
```

**3. Захват ссылок на `Activity`/`Fragment` долговечными корутинами**
```kotlin
// Потенциальная утечка
class MyActivity : Activity() {
    fun startWork() {
        GlobalScope.launch {
            // Если эта корутина переживет Activity и внутри используются
            // this@MyActivity, её поля или ссылки на View,
            // она будет удерживать MyActivity в памяти.
            updateUI()  // Может неявно захватывать this@MyActivity
        }
    }
}
```

Проблема не в самом вызове `updateUI()`, а в том, что корутина запущена в `GlobalScope` и может жить дольше `Activity`, удерживая её через захваченные ссылки.

**4. Игнорирование отмены и блокирующие операции внутри корутин**

Даже при правильной привязке scope к жизненному циклу утечки возможны, если:
- используются блокирующие вызовы (например, долгие операции ввода-вывода или `Thread.sleep`) без `withContext(Dispatchers.IO)`,
- выполняются длительные циклы без проверки `isActive` или `ensureActive()`.

В таких случаях корутина продолжает выполняться после отмены scope, удерживая ссылки и ресурсы.

### Инструменты Обнаружения
- LeakCanary для Android
- Memory Profiler в Android Studio
- Анализ heap dumps

### Предотвращение
1. Используйте структурированную конкурентность (`coroutineScope`, `supervisorScope`) и scopes, привязанные к жизненному циклу.
2. Отменяйте scopes в методах жизненного цикла или полагайтесь на `viewModelScope`/`lifecycleScope` там, где это доступно.
3. Избегайте `GlobalScope`, кроме действительно операций уровня приложения (и тщательно управляйте ими).
4. Следите, чтобы долгие операции выполнялись не на `Dispatchers.Main`, и чтобы `suspend`-функции и циклы корректно реагировали на отмену (используйте кооперативную отмену и не блокируйте поток).

---

## Answer (EN)

Memory leaks in coroutines typically occur when coroutines are not bound to the correct lifecycle or not properly cancelled, causing references to be retained and resources to be consumed longer than necessary. Leaks can also occur when long-running work inside coroutines does not cooperate with cancellation (ignoring `isActive`/`ensureActive()` or using blocking calls), so coroutines continue to run and hold references even after their scope is cancelled.

### Common Leak Causes

**1. Improperly managed scopes (anti-pattern)**
```kotlin
class MyViewModel {
    private val scope = CoroutineScope(Dispatchers.Main)
    
    fun loadData() {
        scope.launch { /* work */ }
    }
    
    // If onCleared is not called or does not cancel the scope,
    // coroutines may outlive the intended lifetime.
    fun onCleared() {
        scope.cancel()
    }
}
```

Without tying the scope to lifecycle-aware constructs (e.g. `viewModelScope`), it's easy to end up with coroutines that outlive their owning component.

```kotlin
// Recommended approach (Android ViewModel)
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            /* work */
        }
    }
}
```

**2. Using GlobalScope without lifecycle awareness**
```kotlin
// Potential leak: coroutine may live longer than the `Activity`/`Fragment`
// until it finishes or the app process is killed.
GlobalScope.launch {
    // This may keep running after the Activity is destroyed,
    // retaining its references if they are captured.
}

// Fix (Android): use lifecycleScope on LifecycleOwners.
lifecycleScope.launch {
    // Automatically cancelled when the LifecycleOwner is destroyed.
}
```

**3. Capturing `Activity`/`Fragment` references in long-lived coroutines**
```kotlin
// Potential leak
class MyActivity : Activity() {
    fun startWork() {
        GlobalScope.launch {
            // If this coroutine outlives the Activity and uses
            // this@MyActivity, its fields or View references,
            // it will keep MyActivity in memory.
            updateUI()  // May implicitly capture this@MyActivity
        }
    }
}
```

The issue is not `updateUI()` itself but launching in `GlobalScope` without lifecycle binding, allowing the coroutine to outlive the `Activity` while holding captured references.

**4. Ignoring cancellation and blocking inside coroutines**

Even with proper lifecycle binding, leaks can occur if:
- blocking calls (e.g. long I/O or `Thread.sleep`) are used instead of suspending APIs / `withContext(Dispatchers.IO)`,
- long-running loops do not check `isActive` or call `ensureActive()`.

In such cases, the coroutine keeps running after the scope is cancelled, holding references and resources.

### Detection Tools
- LeakCanary for Android
- Memory Profiler in Android Studio
- Heap dump analysis

### Prevention
1. Use structured concurrency (`coroutineScope`, `supervisorScope`) and lifecycle-aware scopes.
2. Cancel scopes in lifecycle callbacks or rely on `viewModelScope`/`lifecycleScope` where available.
3. Avoid `GlobalScope` except for true app-wide operations, and manage them carefully.
4. Ensure long-running work is not done on `Dispatchers.Main` and that suspend functions and loops cooperate with cancellation (use cooperative cancellation and avoid blocking threads).

---

## Дополнительные Вопросы (RU)

1. Как структурированная конкурентность помогает предотвращать утечки памяти, связанные с корутинами, в крупных Android-приложениях?
2. В каких сценариях, если вообще, допустимо использовать `GlobalScope`, и как минимизировать риск утечек при его использовании?
3. Как вы спроектируете scopes и отмену корутин для мультиэкранного фиче-модуля с общими `ViewModel`?
4. Как совместно использовать LeakCanary и анализ heap dumps для подтверждения утечек, вызванных корутинами?
5. Какие подходы вы примените для безопасной передачи колбэков или слушателей в долгоживущие корутины без утечек Android-компонентов?

---

## Follow-ups

1. How does structured concurrency help prevent coroutine-related memory leaks in large Android applications?
2. In what scenarios, if any, is it acceptable to use `GlobalScope`, and how would you mitigate leak risks when doing so?
3. How would you design coroutine scopes and cancellation for a multi-screen feature that uses shared `ViewModel`s?
4. How can tools like LeakCanary and heap dump analysis be used together to confirm coroutine-induced leaks?
5. What patterns would you apply to safely pass callbacks or listeners into long-running coroutines without leaking Android components?

---

## Ссылки (RU)

- [Документация по Kotlin Coroutines](https://kotlinlang.org/docs/coroutines-overview.html)
- [[c-kotlin]]
- [[c-coroutines]]

---

## References

- [Kotlin Coroutines Documentation](https://kotlinlang.org/docs/coroutines-overview.html)
- [[c-kotlin]]
- [[c-coroutines]]

---

## Связанные Вопросы (RU)

### Сложные (Hard)
- [[q-coroutine-profiling--kotlin--hard]] - Coroutines
- [[q-coroutine-performance-optimization--kotlin--hard]] - Coroutines
- [[q-advanced-coroutine-patterns--kotlin--hard]] - Coroutines
- [[q-select-expression-channels--kotlin--hard]] - Coroutines

### Предпосылки (Легче)
- [[q-flow-combining-zip-combine--kotlin--medium]] - Coroutines
- [[q-what-is-coroutine--kotlin--easy]] - Coroutines

---

## Related Questions

### Related (Hard)
- [[q-coroutine-profiling--kotlin--hard]] - Coroutines
- [[q-coroutine-performance-optimization--kotlin--hard]] - Coroutines
- [[q-advanced-coroutine-patterns--kotlin--hard]] - Coroutines
- [[q-select-expression-channels--kotlin--hard]] - Coroutines

### Prerequisites (Easier)
- [[q-flow-combining-zip-combine--kotlin--medium]] - Coroutines
- [[q-what-is-coroutine--kotlin--easy]] - Coroutines
