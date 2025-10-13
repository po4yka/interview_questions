---
topic: jetpack-compose
tags:
  - jetpack-compose
  - lazy-lists
  - performance
  - optimization
difficulty: hard
status: draft
---

# LazyColumn/LazyRow Performance Optimization

**English**: Optimize LazyColumn/LazyRow performance. Implement custom keys, item reuse, prefetching, and avoid common pitfalls.

**Russian**: Оптимизируйте производительность LazyColumn/LazyRow. Реализуйте кастомные ключи, переиспользование элементов, prefetching и избегайте распространенных ошибок.

## Answer (EN)

LazyColumn and LazyRow are highly optimized composables for displaying large lists, but incorrect usage can lead to poor performance, janky scrolling, and unnecessary recompositions.

### Key Concepts

**1. Composition Reuse**: Lazy layouts reuse compositions for items as they scroll
**2. Subcomposition**: Items are composed on-demand as they enter viewport
**3. Prefetching**: Items are measured ahead of time before becoming visible
**4. Keys**: Stable identifiers for item identity across data changes

### Item Keys - Critical for Performance

Without keys, Compose cannot track item identity across data changes:

```kotlin
// BAD: No keys - entire list recomposes on any change
@Composable
fun BadList(items: List<Item>) {
    LazyColumn {
        items(items) { item ->
            ItemRow(item)
        }
    }
}

// GOOD: With keys - only changed items recompose
@Composable
fun GoodList(items: List<Item>) {
    LazyColumn {
        items(
            items = items,
            key = { item -> item.id }  //  Stable unique key
        ) { item ->
            ItemRow(item)
        }
    }
}
```

**Why keys matter**:
```kotlin
// Without keys:
// Initial: [A, B, C]
// After insert at 0: [D, A, B, C]
// Compose sees: position 0 changed A→D, position 1 changed B→A, etc.
// Result: ALL items recompose!

// With keys:
// Initial: [A(key:1), B(key:2), C(key:3)]
// After insert: [D(key:4), A(key:1), B(key:2), C(key:3)]
// Compose sees: item D added, items A,B,C unchanged
// Result: Only new item D composes!
```

**Key selection guidelines**:
```kotlin
//  GOOD: Database ID
items(users, key = { it.id }) { ... }

//  GOOD: Composite key for uniqueness
items(messages, key = { "${it.userId}_${it.timestamp}" }) { ... }

//  BAD: Index (changes when list changes)
items(items.size) { index ->
    val item = items[index]
    // index is not stable!
}

//  BAD: Non-unique property
items(users, key = { it.name }) { ... }  // Names can duplicate!

//  BAD: Mutable property
items(users, key = { it.lastSeenTime }) { ... }  // Changes over time!
```

### Content Types for Better Reuse

```kotlin
@Composable
fun OptimizedMixedList(items: List<ListItem>) {
    LazyColumn {
        items(
            items = items,
            key = { it.id },
            contentType = { item ->
                when (item) {
                    is TextItem -> "text"
                    is ImageItem -> "image"
                    is VideoItem -> "video"
                    else -> null
                }
            }
        ) { item ->
            when (item) {
                is TextItem -> TextRow(item)
                is ImageItem -> ImageRow(item)
                is VideoItem -> VideoRow(item)
            }
        }
    }
}
```

**Benefits**:
- Compose reuses compositions only within same content type
- Different layouts can have different reuse pools
- Better memory efficiency for heterogeneous lists

### Prefetching Configuration

```kotlin
@Composable
fun CustomPrefetchList(items: List<Item>) {
    val listState = rememberLazyListState()

    // Default prefetch distance is typically 2 items
    // Can be tuned based on item complexity
    LazyColumn(
        state = listState,
        // Prefetch config is internal, but we can optimize items
    ) {
        items(
            items = items,
            key = { it.id }
        ) { item ->
            // Keep item composables lightweight for faster prefetch
            OptimizedItemRow(item)
        }
    }
}
```

