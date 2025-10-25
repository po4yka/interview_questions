---
id: 20251012-400002
title: "LazyGrid & LazyStaggeredGrid / LazyGrid и LazyStaggeredGrid"
topic: android
difficulty: medium
status: draft
created: 2025-10-12
tags: [jetpack-compose, lazy-layout, grid, performance, android/compose, android/lazy-layout, android/grid, android/performance, android/ui, difficulty/medium]
moc: moc-android
related: [q-handler-looper-comprehensive--android--medium, q-compose-navigation-advanced--jetpack-compose--medium, q-koin-vs-hilt-comparison--dependency-injection--medium]
  - q-jetpack-compose-lazy-column--android--easy
  - q-compose-lazy-layout-optimization--jetpack-compose--hard
  - q-paging-library-3--android--medium
subtopics:
  - jetpack-compose
  - lazy-layout
  - grid
  - performance
  - ui
---
# LazyGrid & LazyStaggeredGrid

## English Version

### Problem Statement

LazyVerticalGrid, LazyHorizontalGrid, and LazyStaggeredGrid are essential composables for displaying collections in grid layouts efficiently. Understanding their usage, customization, and performance characteristics is crucial for modern Android development.

**The Question:** How do LazyGrid and LazyStaggeredGrid work? What's the difference between fixed and adaptive columns? How do you handle item spacing, spans, and performance optimization?

### Detailed Answer

---

### LAZYVERTICALGRID BASICS

**Display items in a vertical scrolling grid.**

```kotlin
@Composable
fun BasicGridExample() {
    LazyVerticalGrid(
        columns = GridCells.Fixed(2),  // 2 columns
        modifier = Modifier.fillMaxSize()
    ) {
        items(20) { index ->
            Card(
                modifier = Modifier
                    .padding(8.dp)
                    .aspectRatio(1f),
                elevation = CardDefaults.cardElevation(4.dp)
            ) {
                Box(
                    contentAlignment = Alignment.Center,
                    modifier = Modifier.fillMaxSize()
                ) {
                    Text("Item $index")
                }
            }
        }
    }
}
```

---

### GRIDCELLS TYPES

#### 1. Fixed Columns

```kotlin
@Composable
fun FixedColumnsGrid() {
    LazyVerticalGrid(
        columns = GridCells.Fixed(3),  // Always 3 columns
        contentPadding = PaddingValues(16.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(30) { index ->
            GridItem(index)
        }
    }
}

@Composable
fun GridItem(index: Int) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .aspectRatio(1f),
        colors = CardDefaults.cardColors(
            containerColor = MaterialTheme.colorScheme.primaryContainer
        )
    ) {
        Box(
            modifier = Modifier.fillMaxSize(),
            contentAlignment = Alignment.Center
        ) {
            Text(
                text = "Item $index",
                style = MaterialTheme.typography.titleMedium
            )
        }
    }
}
```

---

#### 2. Adaptive Columns

```kotlin
@Composable
fun AdaptiveColumnsGrid() {
    LazyVerticalGrid(
        // Fit as many columns as possible with min 120.dp width
        columns = GridCells.Adaptive(minSize = 120.dp),
        contentPadding = PaddingValues(16.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(50) { index ->
            GridItem(index)
        }
    }
}

// On phone (360dp wide):
// 360 - 32 (padding) = 328
// 328 / 120 = 2.73 → 2 columns

// On tablet (800dp wide):
// 800 - 32 (padding) = 768
// 768 / 120 = 6.4 → 6 columns
```

**Adaptive vs Fixed:**
```
GridCells.Fixed(3):
 Predictable column count
 Works well for uniform content
 May look bad on different screen sizes

GridCells.Adaptive(120.dp):
 Responsive across screen sizes
 Better for different devices
 Columns adjust automatically
 Column count varies
```

---

#### 3. Custom GridCells

```kotlin
@Composable
fun CustomGridCells() {
    val customColumns = object : GridCells {
        override fun Density.calculateCrossAxisCellSizes(
            availableSize: Int,
            spacing: Int
        ): List<Int> {
            // First column: 1/3 of width
            // Second column: 2/3 of width
            val column1 = availableSize / 3
            val column2 = availableSize - column1 - spacing

            return listOf(column1, column2)
        }
    }

    LazyVerticalGrid(
        columns = customColumns,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(20) { index ->
            GridItem(index)
        }
    }
}
```

---

### LAZYHORIZONTALGRID

**Horizontal scrolling grid.**

