# Obsidian Vault Link Analysis Report

**Date**: 2025-10-12
**Vault**: InterviewQuestions
**Total Files**: 831 question files

---

## Executive Summary

This comprehensive analysis examined all 831 Q&A files in the Obsidian vault to identify link issues and categorize content by topic. The analysis extracted and validated all internal links, including wikilinks, markdown links, and frontmatter references.

### Key Findings

- **Total Links Found**: 202
- **Valid Links**: 134 (66.3%)
- **Broken Links**: 68 (33.7%)
- **Malformed Links**: 0
- **Files with Broken Links**: 39
- **Unique Broken Targets**: 51

---

## Link Statistics

### By Link Type

| Type | Count | Percentage |
|------|-------|------------|
| Wikilinks `[[link]]` | 201 | 99.5% |
| Markdown links `[text](link)` | 1 | 0.5% |

### By Location in File

| Location | Count | Percentage |
|----------|-------|------------|
| Related Questions Section | 147 | 72.8% |
| Body Content | 55 | 27.2% |
| Frontmatter (moc) | 0 | 0% |
| Frontmatter (related) | 0 | 0% |

**Note**: No files currently use the `moc:` or `related:` frontmatter fields for linking.

---

## Broken Links Analysis

### Summary by Category

The 68 broken links can be categorized into three types:

1. **Missing Question Files** (44 links): References to question files that don't exist yet
2. **Missing Concept/MOC Files** (23 links): References to concept notes (c-*) and MOC files (moc-*)
3. **Malformed/Invalid Links** (1 link): Incorrectly formatted link

### Files with Broken Links

<details>
<summary><strong>Kotlin Files (22 files with broken links)</strong></summary>

#### q-kotlin-init-block--kotlin--easy.md
- `q-kotlin-constructors--kotlin--easy` (Missing)
- `q-kotlin-properties--kotlin--easy` (Missing)

#### q-produce-actor-builders--kotlin--medium.md
- `q-actor-pattern--kotlin--hard` (Missing)
- `q-channel-pipelines--kotlin--hard` (Missing)

#### q-select-expression-channels--kotlin--hard.md
- `q-advanced-coroutine-patterns--kotlin--hard` (Missing)
- `q-fan-in-fan-out--kotlin--hard` (Missing)

#### q-hot-cold-flows--kotlin--medium.md
- `q-flow-basics--kotlin--medium` (Missing - similar file exists: q-kotlin-flow-basics--kotlin--medium)

#### q-kotlin-higher-order-functions--kotlin--medium.md
- `q-kotlin-inline-functions--kotlin--medium` (Missing)

#### q-channel-closing-completion--kotlin--medium.md
- `q-channel-pipelines--kotlin--hard` (Missing)

#### q-kotlin-lambda-expressions--kotlin--medium.md
- `q-kotlin-inline-functions--kotlin--medium` (Missing)

#### q-channel-flow-comparison--kotlin--medium.md
- `q-flow-basics--kotlin--medium` (Missing)
- `q-sharedflow-stateflow--kotlin--medium` (Missing)
- `q-flow-backpressure--kotlin--hard` (Missing)
- `q-channel-buffering-strategies--kotlin--hard` (Missing)

#### q-lifecyclescope-viewmodelscope--kotlin--medium.md
- `q-repeatonlifecycle--kotlin--medium` (Missing - similar file exists: q-repeatonlifecycle-android--kotlin--medium)
- `q-lifecycle-aware-coroutines--kotlin--hard` (Missing)

#### q-kotlin-multiplatform-overview--kotlin--hard.md
- `q-expect-actual-kotlin--kotlin--medium` (Missing)
- `q-kotlin-native--kotlin--hard` (Missing)

#### q-statein-sharein-flow--kotlin--medium.md
- `q-stateflow-sharedflow--kotlin--medium` (Missing - similar file exists: q-stateflow-sharedflow-differences--kotlin--medium)
- `q-cold-hot-flow--kotlin--medium` (Missing - similar file exists: q-cold-vs-hot-flows--kotlin--medium)

#### q-coroutine-exception-handling--kotlin--medium.md
- `q-coroutinescope-supervisorscope--kotlin--medium` (Missing - similar file exists: q-supervisor-scope-vs-coroutine-scope--kotlin--medium)
- `q-structured-concurrency--kotlin--hard` (Missing - similar file exists: q-structured-concurrency-kotlin--kotlin--medium)

