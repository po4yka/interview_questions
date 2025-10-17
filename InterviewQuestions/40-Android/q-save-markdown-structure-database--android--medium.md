---
id: "20251015082237379"
title: "Save Markdown Structure Database / Сохранение структуры Markdown в базе данных"
topic: android
difficulty: medium
status: draft
created: 2025-10-15
tags: - android
  - android/data-storage
  - data-storage
  - database
  - markdown
  - room
  - serialization
  - storage
---
# Как бы ты сохранил структуру Markdown в базу данных/на диск?

**English**: How would you save Markdown structure to a database/disk?

## Answer (EN)
Saving Markdown structure depends on your application's goals. There are several approaches with different trade-offs.

## Approach 1: Store as Plain Text (Simplest)

**Best for:** Simple use cases, read-heavy applications, rich text editors

Store the raw Markdown text as a string in the database or file.

### Using Room Database

```kotlin
@Entity(tableName = "documents")
data class Document(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
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
    suspend fun getDocumentById(id: Int): Document?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(document: Document)

    @Update
    suspend fun update(document: Document)

    @Query("UPDATE documents SET markdownContent = :content, updatedAt = :timestamp WHERE id = :id")
    suspend fun updateContent(id: Int, content: String, timestamp: Long)
}
```

**Usage:**

```kotlin
class MarkdownRepository(private val documentDao: DocumentDao) {
    suspend fun saveDocument(title: String, markdown: String) {
        val document = Document(
            title = title,
            markdownContent = markdown
        )
        documentDao.insert(document)
    }

    suspend fun getDocument(id: Int): Document? {
        return documentDao.getDocumentById(id)
    }

    fun getAllDocuments(): Flow<List<Document>> {
        return documentDao.getAllDocuments()
    }
}
```

**Pros:**
- - Simple implementation
- - Preserves original formatting
- - Easy to edit
- - Small storage footprint

**Cons:**
- - Can't search by structure (headings, lists, etc.)
- - Can't query specific elements
- - Rendering required for display

---

## Approach 2: Parse to JSON and Store

**Best for:** Complex queries, structured search, content analysis

Parse Markdown into a structured format (AST - Abstract Syntax Tree), serialize to JSON, and store.

### Using Markdown Parser

```kotlin
// Gradle dependency
dependencies {
    implementation "org.commonmark:commonmark:0.21.0"
}
```

### Parse and Store

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
    val id: Int = 0,
    val title: String,
    val markdownRaw: String,        // Original Markdown
    val structureJson: String,      // Parsed structure as JSON
    val createdAt: Long = System.currentTimeMillis()
)

// Parse Markdown to structure
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
                content = extractText(node)
            )
        }
    }

    return nodeToStructure(document)
}

fun extractText(node: Node): String {
    val text = StringBuilder()
    node.accept(object : AbstractVisitor() {
        override fun visit(text: org.commonmark.node.Text) {
            this@StringBuilder.append(text.literal)
        }
    })
    return text.toString()
}

// Node extension
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

### Store with Room + TypeConverter

```kotlin
class Converters {
    private val gson = Gson()

    @TypeConverter
    fun fromMarkdownStructure(value: MarkdownStructure?): String? {
        return gson.toJson(value)
    }

    @TypeConverter
    fun toMarkdownStructure(value: String?): MarkdownStructure? {
        return value?.let { gson.fromJson(it, MarkdownStructure::class.java) }
    }
}

@Database(entities = [DocumentEntity::class], version = 1)
@TypeConverters(Converters::class)
abstract class AppDatabase : RoomDatabase() {
    abstract fun documentDao(): DocumentDao
}

// Repository
class MarkdownRepository(
    private val documentDao: DocumentDao,
    private val gson: Gson
) {
    suspend fun saveMarkdown(title: String, markdown: String) {
        val structure = parseMarkdownToStructure(markdown)
        val structureJson = gson.toJson(structure)

        val document = DocumentEntity(
            title = title,
            markdownRaw = markdown,
            structureJson = structureJson
        )
        documentDao.insert(document)
    }

    suspend fun getDocument(id: Int): Pair<String, MarkdownStructure>? {
        val doc = documentDao.getDocumentById(id) ?: return null
        val structure = gson.fromJson(doc.structureJson, MarkdownStructure::class.java)
        return doc.markdownRaw to structure
    }

    // Query by structure
    suspend fun searchHeadings(query: String): List<DocumentEntity> {
        // Search in structure JSON
        return documentDao.searchByStructure("%\"type\":\"heading\"%\"content\":\"$query\"%")
    }
}
```

**Pros:**
- - Can query structure
- - Content analysis
- - Search by element type
- - Preserves both raw and parsed

**Cons:**
- - More complex
- - Larger storage size
- - Parsing overhead

---

## Approach 3: Convert to HTML and Store

**Best for:** Web-based rendering, display-focused apps

