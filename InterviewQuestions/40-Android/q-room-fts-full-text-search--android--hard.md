---
id: android-427
title: "Room Full-Text Search (FTS) / Полнотекстовый поиск FTS в Room"
aliases: ["Room Full-Text Search", "Полнотекстовый поиск FTS в Room"]
topic: android
subtopics: [performance-rendering, room]
question_kind: android
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-room-database, q-room-basics-dao-entity--android--easy, q-room-relationships-embedded--android--medium]
created: 2025-10-15
updated: 2025-10-28
sources: []
tags: [android/performance-rendering, android/room, database, difficulty/hard, fts, performance, search]
---

# Вопрос (RU)

Реализуйте полнотекстовый поиск в Room с использованием FTS4/FTS5. Оптимизируйте производительность поиска для больших наборов данных. Когда использовать FTS вместо LIKE? Как синхронизировать FTS таблицы с основными таблицами?

# Question (EN)

Implement full-text search in Room using FTS4/FTS5. Optimize search performance for large datasets. When to use FTS instead of LIKE? How to synchronize FTS tables with main tables?

---

## Ответ (RU)

**Полнотекстовый поиск (FTS)** в Room обеспечивает эффективный текстовый поиск через расширения FTS SQLite. FTS в 10-100 раз быстрее LIKE запросов на больших данных и поддерживает ранжирование, префиксный поиск и булевы операторы.

### Когда Использовать FTS

| Сценарий | LIKE | FTS5 |
|----------|------|------|
| < 1000 записей | ✅ Достаточно | ⚠️ Избыточно |
| > 10000 записей | ❌ Медленно | ✅ Быстро |
| Простой поиск | ✅ Проще | ⚠️ Сложнее |
| Ранжирование | ❌ Нет | ✅ BM25 |
| Префиксы | ❌ Только `%` | ✅ Оптимизированно |

**Ключевые преимущества FTS5**:
- Производительность: 10-100x быстрее LIKE
- BM25 ранжирование по релевантности
- Функции highlight() и snippet()
- Булевы операторы (AND, OR, NOT)

### Базовая Реализация FTS5

```kotlin
// ✅ Основная сущность
@Entity(tableName = "articles")
data class Article(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val title: String,
    val content: String
)

// ✅ FTS сущность с внешним содержимым (избегает дублирования)
@Fts4(contentEntity = Article::class) // Room использует @Fts4 для FTS5
@Entity(tableName = "articles_fts")
data class ArticleFts(
    @PrimaryKey @ColumnInfo(name = "rowid")
    val rowid: Long,
    val title: String,    // Индексируется
    val content: String   // Индексируется
)
```

### Синхронизация Через Триггеры

```kotlin
@Database(entities = [Article::class, ArticleFts::class], version = 1)
abstract class AppDatabase : RoomDatabase() {

    override fun onCreate(db: SupportSQLiteDatabase) {
        super.onCreate(db)

        // ✅ Автоматическая синхронизация при INSERT
        db.execSQL("""
            CREATE TRIGGER articles_fts_insert AFTER INSERT ON articles
            BEGIN
                INSERT INTO articles_fts (rowid, title, content)
                VALUES (new.id, new.title, new.content);
            END
        """)

        // ✅ Автоматическая синхронизация при UPDATE
        db.execSQL("""
            CREATE TRIGGER articles_fts_update AFTER UPDATE ON articles
            BEGIN
                UPDATE articles_fts SET title = new.title, content = new.content
                WHERE rowid = new.id;
            END
        """)

        // ✅ Автоматическая синхронизация при DELETE
        db.execSQL("""
            CREATE TRIGGER articles_fts_delete AFTER DELETE ON articles
            BEGIN
                DELETE FROM articles_fts WHERE rowid = old.id;
            END
        """)
    }
}
```

### Поиск С Ранжированием BM25

```kotlin
data class ArticleSearchResult(
    @Embedded val article: Article,
    val rank: Double  // ✅ BM25 score (меньше = релевантнее)
)

@Dao
interface ArticleDao {
    // ✅ Базовый поиск с ранжированием
    @Query("""
        SELECT articles.*, bm25(articles_fts) as rank
        FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY rank
    """)
    fun search(query: String): Flow<List<ArticleSearchResult>>

    // ✅ Взвешенное ранжирование (title важнее content)
    @Query("""
        SELECT articles.*, bm25(articles_fts, 10.0, 1.0) as rank
        FROM articles INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY rank LIMIT :limit
    """)
    suspend fun searchWeighted(query: String, limit: Int): List<ArticleSearchResult>

    // ✅ Префиксный поиск для автодополнения
    @Query("""
        SELECT articles.* FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query || '*'
        LIMIT 10
    """)
    suspend fun autocomplete(query: String): List<Article>
}
```

