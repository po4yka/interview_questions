---
id: cs-dist-patterns
title: Distributed Systems - Design Patterns
topic: distributed_systems
difficulty: hard
tags:
- cs_distributed_systems
- patterns
anki_cards:
- slug: cs-dist-pat-0-en
  language: en
  anki_id: 1769160675277
  synced_at: '2026-01-23T13:31:18.857821'
- slug: cs-dist-pat-0-ru
  language: ru
  anki_id: 1769160675300
  synced_at: '2026-01-23T13:31:18.859095'
- slug: cs-dist-pat-1-en
  language: en
  anki_id: 1769160675325
  synced_at: '2026-01-23T13:31:18.860383'
- slug: cs-dist-pat-1-ru
  language: ru
  anki_id: 1769160675349
  synced_at: '2026-01-23T13:31:18.861603'
- slug: cs-dist-pat-2-en
  language: en
  anki_id: 1769160675374
  synced_at: '2026-01-23T13:31:18.864265'
- slug: cs-dist-pat-2-ru
  language: ru
  anki_id: 1769160675400
  synced_at: '2026-01-23T13:31:18.865525'
---
# Distributed Systems Patterns

## Communication Patterns

### Request-Response

Synchronous communication. Client waits for response.

```
Client --request--> Server
Client <--response-- Server
```

**Use case**: APIs, RPC.

### Publish-Subscribe

Asynchronous, decoupled communication.

```
Publisher -> Topic -> Subscriber 1
                  -> Subscriber 2
                  -> Subscriber 3
```

**Use case**: Event-driven systems, notifications.

### Message Queue

Producer-consumer with queue buffer.

```
Producer -> Queue -> Consumer
```

**Use case**: Task processing, load leveling.

## Resilience Patterns

### Circuit Breaker

Prevent cascade failures by stopping calls to failing service.

```
States:
  Closed: Requests flow normally
  Open: Requests fail immediately
  Half-Open: Test requests to check recovery

         success
  Closed ---------> Closed
    |
    | failure threshold
    v
   Open
    |
    | timeout
    v
  Half-Open
    |
    +-- success --> Closed
    +-- failure --> Open
```

```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, timeout=60):
        self.failures = 0
        self.threshold = failure_threshold
        self.timeout = timeout
        self.state = 'closed'
        self.last_failure = None

    def call(self, func, *args):
        if self.state == 'open':
            if time.time() - self.last_failure > self.timeout:
                self.state = 'half-open'
            else:
                raise CircuitOpenError()

        try:
            result = func(*args)
            if self.state == 'half-open':
                self.state = 'closed'
            self.failures = 0
            return result
        except Exception as e:
            self.failures += 1
            self.last_failure = time.time()
            if self.failures >= self.threshold:
                self.state = 'open'
            raise
```

### Retry with Backoff

Retry failed operations with increasing delays.

```python
def retry_with_backoff(func, max_retries=3, base_delay=1):
    for attempt in range(max_retries):
        try:
            return func()
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt)  # Exponential
            delay += random.uniform(0, delay * 0.1)  # Jitter
            time.sleep(delay)
```

**Strategies**:
- **Fixed**: Same delay each time
- **Linear**: delay = base * attempt
- **Exponential**: delay = base * 2^attempt
- **Jitter**: Add randomness to prevent thundering herd

### Bulkhead

Isolate failures to prevent cascade.

```
                +-------------+
Request 1 ----->| Pool A      |-----> Service A
                +-------------+
                +-------------+
Request 2 ----->| Pool B      |-----> Service B
                +-------------+

Service A failure doesn't exhaust Pool B
```

### Timeout

Don't wait forever for response.

```python
try:
    response = requests.get(url, timeout=5)
except requests.Timeout:
    # Handle timeout
```

**Types**:
- Connection timeout
- Read timeout
- Total timeout

## Data Patterns

### Saga Pattern

Long-running transactions with compensating actions.

```
Choreography (events):
  Order Created -> Payment Charged -> Inventory Reserved -> Order Confirmed
       |                |                   |
       v                v                   v
  Cancel Order    Refund Payment    Release Inventory

Orchestration (central coordinator):
  Saga Orchestrator controls all steps
```

