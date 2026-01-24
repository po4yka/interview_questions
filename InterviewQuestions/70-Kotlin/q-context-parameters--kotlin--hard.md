---
anki_cards:
- slug: q-context-parameters--kotlin--hard-0-en
  language: en
  anki_id: 1769173383011
  synced_at: '2026-01-23T17:03:50.671543'
- slug: q-context-parameters--kotlin--hard-0-ru
  language: ru
  anki_id: 1769173383034
  synced_at: '2026-01-23T17:03:50.673589'
---
# Вопрос (RU)
> Объясните context parameters в Kotlin. Чем они отличаются от context receivers? Каков путь миграции?

# Question (EN)
> Explain context parameters in Kotlin. How do they differ from context receivers? What is the migration path?

## Ответ (RU)

**Preview с Kotlin 2.2**

**Context parameters** - это новый дизайн функции контекстных получателей, заменяющий устаревший синтаксис `context(Type)`. Новый синтаксис использует явные именованные параметры в `context()` блоке.

---

### Изменения в синтаксисе

**Старый синтаксис (context receivers):**

```kotlin
// Deprecated
context(Logger, Database)
fun fetchData(): List<String> {
    log("Fetching...")  // неявный доступ к Logger
    return query("SELECT *")  // неявный доступ к Database
}
```

**Новый синтаксис (context parameters):**

```kotlin
// Kotlin 2.2+
context(logger: Logger, db: Database)
fun fetchData(): List<String> {
    logger.log("Fetching...")  // явный доступ через имя
    return db.query("SELECT *")
}
```

---

### Ключевые отличия

| Аспект | Context Receivers | Context Parameters |
|--------|-------------------|-------------------|
| Синтаксис | `context(Type)` | `context(name: Type)` |
| Доступ | Неявный (this) | Явный (по имени) |
| Читаемость | Менее явно | Более явно |
| Конфликты имен | Возможны | Разрешаются именами |

---

### Преимущества нового подхода

**1. Явность:**

```kotlin
// Старый: откуда приходит log()?
context(Logger, Database, Cache)
fun process() {
    log("Processing")  // Logger? Откуда?
}

// Новый: ясно, что log из logger
context(logger: Logger, db: Database, cache: Cache)
fun process() {
    logger.log("Processing")  // явно
}
```

**2. Разрешение конфликтов:**

```kotlin
interface Logger { fun log(msg: String) }
interface AuditLogger { fun log(msg: String) }

// Старый: конфликт имен
context(Logger, AuditLogger)
fun audit() {
    log("...")  // какой log?
}

// Новый: нет конфликта
context(logger: Logger, audit: AuditLogger)
fun auditAction() {
    logger.log("App log")
    audit.log("Audit log")
}
```

**3. Совместимость с IDE:**

- Автодополнение работает лучше
- Рефакторинг понятнее
- Навигация к определению очевидна

---

### Практические примеры

**Transaction scope:**

```kotlin
interface Transaction {
    fun execute(sql: String)
    fun rollback()
}

context(tx: Transaction)
fun transferMoney(from: Int, to: Int, amount: Double) {
    tx.execute("UPDATE accounts SET balance = balance - $amount WHERE id = $from")
    tx.execute("UPDATE accounts SET balance = balance + $amount WHERE id = $to")
}

// Использование
fun performTransfer(db: Database, from: Int, to: Int, amount: Double) {
    db.transaction { tx ->
        with(tx) {
            transferMoney(from, to, amount)
        }
    }
}
```

**Logging context:**

```kotlin
interface Logger {
    fun info(message: String)
    fun error(message: String, e: Throwable? = null)
}

context(log: Logger)
suspend fun fetchUsers(): List<User> {
    log.info("Fetching users...")
    return try {
        api.getUsers()
    } catch (e: Exception) {
        log.error("Failed to fetch users", e)
        emptyList()
    }
}
```

**Coroutine scope:**

```kotlin
context(scope: CoroutineScope, dispatcher: CoroutineDispatcher)
fun launchWork(work: suspend () -> Unit) {
    scope.launch(dispatcher) {
        work()
    }
}
```

---

### Миграция

**Шаг 1: Добавить имена к context receivers**

```kotlin
// До
context(Logger)
fun oldFunction() { ... }

// После
context(logger: Logger)
fun newFunction() { ... }
```

**Шаг 2: Заменить неявные вызовы на явные**

```kotlin
// До
context(Logger)
fun process() {
    log("message")  // неявный вызов
}

// После
context(logger: Logger)
fun process() {
    logger.log("message")  // явный вызов
}
```

**Шаг 3: Обновить вызывающий код**

```kotlin
// Остается таким же
with(loggerInstance) {
    process()
}
```

---

### Включение функции

```kotlin
// build.gradle.kts
kotlin {
    compilerOptions {
        freeCompilerArgs.add("-Xcontext-parameters")
    }
}
```

---

### DSL с context parameters

```kotlin
@DslMarker
annotation class HtmlDsl

@HtmlDsl
class Element(val name: String) {
    val children = mutableListOf<Element>()
    fun addChild(e: Element) = children.add(e)
}

context(parent: Element)
fun div(block: context(Element) () -> Unit) {
    val element = Element("div")
    with(element) { block() }
    parent.addChild(element)
}

context(parent: Element)
fun span(text: String) {
    val element = Element("span")
    parent.addChild(element)
}

// Использование
fun buildHtml(): Element {
    val root = Element("html")
    with(root) {
        div {
            span("Hello")
        }
    }
    return root
}
```