### Подсветка Результатов

```kotlin
data class ArticleWithHighlight(
    @Embedded val article: Article,
    val highlightedTitle: String,    // ✅ Подсвеченный заголовок
    val snippet: String,              // ✅ Фрагмент с контекстом
    val rank: Double
)

@Dao
interface ArticleDao {
    @Query("""
        SELECT articles.*,
               highlight(articles_fts, 0, '<b>', '</b>') as highlightedTitle,
               snippet(articles_fts, 1, '<mark>', '</mark>', '...', 30) as snippet,
               bm25(articles_fts) as rank
        FROM articles INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY rank LIMIT :limit
    """)
    suspend fun searchWithHighlight(query: String, limit: Int): List<ArticleWithHighlight>
}
```

### `Repository` С Debouncing

```kotlin
class ArticleRepository(private val dao: ArticleDao) {

    // ✅ Debouncing для оптимизации UX
    fun search(queryFlow: Flow<String>): Flow<List<ArticleSearchResult>> {
        return queryFlow
            .debounce(300)  // Ждать 300мс после ввода
            .filter { it.length >= 2 }
            .distinctUntilChanged()
            .flatMapLatest { query ->
                dao.search(sanitize(query))
            }
    }

    // ✅ Санитизация для предотвращения ошибок FTS
    private fun sanitize(query: String): String {
        return query.trim()
            .replace("\"", "")   // Удалить кавычки
            .split("\\s+".toRegex())
            .filter { it.isNotEmpty() }
            .joinToString(" AND ")
    }
}
```

### Токенизаторы

```kotlin
// ✅ Unicode61 (по умолчанию) - поддержка большинства языков
@Fts4(tokenizer = FtsOptions.TOKENIZER_UNICODE61)
@Entity(tableName = "articles_fts")
data class ArticleFtsUnicode(...)

// ✅ Porter - английский stemming ("running" → "run")
@Fts4(tokenizer = FtsOptions.TOKENIZER_PORTER)
@Entity(tableName = "articles_fts_porter")
data class ArticleFtsPorter(...)

// ❌ Simple - только ASCII, не для интернациональных текстов
@Fts4(tokenizer = FtsOptions.TOKENIZER_SIMPLE)
@Entity(tableName = "articles_fts_simple")
data class ArticleFtsSimple(...)
```

### Best Practices

1. ✅ **FTS5 для новых проектов** - лучшая производительность и функции
2. ✅ **External content** - используйте `contentEntity` для избежания дублирования
3. ✅ **Триггеры** - автоматическая синхронизация FTS таблиц
4. ✅ **Индексируйте только searchable поля** - не индексируйте метаданные
5. ✅ **Debouncing** - не поиск на каждом нажатии клавиши
6. ✅ **BM25 ranking** - сортировка по релевантности
7. ✅ **Sanitize input** - предотвращение ошибок FTS
8. ⚠️ **Paging** - используйте для больших результатов
9. ⚠️ **@Transaction** - FTS sync должен быть атомарным
10. ❌ **Не дублируйте данные** - всегда используйте contentEntity

### Частые Ошибки

```kotlin
// ❌ WRONG - Ручная синхронизация (подвержена ошибкам)
@Transaction
suspend fun insert(article: Article) {
    val id = insertArticle(article)
    insertFts(ArticleFts(id, article.title, article.content))
}

// ✅ CORRECT - Автоматическая синхронизация через триггеры
// Просто insert в основную таблицу, триггер обновит FTS

// ❌ WRONG - Не санитизация query
dao.search(userInput)  // Может вызвать ошибку FTS

// ✅ CORRECT - Санитизация входных данных
dao.search(sanitize(userInput))

// ❌ WRONG - Индексация всех полей
@Fts4(contentEntity = Article::class)
data class ArticleFts(
    val id: Long,
    val title: String,
    val content: String,
    val metadata: String,  // Не нужно индексировать
    val timestamps: Long   // Не нужно индексировать
)

// ✅ CORRECT - Индексация только searchable полей
@Fts4(contentEntity = Article::class)
data class ArticleFts(
    val rowid: Long,
    val title: String,
    val content: String
)
```

