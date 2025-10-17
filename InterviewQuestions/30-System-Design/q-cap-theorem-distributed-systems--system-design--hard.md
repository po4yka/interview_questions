---
id: 20251012-300004
title: "CAP Theorem and Distributed Systems / CAP теорема и распределённые системы"
topic: system-design
difficulty: hard
status: draft
created: 2025-10-12
tags: - system-design
  - distributed-systems
  - cap-theorem
  - consistency
  - availability
moc: moc-system-design
related:   - q-eventual-consistency--system-design--hard
  - q-database-replication--system-design--medium
  - q-consensus-algorithms--system-design--hard
subtopics:   - distributed-systems
  - consistency
  - availability
  - partition-tolerance
  - cap-theorem
---
# Question (EN)
> What is the CAP theorem? What trade-offs do different systems make, and how do you choose between CP and AP systems?

# Вопрос (RU)
> Что такое CAP теорема? Какие компромиссы делают разные системы, и как выбрать между CP и AP системами?

---

## Answer (EN)

When designing distributed systems, you cannot have all three guarantees simultaneously: **Consistency**, **Availability**, and **Partition Tolerance**. Understanding the CAP theorem helps you make informed trade-offs when designing distributed databases and systems.



### What is the CAP Theorem?

**CAP Theorem** (Brewer's Theorem) states that a distributed system can provide at most **TWO** of the following three guarantees:

```
        C (Consistency)
           /\
          /  \
         /    \
        /    \
       /  Pick  \
      /   Only   \
     /     2      \
    /______________\
   A                P
(Availability)  (Partition
                Tolerance)
```

### The Three Guarantees

**1. Consistency (C)**
- Every read receives the most recent write
- All nodes see the same data at the same time
- Strong consistency guarantee

```
Write(x=5) → Node1
Read(x) from Node2 → Must return 5 (not old value)
```

**2. Availability (A)**
- Every request receives a response (success or failure)
- No request is lost
- System remains operational

```
Request → Node1 (down) → Node2 responds 
All requests get responses, even if nodes fail
```

**3. Partition Tolerance (P)**
- System continues to operate despite network partitions
- Nodes can't communicate, but system still works
- Network failures are tolerated

```
Network Split:
[Node1, Node2] | PARTITION | [Node3, Node4]
      ↕                           ↕
Can't communicate, but both sides still work
```

---

### CAP Trade-offs

### In Reality: You Must Choose P

**Network partitions WILL happen:**
- Network failures
- Data center outages
- Hardware failures
- Slow networks

**Therefore, real choice is:**
- **CP** (Consistency + Partition Tolerance) - Sacrifice Availability
- **AP** (Availability + Partition Tolerance) - Sacrifice Consistency

```
Real-world CAP:
Pick one 
               
        
                     
       CP            AP
  (Consistent)  (Available)
  but may       but may be
  reject        inconsistent
  requests      temporarily
```

---

### CP Systems (Consistency + Partition Tolerance)

**Trade-off:** Sacrifice availability for consistency

**Behavior during partition:**
- Returns error if can't guarantee consistency
- Blocks reads/writes until partition resolves
- Maintains strong consistency

**Examples:**
- **MongoDB** (with default settings)
- **HBase**
- **Redis** (with wait command)
- **Zookeeper**
- **etcd**
- **Consul**

**Use Cases:**
- Financial systems (bank transfers)
- Inventory management
- Booking systems
- Any system where incorrect data is worse than no data

**Example: Banking System**
```kotlin
// CP System: Bank account transfer
class BankingService(
    private val database: ConsistentDB // CP database
) {
    suspend fun transfer(from: Long, to: Long, amount: Money): Result<Transfer> {
        return try {
            database.transaction {
                // Strong consistency - blocks if partition exists
                val fromAccount = database.getAccount(from)
                    ?: return Result.Error("Source account not found")

                val toAccount = database.getAccount(to)
                    ?: return Result.Error("Destination account not found")

                if (fromAccount.balance < amount) {
                    return Result.Error("Insufficient funds")
                }

                // Both updates or neither (ACID)
                database.updateBalance(from, fromAccount.balance - amount)
                database.updateBalance(to, toAccount.balance + amount)

                Result.Success(Transfer(from, to, amount))
            }
        } catch (e: PartitionException) {
            // During partition, reject request (sacrifice availability)
            Result.Error("Service temporarily unavailable")
        }
    }
}
```

**MongoDB CP Example:**
```javascript
// MongoDB with majority write concern (CP)
db.accounts.updateOne(
  { _id: accountId },
  { $inc: { balance: -100 } },
  {
    writeConcern: { w: "majority", j: true },
    readConcern: { level: "majority" }
  }
);
// Blocks until majority of replicas confirm
// During partition: may timeout/fail (sacrifices availability)
```

---

### AP Systems (Availability + Partition Tolerance)

**Trade-off:** Sacrifice consistency for availability

**Behavior during partition:**
- Always accepts reads and writes
- Different nodes may have different data
- Eventually consistent (converges over time)

**Examples:**
- **Cassandra**
- **DynamoDB**
- **Riak**
- **CouchDB**
- **DNS**

**Use Cases:**
- Social media feeds
- Product catalogs
- Logging/analytics
- Shopping carts
- View counts/likes
- Any system where availability > consistency

**Example: Social Media Likes**
```kotlin
// AP System: Like counter (eventual consistency OK)
class SocialMediaService(
    private val database: AvailableDB // AP database
) {
    suspend fun likePost(postId: Long, userId: Long): Result<Unit> {
        return try {
            // Always succeeds, even during partition
            database.incrementLikes(postId)
            database.addUserLike(postId, userId)

            Result.Success(Unit)
        } catch (e: Exception) {
            // Rarely fails - high availability
            Result.Error("Could not process like")
        }
    }

    suspend fun getLikes(postId: Long): Int {
        // May return slightly stale count (eventual consistency)
        // Different replicas might show different counts temporarily
        return database.getLikes(postId)
    }
}
```

**Cassandra AP Example:**
```kotlin
// Cassandra with eventual consistency (AP)
session.execute(
    "UPDATE posts SET likes = likes + 1 WHERE id = ?",
    postId
)
// Write succeeds immediately on available nodes
// During partition: writes accepted on both sides
// After partition heals: conflict resolution (last-write-wins)
```

---

### Conflict Resolution in AP Systems

When partition heals, how to resolve conflicts?

### 1. Last-Write-Wins (LWW)
```
Partition occurs:
Side A: Write x=10 at timestamp T1
Side B: Write x=20 at timestamp T2 (T2 > T1)

After merge:
x = 20 (timestamp T2 wins)
```

**Pros:** Simple
**Cons:** Data loss possible

### 2. Version Vectors
```
Initial: x=5 [v1]

Partition:
Side A: x=10 [v2a]
Side B: x=20 [v2b]

After merge:
Conflict detected! [v2a] vs [v2b]
→ Application-level resolution required
```

### 3. CRDTs (Conflict-free Replicated Data Types)
```kotlin
// Counter CRDT - always converges correctly
class GCounter {
    private val counters = mutableMapOf<NodeId, Long>()

    fun increment(nodeId: NodeId, amount: Long = 1) {
        counters[nodeId] = (counters[nodeId] ?: 0) + amount
    }

    fun value(): Long = counters.values.sum()

    fun merge(other: GCounter): GCounter {
        val merged = GCounter()
        (counters.keys + other.counters.keys).forEach { nodeId ->
            merged.counters[nodeId] = maxOf(
                counters[nodeId] ?: 0,
                other.counters[nodeId] ?: 0
            )
        }
        return merged
    }
}

// Usage during partition
val counter1 = GCounter()
counter1.increment(node1, 5)

val counter2 = GCounter()
counter2.increment(node2, 3)

// After partition heals
val merged = counter1.merge(counter2)
merged.value() // = 8 (correct!)
```

---

### Consistency Models

### Strong Consistency (CP)
- Reads always return latest write
- Linearizability
- Like single-machine behavior

```
Write(x=5) completed at T1
Read(x) at T2 (T2 > T1) → Always returns 5
```

### Eventual Consistency (AP)
- All replicas converge to same value eventually
- Reads may return stale data temporarily
- Given enough time without writes, all reads return same value

```
Write(x=5) at T1
Read(x) at T2 (T2 > T1) → May return old value temporarily
Read(x) at T3 (T3 >> T1) → Eventually returns 5
```

### Causal Consistency
- Preserves cause-effect relationships
- Weaker than strong, stronger than eventual

```
Write(x=5) causes Write(y=10)
All nodes see x=5 before y=10 (causal order preserved)
```

---

### Real-World Examples

### CP System: MongoDB

```javascript
// MongoDB with strong consistency
const session = client.startSession();
session.startTransaction({
  readConcern: { level: 'snapshot' },
  writeConcern: { w: 'majority', j: true }
});

try {
  // Strongly consistent read
  const account = await Account.findById(accountId).session(session);

  if (account.balance < amount) {
    throw new Error('Insufficient funds');
  }

  account.balance -= amount;
  await account.save({ session });

  await session.commitTransaction();
} catch (error) {
  await session.abortTransaction();
  // During partition: transaction fails (sacrifices availability)
  throw error;
} finally {
  session.endSession();
}
```

### AP System: Cassandra

```kotlin
// Cassandra with tunable consistency
class CassandraRepository(private val session: CqlSession) {

    fun writePost(post: Post) {
        // Write with LOCAL_QUORUM (AP - favors availability)
        session.execute(
            SimpleStatement.newInstance(
                "INSERT INTO posts (id, content, likes) VALUES (?, ?, ?)",
                post.id, post.content, post.likes
            ).setConsistencyLevel(ConsistencyLevel.LOCAL_QUORUM)
        )
        // Succeeds even if some replicas are down
    }

    fun readPost(id: UUID): Post? {
        // Read with ONE (AP - maximum availability)
        val result = session.execute(
            SimpleStatement.newInstance(
                "SELECT * FROM posts WHERE id = ?",
                id
            ).setConsistencyLevel(ConsistencyLevel.ONE)
        )
        // Returns immediately from any available replica
        // May return slightly stale data
        return result.one()?.let { /* map to Post */ }
    }
}
```

---

### Hybrid Approaches

### Tunable Consistency

**Cassandra/DynamoDB allow tuning:**
```
Quorum Reads + Quorum Writes = Strong Consistency
R + W > N (where N = replication factor)

Example: N=3, R=2, W=2
2 + 2 > 3 → Guarantees consistency
```

```kotlin
// Cassandra tunable consistency
fun criticalRead(id: UUID): Data {
    // CP behavior: strong consistency for critical reads
    return session.execute(
        statement.setConsistencyLevel(ConsistencyLevel.QUORUM)
    )
}

fun casualRead(id: UUID): Data {
    // AP behavior: eventual consistency for casual reads
    return session.execute(
        statement.setConsistencyLevel(ConsistencyLevel.ONE)
    )
}
```

### PACELC Extension

**PACELC**: If **P**artition, choose **A** or **C**, **E**lse (no partition), choose **L**atency or **C**onsistency

```
During Partition: A vs C
Normal operation: Latency vs Consistency

Examples:
- DynamoDB: PA/EL (Availability during partition, Low latency normally)
- MongoDB: PC/EC (Consistency during partition and normally)
- Cassandra: PA/EL (Availability and Low latency)
```

---

### Decision Matrix

| Requirement | Choose | Example |
|------------|--------|---------|
| Financial transactions | CP | Banking, payments |
| Strong consistency needed | CP | Inventory, bookings |
| High availability critical | AP | Social media, catalogs |
| Network partitions common | AP | Geo-distributed systems |
| Temporary inconsistency OK | AP | View counts, likes |
| Incorrect data unacceptable | CP | Medical records |
| 100% uptime required | AP | CDN, DNS |

---

### Key Takeaways

1. **CAP Theorem**: Can't have all three (C, A, P) simultaneously
2. **Network partitions happen** - must choose P
3. **Real choice**: CP (consistent) vs AP (available)
4. **CP systems**: Reject requests during partition (banks, inventory)
5. **AP systems**: Accept requests, eventual consistency (social media)
6. **Conflict resolution**: LWW, version vectors, CRDTs
7. **Strong consistency**: CP, all nodes see same data
8. **Eventual consistency**: AP, converges over time
9. **Tunable consistency**: Some systems allow per-request tuning
10. **PACELC**: Consider latency vs consistency in normal operation too

---

## Ответ (RU)

При проектировании распределённых систем невозможно одновременно иметь все три гарантии: **Консистентность**, **Доступность** и **Устойчивость к разделению**. Понимание CAP теоремы помогает принимать обоснованные компромиссы при проектировании распределённых баз данных и систем.



### Что такое CAP теорема?

**CAP теорема** (теорема Брюера) гласит, что распределённая система может обеспечить максимум **ДВЕ** из следующих трёх гарантий:

```
        C (Consistency)
    (Консистентность)
           /\
          /  \
         /    \
        /    \
       / Выбери \
      /  только  \
     /     2      \
    /______________\
   A                P
(Availability)  (Partition
(Доступность)    Tolerance)
              (Устойчивость
              к разделению)
```

### Три гарантии

**1. Consistency (Консистентность)**
- Каждое чтение получает самую последнюю запись
- Все узлы видят одинаковые данные одновременно
- Гарантия строгой консистентности

**2. Availability (Доступность)**
- Каждый запрос получает ответ (успех или неудачу)
- Ни один запрос не теряется
- Система остаётся работоспособной

**3. Partition Tolerance (Устойчивость к разделению)**
- Система продолжает работать несмотря на разделение сети
- Узлы не могут общаться, но система все еще работает
- Сетевые сбои допускаются

### CP системы (Консистентность + Устойчивость к разделению)

**Компромисс:** Жертвуем доступностью ради консистентности

**Примеры:**
- **MongoDB**
- **HBase**
- **Redis**
- **Zookeeper**
- **etcd**

**Сценарии использования:**
- Финансовые системы (банковские переводы)
- Управление инвентарём
- Системы бронирования
- Любая система, где неправильные данные хуже чем отсутствие данных

### AP системы (Доступность + Устойчивость к разделению)

**Компромисс:** Жертвуем консистентностью ради доступности

**Примеры:**
- **Cassandra**
- **DynamoDB**
- **Riak**
- **CouchDB**
- **DNS**

**Сценарии использования:**
- Ленты социальных сетей
- Каталоги товаров
- Логирование/аналитика
- Корзины покупок
- Счётчики просмотров/лайков

### Ключевые выводы

1. **CAP теорема**: Нельзя иметь все три (C, A, P) одновременно
2. **Сетевые разделения случаются** - нужно выбирать P
3. **Реальный выбор**: CP (консистентные) vs AP (доступные)
4. **CP системы**: Отклоняют запросы во время разделения (банки, инвентарь)
5. **AP системы**: Принимают запросы, eventual consistency (соцсети)
6. **Разрешение конфликтов**: LWW, version vectors, CRDTs
7. **Строгая консистентность**: CP, все узлы видят одинаковые данные
8. **Eventual consistency**: AP, со временем сходится
9. **Настраиваемая консистентность**: Некоторые системы позволяют настройку per-request
10. **PACELC**: Учитывайте latency vs consistency и в нормальной работе

## Follow-ups

1. What is the difference between strong and eventual consistency?
2. How does the PACELC theorem extend CAP?
3. Explain different conflict resolution strategies in AP systems
4. What are CRDTs and how do they help in distributed systems?
5. How does quorum-based replication work?
6. What is the difference between linearizability and serializability?
7. How do you implement distributed transactions in microservices?
8. Explain the two-phase commit (2PC) protocol and its limitations
9. What is the Saga pattern for distributed transactions?
10. How do consensus algorithms (Raft, Paxos) relate to CAP theorem?

---

## Related Questions

### Android Implementation
- [[q-when-can-the-system-restart-a-service--android--medium]] - Networking
- [[q-data-sync-unstable-network--android--hard]] - Networking
- [[q-kmm-ktor-networking--multiplatform--medium]] - Networking
- [[q-retrofit-call-adapter-advanced--networking--medium]] - Networking
- [[q-network-error-handling-strategies--networking--medium]] - Networking
- [[q-api-file-upload-server--android--medium]] - Networking
- [[q-okhttp-interceptors-advanced--networking--medium]] - Networking
