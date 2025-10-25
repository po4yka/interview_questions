---
id: 20251016-164554
title: "Room Fts Full Text Search / Полнотекстовый поиск FTS в Room"
topic: room
difficulty: hard
status: draft
moc: moc-android
related: [q-what-navigation-methods-exist-in-kotlin--programming-languages--medium, q-how-jetpack-compose-works--programming-languages--medium, q-espresso-advanced-patterns--testing--medium]
created: 2025-10-15
tags: [database, fts, search, performance, optimization, difficulty/hard]
---

# Room Full-Text Search (FTS) / Полнотекстовый поиск в Room

**English**: Implement full-text search in Room using FTS4/FTS5. Optimize search performance for large datasets.

## Answer (EN)
**Full-Text Search (FTS)** in Room provides efficient text searching capabilities through SQLite's FTS extensions (FTS3, FTS4, and FTS5). FTS is essential for searching large text datasets with complex queries, supporting features like prefix matching, ranking, and highlighting.

### Why Use FTS?

Traditional `LIKE` queries become extremely slow with large datasets and don't support advanced text search features. FTS provides:

- **Performance**: 10-100x faster than LIKE queries on large datasets
- **Relevance Ranking**: Sort results by relevance score
- **Prefix Matching**: Search for partial words
- **Boolean Operators**: AND, OR, NOT queries
- **Phrase Queries**: Search for exact phrases
- **Tokenization**: Language-aware word splitting

### FTS4 vs FTS5

| Feature | FTS4 | FTS5 |
|---------|------|------|
| Performance | Good | Better (optimized) |
| Ranking | Basic | BM25 algorithm |
| Memory Usage | Higher | Lower |
| Auxiliary Functions | Limited | Rich (highlight, snippet) |
| Prefix Queries | Supported | Better optimized |
| Recommendation | Legacy | **Use for new projects** |

**Always use FTS5 for new projects** unless you need backward compatibility with very old Android versions.

### Basic FTS5 Implementation

#### Simple FTS Entity

```kotlin
// FTS entity for searching notes
@Fts4  // or @Fts5 for better performance
@Entity(tableName = "notes_fts")
data class NoteFts(
    @PrimaryKey
    @ColumnInfo(name = "rowid")
    val rowid: Long,
    val title: String,
    val content: String
)

// Regular entity for storing note data
@Entity(tableName = "notes")
data class Note(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val title: String,
    val content: String,
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis(),
    val categoryId: Long? = null
)
```

#### FTS DAO

```kotlin
@Dao
interface NoteDao {
    // Regular CRUD operations
    @Insert
    suspend fun insertNote(note: Note): Long

    @Update
    suspend fun updateNote(note: Note)

    @Delete
    suspend fun deleteNote(note: Note)

    @Query("SELECT * FROM notes WHERE id = :id")
    suspend fun getNoteById(id: Long): Note?

    @Query("SELECT * FROM notes ORDER BY updatedAt DESC")
    fun getAllNotesFlow(): Flow<List<Note>>

    // FTS operations
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertNoteFts(noteFts: NoteFts)

    @Query("DELETE FROM notes_fts WHERE rowid = :noteId")
    suspend fun deleteNoteFts(noteId: Long)

    // Basic FTS search using MATCH operator
    @Query("""
        SELECT notes.* FROM notes
        INNER JOIN notes_fts ON notes.id = notes_fts.rowid
        WHERE notes_fts MATCH :query
        ORDER BY notes.updatedAt DESC
    """)
    fun searchNotes(query: String): Flow<List<Note>>

    // Search with limit
    @Query("""
        SELECT notes.* FROM notes
        INNER JOIN notes_fts ON notes.id = notes_fts.rowid
        WHERE notes_fts MATCH :query
        ORDER BY notes.updatedAt DESC
        LIMIT :limit
    """)
    suspend fun searchNotesLimit(query: String, limit: Int): List<Note>
}
```

### Advanced FTS5 with Content Table

For production apps, use FTS5 with **external content table** to avoid data duplication.

#### Entities with External Content

```kotlin
// Main content entity
@Entity(tableName = "articles")
data class Article(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val title: String,
    val content: String,
    val author: String,
    val publishedAt: Long,
    val categoryId: Long,
    val tags: String,  // Comma-separated
    val viewCount: Int = 0,
    val isFavorite: Boolean = false
)

// FTS5 entity with external content
// The content parameter points to the main table
@Fts4(contentEntity = Article::class)
@Entity(tableName = "articles_fts")
data class ArticleFts(
    @PrimaryKey
    @ColumnInfo(name = "rowid")
    val rowid: Long,
    val title: String,
    val content: String,
    val author: String,
    val tags: String
)
```