---

## Answer (EN)

**Full-Text Search (FTS)** in Room provides efficient text search through SQLite's FTS extensions. FTS is 10-100x faster than LIKE queries on large datasets and supports ranking, prefix search, and boolean operators.

### When to Use FTS

| Scenario | LIKE | FTS5 |
|----------|------|------|
| < 1000 records | ✅ Sufficient | ⚠️ Overkill |
| > 10000 records | ❌ Slow | ✅ Fast |
| Simple search | ✅ Simpler | ⚠️ More complex |
| Ranking | ❌ No | ✅ BM25 |
| Prefix search | ❌ Only `%` | ✅ Optimized |

**Key FTS5 Benefits**:
- Performance: 10-100x faster than LIKE
- BM25 relevance ranking
- highlight() and snippet() functions
- `Boolean` operators (AND, OR, NOT)

### Basic FTS5 Implementation

```kotlin
// ✅ Main entity
@Entity(tableName = "articles")
data class Article(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val title: String,
    val content: String
)

// ✅ FTS entity with external content (avoids duplication)
@Fts4(contentEntity = Article::class) // Room uses @Fts4 for FTS5
@Entity(tableName = "articles_fts")
data class ArticleFts(
    @PrimaryKey @ColumnInfo(name = "rowid")
    val rowid: Long,
    val title: String,    // Indexed
    val content: String   // Indexed
)
```

### Synchronization via Triggers

```kotlin
@Database(entities = [Article::class, ArticleFts::class], version = 1)
abstract class AppDatabase : RoomDatabase() {

    override fun onCreate(db: SupportSQLiteDatabase) {
        super.onCreate(db)

        // ✅ Auto-sync on INSERT
        db.execSQL("""
            CREATE TRIGGER articles_fts_insert AFTER INSERT ON articles
            BEGIN
                INSERT INTO articles_fts (rowid, title, content)
                VALUES (new.id, new.title, new.content);
            END
        """)

        // ✅ Auto-sync on UPDATE
        db.execSQL("""
            CREATE TRIGGER articles_fts_update AFTER UPDATE ON articles
            BEGIN
                UPDATE articles_fts SET title = new.title, content = new.content
                WHERE rowid = new.id;
            END
        """)

        // ✅ Auto-sync on DELETE
        db.execSQL("""
            CREATE TRIGGER articles_fts_delete AFTER DELETE ON articles
            BEGIN
                DELETE FROM articles_fts WHERE rowid = old.id;
            END
        """)
    }
}
```

### Search with BM25 Ranking

```kotlin
data class ArticleSearchResult(
    @Embedded val article: Article,
    val rank: Double  // ✅ BM25 score (lower = more relevant)
)

@Dao
interface ArticleDao {
    // ✅ Basic search with ranking
    @Query("""
        SELECT articles.*, bm25(articles_fts) as rank
        FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY rank
    """)
    fun search(query: String): Flow<List<ArticleSearchResult>>

    // ✅ Weighted ranking (title more important than content)
    @Query("""
        SELECT articles.*, bm25(articles_fts, 10.0, 1.0) as rank
        FROM articles INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY rank LIMIT :limit
    """)
    suspend fun searchWeighted(query: String, limit: Int): List<ArticleSearchResult>

    // ✅ Prefix search for autocomplete
    @Query("""
        SELECT articles.* FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query || '*'
        LIMIT 10
    """)
    suspend fun autocomplete(query: String): List<Article>
}
```

### Highlighting Results

```kotlin
data class ArticleWithHighlight(
    @Embedded val article: Article,
    val highlightedTitle: String,    // ✅ Highlighted title
    val snippet: String,              // ✅ Snippet with context
    val rank: Double
)

@Dao
interface ArticleDao {
    @Query("""
        SELECT articles.*,
               highlight(articles_fts, 0, '<b>', '</b>') as highlightedTitle,
               snippet(articles_fts, 1, '<mark>', '</mark>', '...', 30) as snippet,
               bm25(articles_fts) as rank
        FROM articles INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY rank LIMIT :limit
    """)
    suspend fun searchWithHighlight(query: String, limit: Int): List<ArticleWithHighlight>
}
```

### `Repository` with Debouncing