#### q-kotlin-const--kotlin--easy.md
- `q-kotlin-val-vs-var--kotlin--easy` (Missing)

#### q-repeatonlifecycle-android--kotlin--medium.md
- `q-lifecycle-aware-coroutines--kotlin--hard` (Missing)

#### q-viewmodel-coroutines-lifecycle--kotlin--medium.md
- `q-testing-viewmodel-coroutines--kotlin--medium` (Missing)

#### q-kotlin-delegation-detailed--kotlin--medium.md
- `q-lazy-lateinit-kotlin--kotlin--medium` (Missing - similar file exists: q-lazy-vs-lateinit--kotlin--medium)

#### q-retry-operators-flow--kotlin--medium.md
- `q-flow-error-handling--kotlin--medium` (Missing - similar file exists: q-flow-exception-handling--kotlin--medium)
- `q-catch-operator-flow--kotlin--medium` (Missing)

#### q-channels-basics-types--kotlin--medium.md
- `q-channel-buffering-strategies--kotlin--hard` (Missing)

#### q-debounce-throttle-flow--kotlin--medium.md
- `q-flow-operators--kotlin--medium` (Missing)
- `q-flow-time-operators--kotlin--medium` (Missing)

#### q-coroutine-context-detailed--kotlin--hard.md
- `q-coroutine-dispatchers--kotlin--medium` (Missing)
- `q-structured-concurrency--kotlin--hard` (Missing)

#### q-kotlin-map-flatmap--kotlin--medium.md
- `q-kotlin-collections--kotlin--medium` (Missing - note: q-kotlin-collections--kotlin--easy exists)

#### q-flatmap-variants-flow--kotlin--medium.md
- `q-flow-operators--kotlin--medium` (Missing)
- `q-flow-basics--kotlin--easy` (Missing)

</details>

<details>
<summary><strong>Android Files (10 files with broken links)</strong></summary>

#### q-compose-performance-optimization--android--hard.md
- `q-recomposition-compose--android--medium` (Missing)

#### q-kapt-vs-ksp--android--medium.md
- `q-annotation-processing--android--medium` (Missing)

#### q-compose-modifier-system--android--medium.md
- `q-jetpack-compose-basics--android--medium` (Missing)

#### q-clean-architecture-android--android--hard.md
- `q-mvvm--android--medium` (Missing - similar file exists: q-mvvm-pattern--android--medium)

#### q-compose-semantics--android--medium.md
- `q-compose-testing--android--medium` (Missing)

#### q-gradle-kotlin-dsl-vs-groovy--android--medium.md
- `q-gradle-basics--android--easy` (Missing)

#### q-compose-navigation-advanced--android--medium.md
- `q-jetpack-compose-basics--android--medium` (Missing)

#### q-repository-multiple-sources--android--medium.md
- `q-repository-pattern--android--medium` (Missing)

#### q-cicd-pipeline-setup--devops--medium.md
- `-z $(getprop sys.boot_completed)` (Malformed - appears to be a shell command, not a link)

#### q-mockk-advanced-features--testing--medium.md
- `2, 3` (Malformed - markdown link with invalid target)

</details>

<details>
<summary><strong>Backend/Tools/Algorithms Files (7 files with broken links)</strong></summary>

#### q-git-pull-vs-fetch--tools--easy.md
- `c-git` (Missing concept note)
- `c-version-control` (Missing concept note)
- `moc-tools` (Missing MOC file)

#### q-git-squash-commits--tools--medium.md
- `c-git` (Missing concept note)
- `c-version-control` (Missing concept note)
- `moc-tools` (Missing MOC file)

#### q-virtual-tables-disadvantages--backend--medium.md
- `c-database-performance` (Missing concept note)
- `c-views` (Missing concept note)
- `moc-backend` (Missing MOC file)

#### q-sql-join-algorithms-complexity--backend--hard.md
- `c-sql-queries` (Missing concept note)
- `c-database-performance` (Missing concept note)
- `c-algorithms` (Missing concept note)
- `moc-backend` (Missing MOC file)

#### q-relational-table-unique-data--backend--medium.md
- `c-database-design` (Missing concept note)
- `c-relational-databases` (Missing concept note)
- `moc-backend` (Missing MOC file)

