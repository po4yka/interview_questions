---
id: kotlin-218
title: "Executor Service Java / ExecutorService в Java"
aliases: [Executor, Service, Java]
topic: kotlin
subtopics: [access-modifiers, type-system, class-features]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [q-kotlin-data-sealed-classes-combined--programming-languages--medium, q-kotlin-inline-functions--kotlin--medium, q-kotlin-partition-function--programming-languages--easy]
created: 2025-10-15
updated: 2025-10-31
tags:
  - 
  - difficulty/medium
---
# Как работают Executor и ExecutorService?

# Question (EN)
> How does Executor and ExecutorService work in Java?

# Вопрос (RU)
> Как работают Executor и ExecutorService в Java?

---

## Answer (EN)

**Executor** is a basic interface with `execute(Runnable)` method for task execution. **ExecutorService** extends it with lifecycle management (`shutdown()`, `awaitTermination()`) and result-returning methods (`submit(Callable)`, `invokeAll()`, `invokeAny()`).

**Types:**
- **FixedThreadPool**: Fixed number of threads for controlled parallelism
- **CachedThreadPool**: Dynamic thread creation, reuses idle threads
- **SingleThreadExecutor**: One thread for sequential execution
- **ScheduledThreadPool**: Delayed and periodic task execution

**Future** represents async result with `get()`, `cancel()`, `isDone()`. **ThreadPoolExecutor** allows custom configuration (core/max pool size, queue, rejection policies). Always call `shutdown()` and handle exceptions in tasks.

---

## Ответ (RU)

`Executor` — это интерфейс из библиотеки `java.util.concurrent`, который представляет собой абстракцию для запуска задач. Он позволяет отделить создание задач от их выполнения, обеспечивая гибкость и контроль над выполнением параллельных операций.

### 1. Базовый интерфейс Executor

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
    boolean awaitTermination(long timeout, TimeUnit unit);

    // Выполнение задач с результатом
    <T> Future<T> submit(Callable<T> task);
    Future<?> submit(Runnable task);
    <T> Future<T> submit(Runnable task, T result);

    // Массовое выполнение
    <T> List<Future<T>> invokeAll(Collection<? extends Callable<T>> tasks);
    <T> T invokeAny(Collection<? extends Callable<T>> tasks);
}
```

**Пример использования:**

```java
// Создание ExecutorService
ExecutorService executor = Executors.newFixedThreadPool(4);

try {
    // Submit задачи с результатом
    Future<Integer> future = executor.submit(() -> {
        Thread.sleep(1000);
        return 42;
    });

    // Получить результат (блокирующий вызов)
    Integer result = future.get();
    System.out.println("Result: " + result);

    // Submit задачи без результата
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
    if (!executor.awaitTermination(60, TimeUnit.SECONDS)) {
        executor.shutdownNow(); // Force shutdown
    }
}
```

### 3. Типы ExecutorService

#### FixedThreadPool

Пул с фиксированным количеством потоков.

```java
// Создать пул с 4 потоками
ExecutorService executor = Executors.newFixedThreadPool(4);

