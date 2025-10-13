# Linking Strategy for Interview Questions Vault

**Date Created**: 2025-10-12
**Purpose**: Systematic approach to connect 752 orphaned question files (82.5% of vault)
**Status**:  Critical - Most files are isolated

---

##  Current State Analysis

### Overall Statistics
- **Total Question Files**: 911
- **Connected Files**: 159 (17.5%)
- **Orphaned Files**: 752 (82.5%)
- **Total Wikilinks**: 464

### Orphaned Files by Directory

| Directory | Total | Connected | Orphaned | % Orphaned | Priority |
|-----------|-------|-----------|----------|------------|----------|
| **30-System-Design** | 2 | 0 | 2 | 100% |  High |
| **60-CompSci** | 163 | 3 | 160 | 98% |  High |
| **40-Android** | 495 | 20 | 475 | 96% | 🟠 Medium |
| **70-Kotlin** | 243 | 128 | 115 | 47% | 🟢 Low |

### Link Source Distribution
- **Q-files linking to Q-files**: 442 (95.3%)
- **MOC/Concept files linking to Q-files**: 22 (4.7%)

**Problem**: MOCs and topic files barely reference questions!

---

##  Strategic Goals

### Primary Goals
1. **Reduce orphan rate from 82.5% to <10%** (Target: 90% connectivity)
2. **Balance link distribution** - Each file should have 3-7 incoming links
3. **Strengthen MOC → Question links** - MOCs should be discovery hubs
4. **Create topic clusters** - Related questions should interconnect

### Success Metrics
-  <10% orphan rate (currently 82.5%)
-  Average 4-6 incoming links per file (currently 0.5)
-  Every MOC links to 20+ questions (currently ~5)
-  90% of questions appear in at least one topic cluster

---

##  Three-Phase Linking Strategy

### Phase 1: MOC Strengthening (Quick Wins)
**Goal**: Make MOC files serve as discovery hubs
**Impact**: Can connect 200+ orphaned files quickly
**Effort**: Low (use Dataview queries + manual curation)

#### Tasks:
1. **Update moc-kotlin.md**
   - Add sections for each subtopic (coroutines, flow, delegation, etc.)
   - Link to top 50 Kotlin questions per subtopic
   - Use Dataview to auto-list by difficulty

2. **Update moc-android.md**
   - Group by: Compose, Architecture, Testing, Gradle, Performance
   - Link to top 100 Android questions
   - Include quick reference tables

3. **Update moc-backend.md**
   - Sections: Databases, SQL, APIs, Design Patterns
   - Link to all backend questions

4. **Update moc-algorithms.md**
   - Sections: Data Structures, Sorting, Searching, Complexity
   - Link to all algorithm questions

5. **Create missing MOCs**:
   - `moc-system-design.md` - Link to 2 system design questions
   - `moc-testing.md` - Link to all testing questions
   - `moc-security.md` - Link to security questions
   - `moc-accessibility.md` - Link to accessibility questions

**Expected Result**: 200-300 files gain 1 incoming link from MOCs

---

### Phase 2: Topic Cluster Creation (Medium Effort)
**Goal**: Create interconnected question clusters by topic
**Impact**: Improves discoverability and learning paths
**Effort**: Medium (semi-automated with review)

#### Strategy: Hub-and-Spoke Model

```
        [Topic Hub]
       /    |    \
      /     |     \
   [Q1]   [Q2]   [Q3]
    |  \  / |  \  /
    |   \/  |   \/
    |   /\  |   /\
    |  /  \ |  /  \
   [Q4]   [Q5]   [Q6]
```

#### Clusters to Create:

**Kotlin Clusters** (70-Kotlin):
1. **Coroutines Fundamentals** (15 questions)
   - Hub: q-kotlin-coroutines-introduction--kotlin--medium
   - Spokes: suspend functions, builders, scope, context, dispatchers

2. **Flow & Reactive Streams** (20 questions)
   - Hub: q-kotlin-flow-basics--kotlin--medium
   - Spokes: operators, hot/cold, SharedFlow, StateFlow, channels

3. **Delegation & Properties** (10 questions)
   - Hub: q-kotlin-delegation-detailed--kotlin--medium
   - Spokes: by keyword, lazy, lateinit, property delegates

