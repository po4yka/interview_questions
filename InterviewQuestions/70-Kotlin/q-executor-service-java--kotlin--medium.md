---
anki_cards:
- slug: q-executor-service-java--kotlin--medium-0-en
  language: en
  anki_id: 1768326293381
  synced_at: '2026-01-23T17:03:51.597449'
- slug: q-executor-service-java--kotlin--medium-0-ru
  language: ru
  anki_id: 1768326293406
  synced_at: '2026-01-23T17:03:51.598319'
---
# Question (EN)
> How do `Executor` and ExecutorService work in Java?

## Ответ (RU)

`Executor` — это интерфейс из библиотеки `java.util.concurrent`, который представляет собой абстракцию для запуска задач. Он позволяет отделить создание задач от их выполнения, обеспечивая гибкость и контроль над выполнением параллельных операций.

### 1. Базовый Интерфейс Executor

```java
public interface Executor {
    void execute(Runnable command);
}

// Простейшая реализация - прямое выполнение
class DirectExecutor implements Executor {
    @Override
    public void execute(Runnable command) {
        command.run(); // Выполняется в текущем потоке
    }
}

// Выполнение в новом потоке
class ThreadPerTaskExecutor implements Executor {
    @Override
    public void execute(Runnable command) {
        new Thread(command).start();
    }
}

// Использование
Executor executor = new ThreadPerTaskExecutor();
executor.execute(() -> System.out.println("Task executed"));
```

### 2. ExecutorService

Расширяет `Executor` и добавляет методы для управления жизненным циклом и получения результатов.

```java
public interface ExecutorService extends Executor {
    // Управление жизненным циклом
    void shutdown();
    List<Runnable> shutdownNow();
    boolean isShutdown();
    boolean isTerminated();
    boolean awaitTermination(long timeout, TimeUnit unit) throws InterruptedException;

    // Выполнение задач с результатом
    <T> Future<T> submit(Callable<T> task);
    Future<?> submit(Runnable task);
    <T> Future<T> submit(Runnable task, T result);

    // Массовое выполнение
    <T> List<Future<T>> invokeAll(Collection<? extends Callable<T>> tasks) throws InterruptedException;
    <T> T invokeAny(Collection<? extends Callable<T>> tasks) throws InterruptedException, ExecutionException;
}
```

**Пример использования:**

```java
// Создание ExecutorService
ExecutorService executor = Executors.newFixedThreadPool(4);

try {
    // Submit задачи с результатом (Callable)
    Future<Integer> future = executor.submit(() -> {
        Thread.sleep(1000);
        return 42;
    });

    // Получить результат (блокирующий вызов)
    Integer result = future.get();
    System.out.println("Result: " + result);

    // Submit задачи без результата (Runnable)
    executor.submit(() -> {
        System.out.println("Task executed in: " + Thread.currentThread().getName());
    });

    // Execute (метод из Executor)
    executor.execute(() -> {
        System.out.println("Another task");
    });

} finally {
    // Graceful shutdown
    executor.shutdown();

    // Ждать завершения всех задач
    try {
        if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
            executor.shutdownNow(); // Force shutdown
        }
    } catch (InterruptedException e) {
        executor.shutdownNow();
        Thread.currentThread().interrupt();
    }
}
```

### 3. Типы ExecutorService

#### FixedThreadPool

Пул с фиксированным количеством потоков.

```java
// Создать пул с 4 потоками
ExecutorService executor = Executors.newFixedThreadPool(4);

// Отправить 10 задач - одновременно будет выполняться не более 4 задач
for (int i = 0; i < 10; i++) {
    final int taskId = i;
    executor.submit(() -> {
        System.out.println("Task " + taskId + " on " + Thread.currentThread().getName());
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return taskId; // Используем Callable, чтобы показать возвращаемое значение
    });
}

executor.shutdown();
```

**Use case**: Ограничение одновременных операций, например, параллельных сетевых запросов.

#### CachedThreadPool

Создает новые потоки по мере необходимости, переиспользует существующие.

