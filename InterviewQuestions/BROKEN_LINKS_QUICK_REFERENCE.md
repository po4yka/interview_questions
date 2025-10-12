# Broken Links Quick Reference Guide

This document provides an actionable list of all broken links found in the vault, organized by action type.

---

## Quick Stats

- **Total Broken Links**: 68
- **Files Affected**: 39
- **Unique Broken Targets**: 51

---

## Action 1: Fix Naming Inconsistencies (7 fixes)

These links reference files that exist with slightly different names. Simply update the link text.

| Source File | Broken Link | Should Be | Action |
|-------------|-------------|-----------|--------|
| q-hot-cold-flows--kotlin--medium.md | `q-flow-basics--kotlin--medium` | `q-kotlin-flow-basics--kotlin--medium` | Update link |
| q-channel-flow-comparison--kotlin--medium.md | `q-flow-basics--kotlin--medium` | `q-kotlin-flow-basics--kotlin--medium` | Update link |
| q-statein-sharein-flow--kotlin--medium.md | `q-stateflow-sharedflow--kotlin--medium` | `q-stateflow-sharedflow-differences--kotlin--medium` | Update link |
| q-statein-sharein-flow--kotlin--medium.md | `q-cold-hot-flow--kotlin--medium` | `q-cold-vs-hot-flows--kotlin--medium` | Update link |
| q-coroutine-exception-handling--kotlin--medium.md | `q-coroutinescope-supervisorscope--kotlin--medium` | `q-supervisor-scope-vs-coroutine-scope--kotlin--medium` | Update link |
| q-kotlin-delegation-detailed--kotlin--medium.md | `q-lazy-lateinit-kotlin--kotlin--medium` | `q-lazy-vs-lateinit--kotlin--medium` | Update link |
| q-clean-architecture-android--android--hard.md | `q-mvvm--android--medium` | `q-mvvm-pattern--android--medium` | Update link |

---

## Action 2: Fix Malformed Links (2 fixes)

| Source File | Malformed Link | Issue | Action |
|-------------|----------------|-------|--------|
| q-cicd-pipeline-setup--devops--medium.md | `-z $(getprop sys.boot_completed)` | Shell command incorrectly formatted as wikilink | Remove or fix link syntax |
| q-mockk-advanced-features--testing--medium.md | `2, 3` | Invalid markdown link target | Fix or remove link |

---

## Action 3: Create Missing Question Files

### High Priority (Referenced 2+ times)

| Missing File | Referenced By | Count |
|--------------|---------------|-------|
| `q-kotlin-inline-functions--kotlin--medium.md` | q-kotlin-higher-order-functions, q-kotlin-lambda-expressions | 2 |
| `q-channel-pipelines--kotlin--hard.md` | q-produce-actor-builders, q-channel-closing-completion | 2 |
| `q-jetpack-compose-basics--android--medium.md` | q-compose-modifier-system, q-compose-navigation-advanced | 2 |
| `q-flow-operators--kotlin--medium.md` | q-debounce-throttle-flow, q-flatmap-variants-flow | 2 |
| `q-lifecycle-aware-coroutines--kotlin--hard.md` | q-lifecyclescope-viewmodelscope, q-repeatonlifecycle-android | 2 |

### Medium Priority (Referenced 1 time)

#### Kotlin Basics
- `q-kotlin-constructors--kotlin--easy.md`
- `q-kotlin-properties--kotlin--easy.md`
- `q-kotlin-val-vs-var--kotlin--easy.md`
- `q-kotlin-collections--kotlin--medium.md` (Note: easy version exists)

#### Kotlin Coroutines - Advanced
- `q-actor-pattern--kotlin--hard.md`
- `q-advanced-coroutine-patterns--kotlin--hard.md`
- `q-fan-in-fan-out--kotlin--hard.md`
- `q-coroutine-dispatchers--kotlin--medium.md`
- `q-structured-concurrency--kotlin--hard.md` (Note: medium version exists)

