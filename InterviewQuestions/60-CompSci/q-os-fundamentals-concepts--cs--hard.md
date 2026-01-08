---\
id: cs-004
title: "Operating System Fundamentals / Основы операционных систем"
aliases: ["OS Fundamentals", "Основы ОС"]
topic: cs
subtopics: [memory-management, operating-systems, processes]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-computer-science, q-abstract-class-purpose--cs--medium]
created: 2025-10-12
updated: 2025-11-11
tags: [cpu-scheduling, difficulty/hard, memory, os, processes, threads, virtual-memory]
sources: ["https://en.wikipedia.org/wiki/Operating_system"]

---\
# Вопрос (RU)
> Что такое основные концепции операционных систем? Как работают процессы и потоки, виртуальная память и планирование CPU?

# Question (EN)
> What are the core OS concepts? How do processes, threads, virtual memory, and CPU scheduling work?

---

## Ответ (RU)

**Теория OS Fundamentals:**
Operating Systems управляют аппаратными ресурсами, предоставляют уровни абстракции, обеспечивают параллельное/псевдопараллельное выполнение. Базовые концепции: Process (изолированная единица выполнения), `Thread` (легковесный поток выполнения внутри процесса), Virtual Memory (абстракция адресного пространства), CPU Scheduling (распределение процессорного времени), System Calls (сервисы ядра), IPC (межпроцессное взаимодействие), Deadlock (взаимная блокировка).

**Процессы vs Потоки:**

*Теория:* Process — программа в выполнении, собственное виртуальное адресное пространство и ресурсы. `Thread` — легковесный поток внутри процесса, разделяет память процесса. Process: более независим, «тяжёлый», более дорогой контекстный переключатель, взаимодействует с другими процессами через IPC. `Thread`: общая память внутри процесса, «легкий», контекстный переключатель дешевле, обмен данными через общие структуры (но требуется синхронизация). Ключевое отличие: изоляция vs разделение.

```kotlin
// ✅ Process: отдельное (обычно) изолированное адресное пространство
// Типичное Android-приложение запускается в отдельном Linux-процессе
// Каждый процесс имеет своё виртуальное адресное пространство
// Процессы взаимодействуют через IPC (например, Binder)

// ✅ Thread: общая память внутри процесса
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Main Thread (UI Thread)
        textView.text = "Hello"  // ✅ Безопасно для UI

        // Background Thread
        Thread {
            val data = fetchData()  // Фоновая работа
            runOnUiThread {
                textView.text = data  // Постинг на UI-поток
            }
        }.start()

        // ✅ Современный подход: Coroutines
        lifecycleScope.launch {
            val data = withContext(Dispatchers.IO) {
                fetchDataFromNetwork()
            }
            textView.text = data  // Обновление на главном потоке
        }
    }
}
```

**Состояния процесса:**

*Теория:* Базовый жизненный цикл процесса: NEW → READY → RUNNING → WAITING/BLOCKED → TERMINATED. Типичные переходы: прерывание (RUNNING → READY), ожидание ввода-вывода (RUNNING → WAITING), завершение ожидания/ввода-вывода (WAITING → READY), выбор планировщиком (READY → RUNNING). Android дополнительно вводит приоритеты процессов: FOREGROUND > VISIBLE > SERVICE > BACKGROUND > EMPTY.

**CPU Scheduling:**

*Теория:* Планировщик решает, какой процесс (или поток) будет выполняться дальше. Базовые алгоритмы: FCFS (First-Come First-Served), SJF (Shortest Job First), RR (Round Robin). Цели: справедливость, пропускная способность, время отклика, минимизация времени ожидания и накладных расходов на переключения. Важно различать:
- Невытесняющее (non-preemptive) планирование: задача выполняется до завершения или блокировки.
- Вытесняющее (preemptive) планирование: задача может быть принудительно остановлена по таймеру или событию и заменена другой.

**1. FCFS:**
*Теория:* Невытесняющий, процессы выполняются в порядке прихода. Прост, но страдает от convoy effect — короткие задачи ждут длинную. Пример: P1(24ms) → P2(3ms) → P3(3ms). Среднее ожидание: (0 + 24 + 27) / 3 = 17ms.

