---
id: cs-004
title: "Operating System Fundamentals / Основы операционных систем"
aliases: ["OS Fundamentals", "Основы ОС"]
topic: cs
subtopics: [cpu-scheduling, memory-management, operating-systems, processes, threads]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [q-concurrency-fundamentals--computer-science--hard, q-oop-principles-deep-dive--computer-science--medium]
created: 2025-10-12
updated: 2025-01-25
tags: [cpu-scheduling, difficulty/hard, memory, os, processes, threads, virtual-memory]
sources: [https://en.wikipedia.org/wiki/Operating_system]
---

# Вопрос (RU)
> Что такое основные концепции операционных систем? Как работают процессы и потоки, виртуальная память и планирование CPU?

# Question (EN)
> What are the core OS concepts? How do processes, threads, virtual memory, and CPU scheduling work?

---

## Ответ (RU)

**Теория OS Fundamentals:**
Operating Systems manage hardware resources, provide abstraction layers, enable concurrent execution. Core concepts: Processes (isolated execution units), Threads (lightweight processes), Virtual Memory (address space abstraction), CPU Scheduling (resource allocation), System Calls (kernel services), IPC (Inter-Process Communication), Deadlock (circular waiting).

**Процессы vs Потоки:**

*Теория:* Process - program in execution, isolated memory space, own resources. Thread - lightweight process within process, shared memory. Process: independent, heavyweight, slow context switch, IPC required. Thread: shared memory, lightweight, fast context switch, no IPC needed. Key difference: isolation vs sharing.

```kotlin
// ✅ Process: Isolated memory space
// Android app runs in separate Linux process
// Each app has its own address space
// Processes communicate via IPC (Binder)

// ✅ Thread: Shared memory within process
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Main Thread (UI Thread)
        textView.text = "Hello"  // ✅ Safe

        // Background Thread
        Thread {
            val data = fetchData()  // Background work
            runOnUiThread {
                textView.text = data  // Post to UI thread
            }
        }.start()

        // ✅ Modern: Coroutines
        lifecycleScope.launch {
            val data = withContext(Dispatchers.IO) {
                fetchDataFromNetwork()
            }
            textView.text = data  // Main thread
        }
    }
}
```

**Состояния процесса:**

*Теория:* Process lifecycle: NEW → READY → RUNNING → WAITING → TERMINATED. State transitions: interrupt (RUNNING → READY), I/O wait (RUNNING → WAITING), scheduler dispatch (READY → RUNNING). Android process importance: FOREGROUND > VISIBLE > SERVICE > BACKGROUND > EMPTY.

**CPU Scheduling:**

*Теория:* Scheduling - decide which process runs next. Algorithms: FCFS (First-Come First-Served), SJF (Shortest Job First), RR (Round Robin). Goals: fairness, throughput, response time, waiting time. Trade-offs: convoy effect vs starvation vs overhead.

**1. FCFS:**
*Теория:* Non-preemptive, execute processes in arrival order. Simple but convoy effect - short processes wait for long ones. Example: P1(24ms) → P2(3ms) → P3(3ms). Average waiting: (0 + 24 + 27) / 3 = 17ms.

**2. SJF:**
*Теория:* Execute shortest process first. Optimal average waiting time but starvation - long processes never execute. Example: P2(3ms) → P3(3ms) → P1(24ms). Average: (0 + 3 + 6) / 3 = 3ms.

**3. Round Robin:**
*Теория:* Each process gets time quantum, then preempted. Fair, no starvation, good response time. Higher waiting time due to context switches. Example: quantum=4ms, P1(24ms) requires 6 quanta, P2(3ms) 1 quantum.

**Виртуальная память:**

*Теория:* Virtual Memory - abstraction providing large, contiguous address space. Benefits: process isolation (security), more processes than physical RAM, efficient memory use. Mechanism: Virtual Address → MMU → Physical Address. Paging - divide memory into pages (typically 4KB). Physical memory divided into frames (same size).

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

*Теория:* Page Fault - referenced page not in physical memory. Steps: save state, find free frame, load from disk, update page table, resume process. Allows more processes than RAM but slow (disk I/O).

**System Calls:**

*Теория:* System Call - request to OS kernel for service. Categories: Process Control (fork, exec, exit), File Management (open, read, write), Device Management (ioctl), Information Maintenance (getpid, alarm), Communication (pipe, socket), Protection (chmod). User mode → Kernel mode → User mode.

```kotlin
// ✅ System Call Flow
// High-level: File API
val file = File("data.txt")
file.writeText("Hello")

// Behind scenes:
// 1. open("data.txt", O_WRONLY|O_CREAT, 0644)  // System call
// 2. write(fd, "Hello", 5)  // System call
// 3. close(fd)  // System call

// User Mode → Kernel Mode → User Mode
```

**IPC (Inter-Process Communication):**

*Теория:* IPC - communication between processes. Mechanisms: Shared Memory (fastest, direct access), Message Passing (Binder in Android), Pipes (unidirectional), Sockets (bidirectional, network). Android uses Binder for all inter-app communication.

```kotlin
// ✅ Binder IPC Example
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

**Context Switching:**

*Теория:* Context Switch - save current process state, load another. Context includes: Program Counter, CPU Registers, Process State, Memory Management Info, I/O Status. Cost: save/restore registers, update memory mappings, cache/TLB invalidation (1-10 microseconds). Pure overhead but necessary for multitasking.

**Deadlock:**

*Теория:* Deadlock - processes waiting for each other indefinitely. Four necessary conditions: Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait. Prevention: lock ordering (always acquire in same order), timeout, resource hierarchy.

```kotlin
// ❌ Deadlock
val lock1 = ReentrantLock()
val lock2 = ReentrantLock()

// Thread 1: lock1.lock(), wait lock2
// Thread 2: lock2.lock(), wait lock1
// → Circular wait → DEADLOCK

// ✅ Prevention: Lock ordering
// Always: lock1 first, then lock2
thread {
    lock1.lock()
    lock2.lock()
    // Work
    lock2.unlock()
    lock1.unlock()
}

// No circular wait → No deadlock
```

**Ключевые выводы:**
1. Process - isolated execution with own memory space
2. Thread - lightweight process with shared memory
3. Virtual Memory - address space abstraction for isolation
4. CPU Scheduling - determine which process runs next
5. System Call - request kernel service (user→kernel mode)
6. Context Switch - save/load process state (overhead)
7. IPC - communication between processes (Binder in Android)
8. Deadlock - circular wait, prevent with lock ordering
9. Page Fault - slow disk I/O for memory access
10. Paging - divide memory into fixed-size pages

## Answer (EN)

**OS Fundamentals Theory:**
Operating Systems manage hardware resources, provide abstraction layers, enable concurrent execution. Core concepts: Processes (isolated execution units), Threads (lightweight processes), Virtual Memory (address space abstraction), CPU Scheduling (resource allocation), System Calls (kernel services), IPC (Inter-Process Communication), Deadlock (circular waiting).

**Processes vs Threads:**

*Theory:* Process - program in execution, isolated memory space, own resources. Thread - lightweight process within process, shared memory. Process: independent, heavyweight, slow context switch, IPC required. Thread: shared memory, lightweight, fast context switch, no IPC needed. Key difference: isolation vs sharing.

```kotlin
// ✅ Process: Isolated memory space
// Android app runs in separate Linux process
// Each app has its own address space
// Processes communicate via IPC (Binder)

// ✅ Thread: Shared memory within process
class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Main Thread (UI Thread)
        textView.text = "Hello"  // ✅ Safe

        // Background Thread
        Thread {
            val data = fetchData()  // Background work
            runOnUiThread {
                textView.text = data  // Post to UI thread
            }
        }.start()

        // ✅ Modern: Coroutines
        lifecycleScope.launch {
            val data = withContext(Dispatchers.IO) {
                fetchDataFromNetwork()
            }
            textView.text = data  // Main thread
        }
    }
}
```

**Process States:**

*Theory:* Process lifecycle: NEW → READY → RUNNING → WAITING → TERMINATED. State transitions: interrupt (RUNNING → READY), I/O wait (RUNNING → WAITING), scheduler dispatch (READY → RUNNING). Android process importance: FOREGROUND > VISIBLE > SERVICE > BACKGROUND > EMPTY.

**CPU Scheduling:**

*Theory:* Scheduling - decide which process runs next. Algorithms: FCFS (First-Come First-Served), SJF (Shortest Job First), RR (Round Robin). Goals: fairness, throughput, response time, waiting time. Trade-offs: convoy effect vs starvation vs overhead.

**1. FCFS:**
*Theory:* Non-preemptive, execute processes in arrival order. Simple but convoy effect - short processes wait for long ones. Example: P1(24ms) → P2(3ms) → P3(3ms). Average waiting: (0 + 24 + 27) / 3 = 17ms.

**2. SJF:**
*Theory:* Execute shortest process first. Optimal average waiting time but starvation - long processes never execute. Example: P2(3ms) → P3(3ms) → P1(24ms). Average: (0 + 3 + 6) / 3 = 3ms.

**3. Round Robin:**
*Theory:* Each process gets time quantum, then preempted. Fair, no starvation, good response time. Higher waiting time due to context switches. Example: quantum=4ms, P1(24ms) requires 6 quanta, P2(3ms) 1 quantum.

**Virtual Memory:**

*Theory:* Virtual Memory - abstraction providing large, contiguous address space. Benefits: process isolation (security), more processes than physical RAM, efficient memory use. Mechanism: Virtual Address → MMU → Physical Address. Paging - divide memory into pages (typically 4KB). Physical memory divided into frames (same size).

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

*Theory:* Page Fault - referenced page not in physical memory. Steps: save state, find free frame, load from disk, update page table, resume process. Allows more processes than RAM but slow (disk I/O).

**System Calls:**

*Theory:* System Call - request to OS kernel for service. Categories: Process Control (fork, exec, exit), File Management (open, read, write), Device Management (ioctl), Information Maintenance (getpid, alarm), Communication (pipe, socket), Protection (chmod). User mode → Kernel mode → User mode.

```kotlin
// ✅ System Call Flow
// High-level: File API
val file = File("data.txt")
file.writeText("Hello")

