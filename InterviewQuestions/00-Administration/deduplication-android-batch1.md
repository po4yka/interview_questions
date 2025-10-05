# Deduplication Analysis - Android Batch 1 (Kirchhoff Repository)

## Summary
- Total analyzed: 30
- Exact duplicates: 5
- Similar (50%+ overlap): 10
- Unique to import: 15

## Detailed Results

### EXACT_DUPLICATE (Skip These - 5 items)

1. **Activity Lifecycle.md** → `/40-Android/q-activity-lifecycle-methods--android--medium.md`
   - Reason: We already have comprehensive coverage of Activity lifecycle methods (onCreate, onStart, onResume, onPause, onStop, onDestroy)

2. **Difference between Room and SQLite.md** → `/40-Android/q-room-vs-sqlite--android--medium.md`
   - Reason: Exact same topic - differences between Room and SQLite, including compile-time validation, boilerplate code reduction

3. **What is Context.md** → Multiple files cover Context extensively
   - Reason: Context is already covered in various questions related to Application vs Activity context

4. **What is Fragment.md** → `/40-Android/q-what-are-fragments-for-if-there-is-activity--android--medium.md` and `/40-Android/q-what-are-fragments-and-why-are-they-more-convenient-to-use-instead-of-multiple-activities--android--hard.md`
   - Reason: Multiple files already explain fragments, their modularity, lifecycle, and usage patterns

5. **What's WorkManager.md** → `/40-Android/q-workmanager-decision-guide--android--medium.md` and related files
   - Reason: WorkManager is extensively covered with decision guides, data passing, return results

### SIMILAR (Review These - 10 items)

1. **What do you know about side effects in jetpack compose.md**
   - Existing coverage: `/40-Android/q-compose-side-effects-launchedeffect-disposableeffect--android--hard.md`
   - Overlap %: 90%
   - Recommendation: Skip - Existing file covers LaunchedEffect, DisposableEffect, rememberCoroutineScope, rememberUpdatedState, SideEffect, produceState, derivedStateOf

2. **What do you know about tasks and the back stack.md**
   - Existing coverage: `/40-Android/q-activity-navigation-how-it-works--android--medium.md`
   - Overlap %: 60%
   - Recommendation: Merge - Source has good diagrams and explanations of back stack lifecycle, could enhance existing content

3. **What is background task and how it should be performed.md**
   - Existing coverage: `/40-Android/q-workmanager-decision-guide--android--medium.md`, `/40-Android/q-async-operations-android--android--medium.md`
   - Overlap %: 70%
   - Recommendation: Skip - Existing files cover asynchronous work, task scheduling APIs, foreground services

4. **What's View.md**
   - Existing coverage: `/40-Android/q-what-is-a-view-and-what-is-responsible-for-its-visual-part--android--medium.md`, `/40-Android/q-view-methods-and-their-purpose--android--medium.md`
   - Overlap %: 80%
   - Recommendation: Skip - View hierarchy, properties, IDs, event handling already covered

5. **What is the difference between Dialog & DialogFragment.md**
   - Existing coverage: `/40-Android/q-kakaya-raznitsa-mezhdu-dialogom-i-fragmentom--android--medium.md`
   - Overlap %: 100%
   - Recommendation: Skip - Same content in Russian file

6. **Describe android modularization in general.md**
   - Existing coverage: `/40-Android/q-multiple-manifests-multimodule--android--medium.md` (partial)
   - Overlap %: 40%
   - Recommendation: Import - Good overview of modularization benefits, pitfalls, but existing files only touch on specific aspects

7. **What types of modules do you know.md**
   - Existing coverage: None specific
   - Overlap %: 30%
   - Recommendation: Import - Covers data modules, feature modules, app modules, common modules, test modules in detail

8. **What do you know about Parcelable.md**
   - Existing coverage: `/40-Android/q-how-to-pass-data-from-one-activity-to-another--android--medium.md`, `/40-Android/q-bundle-data-types--android--medium.md`
   - Overlap %: 50%
   - Recommendation: Import as separate topic - Parcelable deserves its own question with implementation details

9. **What you know about DataStore.md**
   - Existing coverage: `/40-Android/q-android-storage-types--android--medium.md`, `/40-Android/q-sharedpreferences-definition--android--easy.md`
   - Overlap %: 40%
   - Recommendation: Import - DataStore is newer technology, comprehensive coverage of Preferences vs Proto DataStore

10. **What do you know about View Binding.md**
    - Existing coverage: `/40-Android/q-what-is-data-binding--android--easy.md`
    - Overlap %: 30%
    - Recommendation: Import - View Binding is different from Data Binding, deserves separate question

### UNIQUE (Import These - 15 items)

1. **What do you know about App Bundles.md**
   - Topic: Android App Bundle (AAB) format, dynamic delivery, size restrictions
   - Recommended difficulty: easy
   - Target folder: 40-Android/
   - Reason: AAB is important modern Android development topic not covered