**2. SJF:**
*Теория:* Выбирает процесс с наименьшим временем выполнения. Оптимален по среднему времени ожидания, но возможна голодовка длинных задач. Пример: P2(3ms) → P3(3ms) → P1(24ms). Среднее ожидание: (0 + 3 + 6) / 3 = 3ms.

**3. Round Robin:**
*Теория:* Каждый процесс получает квантом времени (preemptive). Обеспечивает хорошее время отклика и ограничивает голодовку при разумном выборе кванта. Недостаток: повышенные накладные расходы из-за частых переключений контекста. Пример: quantum = 4ms, P1(24ms) требует 6 квантов, P2(3ms) — 1 кванта.

**Виртуальная память:**

*Теория:* Virtual Memory — абстракция, дающая каждому процессу большое непрерывное виртуальное адресное пространство. Преимущества: изоляция процессов (безопасность), возможность больше процессов, чем доступной физической памяти, эффективное использование памяти. Механизм: Virtual Address → MMU → Physical Address. Paging — разбиение адресного пространства на страницы (обычно 4KB), физическая память — на фреймы такого же размера.

```kotlin
// ✅ Пример виртуальной памяти
// Виртуальное адресное пространство: 0x0000 - 0xFFFF (64KB)
// Физическая память: 32KB (8 фреймов по 4KB)

// Таблица страниц:
// Virtual Page → Physical Frame
// 0 → 3
// 1 → 7
// 2 → 1
// 3 → (нет в памяти, на диске)

// Процесс обращается к 0x1000:
// 1. Номер страницы: 0x1000 / 4KB = страница 0
// 2. Таблица страниц: страница 0 → фрейм 3
// 3. Физический адрес: (фрейм 3 × 4KB) + смещение
// 4. Доступ к физической памяти
```

**Page Fault:**

*Теория:* Page Fault — обращение к странице, отсутствующей в текущем отображении. Для major page fault (страница на диске): сохранить состояние, найти свободный или освободить фрейм, загрузить страницу с диска, обновить таблицу страниц, возобновить процесс. Это позволяет иметь память «больше» физической, но обращение к диску очень медленное. (Minor page fault — когда данные уже в памяти, но требуют обновления структур, существенно дешевле.)

**System Calls:**

*Теория:* System `Call` — запрос к ядру ОС на выполнение операции от имени процесса. Категории: Process Control (fork, exec, exit), File Management (open, read, write), Device Management (ioctl), Information Maintenance (getpid, alarm), Communication (pipe, socket), Protection (chmod). Выполнение: переход из user mode в kernel mode и обратно.

```kotlin
// ✅ Поток системных вызовов
// Высокоуровневое API:
val file = File("data.txt")
file.writeText("Hello")

// Под капотом (упрощенно):
// 1. open("data.txt", O_WRONLY|O_CREAT, 0644)  // системный вызов
// 2. write(fd, "Hello", 5)                      // системный вызов
// 3. close(fd)                                   // системный вызов

// User Mode → Kernel Mode → User Mode
```

**IPC (Inter-Process Communication):**

*Теория:* IPC — взаимодействие между процессами. Механизмы: Shared Memory (быстрый доступ, нужна синхронизация), `Message` Passing (например, Binder в Android), Pipes (однонаправленные локальные каналы), Sockets (двунаправленные, в том числе по сети), очереди сообщений и др. В Android Binder — основной механизм для обращения к системным сервисам и многим межпроцессным взаимодействиям, но приложения также могут использовать сокеты, контент-провайдеры и т.п.

```kotlin
// ✅ Пример Binder IPC (упрощенно)
class MyService : Service() {
    private val binder = object : IMyService.Stub() {
        override fun doSomething(data: String): String {
            return "Processed: $data"
        }
    }
    override fun onBind(intent: Intent): IBinder = binder
}

// Client
class ClientActivity : AppCompatActivity() {
    private val connection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName, binder: IBinder) {
            val service = IMyService.Stub.asInterface(binder)
            val result = service?.doSomething("Hello")
        }
        override fun onServiceDisconnected(name: ComponentName) { }
    }
}
```

**`Context` Switching:**

