---\
id: android-427
anki_cards:
  - slug: android-427-0-en
    front: "When should you use FTS instead of LIKE in Room?"
    back: |
      **Use FTS (Full-Text Search) when:**
      - Large tables (10K+ rows) - FTS is much faster
      - Need relevance ranking (bm25 in FTS5)
      - Prefix search or boolean operators required

      **Use LIKE when:**
      - Small tables (hundreds of rows)
      - Simple single-field search

      **FTS5 features:**
      - `bm25()` for relevance ranking
      - `highlight()` and `snippet()` for UI
      - Prefix search with `query*`

      ```kotlin
      @Fts5(contentEntity = Article::class)
      @Entity(tableName = "articles_fts")
      data class ArticleFts(val title: String, val content: String)
      ```
    tags:
      - android_room
      - difficulty::hard
  - slug: android-427-0-ru
    front: "Когда использовать FTS вместо LIKE в Room?"
    back: |
      **Используйте FTS (полнотекстовый поиск) когда:**
      - Большие таблицы (10K+ записей) - FTS значительно быстрее
      - Нужно ранжирование по релевантности (bm25 в FTS5)
      - Требуется префиксный поиск или булевы операторы

      **Используйте LIKE когда:**
      - Маленькие таблицы (сотни записей)
      - Простой поиск по одному полю

      **Возможности FTS5:**
      - `bm25()` для ранжирования
      - `highlight()` и `snippet()` для UI
      - Префиксный поиск через `query*`

      ```kotlin
      @Fts5(contentEntity = Article::class)
      @Entity(tableName = "articles_fts")
      data class ArticleFts(val title: String, val content: String)
      ```
    tags:
      - android_room
      - difficulty::hard
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

---\
# Вопрос (RU)

> Реализуйте полнотекстовый поиск в `Room` с использованием FTS4/FTS5. Оптимизируйте производительность поиска для больших наборов данных. Когда использовать FTS вместо LIKE? Как синхронизировать FTS таблицы с основными таблицами?

# Question (EN)

> Implement full-text search in `Room` using FTS4/FTS5. Optimize search performance for large datasets. When to use FTS instead of LIKE? How to synchronize FTS tables with main tables?

---

## Ответ (RU)

**Полнотекстовый поиск (FTS)** в `Room` обеспечивает эффективный текстовый поиск через расширения FTS `SQLite`. На больших наборах данных FTS обычно значительно быстрее, чем LIKE-запросы по неиндексированному тексту или LIKE c ведущим `%`, и поддерживает ранжирование (FTS5), префиксный поиск и булевы операторы.

### Когда Использовать FTS

| Сценарий | LIKE | FTS4/FTS5 |
|----------|------|-----------|
| Малые таблицы (порядка сотен записей) | ✅ Часто достаточно | ⚠️ Может быть избыточно |
| Крупные таблицы (десятки/сотни тысяч записей) | ❌ Часто медленно (особенно с ведущим `%`) | ✅ Обычно быстрее и масштабируемее |
| Простой поиск по одному полю | ✅ Проще | ⚠️ Сложнее в настройке |
| Ранжирование по релевантности | ❌ Нет | ✅ Через `bm25()` (FTS5) |
| Продвинутый / префиксный поиск | ❌ Ограничен шаблонами `%` | ✅ Специализированные операторы и индексация |

(Оценки типа «10–100x быстрее» стоит рассматривать как типичную оценку для полнотекстовых задач, а не жёсткую гарантию: всё зависит от данных и запросов.)

**Ключевые возможности FTS (особенно FTS5)**:
- Повышенная производительность полнотекстового поиска по сравнению с последовательным LIKE-поиском
- Ранжирование по релевантности через `bm25()` (FTS5)
- Функции `highlight()` и `snippet()`
- Булевы операторы (AND, OR, NOT) и префиксный поиск в MATCH-выражениях

### Базовая Реализация (пример С FTS5)

Пример ниже показывает FTS-таблицу с внешним содержимым (external content) для FTS5, управляемую `Room` через `contentEntity`.

