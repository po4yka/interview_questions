---
id: android-427
title: "Room Full-Text Search (FTS) / Полнотекстовый поиск FTS в Room"
aliases: ["Room Full-Text Search", "Полнотекстовый поиск FTS в Room"]
topic: android
subtopics: [room]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-basics, c-database-performance, q-android-storage-types--android--medium]
created: 2025-10-15
updated: 2025-10-15
sources: []
tags: [android/room, difficulty/hard]

---

# Вопрос (RU)

> Реализуйте полнотекстовый поиск в Room с использованием FTS4/FTS5. Оптимизируйте производительность поиска для больших наборов данных. Когда использовать FTS вместо LIKE? Как синхронизировать FTS таблицы с основными таблицами?

# Question (EN)

> Implement full-text search in Room using FTS4/FTS5. Optimize search performance for large datasets. When to use FTS instead of LIKE? How to synchronize FTS tables with main tables?

---

## Ответ (RU)

**Полнотекстовый поиск (FTS)** в Room обеспечивает эффективный текстовый поиск через расширения FTS SQLite. На больших наборах данных FTS обычно значительно быстрее, чем LIKE-запросы по неиндексированному тексту, и поддерживает ранжирование (FTS5), префиксный поиск и булевы операторы.

### Когда Использовать FTS

| Сценарий | LIKE | FTS4/FTS5 |
|----------|------|-----------|
| Малые таблицы (порядка сотен записей) | ✅ Часто достаточно | ⚠️ Может быть избыточно |
| Крупные таблицы (десятки/сотни тысяч записей) | ❌ Часто медленно без спец. индексов | ✅ Обычно быстрее и масштабируемее |
| Простой поиск по одному полю | ✅ Проще | ⚠️ Сложнее в настройке |
| Ранжирование по релевантности | ❌ Нет | ✅ Через `bm25()` (FTS5) |
| Продвинутый / префиксный поиск | ❌ Ограничен шаблонами `%` | ✅ Специализированные операторы и индексация |

(Цифры про «10-100x» рассматривайте как типичную оценку для полнотекстовых задач, а не жёсткую гарантию: всё зависит от данных и запросов.)

**Ключевые возможности FTS (особенно FTS5)**:
- Повышенная производительность полнотекстового поиска по сравнению с последовательным LIKE-поиском
- Ранжирование по релевантности через `bm25()` (FTS5)
- Функции `highlight()` и `snippet()`
- Булевы операторы (AND, OR, NOT) и префиксный поиск в MATCH-выражениях

### Базовая Реализация (пример с FTS5)

Пример ниже показывает FTS-таблицу с внешним содержимым (external content) для FTS5.

```kotlin
// ✅ Основная сущность
@Entity(tableName = "articles")
data class Article(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val title: String,
    val content: String
)

// ✅ FTS5 сущность с внешним содержимым (избегает дублирования)
// Требуется версия Room с поддержкой @Fts5
@Fts5(contentEntity = Article::class)
@Entity(tableName = "articles_fts")
data class ArticleFts(
    // Для FTS-таблиц Room использует виртуальный rowid; явный @PrimaryKey обычно не объявляется
    val title: String,    // Индексируется
    val content: String   // Индексируется
)
```

Если используется FTS4, аннотация будет `@Fts4`, а часть функций (например, `bm25()`) недоступна.

### Синхронизация С Основной Таблицей

Для external content FTS-таблиц есть два основных подхода:

1. Настроить виртуальную таблицу как `content='articles'`, `content_rowid='id'` (Room делает это при `contentEntity`), и обеспечивать согласованность вставками/обновлениями в основную таблицу.
2. Использовать триггеры для явного обновления FTS-таблицы при изменениях основной таблицы.

Ниже пример с триггерами (упрощённый; подходит для базового сценария, не учитывает все варианты contentless-таблиц):

