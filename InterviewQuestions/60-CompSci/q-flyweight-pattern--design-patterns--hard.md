---
id: cs-012
title: "Flyweight Pattern / Паттерн легкий вес"
aliases: [Flyweight Pattern, Паттерн легкий вес]
topic: cs
subtopics: [design-patterns, memory-optimization, structural-patterns]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-cs
related: [c-computer-science, c-architecture-patterns, q-abstract-factory-pattern--cs--medium]
created: 2025-10-15
updated: 2025-11-11
tags: [cs, difficulty/hard, flyweight, gof-patterns, memory-optimization, structural-patterns]

---

# Вопрос (RU)
> Что такое паттерн Flyweight? Когда и зачем его использовать?

# Question (EN)
> What is the Flyweight pattern? When and why should it be used?

---

## Ответ (RU)

### Определение

**Flyweight (Легковес/Приспособленец)** — это структурный паттерн проектирования, который позволяет эффективно работать с очень большим количеством похожих объектов за счёт разделения общего (внутреннего, intrinsic) состояния между ними. Общие, как правило неизменяемые данные хранятся в разделяемых объектах, а контекстно-зависимое (внешнее, extrinsic) состояние передаётся снаружи при использовании.

### Проблемы, которые решает

Паттерн Flyweight решает следующие задачи:

1. Необходимость эффективно поддерживать огромное количество однотипных объектов.
2. Необходимость избежать дублирования тяжёлого общего состояния в каждом объекте.

Пример: в текстовом редакторе хранить полный набор данных (глиф, метрики, шрифт) для каждого символа дорого. Вместо этого глифы и метрики шрифта разделяются, а позиции и оформление хранятся отдельно.

### Решение

Определяются объекты `Flyweight`, которые:

- Хранят внутреннее (инвариантное, общее) состояние.
- Предоставляют операции, принимающие внешнее (вариативное, контекстное) состояние как параметры.

Клиенты:

- Получают flyweight-объекты из фабрики/кэша и переиспользуют их.
- Передают внешнее состояние (позиция, цвет, контекст) при каждом вызове.

Это значительно уменьшает объём дублируемых данных без отказа от объектной модели.

### Ключевые концепции

- Внутреннее состояние (intrinsic): общее, разделяемое, хранится внутри Flyweight и должно быть по сути неизменяемым (например, глиф символа, bitmap иконки, внешний вид частицы).
- Внешнее состояние (extrinsic): контекстно-зависимое, не разделяется, передаётся клиентом (например, позиция, цвет, скорость, конкретный контекст использования).

### Пример: символы в текстовом редакторе

```kotlin
// Интерфейс Flyweight
interface CharacterFlyweight {
    fun display(row: Int, column: Int, font: String)
}

// Конкретный flyweight: внутреннее состояние — сам символ
class Character(private val char: Char) : CharacterFlyweight {
    override fun display(row: Int, column: Int, font: String) {
        println("Displaying '$char' at ($row, $column) with font $font")
    }
}

// Фабрика Flyweight: управляет общими экземплярами Character
class CharacterFactory {
    private val characters = mutableMapOf<Char, CharacterFlyweight>()

    fun getCharacter(char: Char): CharacterFlyweight {
        return characters.getOrPut(char) {
            println("Creating new flyweight for '$char'")
            Character(char)
        }
    }

    fun getTotalFlyweights() = characters.size
}

// Клиент: хранит внешнее состояние (позицию) отдельно
class TextEditor {
    private val factory = CharacterFactory()
    private val document = mutableListOf<Triple<CharacterFlyweight, Int, Int>>()

    fun insertCharacter(char: Char, row: Int, column: Int) {
        val flyweight = factory.getCharacter(char)
        document.add(Triple(flyweight, row, column))
    }

    fun display(font: String) {
        document.forEach { (char, row, col) ->
            char.display(row, col, font) // font — внешнее состояние
        }
        println("Total unique characters: ${factory.getTotalFlyweights()}")
    }
}
```

Здесь символ (`char`) и логика его отображения являются внутренним состоянием, а позиция и шрифт — внешним.

### Android пример: кэш иконок