#### Advanced FTS DAO

```kotlin
@Dao
interface ArticleDao {
    // Insert article and sync FTS
    @Transaction
    suspend fun insertArticleWithFts(article: Article) {
        val id = insertArticle(article)
        insertArticleFts(
            ArticleFts(
                rowid = id,
                title = article.title,
                content = article.content,
                author = article.author,
                tags = article.tags
            )
        )
    }

    // Update article and sync FTS
    @Transaction
    suspend fun updateArticleWithFts(article: Article) {
        updateArticle(article)
        deleteArticleFts(article.id)
        insertArticleFts(
            ArticleFts(
                rowid = article.id,
                title = article.title,
                content = article.content,
                author = article.author,
                tags = article.tags
            )
        )
    }

    // Delete article and sync FTS
    @Transaction
    suspend fun deleteArticleWithFts(article: Article) {
        deleteArticle(article)
        deleteArticleFts(article.id)
    }

    @Insert
    suspend fun insertArticle(article: Article): Long

    @Update
    suspend fun updateArticle(article: Article)

    @Delete
    suspend fun deleteArticle(article: Article)

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertArticleFts(articleFts: ArticleFts)

    @Query("DELETE FROM articles_fts WHERE rowid = :articleId")
    suspend fun deleteArticleFts(articleId: Long)

    // Basic search
    @Query("""
        SELECT articles.* FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY articles.publishedAt DESC
    """)
    fun searchArticles(query: String): Flow<List<Article>>

    // Search with specific field
    @Query("""
        SELECT articles.* FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts.title MATCH :query
        ORDER BY articles.publishedAt DESC
    """)
    fun searchArticlesByTitle(query: String): Flow<List<Article>>

    // Search with multiple fields using column filter
    @Query("""
        SELECT articles.* FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH 'title:' || :titleQuery || ' OR content:' || :contentQuery
        ORDER BY articles.publishedAt DESC
    """)
    fun searchArticlesByTitleOrContent(
        titleQuery: String,
        contentQuery: String
    ): Flow<List<Article>>

    // Prefix search (for autocomplete)
    @Query("""
        SELECT articles.* FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query || '*'
        ORDER BY articles.publishedAt DESC
        LIMIT 10
    """)
    suspend fun autocompleteSearch(query: String): List<Article>

    // Boolean search (AND, OR, NOT)
    @Query("""
        SELECT articles.* FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY articles.publishedAt DESC
    """)
    suspend fun booleanSearch(query: String): List<Article>
    // Usage: booleanSearch("kotlin AND coroutines")
    //        booleanSearch("java OR kotlin NOT javascript")

    // Phrase search
    @Query("""
        SELECT articles.* FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH '"' || :phrase || '"'
        ORDER BY articles.publishedAt DESC
    """)
    suspend fun phraseSearch(phrase: String): List<Article>
}
```

### FTS5 with BM25 Ranking

BM25 is a ranking algorithm that scores search results by relevance.

```kotlin
// Search result with relevance score
data class ArticleSearchResult(
    @Embedded
    val article: Article,
    val rank: Double  // BM25 relevance score
)

@Dao
interface ArticleSearchDao {
    // Search with BM25 ranking (lower score = more relevant)
    @Query("""
        SELECT articles.*, bm25(articles_fts) as rank
        FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY rank
    """)
    fun searchWithRanking(query: String): Flow<List<ArticleSearchResult>>

    // Weighted BM25 ranking (boost title matches)
    // Syntax: bm25(fts_table, weight_col1, weight_col2, ...)
    @Query("""
        SELECT articles.*, bm25(articles_fts, 10.0, 1.0, 5.0, 2.0) as rank
        FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY rank
        LIMIT :limit
    """)
    suspend fun searchWithWeightedRanking(
        query: String,
        limit: Int = 20
    ): List<ArticleSearchResult>
    // Weights: title=10.0, content=1.0, author=5.0, tags=2.0
}
```

### Highlighting Search Results

FTS5 provides functions to highlight matching terms in search results.

```kotlin
data class ArticleWithHighlight(
    @Embedded
    val article: Article,
    val highlightedTitle: String,
    val highlightedSnippet: String,
    val rank: Double
)

@Dao
interface ArticleHighlightDao {
    // Highlight matching terms with custom tags
    @Query("""
        SELECT
            articles.*,
            highlight(articles_fts, 0, '<b>', '</b>') as highlightedTitle,
            snippet(articles_fts, 1, '<mark>', '</mark>', '...', 30) as highlightedSnippet,
            bm25(articles_fts) as rank
        FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY rank
        LIMIT :limit
    """)
    suspend fun searchWithHighlight(
        query: String,
        limit: Int = 20
    ): List<ArticleWithHighlight>

    // highlight() syntax:
    // highlight(fts_table, column_index, start_tag, end_tag)
    // column_index: 0=title, 1=content, 2=author, 3=tags

    // snippet() syntax:
    // snippet(fts_table, column_index, start_tag, end_tag, ellipsis, max_tokens)
}
```

