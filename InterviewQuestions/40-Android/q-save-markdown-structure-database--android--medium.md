---
id: android-218
title: Save Markdown Structure To Database / Сохранение структуры Markdown в базе данных
aliases: [Save Markdown Structure To Database, Сохранение структуры Markdown в базе данных]
topic: android
subtopics: [room]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android, c-database-design, q-database-encryption-android--android--medium, q-how-to-save-and-apply-theme-settings--android--medium, q-room-database-migrations--android--medium, q-save-data-outside-fragment--android--medium]
created: 2025-10-15
updated: 2025-11-10
tags: [android/room, difficulty/medium]
---
# Вопрос (RU)
> Сохранение структуры Markdown в базе данных

# Question (EN)
> Save Markdown Structure To Database

---

## Ответ (RU)
Сохранение Markdown (и при необходимости его структуры) зависит от задач приложения. На Android обычно используют Room (SQLite) и/или файловое хранение. Ниже приведены основные подходы с примерами реализации, плюс гибридный вариант.

### Подход 1: Хранить Как Обычный Текст (самый простой)

Лучше всего подходит для простых случаев, read-heavy-приложений, редакторов форматированного текста.

Сохраняем сырой Markdown как строку в базе (например, Room поверх SQLite).

```kotlin
@Entity(tableName = "documents")
data class Document(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0L,
    val title: String,
    val markdownContent: String,  // Храним сырой Markdown
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis()
)

@Dao
interface DocumentDao {
    @Query("SELECT * FROM documents")
    fun getAllDocuments(): Flow<List<Document>>

    @Query("SELECT * FROM documents WHERE id = :id")
    suspend fun getDocumentById(id: Long): Document?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(document: Document): Long

    @Update
    suspend fun update(document: Document)

    @Query("UPDATE documents SET markdownContent = :content, updatedAt = :timestamp WHERE id = :id")
    suspend fun updateContent(id: Long, content: String, timestamp: Long)
}
```

Использование:

```kotlin
class MarkdownRepository(private val documentDao: DocumentDao) {
    suspend fun saveDocument(title: String, markdown: String): Long {
        val document = Document(
            title = title,
            markdownContent = markdown
        )
        return documentDao.insert(document)
    }

    suspend fun getDocument(id: Long): Document? {
        return documentDao.getDocumentById(id)
    }

    fun getAllDocuments(): Flow<List<Document>> {
        return documentDao.getAllDocuments()
    }
}
```

Плюсы:
- Простая реализация
- Полностью сохраняет исходное форматирование
- Удобно редактировать
- Небольшой объем хранения

Минусы:
- Нельзя эффективно искать по структуре (заголовки, списки и т.п.)
- Нельзя удобно выбирать отдельные элементы
- Нужен рендеринг для отображения

---

### Подход 2: Парсить В JSON И Сохранять Структуру

Лучше всего подходит для сложных запросов, структурированного поиска, анализа содержимого.

Идея: распарсить Markdown в AST (Abstract Syntax Tree), преобразовать в модель, сериализовать в JSON и хранить вместе с исходным Markdown.

```kotlin
// Gradle-зависимость
dependencies {
    implementation("org.commonmark:commonmark:0.21.0")
}
```

Парсинг и преобразование в структуру:

```kotlin
import org.commonmark.parser.Parser
import org.commonmark.node.*

data class MarkdownStructure(
    val type: String,           // "document", "heading", "paragraph" и т.д.
    val content: String?,
    val level: Int? = null,     // Для заголовков
    val children: List<MarkdownStructure> = emptyList()
)

@Entity(tableName = "documents")
data class DocumentEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0L,
    val title: String,
    val markdownRaw: String,        // Исходный Markdown
    val structureJson: String,      // Спарсенная структура в виде JSON
    val createdAt: Long = System.currentTimeMillis()
)

fun parseMarkdownToStructure(markdown: String): MarkdownStructure {
    val parser = Parser.builder().build()
    val document = parser.parse(markdown)

    fun nodeToStructure(node: Node): MarkdownStructure {
        return when (node) {
            is Heading -> MarkdownStructure(
                type = "heading",
                content = extractText(node),
                level = node.level,
                children = node.children().map { nodeToStructure(it) }
            )
            is Paragraph -> MarkdownStructure(
                type = "paragraph",
                content = extractText(node),
                children = node.children().map { nodeToStructure(it) }
            )
            is BulletList -> MarkdownStructure(
                type = "bullet_list",
                content = null,
                children = node.children().map { nodeToStructure(it) }
            )
            is ListItem -> MarkdownStructure(
                type = "list_item",
                content = extractText(node),
                children = node.children().map { nodeToStructure(it) }
            )
            else -> MarkdownStructure(
                type = node.javaClass.simpleName.lowercase(),
                content = extractText(node),
                children = node.children().map { nodeToStructure(it) }
            )
        }
    }

    return MarkdownStructure(
        type = "document",
        content = null,
        children = document.children().map { nodeToStructure(it) }
    )
}

fun extractText(node: Node): String {
    val sb = StringBuilder()
    node.accept(object : AbstractVisitor() {
        override fun visit(text: org.commonmark.node.Text) {
            sb.append(text.literal)
        }
    })
    return sb.toString()
}

private fun Node.children(): List<Node> {
    val children = mutableListOf<Node>()
    var child = firstChild
    while (child != null) {
        children.add(child)
        child = child.next
    }
    return children
}
```

