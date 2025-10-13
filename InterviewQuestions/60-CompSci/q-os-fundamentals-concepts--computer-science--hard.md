---
id: 20251012-600001
title: "Operating System Fundamentals / Основы операционных систем"
slug: os-fundamentals-concepts-computer-science-hard
topic: operating-systems
subtopics: ["computer-science", "fundamentals"]

subtopics:
  - operating-systems
  - processes
  - threads
  - memory-management
  - cpu-scheduling
status: draft
difficulty: hard
moc: moc-operating-systems
date_created: 2025-10-12
date_updated: 2025-10-13
related_questions:
  - q-concurrency-fundamentals--computer-science--hard
  - q-solid-principles--software-design--medium
  - q-data-structures-overview--algorithms--easy
tags:
  - os
  - processes
  - threads
  - memory
  - cpu-scheduling
  - virtual-memory
---

# Operating System Fundamentals

## English Version

### Problem Statement

Operating Systems manage hardware resources, provide abstraction layers, and enable concurrent execution. Understanding OS concepts like processes, threads, memory management, and scheduling is crucial for building efficient applications and debugging performance issues.

**The Question:** What are the core OS concepts? How do processes and threads work? What is virtual memory? How does CPU scheduling work? What are system calls?

### Detailed Answer

---

### PROCESSES VS THREADS

**Process:**
```
Process = Program in execution

Components:
- Program Code (text section)
- Current Activity (program counter, registers)
- Stack (temporary data: function parameters, local variables)
- Heap (dynamically allocated memory)
- Data Section (global variables)

Characteristics:
 Independent memory space
 Own resources (files, I/O)
 Heavyweight (expensive to create/switch)
 Inter-process communication (IPC) required
 Slow context switching
 High memory overhead
```

**Thread:**
```
Thread = Lightweight process, unit of execution within process

Components:
- Program Counter
- Register Set
- Stack
- Thread ID

Shares with other threads in same process:
- Code Section
- Data Section
- Heap
- Open Files

Characteristics:
 Share memory space
 Lightweight (cheap to create/switch)
 Fast context switching
 Easy communication (shared memory)
 No memory protection between threads
 One thread crash can crash entire process
```

**Android Example:**
```kotlin
// Process: Each Android app runs in separate process
// Android creates new Linux process for each app

class MainActivity : AppCompatActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Main Thread (UI Thread)
        // Only thread that can update UI
        textView.text = "Hello"  //  Safe

        // Background Thread
        Thread {
            // Perform long operation
            val data = fetchDataFromNetwork()

            //  CRASH: Can't update UI from background thread
            // textView.text = data

            //  Correct: Post to UI thread
            runOnUiThread {
                textView.text = data
            }
        }.start()

        // Modern approach: Coroutines
        lifecycleScope.launch {
            val data = withContext(Dispatchers.IO) {
                fetchDataFromNetwork()  // Background thread
            }
            textView.text = data  //  Back on Main thread
        }
    }
}
```

---

### PROCESS STATES

```

   NEW     Process being created

     
     

  READY    Process waiting for CPU

      scheduler dispatch
     

 RUNNING   Process executing on CPU

      
       I/O or event wait
      
     
      WAITING    Process waiting for I/O/event
     
           I/O complete
          
        READY
    
     interrupt
     READY
  
   exit
  

TERMINATED Process finished

```

**Android Process States:**
```kotlin
// Android process importance hierarchy
enum class ProcessImportance {
    FOREGROUND,          // Visible activity
    VISIBLE,             // Visible but not foreground
    SERVICE,             // Running service
    BACKGROUND,          // Not visible
    EMPTY                // No active components
}

// System kills processes from bottom up when memory needed
```

---

### CPU SCHEDULING

**Scheduling Algorithms:**

**1. First-Come, First-Served (FCFS)**
```
Non-preemptive, processes executed in arrival order

Example:
Process  Burst Time  Arrival Time
P1       24          0
P2       3           0
P3       3           0

Timeline: |--P1 (24ms)--|P2(3)|P3(3)|
Waiting time:
- P1: 0ms
- P2: 24ms (waits for P1)
- P3: 27ms (waits for P1, P2)
Average: (0 + 24 + 27) / 3 = 17ms

 Convoy Effect: Short processes wait for long ones
```

