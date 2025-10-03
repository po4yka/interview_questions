# Import Strategy for 891 Q&A Pairs

**Source**: channels.db (easy_kotlin table)
**Target**: Obsidian Interview Vault
**Total Q&As**: 891

---

## Phase 1: Preparation ✅

- [x] Analyze database themes
- [x] Create theme → topic mapping (DB-MAPPING.md)
- [x] Create machine-readable mapping (theme-mapping.json)
- [x] Design import strategy (this document)

---

## Phase 2: Testing (Sample Batch)

### Sample Selection Strategy

**Batch size**: 15-20 Q&As covering diverse topics

**Selection criteria**:
1. Pick 2-3 from each major topic:
   - Android UI (2-3)
   - Android Lifecycle (2-3)
   - Kotlin Basics (2-3)
   - Kotlin Coroutines (2-3)
   - Android Architecture (2)
   - Data Structures (1)
   - Databases (1)
   - Other topics (2-3)

2. Include variety of tag patterns:
   - Simple tags: 1-2 tags
   - Complex tags: 3-5 tags
   - Different tag types (lifecycle, UI, coroutines, etc.)

3. Include variety of answer lengths:
   - Short answers (< 500 chars)
   - Medium answers (500-1500 chars)
   - Long answers (> 1500 chars)

**Sample extraction**:
```sql
-- Android UI sample
SELECT * FROM easy_kotlin WHERE theme = 'Android UI' LIMIT 3;

-- Kotlin Basics sample
SELECT * FROM easy_kotlin WHERE theme = 'Basic Kotlin' LIMIT 3;

-- Kotlin Coroutines sample
SELECT * FROM easy_kotlin WHERE theme = 'Kotlin Coroutines' LIMIT 3;

-- Android Lifecycle sample
SELECT * FROM easy_kotlin WHERE theme = 'Android Lifecycle' LIMIT 2;

-- Architecture sample
SELECT * FROM easy_kotlin WHERE theme = 'Android Architecture' LIMIT 2;

-- Mixed other topics
SELECT * FROM easy_kotlin WHERE theme IN (
  'Data Structures', 'Database Concepts', 'Git Basics', 'Android Testing'
) LIMIT 5;
```

### Translation Approach

**Strategy**: AI-assisted translation with human review

**Tools**:
1. **Primary**: Claude/GPT-4 for translation
2. **Validation**: DeepL for comparison
3. **Review**: Human verification of technical terms

**Process**:
1. Extract Russian question + answer
2. Translate to English using AI
3. Preserve technical terms (CoroutineContext, Activity, etc.)
4. Maintain code examples as-is
5. Review for accuracy

**Quality checks**:
- Technical terms match (coroutines = корутины)
- Code examples identical
- Formatting preserved (bullets, code blocks)
- Links/references preserved

### Difficulty Assignment

**Heuristics**:

1. **Easy**:
   - Single-concept questions
   - Simple definitions
   - Basic "what is X" questions
   - Short answers (< 500 chars)

2. **Medium** (default):
   - Multi-concept explanations
   - Comparisons (A vs B)
   - Lifecycle methods with examples
   - Medium-length answers (500-1500 chars)

3. **Hard**:
   - Architecture decisions
   - Performance optimization
   - Complex trade-offs
   - Multi-part answers with code
   - Long answers (> 1500 chars)

**Manual review**: Adjust during sample import based on complexity

### Question Kind Detection

**Rules**:

1. **coding**:
   - Question asks to "implement", "write code", "show example"
   - Answer contains significant code blocks
   - Tags include algorithms, leetcode

2. **android**:
   - Topic = android
   - Android-specific question (Activity, Fragment, Compose, etc.)
   - Most Android Q&As use this

3. **theory**:
   - Question asks "what is", "explain", "difference between"
   - Conceptual explanation
   - No code required
   - Most Kotlin basics, CS fundamentals

4. **system-design**:
   - Architecture patterns
   - High-level design discussions
   - Scalability, trade-offs

**Default for Android**: `question_kind: android`
**Default for others**: `question_kind: theory`

---

## Phase 3: Full Import

### Batching Strategy

**Approach**: Process in topic-based batches

**Benefits**:
- Easier to review by topic
- Can create MOCs incrementally
- Easier to track progress
- Can pause/resume by topic

**Batch plan**:

1. **Batch 1**: Android UI (~110 Q&As)
2. **Batch 2**: Basic Kotlin (~111 Q&As)
3. **Batch 3**: Android Lifecycle (~70 Q&As)
4. **Batch 4**: Kotlin Coroutines (~55 Q&As)
5. **Batch 5**: Kotlin Basics (~40 Q&As)
6. **Batch 6**: Kotlin Collections (~30 Q&As)
7. **Batch 7**: Kotlin Language Features (~28 Q&As)
8. **Batch 8**: Android Architecture (~35 Q&As)
9. **Batch 9**: Mixed (remaining ~400 Q&As)
   - Process by smaller themes
   - Group similar topics together

**Progress tracking**:
- Log each processed message_id
- Track success/failures
- Generate progress report after each batch

### Translation Strategy for Full Import

**Options**:

#### Option A: Pre-translate all (Recommended)
1. Extract all Q&As to JSON
2. Batch translate using AI API
3. Human review sample (~5% random)
4. Generate notes from translated content

**Pros**: Faster, consistent, can parallelize
**Cons**: Upfront cost, less control per-item

#### Option B: Translate on-the-fly
1. Translate during note generation
2. Review each translation before writing

**Pros**: More control, can adjust
**Cons**: Slower, harder to batch

#### Option C: Hybrid (Recommended for Phase 3)
1. Pre-translate in batches (50-100 at a time)
2. Quick human review of batch
3. Generate notes from batch
4. Move to next batch

**Pros**: Balance of speed and quality
**Cons**: Requires multiple steps

**Decision**: Use Option C (Hybrid) for full import

### Filename Generation

**Pattern**: `q-<slug>--<topic>--<difficulty>.md`

**Slug generation**:
1. Take first 5-8 words of Russian question
2. Transliterate to English or use English translation
3. Convert to kebab-case
4. Ensure uniqueness (append -2, -3 if collision)

**Examples**:
- "Какие есть методы жизненного цикла Activity" → `q-activity-lifecycle-methods--android--medium.md`
- "Для чего нужен data class" → `q-data-class-purpose--programming-languages--easy.md`
- "Что является сущностью корутин контекста" → `q-coroutine-context-entity--concurrency--medium.md`

**Collision handling**:
- Check if filename exists
- Append message_id if collision: `q-activity-lifecycle-methods-8--android--medium.md`

### ID Generation

**Pattern**: `YYYYMMDD-HHmmss` (timestamp-based)

**Strategy**:
- Use current timestamp for each note
- Ensures uniqueness
- Sequential IDs for import batch
- Increment by 1 second for each note to avoid collisions

**Example**:
```
20251003-140000  (first note)
20251003-140001  (second note)
20251003-140002  (third note)
...
```

### Tag Processing

**DB tags → Vault tags**:

1. **Parse JSON array**: `["coroutines", "CoroutineContext"]`
2. **Normalize**:
   - Lowercase where appropriate
   - Keep Android-specific capitalization (Activity, ViewModel)
   - Convert to kebab-case if needed
3. **Add namespace tags**:
   - `difficulty/<level>`
   - `lang/ru` (since originals are Russian)
   - `platform/android` (for Android Q&As)
4. **Add source tag**: `easy_kotlin` (to track origin)
5. **Android subtopic tags**: Add `android/<subtopic>` based on mapping

**Example transformation**:
```json
// DB
["coroutines", "suspend functions"]

// Vault
[
  "coroutines",
  "suspend-functions",
  "difficulty/medium",
  "lang/ru",
  "easy_kotlin",
  "android/coroutines"  // if Android-related
]
```

### Android Subtopic Detection

**Algorithm**:

1. Check if `topic == "android"`
2. Analyze DB theme and tags:
   ```python
   def detect_android_subtopics(theme, tags):
       subtopics = []

       # UI-related
       if any(kw in theme.lower() for kw in ['ui', 'compose', 'view', 'widget']):
           if 'compose' in theme.lower():
               subtopics.append('ui-compose')
           else:
               subtopics.append('ui-views')

       # Lifecycle
       if any(kw in theme.lower() for kw in ['lifecycle', 'activity', 'fragment']):
           if 'activity' in theme.lower() or 'activity' in tags:
               subtopics.append('activity')
           if 'fragment' in theme.lower() or 'fragment' in tags:
               subtopics.append('fragment')
           if 'lifecycle' in theme.lower():
               subtopics.append('lifecycle')

       # Coroutines
       if 'coroutines' in tags or 'coroutines' in theme.lower():
           subtopics.append('coroutines')

       # Architecture
       if any(kw in theme.lower() for kw in ['mvvm', 'mvi', 'architecture']):
           if 'mvvm' in theme.lower():
               subtopics.append('architecture-mvvm')
           elif 'mvi' in theme.lower():
               subtopics.append('architecture-mvi')
           else:
               subtopics.append('architecture-clean')

       # DI
       if any(kw in str(tags).lower() for kw in ['dagger', 'hilt', 'dependency injection']):
           subtopics.append('di-hilt')

       # Networking
       if 'network' in theme.lower():
           subtopics.append('networking-http')

       # Storage
       if any(kw in theme.lower() for kw in ['storage', 'database', 'room']):
           subtopics.append('room')

       # Performance
       if 'performance' in theme.lower():
           if 'memory' in theme.lower():
               subtopics.append('performance-memory')
           else:
               subtopics.append('performance-startup')

       # Testing
       if 'testing' in theme.lower():
           subtopics.append('testing-unit')

       # Build
       if any(kw in theme.lower() for kw in ['build', 'gradle']):
           subtopics.append('gradle')

       # Default if none found
       if not subtopics:
           subtopics.append('lifecycle')  # Safe default for Android

       return subtopics[:3]  # Max 3 subtopics
   ```

### Link Generation

**Strategy**: Create skeleton links, populate later

**MOC links**:
- `moc: moc-android` for Android Q&As
- `moc: moc-kotlin` for Kotlin Q&As (create this MOC)
- `moc: moc-concurrency` for concurrency Q&As

**Concept links**:
- Parse DB tags for concept keywords
- Create links to concepts (without wikilink brackets in YAML)
- Add to `related` field as list
- **Note**: Concepts may not exist yet, create them later

**Related question links**:
- Initially empty or add a few
- Can be populated in post-processing by finding questions with similar tags

**Example**:
```yaml
moc: moc-android
related:
  - c-activity-lifecycle
  - c-fragment
  - c-lifecycle-methods
```

---

## Phase 4: Post-Import Processing

### Validation

**Run validation script** on all imported notes:

```python
def validate_note(note_path):
    errors = []

    # Check YAML completeness
    if not yaml.topic:
        errors.append("Missing topic")
    if yaml.topic not in VALID_TOPICS:
        errors.append(f"Invalid topic: {yaml.topic}")

    # Check bilingual content
    if "# Question (EN)" not in content:
        errors.append("Missing EN question")
    if "# Вопрос (RU)" not in content:
        errors.append("Missing RU question")

    # Check tags
    for tag in yaml.tags:
        if any(ord(c) > 127 for c in tag):  # Non-ASCII
            errors.append(f"Non-English tag: {tag}")

    # Check Android subtopic mirroring
    if yaml.topic == "android":
        for subtopic in yaml.subtopics:
            expected_tag = f"android/{subtopic}"
            if expected_tag not in yaml.tags:
                errors.append(f"Missing tag: {expected_tag}")

    # Check links
    if not yaml.moc:
        errors.append("Missing MOC link")

    return errors
```

**Validation report**:
- Total notes: 891
- Valid: X
- Invalid: Y
- Common errors:
  - Missing EN translations: Z
  - Invalid topics: A
  - Missing tags: B
  - etc.

### MOC Creation

**Create/Update MOCs**:

1. **moc-android.md** (~450 Q&As)
   - Sections by subtopic (UI, Lifecycle, Architecture, etc.)
   - Dataview queries for each section

2. **moc-kotlin.md** (create new, ~280 Q&As)
   - Sections: Basics, Collections, Coroutines, Advanced
   - Dataview queries

3. **moc-concurrency.md** (create new, ~80 Q&As)
   - Coroutines, Threading, RxJava

4. **Other MOCs** as needed

**Dataview query examples**:
```dataview
TABLE difficulty, subtopics, status
FROM "40-Android"
WHERE contains(tags, "android/lifecycle")
SORT difficulty ASC, file.name ASC
```

### Concept Note Creation

**Priority concepts** (based on tag frequency):

1. `c-coroutines.md` (57 occurrences)
2. `c-collections.md` (38)
3. `c-null-safety.md` (36)
4. `c-inheritance.md` (31)
5. `c-activity-lifecycle.md` (29)
6. `c-data-class.md` (28)
7. `c-fragment.md` (25)
8. `c-activity.md` (25)
9. `c-data-structures.md` (25)
10. `c-memory-management.md` (23)