```kotlin
// Flyweight: общий bitmap для заданного resourceId
data class IconBitmap(
    val bitmap: Bitmap
)

// Фабрика Flyweight с кэшем в памяти (упрощённо)
class IconCache(private val context: Context) {
    // Для краткости считаем размер единичным. В реальности sizeOf должен учитывать байты.
    private val cache = object : LruCache<Int, IconBitmap>(128) {}

    fun getIcon(resourceId: Int): IconBitmap {
        val cached = cache.get(resourceId)
        if (cached != null) return cached

        val bitmap = BitmapFactory.decodeResource(context.resources, resourceId)
        val icon = IconBitmap(bitmap)
        cache.put(resourceId, icon)
        return icon
    }

    fun clear() = cache.evictAll()
}

// Использование в RecyclerView
class AppAdapter(
    private val apps: List<AppInfo>,
    private val iconCache: IconCache
) : RecyclerView.Adapter<AppViewHolder>() {

    override fun onBindViewHolder(holder: AppViewHolder, position: Int) {
        val app = apps[position]
        val icon = iconCache.getIcon(app.iconResourceId)
        holder.imageView.setImageBitmap(icon.bitmap)
        holder.textView.text = app.name
    }

    override fun getItemCount(): Int = apps.size

    // ... onCreateViewHolder и др.
}
```

Тяжёлые bitmap-ы общие для всех элементов, используют идею Flyweight.

### Kotlin пример: частицы в игре

```kotlin
// Flyweight — общий внешний вид частицы (внутреннее состояние)
data class ParticleType(
    val color: String,
    val sprite: String,
    val size: Int
) {
    fun draw(x: Int, y: Int, velocity: Pair<Int, Int>) {
        println("Drawing $color $sprite particle at ($x, $y) moving $velocity")
    }
}

// Фабрика Flyweight
object ParticleFactory {
    private val types = mutableMapOf<String, ParticleType>()

    fun getParticleType(
        color: String,
        sprite: String,
        size: Int
    ): ParticleType {
        val key = "$color-$sprite-$size"
        return types.getOrPut(key) {
            println("Creating new particle type: $key")
            ParticleType(color, sprite, size)
        }
    }
}

// Частица с внешним состоянием (позиция, скорость)
data class Particle(
    val type: ParticleType,
    var x: Int,
    var y: Int,
    var velocity: Pair<Int, Int>
) {
    fun move() {
        x += velocity.first
        y += velocity.second
    }

    fun draw() = type.draw(x, y, velocity)
}

// Система с большим количеством частиц и немногими типами
class ParticleSystem {
    private val particles = mutableListOf<Particle>()

    fun addParticle(
        x: Int, y: Int,
        color: String, sprite: String, size: Int,
        velocity: Pair<Int, Int>
    ) {
        val type = ParticleFactory.getParticleType(color, sprite, size)
        particles.add(Particle(type, x, y, velocity))
    }

    fun update() {
        particles.forEach { it.move() }
    }

    fun render() {
        particles.forEach { it.draw() }
    }
}
```

Экономия памяти достигается за счёт разделения `ParticleType` (внутреннее состояние), при этом каждая `Particle` хранит только свои координаты и скорость.

### Пояснение

- Внутреннее состояние (глифы, внешний вид частицы, bitmap иконки) разделяется между многими объектами и должно быть по сути неизменяемым.
- Внешнее состояние (позиция, скорость, текущий шрифт, контекст) передаётся при каждом использовании.
- Фабрика или кэш управляет пулом flyweight-объектов, обеспечивая их переиспользование.
- Экономия памяти достигается за счёт избегания дублирования тяжёлых данных (а не полного устранения объектов).
- Типичные применения: кэши иконок/bitmap, текстовый рендеринг, пулы строк, системы частиц, тайловые карты.

### Применение

Используйте Flyweight, если одновременно выполняются условия:

- Нужны очень многие однотипные объекты.
- У них есть существенная доля общего, преимущественно неизменяемого состояния.
- Важна экономия памяти.
- Дополнительная сложность разделения состояния оправдана.

Примеры:

- Текстовые редакторы: общие глифы и метрики шрифтов.
- Игровые частицы: общие типы частиц при разных координатах.
- Кэширование иконок: общие bitmap для повторяющихся иконок.
- Пулы строк / интернирование строк.
- Тайловые карты и ресурсы, которые повторяются очень часто.

### Преимущества

1. Экономия памяти — сокращает дублирование общего состояния.
2. Повышение производительности — меньше тяжёлых объектов для создания и GC.
3. Масштабируемость — позволяет обрабатывать очень большие наборы объектов.
4. Централизованное управление — фабрика/кэш управляет жизненным циклом flyweight.

### Недостатки

1. Сложность — нужно аккуратно выделить внутреннее и внешнее состояние.
2. Нагрузка на CPU — дополнительные обращения к фабрике/кэшу и косвенность.
3. Требование неизменяемости — внутреннее состояние должно быть по сути неизменяемым.
4. Потокобезопасность — фабрика и кэш должны быть корректно синхронизированы в многопоточной среде.