**2. Shortest Job First (SJF)**
```
Execute shortest process first

Example (same processes):
Timeline: |P2(3)|P3(3)|--P1 (24ms)--|
Waiting time:
- P2: 0ms
- P3: 3ms
- P1: 6ms
Average: (0 + 3 + 6) / 3 = 3ms

 Optimal average waiting time
 Starvation: Long processes may never execute
 Need to predict burst time
```

**3. Round Robin (RR)**
```
Each process gets time quantum (e.g., 4ms), then preempted

Example (quantum = 4ms):
Process  Burst Time
P1       24
P2       3
P3       3

Timeline: |P1(4)|P2(3)|P3(3)|P1(4)|P1(4)|P1(4)|P1(4)|P1(4)|

 Fair, good response time
 No starvation
 Higher average waiting time
 Context switch overhead
```

**Android Scheduling:**
```kotlin
// Android uses CFS (Completely Fair Scheduler)
// + Priority-based scheduling

// Thread priorities
Thread.MIN_PRIORITY   // 1
Thread.NORM_PRIORITY  // 5
Thread.MAX_PRIORITY   // 10

// Android Process priorities
android:process="backgroundProcess"
android:priority="background"

// Handler priority
val handler = Handler(HandlerThread("background").apply {
    priority = Process.THREAD_PRIORITY_BACKGROUND
}.looper)
```

---

### MEMORY MANAGEMENT

**Virtual Memory:**
```
Virtual Memory = Abstraction that gives each process
                 illusion of large, contiguous address space

Benefits:
 Process isolation (security)
 More processes than physical RAM
 Efficient memory use
 Simplified programming

How it works:
Virtual Address → MMU (Memory Management Unit) → Physical Address

Virtual Memory divided into:
- Pages (typically 4KB)

Physical Memory divided into:
- Frames (same size as pages)

Page Table: Maps virtual pages to physical frames
```

**Paging Example:**
```
Virtual Address Space: 0x0000 - 0xFFFF (64KB)
Physical Memory: 32KB (8 frames of 4KB each)

Page Table:
Virtual Page  →  Physical Frame
0             →  3
1             →  7
2             →  1
3             →  (not in memory, on disk)
4             →  5

Process accesses address 0x1000:
1. Extract page number: 0x1000 / 4KB = Page 0
2. Look up in page table: Page 0 → Frame 3
3. Calculate physical address: (Frame 3 × 4KB) + offset
4. Access physical memory
```

**Page Fault:**
```
Page Fault = Referenced page not in physical memory

Steps:
1. Process accesses virtual address
2. MMU looks up page table
3. Page not present → Page Fault exception
4. OS:
   - Save process state
   - Find free frame (or evict page)
   - Load page from disk
   - Update page table
   - Resume process

Performance:
 Allows more processes than RAM
 Page faults are SLOW (disk I/O)
```

**Android Memory:**
```kotlin
// Android Low Memory Killer (LMK)
// Kills processes when memory low

class MyApplication : Application() {
    override fun onLowMemory() {
        // System is running low on memory
        // Release caches, bitmaps, etc.
        imageCache.clear()
        memoryCache.evictAll()
    }

    override fun onTrimMemory(level: Int) {
        when (level) {
            TRIM_MEMORY_RUNNING_CRITICAL -> {
                // App in foreground, memory critically low
                releaseNonEssentialMemory()
            }
            TRIM_MEMORY_BACKGROUND -> {
                // App in background, release more memory
                releaseAllCaches()
            }
            TRIM_MEMORY_COMPLETE -> {
                // App about to be killed
                releaseEverything()
            }
        }
    }
}

// Check available memory
val activityManager = getSystemService(Context.ACTIVITY_MANAGER_SERVICE) as ActivityManager
val memoryInfo = ActivityManager.MemoryInfo()
activityManager.getMemoryInfo(memoryInfo)

if (memoryInfo.lowMemory) {
    // Memory is low
    val availableMB = memoryInfo.availMem / (1024 * 1024)
    Log.w("Memory", "Low memory: ${availableMB}MB available")
}
```

---

### SYSTEM CALLS

**System Call = Request to OS kernel for service**

**Categories:**
```
1. Process Control
   - fork(), exec(), exit(), wait()
   - Android: Process.start(), Process.killProcess()

2. File Management
   - open(), read(), write(), close()
   - Android: FileInputStream, FileOutputStream

3. Device Management
   - ioctl(), read(), write()
   - Android: Camera API, Sensor API

4. Information Maintenance
   - getpid(), alarm(), sleep()
   - Android: Process.myPid(), SystemClock.sleep()

5. Communication
   - pipe(), socket(), send(), receive()
   - Android: Socket, LocalSocket

6. Protection
   - chmod(), umask(), chown()
   - Android: File permissions, SELinux
```