4. **Kotlin Multiplatform** (5 questions)
   - Hub: q-kotlin-multiplatform-overview--kotlin--hard
   - Spokes: expect/actual, KMM, native, JS

**Android Clusters** (40-Android):
1. **Jetpack Compose Basics** (30 questions)
   - Hub: q-jetpack-compose-basics--android--medium
   - Spokes: composable functions, state, recomposition, modifiers

2. **Compose Advanced** (25 questions)
   - Hub: q-compose-performance-optimization--android--hard
   - Spokes: custom layouts, animations, gestures, effects

3. **Architecture Patterns** (20 questions)
   - Hub: q-clean-architecture-android--android--hard
   - Spokes: MVVM, MVI, Repository, UseCase, DI

4. **Testing** (15 questions)
   - Hub: q-compose-ui-testing-advanced--testing--hard
   - Spokes: unit tests, UI tests, mocking, Hilt testing

5. **Gradle & Build** (10 questions)
   - Hub: q-gradle-kotlin-dsl-vs-groovy--android--medium
   - Spokes: dependencies, optimization, multi-module

**CompSci Clusters** (60-CompSci):
1. **Design Patterns** (25 questions)
   - Hub: q-design-patterns-types--design-patterns--medium
   - Spokes: Creational, Structural, Behavioral patterns

2. **OOP Fundamentals** (15 questions)
   - Hub: Create new hub or use existing
   - Spokes: inheritance, polymorphism, encapsulation

3. **Coroutines Theory** (20 questions)
   - Hub: q-coroutine-context-essence--programming-languages--medium
   - Spokes: dispatchers, scope, context, structured concurrency

**Implementation**:
```python
# For each cluster:
1. Identify hub question (most comprehensive)
2. Find 5-15 related questions using:
   - Matching subtopics in frontmatter
   - Similar keywords in title
   - Related difficulty levels
3. Add bidirectional links:
   - Hub → Spokes (in "Related Questions")
   - Spokes → Hub (in "Related Questions")
   - Spokes ↔ Spokes (relevant pairs)
```

**Expected Result**: 400-500 files gain 2-4 incoming links

---

### Phase 3: Automated Cross-Referencing (High Effort)
**Goal**: Intelligently link related questions using metadata
**Impact**: Creates comprehensive knowledge graph
**Effort**: High (requires scripting + manual review)

#### Algorithm: Similarity-Based Linking

```python
def find_related_questions(question_file):
    """
    Find related questions based on:
    1. Shared subtopics (70% weight)
    2. Same topic + adjacent difficulty (20% weight)
    3. Keyword matching in title (10% weight)
    """

    # Extract metadata from frontmatter
    topic = question_file.frontmatter['topic']
    subtopics = question_file.frontmatter['subtopics']
    difficulty = question_file.frontmatter['difficulty']

    # Find candidates
    candidates = []

    for other_file in all_questions:
        if other_file == question_file:
            continue

        # Calculate similarity score
        score = 0

        # Shared subtopics (max 2-3 overlaps)
        shared_subtopics = set(subtopics) & set(other_file.subtopics)
        score += len(shared_subtopics) * 35  # 70% weight distributed

        # Same topic, adjacent difficulty
        if other_file.topic == topic:
            if abs(difficulty_to_num(difficulty) -
                   difficulty_to_num(other_file.difficulty)) <= 1:
                score += 20

        # Keyword matching in title
        shared_keywords = title_keywords_overlap(
            question_file.title,
            other_file.title
        )
        score += shared_keywords * 5  # 10% weight

        if score >= 40:  # Threshold for relevance
            candidates.append((other_file, score))

    # Return top 5-7 most related
    return sorted(candidates, key=lambda x: x[1], reverse=True)[:7]
```

#### Implementation Steps:
1. **Run similarity analysis** on all orphaned files
2. **Generate suggested links** (automated)
3. **Manual review** of top 100 suggestions
4. **Batch update** "Related Questions" sections
5. **Iterate** on remaining orphans

**Expected Result**: 700+ files gain 3-5 incoming links

---

##  Implementation Tools

### Tool 1: MOC Link Generator
```python
# /scripts/moc_link_generator.py
"""
Generates MOC sections with links to questions.
Uses Dataview-style queries to group by subtopic and difficulty.
"""
```

### Tool 2: Cluster Creator
```python
# /scripts/cluster_creator.py
"""
Given a hub question and topic/subtopics,
finds related questions and creates bidirectional links.
"""
```