*Теория:* `Context` Switch — сохранение состояния текущего процесса/потока и загрузка состояния другого. Контекст включает: Program Counter, регистры CPU, состояние процесса, информацию об управлении памятью, статус I/O и др. Стоимость: накладные расходы на сохранение/восстановление состояния, возможное обновление отображений памяти, влияние на кеш/TLB. Типичные современные системы тратят на переключение микросекунды порядка 1–10 µs, но точное значение сильно зависит от архитектуры и нагрузки. Это чистые накладные расходы, необходимые для многозадачности.

**Deadlock:**

*Теория:* Deadlock — ситуация, когда набор процессов/потоков навсегда ждёт ресурсы, удерживаемые друг другом. Четыре необходимые условия: Mutual Exclusion (взаимное исключение), Hold and Wait (захват и ожидание), No Preemption (нет принудительного отъёма), Circular Wait (циклическое ожидание). Подходы:
- Prevention: гарантированно нарушить хотя бы одно из условий (например, строгий порядок захвата блокировок/ресурсов).
- Avoidance/Detection & Recovery: анализ состояний, тайм-ауты, откат транзакций, завершение/перезапуск некоторых процессов.

```kotlin
// ❌ Deadlock
val lock1 = ReentrantLock()
val lock2 = ReentrantLock()

// Thread 1: lock1.lock(), затем ожидание lock2
// Thread 2: lock2.lock(), затем ожидание lock1
// → Циклическое ожидание → DEADLOCK

// ✅ Prevention: строгий порядок блокировок
// Всегда брать lock1, затем lock2
thread {
    lock1.lock()
    lock2.lock()
    try {
        // Work
    } finally {
        lock2.unlock()
        lock1.unlock()
    }
}

// Нет циклического ожидания → deadlock исключён при соблюдении порядка
```

**Ключевые выводы:**
1. Process — изолированная единица выполнения с собственным виртуальным адресным пространством.
2. `Thread` — легковесный поток внутри процесса, разделяющий память; требует синхронизации.
3. Virtual Memory — абстракция адресного пространства для изоляции и эффективного использования памяти.
4. CPU Scheduling — определяет, какой процесс/поток выполняется далее; есть вытесняющие и невытесняющие алгоритмы.
5. System `Call` — запрос сервиса ядра (переход user → kernel → user mode).
6. `Context` Switch — сохранение/восстановление состояния (накладные расходы, зависящие от системы).
7. IPC — механизмы взаимодействия процессов (Binder в Android — основной системный механизм, но не единственный возможный).
8. Deadlock — взаимная блокировка; предотвращается нарушением условий (например, порядком захвата).
9. Page Fault — обращение к отсутствующей странице; major fault требует медленного I/O.
10. Paging — разбиение памяти на страницы фиксированного размера.

## Answer (EN)

**OS Fundamentals Theory:**
Operating Systems manage hardware resources, provide abstraction layers, and enable concurrent/multiprogrammed execution. Core concepts: Processes (isolated execution units), Threads (lightweight execution units within a process), Virtual Memory (address space abstraction), CPU Scheduling (CPU time allocation), System Calls (kernel services), IPC (Inter-Process Communication), Deadlock (circular waiting).

**Processes vs Threads:**

*Theory:* A process is a program in execution with its own virtual address space and resources. A thread is a lightweight execution unit within a process that shares the process address space. Process: more independent, heavyweight, context switch is more expensive, inter-process data exchange requires IPC. `Thread`: shares memory within the process, lightweight, cheaper context switches, data exchange via shared variables (requires synchronization). Key difference: isolation vs sharing.

```kotlin
// ✅ Process: typically its own isolated address space
// A typical Android app runs in its own Linux process
// Each process has its own virtual address space
// Processes communicate via IPC (e.g., Binder)

// ✅ Thread: shared memory within a process
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Main Thread (UI Thread)
        textView.text = "Hello"  // ✅ Safe for UI

        // Background Thread
        Thread {
            val data = fetchData()  // Background work
            runOnUiThread {
                textView.text = data  // Post update to UI thread
            }
        }.start()

        // ✅ Modern: Coroutines
        lifecycleScope.launch {
            val data = withContext(Dispatchers.IO) {
                fetchDataFromNetwork()
            }
            textView.text = data  // Update on main thread
        }
    }
}
```

**Process States:**

