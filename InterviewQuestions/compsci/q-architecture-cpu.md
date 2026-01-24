---
id: cs-arch-cpu
title: Computer Architecture - CPU
topic: computer_architecture
difficulty: medium
tags:
- cs_architecture
- cpu
- hardware
anki_cards:
- slug: cs-arch-cpu-0-en
  language: en
  anki_id: 1769160677174
  synced_at: '2026-01-23T13:31:18.989519'
- slug: cs-arch-cpu-0-ru
  language: ru
  anki_id: 1769160677199
  synced_at: '2026-01-23T13:31:18.990793'
- slug: cs-arch-cpu-1-en
  language: en
  anki_id: 1769160677224
  synced_at: '2026-01-23T13:31:18.991969'
- slug: cs-arch-cpu-1-ru
  language: ru
  anki_id: 1769160677249
  synced_at: '2026-01-23T13:31:18.993195'
---
# CPU Architecture

## CPU Components

### Arithmetic Logic Unit (ALU)

Performs arithmetic and logical operations.

- Addition, subtraction, multiplication, division
- AND, OR, NOT, XOR
- Comparisons

### Control Unit (CU)

Directs operation of processor.

- Fetches instructions
- Decodes instructions
- Controls execution

### Registers

Fast storage within CPU.

| Type | Purpose |
|------|---------|
| General purpose | Data operations |
| Program Counter (PC) | Address of next instruction |
| Instruction Register (IR) | Current instruction |
| Stack Pointer (SP) | Top of stack |
| Flags/Status | Condition codes (zero, carry, overflow) |

## Instruction Cycle

**Fetch-Decode-Execute**

```
1. Fetch: Read instruction from memory (PC -> MAR -> Memory -> MDR -> IR)
2. Decode: Interpret instruction
3. Execute: Perform operation
4. Store: Write results
5. Update PC: Move to next instruction
```

## Pipelining

Overlap instruction execution stages.

```
Without pipeline:
  Instr 1: [F][D][E][S]
  Instr 2:             [F][D][E][S]

With pipeline:
  Instr 1: [F][D][E][S]
  Instr 2:    [F][D][E][S]
  Instr 3:       [F][D][E][S]
  Instr 4:          [F][D][E][S]
```

**Throughput**: 1 instruction per cycle (instead of N cycles).

### Pipeline Hazards

**Data Hazard**: Instruction depends on result of previous.

```
ADD R1, R2, R3  # R1 = R2 + R3
SUB R4, R1, R5  # R4 = R1 - R5 (needs R1 from ADD)

Solution: Forwarding/bypassing, stalling
```

**Control Hazard**: Branch changes program flow.

```
BEQ R1, R2, label  # Branch if equal
ADD R3, R4, R5     # Which instruction to fetch?

Solution: Branch prediction, speculative execution
```

**Structural Hazard**: Resource conflict.

```
Two instructions need same ALU

Solution: More resources, stalling
```

### Branch Prediction

Guess branch outcome before evaluation.

**Static prediction**: Always predict taken/not taken.

**Dynamic prediction**: Based on history.

```
Branch History Table (BHT):
  PC -> 2-bit counter (strongly/weakly taken/not taken)

Branch Target Buffer (BTB):
  PC -> target address
```

## RISC vs CISC

| Aspect | RISC | CISC |
|--------|------|------|
| Instructions | Simple, fixed-size | Complex, variable-size |
| Cycles per instruction | Usually 1 | Multiple |
| Registers | Many | Fewer |
| Memory access | Load/store only | Any instruction |
| Examples | ARM, RISC-V | x86 |

**Modern reality**: x86 translates to micro-ops (RISC-like internally).

## Superscalar Execution

Execute multiple instructions per cycle.

```
Cycle 1: [ADD] [MUL] [LOAD]  # 3 instructions
Cycle 2: [SUB] [DIV] [STORE] # 3 instructions
```

**Requirements**: Multiple execution units, instruction-level parallelism (ILP).

## Out-of-Order Execution

Execute instructions in different order than program.

```
Program order:      Out-of-order:
1. LOAD R1, [addr]  1. LOAD R1 (stall)
2. ADD R2, R1, R3   3. MUL R4, R5 (independent, execute first)
3. MUL R4, R5, R6   2. ADD R2, R1 (after LOAD completes)
```

**Tomasulo's Algorithm**: Track dependencies with reservation stations.

## Speculative Execution

Execute instructions before knowing if needed.

```
if (condition) {
    // Execute speculatively
}
// Commit if prediction correct
// Rollback if wrong
```

**Security**: Spectre/Meltdown attacks exploit speculative execution.

## Instruction Set Architecture (ISA)

Interface between hardware and software.

**Common ISAs**:
- **x86-64**: Intel/AMD, complex, backwards compatible
- **ARM**: Mobile, efficient, licensing model
- **RISC-V**: Open source, modular

### x86-64 Registers

```
RAX, RBX, RCX, RDX  # General purpose
RSI, RDI           # Source, destination index
RBP                # Base pointer
RSP                # Stack pointer
R8-R15             # Additional GP registers
RIP                # Instruction pointer
RFLAGS             # Flags register
```

## Multicore Architecture

Multiple CPU cores on single chip.

```
    +------+------+------+------+
    | Core | Core | Core | Core |
    |  0   |  1   |  2   |  3   |
    +------+------+------+------+
    |          L3 Cache          |
    +----------------------------+
    |       Memory Controller     |
    +----------------------------+
```

### Cache Coherence

Ensure all cores see consistent memory.

**MESI Protocol**:
- **Modified**: Only in this cache, dirty
- **Exclusive**: Only in this cache, clean
- **Shared**: In multiple caches, clean
- **Invalid**: Not valid

### Memory Model

Rules for how memory operations appear to other cores.

**Sequential consistency**: All operations appear in program order.

**Relaxed models**: Allow reordering for performance.

```cpp
// May need memory barriers
std::atomic_thread_fence(std::memory_order_seq_cst);
```

## Performance Metrics

**Clock speed**: Cycles per second (GHz).

**IPC**: Instructions Per Cycle.

**CPI**: Cycles Per Instruction (inverse of IPC).

**Performance = Clock_speed * IPC / Instructions**

### Amdahl's Law

Speedup limited by non-parallelizable portion.

```
Speedup = 1 / ((1 - P) + P/N)

P = parallelizable fraction
N = number of processors

Example: P=0.9, N=10
Speedup = 1 / (0.1 + 0.9/10) = 5.26x (not 10x)
```

## Interview Questions

1. **What is pipelining?**
   - Overlap instruction execution stages
   - Increases throughput to ~1 instruction/cycle
   - Hazards: data, control, structural

2. **What is branch prediction?**
   - Guess branch outcome before evaluation
   - Avoids pipeline stalls
   - Uses history tables for accuracy

3. **RISC vs CISC?**
   - RISC: Simple instructions, many registers
   - CISC: Complex instructions, fewer registers
   - Modern x86 translates to RISC-like internally

4. **What is cache coherence?**
   - Ensure all cores see consistent memory
   - MESI protocol for state management
   - Required for correct multicore programs