```kotlin
import org.commonmark.parser.Parser
import org.commonmark.renderer.html.HtmlRenderer

@Entity(tableName = "documents")
data class DocumentEntity(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
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

class MarkdownRepository(private val documentDao: DocumentDao) {
    suspend fun saveDocument(title: String, markdown: String) {
        val html = markdownToHtml(markdown)
        val document = DocumentEntity(
            title = title,
            markdownRaw = markdown,
            htmlContent = html
        )
        documentDao.insert(document)
    }
}
```

**Display with WebView:**

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

**Pros:**
- - Fast rendering (pre-rendered)
- - Easy WebView display
- - CSS styling support

**Cons:**
- - Editing requires re-parsing
- - Larger storage
- - Loses Markdown structure

---

## Approach 4: File Storage

**Best for:** Large documents, export/import features

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

    // Save to external storage (scoped storage)
    fun saveToExternalStorage(filename: String, markdown: String) {
        val file = File(context.getExternalFilesDir(null), "$filename.md")
        file.writeText(markdown)
    }

    // Export to Downloads (MediaStore)
    fun exportToDownloads(context: Context, filename: String, markdown: String) {
        val contentValues = ContentValues().apply {
            put(MediaStore.Downloads.DISPLAY_NAME, "$filename.md")
            put(MediaStore.Downloads.MIME_TYPE, "text/markdown")
            put(MediaStore.Downloads.IS_PENDING, 1)
        }

        val uri = context.contentResolver.insert(
            MediaStore.Downloads.EXTERNAL_CONTENT_URI,
            contentValues
        )

        uri?.let {
            context.contentResolver.openOutputStream(it)?.use { output ->
                output.write(markdown.toByteArray())
            }

            contentValues.clear()
            contentValues.put(MediaStore.Downloads.IS_PENDING, 0)
            context.contentResolver.update(it, contentValues, null, null)
        }
    }

    // List all Markdown files
    fun listMarkdownFiles(): List<String> {
        return context.filesDir.listFiles { file ->
            file.extension == "md"
        }?.map { it.nameWithoutExtension } ?: emptyList()
    }
}
```

**Pros:**
- - Standard file format
- - Easy export/import
- - External editor support
- - Version control friendly

**Cons:**
- - No structured queries
- - File management overhead

---

## Hybrid Approach (Recommended)

Combine multiple approaches for best results:

```kotlin
@Entity(tableName = "documents")
data class Document(
    @PrimaryKey(autoGenerate = true)
    val id: Int = 0,
    val title: String,
    val markdownContent: String,     // Raw Markdown (editable)
    val htmlCache: String? = null,   // Cached HTML (fast display)
    val filePath: String? = null,    // Optional file backup
    val tags: String? = null,        // Extracted from headings
    val wordCount: Int = 0,
    val createdAt: Long = System.currentTimeMillis(),
    val updatedAt: Long = System.currentTimeMillis()
)

class MarkdownRepository(
    private val dao: DocumentDao,
    private val fileManager: MarkdownFileManager
) {
    suspend fun saveDocument(title: String, markdown: String) {
        // Parse and extract metadata
        val html = markdownToHtml(markdown)
        val tags = extractTags(markdown)
        val wordCount = markdown.split("\\s+".toRegex()).size

        // Save to database
        val document = Document(
            title = title,
            markdownContent = markdown,
            htmlCache = html,
            tags = tags.joinToString(","),
            wordCount = wordCount
        )
        val id = dao.insert(document)

        // Backup to file
        fileManager.saveToInternalStorage("doc_$id", markdown)
    }

    private fun extractTags(markdown: String): List<String> {
        // Extract from headings, hashtags, etc.
        val headingRegex = """^#{1,6}\s+(.+)$""".toRegex(RegexOption.MULTILINE)
        return headingRegex.findAll(markdown)
            .map { it.groupValues[1].trim() }
            .toList()
    }
}
```

---

## Summary

**Four main approaches:**

1. **Plain text** - Store raw Markdown (simplest, recommended for most cases)
2. **JSON structure** - Parse and store AST (for complex queries)
3. **HTML conversion** - Pre-render to HTML (for fast display)
4. **File storage** - Save as .md files (for export/import)

**Recommendation:**

- **Simple app**: Store raw Markdown in Room database
- **Complex app**: Hybrid - raw Markdown + HTML cache + metadata
- **Large documents**: File storage + database index

## Ответ (RU)
Сохранение структуры Markdown зависит от целей приложения. Варианты: хранить как обычный текст в базе или файле, парсить Markdown в JSON и сохранять структуру с помощью Room + TypeConverter или конвертировать Markdown в HTML и хранить. Примеры кода на Kotlin/Android с использованием SQLite, Room и файлового хранения.


---

## Related Questions

### Prerequisites (Easier)
- [[q-sharedpreferences-commit-vs-apply--android--easy]] - Storage
- [[q-sharedpreferences-definition--android--easy]] - Storage

### Related (Medium)
- [[q-database-optimization-android--android--medium]] - Storage
- [[q-room-database-migrations--room--medium]] - Storage
- [[q-database-encryption-android--android--medium]] - Storage
- [[q-room-code-generation-timing--android--medium]] - Storage
- [[q-room-transactions-dao--room--medium]] - Storage

### Advanced (Harder)
- [[q-room-fts-full-text-search--room--hard]] - Storage