**Prefetch optimization tips**:
1. Keep item composables lightweight
2. Defer heavy operations to LaunchedEffect
3. Use async image loading
4. Avoid blocking operations in item composition

### State Hoisting for Item Stability

```kotlin
// BAD: State inside item - lost when scrolled away
@Composable
fun UnstableItem(item: Item) {
    var isExpanded by remember { mutableStateOf(false) }

    ExpandableCard(
        expanded = isExpanded,
        onToggle = { isExpanded = !isExpanded }
    )
}

// GOOD: State hoisted - survives scroll
@Composable
fun StableList(items: List<Item>) {
    // State map survives item recomposition
    val expandedStates = remember { mutableStateMapOf<String, Boolean>() }

    LazyColumn {
        items(
            items = items,
            key = { it.id }
        ) { item ->
            val isExpanded = expandedStates[item.id] ?: false

            ExpandableCard(
                expanded = isExpanded,
                onToggle = {
                    expandedStates[item.id] = !isExpanded
                }
            )
        }
    }
}
```

### Avoid Nested Scrolling Issues

```kotlin
// BAD: Nested lazy layouts
@Composable
fun BadNestedLazy() {
    LazyColumn {
        items(categories) { category ->
            LazyRow {  //  Nested lazy layout
                items(category.items) { item ->
                    ItemCard(item)
                }
            }
        }
    }
}

// GOOD: Single lazy column with groups
@Composable
fun GoodGroupedList(categories: List<Category>) {
    LazyColumn {
        categories.forEach { category ->
            item {
                CategoryHeader(category)
            }
            items(
                items = category.items,
                key = { it.id }
            ) { item ->
                ItemCard(item)
            }
        }
    }
}

// ALTERNATIVE: Horizontal pager for truly nested content
@Composable
fun AlternativeNested() {
    LazyColumn {
        items(categories) { category ->
            HorizontalPager(
                count = category.items.size,
                modifier = Modifier.height(200.dp)
            ) { page ->
                ItemCard(category.items[page])
            }
        }
    }
}
```

### Fixed Height Items for Performance

```kotlin
// GOOD: Fixed height - faster layout
@Composable
fun FixedHeightList(items: List<Item>) {
    LazyColumn {
        items(
            items = items,
            key = { it.id }
        ) { item ->
            ItemRow(
                item = item,
                modifier = Modifier.height(72.dp)  // Fixed height
            )
        }
    }
}

// When variable height needed, minimize differences
@Composable
fun MinimalVarianceList(items: List<Item>) {
    LazyColumn {
        items(
            items = items,
            key = { it.id }
        ) { item ->
            ItemRow(
                item = item,
                // Constrain height variance
                modifier = Modifier.heightIn(min = 64.dp, max = 120.dp)
            )
        }
    }
}
```

### Pagination Implementation

```kotlin
@Composable
fun PaginatedList(
    viewModel: ListViewModel,
    loadMore: () -> Unit
) {
    val items by viewModel.items.collectAsState()
    val listState = rememberLazyListState()

    // Detect when near bottom
    val isScrolledToBottom by remember {
        derivedStateOf {
            val layoutInfo = listState.layoutInfo
            val lastVisible = layoutInfo.visibleItemsInfo.lastOrNull()
            lastVisible != null && lastVisible.index >= layoutInfo.totalItemsCount - 3
        }
    }

    // Trigger load more
    LaunchedEffect(isScrolledToBottom) {
        if (isScrolledToBottom) {
            loadMore()
        }
    }

    LazyColumn(state = listState) {
        items(
            items = items,
            key = { it.id }
        ) { item ->
            ItemRow(item)
        }

        if (viewModel.isLoadingMore) {
            item {
                Box(
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(16.dp),
                    contentAlignment = Alignment.Center
                ) {
                    CircularProgressIndicator()
                }
            }
        }
    }
}
```

### Sticky Headers