// Отправить 10 задач - только 4 будут выполняться одновременно
for (int i = 0; i < 10; i++) {
    final int taskId = i;
    executor.submit(() -> {
        System.out.println("Task " + taskId + " on " + Thread.currentThread().getName());
        Thread.sleep(1000);
        return taskId;
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

**Use case**: Много коротких асинхронных задач. Потоки переиспользуются, неактивные убираются через 60 секунд.

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

**Use case**: Гарантированная последовательность выполнения (альтернатива synchronized блокам).

#### ScheduledThreadPool

Для отложенных и периодических задач.

```java
ScheduledExecutorService scheduler = Executors.newScheduledThreadPool(2);

// Запустить через 5 секунд
scheduler.schedule(() -> {
    System.out.println("Delayed task");
}, 5, TimeUnit.SECONDS);

// Повторять каждые 3 секунды
scheduler.scheduleAtFixedRate(() -> {
    System.out.println("Periodic task: " + System.currentTimeMillis());
}, 0, 3, TimeUnit.SECONDS); // initialDelay=0, period=3

// Повторять с задержкой 2 секунды после завершения предыдущей
scheduler.scheduleWithFixedDelay(() -> {
    System.out.println("Task with delay");
    Thread.sleep(1000); // Задача занимает 1 сек
}, 0, 2, TimeUnit.SECONDS); // Следующая через 1+2=3 сек после старта

// Остановить через 30 секунд
scheduler.schedule(() -> {
    scheduler.shutdown();
}, 30, TimeUnit.SECONDS);
```

**Use case**: Периодическое обновление данных, polling, отложенные уведомления.

### 4. Future и Callable

#### Callable - задача с результатом

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

#### Future с timeout

```java
Future<String> future = executor.submit(() -> {
    Thread.sleep(5000);
    return "Late result";
});

try {
    // Ждать максимум 2 секунды
    String result = future.get(2, TimeUnit.SECONDS);
} catch (TimeoutException e) {
    System.out.println("Task took too long");
    future.cancel(true); // Прервать задачу
}
```

#### Отмена задач

```java
Future<Integer> future = executor.submit(() -> {
    for (int i = 0; i < 100; i++) {
        if (Thread.currentThread().isInterrupted()) {
            System.out.println("Task was cancelled");
            return -1;
        }
        Thread.sleep(100);
    }
    return 100;
});

// Отменить через 1 секунду
Thread.sleep(1000);
future.cancel(true); // true = прервать поток если задача уже запущена
```

### 5. invokeAll и invokeAny

#### invokeAll - выполнить все задачи

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

#### invokeAny - выполнить пока одна не завершится

```java
List<Callable<String>> tasks = Arrays.asList(
    () -> { Thread.sleep(3000); return "Slow task"; },
    () -> { Thread.sleep(1000); return "Fast task"; },
    () -> { Thread.sleep(2000); return "Medium task"; }
);

ExecutorService executor = Executors.newFixedThreadPool(3);

// Вернуть результат первой завершенной задачи
// Остальные будут отменены
String result = executor.invokeAny(tasks);
System.out.println("First result: " + result); // "Fast task"

executor.shutdown();
```

### 6. Кастомная конфигурация ThreadPoolExecutor

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

// Статистика
System.out.println("Active threads: " + executor.getActiveCount());
System.out.println("Pool size: " + executor.getPoolSize());
System.out.println("Queue size: " + executor.getQueue().size());

executor.shutdown();
```

### 7. Rejection Policies

Политики обработки когда очередь заполнена:

```java
// 1. AbortPolicy (по умолчанию) - выбросить RejectedExecutionException
new ThreadPoolExecutor.AbortPolicy()

// 2. CallerRunsPolicy - выполнить в вызывающем потоке
new ThreadPoolExecutor.CallerRunsPolicy()

// 3. DiscardPolicy - тихо отбросить задачу
new ThreadPoolExecutor.DiscardPolicy()

// 4. DiscardOldestPolicy - отбросить самую старую задачу
new ThreadPoolExecutor.DiscardOldestPolicy()

// 5. Custom policy
new RejectedExecutionHandler() {
    @Override
    public void rejectedExecution(Runnable r, ThreadPoolExecutor executor) {
        // Логирование, метрики, retry логика
        System.err.println("Task rejected: " + r);
    }
}
```

### 8. Android использование

```kotlin
// Android - использовать Executors для фоновых задач
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
                // Handle error
            }
        }
    }

    fun shutdown() {
        executor.shutdown()
    }
}

// Современный подход - использовать Coroutines или WorkManager
// Executor подходит для простых случаев или Java кода
```

### Сравнительная таблица

| Тип | Потоки | Use Case | Преимущества |
|-----|--------|----------|--------------|
| **FixedThreadPool** | Фиксированное кол-во | Ограничение параллелизма | Контроль ресурсов |
| **CachedThreadPool** | Динамическое | Много коротких задач | Переиспользование |
| **SingleThreadExecutor** | 1 | Последовательное выполнение | Гарантия порядка |
| **ScheduledThreadPool** | Фиксированное кол-во | Отложенные/периодические | Scheduling |

### Best Practices

```java
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

// 2. Использовать try-with-resources (Java 19+)
try (ExecutorService executor = Executors.newVirtualThreadPerTaskExecutor()) {
    executor.submit(() -> System.out.println("Task"));
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

// 4. Использовать CompletableFuture для composition (Java 8+)
CompletableFuture<String> future = CompletableFuture.supplyAsync(
    () -> "Hello",
    executor
).thenApply(s -> s + " World");
```

## Related Questions

- [[q-kotlin-data-sealed-classes-combined--programming-languages--medium]]
- [[q-kotlin-inline-functions--kotlin--medium]]
- [[q-kotlin-partition-function--programming-languages--easy]]