```java
ExecutorService executor = Executors.newCachedThreadPool();

// Отправить много коротких задач
for (int i = 0; i < 100; i++) {
    executor.submit(() -> {
        // Короткая задача
        System.out.println("Quick task on " + Thread.currentThread().getName());
    });
}

executor.shutdown();
```

**Use case**: Много коротких асинхронных задач. Потоки переиспользуются, неактивные потоки завершаются (по умолчанию keep-alive около 60 секунд).

#### SingleThreadExecutor

Один поток для последовательного выполнения задач.

```java
ExecutorService executor = Executors.newSingleThreadExecutor();

// Все задачи выполняются последовательно в одном потоке
executor.submit(() -> System.out.println("Task 1"));
executor.submit(() -> System.out.println("Task 2"));
executor.submit(() -> System.out.println("Task 3"));

executor.shutdown();
```

**Use case**: Гарантированная последовательность выполнения (альтернатива ручной синхронизации для некоторого состояния).

#### ScheduledThreadPool

Для отложенных и периодических задач.

```java
ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);

// Запустить через 5 секунд
scheduler.schedule(() -> {
    System.out.println("Delayed task");
}, 5, TimeUnit.SECONDS);

// Повторять каждые 3 секунды (фиксированный период от старта предыдущей задачи)
scheduler.scheduleAtFixedRate(() -> {
    System.out.println("Periodic task: " + System.currentTimeMillis());
}, 0, 3, TimeUnit.SECONDS); // initialDelay=0, period=3

// Повторять с задержкой 2 секунды после завершения предыдущей
scheduler.scheduleWithFixedDelay(() -> {
    System.out.println("Task with delay");
    try {
        Thread.sleep(1000); // Задача занимает ~1 сек
    } catch (InterruptedException e) {
        Thread.currentThread().interrupt();
    }
}, 0, 2, TimeUnit.SECONDS); // Следующий запуск планируется через 2 сек после завершения предыдущего

// Остановить через 30 секунд
scheduler.schedule(() -> {
    scheduler.shutdown();
}, 30, TimeUnit.SECONDS);
```

**Use case**: Периодическое обновление данных, polling, отложенные уведомления.

### 4. Future И Callable

#### Callable - Задача С Результатом

```java
Callable<String> task = () -> {
    Thread.sleep(2000);
    return "Result from task";
};

ExecutorService executor = Executors.newSingleThreadExecutor();
Future<String> future = executor.submit(task);

// Проверить статус
System.out.println("Is done: " + future.isDone());
System.out.println("Is cancelled: " + future.isCancelled());

// Получить результат (блокирует до завершения)
try {
    String result = future.get(); // Блокирующий вызов
    System.out.println("Result: " + result);
} catch (ExecutionException e) {
    // Задача выбросила исключение
    System.err.println("Task failed: " + e.getCause());
} catch (InterruptedException e) {
    // Поток был прерван во время ожидания
    Thread.currentThread().interrupt();
}

executor.shutdown();
```

#### Future С Timeout

```java
ExecutorService executor = Executors.newSingleThreadExecutor();

Future<String> future = executor.submit(() -> {
    Thread.sleep(5000);
    return "Late result";
});

try {
    // Ждать максимум 2 секунды
    String result = future.get(2, TimeUnit.SECONDS);
} catch (TimeoutException e) {
    System.out.println("Task took too long");
    future.cancel(true); // Прервать задачу (если поддерживает прерывание)
} catch (InterruptedException | ExecutionException e) {
    Thread.currentThread().interrupt();
}

executor.shutdown();
```

#### Отмена Задач

```java
ExecutorService executor = Executors.newSingleThreadExecutor();

Future<Integer> future = executor.submit(() -> {
    for (int i = 0; i < 100; i++) {
        if (Thread.currentThread().isInterrupted()) {
            System.out.println("Task was cancelled");
            return -1;
        }
        try {
            Thread.sleep(100);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return -1;
        }
    }
    return 100;
});

// Отменить через 1 секунду
Thread.sleep(1000);
future.cancel(true); // true = попытаться прервать, если задача уже запущена

executor.shutdown();
```

### 5. invokeAll И invokeAny

#### invokeAll - Выполнить Все Задачи