```kotlin
@Composable
fun ListWithStickyHeaders(groupedItems: Map<String, List<Item>>) {
    LazyColumn {
        groupedItems.forEach { (header, items) ->
            stickyHeader {
                SectionHeader(header)
            }
            items(
                items = items,
                key = { it.id }
            ) { item ->
                ItemRow(item)
            }
        }
    }
}

@Composable
fun SectionHeader(text: String) {
    Box(
        modifier = Modifier
            .fillMaxWidth()
            .background(MaterialTheme.colorScheme.primaryContainer)
            .padding(16.dp)
    ) {
        Text(
            text = text,
            style = MaterialTheme.typography.titleMedium
        )
    }
}
```

### Performance Monitoring

```kotlin
@Composable
fun MonitoredList(items: List<Item>) {
    val listState = rememberLazyListState()

    // Log scroll performance metrics
    LaunchedEffect(listState) {
        snapshotFlow { listState.layoutInfo }
            .collect { layoutInfo ->
                Log.d("LazyList", """
                    Visible items: ${layoutInfo.visibleItemsInfo.size}
                    Total items: ${layoutInfo.totalItemsCount}
                    Viewport: ${layoutInfo.viewportStartOffset} to ${layoutInfo.viewportEndOffset}
                    First visible: ${layoutInfo.visibleItemsInfo.firstOrNull()?.index}
                """.trimIndent())
            }
    }

    LazyColumn(state = listState) {
        items(items, key = { it.id }) { item ->
            ItemRow(item)
        }
    }
}
```

### Complete Optimized Example

```kotlin
data class Message(
    val id: String,
    val userId: String,
    val text: String,
    val timestamp: Long,
    val type: MessageType
)

enum class MessageType { TEXT, IMAGE, VIDEO }

@Composable
fun OptimizedMessageList(
    messages: List<Message>,
    onLoadMore: () -> Unit,
    isLoading: Boolean
) {
    val listState = rememberLazyListState()
    val expandedMessages = remember { mutableStateMapOf<String, Boolean>() }

    // Auto-load more when near bottom
    LaunchedEffect(listState) {
        snapshotFlow {
            val layoutInfo = listState.layoutInfo
            val lastVisible = layoutInfo.visibleItemsInfo.lastOrNull()
            lastVisible != null &&
            lastVisible.index >= layoutInfo.totalItemsCount - 5
        }
        .distinctUntilChanged()
        .collect { shouldLoad ->
            if (shouldLoad && !isLoading) {
                onLoadMore()
            }
        }
    }

    LazyColumn(
        state = listState,
        modifier = Modifier.fillMaxSize()
    ) {
        items(
            items = messages,
            key = { it.id },
            contentType = { it.type }
        ) { message ->
            val isExpanded = expandedMessages[message.id] ?: false

            MessageRow(
                message = message,
                isExpanded = isExpanded,
                onToggleExpand = {
                    expandedMessages[message.id] = !isExpanded
                },
                modifier = Modifier
                    .fillMaxWidth()
                    .animateItemPlacement()
            )
        }

        if (isLoading) {
            item(key = "loading") {
                LoadingIndicator(Modifier.fillMaxWidth())
            }
        }
    }
}

@Composable
fun MessageRow(
    message: Message,
    isExpanded: Boolean,
    onToggleExpand: () -> Unit,
    modifier: Modifier = Modifier
) {
    Card(
        modifier = modifier.padding(horizontal = 16.dp, vertical = 8.dp),
        onClick = onToggleExpand
    ) {
        Column(modifier = Modifier.padding(16.dp)) {
            Text(
                text = message.text,
                maxLines = if (isExpanded) Int.MAX_VALUE else 2,
                overflow = TextOverflow.Ellipsis
            )
            Text(
                text = formatTimestamp(message.timestamp),
                style = MaterialTheme.typography.bodySmall
            )
        }
    }
}
```

### Common Pitfalls

**1. Missing keys**:
```kotlin
//  No keys - poor performance on updates
items(list) { item -> ItemRow(item) }

//  With keys
items(list, key = { it.id }) { item -> ItemRow(item) }
```

