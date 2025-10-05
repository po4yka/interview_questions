# Source Repositories Import Plan

**Created**: 2025-10-05
**Status**: Planning Phase

---

## Overview

Two GitHub repositories in `sources/` folder contain extensive Android and Kotlin interview questions:

1. **amitshekhariitbhu/android-interview-questions** - Single README with ~200+ Q&A topics
2. **Kirchhoff/Android-Interview-Questions** - 337 individual markdown files

**Goal**: Import high-quality questions into our vault using standardized bilingual template.

---

## Source Analysis

### Repository 1: amitshekhariitbhu-android-interview-questions

**Structure**: Single README.md (1,189 lines)
**Format**: Question-and-answer list with external links (YouTube, blog posts)
**Content**: ~200+ topics organized by category

**Categories**:
- ✅ Kotlin Coroutines (~15 topics)
- ✅ Kotlin Flow API (~15 topics)
- ✅ Kotlin (~40 topics)
- ✅ Android (~50+ topics)
- ✅ Android Libraries (~20 topics)
- ✅ Android Architecture (~15 topics)
- ✅ Design Patterns (~10 topics)
- ✅ Android System Design (~10 topics)
- ✅ Android Unit Testing (~15 topics)
- ✅ Jetpack Compose (~15 topics)
- ✅ Java (~10 topics)