### Tool 3: Orphan Analyzer
```python
# /scripts/orphan_analyzer.py
"""
Identifies orphaned files and suggests linking opportunities.
Outputs prioritized list for manual review.
"""
```

### Tool 4: Link Validator
```python
# /scripts/link_validator.py
"""
Validates that:
- All wikilinks resolve to existing files
- Related Questions sections exist
- No self-links
- Links are bidirectional where appropriate
"""
```

---

##  Execution Plan

### Week 1: Quick Wins (Phase 1)
**Goal**: Reduce orphan rate to 60%

- [ ] Day 1: Update moc-kotlin.md (link 50 questions)
- [ ] Day 2: Update moc-android.md (link 100 questions)
- [ ] Day 3: Update moc-backend.md, moc-algorithms.md (link 30 questions)
- [ ] Day 4: Create moc-system-design.md, moc-testing.md (link 20 questions)
- [ ] Day 5: Review and fix any broken links

**Expected Progress**: 200 files connected (orphan rate: 60%)

---

### Week 2: Kotlin Clusters (Phase 2)
**Goal**: Complete Kotlin directory connectivity

- [ ] Day 6-7: Create Coroutines cluster (15 questions)
- [ ] Day 8-9: Create Flow cluster (20 questions)
- [ ] Day 10: Create Delegation and Multiplatform clusters (15 questions)

**Expected Progress**: 50 more files connected (orphan rate: 55%)

---

### Week 3: Android Clusters (Phase 2)
**Goal**: Reduce Android orphan rate to 50%

- [ ] Day 11-12: Create Compose Basics cluster (30 questions)
- [ ] Day 13-14: Create Compose Advanced cluster (25 questions)
- [ ] Day 15: Create Architecture cluster (20 questions)

**Expected Progress**: 75 more files connected (orphan rate: 46%)

---

### Week 4: CompSci Clusters (Phase 2)
**Goal**: Reduce CompSci orphan rate to 50%

- [ ] Day 16-17: Create Design Patterns cluster (25 questions)
- [ ] Day 18-19: Create OOP and Coroutines Theory clusters (35 questions)
- [ ] Day 20: Review phase 2 progress

**Expected Progress**: 60 more files connected (orphan rate: 39%)

---

### Week 5-6: Automated Cross-Referencing (Phase 3)
**Goal**: Achieve <10% orphan rate

- [ ] Week 5: Run similarity analysis and generate suggestions
- [ ] Week 6: Manual review and batch updates

**Expected Progress**: 350+ more files connected (orphan rate: <10%)

---

##  Success Tracking

### Key Metrics Dashboard

Create a tracking file: `00-Administration/LINKING-PROGRESS.md`

```markdown
## Linking Progress Tracker

### Overall Metrics
- **Orphan Rate**: 82.5% → Target: <10%
- **Average Incoming Links**: 0.5 → Target: 4-6
- **Total Links**: 464 → Target: 3600+

### Weekly Progress
| Week | Orphans | % Connected | New Links | Milestone |
|------|---------|-------------|-----------|-----------|
| 0    | 752     | 17.5%       | 464       | Baseline  |
| 1    | 552     | 39.4%       | 664       | MOCs done |
| 2    | 502     | 44.9%       | 764       | Kotlin    |
| 3    | 427     | 53.1%       | 939       | Android   |
| 4    | 367     | 59.7%       | 1079      | CompSci   |
| 5-6  | <91     | >90%        | 3600+     |  Target |

### Directory Progress
| Directory | Start | Week 1 | Week 2 | Week 3 | Week 4 | Week 6 |
|-----------|-------|--------|--------|--------|--------|--------|
| Kotlin    | 47%   | 55%    | 85%    | 85%    | 85%    | 95%    |
| Android   | 4%    | 25%    | 25%    | 55%    | 55%    | 92%    |
| CompSci   | 2%    | 10%    | 10%    | 10%    | 65%    | 90%    |
| System    | 0%    | 100%   | 100%   | 100%   | 100%   | 100%   |
```

---

##  Link Quality Guidelines

### Good Link Characteristics
 **Relevant**: Links to actually related content
 **Balanced**: 3-7 incoming links per file
 **Bidirectional**: Related questions link back
 **Hierarchical**: Easy → Medium → Hard progression
 **Discoverable**: Linked from at least one MOC

