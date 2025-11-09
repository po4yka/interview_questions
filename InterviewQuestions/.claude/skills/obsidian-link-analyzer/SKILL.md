---
name: obsidian-link-analyzer
description: >
  Suggest and add cross-references between interview notes. Analyzes target note's
  topic, subtopics, and difficulty to find related questions and concepts. Ranks
  by relevance and adds to both YAML related field and content sections. Builds
  knowledge graph connections.
---

# Obsidian Link Analyzer

## Purpose

Enhance notes with cross-references and build knowledge graph:
- Find related questions by topic, subtopics, difficulty
- Identify prerequisite and advanced questions
- Suggest relevant concept notes
- Add links to YAML `related` field and content sections
- Improve vault discoverability

Link analysis strengthens connections between notes and helps learners discover related content.

## When to Use

Activate this skill when user requests:
- "Find related questions for [note]"
- "Add cross-references to [note]"
- "Suggest links for [note]"
- "Build connections for [note]"
- After creating new notes
- When enhancing existing content

## Prerequisites

Required context:
- Target note file path
- Access to search vault for related notes
- Understanding of topic relationships

## Process

### Step 1: Analyze Target Note

1. **Read target note**
2. **Extract metadata**:
   - `topic`: Main topic area
   - `subtopics`: List of subtopics
   - `difficulty`: easy, medium, or hard
   - `question_kind`: Type of question
   - Existing `related` links

3. **Extract content keywords**:
   - Technical terms mentioned
   - Patterns or algorithms discussed
   - Technologies referenced

### Step 2: Search for Related Notes

**Search Strategies**:

#### Strategy 1: Same Topic, Adjacent Difficulty

Find questions with:
- Same `topic`
- Difficulty one level easier (for prerequisites)
- Difficulty one level harder (for advanced)

Example:
```
Target: q-coroutine-context--kotlin--medium

Find:
- Easy: q-what-is-coroutine--kotlin--easy (prerequisite)
- Hard: q-structured-concurrency--kotlin--hard (advanced)
```

#### Strategy 2: Shared Subtopics

Find questions with:
- Same `topic`
- At least one shared subtopic
- Any difficulty

Example:
```
Target: q-compose-remember--android--medium
Subtopics: [ui-compose, ui-state]

Find questions with:
- ui-compose OR ui-state
- Different difficulty levels
```

#### Strategy 3: Related Concepts

Find concept notes:
- Referenced in content
- Related to topic or subtopics
- Fundamental to understanding question

Example:
```
Target: q-viewmodel-lifecycle--android--medium

Related concepts:
- c-viewmodel
- c-lifecycle
- c-mvvm-pattern
```

#### Strategy 4: Same Question Kind

Find questions with:
- Same `question_kind`
- Same or adjacent difficulty
- Different subtopics in same topic

Example:
```
Target: q-system-design-cache--system-design--hard
Question kind: system-design

Find other system-design questions:
- q-design-url-shortener--system-design--hard
- q-design-rate-limiter--system-design--medium
```

### Step 3: Rank by Relevance

**Scoring System** (higher = more relevant):

- **+5 points**: Same topic + shared subtopic
- **+4 points**: Same topic + adjacent difficulty
- **+3 points**: Same topic + same difficulty
- **+3 points**: Referenced in content
- **+2 points**: Same topic
- **+2 points**: Related concept note
- **+1 point**: Same question_kind
- **-1 point**: Already in `related` field

**Exclude**:
- The target note itself
- Notes already in `related` field (unless suggesting additions)
- Duplicate suggestions

**Select Top 5-7**:
- Rank all candidates by score
- Select top 5-7 most relevant
- Ensure mix of prerequisites, same-level, and advanced
- Prefer variety in subtopics

### Step 4: Categorize Suggestions

Organize suggestions by relationship type:

**Prerequisites (Easier)**:
- Questions with lower difficulty
- Cover foundational concepts
- Should be understood before target

**Related (Same Level)**:
- Questions with same difficulty
- Cover complementary topics
- Alternative approaches or patterns

**Advanced (Harder)**:
- Questions with higher difficulty
- Build on target concepts
- More complex scenarios

**Concepts**:
- Fundamental concept notes
- Theory and background
- Reference material

### Step 5: Add Links to Note

**Update YAML `related` field**:

```yaml
# Before
related: [c-coroutines, c-scope]

# After
related: [
  c-coroutines,
  c-scope,
  c-structured-concurrency,
  q-what-is-coroutine--kotlin--easy,
  q-coroutine-scope--kotlin--medium,
  q-structured-concurrency--kotlin--hard
]
```

**Update Related Questions section** in content:

```markdown
## Related Questions

### Prerequisites (Easier)
- [[q-what-is-coroutine--kotlin--easy]] - Introduction to coroutines
- [[q-suspend-function--kotlin--easy]] - Understanding suspend

### Related (Same Level)
- [[q-coroutine-scope--kotlin--medium]] - Scope and context relationship
- [[q-coroutine-dispatcher--kotlin--medium]] - Choosing dispatchers

### Advanced (Harder)
- [[q-structured-concurrency--kotlin--hard]] - Complex concurrent flows
- [[q-exception-handling-coroutines--kotlin--hard]] - Error handling
```

### Step 6: Generate Report

**Report Format**:

```markdown
# Link Analysis Report: [filename]

## Current Links: [X items]

Existing related links:
- [[c-concept-1]]
- [[q-existing-question--topic--level]]

## Suggested Additions: [Y items]

### High Relevance (Score 8+)
✅ [[q-question-1--topic--easy]] - Score: 9
   Reason: Same topic, shared subtopic (coroutines), prerequisite

✅ [[c-concept-2]] - Score: 8
   Reason: Referenced in content, fundamental concept

### Medium Relevance (Score 5-7)
💡 [[q-question-2--topic--medium]] - Score: 6
   Reason: Same topic, same difficulty, complementary

💡 [[q-question-3--topic--hard]] - Score: 5
   Reason: Same topic, advanced, builds on concepts

### Recommended Action

Add 5 high/medium relevance links to:
1. YAML `related` field
2. "Related Questions" content section

Updated `related` field will have 7 total items (current 2 + suggested 5).
```