### Custom Tokenizers

FTS supports different tokenizers for language-specific text processing.

```kotlin
// Unicode61 tokenizer (default, supports most languages)
@Fts4(tokenizer = FtsOptions.TOKENIZER_UNICODE61)
@Entity(tableName = "articles_fts")
data class ArticleFtsUnicode(
    val title: String,
    val content: String
)

// Porter tokenizer (English stemming)
// "running" matches "run", "runner", "runs"
@Fts4(tokenizer = FtsOptions.TOKENIZER_PORTER)
@Entity(tableName = "articles_fts_porter")
data class ArticleFtsPorter(
    val title: String,
    val content: String
)

// Simple tokenizer (ASCII only, faster)
@Fts4(tokenizer = FtsOptions.TOKENIZER_SIMPLE)
@Entity(tableName = "articles_fts_simple")
data class ArticleFtsSimple(
    val title: String,
    val content: String
)

// ICU tokenizer (best for international text)
// Requires ICU library
@Fts4(tokenizer = "icu")
@Entity(tableName = "articles_fts_icu")
data class ArticleFtsIcu(
    val title: String,
    val content: String
)
```

### Performance Optimization

#### 1. Use Triggers for Automatic FTS Sync

Instead of manually syncing FTS tables, use SQLite triggers:

```kotlin
@Database(
    entities = [Article::class, ArticleFts::class],
    version = 1
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun articleDao(): ArticleDao

    override fun onCreate(db: SupportSQLiteDatabase) {
        super.onCreate(db)

        // Trigger to sync INSERT
        db.execSQL("""
            CREATE TRIGGER articles_fts_insert AFTER INSERT ON articles
            BEGIN
                INSERT INTO articles_fts (rowid, title, content, author, tags)
                VALUES (new.id, new.title, new.content, new.author, new.tags);
            END
        """)

        // Trigger to sync UPDATE
        db.execSQL("""
            CREATE TRIGGER articles_fts_update AFTER UPDATE ON articles
            BEGIN
                UPDATE articles_fts
                SET title = new.title,
                    content = new.content,
                    author = new.author,
                    tags = new.tags
                WHERE rowid = new.id;
            END
        """)

        // Trigger to sync DELETE
        db.execSQL("""
            CREATE TRIGGER articles_fts_delete AFTER DELETE ON articles
            BEGIN
                DELETE FROM articles_fts WHERE rowid = old.id;
            END
        """)
    }
}
```

#### 2. Optimize FTS Table Size

```kotlin
// Only index searchable fields, exclude metadata
@Fts4(contentEntity = Article::class)
@Entity(tableName = "articles_fts")
data class ArticleFtsOptimized(
    @PrimaryKey
    @ColumnInfo(name = "rowid")
    val rowid: Long,
    val title: String,      // Index
    val content: String,    // Index
    // Exclude: publishedAt, categoryId, viewCount, isFavorite
)
```

#### 3. Pagination for Large Result Sets

```kotlin
@Dao
interface ArticleDao {
    // Use LIMIT and OFFSET for pagination
    @Query("""
        SELECT articles.*, bm25(articles_fts) as rank
        FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY rank
        LIMIT :limit OFFSET :offset
    """)
    suspend fun searchArticlesPaged(
        query: String,
        limit: Int,
        offset: Int
    ): List<ArticleSearchResult>

    // Or use Paging 3
    @Query("""
        SELECT articles.* FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY bm25(articles_fts)
    """)
    fun searchArticlesPaging(query: String): PagingSource<Int, Article>
}
```

### Performance Comparison

Let's compare FTS5 vs LIKE queries on different dataset sizes:

```kotlin
class SearchBenchmark {
    suspend fun benchmarkSearch(query: String, dataset: List<Article>) {
        val dao = database.articleDao()

        // Populate test data
        dataset.forEach { dao.insertArticleWithFts(it) }

        // Benchmark LIKE query
        val likeStart = System.currentTimeMillis()
        val likeResults = dao.searchWithLike("%$query%")
        val likeTime = System.currentTimeMillis() - likeStart

        // Benchmark FTS5 query
        val ftsStart = System.currentTimeMillis()
        val ftsResults = dao.searchArticles(query).first()
        val ftsTime = System.currentTimeMillis() - ftsStart

        println("""
            Dataset size: ${dataset.size}
            Query: "$query"

            LIKE query:
              Time: ${likeTime}ms
              Results: ${likeResults.size}

            FTS5 query:
              Time: ${ftsTime}ms
              Results: ${ftsResults.size}
              Speedup: ${likeTime.toFloat() / ftsTime}x
        """.trimIndent())
    }
}

// Expected results:
// 1,000 articles:   FTS5 ~2-5x faster
// 10,000 articles:  FTS5 ~10-20x faster
// 100,000 articles: FTS5 ~50-100x faster
```

