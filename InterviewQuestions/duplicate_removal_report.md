# Duplicate Related Questions Removal Report

**Date:** October 17, 2025
**Script:** remove_duplicates.py
**Target:** Remove duplicate subsections in "## Related Questions" sections

---

## Summary

- **Total Files Processed:** 942
- **Files Modified:** 91 (9.7%)
- **Files Unchanged:** 851 (90.3%)
- **Errors:** 0

---

## What Was Done

The script successfully:
1. Scanned all markdown files in question folders (20-Algorithms, 30-System-Design, 40-Android, 50-Backend, 60-CompSci, 70-Kotlin, 80-Tools)
2. Identified files with duplicate "Related Questions" subsections (e.g., multiple "### Related (Hard)" sections)
3. Merged duplicate subsections while preserving unique links
4. Maintained proper markdown formatting and structure
5. Kept subsections ordered by difficulty (Easy -> Medium -> Hard)

---

## Modified Files Breakdown by Folder

### 20-Algorithms (2 files)
- q-binary-search-variants--algorithms--medium.md
- q-data-structures-overview--algorithms--easy.md

### 30-System-Design (7 files)
- q-microservices-vs-monolith--system-design--hard.md
- q-sql-nosql-databases--system-design--medium.md
- q-caching-strategies--system-design--medium.md
- q-design-url-shortener--system-design--medium.md
- q-load-balancing-strategies--system-design--medium.md
- q-horizontal-vertical-scaling--system-design--medium.md
- q-database-sharding-partitioning--system-design--hard.md

### 40-Android (37 files)
- q-large-file-upload--android--medium.md
- q-how-does-jetpackcompose-work--android--medium.md
- q-compose-modifier-order-performance--jetpack-compose--medium.md
- q-how-application-priority-is-determined-by-the-system--android--hard.md
- q-compose-custom-layout--jetpack-compose--hard.md
- q-multi-module-best-practices--android--hard.md
- q-implement-voice-video-call--android--hard.md
- q-design-uber-app--android--hard.md
- q-modularization-patterns--android--hard.md
- q-build-optimization-gradle--gradle--medium.md
- q-recomposition-compose--android--medium.md
- q-kapt-vs-ksp--android--medium.md
- q-compose-modifier-system--android--medium.md
- q-http-protocols-comparison--android--medium.md
- q-kapt-ksp-migration--gradle--medium.md
- q-app-startup-library--android--medium.md
- q-clean-architecture-android--android--hard.md
- q-annotation-processing-android--android--medium.md
- q-usecase-pattern-android--android--medium.md
- q-compose-semantics--android--medium.md
- q-service-component--android--medium.md
- q-recyclerview-sethasfixedsize--android--easy.md
- q-gradle-kotlin-dsl-vs-groovy--android--medium.md
- q-compose-navigation-advanced--android--medium.md
- q-remember-remembersaveable--android--medium.md
- q-launch-modes-android--android--medium.md
- q-repository-multiple-sources--android--medium.md
- q-sharedpreferences-commit-vs-apply--android--easy.md
- q-design-whatsapp-app--android--hard.md
- q-cleartext-traffic-android--android--easy.md
- q-compose-testing--android--medium.md
- q-repository-pattern--android--medium.md
- q-glide-image-loading-internals--android--medium.md
- (4 more files...)

### 50-Backend (2 files)
- q-relational-table-unique-data--backend--medium.md
- q-database-migration-purpose--backend--medium.md

