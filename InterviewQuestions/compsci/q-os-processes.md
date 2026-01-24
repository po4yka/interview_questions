---
id: cs-os-processes
title: Operating Systems - Processes and Threads
topic: operating_systems
difficulty: medium
tags:
- cs_os
- processes
- threads
anki_cards:
- slug: cs-os-processes-0-en
  language: en
  anki_id: 1769160678174
  synced_at: '2026-01-23T13:31:19.051474'
- slug: cs-os-processes-0-ru
  language: ru
  anki_id: 1769160678199
  synced_at: '2026-01-23T13:31:19.053244'
- slug: cs-os-processes-1-en
  language: en
  anki_id: 1769160678224
  synced_at: '2026-01-23T13:31:19.056050'
- slug: cs-os-processes-1-ru
  language: ru
  anki_id: 1769160678250
  synced_at: '2026-01-23T13:31:19.057630'
- slug: cs-os-processes-2-en
  language: en
  anki_id: 1769160678274
  synced_at: '2026-01-23T13:31:19.059142'
- slug: cs-os-processes-2-ru
  language: ru
  anki_id: 1769160678299
  synced_at: '2026-01-23T13:31:19.060358'
---
# Processes and Threads

## Process Basics

**Process**: Instance of a running program with its own address space.

### Process Control Block (PCB)

Kernel data structure containing process information:

```
PCB Contents:
- Process ID (PID)
- Process state
- Program counter
- CPU registers
- Memory management info (page tables)
- I/O status (open files)
- Scheduling info (priority, time slice)
- Parent/child relationships
```

### Process States

```
         new
          |
          v
       +-----+    interrupt    +--------+
       |ready| <-------------- |running |
       +-----+                 +--------+
          |                        |
          |    scheduler           | I/O or event
          +--------dispatch------->| wait
                                   v
                              +--------+
                              |waiting |
                              +--------+
                                   |
                                   | I/O done
                                   v
                                 ready
```

**States**:
- **New**: Being created
- **Ready**: Waiting for CPU
- **Running**: Executing on CPU
- **Waiting/Blocked**: Waiting for I/O or event
- **Terminated**: Finished execution

## Process Creation

### fork()

Creates child process as copy of parent.

```c
pid_t pid = fork();

if (pid == 0) {
    // Child process
    printf("Child PID: %d\n", getpid());
} else if (pid > 0) {
    // Parent process
    printf("Child created with PID: %d\n", pid);
} else {
    // Fork failed
    perror("fork");
}
```

**Key points**:
- Child gets copy of parent's address space (COW)
- Child gets copy of file descriptors
- fork() returns twice: 0 to child, child PID to parent

### exec()

Replace current process image with new program.

```c
// Fork and exec pattern
pid_t pid = fork();
if (pid == 0) {
    execlp("ls", "ls", "-l", NULL);
    // Only reached if exec fails
    perror("exec");
}
```

### wait()

Parent waits for child to terminate.

```c
int status;
pid_t child = wait(&status);  // Wait for any child

waitpid(pid, &status, 0);  // Wait for specific child
```

## Context Switch

Saving state of current process and loading state of next process.

**Steps**:
1. Save current process state to PCB
2. Update process state (running -> ready/blocked)
3. Move PCB to appropriate queue
4. Select next process (scheduler)
5. Load new process state from PCB
6. Update MMU (page tables, TLB flush)

**Cost**: 1-1000 microseconds depending on hardware.

## Threads

**Thread**: Lightweight execution unit within a process.

### Thread vs Process

| Aspect | Process | Thread |
|--------|---------|--------|
| Address space | Separate | Shared |
| Creation cost | High | Low |
| Context switch | Expensive | Cheaper |
| Communication | IPC needed | Shared memory |
| Isolation | Strong | Weak |
| Fault isolation | Yes | No |

### Thread Types

**User-level threads**:
- Managed by user-space library
- Fast creation/switching
- OS unaware (blocks entire process)

**Kernel-level threads**:
- Managed by OS
- True parallelism on multicore
- More overhead

**Hybrid (M:N model)**:
- M user threads mapped to N kernel threads
- Best of both worlds
- Complex implementation

### Thread Models

**Many-to-One**: Many user threads -> one kernel thread
- Fast but no parallelism

**One-to-One**: Each user thread -> one kernel thread
- Parallelism but overhead (Linux, Windows)

**Many-to-Many**: Many user threads -> many kernel threads
- Flexible (older Solaris)

## POSIX Threads (pthreads)

```c
#include <pthread.h>

void* thread_func(void* arg) {
    int* num = (int*)arg;
    printf("Thread received: %d\n", *num);
    return NULL;
}

int main() {
    pthread_t thread;
    int arg = 42;

    // Create thread
    pthread_create(&thread, NULL, thread_func, &arg);

    // Wait for thread to complete
    pthread_join(thread, NULL);

    return 0;
}
```

## Inter-Process Communication (IPC)

### Pipes

Unidirectional byte stream between related processes.

```c
int fd[2];
pipe(fd);  // fd[0] for reading, fd[1] for writing

if (fork() == 0) {
    // Child reads
    close(fd[1]);
    read(fd[0], buffer, size);
} else {
    // Parent writes
    close(fd[0]);
    write(fd[1], "Hello", 5);
}
```

### Named Pipes (FIFOs)

Pipes with filesystem names, for unrelated processes.

```c
mkfifo("/tmp/myfifo", 0666);
int fd = open("/tmp/myfifo", O_WRONLY);
write(fd, "data", 4);
```

### Message Queues

Structured messages with types.

### Shared Memory

Fastest IPC - direct memory access.

```c
// Create shared memory
int shm_fd = shm_open("/myshm", O_CREAT | O_RDWR, 0666);
ftruncate(shm_fd, SIZE);
void* ptr = mmap(0, SIZE, PROT_WRITE, MAP_SHARED, shm_fd, 0);

// Write
sprintf(ptr, "Hello from process");

// Other process can read same memory
```

### Sockets

Network communication (also local).

### Signals

Asynchronous notifications.

```c
signal(SIGINT, handler);  // Register handler
kill(pid, SIGTERM);       // Send signal to process
```

| Signal | Default | Use |
|--------|---------|-----|
| SIGINT | Terminate | Ctrl+C |
| SIGTERM | Terminate | Graceful shutdown |
| SIGKILL | Terminate | Force kill (can't catch) |
| SIGSTOP | Stop | Pause process |
| SIGCHLD | Ignore | Child terminated |

### IPC Comparison

| Method | Speed | Complexity | Use Case |
|--------|-------|------------|----------|
| Pipes | Medium | Low | Parent-child |
| Named pipes | Medium | Low | Unrelated processes |
| Message queues | Medium | Medium | Structured data |
| Shared memory | Fast | High | Large data |
| Sockets | Slow | Medium | Network/local |
| Signals | Fast | Low | Notifications |

## Process vs Thread Usage

**Use processes when**:
- Isolation needed (crash protection)
- Different privilege levels
- Multi-machine distribution

**Use threads when**:
- Need shared memory
- Lightweight concurrency
- Responsive UI (background work)

## Interview Questions

1. **What happens when you type a command in shell?**
   - Shell fork()s
   - Child exec()s the command
   - Parent wait()s for child
   - Child terminates, parent continues

2. **Why is fork() useful?**
   - Create worker processes
   - Run different programs
   - Parallel processing

3. **How does COW work with fork()?**
   - Parent and child share pages (marked read-only)
   - On write, page fault triggers copy
   - Only modified pages are duplicated