#### Kotlin Coroutines - Scopes & Lifecycle
- `q-repeatonlifecycle--kotlin--medium.md` (Note: android version exists)
- `q-testing-viewmodel-coroutines--kotlin--medium.md`

#### Kotlin Flow
- `q-flow-basics--kotlin--easy.md`
- `q-flow-basics--kotlin--medium.md` (Note: q-kotlin-flow-basics exists)
- `q-flow-error-handling--kotlin--medium.md` (Note: exception-handling version exists)
- `q-flow-backpressure--kotlin--hard.md`
- `q-flow-time-operators--kotlin--medium.md`
- `q-catch-operator-flow--kotlin--medium.md`
- `q-sharedflow-stateflow--kotlin--medium.md`

#### Kotlin Channels
- `q-channel-buffering-strategies--kotlin--hard.md`

#### Kotlin Multiplatform
- `q-expect-actual-kotlin--kotlin--medium.md`
- `q-kotlin-native--kotlin--hard.md`

#### Android - Compose
- `q-recomposition-compose--android--medium.md`
- `q-compose-testing--android--medium.md`

#### Android - Architecture
- `q-repository-pattern--android--medium.md`

#### Android - Build & Tools
- `q-annotation-processing--android--medium.md`
- `q-gradle-basics--android--easy.md`

---

## Action 4: Create Concept Notes (c-*)

### Database Concepts (6 files)
- `c-database-design.md` - Referenced by: q-database-migration-purpose, q-relational-table-unique-data
- `c-database-performance.md` - Referenced by: q-virtual-tables-disadvantages, q-sql-join-algorithms-complexity
- `c-sql-queries.md` - Referenced by: q-sql-join-algorithms-complexity
- `c-relational-databases.md` - Referenced by: q-relational-table-unique-data
- `c-migrations.md` - Referenced by: q-database-migration-purpose
- `c-views.md` - Referenced by: q-virtual-tables-disadvantages

### Version Control Concepts (2 files)
- `c-git.md` - Referenced by: q-git-pull-vs-fetch, q-git-squash-commits
- `c-version-control.md` - Referenced by: q-git-pull-vs-fetch, q-git-squash-commits

### Algorithm Concepts (2 files)
- `c-data-structures.md` - Referenced by: q-data-structures-overview
- `c-algorithms.md` - Referenced by: q-data-structures-overview, q-sql-join-algorithms-complexity

---

## Action 5: Create MOC Files (moc-*)

### MOC Structure Files (3 files)
- `moc-tools.md` - Referenced by: q-git-pull-vs-fetch, q-git-squash-commits
- `moc-backend.md` - Referenced by: q-virtual-tables-disadvantages, q-sql-join-algorithms-complexity, q-relational-table-unique-data, q-database-migration-purpose
- `moc-algorithms.md` - Referenced by: q-data-structures-overview

**Suggested MOC Structure:**

```markdown
# moc-tools.md
---
topic: tools
type: moc
---

# Tools & Development Environment

## Version Control
- [[c-git]]
- [[c-version-control]]

## Git Commands
- [[q-git-pull-vs-fetch--tools--easy]]
- [[q-git-squash-commits--tools--medium]]
- [[q-git-merge-vs-rebase--tools--medium]]
```

---

## Detailed Broken Links by Source File

### Kotlin Files

#### /70-Kotlin/q-abstract-class-vs-interface--kotlin--medium.md
No broken links

#### /70-Kotlin/q-channel-closing-completion--kotlin--medium.md
- [ ] `q-channel-pipelines--kotlin--hard`

#### /70-Kotlin/q-channel-flow-comparison--kotlin--medium.md
- [ ] `q-flow-basics--kotlin--medium` → Use `q-kotlin-flow-basics--kotlin--medium`
- [ ] `q-sharedflow-stateflow--kotlin--medium`
- [ ] `q-flow-backpressure--kotlin--hard`
- [ ] `q-channel-buffering-strategies--kotlin--hard`

#### /70-Kotlin/q-channels-basics-types--kotlin--medium.md
- [ ] `q-channel-buffering-strategies--kotlin--hard`