## Examples

### Example 1: Kotlin Coroutine Question

**Target**: `q-coroutine-context--kotlin--medium.md`

**Analysis**:
- Topic: kotlin
- Subtopics: [coroutines, concurrency]
- Difficulty: medium

**Suggestions**:

**Prerequisites**:
- `q-what-is-coroutine--kotlin--easy` (Score: 8) - Foundation
- `q-suspend-function--kotlin--easy` (Score: 7) - Key concept

**Related**:
- `q-coroutine-scope--kotlin--medium` (Score: 9) - Closely related
- `q-coroutine-dispatcher--kotlin--medium` (Score: 8) - Complementary

**Advanced**:
- `q-structured-concurrency--kotlin--hard` (Score: 7) - Builds on context
- `q-exception-handling-coroutines--kotlin--hard` (Score: 6) - Advanced topic

**Concepts**:
- `c-structured-concurrency` (Score: 8) - Fundamental concept

**Total**: 7 suggestions

### Example 2: Android Compose Question

**Target**: `q-compose-remember--android--medium.md`

**Analysis**:
- Topic: android
- Subtopics: [ui-compose, ui-state]
- Difficulty: medium

**Suggestions**:

**Prerequisites**:
- `q-compose-basics--android--easy` (Score: 8) - Foundation
- `q-compose-recomposition--android--easy` (Score: 9) - Key concept for remember

**Related**:
- `q-state-hoisting--android--medium` (Score: 9) - Closely related to state
- `q-derivedstateof--android--medium` (Score: 8) - Alternative state approach
- `q-mutablestateof--android--medium` (Score: 7) - Related state concept

**Advanced**:
- `q-compose-side-effects--android--hard` (Score: 6) - Advanced state handling
- `q-snapshot-state--android--hard` (Score: 5) - Internal mechanisms

**Concepts**:
- `c-compose-state` (Score: 9) - Fundamental concept
- `c-recomposition` (Score: 8) - Core concept for remember

**Total**: 9 suggestions (select top 6-7)

### Example 3: Algorithm Question

**Target**: `q-binary-search--algorithms--easy.md`

**Analysis**:
- Topic: algorithms
- Subtopics: [arrays, binary-search, searching]
- Difficulty: easy

**Suggestions**:

**Related (Same Level)**:
- `q-two-pointers--algorithms--easy` (Score: 6) - Similar technique
- `q-linear-search--algorithms--easy` (Score: 5) - Alternative approach

**Advanced**:
- `q-search-rotated-array--algorithms--medium` (Score: 9) - Binary search variant
- `q-find-peak-element--algorithms--medium` (Score: 8) - Uses binary search
- `q-median-sorted-arrays--algorithms--hard` (Score: 7) - Advanced binary search

**Concepts**:
- `c-binary-search` (Score: 9) - Core algorithm concept
- `c-divide-and-conquer` (Score: 7) - Underlying strategy
- `c-time-complexity` (Score: 6) - For understanding O(log n)

**Total**: 8 suggestions

## Error Handling

### No Related Notes Found

**Problem**: Cannot find any related notes

**Solution**:
1. Inform user that note appears isolated
2. Suggest creating prerequisite or concept notes
3. Recommend linking to MOC at minimum
4. Note that more links can be added as vault grows

### Too Many Related Notes

**Problem**: Many notes share topic/subtopics (e.g., 50+ matches)

**Solution**:
1. Use stricter scoring (require higher thresholds)
2. Prioritize by subtopic overlap
3. Select diverse set covering difficulty range
4. Limit to top 7 most relevant

### All Suggestions Already Linked

**Problem**: Target note already has all relevant links

**Solution**:
1. Report that note is well-connected
2. Congratulate on thorough linking
3. Suggest reviewing link quality/descriptions
4. Note that no changes needed

### Circular Dependencies

**Problem**: Two notes referencing each other

**Solution**:
1. This is expected and desirable
2. Bidirectional links strengthen knowledge graph
3. Ensure descriptions are helpful from both directions
4. No action needed

## Integration with Other Skills

**Common workflows**:

1. **After creating note**:
   → Use `obsidian-qna-creator`
   → Immediately use `obsidian-link-analyzer`
   → Enhance connections from the start

2. **Bulk link enhancement**:
   → Identify notes with few links (<3 in `related`)
   → Run `obsidian-link-analyzer` on each
   → Build comprehensive knowledge graph

3. **After adding new content**:
   → Create multiple new notes
   → Run `obsidian-link-analyzer` on older related notes
   → Update to include new notes

4. **Validation workflow**:
   → Use `obsidian-validator` to check link count
   → If WARNING about few links, use `obsidian-link-analyzer`
   → Validate again to confirm improvement

## Notes

**Knowledge Graph**: Well-connected notes create a web of knowledge that helps learners discover related content organically.

**Discoverability**: Cross-references make vault more navigable and valuable.

**Learning Paths**: Links from easy → medium → hard create natural progression paths.

**Maintenance**: As vault grows, periodic link analysis ensures older notes connect to newer content.

**Bidirectional**: Obsidian backlinks mean adding a link in one note creates connection in both directions.

**Quality over Quantity**: Better to have 5-7 highly relevant links than 20 loosely related ones.

---

**Version**: 1.0
**Last Updated**: 2025-11-09
**Status**: Production Ready
