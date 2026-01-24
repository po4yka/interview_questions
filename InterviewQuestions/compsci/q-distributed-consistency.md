---
id: cs-dist-consistency
title: Distributed Systems - Consistency and Consensus
topic: distributed_systems
difficulty: hard
tags:
- cs_distributed_systems
- consistency
- consensus
anki_cards:
- slug: cs-dist-cons-0-en
  language: en
  anki_id: 1769160675925
  synced_at: '2026-01-23T13:31:18.901611'
- slug: cs-dist-cons-0-ru
  language: ru
  anki_id: 1769160675950
  synced_at: '2026-01-23T13:31:18.902994'
- slug: cs-dist-cons-1-en
  language: en
  anki_id: 1769160675975
  synced_at: '2026-01-23T13:31:18.905258'
- slug: cs-dist-cons-1-ru
  language: ru
  anki_id: 1769160676000
  synced_at: '2026-01-23T13:31:18.906787'
---
# Consistency and Consensus

## Consistency Models

### Strong Consistency

All reads see most recent write. Equivalent to single-copy system.

**Linearizability**: Operations appear instantaneous at some point between invocation and response.

```
Write(x=1) completes at time T
Any read after T returns x=1
```

**Cost**: High latency, reduced availability.

### Sequential Consistency

Operations appear in program order, same order for all processes.

```
Process A: Write(x=1), Write(y=2)
Process B: Read(y)=2, Read(x)=1  OK (sees A's order)
Process B: Read(y)=2, Read(x)=0  NOT OK (violates order)
```

### Causal Consistency

Causally related operations seen in same order by all.

```
A: Write(x=1)
B: Read(x)=1, Write(y=2)   <- Causal dependency
C: Must see x=1 before y=2
```

### Eventual Consistency

Given no new updates, all replicas converge eventually.

**Variations**:
- **Read-your-writes**: See own writes
- **Monotonic reads**: Never see older values
- **Monotonic writes**: Writes applied in order

## Consensus Algorithms

**Problem**: Get distributed nodes to agree on a value despite failures.

### Paxos

Classic consensus algorithm. Complex but foundational.

**Roles**:
- **Proposer**: Proposes values
- **Acceptor**: Votes on proposals
- **Learner**: Learns chosen value

**Two phases**:

```
Phase 1 (Prepare):
  Proposer -> Acceptors: prepare(n)
  Acceptors -> Proposer: promise(n, accepted_value)

Phase 2 (Accept):
  Proposer -> Acceptors: accept(n, value)
  Acceptors -> Proposer: accepted(n, value)
```

**Majority quorum**: Need > N/2 nodes to agree.

### Multi-Paxos

Optimization for sequences of values. Elect leader to skip Phase 1.

### Raft

Designed for understandability. Used in etcd, Consul.

**Roles**:
- **Leader**: Handles all client requests
- **Follower**: Passive, responds to leader
- **Candidate**: Seeking election

**Leader Election**:
```
1. Follower timeout (no heartbeat)
2. Becomes candidate, increments term
3. Votes for itself, requests votes
4. Receives majority -> becomes leader
5. Sends heartbeats to maintain leadership
```

**Log Replication**:
```
1. Client sends command to leader
2. Leader appends to local log
3. Leader replicates to followers
4. Once majority has entry, it's committed
5. Leader notifies client of success
```

**Safety**: Only nodes with up-to-date logs can be elected.

### Comparison

| Aspect | Paxos | Raft |
|--------|-------|------|
| Understandability | Complex | Simpler |
| Leader | Optional | Required |
| Safety | Proven | Proven |
| Liveness | Under assumptions | Under assumptions |

## Two-Phase Commit (2PC)

Distributed transaction protocol.

```
Phase 1 (Prepare):
  Coordinator -> Participants: "Prepare to commit"
  Participants -> Coordinator: "Ready" or "Abort"

Phase 2 (Commit/Abort):
  If all ready:
    Coordinator -> Participants: "Commit"
  Else:
    Coordinator -> Participants: "Abort"
```

**Problems**:
- **Blocking**: If coordinator fails after prepare, participants wait
- **Coordinator is single point of failure**

### Three-Phase Commit (3PC)

Adds pre-commit phase to reduce blocking. Still not perfect.

## Distributed Clocks

### Physical Clocks

Wall-clock time. Requires synchronization (NTP).

**Problems**: Clock skew, drift.

### Lamport Timestamps

Logical clocks for ordering events.

**Rules**:
1. Before event: increment local counter
2. Send message: include timestamp
3. Receive message: max(local, received) + 1

```
Process A: [1] -> [2] -> [3]
Process B:       [1] -> [2] -> [4]
              send   receive
```

**Property**: If A happened-before B, then timestamp(A) < timestamp(B).
**Limitation**: Converse not true.

### Vector Clocks

Track causality accurately.

```
Each process maintains vector [t1, t2, ..., tn]
Increment own entry on event
On receive: element-wise max + increment own

A: [1,0,0] -> [2,0,0]
B: [0,1,0] -> receive from A -> [2,2,0]
```

**Property**: A happened-before B iff A's vector <= B's element-wise.

**Concurrent**: Neither vector <= other.

## Failure Modes

### Crash Failures

Node stops responding. Can detect via timeout.

### Byzantine Failures

Node behaves arbitrarily (malicious or buggy).

**Byzantine Fault Tolerance (BFT)**:
- Need 3f+1 nodes to tolerate f failures
- Used in blockchain consensus

### Network Partitions

Groups of nodes can't communicate.

**Split brain**: Multiple leaders in different partitions.

## Quorum Systems

**Read quorum (R)**: Minimum nodes to read from.
**Write quorum (W)**: Minimum nodes to write to.
**Total nodes (N)**.

**Requirements**:
- R + W > N (read sees latest write)
- W + W > N (no concurrent writes)

**Examples**:
```
N=3, W=2, R=2  (strong consistency)
N=3, W=1, R=3  (fast writes, slow reads)
N=3, W=3, R=1  (slow writes, fast reads)
```

## Leader Election

### Bully Algorithm

Highest ID wins.

```
1. Process detects leader failure
2. Sends election to higher IDs
3. If no response, becomes leader
4. If response, wait for winner
```

### Ring Algorithm

Pass election token around ring.

## Replication Strategies

### Primary-Backup

One primary handles writes, replicates to backups.

```
         Writes
Client --------> Primary
                    |
              ------+------
              |           |
           Backup      Backup
```

### Chain Replication

Writes go to head, reads from tail.

```
Client -> Head -> Node -> ... -> Tail -> Client
         write                    read
```

**Strong consistency** with good throughput.

## Interview Questions

1. **What is the CAP theorem?**
   - Consistency, Availability, Partition tolerance
   - Can only have 2 of 3
   - Partitions happen, so choose C or A

2. **Explain Raft consensus**
   - Leader-based consensus
   - Leader election via terms
   - Log replication with majority
   - Simpler than Paxos

3. **What are vector clocks?**
   - Track causality in distributed systems
   - Each node has vector of timestamps
   - Detect concurrent vs causally related events

4. **What is 2PC and its problems?**
   - Two-phase commit for distributed transactions
   - Blocking if coordinator fails
   - Single point of failure