#### /70-Kotlin/q-coroutine-context-detailed--kotlin--hard.md
- [ ] `q-coroutine-dispatchers--kotlin--medium`
- [ ] `q-structured-concurrency--kotlin--hard`

#### /70-Kotlin/q-coroutine-exception-handling--kotlin--medium.md
- [ ] `q-coroutinescope-supervisorscope--kotlin--medium` → Use `q-supervisor-scope-vs-coroutine-scope--kotlin--medium`
- [ ] `q-structured-concurrency--kotlin--hard`

#### /70-Kotlin/q-debounce-throttle-flow--kotlin--medium.md
- [ ] `q-flow-operators--kotlin--medium`
- [ ] `q-flow-time-operators--kotlin--medium`

#### /70-Kotlin/q-flatmap-variants-flow--kotlin--medium.md
- [ ] `q-flow-operators--kotlin--medium`
- [ ] `q-flow-basics--kotlin--easy`

#### /70-Kotlin/q-hot-cold-flows--kotlin--medium.md
- [ ] `q-flow-basics--kotlin--medium` → Use `q-kotlin-flow-basics--kotlin--medium`

#### /70-Kotlin/q-kotlin-const--kotlin--easy.md
- [ ] `q-kotlin-val-vs-var--kotlin--easy`

#### /70-Kotlin/q-kotlin-delegation-detailed--kotlin--medium.md
- [ ] `q-lazy-lateinit-kotlin--kotlin--medium` → Use `q-lazy-vs-lateinit--kotlin--medium`

#### /70-Kotlin/q-kotlin-higher-order-functions--kotlin--medium.md
- [ ] `q-kotlin-inline-functions--kotlin--medium`

#### /70-Kotlin/q-kotlin-init-block--kotlin--easy.md
- [ ] `q-kotlin-constructors--kotlin--easy`
- [ ] `q-kotlin-properties--kotlin--easy`

#### /70-Kotlin/q-kotlin-lambda-expressions--kotlin--medium.md
- [ ] `q-kotlin-inline-functions--kotlin--medium`

#### /70-Kotlin/q-kotlin-map-flatmap--kotlin--medium.md
- [ ] `q-kotlin-collections--kotlin--medium`

#### /70-Kotlin/q-kotlin-multiplatform-overview--kotlin--hard.md
- [ ] `q-expect-actual-kotlin--kotlin--medium`
- [ ] `q-kotlin-native--kotlin--hard`

#### /70-Kotlin/q-lifecyclescope-viewmodelscope--kotlin--medium.md
- [ ] `q-repeatonlifecycle--kotlin--medium` → Use `q-repeatonlifecycle-android--kotlin--medium`
- [ ] `q-lifecycle-aware-coroutines--kotlin--hard`

#### /70-Kotlin/q-produce-actor-builders--kotlin--medium.md
- [ ] `q-actor-pattern--kotlin--hard`
- [ ] `q-channel-pipelines--kotlin--hard`

#### /70-Kotlin/q-repeatonlifecycle-android--kotlin--medium.md
- [ ] `q-lifecycle-aware-coroutines--kotlin--hard`

#### /70-Kotlin/q-retry-operators-flow--kotlin--medium.md
- [ ] `q-flow-error-handling--kotlin--medium`
- [ ] `q-catch-operator-flow--kotlin--medium`

#### /70-Kotlin/q-select-expression-channels--kotlin--hard.md
- [ ] `q-advanced-coroutine-patterns--kotlin--hard`
- [ ] `q-fan-in-fan-out--kotlin--hard`

#### /70-Kotlin/q-statein-sharein-flow--kotlin--medium.md
- [ ] `q-stateflow-sharedflow--kotlin--medium` → Use `q-stateflow-sharedflow-differences--kotlin--medium`
- [ ] `q-cold-hot-flow--kotlin--medium` → Use `q-cold-vs-hot-flows--kotlin--medium`