Room + поиск по JSON-строке (без JSON-операторов):

```kotlin
@Dao
interface DocumentEntityDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(document: DocumentEntity): Long

    @Query("SELECT * FROM documents WHERE id = :id")
    suspend fun getDocumentById(id: Long): DocumentEntity?

    // Пример наивного поиска по JSON через LIKE; для продакшена лучше FTS или отдельные колонки
    @Query("SELECT * FROM documents WHERE structureJson LIKE :pattern")
    suspend fun searchByStructure(pattern: String): List<DocumentEntity>
}

@Database(entities = [DocumentEntity::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun documentEntityDao(): DocumentEntityDao
}

class MarkdownStructureRepository(
    private val documentDao: DocumentEntityDao,
    private val gson: Gson
) {
    suspend fun saveMarkdown(title: String, markdown: String): Long {
        val structure = parseMarkdownToStructure(markdown)
        val structureJson = gson.toJson(structure)

        val document = DocumentEntity(
            title = title,
            markdownRaw = markdown,
            structureJson = structureJson
        )
        return documentDao.insert(document)
    }

    suspend fun getDocument(id: Long): Pair<String, MarkdownStructure>? {
        val doc = documentDao.getDocumentById(id) ?: return null
        val structure = gson.fromJson(doc.structureJson, MarkdownStructure::class.java)
        return doc.markdownRaw to structure
    }

    // Наивный пример: поиск заголовков по JSON-строке
    suspend fun searchHeadings(query: String): List<DocumentEntity> {
        val pattern = "%\"type\":\"heading\"%" + query + "%"
        return documentDao.searchByStructure(pattern)
    }
}
```

Замечание: поиск по JSON через LIKE в SQLite (включая Android) хрупкий и неэффективный, так как нет нативных JSON-операторов. Для серьезных задач стоит:
- нормализовать структуру в отдельные таблицы (например, таблица заголовков), и/или
- использовать FTS (Full-Text Search) по содержимому.

Плюсы:
- Явно представлена структура Markdown
- Удобно для анализа и продвинутого поиска
- Можно хранить и исходный текст, и структуру

Минусы:
- Сложнее реализация
- Больше объем данных
- Нагрузка на парсинг и сериализацию
- JSON-поиск ограничен; лучше нормализовать ключевые поля

---

### Подход 3: Конвертация В HTML И Хранение HTML

Лучше всего подходит для приложений, ориентированных на отображение, особенно если используется WebView.

```kotlin
import org.commonmark.parser.Parser
import org.commonmark.renderer.html.HtmlRenderer

@Entity(tableName = "documents")
data class DocumentHtmlEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0L,
    val title: String,
    val markdownRaw: String,
    val htmlContent: String,  // Сгенерированный HTML
    val createdAt: Long = System.currentTimeMillis()
)

fun markdownToHtml(markdown: String): String {
    val parser = Parser.builder().build()
    val document = parser.parse(markdown)
    val renderer = HtmlRenderer.builder().build()
    return renderer.render(document)
}

@Dao
interface DocumentHtmlDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(document: DocumentHtmlEntity): Long

    @Query("SELECT * FROM documents WHERE id = :id")
    suspend fun getDocumentById(id: Long): DocumentHtmlEntity?
}

class MarkdownHtmlRepository(private val documentDao: DocumentHtmlDao) {
    suspend fun saveDocument(title: String, markdown: String): Long {
        val html = markdownToHtml(markdown)
        val document = DocumentHtmlEntity(
            title = title,
            markdownRaw = markdown,
            htmlContent = html
        )
        return documentDao.insert(document)
    }
}
```