---

### Совместимость

- Context receivers (`context(Type)`) deprecated с Kotlin 2.2
- Context parameters (`context(name: Type)`) - замена
- Постепенная миграция возможна
- IDE помогает с автоматическими исправлениями

---

## Answer (EN)

**Preview since Kotlin 2.2**

**Context parameters** is a new design for context receivers, replacing the deprecated `context(Type)` syntax. The new syntax uses explicit named parameters in the `context()` block.

---

### Syntax Changes

**Old syntax (context receivers):**

```kotlin
// Deprecated
context(Logger, Database)
fun fetchData(): List<String> {
    log("Fetching...")  // implicit access to Logger
    return query("SELECT *")  // implicit access to Database
}
```

**New syntax (context parameters):**

```kotlin
// Kotlin 2.2+
context(logger: Logger, db: Database)
fun fetchData(): List<String> {
    logger.log("Fetching...")  // explicit access via name
    return db.query("SELECT *")
}
```

---

### Key Differences

| Aspect | Context Receivers | Context Parameters |
|--------|-------------------|-------------------|
| Syntax | `context(Type)` | `context(name: Type)` |
| Access | Implicit (this) | Explicit (by name) |
| Readability | Less explicit | More explicit |
| Name conflicts | Possible | Resolved by names |

---

### Advantages of New Approach

**1. Explicitness:**

```kotlin
// Old: where does log() come from?
context(Logger, Database, Cache)
fun process() {
    log("Processing")  // Logger? From where?
}

// New: clear that log is from logger
context(logger: Logger, db: Database, cache: Cache)
fun process() {
    logger.log("Processing")  // explicit
}
```

**2. Conflict Resolution:**

```kotlin
interface Logger { fun log(msg: String) }
interface AuditLogger { fun log(msg: String) }

// Old: name conflict
context(Logger, AuditLogger)
fun audit() {
    log("...")  // which log?
}

// New: no conflict
context(logger: Logger, audit: AuditLogger)
fun auditAction() {
    logger.log("App log")
    audit.log("Audit log")
}
```

**3. IDE Compatibility:**

- Better autocompletion
- Clearer refactoring
- Obvious navigation to definition

---

### Practical Examples

**Transaction Scope:**

```kotlin
interface Transaction {
    fun execute(sql: String)
    fun rollback()
}

context(tx: Transaction)
fun transferMoney(from: Int, to: Int, amount: Double) {
    tx.execute("UPDATE accounts SET balance = balance - $amount WHERE id = $from")
    tx.execute("UPDATE accounts SET balance = balance + $amount WHERE id = $to")
}

// Usage
fun performTransfer(db: Database, from: Int, to: Int, amount: Double) {
    db.transaction { tx ->
        with(tx) {
            transferMoney(from, to, amount)
        }
    }
}
```

**Logging Context:**

```kotlin
interface Logger {
    fun info(message: String)
    fun error(message: String, e: Throwable? = null)
}

context(log: Logger)
suspend fun fetchUsers(): List<User> {
    log.info("Fetching users...")
    return try {
        api.getUsers()
    } catch (e: Exception) {
        log.error("Failed to fetch users", e)
        emptyList()
    }
}
```

**Coroutine Scope:**

```kotlin
context(scope: CoroutineScope, dispatcher: CoroutineDispatcher)
fun launchWork(work: suspend () -> Unit) {
    scope.launch(dispatcher) {
        work()
    }
}
```

---

### Migration

**Step 1: Add names to context receivers**

```kotlin
// Before
context(Logger)
fun oldFunction() { ... }

// After
context(logger: Logger)
fun newFunction() { ... }
```

**Step 2: Replace implicit calls with explicit**

```kotlin
// Before
context(Logger)
fun process() {
    log("message")  // implicit call
}

// After
context(logger: Logger)
fun process() {
    logger.log("message")  // explicit call
}
```

**Step 3: Update calling code**

```kotlin
// Stays the same
with(loggerInstance) {
    process()
}
```

---

### Enabling the Feature

```kotlin
// build.gradle.kts
kotlin {
    compilerOptions {
        freeCompilerArgs.add("-Xcontext-parameters")
    }
}
```

---

### DSL with Context Parameters

```kotlin
@DslMarker
annotation class HtmlDsl

@HtmlDsl
class Element(val name: String) {
    val children = mutableListOf<Element>()
    fun addChild(e: Element) = children.add(e)
}

context(parent: Element)
fun div(block: context(Element) () -> Unit) {
    val element = Element("div")
    with(element) { block() }
    parent.addChild(element)
}

context(parent: Element)
fun span(text: String) {
    val element = Element("span")
    parent.addChild(element)
}

// Usage
fun buildHtml(): Element {
    val root = Element("html")
    with(root) {
        div {
            span("Hello")
        }
    }
    return root
}
```

---

### Compatibility

- Context receivers (`context(Type)`) deprecated since Kotlin 2.2
- Context parameters (`context(name: Type)`) - replacement
- Gradual migration possible
- IDE helps with automatic fixes

---

## Follow-ups

- When will context parameters become stable?
- Can context parameters be optional?
- How do context parameters work with extension functions?

## Related Questions

- [[q-context-receivers--kotlin--hard]]
- [[q-kotlin-higher-order-functions--kotlin--medium]]

## References

- https://blog.jetbrains.com/kotlin/2025/04/update-on-context-parameters/
- https://github.com/Kotlin/KEEP/issues/367
- https://kotlinlang.org/docs/whatsnew22.html