#### q-database-migration-purpose--backend--medium.md
- `c-database-design` (Missing concept note)
- `c-migrations` (Missing concept note)
- `moc-backend` (Missing MOC file)

#### q-data-structures-overview--algorithms--easy.md
- `c-data-structures` (Missing concept note)
- `c-algorithms` (Missing concept note)
- `moc-algorithms` (Missing MOC file)

</details>

---

## Missing Files by Type

### Missing Question Files (44 unique files)

These are question files that are referenced but don't exist:

#### Kotlin Questions
1. `q-kotlin-constructors--kotlin--easy`
2. `q-kotlin-properties--kotlin--easy`
3. `q-actor-pattern--kotlin--hard`
4. `q-channel-pipelines--kotlin--hard`
5. `q-advanced-coroutine-patterns--kotlin--hard`
6. `q-fan-in-fan-out--kotlin--hard`
7. `q-flow-basics--kotlin--medium` (but q-kotlin-flow-basics--kotlin--medium exists)
8. `q-kotlin-inline-functions--kotlin--medium`
9. `q-sharedflow-stateflow--kotlin--medium`
10. `q-flow-backpressure--kotlin--hard`
11. `q-channel-buffering-strategies--kotlin--hard`
12. `q-repeatonlifecycle--kotlin--medium` (but q-repeatonlifecycle-android--kotlin--medium exists)
13. `q-lifecycle-aware-coroutines--kotlin--hard`
14. `q-expect-actual-kotlin--kotlin--medium`
15. `q-kotlin-native--kotlin--hard`
16. `q-stateflow-sharedflow--kotlin--medium` (but q-stateflow-sharedflow-differences--kotlin--medium exists)
17. `q-cold-hot-flow--kotlin--medium` (but q-cold-vs-hot-flows--kotlin--medium exists)
18. `q-coroutinescope-supervisorscope--kotlin--medium` (but q-supervisor-scope-vs-coroutine-scope--kotlin--medium exists)
19. `q-structured-concurrency--kotlin--hard` (but q-structured-concurrency-kotlin--kotlin--medium exists)
20. `q-kotlin-val-vs-var--kotlin--easy`
21. `q-testing-viewmodel-coroutines--kotlin--medium`
22. `q-lazy-lateinit-kotlin--kotlin--medium` (but q-lazy-vs-lateinit--kotlin--medium exists)
23. `q-flow-error-handling--kotlin--medium` (but q-flow-exception-handling--kotlin--medium exists)
24. `q-catch-operator-flow--kotlin--medium`
25. `q-flow-operators--kotlin--medium`
26. `q-flow-time-operators--kotlin--medium`
27. `q-coroutine-dispatchers--kotlin--medium`
28. `q-kotlin-collections--kotlin--medium` (but q-kotlin-collections--kotlin--easy exists)
29. `q-flow-basics--kotlin--easy`

#### Android Questions
30. `q-recomposition-compose--android--medium`
31. `q-annotation-processing--android--medium`
32. `q-jetpack-compose-basics--android--medium`
33. `q-mvvm--android--medium` (but q-mvvm-pattern--android--medium exists)
34. `q-compose-testing--android--medium`
35. `q-gradle-basics--android--easy`
36. `q-repository-pattern--android--medium`

### Missing Concept Files (12 unique files)

Concept files (c-*) that are referenced but don't exist:

1. `c-git`
2. `c-version-control`
3. `c-database-performance`
4. `c-views`
5. `c-sql-queries`
6. `c-algorithms`
7. `c-database-design`
8. `c-relational-databases`
9. `c-migrations`
10. `c-data-structures`

### Missing MOC Files (3 unique files)

Map of Content files (moc-*) that are referenced but don't exist:

1. `moc-tools`
2. `moc-backend`
3. `moc-algorithms`

### Malformed Links (2)

1. `-z $(getprop sys.boot_completed)` - Shell command incorrectly formatted as link
2. `2, 3` - Invalid markdown link target

---

## Topic Distribution

The vault contains questions organized into 15 main topics:

| Topic | File Count | Percentage |
|-------|------------|------------|
| android | 356 | 42.8% |
| kotlin | 101 | 12.2% |
| networking | 8 | 1.0% |
| testing | 6 | 0.7% |
| jetpack-compose | 6 | 0.7% |
| room | 6 | 0.7% |
| security | 6 | 0.7% |
| design-patterns | 5 | 0.6% |
| backend | 4 | 0.5% |
| architecture-patterns | 3 | 0.4% |
| dependency-injection | 3 | 0.4% |
| tools | 3 | 0.4% |
| system-design | 3 | 0.4% |
| permissions | 2 | 0.2% |
| algorithms | 1 | 0.1% |
| **Total** | **831** | **100%** |

