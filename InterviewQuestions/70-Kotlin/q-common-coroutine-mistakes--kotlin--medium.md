---
id: kotlin-098
title: "Top 10 common Kotlin coroutines mistakes and anti-patterns / 10 частых ошибок с Kotlin корутинами"
topic: kotlin
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
created: 2025-10-12
updated: 2025-11-09
aliases: []
question_kind: theory
tags: [anti-patterns, best-practices, code-review, coroutines, difficulty/medium, gotchas, kotlin, mistakes]
moc: moc-kotlin
related: [c-coroutines, q-coroutine-exception-handler--kotlin--medium, q-debugging-coroutines-techniques--kotlin--medium, q-mutex-synchronized-coroutines--kotlin--medium]
subtopics: [anti-patterns, best-practices, coroutines]

---
# Вопрос (RU)
> Какие самые распространенные ошибки при использовании Kotlin корутин, и как их исправить?

---

# Question (EN)
> What are the most common mistakes when using Kotlin coroutines, and how do you fix them?

## Ответ (RU)

Даже опытные разработчики совершают типичные ошибки при работе с Kotlin корутинами. Эти ошибки могут привести к утечкам памяти, крашам, состояниям гонки или плохой производительности. Понимание и избегание этих анти-паттернов критично для production-ready кода.

Ниже приведен один из ключевых примеров (остальные ошибки перечислены в кратком списке):

### Ошибка 1: Использование GlobalScope

Проблема: корутины в `GlobalScope` не привязаны к жизненному циклу компонента и могут утекать.

```kotlin
// НЕПРАВИЛЬНО: корутина в GlobalScope продолжается после уничтожения Activity
class MyActivity : AppCompatActivity() {
    fun loadData() {
        GlobalScope.launch {
            val data = repository.fetchData()
            updateUI(data) // Возможен краш, если Activity уже уничтожена!
        }
    }
}
```

Почему это ошибка:
- Корутина продолжает выполняться после уничтожения `Activity`/`ViewModel`
- Возможны утечки памяти
- Возможны краши при обращении к уничтоженным `View`
- Нарушается структурированная конкурентность

**FIX: используйте корректный scope**

```kotlin
// ПРАВИЛЬНО: используем lifecycleScope
class MyActivity : AppCompatActivity() {
    fun loadData() {
        lifecycleScope.launch {
            val data = repository.fetchData()
            updateUI(data) // Безопасно: корутина отменяется при уничтожении Activity
        }
    }
}

// ПРАВИЛЬНО: используем viewModelScope
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            val data = repository.fetchData()
            _dataState.value = data // Безопасно: отменяется при onCleared()
        }
    }
}

// ПРАВИЛЬНО: собственный scope, управляемый явно
class MyRepository {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    fun fetchData() {
        scope.launch {
            // Работа репозитория
        }
    }

    fun cleanup() {
        scope.cancel() // Отменяем все корутины при завершении жизненного цикла репозитория
    }
}
```

Детектирование: найдите использования `GlobalScope` в кодовой базе и замените на области, привязанные к жизненному циклу.

### Ключевые Выводы

1. Никогда не используйте GlobalScope без крайней необходимости — используйте области, привязанные к жизненному циклу.
2. Всегда учитывайте отмену — проверяйте `isActive`, используйте `ensureActive()` в долгих циклах и вычислениях.
3. Не блокируйте потоки — избегайте `runBlocking` и `Thread.sleep` в production-коде на главном и рабочих потоках.
4. Используйте правильные диспетчеры — `Dispatchers.IO` для ввода-вывода, `Dispatchers.Default` для CPU-bound задач, `Dispatchers.Main` для UI.
5. Используйте `supervisorScope` или `SupervisorJob` там, где сбои дочерних задач не должны отменять всех.
6. Не забывайте `await()` у `async` — иначе вы игнорируете результат и возможные исключения.
7. Не создавайте корутины без необходимости — оценивайте накладные расходы и читабельность.
8. Соблюдайте структурированную конкурентность — позволяйте фреймворку управлять жизненным циклом, избегайте "висящих" корутин.
9. Избегайте утечек памяти — следите, чтобы корутины не держали ссылки на уничтоженные компоненты.
10. Корректно обрабатывайте исключения — понимайте различия поведения `launch` и `async`, используйте `CoroutineExceptionHandler` там, где это уместно.

См. также: [[c-coroutines]].

---

## Answer (EN)

Even experienced developers make common mistakes when working with Kotlin coroutines. These mistakes can lead to memory leaks, crashes, race conditions, or poor performance. Understanding and avoiding these anti-patterns is critical for production-ready code.

Below is one key example (with other common issues summarized in the key takeaways):

### Mistake 1: Using GlobalScope

Problem: `GlobalScope` coroutines are not tied to any lifecycle and can leak.