2. **What do you know about ArrayMap.md**
   - Topic: ArrayMap data structure, memory efficiency vs HashMap, binary search implementation
   - Recommended difficulty: medium
   - Target folder: 40-Android/
   - Reason: Performance optimization topic, not found in vault

3. **What do you know about Auto Backup.md**
   - Topic: Auto Backup for Apps, cloud backup, device-to-device transfer, backup rules
   - Recommended difficulty: medium
   - Target folder: 40-Android/
   - Reason: Data persistence and user experience topic not covered

4. **What do you know about CompositionLocal.md**
   - Topic: CompositionLocal in Jetpack Compose, implicit data sharing, compositionLocalOf vs staticCompositionLocalOf
   - Recommended difficulty: hard
   - Target folder: 40-Android/
   - Reason: Advanced Compose topic not in vault

5. **What do you know about Converters in Room.md**
   - Topic: TypeConverters in Room, custom data type handling, @TypeConverter annotation
   - Recommended difficulty: medium
   - Target folder: 40-Android/
   - Reason: Room-specific feature not covered separately

6. **What do you know about Intent Filter.md**
   - Topic: Intent filters in AndroidManifest, deep linking, implicit intents, action/category/data elements
   - Recommended difficulty: medium
   - Target folder: 40-Android/
   - Reason: Core Android component topic with comprehensive coverage

7. **What do you know about Play Feature Delivery.md**
   - Topic: Dynamic feature modules, conditional/on-demand delivery, feature module build configuration
   - Recommended difficulty: medium
   - Target folder: 40-Android/
   - Reason: Modern app distribution feature not covered

8. **What do you know about Version catalog.md**
   - Topic: Gradle version catalogs, dependency management, TOML format, type-safe accessors
   - Recommended difficulty: medium
   - Target folder: 40-Android/
   - Reason: Modern Gradle feature for dependency management

9. **What are Sticky Intent.md**
   - Topic: Sticky broadcasts, sendStickyBroadcast, BATTERY_LOW example
   - Recommended difficulty: easy
   - Target folder: 40-Android/
   - Reason: Specific Intent type not covered (deprecated but still interview topic)

10. **Difference between raw and assets folders.md**
    - Topic: res/raw vs assets folder, R class ID generation, access methods
    - Recommended difficulty: easy
    - Target folder: 40-Android/
    - Reason: Resource management fundamentals

11. **What is installLocation tag in AndroidManifest.md**
    - Topic: installLocation attribute, internalOnly/auto/preferExternal, APK install location
    - Recommended difficulty: easy
    - Target folder: 40-Android/
    - Reason: Manifest configuration detail

12. **What is Spannable.md**
    - Topic: Spannable text styling, SpannedString/SpannableString/SpannableStringBuilder, appearance vs metric spans
    - Recommended difficulty: medium
    - Target folder: 40-Android/
    - Reason: Text formatting API not covered

13. **What is StrictMode.md**
    - Topic: StrictMode developer tool, detecting disk/network on main thread, penalty types
    - Recommended difficulty: medium
    - Target folder: 40-Android/
    - Reason: Performance debugging tool not covered

14. **What security best practices you know.md**
    - Topic: Security best practices - app chooser, signature permissions, SSL, WebView security, data storage
    - Recommended difficulty: medium
    - Target folder: 40-Android/
    - Reason: Security is important topic with comprehensive coverage

15. **What's Widget.md**
    - Topic: Home screen widgets, widget types (information/collection/control/hybrid), lifecycle, limitations
    - Recommended difficulty: medium
    - Target folder: 40-Android/
    - Reason: App widgets not covered in vault

## Import Priority

### High Priority (Import Immediately - 8 items)
1. What do you know about App Bundles.md
2. What do you know about Intent Filter.md
3. What do you know about Version catalog.md
4. What you know about DataStore.md
5. What do you know about View Binding.md
6. What do you know about CompositionLocal.md
7. What security best practices you know.md
8. What is StrictMode.md

### Medium Priority (Import Soon - 7 items)
1. Describe android modularization in general.md
2. What types of modules do you know.md
3. What do you know about Parcelable.md
4. What do you know about Converters in Room.md
5. What do you know about Play Feature Delivery.md
6. What is Spannable.md
7. What's Widget.md

### Low Priority (Import Later - 4 items)
1. What do you know about ArrayMap.md
2. What do you know about Auto Backup.md
3. What are Sticky Intent.md
4. Difference between raw and assets folders.md
5. What is installLocation tag in AndroidManifest.md
6. What do you know about tasks and the back stack.md (merge with existing)

## Notes

- Several Russian-language files in vault (`kakaya-raznitsa-mezhdu-dialogom-i-fragmentom`, etc.) should be reviewed for potential cleanup/translation
- Consider creating a "Compose Advanced" category for CompositionLocal and other advanced Compose topics
- Security best practices file is comprehensive and should be tagged appropriately
- Version catalog is becoming standard practice in modern Android, high priority import
- Some exact duplicates could be consolidated to avoid redundancy