```java
List<Callable<Integer>> tasks = Arrays.asList(
    () -> { Thread.sleep(1000); return 1; },
    () -> { Thread.sleep(2000); return 2; },
    () -> { Thread.sleep(500); return 3; }
);

ExecutorService executor = Executors.newFixedThreadPool(3);

// Выполнить все и дождаться завершения всех
List<Future<Integer>> futures = executor.invokeAll(tasks);

// Получить результаты
for (Future<Integer> future : futures) {
    System.out.println("Result: " + future.get());
}

executor.shutdown();
```

#### invokeAny - Выполнить Пока Одна Не Завершится

```java
List<Callable<String>> tasks = Arrays.asList(
    () -> { Thread.sleep(3000); return "Slow task"; },
    () -> { Thread.sleep(1000); return "Fast task"; },
    () -> { Thread.sleep(2000); return "Medium task"; }
);

ExecutorService executor = Executors.newFixedThreadPool(3);

// Вернуть результат первой успешно завершенной задачи
// Остальные будут отменены и/или прерваны (в зависимости от реализации и кода задач)
String result = executor.invokeAny(tasks);
System.out.println("First result: " + result); // Ожидаемо "Fast task"

executor.shutdown();
```

### 6. Кастомная Конфигурация ThreadPoolExecutor

```java
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    2,                      // corePoolSize - минимум потоков
    4,                      // maximumPoolSize - максимум потоков
    60L,                    // keepAliveTime
    TimeUnit.SECONDS,       // единица времени
    new LinkedBlockingQueue<>(100), // очередь задач
    new ThreadFactory() {   // фабрика потоков
        private final AtomicInteger counter = new AtomicInteger(0);

        @Override
        public Thread newThread(Runnable r) {
            Thread thread = new Thread(r, "MyPool-" + counter.incrementAndGet());
            thread.setDaemon(false);
            return thread;
        }
    },
    new ThreadPoolExecutor.CallerRunsPolicy() // политика отклонения
);

// Отправить задачи
for (int i = 0; i < 200; i++) {
    final int taskId = i;
    executor.execute(() -> {
        System.out.println("Task " + taskId + " on " + Thread.currentThread().getName());
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    });
}

// Статистика (могут измениться к моменту вызова)
System.out.println("Active threads: " + executor.getActiveCount());
System.out.println("Pool size: " + executor.getPoolSize());
System.out.println("Queue size: " + executor.getQueue().size());

executor.shutdown();
```

### 7. Rejection Policies

Политики обработки, когда очередь заполнена и пул не может принять новую задачу:

```java
// 1. AbortPolicy (по умолчанию) - выбросить RejectedExecutionException
new ThreadPoolExecutor.AbortPolicy();

// 2. CallerRunsPolicy - выполнить в вызывающем потоке
new ThreadPoolExecutor.CallerRunsPolicy();

// 3. DiscardPolicy - тихо отбросить задачу
new ThreadPoolExecutor.DiscardPolicy();

// 4. DiscardOldestPolicy - отбросить самую старую задачу в очереди и попробовать добавить новую
new ThreadPoolExecutor.DiscardOldestPolicy();

// 5. Custom policy
new RejectedExecutionHandler() {
    @Override
    public void rejectedExecution(Runnable r, ThreadPoolExecutor executor) {
        // Логирование, метрики, retry логика
        System.err.println("Task rejected: " + r);
    }
};
```

### 8. Android Использование

```kotlin
// Android - пример использования Executor для фоновых задач в Java-стиле
class UserRepository(private val apiService: ApiService) {
    private val executor = Executors.newFixedThreadPool(4)

    fun loadUsers(callback: (List<User>) -> Unit) {
        executor.submit {
            try {
                val users = apiService.getUsers()
                // Вернуться в main thread
                Handler(Looper.getMainLooper()).post {
                    callback(users)
                }
            } catch (e: Exception) {
                // TODO: handle error / callback on error
            }
        }
    }

    fun shutdown() {
        executor.shutdown()
    }
}

// На практике в Android для долгоживущих и UI-связанных задач
// обычно предпочтительны Coroutines (Dispatchers.IO) или WorkManager.
// Executor полезен для простых случаев или Java-кода без корутин.
```