```kotlin
@Composable
fun HorizontalGridExample() {
    LazyHorizontalGrid(
        rows = GridCells.Fixed(2),  // 2 rows
        modifier = Modifier
            .fillMaxWidth()
            .height(300.dp),
        contentPadding = PaddingValues(16.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(30) { index ->
            Card(
                modifier = Modifier
                    .width(120.dp)
                    .aspectRatio(1f)
            ) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Text("Item $index")
                }
            }
        }
    }
}
```

---

### ITEM SPANS

**Control how many columns/rows an item occupies.**

```kotlin
@Composable
fun GridWithSpans() {
    val items = (0..20).toList()

    LazyVerticalGrid(
        columns = GridCells.Fixed(3),
        contentPadding = PaddingValues(16.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(
            count = items.size,
            span = { index ->
                // Every 4th item spans all columns
                GridItemSpan(if (index % 4 == 0) maxLineSpan else 1)
            }
        ) { index ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(if (index % 4 == 0) 150.dp else 100.dp),
                colors = CardDefaults.cardColors(
                    containerColor = if (index % 4 == 0) {
                        MaterialTheme.colorScheme.secondaryContainer
                    } else {
                        MaterialTheme.colorScheme.primaryContainer
                    }
                )
            ) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Text(
                        text = if (index % 4 == 0) "Header $index" else "Item $index",
                        style = if (index % 4 == 0) {
                            MaterialTheme.typography.headlineSmall
                        } else {
                            MaterialTheme.typography.bodyLarge
                        }
                    )
                }
            }
        }
    }
}
```

**Real-world span pattern:**
```kotlin
@Composable
fun PhotoGalleryWithHeaders() {
    data class GalleryItem(val id: Int, val isHeader: Boolean, val title: String)

    val items = listOf(
        GalleryItem(0, true, "Recent Photos"),
        GalleryItem(1, false, "Photo 1"),
        GalleryItem(2, false, "Photo 2"),
        GalleryItem(3, false, "Photo 3"),
        GalleryItem(4, true, "Last Week"),
        GalleryItem(5, false, "Photo 4"),
        GalleryItem(6, false, "Photo 5"),
    )

    LazyVerticalGrid(
        columns = GridCells.Adaptive(minSize = 100.dp),
        contentPadding = PaddingValues(16.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(
            count = items.size,
            key = { items[it].id },
            span = { index ->
                val item = items[index]
                GridItemSpan(if (item.isHeader) maxLineSpan else 1)
            }
        ) { index ->
            val item = items[index]

            if (item.isHeader) {
                // Header spans full width
                Text(
                    text = item.title,
                    style = MaterialTheme.typography.titleLarge,
                    modifier = Modifier
                        .fillMaxWidth()
                        .padding(vertical = 8.dp)
                )
            } else {
                // Photo item
                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .aspectRatio(1f)
                ) {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Text(item.title)
                    }
                }
            }
        }
    }
}
```

---

### LAZYSTAGGEREDGRID

**Grid with variable item heights (Pinterest-style layout).**

```kotlin
@Composable
fun StaggeredGridExample() {
    val items = remember {
        (1..50).map {
            GridItemData(
                id = it,
                height = (100..300).random()
            )
        }
    }

    LazyVerticalStaggeredGrid(
        columns = StaggeredGridCells.Fixed(2),
        contentPadding = PaddingValues(16.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalItemSpacing = 8.dp
    ) {
        items(
            count = items.size,
            key = { items[it].id }
        ) { index ->
            val item = items[index]

            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .height(item.height.dp)
            ) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Text("Item ${item.id}")
                }
            }
        }
    }
}

data class GridItemData(val id: Int, val height: Int)
```

---

#### StaggeredGrid with Adaptive Columns

```kotlin
@Composable
fun AdaptiveStaggeredGrid() {
    LazyVerticalStaggeredGrid(
        columns = StaggeredGridCells.Adaptive(minSize = 150.dp),
        contentPadding = PaddingValues(16.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp),
        verticalItemSpacing = 8.dp
    ) {
        items(100) { index ->
            Card(
                modifier = Modifier
                    .fillMaxWidth()
                    .wrapContentHeight()
            ) {
                Column(modifier = Modifier.padding(16.dp)) {
                    Text(
                        text = "Card $index",
                        style = MaterialTheme.typography.titleMedium
                    )

                    // Variable content length
                    repeat((1..5).random()) {
                        Text(
                            text = "Line $it of content",
                            style = MaterialTheme.typography.bodySmall
                        )
                    }
                }
            }
        }
    }
}
```