```kotlin
@Database(entities = [Article::class, ArticleFts::class], version = 1)
abstract class AppDatabase : RoomDatabase() {

    override fun onCreate(db: SupportSQLiteDatabase) {
        super.onCreate(db)

        // ✅ Автоматическая синхронизация при INSERT
        db.execSQL("""
            CREATE TRIGGER IF NOT EXISTS articles_fts_insert
            AFTER INSERT ON articles
            BEGIN
                INSERT INTO articles_fts(rowid, title, content)
                VALUES (new.id, new.title, new.content);
            END;
        """)

        // ✅ Автоматическая синхронизация при UPDATE
        db.execSQL("""
            CREATE TRIGGER IF NOT EXISTS articles_fts_update
            AFTER UPDATE ON articles
            BEGIN
                UPDATE articles_fts
                SET title = new.title,
                    content = new.content
                WHERE rowid = new.id;
            END;
        """)

        // ✅ Автоматическая синхронизация при DELETE
        db.execSQL("""
            CREATE TRIGGER IF NOT EXISTS articles_fts_delete
            AFTER DELETE ON articles
            BEGIN
                DELETE FROM articles_fts WHERE rowid = old.id;
            END;
        """)
    }
}
```

Важно: точная схема триггеров и использование вспомогательных команд FTS (`INSERT`, `DELETE`, `UPDATE`) зависит от того, используется ли external content/contentless режим. Для production-решения нужно строго следовать документации SQLite FTS и Room.

### Поиск С Ранжированием BM25 (FTS5)

```kotlin
data class ArticleSearchResult(
    @Embedded val article: Article,
    val rank: Double  // ✅ bm25 score (меньше = релевантнее)
)

@Dao
interface ArticleDao {
    // ✅ Базовый поиск с ранжированием (FTS5)
    @Query("""
        SELECT articles.*, bm25(articles_fts) AS rank
        FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY rank
    """)
    fun search(query: String): Flow<List<ArticleSearchResult>>

    // ✅ Взвешенное ранжирование (title важнее content)
    @Query("""
        SELECT articles.*, bm25(articles_fts, 10.0, 1.0) AS rank
        FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY rank
        LIMIT :limit
    """)
    suspend fun searchWeighted(query: String, limit: Int): List<ArticleSearchResult>

    // ✅ Префиксный поиск для автодополнения (FTS MATCH синтаксис)
    @Query("""
        SELECT articles.*
        FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query || '*'
        LIMIT 10
    """)
    suspend fun autocomplete(query: String): List<Article>
}
```

(Функции `bm25()` и расширенные MATCH-выражения требуют FTS5 и сборки SQLite/Room с соответствующей поддержкой.)

### Подсветка Результатов

```kotlin
data class ArticleWithHighlight(
    @Embedded val article: Article,
    val highlightedTitle: String,    // ✅ Подсвеченный заголовок
    val snippet: String,             // ✅ Фрагмент с контекстом
    val rank: Double
)

@Dao
interface ArticleDaoHighlight {
    @Query("""
        SELECT articles.*,
               highlight(articles_fts, 0, '<b>', '</b>') AS highlightedTitle,
               snippet(articles_fts, 1, '<mark>', '</mark>', '...', 30) AS snippet,
               bm25(articles_fts) AS rank
        FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY rank
        LIMIT :limit
    """)
    suspend fun searchWithHighlight(query: String, limit: Int): List<ArticleWithHighlight>
}
```

### Repository С Debouncing

```kotlin
class ArticleRepository(private val dao: ArticleDao) {

    // ✅ Debouncing для оптимизации UX (примерный вариант)
    fun search(queryFlow: Flow<String>): Flow<List<ArticleSearchResult>> {
        return queryFlow
            .debounce(300)
            .map { it.trim() }
            .filter { it.length >= 2 }
            .distinctUntilChanged()
            .flatMapLatest { query ->
                dao.search(simpleSanitize(query))
            }
    }

    // Простейшая санитизация для демонстрации.
    // В реальном коде нужно аккуратно обрабатывать спецсимволы и операторы FTS.
    private fun simpleSanitize(query: String): String {
        return query
            .replace("\"", "")
            .split("\\s+".toRegex())
            .filter { it.isNotEmpty() }
            .joinToString(" AND ")
    }
}
```

### Токенизаторы

```kotlin
// ✅ Unicode61 (по умолчанию в FTS5) — поддержка большинства языков
@Fts5(tokenizer = FtsOptions.TOKENIZER_UNICODE61)
@Entity(tableName = "articles_fts_unicode")
data class ArticleFtsUnicode(
    val title: String,
    val content: String
)

// ✅ Porter — английский stemming ("running" → "run")
@Fts5(tokenizer = FtsOptions.TOKENIZER_PORTER)
@Entity(tableName = "articles_fts_porter")
data class ArticleFtsPorter(
    val title: String,
    val content: String
)

// ⚠️ Simple — простой байтовый токенизатор, не Unicode-aware,
// обычно не подходит для интернациональных текстов
@Fts5(tokenizer = FtsOptions.TOKENIZER_SIMPLE)
@Entity(tableName = "articles_fts_simple")
data class ArticleFtsSimple(
    val title: String,
    val content: String
)
```