### Сравнительная Таблица

| Тип | Потоки | Use Case | Преимущества |
|-----|--------|----------|--------------|
| **FixedThreadPool** | Фиксированное кол-во | Ограничение параллелизма | Контроль ресурсов |
| **CachedThreadPool** | Динамическое | Много коротких задач | Переиспользование потоков |
| **SingleThreadExecutor** | 1 | Последовательное выполнение | Гарантия порядка |
| **ScheduledThreadPool** | Фиксированное кол-во | Отложенные/периодические задачи | Scheduling |

### Best Practices

```java
ExecutorService executor = Executors.newFixedThreadPool(4);

// 1. Всегда закрывать executor
executor.shutdown();
try {
    if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
        executor.shutdownNow();
    }
} catch (InterruptedException e) {
    executor.shutdownNow();
    Thread.currentThread().interrupt();
}

// 2. Использовать try-with-resources для Executor, реализующего AutoCloseable (например, Executors.newVirtualThreadPerTaskExecutor() в новых версиях Java)
try (ExecutorService vExecutor = Executors.newVirtualThreadPerTaskExecutor()) {
    vExecutor.submit(() -> System.out.println("Task"));
} // Автоматически закроется

// 3. Обрабатывать исключения в задачах
executor.submit(() -> {
    try {
        // Task logic
    } catch (Exception e) {
        // Log error
        logger.error("Task failed", e);
    }
});

// 4. Использовать CompletableFuture для композиции асинхронных операций (Java 8+)
CompletableFuture<String> future = CompletableFuture.supplyAsync(
    () -> "Hello",
    executor
).thenApply(s -> s + " World");
```

## Answer (EN)

`Executor` is an interface from `java.util.concurrent` with a single `execute(Runnable)` method that decouples task submission from execution.

### 1. Basic Executor Interface

```java
public interface Executor {
    void execute(Runnable command);
}

class DirectExecutor implements Executor {
    @Override
    public void execute(Runnable command) {
        command.run();
    }
}

class ThreadPerTaskExecutor implements Executor {
    @Override
    public void execute(Runnable command) {
        new Thread(command).start();
    }
}

Executor executor = new ThreadPerTaskExecutor();
executor.execute(() -> System.out.println("Task executed"));
```

### 2. ExecutorService

ExecutorService extends `Executor` and adds lifecycle management and result-bearing task APIs.

```java
public interface ExecutorService extends Executor {
    void shutdown();
    List<Runnable> shutdownNow();
    boolean isShutdown();
    boolean isTerminated();
    boolean awaitTermination(long timeout, TimeUnit unit) throws InterruptedException;

    <T> Future<T> submit(Callable<T> task);
    Future<?> submit(Runnable task);
    <T> Future<T> submit(Runnable task, T result);

    <T> List<Future<T>> invokeAll(Collection<? extends Callable<T>> tasks) throws InterruptedException;
    <T> T invokeAny(Collection<? extends Callable<T>> tasks) throws InterruptedException, ExecutionException;
}
```

Example usage:

```java
ExecutorService executor = Executors.newFixedThreadPool(4);

try {
    Future<Integer> future = executor.submit(() -> {
        Thread.sleep(1000);
        return 42;
    });

    Integer result = future.get();
    System.out.println("Result: " + result);

    executor.submit(() -> {
        System.out.println("Task executed in: " + Thread.currentThread().getName());
    });

    executor.execute(() -> {
        System.out.println("Another task");
    });

} finally {
    executor.shutdown();
    try {
        if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
            executor.shutdownNow();
        }
    } catch (InterruptedException e) {
        executor.shutdownNow();
        Thread.currentThread().interrupt();
    }
}
```

### 3. Types of ExecutorService

- FixedThreadPool: fixed number of threads, limits concurrency and controls resources.
- CachedThreadPool: creates threads as needed, reuses idle threads, good for many short tasks.
- SingleThreadExecutor: single worker thread, guarantees sequential execution.
- ScheduledThreadPool (ScheduledExecutorService): delayed and periodic task execution.