**Compensation**: Undo action if later step fails.

### Event Sourcing

Store all changes as events, derive state.

```
Events:
  AccountCreated(id=1, name="John")
  MoneyDeposited(id=1, amount=100)
  MoneyWithdrawn(id=1, amount=30)

Current State:
  id=1, name="John", balance=70
```

**Benefits**:
- Complete audit trail
- Temporal queries
- Easy debugging

### CQRS (Command Query Responsibility Segregation)

Separate read and write models.

```
         Commands                    Queries
Client -----------> Write Model   Read Model <------ Client
                         |             ^
                         v             |
                    Event Store -------+
                         |
                    Projection
```

**Benefits**: Optimize read/write independently.

### Outbox Pattern

Ensure exactly-once message delivery with database.

```
Transaction:
  1. Update business data
  2. Insert message to outbox table

Separate process:
  1. Read outbox
  2. Publish message
  3. Mark as processed

Guarantees: Message published iff data committed
```

## Scaling Patterns

### Consistent Hashing

Distribute data with minimal reshuffling when nodes change.

```
Hash ring:
        Node A
       /      \
  Node D      Node B
       \      /
        Node C

Key hashed to position, stored on next node clockwise
Adding/removing node only affects neighbors
```

### Sharding

Split data across multiple databases.

```
Shard key: user_id
Shard 1: user_id % 4 == 0
Shard 2: user_id % 4 == 1
Shard 3: user_id % 4 == 2
Shard 4: user_id % 4 == 3
```

**Challenges**: Cross-shard queries, transactions, rebalancing.

### Read Replicas

Scale reads by replicating data.

```
Write --> Primary
           |
     +-----+-----+
     |     |     |
  Replica Replica Replica <-- Reads
```

## Caching Patterns

### Cache-Aside

Application manages cache.

```python
def get_user(user_id):
    # Check cache
    user = cache.get(f"user:{user_id}")
    if user:
        return user

    # Cache miss - fetch from DB
    user = db.get_user(user_id)
    cache.set(f"user:{user_id}", user, ttl=3600)
    return user
```

### Write-Through

Write to cache and DB together.

```
Write -> Cache -> DB
```

### Write-Behind (Write-Back)

Write to cache, async write to DB.

```
Write -> Cache
         |
         +--> Async --> DB
```

### Cache Invalidation

**TTL**: Expire after time.
**Event-based**: Invalidate on update.
**Versioning**: Include version in key.

## Service Discovery

### Client-Side Discovery

Client queries registry, chooses instance.

```
Client -> Service Registry -> [Service A instances]
Client -> Service A (chosen instance)
```

### Server-Side Discovery

Load balancer queries registry.

```
Client -> Load Balancer -> Service Registry
                       -> Service A instance
```

### Tools

- **Consul**: Service mesh, health checking
- **etcd**: Distributed key-value store
- **ZooKeeper**: Coordination service

## Idempotency

Operation can be applied multiple times with same result.

```python
# Idempotent: SET
cache.set("key", "value")  # Same result if called twice

# Not idempotent: INCREMENT
counter.increment()  # Different result each time

# Make non-idempotent idempotent with idempotency key
def create_order(idempotency_key, order_data):
    existing = db.get_by_idempotency_key(idempotency_key)
    if existing:
        return existing  # Return cached result
    order = db.create_order(order_data)
    db.save_idempotency(idempotency_key, order)
    return order
```

## Interview Questions

1. **What is the circuit breaker pattern?**
   - Prevent cascade failures
   - States: closed, open, half-open
   - Fails fast when service is down

2. **How does consistent hashing work?**
   - Hash ring with nodes and keys
   - Minimal reshuffling on node changes
   - Used in distributed caches

3. **What is the saga pattern?**
   - Long-running distributed transactions
   - Compensating actions for rollback
   - Choreography or orchestration

4. **How to ensure exactly-once delivery?**
   - Outbox pattern with transactional messaging
   - Idempotency keys for consumers
   - Deduplication at receiver
