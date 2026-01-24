---
id: cs-os-memory
title: Operating Systems - Memory Management
topic: operating_systems
difficulty: hard
tags:
- cs_os
- memory
anki_cards:
- slug: cs-os-memory-0-en
  language: en
  anki_id: 1769160676874
  synced_at: '2026-01-23T13:31:18.966559'
- slug: cs-os-memory-0-ru
  language: ru
  anki_id: 1769160676900
  synced_at: '2026-01-23T13:31:18.968172'
- slug: cs-os-memory-1-en
  language: en
  anki_id: 1769160676924
  synced_at: '2026-01-23T13:31:18.969402'
- slug: cs-os-memory-1-ru
  language: ru
  anki_id: 1769160676950
  synced_at: '2026-01-23T13:31:18.972592'
- slug: cs-os-memory-2-en
  language: en
  anki_id: 1769160676975
  synced_at: '2026-01-23T13:31:18.973921'
- slug: cs-os-memory-2-ru
  language: ru
  anki_id: 1769160677001
  synced_at: '2026-01-23T13:31:18.975046'
---
# Memory Management

## Memory Hierarchy

| Level | Type | Size | Speed | Cost |
|-------|------|------|-------|------|
| L1 Cache | SRAM | 32-64 KB | ~1 ns | Highest |
| L2 Cache | SRAM | 256 KB - 1 MB | ~4 ns | High |
| L3 Cache | SRAM | 2-32 MB | ~10 ns | Medium |
| RAM | DRAM | 4-128 GB | ~100 ns | Low |
| SSD | Flash | 128 GB - 4 TB | ~100 us | Lower |
| HDD | Magnetic | 1-20 TB | ~10 ms | Lowest |

## Virtual Memory

**Purpose**: Provides each process illusion of having entire address space.

**Benefits**:
- Process isolation (security)
- Memory abstraction
- Efficient physical memory usage
- Enables swapping

### Address Translation

**Virtual address** -> **Physical address** via page table.

```
Virtual Address: [Page Number | Offset]
                      |
                      v
               Page Table
                      |
                      v
Physical Address: [Frame Number | Offset]
```

## Paging

**Page**: Fixed-size block of virtual memory (typically 4 KB).
**Frame**: Fixed-size block of physical memory.

### Page Table

Maps virtual pages to physical frames.

```
Page Table Entry (PTE):
+--------+---+---+---+---+--------------+
| Unused | D | R | P | W | Frame Number |
+--------+---+---+---+---+--------------+

P = Present bit (1 = in memory)
W = Write permission
R = Referenced (accessed recently)
D = Dirty (modified)
```

### Multi-Level Page Tables

Reduces memory overhead for sparse address spaces.

**Two-level example** (32-bit, 4KB pages):
```
Virtual Address: [L1 Index (10 bits) | L2 Index (10 bits) | Offset (12 bits)]
                       |
                       v
                 L1 Page Table
                       |
                       v
                 L2 Page Table
                       |
                       v
                 Physical Frame
```

### Translation Lookaside Buffer (TLB)

Cache for recent page table lookups.

**TLB hit**: Address translation in ~1 cycle.
**TLB miss**: Walk page tables (~10-100 cycles).

**TLB structure**:
```
[Virtual Page Number | Valid | Frame Number | Permissions]
```

**TLB flush**: Required on context switch (unless tagged with ASID).

## Page Replacement Algorithms

When physical memory is full, choose page to evict.

### Optimal (OPT)

Replace page that won't be used for longest time. Theoretical best, impossible to implement.

### FIFO (First-In-First-Out)

Replace oldest page.

**Problem**: Belady's anomaly - more frames can cause more faults.

```python
def fifo_replacement(pages, num_frames):
    frames = []
    faults = 0

    for page in pages:
        if page not in frames:
            faults += 1
            if len(frames) >= num_frames:
                frames.pop(0)
            frames.append(page)

    return faults
```

### LRU (Least Recently Used)

Replace page not used for longest time.