**Create top 20-30 concepts** to support Q&As

---

## Technical Implementation

### Tools & Dependencies

**Python script** requirements:
- `sqlite3` - DB access
- `pyyaml` - YAML generation
- `json` - JSON parsing
- `transliterate` - Russian → Latin transliteration
- `openai` / `anthropic` - AI translation API
- `python-slugify` - Slug generation

**Directory structure**:
```
scripts/
├── import_qna.py          # Main import script
├── translate_batch.py     # Batch translation
├── validate_notes.py      # Validation script
├── generate_mocs.py       # MOC generation
├── utils/
│   ├── yaml_gen.py        # YAML generation
│   ├── filename_gen.py    # Filename generation
│   ├── topic_mapper.py    # Theme → Topic mapping
│   └── translator.py      # AI translation wrapper
└── config.json            # Configuration
```

### Configuration

**config.json**:
```json
{
  "database_path": "channels.db",
  "vault_path": "/Users/npochaev/Documents/InterviewQuestions",
  "mapping_file": "00-Administration/theme-mapping.json",
  "translation_api": "anthropic",
  "translation_model": "claude-3-5-sonnet-20241022",
  "batch_size": 50,
  "default_difficulty": "medium",
  "default_status": "draft",
  "source_tag": "easy_kotlin",
  "log_file": "import.log"
}
```

### Error Handling

**Graceful failures**:
1. Log all errors to `import.log`
2. Continue processing on non-critical errors
3. Skip problematic records, log message_id
4. Generate error report at end

**Common error scenarios**:
- Translation API timeout → retry 3 times
- Invalid theme → log, use default topic `cs`
- File already exists → skip or append -2
- Missing data → log, use defaults

### Progress Tracking

**Log format**:
```
2025-10-03 14:00:00 [INFO] Starting import batch 1 (Android UI)
2025-10-03 14:00:01 [INFO] Processing message_id=8 (Android Lifecycle)
2025-10-03 14:00:02 [SUCCESS] Created: q-activity-lifecycle-methods--android--medium.md
2025-10-03 14:00:03 [ERROR] Translation failed for message_id=123, retrying...
2025-10-03 14:00:05 [SUCCESS] Batch 1 complete: 110/110 processed, 108 success, 2 errors
```

**Progress file**: `import_progress.json`
```json
{
  "last_processed_id": 456,
  "total_processed": 450,
  "total_success": 445,
  "total_errors": 5,
  "current_batch": "Android UI",
  "batches_completed": ["Android UI", "Basic Kotlin"],
  "error_ids": [123, 456]
}
```

---

## Timeline Estimate

**Phase 2 (Testing)**: 2-4 hours
- Sample extraction: 30 min
- Translation: 1-2 hours
- Note generation: 30 min
- Review & fixes: 1 hour

**Phase 3 (Full Import)**: 8-12 hours
- Script development: 3-4 hours
- Batch translation: 3-4 hours (API calls)
- Note generation: 1-2 hours
- Validation & fixes: 2-3 hours

**Phase 4 (Post-processing)**: 3-4 hours
- MOC creation: 1-2 hours
- Concept creation: 1-2 hours
- Final validation: 1 hour

**Total estimate**: 13-20 hours

---

## Quality Metrics

**Success criteria**:

1. **Coverage**: ≥ 95% of 891 Q&As imported
2. **Validation**: ≥ 98% pass validation checklist
3. **Translation quality**: Sample review shows ≥ 90% accuracy
4. **Bilingual**: 100% have both EN and RU sections
5. **Tags**: 100% have English-only tags
6. **Links**: 100% have MOC link, ≥ 80% have concept links
7. **Android subtopics**: 100% Android notes have subtopics + mirrored tags

**Metrics to track**:
- Notes created: X / 891
- Validation pass rate: Y%
- Translation errors: Z
- Tag issues: A
- Link coverage: B%

---

## Next Steps

1. ✅ Complete Phase 1 (Preparation)
2. ⏭️ Extract sample batch (15-20 Q&As)
3. ⏭️ Translate sample batch
4. ⏭️ Generate sample notes
5. ⏭️ Review with user
6. ⏭️ Build import script
7. ⏭️ Run full import
8. ⏭️ Validate & create MOCs

---

**Document version**: 1.0
**Last updated**: 2025-10-03
