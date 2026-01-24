---
id: cs-os-sync
title: Operating Systems - Synchronization
topic: operating_systems
difficulty: hard
tags:
- cs_os
- synchronization
- concurrency
anki_cards:
- slug: cs-os-sync-0-en
  language: en
  anki_id: 1769160677025
  synced_at: '2026-01-23T13:31:18.975995'
- slug: cs-os-sync-0-ru
  language: ru
  anki_id: 1769160677049
  synced_at: '2026-01-23T13:31:18.977082'
- slug: cs-os-sync-1-en
  language: en
  anki_id: 1769160677075
  synced_at: '2026-01-23T13:31:18.978332'
- slug: cs-os-sync-1-ru
  language: ru
  anki_id: 1769160677099
  synced_at: '2026-01-23T13:31:18.982139'
- slug: cs-os-sync-2-en
  language: en
  anki_id: 1769160677125
  synced_at: '2026-01-23T13:31:18.983860'
- slug: cs-os-sync-2-ru
  language: ru
  anki_id: 1769160677150
  synced_at: '2026-01-23T13:31:18.986999'
---
# Synchronization

## Race Conditions

**Race condition**: Outcome depends on timing of uncontrolled events.

```c
// Shared counter - race condition
int counter = 0;

// Thread 1 and 2 both do:
counter++;  // Read-modify-write is not atomic

// Expected: counter = 2
// Possible: counter = 1 (lost update)
```

**Critical section**: Code that accesses shared resources.

## Critical Section Problem

**Requirements**:
1. **Mutual exclusion**: Only one thread in critical section
2. **Progress**: If no one in CS, waiting thread must enter
3. **Bounded waiting**: Limit on how long thread waits

## Synchronization Primitives

### Mutex (Mutual Exclusion Lock)

Binary lock - acquired or released.

```c
pthread_mutex_t mutex = PTHREAD_MUTEX_INITIALIZER;

pthread_mutex_lock(&mutex);
// Critical section
counter++;
pthread_mutex_unlock(&mutex);
```

**Properties**:
- Only owner can unlock
- Recursive mutex allows same thread to lock multiple times

### Semaphore

Counter-based synchronization.

```c
sem_t sem;
sem_init(&sem, 0, 1);  // Initial value 1 (binary semaphore)

sem_wait(&sem);  // Decrement (block if 0)
// Critical section
sem_post(&sem);  // Increment
```

**Binary semaphore** (value 0 or 1): Like mutex.
**Counting semaphore**: Control access to pool of resources.

**Semaphore vs Mutex**:
| Aspect | Mutex | Semaphore |
|--------|-------|-----------|
| Values | 0 or 1 | 0 to N |
| Ownership | Yes | No |
| Use case | Mutual exclusion | Resource counting, signaling |

### Spinlock

Busy-wait lock - keep trying in loop.

```c
while (!atomic_compare_and_swap(&lock, 0, 1)) {
    // Spin (waste CPU)
}
// Critical section
lock = 0;
```

**Use case**: Very short critical sections on multicore systems.

**Problem**: Wastes CPU cycles.

### Condition Variable

Wait for condition to become true.

```c
pthread_mutex_t mutex;
pthread_cond_t cond;

// Consumer
pthread_mutex_lock(&mutex);
while (queue_empty()) {
    pthread_cond_wait(&cond, &mutex);  // Releases mutex while waiting
}
item = dequeue();
pthread_mutex_unlock(&mutex);

// Producer
pthread_mutex_lock(&mutex);
enqueue(item);
pthread_cond_signal(&cond);  // Wake one waiter
pthread_mutex_unlock(&mutex);
```

**Key points**:
- Always use with mutex
- Always check condition in loop (spurious wakeups)
- signal() wakes one, broadcast() wakes all

### Read-Write Lock

Multiple readers OR single writer.

```c
pthread_rwlock_t rwlock;

// Reader
pthread_rwlock_rdlock(&rwlock);
// Read shared data
pthread_rwlock_unlock(&rwlock);

// Writer
pthread_rwlock_wrlock(&rwlock);
// Modify shared data
pthread_rwlock_unlock(&rwlock);
```