**Implementation options**:
1. **Counter**: Update timestamp on each access
2. **Stack**: Move to top on access, evict bottom
3. **Approximation**: Clock algorithm

```python
from collections import OrderedDict

def lru_replacement(pages, num_frames):
    frames = OrderedDict()
    faults = 0

    for page in pages:
        if page in frames:
            frames.move_to_end(page)
        else:
            faults += 1
            if len(frames) >= num_frames:
                frames.popitem(last=False)
            frames[page] = True

    return faults
```

### Clock (Second Chance)

Approximation of LRU using circular list with reference bit.

```
Algorithm:
1. Examine page at clock hand
2. If reference bit = 0: replace page
3. If reference bit = 1: clear bit, advance hand
4. Repeat until page with bit = 0 found
```

### LFU (Least Frequently Used)

Replace page with lowest access count.

**Problem**: Pages used heavily in past but not anymore stay in memory.

### Comparison

| Algorithm | Complexity | Performance | Notes |
|-----------|------------|-------------|-------|
| OPT | - | Best | Impossible |
| FIFO | O(1) | Poor | Simple |
| LRU | O(1) | Good | Hardware support needed |
| Clock | O(1) | Near LRU | Practical |
| LFU | O(log n) | Variable | Needs aging |

## Segmentation

Divide memory into logical segments (code, data, stack, heap).

**Segment Table**:
```
Segment | Base Address | Limit | Permissions
--------|--------------|-------|------------
Code    | 0x1000      | 0x500 | R-X
Data    | 0x2000      | 0x300 | RW-
Stack   | 0x8000      | 0x400 | RW-
```

**Address translation**:
```
Logical: [Segment Number | Offset]
Physical: Segment Table[Segment Number].Base + Offset
```

**Segmentation vs Paging**:
| Aspect | Segmentation | Paging |
|--------|--------------|--------|
| Unit size | Variable | Fixed |
| Fragmentation | External | Internal |
| Logical division | Yes | No |
| Implementation | Complex | Simpler |

## Memory Allocation

### Contiguous Allocation

**First Fit**: Allocate first hole that fits.
**Best Fit**: Allocate smallest hole that fits.
**Worst Fit**: Allocate largest hole.

**External fragmentation**: Free memory scattered in small holes.

### Memory Compaction

Move processes to eliminate external fragmentation. Expensive operation.

## Copy-on-Write (COW)

Parent and child share pages after fork(). Pages copied only when modified.

**Benefits**:
- Fast fork()
- Memory efficient
- Used by all modern OS

```
Before write:
Parent: Page A -----> Physical Page
Child:  Page A ----^

After child writes:
Parent: Page A -----> Physical Page
Child:  Page A' ----> New Physical Page (copy)
```

## Memory-Mapped Files

Map file contents directly to virtual address space.

**Benefits**:
- Efficient I/O (no system call per read/write)
- Easy file sharing between processes
- Lazy loading

```python
import mmap

with open('file.txt', 'r+b') as f:
    mm = mmap.mmap(f.fileno(), 0)
    print(mm[:10])  # Read first 10 bytes
    mm[0:5] = b'Hello'  # Write directly
    mm.close()
```

## Memory Protection

**Protection bits**: Read, Write, Execute per page.

**Guard pages**: Unmapped pages to detect buffer overflows.

**ASLR** (Address Space Layout Randomization): Randomize memory layout to prevent exploits.

## Thrashing

System spends more time swapping than executing.

**Cause**: Working set > available memory.

**Solution**: Working set model - keep process's active pages in memory.

## Interview Questions

1. **What happens on a page fault?**
   - Trap to OS
   - Find page on disk
   - Allocate frame (may need replacement)
   - Load page from disk
   - Update page table
   - Restart instruction

2. **Why use multi-level page tables?**
   - Sparse address spaces don't need full table
   - Most processes use small portion of address space

3. **When is segmentation fault raised?**
   - Access to invalid address (unmapped)
   - Permission violation (write to read-only)