---

#### Horizontal Staggered Grid

```kotlin
@Composable
fun HorizontalStaggeredGrid() {
    LazyHorizontalStaggeredGrid(
        rows = StaggeredGridCells.Fixed(3),
        modifier = Modifier
            .fillMaxWidth()
            .height(400.dp),
        contentPadding = PaddingValues(16.dp),
        horizontalItemSpacing = 8.dp,
        verticalArrangement = Arrangement.spacedBy(8.dp)
    ) {
        items(50) { index ->
            Card(
                modifier = Modifier
                    .width((100..200).random().dp)
                    .fillMaxHeight()
            ) {
                Box(
                    modifier = Modifier.fillMaxSize(),
                    contentAlignment = Alignment.Center
                ) {
                    Text("Item $index")
                }
            }
        }
    }
}
```

---

### ITEM KEYS & ANIMATIONS

```kotlin
@Composable
fun AnimatedGridItems() {
    var items by remember {
        mutableStateOf((1..20).map { GridItemData(it, (100..200).random()) })
    }

    Column {
        Button(
            onClick = {
                items = items.shuffled()
            }
        ) {
            Text("Shuffle")
        }

        LazyVerticalStaggeredGrid(
            columns = StaggeredGridCells.Fixed(2),
            contentPadding = PaddingValues(16.dp),
            horizontalArrangement = Arrangement.spacedBy(8.dp),
            verticalItemSpacing = 8.dp
        ) {
            items(
                count = items.size,
                key = { items[it].id }  //  Required for animations
            ) { index ->
                val item = items[index]

                Card(
                    modifier = Modifier
                        .fillMaxWidth()
                        .height(item.height.dp)
                        .animateItemPlacement()  //  Animate reordering
                ) {
                    Box(
                        modifier = Modifier.fillMaxSize(),
                        contentAlignment = Alignment.Center
                    ) {
                        Text("Item ${item.id}")
                    }
                }
            }
        }
    }
}
```

---

### REAL-WORLD EXAMPLES

#### Photo Gallery

```kotlin
@Composable
fun PhotoGallery(photos: List<Photo>) {
    var selectedPhoto by remember { mutableStateOf<Photo?>(null) }

    LazyVerticalStaggeredGrid(
        columns = StaggeredGridCells.Adaptive(minSize = 120.dp),
        contentPadding = PaddingValues(4.dp),
        horizontalArrangement = Arrangement.spacedBy(4.dp),
        verticalItemSpacing = 4.dp
    ) {
        items(
            count = photos.size,
            key = { photos[it].id }
        ) { index ->
            val photo = photos[index]

            AsyncImage(
                model = photo.url,
                contentDescription = photo.description,
                modifier = Modifier
                    .fillMaxWidth()
                    .wrapContentHeight()
                    .clickable { selectedPhoto = photo }
                    .clip(RoundedCornerShape(8.dp)),
                contentScale = ContentScale.Crop
            )
        }
    }

    // Full screen dialog
    selectedPhoto?.let { photo ->
        Dialog(onDismissRequest = { selectedPhoto = null }) {
            AsyncImage(
                model = photo.url,
                contentDescription = photo.description,
                modifier = Modifier.fillMaxWidth()
            )
        }
    }
}

data class Photo(
    val id: String,
    val url: String,
    val description: String?,
    val aspectRatio: Float
)
```

---

#### Product Grid with Categories

```kotlin
@Composable
fun ProductGrid(products: List<Product>) {
    LazyVerticalGrid(
        columns = GridCells.Adaptive(minSize = 160.dp),
        contentPadding = PaddingValues(16.dp),
        horizontalArrangement = Arrangement.spacedBy(12.dp),
        verticalArrangement = Arrangement.spacedBy(12.dp)
    ) {
        // Group by category
        products.groupBy { it.category }.forEach { (category, categoryProducts) ->
            // Category header (spans all columns)
            item(span = { GridItemSpan(maxLineSpan) }) {
                Text(
                    text = category,
                    style = MaterialTheme.typography.headlineSmall,
                    modifier = Modifier.padding(vertical = 8.dp)
                )
            }

            // Products in this category
            items(
                count = categoryProducts.size,
                key = { categoryProducts[it].id }
            ) { index ->
                ProductCard(product = categoryProducts[index])
            }
        }
    }
}

@Composable
fun ProductCard(product: Product) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .wrapContentHeight()
    ) {
        Column(modifier = Modifier.padding(12.dp)) {
            AsyncImage(
                model = product.imageUrl,
                contentDescription = product.name,
                modifier = Modifier
                    .fillMaxWidth()
                    .aspectRatio(1f)
                    .clip(RoundedCornerShape(8.dp)),
                contentScale = ContentScale.Crop
            )

            Spacer(modifier = Modifier.height(8.dp))

            Text(
                text = product.name,
                style = MaterialTheme.typography.titleMedium,
                maxLines = 2,
                overflow = TextOverflow.Ellipsis
            )

            Text(
                text = "$${product.price}",
                style = MaterialTheme.typography.bodyLarge,
                color = MaterialTheme.colorScheme.primary,
                modifier = Modifier.padding(top = 4.dp)
            )
        }
    }
}

data class Product(
    val id: String,
    val name: String,
    val price: Double,
    val imageUrl: String,
    val category: String
)
```

