---
tags:
  - kotlin
  - coroutines
  - error-handling
difficulty: medium
---

# В чем отличие между Job и SupervisorJob

**English**: What is the difference between Job and SupervisorJob?

## Answer

`Job` и `SupervisorJob` являются ключевыми понятиями, связанными с управлением жизненным циклом сопрограмм (корутин). Основное отличие заключается в обработке исключений в иерархии корутин.

### Job

Представляет собой базовый строительный блок управления жизненным циклом корутины и позволяет отменять задачи.

**Основная особенность**: Ошибка в одной из дочерних корутин приведет к отмене всех остальных корутин в этой иерархии.

```kotlin
val job = Job()
val scope = CoroutineScope(job)

scope.launch {
    // Дочерняя корутина 1
    delay(100)
    println("Child 1 completed")
}

scope.launch {
    // Дочерняя корутина 2
    throw Exception("Error!")  // ← Ошибка здесь
}

scope.launch {
    // Дочерняя корутина 3
    delay(200)
    println("Child 3 completed")  // ← НЕ выполнится
}

// Результат: Все корутины будут отменены из-за ошибки в Child 2
```

### SupervisorJob

Работает аналогично `Job`, но с ключевым отличием в обработке исключений.

**Основная особенность**: Позволяет дочерним корутинам завершаться независимо, так что сбой в одной корутине не приведет к отмене всей иерархии.

```kotlin
val supervisorJob = SupervisorJob()
val scope = CoroutineScope(supervisorJob)

scope.launch {
    // Дочерняя корутина 1
    delay(100)
    println("Child 1 completed")  // ✓ Выполнится
}

scope.launch {
    // Дочерняя корутина 2
    throw Exception("Error!")  // ← Ошибка только здесь
}

scope.launch {
    // Дочерняя корутина 3
    delay(200)
    println("Child 3 completed")  // ✓ Выполнится
}

// Результат: Только Child 2 завершится с ошибкой, остальные продолжат работу
```

### Ключевые отличия

| Аспект | Job | SupervisorJob |
|--------|-----|---------------|
| **Обработка исключений** | Ошибка в дочерней корутине отменяет все дочерние | Ошибка влияет только на отказавшую корутину |
| **Использование** | Когда нужна строгая связность задач | Когда задачи независимы друг от друга |
| **Применение** | Связанные операции (все или ничего) | Независимые фоновые задачи |

### Практическое применение

```kotlin
// Job - для связанных операций
fun loadUserProfile() = coroutineScope {
    val user = async { fetchUser() }
    val avatar = async { fetchAvatar() }
    val settings = async { fetchSettings() }

    // Если хотя бы одна операция провалится, всё отменится
    UserProfile(user.await(), avatar.await(), settings.await())
}

// SupervisorJob - для независимых операций
class BackgroundSyncManager {
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    fun startAll() {
        scope.launch { syncPhotos() }      // Независимая задача
        scope.launch { syncContacts() }    // Независимая задача
        scope.launch { syncMessages() }    // Независимая задача
        // Сбой одной не влияет на другие
    }
}
```

**English**: Job cancels all child coroutines if one fails. SupervisorJob allows child coroutines to fail independently without affecting siblings. Use Job for related operations (all-or-nothing), SupervisorJob for independent tasks.