### Bad Link Characteristics
 **Tangential**: Barely related content
 **Excessive**: 20+ links in one file
 **Unidirectional**: Dead-end links
 **Circular**: A → B → C → A with no value
 **Orphaned**: File linked from nowhere

### Link Placement Rules

**In Q-files (questions):**
- `## Related Questions` section (3-7 links)
- Links to similar difficulty questions
- Links to prerequisite questions (easier)
- Links to advanced questions (harder)

**In MOC files:**
- Group by subtopic
- List 10-30 questions per section
- Include difficulty indicators
- Use Dataview for auto-generation

**In Concept files:**
- `## See Also` section
- Link to questions that demonstrate concept
- Link to related concepts

---

##  Orphan Prioritization

### High Priority Orphans (Link First)
1. **High difficulty + high quality content** - These are valuable resources
2. **Frequently used subtopics** - Will benefit many learners
3. **Recently created** - New content should be discoverable
4. **High word count** - Comprehensive content deserves visibility

### Medium Priority Orphans
1. **Medium difficulty + standard content**
2. **Common subtopics**
3. **Older but still relevant**

### Low Priority Orphans
1. **Easy questions with short content** - Can be batch linked
2. **Duplicate topics** - May need consolidation
3. **Outdated content** - May need updating first

---

##  Quick Start Commands

### Check Current Orphan Status
```bash
cd /Users/npochaev/Documents/InterviewQuestions
python3 /tmp/find_orphaned_questions_full.py
```

### Generate MOC Links (Pseudo-code)
```bash
python3 scripts/moc_link_generator.py --moc=moc-kotlin --max-links=50
```

### Create Topic Cluster (Pseudo-code)
```bash
python3 scripts/cluster_creator.py \
  --hub="q-kotlin-coroutines-introduction" \
  --topic="kotlin" \
  --subtopics="coroutines,suspend-functions" \
  --max-spokes=15
```

### Validate All Links
```bash
python3 scripts/link_validator.py --fix-broken --report
```

---

##  Manual Linking Template

When manually adding links, use this template:

### For Q-files (in "Related Questions" section):
```markdown
## Related Questions

### Prerequisites (Easier)
- [[q-prerequisite-topic-1--topic--easy]]
- [[q-prerequisite-topic-2--topic--easy]]

### Related (Same Level)
- [[q-related-topic-1--topic--medium]]
- [[q-related-topic-2--topic--medium]]

### Advanced (Harder)
- [[q-advanced-topic-1--topic--hard]]
- [[q-advanced-topic-2--topic--hard]]
```

### For MOC files (new section):
```markdown
## Coroutines & Concurrency

### Easy
- [[q-what-is-coroutine--kotlin--easy]] - Basic concepts
- [[q-suspend-functions-basics--kotlin--easy]] - Suspend keyword

### Medium
- [[q-kotlin-coroutines-introduction--kotlin--medium]] - Comprehensive guide
- [[q-coroutine-scope-basics--kotlin--medium]] - Scope management

### Hard
- [[q-structured-concurrency-kotlin--kotlin--hard]] - Advanced patterns
```

---

##  Next Steps

1. **Review this strategy document**  (Current step)
2. **Choose starting point**:
   - Option A: Week 1 (Quick wins with MOCs)
   - Option B: Week 2 (Focus on Kotlin first)
   - Option C: Custom approach
3. **Execute chosen phase**
4. **Track progress weekly**
5. **Iterate and improve**

---

##  Resources

### Related Documents
- `LINK_ANALYSIS_REPORT.md` - Original broken links analysis
- `LINK_FIX_COMPLETION_REPORT.md` - Phase 1 completion report
- `LINK-MONITORING-GUIDE.md` - Automated monitoring setup
- `LINK-HEALTH-DASHBOARD.md` - Live health metrics

### External Resources
- [Obsidian Graph View Guide](https://help.obsidian.md/Plugins/Graph+view)
- [Effective Note Linking](https://notes.andymatuschak.org/Evergreen_notes)
- [Zettelkasten Method](https://zettelkasten.de/posts/overview/)

---

**Document Status**:  Complete
**Last Updated**: 2025-10-12
**Next Review**: After Week 1 completion
**Owner**: Vault Maintenance Team
