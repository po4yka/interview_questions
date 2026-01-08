---\
name: gap-analyzer
description: >
  Identify content gaps and suggest new Q&As to create. Analyzes coverage by topic
  and difficulty, finds topics with missing difficulty levels, suggests new Q&A
  titles based on gaps, compares against TAXONOMY.md categories, and generates
  prioritized content roadmaps for planning content sprints.
---\

# Gap Analyzer

## Purpose

Identify what's missing from the vault and suggest new content:

1. **Coverage Analysis**: `Map` existing content by topic and difficulty
2. **Gap Detection**: Find topics/subtopics with insufficient coverage
3. **Difficulty Gaps**: Identify missing difficulty levels per topic
4. **Content Suggestions**: Generate specific Q&A ideas to fill gaps
5. **Roadmap Generation**: Create prioritized content creation plans

## When to Use

Activate this skill when user requests:
- "What topics need more content?"
- "Find content gaps"
- "What questions should I add?"
- "Analyze coverage for [topic]"
- "Generate content roadmap"
- "What's missing in the vault?"
- During quarterly content planning
- Before content sprints

## Prerequisites

Required context:
- Access to vault statistics
- `00-Administration/Vault-Rules/TAXONOMY.md` for topic/subtopic lists
- Understanding of interview question domains

## Process

### Step 1: Collect Current Coverage

`Map` all existing content:

```
By Topic:
| Topic | Total | Easy | Medium | Hard |
|-------|-------|------|--------|------|
| android | 527 | 89 | 312 | 126 |
| kotlin | 358 | 45 | 201 | 112 |
| algorithms | 9 | 3 | 4 | 2 |
| system-design | 10 | 0 | 3 | 7 |
| databases | 9 | 2 | 5 | 2 |
| compsci | 56 | 12 | 28 | 16 |
| tools | 3 | 1 | 2 | 0 |

By Subtopic (example: kotlin):
| Subtopic | Count | Coverage |
|----------|-------|----------|
| coroutines | 45 | HIGH |
| flow | 32 | HIGH |
| collections | 8 | LOW |
| type-system | 5 | LOW |
| dsl | 2 | CRITICAL |
```

### Step 2: Compare Against Taxonomy

Check coverage against all defined categories:

```
From TAXONOMY.md:
- 22 valid topics
- ~50 Android subtopics
- ~30 Kotlin subtopics
- Standard difficulty levels

Coverage status:
- COMPLETE: 20+ questions across all difficulties
- HIGH: 10-19 questions, all difficulties covered
- MEDIUM: 5-9 questions, some difficulty gaps
- LOW: 1-4 questions
- MISSING: 0 questions
```

### Step 3: Identify Gaps

Detect specific gaps:

```
Gap Types:

1. Topic Gaps (no coverage):
   - performance: 0 questions
   - security: 0 questions

2. Difficulty Gaps (missing levels):
   - system-design: no easy questions
   - tools: no hard questions
   - algorithms: need more medium/hard

3. Subtopic Gaps (within topics):
   - kotlin/dsl: only 2 questions
   - android/wear-os: 0 questions
   - android/testing-compose: 3 questions

4. Balance Gaps (skewed distribution):
   - android: 60% medium (should be ~40%)
   - kotlin: 31% hard (higher than typical)
```

### Step 4: Generate Suggestions

Create specific Q&A ideas for each gap:

```
For kotlin/collections gap:

Suggested Questions:
1. [EASY] "What are the main collection types in Kotlin?"
   - Covers: List, Set, Map basics
   - Subtopics: collections, fundamentals

2. [MEDIUM] "How do Kotlin sequences differ from collections?"
   - Covers: Lazy evaluation, performance
   - Subtopics: collections, sequences, performance

3. [MEDIUM] "Explain collection transformation functions in Kotlin"
   - Covers: map, filter, reduce, fold
   - Subtopics: collections, functional

4. [HARD] "How would you implement a custom collection in Kotlin?"
   - Covers: Collection interfaces, delegation
   - Subtopics: collections, type-system, advanced
```

### Step 5: Prioritize Content

Rank gaps by importance:

```
Priority Factors:
- Interview frequency (how often asked)
- Foundational importance (prerequisite for other topics)
- Current coverage level (lower = higher priority)
- User request history
- Industry relevance

Priority Levels:
P0: Critical gaps in core topics
P1: Important gaps affecting learning paths
P2: Nice-to-have improvements
P3: Completeness items
```

### Step 6: Generate Roadmap

Create actionable content plan:

```markdown
# Content Roadmap

## Sprint 1: Critical Gaps (P0)

### Week 1: Kotlin Collections
- [ ] q-kotlin-collections-overview--kotlin--easy
- [ ] q-sequences-vs-collections--kotlin--medium
- [ ] q-collection-operations--kotlin--medium
- [ ] q-custom-collection--kotlin--hard

### Week 2: System Design Basics
- [ ] q-system-design-introduction--system-design--easy
- [ ] q-scalability-basics--system-design--easy
- [ ] q-load-balancing-intro--system-design--easy

## Sprint 2: Important Gaps (P1)

### Week 3: Android Testing
- [ ] q-compose-testing-basics--android--easy
- [ ] q-compose-testing-semantics--android--medium
- [ ] q-compose-testing-navigation--android--hard

[... more sprints ...]
```

### Step 7: Generate Report

Produce comprehensive gap analysis:

```markdown
# Content Gap Analysis

**Generated**: 2025-11-15
**Total Q&As**: 972
**Topics Covered**: 7/22

---

## Coverage Summary

| Status | Topics | Notes |
|--------|--------|-------|
| COMPLETE | 2 | android, kotlin |
| HIGH | 1 | compsci |
| MEDIUM | 2 | algorithms, databases |
| LOW | 2 | system-design, tools |
| MISSING | 15 | security, performance, ... |

---

## Top Priority Gaps

### P0: Critical (Must Address)

1. **System Design - Easy Questions**
   - Current: 0 easy, 3 medium, 7 hard
   - Gap: No entry-level content for beginners
   - Suggestion: Add 5 easy questions covering basics

2. **Kotlin Collections**
   - Current: 8 questions total
   - Gap: Insufficient for comprehensive coverage
   - Suggestion: Add 12 questions (3 easy, 6 medium, 3 hard)

3. **Performance Topic**
   - Current: 0 questions
   - Gap: Critical topic completely missing
   - Suggestion: Create 15 questions across all levels

### P1: Important (Should Address)

[... more gaps ...]

---

## Detailed Gap Analysis by Topic

### kotlin (358 Q&As)

| Subtopic | Count | Status | Gap |
|----------|-------|--------|-----|
| coroutines | 45 | COMPLETE | - |
| flow | 32 | HIGH | - |
| collections | 8 | LOW | +12 |
| type-system | 5 | LOW | +10 |
| dsl | 2 | CRITICAL | +8 |
| multiplatform | 0 | MISSING | +10 |

**Suggested Additions**: 40 questions

### android (527 Q&As)

| Subtopic | Count | Status | Gap |
|----------|-------|--------|-----|
| ui-compose | 87 | COMPLETE | - |
| lifecycle | 45 | HIGH | - |
| testing-compose | 3 | CRITICAL | +12 |
| wear-os | 0 | MISSING | +8 |
| auto | 0 | MISSING | +5 |

**Suggested Additions**: 25 questions

[... more topics ...]

---

## Difficulty Distribution Analysis

### Current Distribution
| Difficulty | Count | Percentage | Target |
|------------|-------|------------|--------|
| Easy | 152 | 15.6% | 25% |
| Medium | 555 | 57.1% | 50% |
| Hard | 265 | 27.3% | 25% |

### Recommendations
- Add more EASY questions (+90 to reach 25%)
- Medium questions slightly over target (OK)
- Hard questions slightly over target (OK)

---

## Content Roadmap

### Sprint 1: Critical Gaps
**Duration**: 2 weeks
**Questions to add**: 25

1. System Design Basics (5 easy)
2. Kotlin Collections (8 mixed)
3. Android Testing Compose (7 mixed)
4. Performance Basics (5 easy)

### Sprint 2: Important Gaps
**Duration**: 2 weeks
**Questions to add**: 30

[... more sprints ...]

---

## Suggested Q&A Titles

### Kotlin Collections (Priority: P0)

**Easy**:
- "What are the main collection types in Kotlin?"
- "How do you create immutable vs mutable collections?"
- "What is the difference between List and Array?"

**Medium**:
- "How do Kotlin sequences improve performance?"
- "Explain map, filter, and reduce operations"
- "How does groupBy work in Kotlin collections?"

**Hard**:
- "Implement a custom lazy collection in Kotlin"
- "How would you optimize collection operations for large datasets?"

[... more suggestions ...]

---

**Use this roadmap to prioritize content creation efforts.**
```