Конкретный набор токенизаторов и параметры зависит от версии Room/SQLite и сборки.

### Best Practices

1. ✅ **Используйте FTS5 для новых проектов**, если версия Room/SQLite его поддерживает: больше возможностей и лучшее ранжирование.
2. ✅ **Рассмотрите external content (`contentEntity`)**, чтобы избегать ненужного дублирования, но допускается и contentless-схема, если она лучше подходит под задачи.
3. ✅ **Настройте автоматическую синхронизацию** FTS-таблиц через триггеры или корректно сконфигурированный external content.
4. ✅ **Индексируйте только действительно searchable-поля**, чтобы уменьшить размер индекса и ускорить поиск.
5. ✅ **Используйте debouncing и/или throttling** в UI, чтобы не спамить базу запросами на каждый символ.
6. ✅ **Используйте ранжирование (`bm25`)** там, где важна релевантность (FTS5).
7. ✅ **Корректно обрабатывайте пользовательский ввод** (экранирование спецсимволов, резервированных слов, операторов) вместо слепого подставления в MATCH.
8. ⚠️ **Используйте Paging** для больших результатов, чтобы не загружать всю выборку в память.
9. ⚠️ **Соблюдайте атомарность операций** (например, через `@Transaction` или триггеры), чтобы данные и FTS-индекс не расходились.
10. ⚠️ **Осознанно выбирайте между external content и дублированием данных** — выбор зависит от требований к размеру, скорости и простоте.

### Частые Ошибки

```kotlin
// ❌ Ручная синхронизация без триггеров (подвержена расхождениям)
@Transaction
suspend fun insert(article: Article) {
    val id = insertArticle(article)
    // Легко забыть обновить FTS при обновлении/удалении
    insertFts(ArticleFts(title = article.title, content = article.content))
}

// ✅ Предпочтительно: автоматическая синхронизация через триггеры
// или строго инкапсулированные DAO-операции

// ❌ Отсутствие обработки пользовательского ввода в MATCH
// dao.search(userInput)

// ✅ Минимум: нормализовать/экранировать ввод перед MATCH
// dao.search(simpleSanitize(userInput))

// ❌ Индексация всех полей
@Fts5(contentEntity = Article::class)
data class ArticleFtsTooWide(
    val title: String,
    val content: String,
    val metadata: String,  // Лишняя нагрузка на индекс
    val timestamp: Long    // Обычно не нужен в полнотекстовом индексе
)

// ✅ Индексация только полнотекстовых полей
@Fts5(contentEntity = Article::class)
data class ArticleFtsNarrow(
    val title: String,
    val content: String
)
```

---

## Answer (EN)

**Full-Text Search (FTS)** in Room provides efficient text search via SQLite FTS extensions. On large datasets, FTS is typically much faster than naive LIKE scans over unindexed text and supports (with FTS5) relevance ranking, prefix search, and boolean operators.

### When to Use FTS

| Scenario | LIKE | FTS4/FTS5 |
|----------|------|-----------|
| Small tables (hundreds of rows) | ✅ Often sufficient | ⚠️ May be overkill |
| Large tables (tens/hundreds of thousands of rows) | ❌ Often slow without proper indexes | ✅ Usually faster and more scalable |
| Simple search on one column | ✅ Simpler | ⚠️ More setup |
| Relevance ranking | ❌ Not built-in | ✅ `bm25()` (FTS5) |
| Advanced/prefix search | ❌ Limited to `%` patterns | ✅ Dedicated MATCH syntax/indexing |

(Values like "10-100x faster" should be treated as typical for full-text workloads, not a strict guarantee. Actual gains depend on schema, data, and queries.)

**Key FTS (esp. FTS5) features**:
- Better performance for full-text queries vs. sequential LIKE scans
- Relevance ranking via `bm25()` (FTS5)
- `highlight()` and `snippet()` helper functions
- Boolean operators and prefix queries in MATCH expressions

### Basic Implementation (FTS5 Example)

The following shows an FTS5 table with external content (no duplicated storage).