```kotlin
// ✅ Основная сущность
@Entity(tableName = "articles")
data class Article(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val title: String,
    val content: String
)

// ✅ FTS5 сущность с external content (избегает дублирования хранений текста)
// Room с @Fts5(contentEntity = ...) создаёт виртуальную таблицу вида:
// CREATE VIRTUAL TABLE articles_fts USING fts5(title, content, content='articles', content_rowid='id');
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

Важно различать два режима:
- external content (`contentEntity` / `content='articles'` + `content_rowid='id'`)
- contentless / standalone FTS-таблица с явным дублированием данных

Для них механика синхронизации различается.

1. External content через `contentEntity` (рекомендуемый способ в `Room`)

- `Room` генерирует FTS-таблицу, привязанную к `articles` по `id`.
- Для корректной синхронизации в `SQLite` требуются специальные FTS-команды (`INSERT`, `DELETE`, `UPDATE`) в FTS-таблицу, а не обычные UPDATE/DELETE строк:
  - `INSERT INTO articles_fts(articles_fts, rowid, title, content) VALUES('insert', new.id, new.title, new.content);`
  - `INSERT INTO articles_fts(articles_fts, 'delete', old.id, old.title, old.content);`
  - `INSERT INTO articles_fts(articles_fts, 'delete', old.id, old.title, old.content);` + `INSERT INTO articles_fts(articles_fts, 'insert', new.id, new.title, new.content);` для UPDATE.
- `Room` может управлять этим автоматически в зависимости от конфигурации; если вы создаёте триггеры вручную, их нужно писать в соответствии с документацией `SQLite` FTS, а не делать обычные `UPDATE articles_fts ...`.

1. Contentless или дублирующая FTS-таблица

- Вы храните данные как в основной таблице, так и в FTS-таблице.
- В этом случае вы можете реализовать триггеры, которые используют FTS-специфические команды (например, через управляющий столбец) или инкапсулировать операции в DAO так, чтобы все изменения проходили через один путь и обновляли обе таблицы атомарно.

Ниже — упрощённый пример триггеров для external content FTS5 (демо-идея, проверяйте точный синтаксис под свою схему и версию `SQLite`):

```kotlin
@Database(entities = [Article::class, ArticleFts::class], version = 1)
abstract class AppDatabase : RoomDatabase() {

    override fun onCreate(db: SupportSQLiteDatabase) {
        super.onCreate(db)

        // ✅ INSERT: синхронизация через спец. команду FTS5
        db.execSQL(
            """
            CREATE TRIGGER IF NOT EXISTS articles_ai AFTER INSERT ON articles BEGIN
                INSERT INTO articles_fts(articles_fts, rowid, title, content)
                VALUES('insert', new.id, new.title, new.content);
            END;
            """
        )

        // ✅ DELETE
        db.execSQL(
            """
            CREATE TRIGGER IF NOT EXISTS articles_ad AFTER DELETE ON articles BEGIN
                INSERT INTO articles_fts(articles_fts, 'delete', old.id, old.title, old.content);
            END;
            """
        )

        // ✅ UPDATE
        db.execSQL(
            """
            CREATE TRIGGER IF NOT EXISTS articles_au AFTER UPDATE ON articles BEGIN
                INSERT INTO articles_fts(articles_fts, 'delete', old.id, old.title, old.content);
                INSERT INTO articles_fts(articles_fts, 'insert', new.id, new.title, new.content);
            END;
            """
        )
    }
}
```

Важно: точная схема триггеров и использование управляющего столбца (значения `'insert'`, `'delete'`) зависит от варианта FTS и режима (external content/contentless). Для production-решения нужно строго следовать документации `SQLite` FTS и актуальной документации `Room`; не используйте обычные `UPDATE`/`DELETE` над строками FTS-таблицы для external content.

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
3. ✅ **Настройте автоматическую синхронизацию корректно**: для external content — через FTS-специфичные команды и триггеры; для дублирующей схемы — через триггеры или строго инкапсулированные DAO-операции.
4. ✅ **Индексируйте только действительно searchable-поля**, чтобы уменьшить размер индекса и ускорить поиск.
5. ✅ **Используйте debouncing и/или throttling** в UI, чтобы не спамить базу запросами на каждый символ.
6. ✅ **Используйте ранжирование (`bm25`)** там, где важна релевантность (FTS5).
7. ✅ **Корректно обрабатывайте пользовательский ввод** (экранирование спецсимволов, резервированных слов, операторов) вместо слепого подставления в MATCH.
8. ⚠️ **Используйте Paging** для больших результатов, чтобы не загружать всю выборку в память.
9. ⚠️ **Соблюдайте атомарность операций** (например, через `@Transaction` или триггеры), чтобы данные и FTS-индекс не расходились.
10. ⚠️ **Осознанно выбирайте между external content и дублированием данных** — выбор зависит от требований к размеру, скорости и простоте.

### Частые Ошибки

```kotlin
// ❌ Ручная синхронизация без триггеров или единой точки записи (подвержена расхождениям)
@Transaction
suspend fun insert(article: Article) {
    val id = insertArticle(article)
    // Легко забыть обновить FTS при обновлении/удалении
    insertFts(ArticleFts(title = article.title, content = article.content))
}

