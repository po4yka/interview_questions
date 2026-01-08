---\
name: url-ingestor
description: >
  Generate Q&A notes from web articles and documentation. Fetches and parses URL
  content, extracts key concepts and interview questions, generates bilingual Q&A
  structure, auto-classifies topic and difficulty, and creates draft notes with
  proper YAML. Supports batch URL processing for content sprints.
---\

# URL Ingestor

## Purpose

Generate interview Q&A notes from web content:

1. **URL Fetching**: Retrieve content from articles/documentation
2. **Content Extraction**: Parse relevant text and code
3. **Q&A Generation**: Create interview questions from content
4. **Bilingual Support**: Generate both EN and RU versions
5. **Auto-Classification**: Determine topic, subtopics, difficulty
6. **Batch Processing**: Handle multiple URLs in one session

## When to Use

Activate this skill when user requests:
- "Create questions from [URL]"
- "Ingest this article"
- "Generate Q&As from documentation"
- "Import content from [URL]"
- "Batch ingest these URLs"
- During content sprints
- When expanding topic coverage

## Prerequisites

Required context:
- Valid URL(s) to process
- Target topic (or auto-detect)
- Vault structure knowledge
- TAXONOMY.md for classification

## Process

### Step 1: Fetch URL Content

Retrieve and parse web content:

```
1. Fetch URL using WebFetch tool
2. Extract main content (remove nav, ads, etc.)
3. Parse:
   - Headings and structure
   - Code blocks
   - Key concepts
   - Examples
4. Handle redirects if needed
```

### Step 2: Analyze Content

Understand the article:

```
Determine:
- Main topic (kotlin, android, algorithms, etc.)
- Subtopics covered
- Technical depth (difficulty level)
- Key concepts introduced
- Number of potential questions

Content types:
- Tutorial: Step-by-step guides
- Reference: API documentation
- Article: Explanatory content
- Guide: Best practices
```

### Step 3: Generate Questions

Create interview questions from content:

```
Question extraction strategies:

1. Concept questions:
   "What is [concept]?"
   "Explain [topic]"

2. Comparison questions:
   "What's the difference between A and B?"
   "When would you use A vs B?"

3. Implementation questions:
   "How would you implement [feature]?"
   "What's the best way to [task]?"

4. Problem-solving:
   "How do you handle [scenario]?"
   "What approach would you take for [problem]?"

5. Best practices:
   "What are best practices for [topic]?"
   "What should you avoid when [doing X]?"
```

### Step 4: Classify Each Question

Determine metadata:

```yaml
Topic selection:
- Match content to TAXONOMY.md topics
- Use context clues (Android docs → android topic)
- Consider code language (Kotlin code → kotlin topic)

Difficulty assessment:
- easy: Basic concepts, definitions
- medium: Implementation details, comparisons
- hard: Advanced patterns, edge cases, optimization

Subtopic mapping:
- Extract from content themes
- Match to controlled vocabulary
```

### Step 5: Create Bilingual Content

Generate EN and RU versions:

```
Process:
1. Original content (usually EN)
2. Generate Russian translation
3. Adapt examples if needed
4. Ensure technical accuracy in both

Note: Code examples stay same in both languages
```

### Step 6: Build Q&A Notes

Create complete notes:

```yaml
---
id: kotlin-XXX
title: [Generated Title EN] / [Generated Title RU]
aliases: [Alias EN, Alias RU]
topic: kotlin
subtopics: [extracted-subtopics]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [suggested-related]
created: 2025-11-15
updated: 2025-11-15
tags: [kotlin, subtopic, difficulty/medium]
sources: [source-url]
---

# Question (EN)
[Generated question]

# Вопрос (RU)
[Translated question]

## Answer (EN)
[Generated answer from article content]

## Ответ (RU)
[Translated answer]

## References
- [Source Article](original-url)
```

### Step 7: Review and Save

Present for review:

```
Generated questions:
1. [Question 1 title] - medium
2. [Question 2 title] - easy
3. [Question 3 title] - hard

Options:
- Accept all
- Review individually
- Modify before saving
- Reject and regenerate
```

## Examples

### Example 1: Single Article

**User**: "Create questions from https://kotlinlang.org/docs/coroutines-basics.html"

**Process**:
1. Fetch article content
2. Identify topic: kotlin/coroutines
3. Generate 5 questions
4. Create draft notes

**Output**:
```markdown
# URL Ingestion: Kotlin Coroutines Basics

Source: kotlinlang.org/docs/coroutines-basics.html
Topic detected: kotlin
Subtopics: coroutines, concurrency

## Generated Questions (5)

### 1. What is a coroutine? (easy)
File: q-what-is-coroutine--kotlin--easy.md
Content: Definition and basic concept

### 2. How do you launch a coroutine? (easy)
File: q-launch-coroutine--kotlin--easy.md
Content: launch builder usage

### 3. What is structured concurrency? (medium)
File: q-structured-concurrency--kotlin--medium.md
Content: Scope and lifecycle management

### 4. How do suspending functions work? (medium)
File: q-suspend-functions--kotlin--medium.md
Content: Suspension mechanics

### 5. What is a CoroutineScope? (medium)
File: q-coroutine-scope--kotlin--medium.md
Content: Scope purpose and usage

## Actions
- [x] 5 draft notes created in 70-Kotlin/
- [ ] Review and refine content
- [ ] Add related links
- [ ] Validate with obsidian-validator
```