#### Sample DAO for Comparison

```kotlin
@Dao
interface ArticleDao {
    // Traditional LIKE search (slow on large datasets)
    @Query("""
        SELECT * FROM articles
        WHERE title LIKE :query OR content LIKE :query
        ORDER BY publishedAt DESC
    """)
    suspend fun searchWithLike(query: String): List<Article>

    // FTS5 search (optimized)
    @Query("""
        SELECT articles.* FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY bm25(articles_fts)
    """)
    fun searchWithFts(query: String): Flow<List<Article>>
}
```

### Complete Repository Implementation

```kotlin
class ArticleRepository(private val dao: ArticleDao) {

    // Search with debounce for better UX
    fun searchArticles(queryFlow: Flow<String>): Flow<List<ArticleSearchResult>> {
        return queryFlow
            .debounce(300)  // Wait 300ms after user stops typing
            .filter { it.isNotBlank() && it.length >= 2 }  // Minimum 2 characters
            .distinctUntilChanged()
            .flatMapLatest { query ->
                dao.searchWithRanking(sanitizeQuery(query))
            }
    }

    // Sanitize user input to prevent FTS syntax errors
    private fun sanitizeQuery(query: String): String {
        // Remove special FTS operators if needed
        return query
            .trim()
            .replace("\"", "")  // Remove quotes
            .replace("*", "")   // Remove wildcards
            .split("\\s+".toRegex())  // Split by whitespace
            .filter { it.isNotEmpty() }
            .joinToString(" AND ")  // Join with AND operator
    }

    // Autocomplete suggestions
    suspend fun getAutocompleteSuggestions(prefix: String): List<String> {
        if (prefix.length < 2) return emptyList()

        val results = dao.autocompleteSearch(prefix)
        return results
            .map { it.title }
            .distinct()
            .take(10)
    }

    // Advanced search with filters
    suspend fun advancedSearch(
        query: String,
        categoryId: Long? = null,
        authorName: String? = null,
        fromDate: Long? = null,
        toDate: Long? = null,
        limit: Int = 50
    ): List<ArticleSearchResult> {
        var ftsQuery = query

        // Add field filters
        if (authorName != null) {
            ftsQuery += " author:$authorName"
        }

        return dao.searchWithWeightedRanking(ftsQuery, limit)
            .filter { result ->
                // Apply additional filters
                (categoryId == null || result.article.categoryId == categoryId) &&
                (fromDate == null || result.article.publishedAt >= fromDate) &&
                (toDate == null || result.article.publishedAt <= toDate)
            }
    }

    // Rebuild FTS index (for maintenance)
    @Transaction
    suspend fun rebuildFtsIndex() {
        dao.clearFtsTable()
        val allArticles = dao.getAllArticles()
        allArticles.forEach { article ->
            dao.insertArticleFts(
                ArticleFts(
                    rowid = article.id,
                    title = article.title,
                    content = article.content,
                    author = article.author,
                    tags = article.tags
                )
            )
        }
    }
}
```

### ViewModel Integration

```kotlin
class SearchViewModel(
    private val repository: ArticleRepository
) : ViewModel() {

    private val _searchQuery = MutableStateFlow("")
    val searchQuery: StateFlow<String> = _searchQuery.asStateFlow()

    val searchResults: StateFlow<List<ArticleSearchResult>> =
        repository.searchArticles(_searchQuery)
            .stateIn(
                scope = viewModelScope,
                started = SharingStarted.WhileSubscribed(5000),
                initialValue = emptyList()
            )

    fun onSearchQueryChanged(query: String) {
        _searchQuery.value = query
    }

    // For autocomplete
    private val _suggestions = MutableStateFlow<List<String>>(emptyList())
    val suggestions: StateFlow<List<String>> = _suggestions.asStateFlow()

    fun loadSuggestions(prefix: String) {
        viewModelScope.launch {
            _suggestions.value = repository.getAutocompleteSuggestions(prefix)
        }
    }
}
```

### UI Integration with Jetpack Compose