// Behind scenes:
// 1. open("data.txt", O_WRONLY|O_CREAT, 0644)  // System call
// 2. write(fd, "Hello", 5)  // System call
// 3. close(fd)  // System call

// User Mode → Kernel Mode → User Mode
```

**IPC (Inter-Process Communication):**

*Theory:* IPC - communication between processes. Mechanisms: Shared Memory (fastest, direct access), Message Passing (Binder in Android), Pipes (unidirectional), Sockets (bidirectional, network). Android uses Binder for all inter-app communication.

```kotlin
// ✅ Binder IPC Example
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

**Context Switching:**

*Theory:* Context Switch - save current process state, load another. Context includes: Program Counter, CPU Registers, Process State, Memory Management Info, I/O Status. Cost: save/restore registers, update memory mappings, cache/TLB invalidation (1-10 microseconds). Pure overhead but necessary for multitasking.

**Deadlock:**

*Theory:* Deadlock - processes waiting for each other indefinitely. Four necessary conditions: Mutual Exclusion, Hold and Wait, No Preemption, Circular Wait. Prevention: lock ordering (always acquire in same order), timeout, resource hierarchy.

```kotlin
// ❌ Deadlock
val lock1 = ReentrantLock()
val lock2 = ReentrantLock()

// Thread 1: lock1.lock(), wait lock2
// Thread 2: lock2.lock(), wait lock1
// → Circular wait → DEADLOCK

// ✅ Prevention: Lock ordering
// Always: lock1 first, then lock2
thread {
    lock1.lock()
    lock2.lock()
    // Work
    lock2.unlock()
    lock1.unlock()
}

// No circular wait → No deadlock
```

**Key Takeaways:**
1. Process - isolated execution with own memory space
2. Thread - lightweight process with shared memory
3. Virtual Memory - address space abstraction for isolation
4. CPU Scheduling - determine which process runs next
5. System Call - request kernel service (user→kernel mode)
6. Context Switch - save/load process state (overhead)
7. IPC - communication between processes (Binder in Android)
8. Deadlock - circular wait, prevent with lock ordering
9. Page Fault - slow disk I/O for memory access
10. Paging - divide memory into fixed-size pages

---

## Follow-ups

- What is the difference between preemptive and non-preemptive scheduling?
- How does the Android Low Memory Killer work?
- What is thrashing in virtual memory?
- How do semaphores differ from mutexes?
- What is the Producer-Consumer problem?

## Related Questions

### Prerequisites (Easier)
- Basic computer science concepts
- Understanding of system architecture

### Related (Same Level)
- [[q-concurrency-fundamentals--computer-science--hard]] - Concurrency fundamentals
- [[q-oop-principles-deep-dive--computer-science--medium]] - OOP principles

### Advanced (Harder)
- Advanced OS concepts
- Distributed systems
- Performance optimization