```kotlin
// ✅ Main entity
@Entity(tableName = "articles")
data class Article(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val title: String,
    val content: String
)

// ✅ FTS5 entity with external content (avoids duplication)
// Requires a Room version that supports @Fts5
@Fts5(contentEntity = Article::class)
@Entity(tableName = "articles_fts")
data class ArticleFts(
    // For FTS entities Room relies on the virtual table rowid; you typically do not declare @PrimaryKey
    val title: String,    // Indexed
    val content: String   // Indexed
)
```

If you use FTS4 instead, replace `@Fts5` with `@Fts4` and note that features like `bm25()` are not available.

### Synchronization with Main Table

For external content FTS tables you have two main options:

1. Configure the virtual table with `content='articles'` and `content_rowid='id'` (Room does this based on `contentEntity`), and rely on consistent writes to the main table.
2. Use triggers to explicitly keep the FTS table in sync with the main table.

Below is a simplified trigger-based example (suitable for a basic external content pattern; details depend on your exact FTS mode):

```kotlin
@Database(entities = [Article::class, ArticleFts::class], version = 1)
abstract class AppDatabase : RoomDatabase() {

    override fun onCreate(db: SupportSQLiteDatabase) {
        super.onCreate(db)

        // ✅ Auto-sync on INSERT
        db.execSQL("""
            CREATE TRIGGER IF NOT EXISTS articles_fts_insert
            AFTER INSERT ON articles
            BEGIN
                INSERT INTO articles_fts(rowid, title, content)
                VALUES (new.id, new.title, new.content);
            END;
        """)

        // ✅ Auto-sync on UPDATE
        db.execSQL("""
            CREATE TRIGGER IF NOT EXISTS articles_fts_update
            AFTER UPDATE ON articles
            BEGIN
                UPDATE articles_fts
                SET title = new.title,
                    content = new.content
                WHERE rowid = new.id;
            END;
        """)

        // ✅ Auto-sync on DELETE
        db.execSQL("""
            CREATE TRIGGER IF NOT EXISTS articles_fts_delete
            AFTER DELETE ON articles
            BEGIN
                DELETE FROM articles_fts WHERE rowid = old.id;
            END;
        """)
    }
}
```

Note: For production, align your triggers and FTS table definition (external content vs contentless) strictly with the SQLite FTS documentation; auxiliary `INSERT/UPDATE/DELETE` commands for FTS may be required depending on configuration.

### Search with BM25 Ranking (FTS5)

```kotlin
data class ArticleSearchResult(
    @Embedded val article: Article,
    val rank: Double  // ✅ bm25 score (lower = more relevant)
)

@Dao
interface ArticleDao {
    // ✅ Basic search with ranking (FTS5)
    @Query("""
        SELECT articles.*, bm25(articles_fts) AS rank
        FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY rank
    """)
    fun search(query: String): Flow<List<ArticleSearchResult>>

    // ✅ Weighted ranking (title more important than content)
    @Query("""
        SELECT articles.*, bm25(articles_fts, 10.0, 1.0) AS rank
        FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY rank
        LIMIT :limit
    """)
    suspend fun searchWeighted(query: String, limit: Int): List<ArticleSearchResult>

    // ✅ Prefix search for autocomplete (FTS MATCH syntax)
    @Query("""
        SELECT articles.*
        FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query || '*'
        LIMIT 10
    """)
    suspend fun autocomplete(query: String): List<Article>
}
```

(Again, `bm25()` and advanced MATCH syntax assume FTS5 support.)

### Highlighting Results

```kotlin
data class ArticleWithHighlight(
    @Embedded val article: Article,
    val highlightedTitle: String,    // ✅ Highlighted title
    val snippet: String,             // ✅ Context snippet
    val rank: Double
)

@Dao
interface ArticleDaoHighlight {
    @Query("""
        SELECT articles.*,
               highlight(articles_fts, 0, '<b>', '</b>') AS highlightedTitle,
               snippet(articles_fts, 1, '<mark>', '</mark>', '...', 30) AS snippet,
               bm25(articles_fts) AS rank
        FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY rank
        LIMIT :limit
    """)
    suspend fun searchWithHighlight(query: String, limit: Int): List<ArticleWithHighlight>
}
```

### Repository with Debouncing