*Theory:* Basic process lifecycle: NEW → READY → RUNNING → WAITING/BLOCKED → TERMINATED. Typical transitions: interrupt (RUNNING → READY), I/O wait (RUNNING → WAITING), I/O completion/unblock (WAITING → READY), scheduler dispatch (READY → RUNNING). Android additionally classifies processes by importance: FOREGROUND > VISIBLE > SERVICE > BACKGROUND > EMPTY.

**CPU Scheduling:**

*Theory:* Scheduling decides which process (or thread) runs next. Classic algorithms: FCFS (First-Come First-Served), SJF (Shortest Job First), RR (Round Robin). Goals: fairness, throughput, response time, waiting time, and low context-switch overhead. Important distinction:
- Non-preemptive scheduling: a running task continues until it finishes or blocks.
- Preemptive scheduling: a running task can be interrupted (e.g., by a timer) and replaced.

**1. FCFS:**
*Theory:* Non-preemptive, runs processes in arrival order. Simple but suffers from convoy effect: short jobs wait behind long ones. Example: P1(24ms) → P2(3ms) → P3(3ms). Average waiting: (0 + 24 + 27) / 3 = 17ms.

**2. SJF:**
*Theory:* Runs the job with the shortest CPU burst next. Optimal average waiting time (assuming known burst lengths) but may cause starvation of long jobs. Example: P2(3ms) → P3(3ms) → P1(24ms). Average waiting: (0 + 3 + 6) / 3 = 3ms.

**3. Round Robin:**
*Theory:* Each process gets a time quantum, then is preempted and put back into the ready queue if not finished. Fair and provides good response time; with a reasonable quantum, it largely avoids starvation. Drawback: higher waiting time and overhead due to frequent context switches. Example: quantum=4ms, P1(24ms) needs 6 quanta, P2(3ms) 1 quantum.

**Virtual Memory:**

*Theory:* Virtual Memory provides each process with a large, contiguous virtual address space. Benefits: process isolation and protection, ability to run more processes than fit into physical RAM, efficient memory utilization. Mechanism: Virtual Address → MMU → Physical Address. Paging: divide virtual memory into pages (typically 4KB) and physical memory into frames of the same size.

```kotlin
// ✅ Virtual Memory Example
// Virtual Address Space: 0x0000 - 0xFFFF (64KB)
// Physical Memory: 32KB (8 frames of 4KB)

// Page Table:
// Virtual Page → Physical Frame
// 0 → 3
// 1 → 7
// 2 → 1
// 3 → (not in memory, on disk)

// Process accesses 0x1000:
// 1. Page number: 0x1000 / 4KB = Page 0
// 2. Look up: Page 0 → Frame 3
// 3. Physical address: (Frame 3 × 4KB) + offset
// 4. Access physical memory
```

**Page Fault:**

*Theory:* A Page Fault occurs when a referenced page is not present in the current mapping. For a major page fault (page only on disk): save state, find or free a frame, load the page from disk, update the page table, and resume the process — this is very slow due to disk I/O. A minor page fault (data already in memory but mappings need update) is much cheaper.

**System Calls:**

*Theory:* A System `Call` is a request to the OS kernel to perform an operation on behalf of a process. Categories: Process Control (fork, exec, exit), File Management (open, read, write), Device Management (ioctl), Information Maintenance (getpid, alarm), Communication (pipe, socket), Protection (chmod). Execution: transition from user mode to kernel mode and back.

```kotlin
// ✅ System Call Flow
// High-level: File API
val file = File("data.txt")
file.writeText("Hello")

// Behind the scenes (simplified):
// 1. open("data.txt", O_WRONLY|O_CREAT, 0644)  // system call
// 2. write(fd, "Hello", 5)                      // system call
// 3. close(fd)                                   // system call

// User Mode → Kernel Mode → User Mode
```

**IPC (Inter-Process Communication):**

*Theory:* IPC is communication between processes. Mechanisms: Shared Memory (fastest, requires synchronization), `Message` Passing (e.g., Binder on Android), Pipes (unidirectional local channels), Sockets (bidirectional, including over networks), message queues, etc. In Android, Binder is the primary mechanism for system services and much app-to-app IPC, but apps can also use sockets, content providers, and other mechanisms.