```kotlin
// WRONG: GlobalScope coroutine continues after Activity destroyed
class MyActivity : AppCompatActivity() {
    fun loadData() {
        GlobalScope.launch {
            val data = repository.fetchData()
            updateUI(data) // May crash if Activity is destroyed!
        }
    }
}
```

Why it's wrong:
- The `Coroutine` continues after `Activity`/`ViewModel` is destroyed
- Can cause memory leaks
- Can crash when accessing destroyed `View`s
- Breaks structured concurrency

**FIX: Use proper scope**

```kotlin
// CORRECT: Use lifecycleScope
class MyActivity : AppCompatActivity() {
    fun loadData() {
        lifecycleScope.launch {
            val data = repository.fetchData()
            updateUI(data) // Safe: cancelled when Activity is destroyed
        }
    }
}

// CORRECT: Use viewModelScope
class MyViewModel : ViewModel() {
    fun loadData() {
        viewModelScope.launch {
            val data = repository.fetchData()
            _dataState.value = data // Safe: cancelled when ViewModel is cleared
        }
    }
}

// CORRECT: Custom scope with explicit lifecycle control
class MyRepository {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    fun fetchData() {
        scope.launch {
            // Work
        }
    }

    fun cleanup() {
        scope.cancel() // Cancel all coroutines when repository is no longer needed
    }
}
```

Detection: Search your codebase for `GlobalScope` and replace it with lifecycle-aware or explicitly managed scopes.

### Key Takeaways

1. Never use GlobalScope unless you truly need a process-wide, manually-managed scope; prefer lifecycle-aware scopes.
2. Always handle cancellation — check `isActive`, use `ensureActive()` in long-running loops and computations.
3. Do not block threads — avoid `runBlocking` and `Thread.sleep` in production code on main and worker threads.
4. Use the right dispatchers — `Dispatchers.IO` for I/O, `Dispatchers.Default` for CPU-bound work, `Dispatchers.Main` for UI.
5. Use `supervisorScope` or `SupervisorJob` when failures in child coroutines should not cancel all siblings.
6. Always `await()` results of `async` when you care about the value or its exceptions.
7. Avoid creating coroutines unnecessarily — consider overhead, readability, and structured concurrency.
8. Follow structured concurrency — let scopes manage lifecycles and avoid "dangling" coroutines.
9. Avoid memory leaks — make sure coroutines do not capture references to destroyed components.
10. Handle exceptions correctly — understand `launch` vs `async` behavior and use `CoroutineExceptionHandler` appropriately.

See also: [[c-coroutines]].

## Дополнительные Вопросы (RU)

1. Как реализовать собственный `CoroutineScope` с корректным управлением жизненным циклом?
2. Какие инструменты существуют для обнаружения утечек памяти, связанных с корутинами?
3. Как рефакторить легаси-код с `GlobalScope` на корректные области видимости?
4. В чем заключается влияние чрезмерного создания корутин на производительность?
5. Как провести аудит кодовой базы на наличие анти-паттернов при работе с корутинами?
6. Какие самые скрытые и труднообнаружимые баги, связанные с корутинами?
7. Как выстроить обучение команды лучшим практикам использования корутин?

## Follow-ups

1. How do you implement a custom `CoroutineScope` with proper lifecycle management?
2. What tools exist for detecting coroutine-related memory leaks?
3. How do you refactor legacy code with `GlobalScope` to use proper scopes?
4. What is the performance impact of excessive coroutine creation?
5. How do you audit a codebase for coroutine anti-patterns?
6. What are the most subtle coroutine bugs that are hard to detect?
7. How do you educate a team about coroutine best practices?

## Ссылки (RU)

- [Kotlin `Coroutines` Best Practices](https://kotlinlang.org/docs/coroutines-guide.html)
- [Android `Coroutines` Best Practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices)
- [Common `Coroutine` Mistakes](https://elizarov.medium.com/top-10-coroutines-mistakes-42b19c2a25b2)

## References

- [Kotlin `Coroutines` Best Practices](https://kotlinlang.org/docs/coroutines-guide.html)
- [Android `Coroutines` Best Practices](https://developer.android.com/kotlin/coroutines/coroutines-best-practices)
- [Common `Coroutine` Mistakes](https://elizarov.medium.com/top-10-coroutines-mistakes-42b19c2a25b2)

## Связанные Вопросы (RU)

- [[q-coroutine-exception-handler--kotlin--medium|Использование CoroutineExceptionHandler]]
- [[q-debugging-coroutines-techniques--kotlin--medium|Отладка корутин]]
- [[q-mutex-synchronized-coroutines--kotlin--medium|Потокобезопасные корутины]]

## Related Questions

- [[q-coroutine-exception-handler--kotlin--medium|CoroutineExceptionHandler usage]]
- [[q-debugging-coroutines-techniques--kotlin--medium|Debugging coroutines]]
- [[q-mutex-synchronized-coroutines--kotlin--medium|Thread-safe coroutines]]