**Use case**: Read-heavy workloads.

### Monitor

High-level synchronization construct combining mutex and condition variables.

```java
class BoundedBuffer {
    private Object[] buffer;
    private int count = 0;

    public synchronized void put(Object item) throws InterruptedException {
        while (count == buffer.length) {
            wait();  // Release lock and wait
        }
        buffer[count++] = item;
        notifyAll();
    }

    public synchronized Object get() throws InterruptedException {
        while (count == 0) {
            wait();
        }
        Object item = buffer[--count];
        notifyAll();
        return item;
    }
}
```

## Classic Synchronization Problems

### Producer-Consumer (Bounded Buffer)

```python
from threading import Semaphore, Lock

buffer_size = 10
buffer = []
mutex = Lock()
empty = Semaphore(buffer_size)  # Empty slots
full = Semaphore(0)             # Full slots

def producer():
    while True:
        item = produce()
        empty.acquire()  # Wait for empty slot
        with mutex:
            buffer.append(item)
        full.release()   # Signal item available

def consumer():
    while True:
        full.acquire()   # Wait for item
        with mutex:
            item = buffer.pop(0)
        empty.release()  # Signal slot freed
        consume(item)
```

### Readers-Writers

```python
from threading import Semaphore, Lock

read_count = 0
mutex = Lock()          # Protects read_count
write_lock = Semaphore(1)  # Exclusive write access

def reader():
    with mutex:
        read_count += 1
        if read_count == 1:
            write_lock.acquire()  # First reader blocks writers

    # Read data

    with mutex:
        read_count -= 1
        if read_count == 0:
            write_lock.release()  # Last reader releases

def writer():
    write_lock.acquire()
    # Write data
    write_lock.release()
```

**Problem**: Writer starvation possible.

### Dining Philosophers

Five philosophers, five forks, need two forks to eat.

**Deadlock-free solutions**:
1. Allow max 4 philosophers at table
2. Asymmetric: odd pick left first, even pick right first
3. Resource hierarchy: always pick lower-numbered fork first

```python
def philosopher(i):
    while True:
        think()
        # Resource hierarchy
        first = min(i, (i+1) % 5)
        second = max(i, (i+1) % 5)
        forks[first].acquire()
        forks[second].acquire()
        eat()
        forks[second].release()
        forks[first].release()
```

## Deadlock

**Four necessary conditions** (Coffman conditions):
1. **Mutual exclusion**: Resource held exclusively
2. **Hold and wait**: Hold one, wait for another
3. **No preemption**: Can't force release
4. **Circular wait**: Cycle of waiting

### Deadlock Prevention

Break one of four conditions:
- **No mutual exclusion**: Use shareable resources
- **No hold and wait**: Request all at once
- **Allow preemption**: Force release
- **No circular wait**: Order resources, request in order

### Deadlock Avoidance

**Banker's algorithm**: Check if request leads to safe state.

**Safe state**: Sequence exists where all processes can complete.

### Deadlock Detection

Build wait-for graph, detect cycles.

### Deadlock Recovery

- Kill processes
- Rollback to checkpoint
- Preempt resources

## Lock-Free Programming

Use atomic operations instead of locks.

### Compare-and-Swap (CAS)

```c
bool CAS(int* addr, int expected, int new_val) {
    if (*addr == expected) {
        *addr = new_val;
        return true;
    }
    return false;
}

// Lock-free increment
void atomic_increment(int* counter) {
    int old, new;
    do {
        old = *counter;
        new = old + 1;
    } while (!CAS(counter, old, new));
}
```

### ABA Problem

Value changes A -> B -> A, CAS succeeds incorrectly.

**Solution**: Version counter or hazard pointers.

## Interview Questions

1. **Difference between mutex and semaphore?**
   - Mutex has ownership, semaphore doesn't
   - Mutex is binary, semaphore can count
   - Use mutex for mutual exclusion, semaphore for signaling

2. **How to prevent deadlock?**
   - Consistent lock ordering
   - Lock timeout/trylock
   - Avoid holding multiple locks

3. **Why use spinlock over mutex?**
   - Very short critical sections
   - Multicore systems
   - Avoiding context switch overhead