```kotlin
class ArticleRepository(private val dao: ArticleDao) {

    // ✅ Debouncing for better UX
    fun search(queryFlow: Flow<String>): Flow<List<ArticleSearchResult>> {
        return queryFlow
            .debounce(300)  // Wait 300ms after typing
            .filter { it.length >= 2 }
            .distinctUntilChanged()
            .flatMapLatest { query ->
                dao.search(sanitize(query))
            }
    }

    // ✅ Sanitize to prevent FTS errors
    private fun sanitize(query: String): String {
        return query.trim()
            .replace("\"", "")   // Remove quotes
            .split("\\s+".toRegex())
            .filter { it.isNotEmpty() }
            .joinToString(" AND ")
    }
}
```

### Tokenizers

```kotlin
// ✅ Unicode61 (default) - supports most languages
@Fts4(tokenizer = FtsOptions.TOKENIZER_UNICODE61)
@Entity(tableName = "articles_fts")
data class ArticleFtsUnicode(...)

// ✅ Porter - English stemming ("running" → "run")
@Fts4(tokenizer = FtsOptions.TOKENIZER_PORTER)
@Entity(tableName = "articles_fts_porter")
data class ArticleFtsPorter(...)

// ❌ Simple - ASCII only, not for international text
@Fts4(tokenizer = FtsOptions.TOKENIZER_SIMPLE)
@Entity(tableName = "articles_fts_simple")
data class ArticleFtsSimple(...)
```

### Best Practices

1. ✅ **FTS5 for new projects** - better performance and features
2. ✅ **External content** - use `contentEntity` to avoid duplication
3. ✅ **Triggers** - automatic FTS table synchronization
4. ✅ **Index only searchable fields** - don't index metadata
5. ✅ **Debouncing** - don't search on every keystroke
6. ✅ **BM25 ranking** - sort by relevance
7. ✅ **Sanitize input** - prevent FTS errors
8. ⚠️ **Paging** - use for large result sets
9. ⚠️ **@Transaction** - FTS sync must be atomic
10. ❌ **Don't duplicate data** - always use contentEntity

### Common Mistakes

```kotlin
// ❌ WRONG - Manual synchronization (error-prone)
@Transaction
suspend fun insert(article: Article) {
    val id = insertArticle(article)
    insertFts(ArticleFts(id, article.title, article.content))
}

// ✅ CORRECT - Automatic sync via triggers
// Just insert to main table, trigger updates FTS

// ❌ WRONG - No query sanitization
dao.search(userInput)  // Can cause FTS error

// ✅ CORRECT - Sanitize user input
dao.search(sanitize(userInput))

// ❌ WRONG - Index all fields
@Fts4(contentEntity = Article::class)
data class ArticleFts(
    val id: Long,
    val title: String,
    val content: String,
    val metadata: String,  // Don't index
    val timestamps: Long   // Don't index
)

// ✅ CORRECT - Index only searchable fields
@Fts4(contentEntity = Article::class)
data class ArticleFts(
    val rowid: Long,
    val title: String,
    val content: String
)
```

---

## Follow-ups

1. How does FTS5 handle multi-language content (e.g., English + Russian in same document)?
2. What are the storage overhead implications of FTS tables for large datasets?
3. How to implement fuzzy search or typo tolerance with FTS?
4. Can FTS5 be used with Room's multi-process access?
5. How to optimize FTS rebuild performance for large existing databases?

## References

**Concept Notes**:
- [[c-room-database]] - Room database fundamentals
- [[c-sqlite-indexes]] - SQLite indexing strategies
- [[c-bm25-ranking]] - BM25 relevance ranking algorithm

**Official Documentation**:
- [Room FTS Documentation](https://developer.android.com/training/data-storage/room/defining-data#fts)
- [SQLite FTS5 Extension](https://www.sqlite.org/fts5.html)
- [Room Performance Best Practices](https://developer.android.com/topic/performance/sqlite-performance-best-practices)

## Related Questions

### Prerequisites (Easier)
- [[q-room-basics-dao-entity--android--easy]] - Room fundamentals
- [[q-room-relations-embedded--android--medium]] - Room relationships

### Related (Same Level)
- [[q-room-transactions-dao--android--medium]] - Transaction handling
- [[q-room-paging3-integration--android--medium]] - Pagination integration
- [[q-sqlite-query-optimization--android--hard]] - Query optimization

### Advanced (Harder)
- [[q-room-custom-type-converters--android--hard]] - Advanced type converters
- [[q-multi-module-room-database--android--hard]] - Multi-module Room architecture