Отображение через WebView (упрощенно):

```kotlin
class MarkdownViewerFragment : Fragment() {
    private val viewModel: MarkdownViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewModel.document.observe(viewLifecycleOwner) { doc ->
            webView.loadDataWithBaseURL(
                null,
                doc.htmlContent,
                "text/html",
                "UTF-8",
                null
            )
        }
    }
}
```

Плюсы:
- Быстрое отображение (HTML уже сгенерирован)
- Удобная работа с WebView
- Легкая стилизация через CSS

Минусы:
- Для редактирования нужно возвращаться к Markdown
- HTML обычно занимает больше места, чем сырой текст
- Теряется явная структура AST Markdown

---

### Подход 4: Хранение В Файлах

Лучше всего подходит для больших документов, экспорта/импорта и совместимости с внешними инструментами.

Часто используется вместе с Room: база хранит метаданные и индексы, а сами .md-файлы лежат в файловой системе.

```kotlin
class MarkdownFileManager(private val context: Context) {

    // Сохранение во внутреннее хранилище
    fun saveToInternalStorage(filename: String, markdown: String) {
        val file = File(context.filesDir, "$filename.md")
        file.writeText(markdown)
    }

    // Чтение из внутреннего хранилища
    fun readFromInternalStorage(filename: String): String {
        val file = File(context.filesDir, "$filename.md")
        return if (file.exists()) file.readText() else ""
    }

    // Сохранение в app-specific external storage (без явных READ/WRITE разрешений)
    fun saveToExternalAppDirectory(filename: String, markdown: String) {
        val dir = context.getExternalFilesDir(null) ?: context.filesDir
        val file = File(dir, "$filename.md")
        file.writeText(markdown)
    }

    // Экспорт в Downloads через MediaStore (упрощенный пример)
    fun exportToDownloads(filename: String, markdown: String) {
        val contentValues = ContentValues().apply {
            put(MediaStore.Downloads.DISPLAY_NAME, "$filename.md")
            put(MediaStore.Downloads.MIME_TYPE, "text/markdown")
            put(MediaStore.Downloads.IS_PENDING, 1)
        }

        val resolver = context.contentResolver
        val uri = resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, contentValues)

        uri?.let { outUri ->
            resolver.openOutputStream(outUri)?.use { output ->
                output.write(markdown.toByteArray())
            }

            contentValues.clear()
            contentValues.put(MediaStore.Downloads.IS_PENDING, 0)
            resolver.update(outUri, contentValues, null, null)
        }
    }

    // Список всех Markdown-файлов во внутреннем хранилище
    fun listMarkdownFiles(): List<String> {
        return context.filesDir.listFiles { file ->
            file.extension == "md"
        }?.map { it.nameWithoutExtension } ?: emptyList()
    }
}
```

Важно: для публичного внешнего хранилища на современных версиях Android нужно соблюдать правила scoped storage и корректно работать с разрешениями.

Плюсы:
- Стандартные .md-файлы
- Удобный экспорт/импорт
- Можно редактировать внешними редакторами
- Хорошо сочетается с системой контроля версий

Минусы:
- Без дополнительной индексации сложно делать структурированные запросы по содержимому
- Нужно управлять файловой структурой и синхронизацией с базой

---

### Гибридный Подход (рекомендуемый)

Комбинируем варианты: Room для индексации/метаданных и хранения Markdown, кэш HTML для быстрого отображения, плюс при необходимости бэкап в файл.