### Лучшие практики

```kotlin
// ИСПОЛЬЗУЙТЕ: когда есть большие массивы однотипных элементов с общим тяжёлым состоянием
class TileMap {
    private val tileFactory = TileFactory()
    private val map = Array(1000) { Array(1000) { TileType.GRASS } }

    fun setTile(x: Int, y: Int, type: TileType) {
        map[x][y] = type
    }

    fun render() {
        map.forEachIndexed { x, row ->
            row.forEachIndexed { y, type ->
                tileFactory.getTile(type).draw(x, y)
            }
        }
    }
}

// ДЕЛАЙТЕ: внутреннее состояние flyweight неизменяемым
data class Tile(val image: String, val walkable: Boolean) {
    fun draw(x: Int, y: Int) { /* ... */ }
}

// ДЕЛАЙТЕ: аккуратно выбирайте семантику ссылок в кэшах
// (WeakHashMap ослабляет только ключи; значения могут оставаться сильно достижимыми.)
class ResourceCache {
    private val cache = WeakHashMap<String, Resource>()
}

// ДЕЛАЙТЕ: комбинируйте с паттерном Factory для централизованного шаринга
object FontCache {
    private val fonts = mutableMapOf<Pair<String, Int>, Typeface>()

    fun getFont(name: String, size: Int): Typeface {
        return fonts.getOrPut(name to size) {
            // Создать и вернуть Typeface
        }
    }
}

// НЕ ДЕЛАЙТЕ: использовать Flyweight там, где объекты почти не переиспользуются.
// НЕ ДЕЛАЙТЕ: шарить внешнее (изменяемое, контекстное) состояние между клиентами.
// НЕ ДЕЛАЙТЕ: делать flyweight изменяемым так, чтобы это неожиданно влияло на всех клиентов.
```

### Краткое резюме (RU)

Flyweight — структурный паттерн, минимизирующий использование памяти за счёт разделения общего, по сути неизменяемого состояния между множеством похожих объектов и передачи внешнего состояния извне. Экономия достигается за счёт избежания дублирования тяжёлых общих данных, а не за счёт полного устранения объектов. Применяется при очень большом количестве однотипных объектов с общей тяжёлой частью данных и значимой нагрузкой на память. Типичные кейсы: глифы при рендеринге текста, кэши иконок/bitmap, пулы строк, системы частиц, тайловые карты.

### Дополнительные вопросы (RU)

- Как вы бы комбинировали Flyweight с Factory или пулом объектов на вашей платформе?
- В каких случаях Flyweight станет преждевременной оптимизацией или излишним усложнением?
- Как спроектировать потокобезопасную Flyweight-фабрику для высоконагруженной системы?
- Как соотнести Flyweight с кэшем на основе `WeakHashMap` или мемоизацией тяжёлых объектов?
- Как с помощью профилирования/метрик проверить, что Flyweight действительно даёт выигрыш в вашей системе?

### Похожие вопросы (RU)

- [[q-abstract-factory-pattern--cs--medium]]

### Ссылки (RU)