```kotlin
class ArticleRepository(private val dao: ArticleDao) {

    // ✅ Debouncing for better UX (illustrative)
    fun search(queryFlow: Flow<String>): Flow<List<ArticleSearchResult>> {
        return queryFlow
            .debounce(300)
            .map { it.trim() }
            .filter { it.length >= 2 }
            .distinctUntilChanged()
            .flatMapLatest { query ->
                dao.search(simpleSanitize(query))
            }
    }

    // Simple demo sanitization.
    // Real-world code should robustly escape/handle FTS operators.
    private fun simpleSanitize(query: String): String {
        return query
            .replace("\"", "")
            .split("\\s+".toRegex())
            .filter { it.isNotEmpty() }
            .joinToString(" AND ")
    }
}
```

### Tokenizers

```kotlin
// ✅ Unicode61 (default for FTS5) — supports most languages reasonably well
@Fts5(tokenizer = FtsOptions.TOKENIZER_UNICODE61)
@Entity(tableName = "articles_fts_unicode")
data class ArticleFtsUnicode(
    val title: String,
    val content: String
)

// ✅ Porter — English stemming ("running" → "run")
@Fts5(tokenizer = FtsOptions.TOKENIZER_PORTER)
@Entity(tableName = "articles_fts_porter")
data class ArticleFtsPorter(
    val title: String,
    val content: String
)

// ⚠️ Simple — byte-based, not Unicode-aware; usually unsuitable for multilingual text
@Fts5(tokenizer = FtsOptions.TOKENIZER_SIMPLE)
@Entity(tableName = "articles_fts_simple")
data class ArticleFtsSimple(
    val title: String,
    val content: String
)
```

Actual tokenizer availability/parameters depend on your SQLite/Room build.

### Best Practices

1. ✅ Prefer **FTS5 for new projects** (if supported by your Room/SQLite) for better ranking and features.
2. ✅ Consider **external content (`contentEntity`)** to avoid unnecessary duplication, but contentless setups are valid where they simplify maintenance or offer better control.
3. ✅ Ensure **automatic synchronization** between base and FTS tables (via triggers or tightly controlled DAO operations).
4. ✅ **Index only real searchable text fields** to reduce index size and improve performance.
5. ✅ Use **debouncing/throttling** in the UI to limit query frequency.
6. ✅ Use **bm25 ranking** (FTS5) when relevance matters.
7. ✅ **Handle user input safely** for MATCH (escape/normalize special characters and operators).
8. ⚠️ Use **Paging** for large result sets.
9. ⚠️ Ensure **atomicity** of writes affecting both main and FTS tables.
10. ⚠️ **Choose between external content and duplication consciously**; "never duplicate" is incorrect as a blanket rule.

### Common Mistakes

```kotlin
// ❌ Manual sync without a clear invariant — leads to divergence
@Transaction
suspend fun insert(article: Article) {
    val id = insertArticle(article)
    // Easy to forget updates/deletes or handle failures incorrectly
    insertFts(ArticleFts(title = article.title, content = article.content))
}

// ✅ Prefer triggers or a single well-defined insertion path that updates both.

// ❌ Passing raw user input to MATCH
// dao.search(userInput)

// ✅ Normalize/escape input before MATCH
// dao.search(simpleSanitize(userInput))

// ❌ Indexing every field in FTS
@Fts5(contentEntity = Article::class)
data class ArticleFtsTooWide(
    val title: String,
    val content: String,
    val metadata: String,
    val timestamp: Long
)

// ✅ Keep FTS schema minimal
@Fts5(contentEntity = Article::class)
data class ArticleFtsNarrow(
    val title: String,
    val content: String
)
```

---

## Follow-ups

1. How does FTS5 handle multi-language content (e.g., English and Russian text in the same document), and how would you choose tokenizers for that?
2. What are the storage overhead and migration implications of introducing FTS tables into an existing Room schema?
3. How can you implement fuzzy search or typo tolerance on top of FTS (e.g., with auxiliary tables or client-side ranking)?
4. How would you design FTS synchronization and recovery logic after a partial data loss or corruption of the FTS index?
5. How can you benchmark and profile FTS vs LIKE for your specific workload on Android devices?

## References

- [[c-android-basics]]
- [[c-database-performance]]
- [Room FTS Documentation](https://developer.android.com/training/data-storage/room/defining-data#fts)
- [SQLite FTS5 Extension](https://www.sqlite.org/fts5.html)
- [Room Performance Best Practices](https://developer.android.com/topic/performance/sqlite-performance-best-practices)

## Related Questions

- [[q-android-storage-types--android--medium]]