```java
// FixedThreadPool example
ExecutorService executor = Executors.newFixedThreadPool(4);
for (int i = 0; i < 10; i++) {
    final int taskId = i;
    executor.submit(() -> {
        System.out.println("Task " + taskId + " on " + Thread.currentThread().getName());
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
        return taskId;
    });
}
executor.shutdown();
```

```java
// CachedThreadPool example
ExecutorService cached = Executors.newCachedThreadPool();
for (int i = 0; i < 100; i++) {
    cached.submit(() -> System.out.println("Quick task on " + Thread.currentThread().getName()));
}
cached.shutdown();
```

```java
// SingleThreadExecutor example
ExecutorService single = Executors.newSingleThreadExecutor();
single.submit(() -> System.out.println("Task 1"));
single.submit(() -> System.out.println("Task 2"));
single.submit(() -> System.out.println("Task 3"));
single.shutdown();
```

```java
// ScheduledThreadPool example
ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);

scheduler.schedule(() -> System.out.println("Delayed task"), 5, TimeUnit.SECONDS);

scheduler.scheduleAtFixedRate(
    () -> System.out.println("Periodic task: " + System.currentTimeMillis()),
    0,
    3,
    TimeUnit.SECONDS
);

scheduler.scheduleWithFixedDelay(
    () -> {
        System.out.println("Task with delay");
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    },
    0,
    2,
    TimeUnit.SECONDS
);
```

### 4. Future and Callable

```java
Callable<String> task = () -> {
    Thread.sleep(2000);
    return "Result from task";
};

ExecutorService executor = Executors.newSingleThreadExecutor();
Future<String> future = executor.submit(task);

System.out.println("Is done: " + future.isDone());
System.out.println("Is cancelled: " + future.isCancelled());

try {
    String result = future.get();
    System.out.println("Result: " + result);
} catch (ExecutionException e) {
    System.err.println("Task failed: " + e.getCause());
} catch (InterruptedException e) {
    Thread.currentThread().interrupt();
}

executor.shutdown();
```

Timeout example:

```java
ExecutorService executor = Executors.newSingleThreadExecutor();

Future<String> future = executor.submit(() -> {
    Thread.sleep(5000);
    return "Late result";
});

try {
    String result = future.get(2, TimeUnit.SECONDS);
} catch (TimeoutException e) {
    System.out.println("Task took too long");
    future.cancel(true);
} catch (InterruptedException | ExecutionException e) {
    Thread.currentThread().interrupt();
}

executor.shutdown();
```

Cancellation example:

```java
ExecutorService executor = Executors.newSingleThreadExecutor();

Future<Integer> future = executor.submit(() -> {
    for (int i = 0; i < 100; i++) {
        if (Thread.currentThread().isInterrupted()) {
            System.out.println("Task was cancelled");
            return -1;
        }
        try {
            Thread.sleep(100);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
            return -1;
        }
    }
    return 100;
});

Thread.sleep(1000);
future.cancel(true);

executor.shutdown();
```

### 5. invokeAll and invokeAny

```java
List<Callable<Integer>> tasks = Arrays.asList(
    () -> { Thread.sleep(1000); return 1; },
    () -> { Thread.sleep(2000); return 2; },
    () -> { Thread.sleep(500); return 3; }
);

ExecutorService executor = Executors.newFixedThreadPool(3);
List<Future<Integer>> futures = executor.invokeAll(tasks);

for (Future<Integer> f : futures) {
    System.out.println("Result: " + f.get());
}

executor.shutdown();
```

```java
List<Callable<String>> tasks2 = Arrays.asList(
    () -> { Thread.sleep(3000); return "Slow task"; },
    () -> { Thread.sleep(1000); return "Fast task"; },
    () -> { Thread.sleep(2000); return "Medium task"; }
);

ExecutorService exec2 = Executors.newFixedThreadPool(3);
String first = exec2.invokeAny(tasks2);
System.out.println("First result: " + first);
exec2.shutdown();
```

### 6. Custom ThreadPoolExecutor Configuration