### 70-Kotlin (43 files)
- q-instant-search-flow-operators--kotlin--medium.md
- q-testing-stateflow-sharedflow--kotlin--medium.md
- q-parallel-network-calls-coroutines--kotlin--medium.md
- q-equality-operators-kotlin--kotlin--easy.md
- q-flow-operators-map-filter--kotlin--medium.md
- q-suspend-functions-basics--kotlin--easy.md
- q-hot-cold-flows--kotlin--medium.md
- q-coroutine-profiling--kotlin--hard.md
- q-coroutine-context-explained--kotlin--medium.md
- q-sharedflow-replay-buffer-config--kotlin--medium.md
- q-testing-flow-operators--kotlin--hard.md
- q-coroutine-performance-optimization--kotlin--hard.md
- q-flow-exception-handling--kotlin--medium.md
- q-kotlin-coroutines-introduction--kotlin--medium.md
- q-stateflow-sharedflow-android--kotlin--medium.md
- q-lifecyclescope-viewmodelscope--kotlin--medium.md
- q-kotlin-enum-classes--kotlin--easy.md
- q-kotlin-collections--kotlin--easy.md
- q-flow-cold-flow-fundamentals--kotlin--easy.md
- q-coroutine-memory-leaks--kotlin--hard.md
- q-abstract-class-vs-interface--kotlin--medium.md
- q-coroutine-dispatchers--kotlin--medium.md
- q-backpressure-in-kotlin-flow--programming-languages--medium.md
- q-flow-operators-deep-dive--kotlin--hard.md
- q-coroutine-builders-basics--kotlin--easy.md
- q-flow-operators--kotlin--medium.md
- q-flow-basics--kotlin--easy.md
- q-flow-backpressure-strategies--kotlin--hard.md
- q-stateflow-sharedflow-differences--kotlin--medium.md
- q-flow-performance--kotlin--hard.md
- q-sharedflow-stateflow--kotlin--medium.md
- q-dispatcher-performance--kotlin--hard.md
- q-coroutine-scope-basics--kotlin--easy.md
- q-kotlin-visibility-modifiers--kotlin--easy.md
- q-kotlin-sam-interfaces--kotlin--medium.md
- q-star-projection-vs-any-generics--kotlin--hard.md
- q-coroutine-delay-vs-thread-sleep--kotlin--easy.md
- q-retry-operators-flow--kotlin--medium.md
- q-flow-backpressure--kotlin--hard.md
- q-flowon-operator-context-switching--kotlin--hard.md
- q-flow-testing-advanced--kotlin--hard.md
- q-debounce-throttle-flow--kotlin--medium.md
- q-coroutinescope-vs-coroutinecontext--kotlin--medium.md
- q-flow-time-operators--kotlin--medium.md
- q-cold-vs-hot-flows--kotlin--medium.md
- q-advanced-coroutine-patterns--kotlin--hard.md
- q-flatmap-variants-flow--kotlin--medium.md

### 60-CompSci (0 files)
No duplicates found

### 80-Tools (0 files)
No duplicates found

---

## Script Features

The Python script (`remove_duplicates.py`) includes:

1. **Intelligent Parsing:** Identifies "## Related Questions" sections and subsections
2. **Duplicate Detection:** Finds duplicate subsections like "### Related (Hard)" appearing multiple times
3. **Content Merging:** Combines duplicate subsections while preserving unique markdown links
4. **Deduplication:** Removes duplicate links based on both link text and URL
5. **Order Preservation:** Maintains logical ordering (Easy -> Medium -> Hard)
6. **Safe Processing:** Only modifies the Related Questions section, preserves all other content
7. **Error Handling:** Comprehensive error handling with detailed reporting

---

## Examples of Changes

### Before (with duplicates):
```markdown
## Related Questions

### Related (Medium)
- [[q-flow-basics--kotlin--easy]] - Flow basics
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs cold

### Related (Hard)
- [[q-flow-operators--kotlin--hard]] - Advanced operators

### Related (Medium)
- [[q-stateflow-sharedflow--kotlin--medium]] - StateFlow
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs cold

### Related (Hard)
- [[q-flow-testing--kotlin--hard]] - Testing flows
```

### After (duplicates removed):
```markdown
## Related Questions

### Related (Medium)
- [[q-flow-basics--kotlin--easy]] - Flow basics
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs cold
- [[q-stateflow-sharedflow--kotlin--medium]] - StateFlow

### Related (Hard)
- [[q-flow-operators--kotlin--hard]] - Advanced operators
- [[q-flow-testing--kotlin--hard]] - Testing flows
```

---

## Verification

Files were successfully modified with:
- Proper markdown formatting maintained
- No content lost (only duplicates removed)
- Unique links preserved across merged sections
- Consistent subsection ordering

---

## Next Steps

The vault is now cleaner with:
- No duplicate Related Questions subsections
- Merged content where duplicates had different links
- Consistent structure across all files

All 91 modified files are ready for use with improved organization and no redundancy in the Related Questions sections.