```kotlin
// ✅ Binder IPC Example (simplified)
class MyService : Service() {
    private val binder = object : IMyService.Stub() {
        override fun doSomething(data: String): String {
            return "Processed: $data"
        }
    }
    override fun onBind(intent: Intent): IBinder = binder
}

// Client
class ClientActivity : AppCompatActivity() {
    private val connection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName, binder: IBinder) {
            val service = IMyService.Stub.asInterface(binder)
            val result = service?.doSomething("Hello")
        }
        override fun onServiceDisconnected(name: ComponentName) { }
    }
}
```

**`Context` Switching:**

*Theory:* A `Context` Switch saves the state of the currently running process/thread and restores the state of another. `Context` includes: Program Counter, CPU registers, process state, memory management info, I/O status, etc. Cost: overhead for saving/restoring state, possible page table or address-space changes, cache/TLB effects. Typical modern systems may spend on the order of a few microseconds (e.g., ~1–10 µs), but actual cost varies widely by architecture and workload. This is pure overhead but essential for multitasking.

**Deadlock:**

*Theory:* Deadlock is a situation where a set of processes/threads wait indefinitely for resources held by each other. Four necessary conditions: Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait. Approaches:
- Prevention: structurally violate at least one condition (e.g., strict lock/resource ordering).
- Avoidance / Detection & Recovery: analyze resource allocation, use timeouts, rollbacks, or terminate/restart some participants.

```kotlin
// ❌ Deadlock
val lock1 = ReentrantLock()
val lock2 = ReentrantLock()

// Thread 1: lock1.lock(), then waits for lock2
// Thread 2: lock2.lock(), then waits for lock1
// → Circular wait → DEADLOCK

// ✅ Prevention: lock ordering
// Always acquire lock1 first, then lock2
thread {
    lock1.lock()
    lock2.lock()
    try {
        // Work
    } finally {
        lock2.unlock()
        lock1.unlock()
    }
}

// No circular wait → deadlock avoided when order is respected
```

**Key Takeaways:**
1. Process: isolated execution unit with its own virtual address space.
2. `Thread`: lightweight execution unit within a process sharing memory; requires synchronization.
3. Virtual Memory: address space abstraction for isolation and efficient memory use.
4. CPU Scheduling: decides which process/thread runs next; includes preemptive and non-preemptive algorithms.
5. System `Call`: request for a kernel service (user → kernel → user mode).
6. `Context` Switch: save/restore execution state (overhead; cost depends on system).
7. IPC: mechanisms for inter-process communication (Binder is Android’s primary system IPC mechanism, but not the only option).
8. Deadlock: circular wait; prevent/avoid by breaking necessary conditions (e.g., strict lock ordering).
9. Page Fault: access to a missing page; major faults involve slow disk I/O.
10. Paging: divides memory into fixed-size pages.

---

## Дополнительные Вопросы (RU)

- В чём разница между вытесняющим и невытесняющим планированием?
- Как работает механизм Low Memory Killer в Android?
- Что такое трешинг (thrashing) в виртуальной памяти?
- Чем семафоры отличаются от мьютексов?
- В чём суть задачи «Производитель–Потребитель»?

## Follow-ups

- What is the difference between preemptive and non-preemptive scheduling?
- How does the Android Low Memory Killer work?
- What is thrashing in virtual memory?
- How do semaphores differ from mutexes?
- What is the Producer-Consumer problem?

## Связанные Вопросы (RU)

### Предпосылки (проще)
- Базовые концепции компьютерных наук
- Понимание архитектуры вычислительных систем

### Связанные (тот Же уровень)
- Основы конкурентности
- Принципы ООП

### Продвинутые (сложнее)
- Продвинутые концепции ОС
- Распределённые системы
- Оптимизация производительности

## Related Questions

### Prerequisites (Easier)
- Basic computer science concepts
- Understanding of system architecture

### Related (Same Level)
- Concurrency fundamentals
- OOP principles

### Advanced (Harder)
- Advanced OS concepts
- Distributed systems
- Performance optimization

## Ссылки (RU)

- [[c-computer-science]]
- "Operating System Concepts" by Silberschatz, Galvin, Gagne
- [[moc-cs]]

## References

- [[c-computer-science]]
- "Operating System Concepts" by Silberschatz, Galvin, Gagne
- [[moc-cs]]