```java
ThreadPoolExecutor executor = new ThreadPoolExecutor(
    2,
    4,
    60L,
    TimeUnit.SECONDS,
    new LinkedBlockingQueue<>(100),
    new ThreadFactory() {
        private final AtomicInteger counter = new AtomicInteger(0);

        @Override
        public Thread newThread(Runnable r) {
            Thread t = new Thread(r, "MyPool-" + counter.incrementAndGet());
            t.setDaemon(false);
            return t;
        }
    },
    new ThreadPoolExecutor.CallerRunsPolicy()
);

for (int i = 0; i < 200; i++) {
    final int taskId = i;
    executor.execute(() -> {
        System.out.println("Task " + taskId + " on " + Thread.currentThread().getName());
        try {
            Thread.sleep(1000);
        } catch (InterruptedException e) {
            Thread.currentThread().interrupt();
        }
    });
}

System.out.println("Active threads: " + executor.getActiveCount());
System.out.println("Pool size: " + executor.getPoolSize());
System.out.println("Queue size: " + executor.getQueue().size());

executor.shutdown();
```

### 7. Rejection Policies

```java
new ThreadPoolExecutor.AbortPolicy();      // throws RejectedExecutionException
new ThreadPoolExecutor.CallerRunsPolicy(); // runs in caller thread
new ThreadPoolExecutor.DiscardPolicy();    // silently discards
new ThreadPoolExecutor.DiscardOldestPolicy(); // drops oldest then retries

new RejectedExecutionHandler() {
    @Override
    public void rejectedExecution(Runnable r, ThreadPoolExecutor executor) {
        System.err.println("Task rejected: " + r);
    }
};
```

### 8. Android Usage

```kotlin
class UserRepository(private val apiService: ApiService) {
    private val executor = Executors.newFixedThreadPool(4)

    fun loadUsers(callback: (List<User>) -> Unit) {
        executor.submit {
            try {
                val users = apiService.getUsers()
                Handler(Looper.getMainLooper()).post {
                    callback(users)
                }
            } catch (e: Exception) {
                // handle error
            }
        }
    }

    fun shutdown() {
        executor.shutdown()
    }
}

// In modern Android code prefer Kotlin coroutines (Dispatchers.IO) or WorkManager
// for long-running, structured, or deferrable work, using Executors mainly for
// interoperability with existing Java-style APIs.
```

### Comparative Table

| Type | Threads | Use Case | Advantages |
|------|---------|----------|------------|
| FixedThreadPool | Fixed number | Limit parallelism | Resource control |
| CachedThreadPool | Dynamic | Many short tasks | `Thread` reuse |
| SingleThreadExecutor | 1 | Sequential execution | Ordering guarantees |
| ScheduledThreadPool | Fixed number | Delayed/periodic tasks | Scheduling support |

### Best Practices

```java
ExecutorService executor = Executors.newFixedThreadPool(4);

// Always shut down
executor.shutdown();
try {
    if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
        executor.shutdownNow();
    }
} catch (InterruptedException e) {
    executor.shutdownNow();
    Thread.currentThread().interrupt();
}

// Use try-with-resources for AutoCloseable executors (e.g. virtual thread executor)
try (ExecutorService vExecutor = Executors.newVirtualThreadPerTaskExecutor()) {
    vExecutor.submit(() -> System.out.println("Task"));
}

// Handle exceptions inside tasks
executor.submit(() -> {
    try {
        // Task logic
    } catch (Exception e) {
        logger.error("Task failed", e);
    }
});

// Use CompletableFuture for async composition
CompletableFuture<String> future = CompletableFuture
    .supplyAsync(() -> "Hello", executor)
    .thenApply(s -> s + " World");
```

---

## Follow-ups

- When would you choose a specific ExecutorService type (fixed, cached, single, scheduled) in practice?
- How does this compare to using threads directly?
- What are common pitfalls (thread leaks, deadlocks, blocking in shared pools, lost interruptions)?

## References

- [[c-kotlin]]

## Related Questions

- [[q-kotlin-inline-functions--kotlin--medium]]
- [[q-kotlin-partition-function--kotlin--easy]]