## Examples

### Example 1: Full Vault Analysis

**User**: "Analyze content gaps in the vault"

**Output**:
```markdown
# Gap Analysis Summary

Coverage: 7/22 topics (32%)

## Critical Gaps (P0)
1. Performance: 0 questions (add 15)
2. Security: 0 questions (add 15)
3. System Design Easy: 0 questions (add 5)
4. Kotlin Collections: 8 questions (add 12)

## Suggested First Actions
- Create 5 easy system-design questions
- Add 12 kotlin/collections questions
- Start performance topic with 5 easy questions

Total suggested additions: 62 questions
```

### Example 2: Topic-Specific Analysis

**User**: "What's missing in Kotlin coverage?"

**Output**:
```markdown
# Kotlin Coverage Analysis

Total: 358 Q&As

## Well Covered (No Action)
- coroutines: 45 (COMPLETE)
- flow: 32 (HIGH)
- null-safety: 28 (HIGH)

## Needs Improvement
- collections: 8 (add 12)
- type-system: 5 (add 10)
- dsl: 2 (add 8)
- multiplatform: 0 (add 10)

## Difficulty Gaps
- Need 15 more easy questions
- Hard questions well covered

## Top 5 Suggested Questions
1. [EASY] Kotlin collection types overview
2. [MEDIUM] Sequences vs collections performance
3. [MEDIUM] Type aliases and inline classes
4. [HARD] Building DSLs in Kotlin
5. [MEDIUM] Kotlin Multiplatform project setup
```

### Example 3: Difficulty Gap Analysis

**User**: "Which topics need more easy questions?"

**Output**:
```markdown
# Easy Question Gap Analysis

## Topics Missing Easy Questions
1. system-design: 0 easy (10 total)
2. tools: 1 easy (3 total)
3. algorithms: 3 easy (9 total) - need more

## Topics with Good Easy Coverage
- android: 89 easy (17%)
- kotlin: 45 easy (13%)
- compsci: 12 easy (21%)

## Recommendations
Add easy questions to:
1. system-design: +5 easy questions
2. algorithms: +5 easy questions
3. tools: +3 easy questions

Suggested easy question topics:
- "What is system design?" (system-design)
- "Introduction to Big O notation" (algorithms)
- "Git basics for beginners" (tools)
```

## Error Handling

### No Data for Topic

**Problem**: Topic exists in TAXONOMY but no notes exist

**Solution**:
1. Mark as MISSING
2. Generate starter suggestions
3. Recommend foundational questions first

### Incomplete TAXONOMY

**Problem**: Some subtopics not in TAXONOMY.md

**Solution**:
1. Report found-but-unlisted subtopics
2. Suggest adding to TAXONOMY if valid
3. Continue analysis with available data

### Skewed Data

**Problem**: One topic dominates (e.g., 90% android)

**Solution**:
1. Acknowledge imbalance
2. Suggest diversification if desired
3. Focus gap analysis on intentional scope

## Integration with Other Skills

**Workflow: Content Planning**
1. Run `gap-analyzer` for gap report
2. Use roadmap to plan sprint
3. Create notes with `obsidian-qna-creator`
4. Validate with `batch-validator`

**Workflow: Topic Expansion**
1. Decide to expand topic X
2. Run `gap-analyzer` on topic X
3. Get specific Q&A suggestions
4. Create prioritized content

## Notes

**Data-Driven**: Analysis based on actual vault content.

**Actionable**: Specific Q&A suggestions, not just gap identification.

**Prioritized**: Gaps ranked by importance for efficient planning.

**Comprehensive**: Covers topics, subtopics, and difficulty levels.

**Customizable**: Can analyze full vault or specific topics.

---

**Version**: 1.0
**Last Updated**: 2025-01-05
**Status**: Production Ready