// ✅ Предпочтительно: корректные FTS-триггеры для external content
// или строго инкапсулированные DAO-операции с обновлением обеих таблиц.

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

**Full-Text Search (FTS)** in `Room` provides efficient text search via `SQLite` FTS extensions. On large datasets, FTS is typically much faster than naive LIKE scans (especially with leading `%`) over unindexed text, and supports (with FTS5) relevance ranking, prefix search, and boolean operators.

### When to Use FTS

| Scenario | LIKE | FTS4/FTS5 |
|----------|------|-----------|
| Small tables (hundreds of rows) | ✅ Often sufficient | ⚠️ May be overkill |
| Large tables (tens/hundreds of thousands of rows) | ❌ Often slow (especially with leading `%`) | ✅ Usually faster and more scalable |
| Simple search on one column | ✅ Simpler | ⚠️ More setup |
| Relevance ranking | ❌ Not built-in | ✅ `bm25()` (FTS5) |
| Advanced/prefix search | ❌ Limited to `%` patterns | ✅ Dedicated MATCH syntax/indexing |

(Values like "10–100x faster" should be treated as typical for full-text workloads, not a strict guarantee; actual gains depend on schema, data, and queries.)

**Key FTS (esp. FTS5) features**:
- Better performance for full-text queries vs. sequential LIKE scans
- Relevance ranking via `bm25()` (FTS5)
- `highlight()` and `snippet()` helper functions
- `Boolean` operators and prefix queries in MATCH expressions

### Basic Implementation (FTS5 Example)

The following shows an FTS5 table with external content managed by `Room` via `contentEntity`.

```kotlin
// ✅ Main entity
@Entity(tableName = "articles")
data class Article(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val title: String,
    val content: String
)

// ✅ FTS5 entity with external content (avoids duplicated text storage)
// Room with @Fts5(contentEntity = ...) generates something like:
// CREATE VIRTUAL TABLE articles_fts USING fts5(title, content, content='articles', content_rowid='id');
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

Two conceptual modes matter here:
- external content (`content='articles'` + `content_rowid='id'`, configured via `contentEntity`)
- contentless/duplicated FTS table where you insert searchable text directly

They require different sync strategies.

1. External content via `contentEntity` (preferred with `Room`)

- `Room` creates the FTS table bound to `articles` by `id`.
- In `SQLite` FTS, keeping such a table in sync requires special maintenance statements that target the FTS table:
  - `INSERT INTO articles_fts(articles_fts, rowid, title, content) VALUES('insert', new.id, new.title, new.content);`
  - `INSERT INTO articles_fts(articles_fts, 'delete', old.id, old.title, old.content);`
  - For UPDATE: a `'delete'` for `old.*` followed by an `'insert'` for `new.*`.
- If you define triggers manually, they must use these FTS-specific forms; doing `UPDATE articles_fts SET ... WHERE rowid = new.id;` or plain `DELETE FROM articles_fts WHERE rowid = old.id;` is not the correct pattern for external content FTS maintenance.

1. Contentless / duplicated FTS table

- You store search text both in the base table and in the FTS table.
- You can:
  - Use triggers that insert into/delete from the FTS table using the appropriate FTS commands; or
  - Ensure all writes go through DAO methods that update both tables atomically.

Below is a simplified trigger example for an external-content-style FTS5 setup (illustrative only; adjust to your schema and SQLite/Room version):

```kotlin
@Database(entities = [Article::class, ArticleFts::class], version = 1)
abstract class AppDatabase : RoomDatabase() {