**Characteristics**:
- 📹 Many link to YouTube videos (Amit Shekhar's channel)
- 📝 Most link to blog posts at outcomeschool.com
- ⚠️ Questions are just titles, answers are external
- ✅ High quality, well-organized topics
- ⚠️ Requires fetching external content for answers

**Example Questions**:
```
- What is an inline function in Kotlin?
- Launch vs Async in Kotlin Coroutines
- lateinit vs lazy in Kotlin
- What is a ViewModel and how is it useful?
- Difference between == and === in Kotlin
```

### Repository 2: Kirchhoff-Android-Interview-Questions

**Structure**: 337 individual markdown files in organized folders
**Format**: Self-contained Q&A with explanations and links
**Content**: Detailed answers with code examples

**Categories** (file count):
- 📱 **Android/**: 95 files
- 🔷 **Kotlin/**: 51 files
- ☕ **Java/**: 70 files
- 🏗️ **Patterns/**: 29 files
- 📚 **Libraries/**: 14 files
- 🧪 **Testing/**: 14 files
- 🔄 **Rx/**: 22 files
- 🌐 **General/**: 46 files

**Characteristics**:
- ✅ Self-contained files with complete answers
- ✅ Code examples included
- ✅ Links to official documentation
- ✅ Well-structured with headings
- ✅ Ready to adapt to our template
- ⚠️ English-only, need Russian translation

**Example Structure**:
```markdown
# Activity Lifecycle

[Detailed explanation...]

## onCreate()
[Details...]

## onStart()
[Details...]

# Links
[Official documentation]

# Further reading
[Stack Overflow, etc.]
```

---

## Import Strategy

### Phase 1: Kirchhoff Repository (Priority)
**Why first**: Self-contained answers, easier to process, no external fetching needed

#### Phase 1A: Android Questions (95 files)
- Extract from: `sources/Kirchhoff-Android-Interview-Questions/Android/`
- Target folder: `40-Android/`
- Topic: `android`
- Difficulty: Assess per question (mostly medium)

#### Phase 1B: Kotlin Questions (51 files)
- Extract from: `sources/Kirchhoff-Android-Interview-Questions/Kotlin/`
- Target folder: `70-Kotlin/`
- Topic: `kotlin`
- Difficulty: Assess per question (easy to medium)

#### Phase 1C: Patterns Questions (29 files)
- Extract from: `sources/Kirchhoff-Android-Interview-Questions/Patterns/`
- Target folder: `40-Android/` or `60-CompSci/` (assess per question)
- Topic: `architecture-patterns` or relevant
- Difficulty: Medium to hard

### Phase 2: Amit Shekhar Repository (Later)
**Why later**: Requires external content fetching, more manual work

- Parse README.md structure
- For each question, fetch content from linked blog/video
- Create notes with synthesized answers
- Priority: Kotlin Coroutines, Flow API, Jetpack Compose topics

---

## Template for Import

### Standard Note Structure

```yaml
---
id: YYYYMMDD-HHmmss
title: [EN Title] / [RU Заголовок]
aliases: []

# Classification
topic: android | kotlin | architecture-patterns
subtopics: []  # 1-3 relevant subtopics
question_kind: theory
difficulty: easy | medium | hard

# Language & provenance
original_language: en
language_tags: [en, ru]
source: https://github.com/Kirchhoff-Android-Interview-Questions
source_note: Kirchhoff Android Interview Questions repository

# Workflow & relations
status: reviewed
moc: moc-android | moc-kotlin
related: []

# Timestamps
created: 2025-10-05
updated: 2025-10-05

tags: [android, kotlin, ...]
---

# Question (EN)
> [Original question from source]

# Вопрос (RU)
> [Russian translation]

---

## Answer (EN)
[Original English answer from source, adapted]

## Ответ (RU)
[Russian translation of answer with examples]

---

## References
- [[related-concept]]
- [Original source link]

## Related Questions
- [[related-q1]]
- [[related-q2]]
```

### Mapping Rules

**Kirchhoff Files → Our Structure**:
- File title → Question title (EN)
- Content sections → Answer (EN)
- Need to add: Russian translation, difficulty assessment, subtopics, related links
- Need to generate: Proper filename slug, YAML metadata

**Difficulty Assessment Guidelines**:
- **Easy**: Basic definitions, simple concepts (e.g., "What is Activity?")
- **Medium**: Architecture patterns, lifecycle details, comparisons (e.g., "Fragment vs Activity lifecycle")
- **Hard**: Complex patterns, system design, optimization (e.g., "Custom View rendering pipeline")

---

## Deduplication Strategy

### Check Against Existing Notes

Before importing each question:

1. **Exact match check**: Search existing notes for same question title
2. **Topic overlap check**: Search for similar concepts in related notes
3. **Content similarity**: Avoid duplicating comprehensive notes we already have

**Example**: We already have comprehensive notes on:
- ✅ State hoisting in Compose
- ✅ LaunchedEffect vs DisposableEffect
- ✅ viewModelScope vs lifecycleScope
- ✅ Launch vs Async vs RunBlocking
- ✅ Dispatchers.IO vs Default
- ✅ Testing ViewModels with coroutines
- ✅ Testing Compose UI
- ✅ MVI Architecture

**Action**: Skip or merge if source question covers same topic with less depth

### Deduplication Process

```bash
# For each source file, check if similar note exists
# Search by keywords in title and tags
# If found: SKIP or MERGE additional info
# If new: IMPORT with full template
```

---

## Processing Workflow

### Automated Pipeline (Preferred)

```
1. Read source file
2. Extract title, content
3. Check for duplicates in vault
4. If duplicate: SKIP and log
5. If new:
   a. Generate YAML frontmatter
   b. Assess difficulty
   c. Choose subtopics
   d. Create English slug
   e. Translate to Russian (LLM)
   f. Format as bilingual note
   g. Save to target folder
   h. Update progress tracker
```

### Manual Review Points

- [ ] Difficulty assessment (verify AI suggestion)
- [ ] Subtopic selection (verify relevance)
- [ ] Russian translation quality (spot check)
- [ ] Code examples (verify correctness)
- [ ] Related links (add cross-references)
- [ ] Deduplication decisions (confirm skip/merge/import)

---

## Progress Tracking Structure

### Batch Processing by Category

**Phase 1A: Kirchhoff Android (95 files)**
```
[  0/95] Android questions processed
[  0/95] Duplicates skipped
[  0/95] New notes created
[  0/95] Manual reviews pending
```

**Phase 1B: Kirchhoff Kotlin (51 files)**
```
[  0/51] Kotlin questions processed
[  0/51] Duplicates skipped
[  0/51] New notes created
[  0/51] Manual reviews pending
```

**Phase 1C: Kirchhoff Patterns (29 files)**
```
[  0/29] Pattern questions processed
[  0/29] Duplicates skipped
[  0/29] New notes created
[  0/29] Manual reviews pending
```

**Total Phase 1**: 175 potential new notes

### Success Metrics

- **Import Rate**: Target 80%+ unique content (not duplicates)
- **Quality**: All notes follow template, have Russian translation
- **Coverage**: Fill gaps in existing Android/Kotlin coverage
- **Review Rate**: Manual review within 24 hours of batch import

---

## Implementation Steps

### Step 1: Deduplication Analysis
**Estimate**: 1-2 hours

```bash
# Create list of all source questions
# Compare against existing vault titles/topics
# Generate: skip_list.txt, import_list.txt
```

**Output**:
- `sources-analysis.md` - Detailed breakdown
- `skip_list.txt` - Questions to skip (duplicates)
- `import_list.txt` - Questions to import (new)

### Step 2: Batch Import Script
**Estimate**: 2-3 hours to develop

```python
# Script: import_source_questions.py
# Input: import_list.txt
# Process:
#   - Read source file
#   - Generate YAML frontmatter
#   - Translate to Russian (API call)
#   - Format bilingual note
#   - Save to target folder
# Output: Created notes + progress log
```

### Step 3: Manual Review
**Estimate**: 1 hour per 10 notes

- Review difficulty assignments
- Verify Russian translations
- Add cross-links to related notes
- Update MOCs if needed

### Step 4: Phase 1 Completion
**Estimate**: 1 week total

- Process all Kirchhoff questions
- Complete manual reviews
- Update vault statistics
- Create summary report

### Step 5: Phase 2 (Amit Shekhar Repo)
**Estimate**: 2-3 weeks

- Requires fetching external content
- More manual curation needed
- Lower priority, defer after Phase 1

---

## Risk Assessment

### High Risk
- ⚠️ **Duplicate content**: May waste effort on questions we already have
  - **Mitigation**: Thorough deduplication check before import

### Medium Risk
- ⚠️ **Translation quality**: AI translation may miss nuances
  - **Mitigation**: Manual review of all translations

- ⚠️ **Difficulty assignment**: Subjective, may be inconsistent
  - **Mitigation**: Clear guidelines, human review

### Low Risk
- ⚠️ **File naming conflicts**: Generated slugs may collide
  - **Mitigation**: Check for filename uniqueness, append counter if needed

---

## Next Actions

1. ✅ **Create this plan document** - DONE
2. ⏳ **Run deduplication analysis** - Create `sources-analysis.md`
3. ⏳ **Review analysis with user** - Confirm import strategy
4. ⏳ **Develop import script** - Python automation
5. ⏳ **Process Phase 1A** - Android questions first
6. ⏳ **Manual review batch 1** - Quality check
7. ⏳ **Continue with Phase 1B, 1C** - Kotlin and Patterns
8. ⏳ **Final summary report** - Update vault stats

---

## Decisions Made (2025-10-05)

✅ **User Approval Received**

1. **Deduplication threshold**: YES - Skip questions with >50% content overlap
2. **Translation approach**: AI translation for all content
3. **Initial status**: ALL start as `status: draft` for manual review
4. **Batch size**: Process in batches of **30 Q&A**
5. **Priority order**: Flexible - use any order
6. **Amit Shekhar repo**: Process in **PARALLEL** with Kirchhoff repo

---

## Updated Strategy

### Batch Processing
- **Batch Size**: 30 questions per batch
- **Kirchhoff Total**: 175 questions = 6 batches
  - Batch 1-4: 30 questions each (120 total)
  - Batch 5-6: 27-28 questions each (55 total)
- **Review Cycle**: After each batch, before proceeding to next

### Parallel Processing
- Process Kirchhoff AND Amit Shekhar repositories simultaneously
- Kirchhoff: Self-contained, easier automation
- Amit Shekhar: Manual curation, external fetching in background

---

**Ready to proceed with deduplication analysis.**