```kotlin
@Entity(tableName = "documents")
data class HybridDocument(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0L,
    val title: String,
    val markdownContent: String,     // Сырой Markdown (для редактирования)
    val htmlCache: String? = null,   // Кэшированный HTML (быстрое отображение)
    val filePath: String? = null,    // Путь к файловому бэкапу (опционально)
    val tags: String? = null,        // Теги, извлеченные из заголовков
    val wordCount: Int = 0,
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis()
)

@Dao
interface HybridDocumentDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(document: HybridDocument): Long
}

class HybridMarkdownRepository(
    private val dao: HybridDocumentDao,
    private val fileManager: MarkdownFileManager
) {
    suspend fun saveDocument(title: String, markdown: String): Long {
        val html = markdownToHtml(markdown)
        val tags = extractTags(markdown)
        val wordCount = markdown.split("\\s+".toRegex())
            .filter { it.isNotBlank() }
            .size

        // В реальном коде имеет смысл сначала сохранить документ, получить id, затем вычислить filePath
        val tempDocument = HybridDocument(
            title = title,
            markdownContent = markdown,
            htmlCache = html,
            tags = tags.joinToString(","),
            wordCount = wordCount
        )
        val id = dao.insert(tempDocument)

        val filename = "doc_$id"
        fileManager.saveToInternalStorage(filename, markdown)
        val filePath = "${'$'}{filename}.md"

        val finalDocument = tempDocument.copy(
            id = id,
            filePath = filePath
        )
        dao.insert(finalDocument)

        return id
    }

    private fun extractTags(markdown: String): List<String> {
        val headingRegex = """^#{1,6}\s+(.+)$""".toRegex(RegexOption.MULTILINE)
        return headingRegex.findAll(markdown)
            .map { it.groupValues[1].trim() }
            .toList()
    }
}
```

Такой подход позволяет:
- хранить редактируемый исходник (Markdown);
- быстро показывать содержимое за счет заранее сгенерированного HTML;
- извлекать базовые метаданные (заголовки как теги, количество слов и т.д.);
- при необходимости дополнять структуру нормализованными таблицами или FTS.

---

## Резюме (RU)

Основные подходы на Android (часто комбинируются):

1. Сырой Markdown в Room — самый простой и хороший базовый вариант.
2. AST/JSON + Room — для сложного структурного поиска и анализа.
3. HTML + Room — для быстрого отображения и WebView.
4. Файлы (.md) — для больших документов и интеграции с внешними инструментами; база хранит индексы/метаданные.

Рекомендуется:
- Для простого приложения: хранить сырой Markdown в Room.
- Для сложного: гибрид — сырой Markdown + кэш HTML + метаданные (и/или нормализованная структура, FTS).
- Для очень больших документов/экспорта: хранить содержимое в файлах, а в Room держать только индекс и служебные данные.

---

## Answer (EN)
Saving Markdown (and optionally its structure) depends on your application's goals. There are several approaches with different trade-offs.

### Approach 1: Store as Plain Text (Simplest)

Best for: Simple use cases, read-heavy applications, rich text editors.

Store the raw Markdown text as a string in the database (e.g., Room over SQLite).

```kotlin
@Entity(tableName = "documents")
data class Document(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0L,
    val title: String,
    val markdownContent: String,  // Store raw Markdown
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis()
)

@Dao
interface DocumentDao {
    @Query("SELECT * FROM documents")
    fun getAllDocuments(): Flow<List<Document>>

    @Query("SELECT * FROM documents WHERE id = :id")
    suspend fun getDocumentById(id: Long): Document?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(document: Document): Long

    @Update
    suspend fun update(document: Document)

    @Query("UPDATE documents SET markdownContent = :content, updatedAt = :timestamp WHERE id = :id")
    suspend fun updateContent(id: Long, content: String, timestamp: Long)
}
```

Usage:

```kotlin
class MarkdownRepository(private val documentDao: DocumentDao) {
    suspend fun saveDocument(title: String, markdown: String): Long {
        val document = Document(
            title = title,
            markdownContent = markdown
        )
        return documentDao.insert(document)
    }

    suspend fun getDocument(id: Long): Document? {
        return documentDao.getDocumentById(id)
    }

    fun getAllDocuments(): Flow<List<Document>> {
        return documentDao.getAllDocuments()
    }
}
```

Pros:
- Simple implementation
- Preserves original formatting
- Easy to edit
- Small storage footprint

Cons:
- Can't efficiently query structure (headings, lists, etc.)
- Can't conveniently access individual elements
- Requires rendering for display

---

### Approach 2: Parse to JSON and Store Structure

Best for: Complex queries, structured search, content analysis.

Parse Markdown into a structured format (AST - Abstract Syntax Tree), serialize to JSON, and store alongside the raw Markdown.

```kotlin
// Gradle dependency
dependencies {
    implementation("org.commonmark:commonmark:0.21.0")
}
```

Parse and convert to structure:

```kotlin
import org.commonmark.parser.Parser
import org.commonmark.node.*

data class MarkdownStructure(
    val type: String,           // "document", "heading", "paragraph", etc.
    val content: String?,
    val level: Int? = null,     // For headings
    val children: List<MarkdownStructure> = emptyList()
)

@Entity(tableName = "documents")
data class DocumentEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0L,
    val title: String,
    val markdownRaw: String,        // Original Markdown
    val structureJson: String,      // Parsed structure as JSON
    val createdAt: Long = System.currentTimeMillis()
)

fun parseMarkdownToStructure(markdown: String): MarkdownStructure {
    val parser = Parser.builder().build()
    val document = parser.parse(markdown)

    fun nodeToStructure(node: Node): MarkdownStructure {
        return when (node) {
            is Heading -> MarkdownStructure(
                type = "heading",
                content = extractText(node),
                level = node.level,
                children = node.children().map { nodeToStructure(it) }
            )
            is Paragraph -> MarkdownStructure(
                type = "paragraph",
                content = extractText(node),
                children = node.children().map { nodeToStructure(it) }
            )
            is BulletList -> MarkdownStructure(
                type = "bullet_list",
                content = null,
                children = node.children().map { nodeToStructure(it) }
            )
            is ListItem -> MarkdownStructure(
                type = "list_item",
                content = extractText(node),
                children = node.children().map { nodeToStructure(it) }
            )
            else -> MarkdownStructure(
                type = node.javaClass.simpleName.lowercase(),
                content = extractText(node),
                children = node.children().map { nodeToStructure(it) }
            )
        }
    }

    return MarkdownStructure(
        type = "document",
        content = null,
        children = document.children().map { nodeToStructure(it) }
    )
}

fun extractText(node: Node): String {
    val sb = StringBuilder()
    node.accept(object : AbstractVisitor() {
        override fun visit(text: org.commonmark.node.Text) {
            sb.append(text.literal)
        }
    })
    return sb.toString()
}

private fun Node.children(): List<Node> {
    val children = mutableListOf<Node>()
    var child = firstChild
    while (child != null) {
        children.add(child)
        child = child.next
    }
    return children
}
```

Room + LIKE-based JSON search (no JSON operators):

```kotlin
@Dao
interface DocumentEntityDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(document: DocumentEntity): Long

    @Query("SELECT * FROM documents WHERE id = :id")
    suspend fun getDocumentById(id: Long): DocumentEntity?

    // Example of naive JSON search; for production use FTS or dedicated columns
    @Query("SELECT * FROM documents WHERE structureJson LIKE :pattern")
    suspend fun searchByStructure(pattern: String): List<DocumentEntity>
}

@Database(entities = [DocumentEntity::class], version = 1)
abstract class AppDatabase : RoomDatabase() {
    abstract fun documentEntityDao(): DocumentEntityDao
}

class MarkdownStructureRepository(
    private val documentDao: DocumentEntityDao,
    private val gson: Gson
) {
    suspend fun saveMarkdown(title: String, markdown: String): Long {
        val structure = parseMarkdownToStructure(markdown)
        val structureJson = gson.toJson(structure)

        val document = DocumentEntity(
            title = title,
            markdownRaw = markdown,
            structureJson = structureJson
        )
        return documentDao.insert(document)
    }

    suspend fun getDocument(id: Long): Pair<String, MarkdownStructure>? {
        val doc = documentDao.getDocumentById(id) ?: return null
        val structure = gson.fromJson(doc.structureJson, MarkdownStructure::class.java)
        return doc.markdownRaw to structure
    }

    // Naive example: LIKE-based heading search over JSON string
    suspend fun searchHeadings(query: String): List<DocumentEntity> {
        val pattern = "%\"type\":\"heading\"%" + query + "%"
        return documentDao.searchByStructure(pattern)
    }
}
```

Note: JSON LIKE search in SQLite on Android is fragile and inefficient because there are no native JSON operators by default. For serious use cases, prefer:
- normalized tables for key structural elements (e.g., headings), and/or
- FTS (Full-Text Search) for content.

Pros:
- Explicit Markdown structure representation
- Suitable for advanced search and analysis
- Can store both raw Markdown and structure

Cons:
- More complex implementation
- Larger storage
- Parsing/serialization overhead
- JSON-based search is limited; better to normalize important fields

---

### Approach 3: Convert to HTML and Store HTML