```kotlin
@Composable
fun SearchScreen(viewModel: SearchViewModel = viewModel()) {
    val searchQuery by viewModel.searchQuery.collectAsState()
    val searchResults by viewModel.searchResults.collectAsState()
    val suggestions by viewModel.suggestions.collectAsState()

    Column(modifier = Modifier.fillMaxSize()) {
        SearchBar(
            query = searchQuery,
            onQueryChange = {
                viewModel.onSearchQueryChanged(it)
                viewModel.loadSuggestions(it)
            },
            suggestions = suggestions
        )

        LazyColumn {
            items(searchResults) { result ->
                SearchResultItem(
                    article = result.article,
                    rank = result.rank
                )
            }
        }
    }
}

@Composable
fun SearchResultItem(article: Article, rank: Double) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp)
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = article.title,
                style = MaterialTheme.typography.titleMedium,
                fontWeight = FontWeight.Bold
            )
            Spacer(modifier = Modifier.height(4.dp))
            Text(
                text = article.content.take(150) + "...",
                style = MaterialTheme.typography.bodyMedium,
                color = Color.Gray
            )
            Spacer(modifier = Modifier.height(8.dp))
            Row {
                Text(
                    text = article.author,
                    style = MaterialTheme.typography.bodySmall,
                    color = Color.Gray
                )
                Spacer(modifier = Modifier.width(16.dp))
                Text(
                    text = "Relevance: ${"%.2f".format(rank)}",
                    style = MaterialTheme.typography.bodySmall,
                    color = Color.Gray
                )
            }
        }
    }
}
```

### Best Practices

1. **Use FTS5**: Always prefer FTS5 over FTS4 for better performance
2. **External Content Tables**: Avoid data duplication with contentEntity parameter
3. **Automatic Sync**: Use triggers to keep FTS table in sync with main table
4. **Index Only Searchable Fields**: Don't index metadata fields
5. **Sanitize User Input**: Prevent FTS syntax errors from user queries
6. **Debounce Search**: Wait for user to stop typing before searching
7. **Use BM25 Ranking**: Sort results by relevance for better UX
8. **Pagination**: Use LIMIT/OFFSET or Paging 3 for large result sets
9. **Highlight Matches**: Use highlight() and snippet() functions
10. **Choose Right Tokenizer**: Porter for English, Unicode61 for general use
11. **Rebuild Index**: Provide maintenance function to rebuild FTS index
12. **Test Performance**: Benchmark with production-sized datasets

### Common Pitfalls

1. **Forgetting @Transaction**: FTS sync operations must be atomic
2. **Not Indexing Foreign Keys**: Slows down JOIN operations
3. **Special Characters**: FTS operators in user input cause errors
4. **Duplicating Data**: Not using external content table wastes space
5. **No Debouncing**: Searching on every keystroke impacts performance
6. **Wrong Tokenizer**: Using simple tokenizer for non-ASCII text
7. **Not Using Ranking**: Results not sorted by relevance
8. **Loading All Results**: Not paginating large result sets
9. **Forgetting Triggers**: Manual FTS sync is error-prone
10. **Not Testing Edge Cases**: Empty queries, special characters, long text

### Summary

Room's FTS integration provides powerful text search capabilities:

- **FTS5**: Modern, performant full-text search extension
- **BM25 Ranking**: Relevance-based result ordering
- **External Content**: Avoid data duplication
- **Tokenizers**: Language-specific text processing
- **Highlighting**: Mark matching terms in results
- **10-100x Performance**: Dramatically faster than LIKE queries
- **Boolean Operators**: Complex query support (AND, OR, NOT)
- **Prefix Matching**: Autocomplete functionality
- **Triggers**: Automatic FTS synchronization

Always use FTS5 for production apps with significant text search requirements, and optimize with proper indexing, pagination, and query sanitization.

---

## Ответ (RU)

**Полнотекстовый поиск (FTS)** в Room обеспечивает эффективные возможности текстового поиска через расширения FTS SQLite (FTS3, FTS4 и FTS5). FTS необходим для поиска по большим текстовым наборам данных со сложными запросами, поддерживая функции префиксного поиска, ранжирования и подсветки.

### Зачем использовать FTS?

Традиционные запросы `LIKE` становятся крайне медленными на больших наборах данных и не поддерживают продвинутые функции текстового поиска. FTS обеспечивает:

- **Производительность**: в 10-100 раз быстрее запросов LIKE на больших наборах данных
- **Ранжирование по релевантности**: Сортировка результатов по оценке релевантности
- **Префиксное сопоставление**: Поиск по части слова
- **Булевы операторы**: Запросы AND, OR, NOT
- **Фразовые запросы**: Поиск точных фраз
- **Токенизация**: Языково-зависимое разделение на слова

### FTS4 vs FTS5