**System Call Example:**
```kotlin
// High-level Android API
val file = File("/data/data/com.example.app/file.txt")
file.writeText("Hello")

// Behind the scenes, translates to system calls:
// 1. open("/data/data/com.example.app/file.txt", O_WRONLY|O_CREAT, 0644)
// 2. write(fd, "Hello", 5)
// 3. close(fd)

// System call flow:
// App (User Mode)
//     ↓ syscall
// Kernel (Kernel Mode)
//     → Execute privileged operation
//     → Return to user mode
// App continues
```

---

### INTER-PROCESS COMMUNICATION (IPC)

**IPC Mechanisms:**

**1. Shared Memory:**
```
Fastest IPC, processes share memory region

Android Example: Ashmem (Anonymous Shared Memory)
Used for passing large data (e.g., Bitmaps)

// Sender
val ashmem = AshmemAllocator.createAshmem("mysharedmem", 1024)
ashmem.writeBytes(data)

// Receiver gets same memory region
val ashmem = AshmemAllocator.getAshmem(fd)
val data = ashmem.readBytes()
```

**2. Message Passing:**
```
Processes send/receive messages

Android Example: Binder IPC
All inter-app communication uses Binder

// Service (receives messages)
class MyService : Service() {
    private val binder = object : IMyService.Stub() {
        override fun doSomething(data: String): String {
            return "Processed: $data"
        }
    }

    override fun onBind(intent: Intent): IBinder = binder
}

// Client (sends messages)
class ClientActivity : AppCompatActivity() {
    private var service: IMyService? = null

    private val connection = object : ServiceConnection {
        override fun onServiceConnected(name: ComponentName, binder: IBinder) {
            service = IMyService.Stub.asInterface(binder)
            val result = service?.doSomething("Hello")
        }

        override fun onServiceDisconnected(name: ComponentName) {
            service = null
        }
    }

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        bindService(Intent(this, MyService::class.java), connection, BIND_AUTO_CREATE)
    }
}
```

**3. Pipes:**
```
Unidirectional communication channel

Example: Process output piping
ls | grep "file"
     ↑ pipe connects ls output to grep input
```

**4. Sockets:**
```
Bidirectional, can work across network

Android Example:
val socket = Socket("localhost", 8080)
val output = socket.getOutputStream()
output.write("Hello".toByteArray())

val input = socket.getInputStream()
val response = input.readBytes()
```

---

### CONTEXT SWITCHING

**Context Switch = Save current process state, load another**

```
Context of Process:
- Program Counter (PC)
- CPU Registers
- Process State
- Memory Management Info
- I/O Status
- Accounting Info

Context Switch Steps:
1. Interrupt or system call
2. Save current process context (PCB - Process Control Block)
3. Update process state
4. Select next process (scheduler)
5. Load new process context
6. Resume execution

Cost:
- Save/restore registers
- Update memory mappings
- Cache/TLB invalidation
- Time: 1-10 microseconds

 Pure overhead - no useful work done
 Necessary for multitasking
```

**Android Context Switching:**
```kotlin
// Android minimizes context switches
// Use thread pools instead of creating many threads

//  Bad: Many threads, many context switches
repeat(1000) {
    Thread {
        doWork()
    }.start()
}

//  Good: Thread pool limits concurrent threads
val executor = Executors.newFixedThreadPool(4)
repeat(1000) {
    executor.execute {
        doWork()
    }
}

//  Better: Coroutines (even lighter weight)
runBlocking {
    repeat(1000) {
        launch {
            doWork()
        }
    }
}
```

---

### DEADLOCK

**Deadlock = Processes waiting for each other indefinitely**

**Necessary Conditions (all 4 must be true):**
```
1. Mutual Exclusion
   - At least one resource must be non-shareable

2. Hold and Wait
   - Process holds resource while waiting for another

3. No Preemption
   - Resources cannot be forcibly taken

4. Circular Wait
   - P1 waits for P2, P2 waits for P3, ..., Pn waits for P1
```