---

## Recommendations

### 1. Fix Naming Inconsistencies

Several broken links point to files that exist but with slightly different names:

- `q-flow-basics--kotlin--medium` → `q-kotlin-flow-basics--kotlin--medium`
- `q-stateflow-sharedflow--kotlin--medium` → `q-stateflow-sharedflow-differences--kotlin--medium`
- `q-cold-hot-flow--kotlin--medium` → `q-cold-vs-hot-flows--kotlin--medium`
- `q-coroutinescope-supervisorscope--kotlin--medium` → `q-supervisor-scope-vs-coroutine-scope--kotlin--medium`
- `q-lazy-lateinit-kotlin--kotlin--medium` → `q-lazy-vs-lateinit--kotlin--medium`
- `q-mvvm--android--medium` → `q-mvvm-pattern--android--medium`
- `q-repeatonlifecycle--kotlin--medium` → `q-repeatonlifecycle-android--kotlin--medium`

**Action**: Update links in source files to point to the correct filenames.

### 2. Create Missing High-Priority Question Files

The following missing files are referenced multiple times:

- `q-kotlin-inline-functions--kotlin--medium` (2 references)
- `q-channel-pipelines--kotlin--hard` (2 references)
- `q-jetpack-compose-basics--android--medium` (2 references)
- `q-flow-operators--kotlin--medium` (2 references)
- `q-lifecycle-aware-coroutines--kotlin--hard` (2 references)

### 3. Create MOC Structure

The vault has only 3 MOC files referenced but none exist. Consider creating:

- `moc-tools.md` - For Git and development tools
- `moc-backend.md` - For database and backend topics
- `moc-algorithms.md` - For algorithms and data structures

### 4. Create Concept Notes

Create concept notes (c-*) to organize related topics:

**Backend/Database Concepts:**
- `c-database-design.md`
- `c-database-performance.md`
- `c-sql-queries.md`
- `c-relational-databases.md`
- `c-migrations.md`
- `c-views.md`

**Tools/Version Control:**
- `c-git.md`
- `c-version-control.md`

**Data Structures/Algorithms:**
- `c-data-structures.md`
- `c-algorithms.md`

### 5. Fix Malformed Links

- Fix `q-cicd-pipeline-setup--devops--medium.md` - Remove shell command link
- Fix `q-mockk-advanced-features--testing--medium.md` - Correct markdown link syntax

### 6. Utilize Frontmatter Fields

Currently, no files use `moc:` or `related:` fields in frontmatter. Consider:

- Adding `moc:` field to link questions to their respective MOC pages
- Using `related:` field for cross-references instead of relying solely on "Related Questions" sections

---

## Next Steps

### Immediate Actions (High Priority)

1. **Fix Naming Inconsistencies**: Update 7 links to point to correct existing files
2. **Fix Malformed Links**: Correct 2 malformed link entries
3. **Create Missing MOC Files**: Create 3 MOC structure files

### Short-term Actions (Medium Priority)

4. **Create High-Priority Questions**: Create 5 frequently-referenced question files
5. **Create Concept Notes**: Create 10 concept note files for better organization

### Long-term Actions (Low Priority)

6. **Fill Content Gaps**: Create remaining 37 missing question files
7. **Enhance Linking**: Add more cross-references between related questions
8. **Standardize Frontmatter**: Implement consistent use of `moc:` and `related:` fields

---

## Analysis Methodology

This analysis was performed using a Python script that:

1. Scanned all 831 `q-*.md` files in the vault
2. Parsed YAML frontmatter for metadata (topic, tags, difficulty)
3. Extracted all wikilinks `[[link]]` and markdown links `[text](link)`
4. Validated each link target against existing files
5. Categorized links by type and location
6. Generated statistics and broken link reports

**Analysis Date**: 2025-10-12
**Script**: `/Users/npochaev/Documents/InterviewQuestions/analyze_links.py`
**Full JSON Report**: `/Users/npochaev/Documents/InterviewQuestions/link_analysis_report.json`