---

#### Dashboard with Mixed Content

```kotlin
@Composable
fun Dashboard() {
    LazyVerticalGrid(
        columns = GridCells.Fixed(2),
        contentPadding = PaddingValues(16.dp),
        horizontalArrangement = Arrangement.spacedBy(16.dp),
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        // Large stat card (spans 2 columns)
        item(span = { GridItemSpan(maxLineSpan) }) {
            LargeStatCard(
                title = "Total Revenue",
                value = "$45,231",
                change = "+12.5%"
            )
        }

        // Small stat cards (1 column each)
        item {
            SmallStatCard(title = "Orders", value = "1,234")
        }

        item {
            SmallStatCard(title = "Customers", value = "567")
        }

        // Chart (spans 2 columns)
        item(span = { GridItemSpan(maxLineSpan) }) {
            ChartCard(title = "Sales Overview")
        }

        // Quick actions (1 column each)
        items(4) { index ->
            QuickActionCard(title = "Action ${index + 1}")
        }
    }
}

@Composable
fun LargeStatCard(title: String, value: String, change: String) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .height(150.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Text(text = title, style = MaterialTheme.typography.titleMedium)
            Text(text = value, style = MaterialTheme.typography.displayMedium)
            Text(
                text = change,
                style = MaterialTheme.typography.bodyMedium,
                color = Color.Green
            )
        }
    }
}

@Composable
fun SmallStatCard(title: String, value: String) {
    Card(
        modifier = Modifier
            .fillMaxWidth()
            .height(100.dp)
    ) {
        Column(
            modifier = Modifier
                .fillMaxSize()
                .padding(16.dp),
            verticalArrangement = Arrangement.SpaceBetween
        ) {
            Text(text = title, style = MaterialTheme.typography.bodyMedium)
            Text(text = value, style = MaterialTheme.typography.headlineMedium)
        }
    }
}
```

---

### PERFORMANCE OPTIMIZATION

#### 1. Use Keys

```kotlin
@Composable
fun OptimizedGrid(items: List<Item>) {
    LazyVerticalGrid(
        columns = GridCells.Fixed(2)
    ) {
        items(
            count = items.size,
            key = { items[it].id }  //  Essential for performance
        ) { index ->
            ItemCard(items[index])
        }
    }
}
```

---

#### 2. Avoid Heavy Computations in Item Content

```kotlin
//  Bad: Heavy computation in item
@Composable
fun BadGridItem(data: ComplexData) {
    val processedData = processData(data)  // Called on every recomposition!

    Card { /* Use processedData */ }
}

//  Good: Computation outside or memoized
@Composable
fun GoodGridItem(data: ComplexData) {
    val processedData = remember(data) {
        processData(data)  // Cached!
    }

    Card { /* Use processedData */ }
}
```

---

#### 3. ContentType for Heterogeneous Lists

```kotlin
@Composable
fun OptimizedHeterogeneousGrid(items: List<GridContent>) {
    LazyVerticalGrid(
        columns = GridCells.Fixed(2)
    ) {
        items(
            count = items.size,
            key = { items[it].id },
            contentType = { items[it]::class }  //  Helps reuse composition
        ) { index ->
            when (val item = items[index]) {
                is GridContent.Photo -> PhotoItem(item)
                is GridContent.Video -> VideoItem(item)
                is GridContent.Text -> TextItem(item)
            }
        }
    }
}

sealed class GridContent {
    abstract val id: String

    data class Photo(override val id: String, val url: String) : GridContent()
    data class Video(override val id: String, val url: String) : GridContent()
    data class Text(override val id: String, val text: String) : GridContent()
}
```

---

#### 4. Prefetch Configuration