#### /70-Kotlin/q-viewmodel-coroutines-lifecycle--kotlin--medium.md
- [ ] `q-testing-viewmodel-coroutines--kotlin--medium`

### Android Files

#### /40-Android/q-cicd-pipeline-setup--devops--medium.md
- [ ] `-z $(getprop sys.boot_completed)` **MALFORMED - FIX**

#### /40-Android/q-clean-architecture-android--android--hard.md
- [ ] `q-mvvm--android--medium` → Use `q-mvvm-pattern--android--medium`

#### /40-Android/q-compose-modifier-system--android--medium.md
- [ ] `q-jetpack-compose-basics--android--medium`

#### /40-Android/q-compose-navigation-advanced--android--medium.md
- [ ] `q-jetpack-compose-basics--android--medium`

#### /40-Android/q-compose-performance-optimization--android--hard.md
- [ ] `q-recomposition-compose--android--medium`

#### /40-Android/q-compose-semantics--android--medium.md
- [ ] `q-compose-testing--android--medium`

#### /40-Android/q-gradle-kotlin-dsl-vs-groovy--android--medium.md
- [ ] `q-gradle-basics--android--easy`

#### /40-Android/q-kapt-vs-ksp--android--medium.md
- [ ] `q-annotation-processing--android--medium`

#### /40-Android/q-mockk-advanced-features--testing--medium.md
- [ ] `2, 3` **MALFORMED - FIX**

#### /40-Android/q-repository-multiple-sources--android--medium.md
- [ ] `q-repository-pattern--android--medium`

### Backend/Tools/Algorithms Files

#### /20-Algorithms/q-data-structures-overview--algorithms--easy.md
- [ ] `c-data-structures`
- [ ] `c-algorithms`
- [ ] `moc-algorithms`

#### /50-Backend/q-database-migration-purpose--backend--medium.md
- [ ] `c-database-design`
- [ ] `c-migrations`
- [ ] `moc-backend`

#### /50-Backend/q-relational-table-unique-data--backend--medium.md
- [ ] `c-database-design`
- [ ] `c-relational-databases`
- [ ] `moc-backend`

#### /50-Backend/q-sql-join-algorithms-complexity--backend--hard.md
- [ ] `c-sql-queries`
- [ ] `c-database-performance`
- [ ] `c-algorithms`
- [ ] `moc-backend`

#### /50-Backend/q-virtual-tables-disadvantages--backend--medium.md
- [ ] `c-database-performance`
- [ ] `c-views`
- [ ] `moc-backend`

#### /80-Tools/q-git-pull-vs-fetch--tools--easy.md
- [ ] `c-git`
- [ ] `c-version-control`
- [ ] `moc-tools`

#### /80-Tools/q-git-squash-commits--tools--medium.md
- [ ] `c-git`
- [ ] `c-version-control`
- [ ] `moc-tools`

---

## Progress Tracking

Use this checklist to track your progress:

### Phase 1: Quick Wins
- [ ] Fix 7 naming inconsistencies
- [ ] Fix 2 malformed links
- [ ] Total: 9 fixes

### Phase 2: Infrastructure
- [ ] Create moc-tools.md
- [ ] Create moc-backend.md
- [ ] Create moc-algorithms.md
- [ ] Total: 3 files

### Phase 3: Concept Notes
- [ ] Create 6 database concept files
- [ ] Create 2 version control concept files
- [ ] Create 2 algorithm concept files
- [ ] Total: 10 files

### Phase 4: High-Priority Questions
- [ ] Create q-kotlin-inline-functions--kotlin--medium.md
- [ ] Create q-channel-pipelines--kotlin--hard.md
- [ ] Create q-jetpack-compose-basics--android--medium.md
- [ ] Create q-flow-operators--kotlin--medium.md
- [ ] Create q-lifecycle-aware-coroutines--kotlin--hard.md
- [ ] Total: 5 files

### Phase 5: Remaining Questions
- [ ] Create remaining 32 missing question files
- [ ] Total: 32 files

**Grand Total: 59 actions to resolve all broken links**

---

Last Updated: 2025-10-12
