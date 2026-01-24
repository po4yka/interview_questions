---
id: cs-os-scheduling
title: Operating Systems - CPU Scheduling
topic: operating_systems
difficulty: medium
tags:
- cs_os
- scheduling
anki_cards:
- slug: cs-os-scheduling-0-en
  language: en
  anki_id: 1769160674575
  synced_at: '2026-01-23T13:31:18.831430'
- slug: cs-os-scheduling-0-ru
  language: ru
  anki_id: 1769160674600
  synced_at: '2026-01-23T13:31:18.833826'
- slug: cs-os-scheduling-1-en
  language: en
  anki_id: 1769160674624
  synced_at: '2026-01-23T13:31:18.835365'
- slug: cs-os-scheduling-1-ru
  language: ru
  anki_id: 1769160674649
  synced_at: '2026-01-23T13:31:18.836994'
---
# CPU Scheduling

## Scheduling Goals

| Goal | Description |
|------|-------------|
| **CPU utilization** | Keep CPU busy |
| **Throughput** | Complete more processes per time |
| **Turnaround time** | Time from submission to completion |
| **Waiting time** | Time spent in ready queue |
| **Response time** | Time from request to first response |

**Trade-offs**: Can't optimize all simultaneously.

## Scheduling Types

**Preemptive**: OS can interrupt running process.
**Non-preemptive (cooperative)**: Process runs until it yields or blocks.

## Scheduling Algorithms

### First-Come, First-Served (FCFS)

Non-preemptive. Processes run in arrival order.

```
Process | Arrival | Burst
P1      | 0       | 24
P2      | 1       | 3
P3      | 2       | 3

Timeline: P1(24) | P2(3) | P3(3)

Wait times: P1=0, P2=23, P3=25
Average wait: (0+23+25)/3 = 16
```

**Problem**: Convoy effect - short processes wait behind long ones.

### Shortest Job First (SJF)

Select process with shortest burst time.

**Non-preemptive SJF**:
```
Process | Arrival | Burst
P1      | 0       | 7
P2      | 2       | 4
P3      | 4       | 1
P4      | 5       | 4

Timeline: P1(7) | P3(1) | P2(4) | P4(4)
```

**Preemptive SJF (SRTF - Shortest Remaining Time First)**:
```
Timeline: P1(2) | P2(2) | P3(1) | P2(2) | P4(4) | P1(5)
```

**Problem**: Requires knowing burst time in advance (estimation needed).

**Starvation**: Long processes may never run.

### Round Robin (RR)

Preemptive. Each process gets time quantum, then moves to back of queue.

```
Process | Burst
P1      | 10
P2      | 4
P3      | 5

Quantum = 3
Timeline: P1(3) | P2(3) | P3(3) | P1(3) | P2(1) | P3(2) | P1(4)
```

**Time quantum selection**:
- Too small: Too many context switches
- Too large: Degrades to FCFS
- Typical: 10-100 ms

### Priority Scheduling

Select highest priority process.

```
Process | Priority | Burst
P1      | 3        | 10
P2      | 1        | 1    (highest)
P3      | 4        | 2
P4      | 5        | 1    (lowest)
P5      | 2        | 5

Order: P2 | P5 | P1 | P3 | P4
```

**Problem**: Starvation of low-priority processes.

**Solution**: Aging - increase priority over time.

### Multilevel Queue

Multiple queues with different priorities and algorithms.

```
High priority:   [System processes]    -> RR, q=8
                 [Interactive]         -> RR, q=16
                 [Interactive editing] -> RR, q=32
Low priority:    [Batch processes]     -> FCFS
```

**Fixed priority**: Higher queue must be empty before lower runs.
**Time slice**: Each queue gets CPU percentage.

### Multilevel Feedback Queue (MLFQ)

Processes move between queues based on behavior.

```
Rules:
1. New processes start at highest priority
2. If process uses full quantum, demote
3. If process blocks before quantum, stay/promote
4. Periodic boost to prevent starvation

Queue 0 (highest): RR, q=8ms
Queue 1:           RR, q=16ms
Queue 2 (lowest):  FCFS
```

**Effect**: Interactive processes stay high, CPU-bound sink to low.

## Algorithm Comparison

| Algorithm | Preemptive | Starvation | Complexity | Best For |
|-----------|------------|------------|------------|----------|
| FCFS | No | No | O(1) | Simple batch |
| SJF | Optional | Yes | O(n) | Known burst times |
| RR | Yes | No | O(1) | Time-sharing |
| Priority | Optional | Yes | O(n) | Mixed workloads |
| MLFQ | Yes | No* | O(1) | General purpose |

*With aging/boost

## Real-Time Scheduling

**Hard real-time**: Deadlines must be met (pacemakers).
**Soft real-time**: Deadlines preferred (video playback).

### Rate Monotonic (RM)

Static priority: shorter period = higher priority.

**Schedulable if**: Sum(Ci/Ti) <= n(2^(1/n) - 1)
For large n, limit is ln(2) = 0.693

### Earliest Deadline First (EDF)

Dynamic priority: nearest deadline = highest priority.

**Schedulable if**: Sum(Ci/Ti) <= 1 (100% utilization possible)

## Linux Scheduling

### Completely Fair Scheduler (CFS)

**Goal**: Fair CPU time distribution.

**Virtual runtime**: Track how much CPU time each process has received.

**Red-black tree**: Processes sorted by virtual runtime, pick leftmost (smallest).

```
vruntime = actual_runtime * (NICE_0_LOAD / weight)
```

Lower nice value = higher weight = slower vruntime growth = more CPU time.

### Scheduling Classes

1. **SCHED_DEADLINE**: EDF for real-time
2. **SCHED_FIFO**: Real-time FIFO
3. **SCHED_RR**: Real-time round-robin
4. **SCHED_OTHER/NORMAL**: CFS for normal processes
5. **SCHED_BATCH**: Non-interactive batch
6. **SCHED_IDLE**: Very low priority

## Multiprocessor Scheduling

### Approaches

**Asymmetric**: One CPU makes all decisions.
**Symmetric (SMP)**: Each CPU self-schedules.

### Load Balancing

**Push migration**: Periodic check, move processes from busy to idle.
**Pull migration**: Idle CPU pulls from busy CPU.

### Processor Affinity

Keep process on same CPU for cache benefits.

**Soft affinity**: Preferred but not required.
**Hard affinity**: Process bound to specific CPU(s).

```c
cpu_set_t mask;
CPU_ZERO(&mask);
CPU_SET(0, &mask);  // CPU 0 only
sched_setaffinity(pid, sizeof(mask), &mask);
```

## Interview Questions

1. **Why is MLFQ commonly used?**
   - Adapts to process behavior
   - Good for interactive and batch
   - Prevents starvation with boost

2. **What's convoy effect?**
   - Short processes wait for long one in FCFS
   - Solution: Preemption (RR, SJF)

3. **How does CFS achieve fairness?**
   - Tracks virtual runtime
   - Always runs process with lowest vruntime
   - Red-black tree for O(log n) selection