**Example:**
```kotlin
// Deadlock example
val lock1 = ReentrantLock()
val lock2 = ReentrantLock()

// Thread 1
thread {
    lock1.lock()
    Thread.sleep(100)
    lock2.lock()  //  Waits forever
    // Do work
    lock2.unlock()
    lock1.unlock()
}

// Thread 2
thread {
    lock2.lock()
    Thread.sleep(100)
    lock1.lock()  //  Waits forever
    // Do work
    lock1.unlock()
    lock2.unlock()
}

// Thread 1: Holds lock1, waits for lock2
// Thread 2: Holds lock2, waits for lock1
// → DEADLOCK
```

**Prevention:**
```kotlin
//  Solution: Lock ordering
// Always acquire locks in same order

// Thread 1
thread {
    lock1.lock()  // Always lock1 first
    lock2.lock()
    // Do work
    lock2.unlock()
    lock1.unlock()
}

// Thread 2
thread {
    lock1.lock()  // Always lock1 first
    lock2.lock()
    // Do work
    lock2.unlock()
    lock1.unlock()
}

// No circular wait → No deadlock
```

**Deadlock Detection in Android:**
```kotlin
// StrictMode can detect potential deadlocks
StrictMode.setThreadPolicy(
    StrictMode.ThreadPolicy.Builder()
        .detectAll()
        .penaltyLog()
        .build()
)

// Use timeout with locks
val acquired = lock.tryLock(1, TimeUnit.SECONDS)
if (acquired) {
    try {
        // Do work
    } finally {
        lock.unlock()
    }
} else {
    // Lock not acquired - avoid deadlock
    Log.w("Deadlock", "Could not acquire lock")
}
```

---

### KEY TAKEAWAYS

1. **Process** = program in execution with isolated memory
2. **Thread** = lightweight unit within process, shared memory
3. **Virtual Memory** = abstraction providing large address space
4. **Paging** = divide memory into fixed-size pages
5. **Page Fault** = referenced page not in RAM (slow!)
6. **CPU Scheduling** = determine which process runs next
7. **Context Switch** = save/load process state (overhead)
8. **System Call** = request kernel service (user→kernel mode)
9. **IPC** = communication between processes (Binder in Android)
10. **Deadlock** = circular wait, prevent with lock ordering

---

## Russian Version

### Постановка задачи

Операционные системы управляют аппаратными ресурсами, предоставляют уровни абстракции и обеспечивают параллельное выполнение. Понимание OS концепций как процессы, потоки, управление памятью и планирование критично для создания эффективных приложений и отладки проблем производительности.

**Вопрос:** Каковы ключевые концепции ОС? Как работают процессы и потоки? Что такое виртуальная память? Как работает планирование CPU? Что такое системные вызовы?

### Ключевые выводы

1. **Процесс** = программа в исполнении с изолированной памятью
2. **Поток** = лёгковесная единица внутри процесса, разделяемая память
3. **Виртуальная память** = абстракция, предоставляющая большое адресное пространство
4. **Paging** = разделение памяти на страницы фиксированного размера
5. **Page Fault** = обращение к странице не в RAM (медленно!)
6. **CPU Scheduling** = определение какой процесс выполняется следующим
7. **Context Switch** = сохранение/загрузка состояния процесса (overhead)
8. **Системный вызов** = запрос сервиса ядра (user→kernel mode)
9. **IPC** = коммуникация между процессами (Binder в Android)
10. **Deadlock** = циклическое ожидание, предотвращается упорядочением блокировок

## Follow-ups

1. What is the difference between preemptive and non-preemptive scheduling?
2. How does the Android Low Memory Killer work?
3. What is thrashing in virtual memory?
4. How do semaphores differ from mutexes?
5. What is the Producer-Consumer problem?
6. How does copy-on-write (COW) work?
7. What are Translation Lookaside Buffers (TLB)?
8. How does Android's Binder IPC work internally?
9. What is priority inversion and how to prevent it?
10. How do modern CPUs implement multithreading (SMT/Hyperthreading)?

---

## Related Questions

### Prerequisites (Easier)
- [[q-oop-principles-deep-dive--computer-science--medium]] - Computer Science
- [[q-clean-code-principles--software-engineering--medium]] - Computer Science
- [[q-default-vs-io-dispatcher--programming-languages--medium]] - Computer Science

### Related (Hard)
- [[q-concurrency-fundamentals--computer-science--hard]] - concurrency fundamentals   computer science 