- [Flyweight pattern](https://en.wikipedia.org/wiki/Flyweight_pattern)
- [Flyweight Design Pattern](https://howtodoinjava.com/design-patterns/structural/flyweight-design-pattern/)
- [Flyweight](https://refactoring.guru/design-patterns/flyweight)
- [Flyweight Design Pattern](https://sourcemaking.com/design_patterns/flyweight)

---

## Answer (EN)

Flyweight is a structural design pattern that lets you use a large number of objects efficiently by sharing common (intrinsic) state instead of storing it separately in each object. It reduces memory consumption by separating shared, immutable data from per-use, context-specific (extrinsic) data.

### Definition

A flyweight is an object that:

- Minimizes memory usage by sharing as much data as possible with other similar objects.
- Stores intrinsic (shared) state.
- Accepts extrinsic (context-dependent) state as parameters when performing operations.

It's used when you need many fine-grained objects and a naive representation would consume unacceptable memory.

### Problems it Solves

The Flyweight pattern solves problems such as:

1. Need to efficiently support a very large number of similar objects.
2. Need to avoid duplicating heavy, shared state across those objects.

Example: In a text editor, creating a full object with font metrics and glyph data for every single character leads to huge memory consumption. With Flyweight, glyph data is shared, while positions and formatting are stored externally.

### Solution

Define `Flyweight` objects that:

- Store intrinsic (invariant, shared) state.
- Expose methods that take extrinsic (variant, context) state as parameters.

Clients:

- Reuse flyweight instances (usually via a factory that manages a pool / cache).
- Provide extrinsic state upon each use (e.g., position, color, context).

This reduces the amount of duplicated data while preserving object-oriented structure.

### Key Concepts

- Intrinsic state: Shared, stored in Flyweight (e.g., character glyph, icon bitmap, particle appearance).
- Extrinsic state: Context-dependent, passed by client (e.g., position, color, velocity, current context).

### Example: Text Editor Characters

```kotlin
// Flyweight interface
interface CharacterFlyweight {
    fun display(row: Int, column: Int, font: String)
}

// Concrete flyweight: intrinsic state is the character itself
class Character(private val char: Char) : CharacterFlyweight {
    override fun display(row: Int, column: Int, font: String) {
        println("Displaying '$char' at ($row, $column) with font $font")
    }
}

// Flyweight factory: manages shared Character instances
class CharacterFactory {
    private val characters = mutableMapOf<Char, CharacterFlyweight>()

    fun getCharacter(char: Char): CharacterFlyweight {
        return characters.getOrPut(char) {
            println("Creating new flyweight for '$char'")
            Character(char)
        }
    }

    fun getTotalFlyweights() = characters.size
}

// Client: stores extrinsic state (position) separately
class TextEditor {
    private val factory = CharacterFactory()
    private val document = mutableListOf<Triple<CharacterFlyweight, Int, Int>>()

    fun insertCharacter(char: Char, row: Int, column: Int) {
        val flyweight = factory.getCharacter(char)
        document.add(Triple(flyweight, row, column))
    }

    fun display(font: String) {
        document.forEach { (char, row, col) ->
            char.display(row, col, font) // font is extrinsic state
        }
        println("Total unique characters: ${factory.getTotalFlyweights()}")
    }
}
```

### Android Example: Icon Cache

```kotlin
// Flyweight: shared bitmap for a given resource ID
data class IconBitmap(
    val bitmap: Bitmap
)

// Flyweight factory with memory cache (simplified)
class IconCache(private val context: Context) {
    // NOTE: For brevity we treat each entry as size=1.
    // In production, override sizeOf to account for bitmap size in bytes.
    private val cache = object : LruCache<Int, IconBitmap>(128) {}

    fun getIcon(resourceId: Int): IconBitmap {
        val cached = cache.get(resourceId)
        if (cached != null) return cached

        val bitmap = BitmapFactory.decodeResource(context.resources, resourceId)
        val icon = IconBitmap(bitmap)
        cache.put(resourceId, icon)
        return icon
    }

    fun clear() = cache.evictAll()
}

// Usage in RecyclerView
class AppAdapter(
    private val apps: List<AppInfo>,
    private val iconCache: IconCache
) : RecyclerView.Adapter<AppViewHolder>() {

    override fun onBindViewHolder(holder: AppViewHolder, position: Int) {
        val app = apps[position]
        val icon = iconCache.getIcon(app.iconResourceId)
        holder.imageView.setImageBitmap(icon.bitmap)
        holder.textView.text = app.name
    }

    override fun getItemCount(): Int = apps.size

    // ... onCreateViewHolder, etc.
}
```

### Kotlin Example: Game Particles

```kotlin
// Flyweight - shared particle appearance (intrinsic state)
data class ParticleType(
    val color: String,
    val sprite: String,
    val size: Int
) {
    fun draw(x: Int, y: Int, velocity: Pair<Int, Int>) {
        println("Drawing $color $sprite particle at ($x, $y) moving $velocity")
    }
}

// Flyweight factory
object ParticleFactory {
    private val types = mutableMapOf<String, ParticleType>()

    fun getParticleType(
        color: String,
        sprite: String,
        size: Int
    ): ParticleType {
        val key = "$color-$sprite-$size"
        return types.getOrPut(key) {
            println("Creating new particle type: $key")
            ParticleType(color, sprite, size)
        }
    }
}

// Particle with extrinsic state (position, velocity)
data class Particle(
    val type: ParticleType,
    var x: Int,
    var y: Int,
    var velocity: Pair<Int, Int>
) {
    fun move() {
        x += velocity.first
        y += velocity.second
    }

    fun draw() = type.draw(x, y, velocity)
}

// Game with many particles sharing a few types
class ParticleSystem {
    private val particles = mutableListOf<Particle>()

    fun addParticle(
        x: Int, y: Int,
        color: String, sprite: String, size: Int,
        velocity: Pair<Int, Int>
    ) {
        val type = ParticleFactory.getParticleType(color, sprite, size)
        particles.add(Particle(type, x, y, velocity))
    }

    fun update() {
        particles.forEach { it.move() }
    }

    fun render() {
        particles.forEach { it.draw() }
    }
}
```

### Explanation

- Intrinsic state (glyph, particle appearance, bitmap) is shared in flyweight instances and should be effectively immutable.
- Extrinsic state (position, velocity, current font, context) is supplied by the client on each use.
- A factory (or cache) manages the pool of flyweights and ensures reuse.
- Memory savings come from avoiding duplication of heavy shared data, not from eliminating all objects.
- Typical uses: icon/bitmap caches, glyph sharing in text rendering, string interning, particle systems.

### Usage

Use Flyweight when all of the following hold:

- You have a very large number of similar objects.
- These objects share substantial, mostly immutable state.
- Memory footprint is a concern.
- The cost/complexity of separating intrinsic/extrinsic state is justified.

Examples:

- Text editors: shared glyph / font metrics for characters.
- Game particles: shared particle types with different positions.
- Icon caching: shared bitmaps for repeated icons.
- `String` pools / interning: shared string literals.
- Resource caching (e.g., typefaces, drawables).

### Pros and Cons

#### Pros

1. Memory savings: drastically reduces duplicated shared state.
2. Performance: fewer heavy objects to allocate and collect.
3. Scalability: enables handling of large object graphs.
4. Centralized management: factory/cache controls flyweight lifecycle.

#### Cons

1. Increased complexity: must carefully separate intrinsic and extrinsic state.
2. CPU trade-off: extra indirection and cache lookups may add overhead.
3. Immutability constraint: intrinsic shared state should be effectively immutable.
4. Thread safety: flyweight factory/cache and shared state management must be thread-safe in concurrent environments.

### Best Practices

```kotlin
// DO: Use for large numbers of similar objects sharing heavy state
class TileMap {
    private val tileFactory = TileFactory()
    private val map = Array(1000) { Array(1000) { TileType.GRASS } }

    fun setTile(x: Int, y: Int, type: TileType) {
        map[x][y] = type
    }

    fun render() {
        map.forEachIndexed { x, row ->
            row.forEachIndexed { y, type ->
                tileFactory.getTile(type).draw(x, y)
            }
        }
    }
}

// DO: Make flyweight intrinsic state immutable
data class Tile(val image: String, val walkable: Boolean) {
    fun draw(x: Int, y: Int) { /* ... */ }
}

// DO: Consider reference semantics carefully in caches
// (WeakHashMap only weakens keys; values may still be strongly referenced.)
class ResourceCache {
    private val cache = WeakHashMap<String, Resource>()
}

// DO: Combine with Factory pattern for centralized sharing
object FontCache {
    private val fonts = mutableMapOf<Pair<String, Int>, Typeface>()

    fun getFont(name: String, size: Int): Typeface {
        return fonts.getOrPut(name to size) {
            // Create and return Typeface instance
        }
    }
}

// DON'T: Use for objects that are not heavily reused.
// DON'T: Share extrinsic (mutable, context-specific) state across clients.
// DON'T: Make flyweights mutable in ways that affect all clients unexpectedly.
```

### English summary

Flyweight is a structural pattern that minimizes memory by sharing intrinsic, effectively immutable state among many similar objects while passing extrinsic state from the client. Memory savings are achieved by avoiding duplication of heavy shared data, not by eliminating objects altogether. Use it when you have huge numbers of similar objects with substantial shared data and memory pressure is important. Typical uses: glyphs in text rendering, icon/bitmap caches, string pools, particle systems, tile maps. Pros: memory savings, performance, scalability. Cons: added complexity, CPU/cache overhead, need for immutability and thread-safe factories.

### Links

- [Flyweight pattern](https://en.wikipedia.org/wiki/Flyweight_pattern)
- [Flyweight Design Pattern](https://howtodoinjava.com/design-patterns/structural/flyweight-design-pattern/)

### Further Reading

- [Flyweight](https://refactoring.guru/design-patterns/flyweight)
- [Flyweight Design Pattern](https://sourcemaking.com/design_patterns/flyweight)

---

## Follow-ups

- How would you combine Flyweight with Factory or Pooling in your platform of choice?
- When would Flyweight be an over-optimization or introduce unnecessary complexity?
- How would you design a thread-safe Flyweight factory for a high-concurrency system?
- How does Flyweight compare to using a `WeakHashMap`-based cache or memoization for heavy objects?
- How would you detect (with profiling/metrics) that Flyweight is actually providing benefits in your system?

## Related Questions

- [[q-abstract-factory-pattern--cs--medium]]

## References

- [[c-computer-science]]
- [[c-architecture-patterns]]