**2. Non-unique keys**:
```kotlin
//  Index as key (changes when list reorders)
itemsIndexed(list) { index, item ->
    key(index) { ItemRow(item) }
}

//  Stable ID as key
items(list, key = { it.id }) { item -> ItemRow(item) }
```

**3. Heavy composition**:
```kotlin
//  Heavy operations in composition
@Composable
fun HeavyItem(item: Item) {
    val processed = processHeavyData(item.data)  // Blocking!
    ItemRow(processed)
}

//  Defer to LaunchedEffect
@Composable
fun OptimizedItem(item: Item) {
    var processed by remember { mutableStateOf<ProcessedData?>(null) }

    LaunchedEffect(item.id) {
        processed = withContext(Dispatchers.Default) {
            processHeavyData(item.data)
        }
    }

    processed?.let { ItemRow(it) } ?: LoadingPlaceholder()
}
```

### Best Practices

1. **Always use keys** with stable, unique identifiers
2. **Use contentType** for heterogeneous lists
3. **Hoist state** that should survive scrolling
4. **Avoid nested lazy layouts** - flatten when possible
5. **Keep items lightweight** - defer heavy work
6. **Use fixed heights** when possible
7. **Implement pagination** for large datasets
8. **Test with large datasets** (1000+ items)
9. **Monitor performance** with Layout Inspector
10. **Profile scroll performance** with frame timing

## Ответ (RU)

LazyColumn и LazyRow - высоко оптимизированные composables для отображения больших списков, но неправильное использование может привести к плохой производительности.

### Ключевые концепции

**1. Переиспользование композиции**: Lazy layouts переиспользуют композиции элементов при прокрутке
**2. Subcomposition**: Элементы создаются по требованию при входе во viewport
**3. Prefetching**: Элементы измеряются заранее перед тем как стать видимыми
**4. Ключи**: Стабильные идентификаторы для отслеживания элементов

[Полные примеры приведены в английском разделе]

### Лучшие практики

1. **Всегда используйте ключи** со стабильными уникальными идентификаторами
2. **Используйте contentType** для гетерогенных списков
3. **Поднимайте state** который должен пережить прокрутку
4. **Избегайте вложенных lazy layouts**
5. **Делайте элементы легковесными**
6. **Используйте фиксированные высоты** когда возможно
7. **Реализуйте pagination** для больших датасетов
8. **Тестируйте на больших данных** (1000+ элементов)
9. **Мониторьте производительность** с Layout Inspector
10. **Профилируйте прокрутку** с frame timing

---

## Related Questions

### Prerequisites (Easier)
- [[q-compose-modifier-order-performance--jetpack-compose--medium]] - Performance, Compose
- [[q-compositionlocal-advanced--jetpack-compose--medium]] - Compose, Jetpack
- [[q-compose-navigation-advanced--jetpack-compose--medium]] - Compose, Jetpack

### Related (Hard)
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Compose, Jetpack
- [[q-compose-custom-layout--jetpack-compose--hard]] - Compose, Jetpack
- [[q-compose-performance-optimization--android--hard]] - Performance, Compose
- [[q-compose-slot-table-recomposition--jetpack-compose--hard]] - Compose, Jetpack
- [[q-compose-side-effects-advanced--jetpack-compose--hard]] - Compose, Jetpack

---

## Related Questions

### Prerequisites (Easier)
- [[q-compose-modifier-order-performance--jetpack-compose--medium]] - Performance, Compose
- [[q-compositionlocal-advanced--jetpack-compose--medium]] - Compose, Jetpack
- [[q-compose-navigation-advanced--jetpack-compose--medium]] - Compose, Jetpack

### Related (Hard)
- [[q-compose-stability-skippability--jetpack-compose--hard]] - Compose, Jetpack
- [[q-compose-custom-layout--jetpack-compose--hard]] - Compose, Jetpack
- [[q-compose-performance-optimization--android--hard]] - Performance, Compose
- [[q-compose-slot-table-recomposition--jetpack-compose--hard]] - Compose, Jetpack
- [[q-compose-side-effects-advanced--jetpack-compose--hard]] - Compose, Jetpack