    override fun onCreate(db: SupportSQLiteDatabase) {
        super.onCreate(db)

        // ✅ INSERT sync
        db.execSQL(
            """
            CREATE TRIGGER IF NOT EXISTS articles_ai AFTER INSERT ON articles BEGIN
                INSERT INTO articles_fts(articles_fts, rowid, title, content)
                VALUES('insert', new.id, new.title, new.content);
            END;
            """
        )

        // ✅ DELETE sync
        db.execSQL(
            """
            CREATE TRIGGER IF NOT EXISTS articles_ad AFTER DELETE ON articles BEGIN
                INSERT INTO articles_fts(articles_fts, 'delete', old.id, old.title, old.content);
            END;
            """
        )

        // ✅ UPDATE sync
        db.execSQL(
            """
            CREATE TRIGGER IF NOT EXISTS articles_au AFTER UPDATE ON articles BEGIN
                INSERT INTO articles_fts(articles_fts, 'delete', old.id, old.title, old.content);
                INSERT INTO articles_fts(articles_fts, 'insert', new.id, new.title, new.content);
            END;
            """
        )
    }
}
```

Note: For production, verify trigger syntax against the official `SQLite` FTS4/FTS5 documentation and the `Room` version you target. The key point is: do not treat FTS external-content tables like normal tables with arbitrary `UPDATE`/`DELETE` statements.

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
3. ✅ Ensure **synchronization is implemented with correct FTS maintenance commands**: for external content, do not rely on plain UPDATE/DELETE on the FTS table; for duplicated setups, keep all writes atomic and consistent.
4. ✅ **Index only real searchable text fields** to reduce index size and improve performance.
5. ✅ Use **debouncing/throttling** in the UI to limit query frequency.
6. ✅ Use **bm25 ranking** (FTS5) when relevance matters.
7. ✅ **Handle user input safely** for MATCH (escape/normalize special characters and operators).
8. ⚠️ Use **Paging** for large result sets.
9. ⚠️ Ensure **atomicity** of writes affecting both main and FTS tables.
10. ⚠️ **Choose between external content and duplication consciously**; "never duplicate" is not a universal rule.

### Common Mistakes

```kotlin
// ❌ Manual sync without a clear invariant — leads to divergence
@Transaction
suspend fun insert(article: Article) {
    val id = insertArticle(article)
    // Easy to forget updates/deletes or handle failures incorrectly
    insertFts(ArticleFts(title = article.title, content = article.content))
}

// ✅ Prefer proper FTS triggers for external content
// or a single well-defined insertion path updating both.

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

## Дополнительные Вопросы (RU)

1. Как FTS5 обрабатывает многоязычный контент (например, английский и русский текст в одном документе), и как выбирать подходящие токенизаторы?
2. Каковы накладные расходы по хранилищу и последствия для миграций при добавлении FTS-таблиц в существующую схему `Room`?
3. Как можно реализовать нечёткий поиск или устойчивость к опечаткам поверх FTS (например, с вспомогательными таблицами или клиентским ранжированием)?
4. Как спроектировать синхронизацию и логику восстановления FTS после частичной потери данных или повреждения FTS-индекса?
5. Как бенчмаркать и профилировать FTS против LIKE для вашего конкретного сценария на Android-устройствах?

## Ссылки (RU)

- [[c-android-basics]]
- [[c-database-performance]]
- `Room` FTS документация: https://developer.android.com/training/data-storage/room/defining-data#fts
- `SQLite` FTS5 Extension: https://www.sqlite.org/fts5.html
- Рекомендации по производительности `Room`: https://developer.android.com/topic/performance/sqlite-performance-best-practices

## Связанные Вопросы (RU)

- [[q-android-storage-types--android--medium]]

---

## Follow-ups

1. How does FTS5 handle multi-language content (e.g., English and Russian text in the same document), and how would you choose tokenizers for that?
2. What are the storage overhead and migration implications of introducing FTS tables into an existing `Room` schema?
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