Best for: Display-focused apps, especially when using WebView.

```kotlin
import org.commonmark.parser.Parser
import org.commonmark.renderer.html.HtmlRenderer

@Entity(tableName = "documents")
data class DocumentHtmlEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0L,
    val title: String,
    val markdownRaw: String,
    val htmlContent: String,  // Rendered HTML
    val createdAt: Long = System.currentTimeMillis()
)

fun markdownToHtml(markdown: String): String {
    val parser = Parser.builder().build()
    val document = parser.parse(markdown)
    val renderer = HtmlRenderer.builder().build()
    return renderer.render(document)
}

@Dao
interface DocumentHtmlDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(document: DocumentHtmlEntity): Long

    @Query("SELECT * FROM documents WHERE id = :id")
    suspend fun getDocumentById(id: Long): DocumentHtmlEntity?
}

class MarkdownHtmlRepository(private val documentDao: DocumentHtmlDao) {
    suspend fun saveDocument(title: String, markdown: String): Long {
        val html = markdownToHtml(markdown)
        val document = DocumentHtmlEntity(
            title = title,
            markdownRaw = markdown,
            htmlContent = html
        )
        return documentDao.insert(document)
    }
}
```

Display via WebView (simplified):

```kotlin
class MarkdownViewerFragment : Fragment() {
    private val viewModel: MarkdownViewModel by viewModels()

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)

        viewModel.document.observe(viewLifecycleOwner) { doc ->
            webView.loadDataWithBaseURL(
                null,
                doc.htmlContent,
                "text/html",
                "UTF-8",
                null
            )
        }
    }
}
```

Pros:
- Fast rendering (HTML is pre-generated)
- Easy WebView integration
- CSS styling support

Cons:
- Editing requires using the original Markdown
- Typically larger than raw Markdown
- Loses explicit Markdown AST information

---

### Approach 4: File Storage

Best for: Large documents, import/export, interoperability with external tools.

Frequently combined with Room: DB stores metadata and indexes, while .md files live on the file system.

```kotlin
class MarkdownFileManager(private val context: Context) {

    // Save to internal storage
    fun saveToInternalStorage(filename: String, markdown: String) {
        val file = File(context.filesDir, "$filename.md")
        file.writeText(markdown)
    }

    // Read from internal storage
    fun readFromInternalStorage(filename: String): String {
        val file = File(context.filesDir, "$filename.md")
        return if (file.exists()) file.readText() else ""
    }

    // Save to app-specific external storage (no explicit READ/WRITE permissions)
    fun saveToExternalAppDirectory(filename: String, markdown: String) {
        val dir = context.getExternalFilesDir(null) ?: context.filesDir
        val file = File(dir, "$filename.md")
        file.writeText(markdown)
    }

    // Export to Downloads via MediaStore (simplified)
    fun exportToDownloads(filename: String, markdown: String) {
        val contentValues = ContentValues().apply {
            put(MediaStore.Downloads.DISPLAY_NAME, "$filename.md")
            put(MediaStore.Downloads.MIME_TYPE, "text/markdown")
            put(MediaStore.Downloads.IS_PENDING, 1)
        }

        val resolver = context.contentResolver
        val uri = resolver.insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, contentValues)

        uri?.let { outUri ->
            resolver.openOutputStream(outUri)?.use { output ->
                output.write(markdown.toByteArray())
            }

            contentValues.clear()
            contentValues.put(MediaStore.Downloads.IS_PENDING, 0)
            resolver.update(outUri, contentValues, null, null)
        }
    }

    // List all Markdown files in internal storage
    fun listMarkdownFiles(): List<String> {
        return context.filesDir.listFiles { file ->
            file.extension == "md"
        }?.map { it.nameWithoutExtension } ?: emptyList()
    }
}
```

Note: For public external storage on modern Android, follow scoped storage rules and manage permissions correctly.

Pros:
- Standard .md files
- Easy export/import
- Can be edited with external tools
- Works well with version control

Cons:
- Without indexing, structural/content queries are hard
- Need to manage files and sync with DB

---

### Hybrid Approach (Recommended)

Combine options: Room for indexing/metadata and Markdown storage, HTML cache for fast rendering, plus optional file backup.

