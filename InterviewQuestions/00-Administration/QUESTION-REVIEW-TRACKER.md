# Question Review Progress Tracker

**Purpose**: Track progress of reviewing and updating all Q&A questions in the vault.

**Created**: 2025-10-06
**Last Updated**: 2025-10-06

---

## Overview

This document tracks the systematic review of all questions to ensure:
- ✅ Proper YAML frontmatter
- ✅ Correct topic field
- ✅ Status field set to `draft`
- ✅ Both EN and RU content present
- ✅ Code examples work correctly
- ✅ Links to MOCs and concepts

---

## Progress by Folder

### 20-Algorithms

**Total Questions**: ~1
**Reviewed**: 0
**Progress**: 0%

- [ ] Review all algorithm questions
- [ ] Verify LeetCode links
- [ ] Ensure complexity analysis present

---

### 30-System-Design

**Total Questions**: TBD
**Reviewed**: 0
**Progress**: 0%

- [ ] Review all system design questions
- [ ] Verify diagrams and examples
- [ ] Check trade-offs discussed

---

### 40-Android

**Total Questions**: ~280+ (after CompSci reorganization)
**Reviewed**: 0
**Progress**: 0%

#### By Subtopic

**Jetpack Compose**
- [ ] Review Compose questions
- [ ] Verify code examples compile
- [ ] Check recomposition explanations

**Views & Layouts**
- [ ] Review View system questions
- [ ] Verify RecyclerView examples
- [ ] Check custom View examples

**Architecture**
- [ ] Review MVVM/MVI questions
- [ ] Verify ViewModel examples
- [ ] Check state management

**Lifecycle**
- [ ] Review Activity/Fragment lifecycle
- [ ] Verify lifecycle diagrams
- [ ] Check edge cases

**Data & Storage**
- [ ] Review Room questions
- [ ] Verify SQL examples
- [ ] Check DataStore usage

**Performance**
- [ ] Review performance questions
- [ ] Verify profiling examples
- [ ] Check optimization techniques

**Testing**
- [ ] Review testing questions
- [ ] Verify test examples
- [ ] Check mocking strategies

---

### 50-Backend

**Total Questions**: ~4
**Reviewed**: 0
**Progress**: 0%

- [ ] Review database questions
- [ ] Verify SQL examples
- [ ] Check API design questions

---

### 50-Behavioral

**Total Questions**: TBD
**Reviewed**: 0
**Progress**: 0%

- [ ] Review behavioral questions
- [ ] Check STAR method examples
- [ ] Verify answer frameworks

---

### 60-CompSci

**Total Questions**: ~90 (after reorganization - design patterns & architecture only)
**Reviewed**: 0
**Progress**: 0%

#### Design Patterns
- [ ] Review creational patterns (Factory, Singleton, Builder, etc.)
- [ ] Review structural patterns (Adapter, Decorator, Facade, etc.)
- [ ] Review behavioral patterns (Observer, Strategy, Command, etc.)
- [ ] Verify code examples
- [ ] Check UML diagrams

#### Architecture Patterns
- [ ] Review MVVM pattern
- [ ] Review MVI pattern
- [ ] Review MVP pattern
- [ ] Review Clean Architecture
- [ ] Verify implementation examples

#### OOP & SOLID
- [ ] Review OOP principles
- [ ] Review SOLID principles
- [ ] Verify practical examples

---

### 70-Kotlin

**Total Questions**: ~70+ (after CompSci reorganization)
**Reviewed**: 1
**Progress**: ~1%

**Reviewed Questions**:
- ✅ `q-associatewith-vs-associateby--kotlin--easy.md` (2025-10-06)

#### By Category

**Coroutines**
- [ ] Review coroutine basics
- [ ] Review Job vs SupervisorJob
- [ ] Review CoroutineContext
- [ ] Review coroutine builders
- [ ] Verify code examples run

**Flow**
- [ ] Review Flow basics
- [ ] Review Flow operators
- [ ] Review StateFlow vs SharedFlow
- [ ] Review backpressure
- [ ] Verify Flow examples

**Language Features**
- [x] Collections (associateWith, associateBy) ✅
- [ ] Data classes
- [ ] Sealed classes
- [ ] Object keyword
- [ ] Companion objects
- [ ] Extension functions
- [ ] Inline functions
- [ ] Generics
- [ ] Delegation

**Type System**
- [ ] Null safety
- [ ] Nothing type
- [ ] Type inference
- [ ] Variance

**Collections**
- [ ] List, Set, Map differences
- [ ] Collection operations
- [ ] Sequence vs Collection
- [ ] Array vs List

---

### 80-Tools

**Total Questions**: ~3+ (includes Git)
**Reviewed**: 0
**Progress**: 0%

**Git**
- [ ] Review merge vs rebase
- [ ] Review branching strategies
- [ ] Review conflict resolution

**Build Systems**
- [ ] Review Gradle questions
- [ ] Review dependency management
- [ ] Review build variants

**CI/CD**
- [ ] Review pipeline questions
- [ ] Review automation strategies

---

## Review Checklist (Per Question)

When reviewing each question, verify:

### YAML Frontmatter
- [ ] `id` field present and unique
- [ ] `title` includes both EN/RU
- [ ] `topic` field correct (matches folder)
- [ ] `subtopics` field present (1-3 values)
- [ ] `difficulty` field present (easy/medium/hard)
- [ ] `status` field set to `draft`
- [ ] `language_tags` includes `[en, ru]`
- [ ] `tags` field present and relevant
- [ ] `created` date present
- [ ] `updated` date present

### Content Quality
- [ ] Question (EN) section present and clear
- [ ] Вопрос (RU) section present and accurate translation
- [ ] Answer (EN) section comprehensive
- [ ] Ответ (RU) section comprehensive and accurate
- [ ] Code examples present (if applicable)
- [ ] Code examples compile/run (if applicable)
- [ ] Explanations clear and accurate
- [ ] Edge cases mentioned
- [ ] Trade-offs discussed

### Structure
- [ ] Uses `##` for question headings
- [ ] Uses `##` for answer headings
- [ ] Consistent formatting
- [ ] No extra blank lines before headings
- [ ] Proper code block syntax

### Links & References
- [ ] Links to related concepts
- [ ] Links to MOC present
- [ ] External references cited
- [ ] Related questions linked

---

## Review Status Workflow

Questions go through these stages:

1. **`draft`** (initial) — Not yet reviewed
2. **`reviewed`** — Content reviewed for accuracy
3. **`ready`** — Ready for interview prep use
4. **`retired`** — Deprecated/archived

---

## Dataview Queries for Tracking

### Count by Status
```dataview
TABLE
    length(rows) as "Count"
FROM "20-Algorithms" OR "40-Android" OR "50-Backend" OR "60-CompSci" OR "70-Kotlin" OR "80-Tools"
WHERE startswith(file.name, "q-")
GROUP BY status
```

### Draft Questions by Folder
```dataview
TABLE WITHOUT ID
    file.folder as "Folder",
    length(rows) as "Draft Questions"
FROM "20-Algorithms" OR "40-Android" OR "50-Backend" OR "60-CompSci" OR "70-Kotlin" OR "80-Tools"
WHERE status = "draft" AND startswith(file.name, "q-")
GROUP BY file.folder
```

### Recently Reviewed (Status Changed from Draft)
```dataview
TABLE WITHOUT ID
    file.link as "Question",
    file.folder as "Folder",
    difficulty as "Difficulty",
    updated as "Last Updated"
FROM "20-Algorithms" OR "40-Android" OR "50-Backend" OR "60-CompSci" OR "70-Kotlin" OR "80-Tools"
WHERE status != "draft" AND startswith(file.name, "q-")
SORT updated DESC
LIMIT 20
```

### Questions Missing Required Fields
```dataview
TABLE WITHOUT ID
    file.link as "Question",
    file.folder as "Folder"
FROM "20-Algorithms" OR "40-Android" OR "50-Backend" OR "60-CompSci" OR "70-Kotlin" OR "80-Tools"
WHERE startswith(file.name, "q-")
    AND (!topic OR !difficulty OR !status)
```

---

## Review Goals

### Short Term (This Week)
- [ ] Set all questions to `status: draft` (run script)
- [ ] Review 10 Kotlin questions
- [ ] Review 10 Android questions
- [ ] Fix any questions with missing frontmatter

### Medium Term (This Month)
- [ ] Review all Kotlin questions (promote to `reviewed`)
- [ ] Review all design pattern questions
- [ ] Review top 50 Android questions
- [ ] Create missing concept notes

### Long Term (3 Months)
- [ ] Review all questions in vault
- [ ] Promote high-quality questions to `ready`
- [ ] Create comprehensive MOC updates
- [ ] Add missing cross-links

---

## Quality Metrics

### Target Quality Levels

**By End of Week 1**:
- All questions have `status: draft`
- All questions have complete frontmatter
- No questions with missing EN or RU sections

**By End of Month 1**:
- 50+ questions promoted to `reviewed`
- All Kotlin questions reviewed
- All design patterns reviewed

**By End of Month 3**:
- 200+ questions promoted to `reviewed`
- 50+ questions promoted to `ready`
- All MOCs updated with reviewed questions

---

## Notes & Observations

### Common Issues Found

**Frontmatter Issues**:
- Many questions missing `status` field → Fixed with script
- Some questions missing `id` field
- Inconsistent `topic` values (programming-languages vs kotlin)

**Content Issues**:
- Some RU translations incomplete
- Code examples not always tested
- Missing complexity analysis in algorithm questions

**Organizational Issues**:
- Kotlin/Android questions were in CompSci folder → Moving to correct folders
- Git questions were in separate folder → Moved to Tools

### Review Priorities

1. **High Priority**: Questions used frequently for interviews
   - Kotlin coroutines
   - Android Compose
   - Design patterns
   - MVVM/MVI

2. **Medium Priority**: Important but less common
   - Advanced Kotlin features
   - Android performance
   - System design

3. **Low Priority**: Nice to have
   - Behavioral questions
   - Tool-specific questions

---

## Changelog

### 2025-10-06
- Created tracker document
- Reviewed first Kotlin question: `q-associatewith-vs-associateby--kotlin--easy.md`
- Set progress tracking structure
- Defined review workflow

---

**Next Review Session**: TBD
**Reviewer**: Self-review process