### Example 2: Batch URL Processing

**User**: "Ingest these URLs for Android content:
- developer.android.com/guide/components/activities
- developer.android.com/guide/components/services
- developer.android.com/guide/components/broadcasts"

**Process**:
1. Fetch all 3 URLs
2. Generate questions from each
3. Create batch of notes

**Output**:
```markdown
# Batch URL Ingestion

URLs processed: 3
Questions generated: 12

## By Source

### Activities Guide (5 questions)
1. What is an Activity? (easy)
2. Explain the Activity lifecycle (medium)
3. How do you handle configuration changes? (medium)
4. What's the difference between onCreate and onStart? (easy)
5. How do you save Activity state? (medium)

### Services Guide (4 questions)
1. What is an Android Service? (easy)
2. Started vs Bound services (medium)
3. When to use foreground services? (medium)
4. Service lifecycle management (hard)

### Broadcasts Guide (3 questions)
1. What is a BroadcastReceiver? (easy)
2. Implicit vs explicit broadcasts (medium)
3. Local broadcasts vs system broadcasts (medium)

## Summary
- 12 notes created in 40-Android/
- All marked as draft
- Source URLs added to each note
```

### Example 3: Documentation Import

**User**: "Import `Room` database documentation"

**Process**:
1. Fetch `Room` documentation pages
2. Extract comprehensive content
3. Generate progressive questions

**Output**:
```markdown
# Room Documentation Import

Source: developer.android.com/training/data-storage/room
Pages processed: 5

## Generated Study Path

### Basics (4 easy questions)
- What is Room database?
- Room components overview
- Creating entities
- Basic DAO operations

### Intermediate (5 medium questions)
- Room relationships
- Type converters
- Migrations
- Flow integration
- Testing Room

### Advanced (3 hard questions)
- Complex queries
- Pre-populated databases
- Multi-process database access

## Notes Created: 12
Location: 40-Android/
Status: draft (ready for review)
```

### Example 4: Preview Without Creating

**User**: "Preview questions from this URL without creating files"

**Process**:
1. Fetch and analyze URL
2. Generate question previews
3. Show without saving

**Output**:
```markdown
# Preview: Questions from URL

Source: medium.com/article-about-compose

## Potential Questions

1. **What is Jetpack Compose?** (easy)
   - Would cover: Basic introduction, declarative UI concept
   - Difficulty: Foundational knowledge

2. **How does state work in Compose?** (medium)
   - Would cover: remember, mutableStateOf, recomposition
   - Difficulty: Core concept understanding

3. **Composable vs View comparison** (medium)
   - Would cover: Paradigm differences, migration
   - Difficulty: Requires both knowledge bases

4. **Compose performance optimization** (hard)
   - Would cover: Recomposition skipping, keys, derivedStateOf
   - Difficulty: Advanced optimization

## Preview Summary
- 4 questions could be generated
- Topic: android
- Subtopics: ui-compose, ui-state
- Quality: High (official docs)

Create these notes? [yes/no]
```

## Error Handling

### URL Not Accessible

**Problem**: Cannot fetch URL content

**Solution**:
1. Report fetch error
2. Suggest checking URL validity
3. Try alternative access methods
4. Allow manual content paste

### Insufficient Content

**Problem**: Article too short for multiple questions

**Solution**:
1. Generate what's possible
2. Note limited content
3. Suggest combining with related articles

### Non-Technical Content

**Problem**: URL contains non-technical content

**Solution**:
1. Detect content type
2. Warn if not suitable
3. Skip or adapt extraction

### Duplicate Content

**Problem**: Questions similar to existing notes

**Solution**:
1. Check against vault
2. Flag potential duplicates
3. Suggest alternatives or skip

## Integration with Other Skills

**Workflow: Content Sprint**
1. Gather URLs on topic
2. Run `url-ingestor` in batch
3. Review generated notes
4. Run `batch-validator`
5. Run `link-fixer` to connect
6. Polish with `obsidian-translator`

**Workflow: Topic Expansion**
1. Run `gap-analyzer` to find gaps
2. Find URLs covering gap topics
3. Run `url-ingestor` on URLs
4. Fill gaps systematically

## Ingestion Options

### Question Count
```
--max 5: Generate at most 5 questions
--min 3: Generate at least 3 questions
```

### Difficulty Filter
```
--difficulty medium: Only medium questions
--difficulty easy,medium: Easy and medium only
```

### Preview Mode
```
--preview: Show what would be generated
--dry-run: Analyze without creating files
```

### Auto-Confirm
```
--auto: Create notes without review prompt
```

## Quality Guidelines

### Good Sources
- Official documentation
- Reputable tech blogs
- Conference talks/slides
- Books (with permission)

### Avoid
- Outdated content
- Opinion pieces without facts
- Very short articles
- Content behind paywalls

## Notes

**Source Attribution**: Always includes source URL in notes.

**Draft Status**: All generated notes are draft by default.

**Review Required**: Human review recommended before publishing.

**Bilingual**: Generates both EN and RU content.

**Validation Ready**: Output compatible with obsidian-validator.

---

**Version**: 1.0
**Last Updated**: 2025-01-05
**Status**: Production Ready