```kotlin
@Composable
fun GridWithPrefetch() {
    val gridState = rememberLazyGridState()

    LazyVerticalGrid(
        columns = GridCells.Fixed(2),
        state = gridState,
        // Prefetch items before they're visible
        // Default is 2, increase for smoother scrolling
        flingBehavior = ScrollableDefaults.flingBehavior()
    ) {
        items(1000) { index ->
            ItemCard(index)
        }
    }
}
```

---

### STATE & SCROLL POSITION

```kotlin
@Composable
fun GridWithScrollControl() {
    val gridState = rememberLazyGridState()
    val coroutineScope = rememberCoroutineScope()

    Column {
        Button(
            onClick = {
                coroutineScope.launch {
                    // Scroll to top
                    gridState.animateScrollToItem(0)
                }
            }
        ) {
            Text("Scroll to Top")
        }

        LazyVerticalGrid(
            columns = GridCells.Fixed(3),
            state = gridState
        ) {
            items(100) { index ->
                GridItem(index)
            }
        }
    }

    // Show FAB when scrolled down
    val showFab by remember {
        derivedStateOf {
            gridState.firstVisibleItemIndex > 0
        }
    }

    if (showFab) {
        FloatingActionButton(
            onClick = {
                coroutineScope.launch {
                    gridState.animateScrollToItem(0)
                }
            }
        ) {
            Icon(Icons.Default.KeyboardArrowUp, contentDescription = "Scroll to top")
        }
    }
}
```

---

### KEY TAKEAWAYS

1. **LazyVerticalGrid** for vertical scrolling grids
2. **GridCells.Fixed** for fixed column count
3. **GridCells.Adaptive** for responsive layouts
4. **GridItemSpan** to make items span multiple columns
5. **LazyStaggeredGrid** for Pinterest-style variable height items
6. **Always use keys** for better performance and animations
7. **animateItemPlacement** for smooth reordering
8. **contentType** helps optimize heterogeneous lists
9. **rememberLazyGridState** for scroll control
10. **Staggered grids** automatically balance column heights

---

## Russian Version

### Постановка задачи

LazyVerticalGrid, LazyHorizontalGrid и LazyStaggeredGrid - важные composable для эффективного отображения коллекций в виде сеток. Понимание их использования, кастомизации и характеристик производительности критично для современной Android разработки.

**Вопрос:** Как работают LazyGrid и LazyStaggeredGrid? В чём разница между фиксированными и адаптивными колонками? Как управлять отступами, spans и оптимизацией производительности?

### Ключевые выводы

1. **LazyVerticalGrid** для вертикальной прокручиваемой сетки
2. **GridCells.Fixed** для фиксированного количества колонок
3. **GridCells.Adaptive** для адаптивных layouts
4. **GridItemSpan** чтобы элементы занимали несколько колонок
5. **LazyStaggeredGrid** для Pinterest-style элементов переменной высоты
6. **Всегда используйте keys** для лучшей производительности и анимаций
7. **animateItemPlacement** для плавной пересортировки
8. **contentType** помогает оптимизировать гетерогенные списки
9. **rememberLazyGridState** для контроля прокрутки
10. **Staggered grids** автоматически балансируют высоту колонок

## Follow-ups

1. How does LazyGrid prefetching work?
2. What's the performance difference between LazyGrid and FlowRow?
3. How do you implement drag-and-drop in LazyGrid?
4. What are the memory implications of large grids?
5. How do you implement pull-to-refresh for LazyGrid?
6. What's the difference between LazyGrid and LazyColumn with multiple columns?
7. How do you implement infinite scroll with LazyGrid?
8. What are the best practices for image loading in grids?
9. How do you handle item selection in LazyGrid?
10. What is the relationship between LazyGrid and Paging 3?

---

## Related Questions

### Related (Medium)
- [[q-compose-modifier-order-performance--android--medium]] - Compose, Jetpack
- [[q-compositionlocal-advanced--android--medium]] - Compose, Jetpack
- [[q-compose-navigation-advanced--android--medium]] - Compose, Jetpack
- [[q-jetpack-compose-basics--android--medium]] - Compose, Jetpack
- [[q-compose-gesture-detection--android--medium]] - Compose, Jetpack

### Advanced (Harder)
- [[q-compose-stability-skippability--android--hard]] - Compose, Jetpack
- [[q-compose-custom-layout--android--hard]] - Compose, Jetpack
- [[q-compose-slot-table-recomposition--android--hard]] - Compose, Jetpack