| Характеристика | FTS4 | FTS5 |
|----------------|------|------|
| Производительность | Хорошая | Лучше (оптимизирована) |
| Ранжирование | Базовое | Алгоритм BM25 |
| Использование памяти | Выше | Ниже |
| Вспомогательные функции | Ограниченные | Богатые (highlight, snippet) |
| Префиксные запросы | Поддерживаются | Лучше оптимизированы |
| Рекомендация | Устаревшее | **Использовать для новых проектов** |

**Всегда используйте FTS5 для новых проектов**, если не нужна обратная совместимость с очень старыми версиями Android.

### Базовая реализация FTS5

#### Простая FTS сущность

```kotlin
// FTS сущность для поиска заметок
@Fts4  // или @Fts5 для лучшей производительности
@Entity(tableName = "notes_fts")
data class NoteFts(
    @PrimaryKey
    @ColumnInfo(name = "rowid")
    val rowid: Long,
    val title: String,
    val content: String
)

// Обычная сущность для хранения данных заметки
@Entity(tableName = "notes")
data class Note(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val title: String,
    val content: String,
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis()
)
```

#### FTS DAO

```kotlin
@Dao
interface NoteDao {
    @Insert
    suspend fun insertNote(note: Note): Long

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertNoteFts(noteFts: NoteFts)

    // Базовый FTS поиск используя оператор MATCH
    @Query("""
        SELECT notes.* FROM notes
        INNER JOIN notes_fts ON notes.id = notes_fts.rowid
        WHERE notes_fts MATCH :query
        ORDER BY notes.updatedAt DESC
    """)
    fun searchNotes(query: String): Flow<List<Note>>
}
```

### Продвинутый FTS5 с внешней таблицей содержимого

Для production приложений используйте FTS5 с **внешней таблицей содержимого** чтобы избежать дублирования данных.

```kotlin
// Основная сущность содержимого
@Entity(tableName = "articles")
data class Article(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0,
    val title: String,
    val content: String,
    val author: String,
    val publishedAt: Long
)

// FTS5 сущность с внешним содержимым
@Fts4(contentEntity = Article::class)
@Entity(tableName = "articles_fts")
data class ArticleFts(
    @PrimaryKey
    @ColumnInfo(name = "rowid")
    val rowid: Long,
    val title: String,
    val content: String,
    val author: String
)
```

### FTS5 с ранжированием BM25

BM25 — это алгоритм ранжирования, который оценивает результаты поиска по релевантности.

```kotlin
data class ArticleSearchResult(
    @Embedded
    val article: Article,
    val rank: Double  // Оценка релевантности BM25
)

@Dao
interface ArticleSearchDao {
    // Поиск с ранжированием BM25 (меньшая оценка = более релевантно)
    @Query("""
        SELECT articles.*, bm25(articles_fts) as rank
        FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY rank
    """)
    fun searchWithRanking(query: String): Flow<List<ArticleSearchResult>>

    // Взвешенное ранжирование BM25 (усиление совпадений в заголовке)
    @Query("""
        SELECT articles.*, bm25(articles_fts, 10.0, 1.0, 5.0) as rank
        FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY rank
        LIMIT :limit
    """)
    suspend fun searchWithWeightedRanking(
        query: String,
        limit: Int = 20
    ): List<ArticleSearchResult>
    // Веса: title=10.0, content=1.0, author=5.0
}
```

### Подсветка результатов поиска

FTS5 предоставляет функции для подсветки совпадающих терминов в результатах поиска.

```kotlin
data class ArticleWithHighlight(
    @Embedded
    val article: Article,
    val highlightedTitle: String,
    val highlightedSnippet: String,
    val rank: Double
)

@Dao
interface ArticleHighlightDao {
    // Подсветка совпадающих терминов с кастомными тегами
    @Query("""
        SELECT
            articles.*,
            highlight(articles_fts, 0, '<b>', '</b>') as highlightedTitle,
            snippet(articles_fts, 1, '<mark>', '</mark>', '...', 30) as highlightedSnippet,
            bm25(articles_fts) as rank
        FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY rank
        LIMIT :limit
    """)
    suspend fun searchWithHighlight(
        query: String,
        limit: Int = 20
    ): List<ArticleWithHighlight>

    // highlight() синтаксис:
    // highlight(fts_table, column_index, start_tag, end_tag)
    // column_index: 0=title, 1=content, 2=author

    // snippet() синтаксис:
    // snippet(fts_table, column_index, start_tag, end_tag, ellipsis, max_tokens)
}
```

### Кастомные токенизаторы

FTS поддерживает различные токенизаторы для языково-специфичной обработки текста.