```kotlin
@Entity(tableName = "documents")
data class HybridDocument(
    @PrimaryKey(autoGenerate = true)
    val id: Long = 0L,
    val title: String,
    val markdownContent: String,     // Raw Markdown (editable)
    val htmlCache: String? = null,   // Cached HTML
    val filePath: String? = null,    // Optional file backup path
    val tags: String? = null,        // Extracted from headings
    val wordCount: Int = 0,
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis()
)

@Dao
interface HybridDocumentDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(document: HybridDocument): Long
}

class HybridMarkdownRepository(
    private val dao: HybridDocumentDao,
    private val fileManager: MarkdownFileManager
) {
    suspend fun saveDocument(title: String, markdown: String): Long {
        val html = markdownToHtml(markdown)
        val tags = extractTags(markdown)
        val wordCount = markdown.split("\\s+".toRegex())
            .filter { it.isNotBlank() }
            .size

        // In real code you would typically insert first, get id, then compute and persist filePath
        val tempDocument = HybridDocument(
            title = title,
            markdownContent = markdown,
            htmlCache = html,
            tags = tags.joinToString(","),
            wordCount = wordCount
        )
        val id = dao.insert(tempDocument)

        val filename = "doc_$id"
        fileManager.saveToInternalStorage(filename, markdown)
        val filePath = "${'$'}{filename}.md"

        val finalDocument = tempDocument.copy(
            id = id,
            filePath = filePath
        )
        dao.insert(finalDocument)

        return id
    }

    private fun extractTags(markdown: String): List<String> {
        val headingRegex = """^#{1,6}\s+(.+)$""".toRegex(RegexOption.MULTILINE)
        return headingRegex.findAll(markdown)
            .map { it.groupValues[1].trim() }
            .toList()
    }
}
```

This approach lets you:
- keep editable Markdown source;
- render quickly via cached HTML;
- derive simple metadata (headings as tags, word count, etc.);
- extend with normalized structure tables or FTS when needed.

---

## Summary (EN)

Four main approaches on Android (often combined):

1. Plain Markdown in Room — simplest and a solid default.
2. AST/JSON + Room — for complex structural search and analysis.
3. HTML + Room — for fast display and WebView integration.
4. Files (.md) — for large documents and external tooling; DB stores index/metadata.

Recommended:
- Simple app: store raw Markdown in Room.
- Complex app: hybrid — raw Markdown + HTML cache + metadata (and/or normalized structure, FTS).
- Very large docs/export: store content in files, keep only index/metadata in Room.

---

## Дополнительные Вопросы (RU)

- [[q-database-encryption-android--android--medium]]
- [[q-fragments-vs-activity--android--medium]]
- [[q-mvi-handle-one-time-events--android--hard]]

## Follow-ups

- [[q-database-encryption-android--android--medium]]
- [[q-fragments-vs-activity--android--medium]]
- [[q-mvi-handle-one-time-events--android--hard]]

---

## Ссылки (RU)

- [Room Database](https://developer.android.com/training/data-storage/room)

## References

- [Room Database](https://developer.android.com/training/data-storage/room)

---

## Связанные Вопросы (RU)

### Базовые Концепции

- [[c-android]]
- [[c-database-design]]

### Предпосылки (проще)

- [[q-sharedpreferences-commit-vs-apply--android--easy]] - Storage
- [[q-sharedpreferences-definition--android--easy]] - Storage

### Связанные (средний уровень)

- [[q-database-optimization-android--android--medium]] - Storage
- [[q-room-database-migrations--android--medium]] - Storage
- [[q-database-encryption-android--android--medium]] - Storage
- [[q-room-code-generation-timing--android--medium]] - Storage
- [[q-room-transactions-dao--android--medium]] - Storage

### Продвинутые (сложнее)

- [[q-room-fts-full-text-search--android--hard]] - Storage

## Related Questions

### Prerequisites / Concepts

- [[c-android]]
- [[c-database-design]]

### Prerequisites (Easier)

- [[q-sharedpreferences-commit-vs-apply--android--easy]] - Storage
- [[q-sharedpreferences-definition--android--easy]] - Storage

### Related (Medium)

- [[q-database-optimization-android--android--medium]] - Storage
- [[q-room-database-migrations--android--medium]] - Storage
- [[q-database-encryption-android--android--medium]] - Storage
- [[q-room-code-generation-timing--android--medium]] - Storage
- [[q-room-transactions-dao--android--medium]] - Storage

### Advanced (Harder)

- [[q-room-fts-full-text-search--android--hard]] - Storage