```kotlin
// Unicode61 токенизатор (по умолчанию, поддерживает большинство языков)
@Fts4(tokenizer = FtsOptions.TOKENIZER_UNICODE61)
@Entity(tableName = "articles_fts")
data class ArticleFtsUnicode(
    val title: String,
    val content: String
)

// Porter токенизатор (английский stemming)
// "running" соответствует "run", "runner", "runs"
@Fts4(tokenizer = FtsOptions.TOKENIZER_PORTER)
@Entity(tableName = "articles_fts_porter")
data class ArticleFtsPorter(
    val title: String,
    val content: String
)

// Simple токенизатор (только ASCII, быстрее)
@Fts4(tokenizer = FtsOptions.TOKENIZER_SIMPLE)
@Entity(tableName = "articles_fts_simple")
data class ArticleFtsSimple(
    val title: String,
    val content: String
)
```

### Оптимизация производительности

#### 1. Использование триггеров для автоматической синхронизации FTS

Вместо ручной синхронизации FTS таблиц, используйте SQLite триггеры:

```kotlin
@Database(
    entities = [Article::class, ArticleFts::class],
    version = 1
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun articleDao(): ArticleDao

    override fun onCreate(db: SupportSQLiteDatabase) {
        super.onCreate(db)

        // Триггер для синхронизации INSERT
        db.execSQL("""
            CREATE TRIGGER articles_fts_insert AFTER INSERT ON articles
            BEGIN
                INSERT INTO articles_fts (rowid, title, content, author)
                VALUES (new.id, new.title, new.content, new.author);
            END
        """)

        // Триггер для синхронизации UPDATE
        db.execSQL("""
            CREATE TRIGGER articles_fts_update AFTER UPDATE ON articles
            BEGIN
                UPDATE articles_fts
                SET title = new.title,
                    content = new.content,
                    author = new.author
                WHERE rowid = new.id;
            END
        """)

        // Триггер для синхронизации DELETE
        db.execSQL("""
            CREATE TRIGGER articles_fts_delete AFTER DELETE ON articles
            BEGIN
                DELETE FROM articles_fts WHERE rowid = old.id;
            END
        """)
    }
}
```

#### 2. Оптимизация размера FTS таблицы

```kotlin
// Индексировать только поисковые поля, исключить метаданные
@Fts4(contentEntity = Article::class)
@Entity(tableName = "articles_fts")
data class ArticleFtsOptimized(
    @PrimaryKey
    @ColumnInfo(name = "rowid")
    val rowid: Long,
    val title: String,      // Индекс
    val content: String,    // Индекс
    // Исключить: publishedAt, categoryId, viewCount, isFavorite
)
```

#### 3. Пагинация для больших наборов результатов

```kotlin
@Dao
interface ArticleDao {
    // Использовать LIMIT и OFFSET для пагинации
    @Query("""
        SELECT articles.*, bm25(articles_fts) as rank
        FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY rank
        LIMIT :limit OFFSET :offset
    """)
    suspend fun searchArticlesPaged(
        query: String,
        limit: Int,
        offset: Int
    ): List<ArticleSearchResult>

    // Или использовать Paging 3
    @Query("""
        SELECT articles.* FROM articles
        INNER JOIN articles_fts ON articles.id = articles_fts.rowid
        WHERE articles_fts MATCH :query
        ORDER BY bm25(articles_fts)
    """)
    fun searchArticlesPaging(query: String): PagingSource<Int, Article>
}
```

### Сравнение производительности

Сравнение FTS5 и запросов LIKE на разных размерах наборов данных:

```kotlin
class SearchBenchmark {
    suspend fun benchmarkSearch(query: String, dataset: List<Article>) {
        val dao = database.articleDao()

        // Заполнить тестовые данные
        dataset.forEach { dao.insertArticleWithFts(it) }

        // Бенчмарк LIKE запроса
        val likeStart = System.currentTimeMillis()
        val likeResults = dao.searchWithLike("%$query%")
        val likeTime = System.currentTimeMillis() - likeStart

        // Бенчмарк FTS5 запроса
        val ftsStart = System.currentTimeMillis()
        val ftsResults = dao.searchArticles(query).first()
        val ftsTime = System.currentTimeMillis() - ftsStart

        println("""
            Размер набора данных: ${dataset.size}
            Запрос: "$query"

            LIKE запрос:
              Время: ${likeTime}мс
              Результаты: ${likeResults.size}

            FTS5 запрос:
              Время: ${ftsTime}мс
              Результаты: ${ftsResults.size}
              Ускорение: ${likeTime.toFloat() / ftsTime}x
        """.trimIndent())
    }
}

// Ожидаемые результаты:
// 1,000 статей:    FTS5 ~2-5x быстрее
// 10,000 статей:   FTS5 ~10-20x быстрее
// 100,000 статей:  FTS5 ~50-100x быстрее
```

### Полная реализация Repository

```kotlin
class ArticleRepository(private val dao: ArticleDao) {

    // Поиск с debounce для лучшего UX
    fun searchArticles(queryFlow: Flow<String>): Flow<List<ArticleSearchResult>> {
        return queryFlow
            .debounce(300)  // Ждать 300мс после того как пользователь прекратит печатать
            .filter { it.isNotBlank() && it.length >= 2 }  // Минимум 2 символа
            .distinctUntilChanged()
            .flatMapLatest { query ->
                dao.searchWithRanking(sanitizeQuery(query))
            }
    }

    // Санитизация пользовательского ввода для предотвращения синтаксических ошибок FTS
    private fun sanitizeQuery(query: String): String {
        // Удалить специальные операторы FTS если нужно
        return query
            .trim()
            .replace("\"", "")  // Удалить кавычки
            .replace("*", "")   // Удалить wildcards
            .split("\\s+".toRegex())  // Разделить по пробелам
            .filter { it.isNotEmpty() }
            .joinToString(" AND ")  // Объединить с оператором AND
    }

    // Подсказки автодополнения
    suspend fun getAutocompleteSuggestions(prefix: String): List<String> {
        if (prefix.length < 2) return emptyList()

        val results = dao.autocompleteSearch(prefix)
        return results
            .map { it.title }
            .distinct()
            .take(10)
    }
}
```

### Best Practices

1. **Использовать FTS5**: Всегда предпочитать FTS5 вместо FTS4 для лучшей производительности
2. **Внешние таблицы содержимого**: Избегать дублирования данных с параметром contentEntity
3. **Автоматическая синхронизация**: Использовать триггеры для синхронизации FTS таблицы с основной
4. **Индексировать только поисковые поля**: Не индексировать поля метаданных
5. **Санитизация пользовательского ввода**: Предотвращать синтаксические ошибки FTS из пользовательских запросов
6. **Debounce поиска**: Ждать пока пользователь прекратит печатать перед поиском
7. **Использовать ранжирование BM25**: Сортировать результаты по релевантности для лучшего UX
8. **Пагинация**: Использовать LIMIT/OFFSET или Paging 3 для больших наборов результатов
9. **Подсвечивать совпадения**: Использовать функции highlight() и snippet()
10. **Выбрать правильный токенизатор**: Porter для английского, Unicode61 для общего использования
11. **Перестроение индекса**: Предоставить функцию maintenance для перестроения FTS индекса
12. **Тестировать производительность**: Бенчмаркить с наборами данных размера production

### Частые ошибки

1. **Забывание @Transaction**: Операции синхронизации FTS должны быть атомарными
2. **Неиндексирование внешних ключей**: Замедляет операции JOIN
3. **Специальные символы**: Операторы FTS в пользовательском вводе вызывают ошибки
4. **Дублирование данных**: Неиспользование внешней таблицы содержимого тратит место
5. **Без debouncing**: Поиск на каждом нажатии клавиши влияет на производительность
6. **Неправильный токенизатор**: Использование simple токенизатора для не-ASCII текста
7. **Без ранжирования**: Результаты не отсортированы по релевантности
8. **Загрузка всех результатов**: Непагинирование больших наборов результатов
9. **Забывание триггеров**: Ручная синхронизация FTS подвержена ошибкам
10. **Нетестирование граничных случаев**: Пустые запросы, специальные символы, длинный текст

### Резюме

Интеграция FTS в Room обеспечивает мощные возможности текстового поиска:

- **FTS5**: Современное, производительное расширение полнотекстового поиска
- **Ранжирование BM25**: Упорядочивание результатов на основе релевантности
- **Внешнее содержимое**: Избежание дублирования данных
- **Токенизаторы**: Языково-специфичная обработка текста
- **Подсветка**: Отметка совпадающих терминов в результатах
- **10-100x производительность**: Драматически быстрее запросов LIKE
- **Булевы операторы**: Поддержка сложных запросов (AND, OR, NOT)
- **Префиксное сопоставление**: Функциональность автодополнения
- **Триггеры**: Автоматическая синхронизация FTS

Всегда используйте FTS5 для production приложений со значительными требованиями к текстовому поиску, и оптимизируйте с правильной индексацией, пагинацией и санитизацией запросов. FTS обеспечивает в 10-100 раз лучшую производительность чем LIKE запросы на больших наборах данных и поддерживает продвинутые функции поиска такие как ранжирование BM25, подсветку совпадений и булевы операторы.

---

## Related Questions

### Prerequisites (Easier)
- [[q-room-code-generation-timing--android--medium]] - Storage
- [[q-room-transactions-dao--room--medium]] - Storage
- [[q-room-paging3-integration--room--medium]] - Storage
