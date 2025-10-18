---
id: 20251012-1227111139
title: "Flyweight Pattern / Flyweight Паттерн"
topic: computer-science
difficulty: hard
status: draft
moc: moc-cs
related: [q-when-coroutine-cannot-be-cancelled--programming-languages--medium, q-decorator-pattern--design-patterns--medium, q-how-to-create-suspend-function--programming-languages--medium]
created: 2025-10-15
tags:
  - design-patterns
  - structural-patterns
  - flyweight
  - gof-patterns
  - memory-optimization
---
# Flyweight Pattern

# Question (EN)
> What is the Flyweight pattern? When and why should it be used?

# Вопрос (RU)
> Что такое паттерн Flyweight? Когда и зачем его использовать?

---

## Answer (EN)


**Flyweight (Легковес/Приспособленец)** - это структурный паттерн проектирования, который позволяет использовать разделяемые объекты одновременно в большом количестве, вместо создания отдельного объекта для каждого случая. Приспособленец экономит память за счёт разделения общего состояния, вынесенного в один объект, между множеством объектов.

### Definition


A flyweight is an object that **minimizes memory usage by sharing as much data as possible with other similar objects**. It's a way to use objects in large numbers when a simple repeated representation would use an unacceptable amount of memory. Often some parts of the object state can be shared, and it's common practice to hold them in external data structures and pass them temporarily when used.

### Problems it Solves


The flyweight design pattern solves problems like:

1. **Large numbers of objects should be supported efficiently**
2. **Creating large numbers of objects should be avoided**

When representing large text documents, for example, creating an object for each character would result in a huge number of objects that could not be processed efficiently.

### Solution


Define **`Flyweight`** objects that:

- Store **intrinsic (invariant) state** that can be shared
- Provide an interface through which **extrinsic (variant) state** can be passed in

This enables clients to (1) reuse (share) Flyweight objects and (2) pass in extrinsic state when they invoke a Flyweight operation. This greatly reduces the number of physically created objects.

## Ключевые концепции

**Intrinsic state**: Shared, stored in Flyweight (e.g., character glyph, icon bitmap)
**Extrinsic state**: Context-dependent, passed by client (e.g., character position, color)

## Пример: Text Editor Characters

```kotlin
// Flyweight interface
interface CharacterFlyweight {
    fun display(row: Int, column: Int, font: String)
}

// Concrete flyweight
class Character(private val char: Char) : CharacterFlyweight {
    override fun display(row: Int, column: Int, font: String) {
        println("Displaying '$char' at ($row, $column) with font $font")
    }
}

// Flyweight factory
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

// Client
class TextEditor {
    private val factory = CharacterFactory()
    private val document = mutableListOf<Triple<CharacterFlyweight, Int, Int>>()

    fun insertCharacter(char: Char, row: Int, column: Int) {
        val flyweight = factory.getCharacter(char)
        document.add(Triple(flyweight, row, column))
    }

    fun display(font: String) {
        document.forEach { (char, row, col) ->
            char.display(row, col, font)
        }
        println("Total unique characters: ${factory.getTotalFlyweights()}")
    }
}

fun main() {
    val editor = TextEditor()
    val text = "HELLO"

    text.forEachIndexed { index, char ->
        editor.insertCharacter(char, 0, index)
    }

    editor.display("Arial")
}
```

**Output**:
```
Creating new flyweight for 'H'
Creating new flyweight for 'E'
Creating new flyweight for 'L'
Creating new flyweight for 'O'
Displaying 'H' at (0, 0) with font Arial
Displaying 'E' at (0, 1) with font Arial
Displaying 'L' at (0, 2) with font Arial
Displaying 'L' at (0, 3) with font Arial
Displaying 'O' at (0, 4) with font Arial
Total unique characters: 4
```

## Android Example: Icon Cache

```kotlin
// Flyweight
data class IconBitmap(
    val resourceId: Int,
    val bitmap: Bitmap
)

// Flyweight factory with memory cache
class IconCache(private val context: Context) {
    private val cache = LruCache<Int, IconBitmap>(
        (Runtime.getRuntime().maxMemory() / 1024 / 8).toInt()
    )

    fun getIcon(resourceId: Int): IconBitmap {
        return cache.get(resourceId) ?: run {
            val bitmap = BitmapFactory.decodeResource(
                context.resources,
                resourceId
            )
            val icon = IconBitmap(resourceId, bitmap)
            cache.put(resourceId, icon)
            icon
        }
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

    // ...
}
```

## Kotlin Example: Game Particles

```kotlin
// Flyweight - shared particle appearance
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

// Particle with extrinsic state
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

// Game with many particles
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

fun main() {
    val system = ParticleSystem()

    // Create 1000 particles, but only few types
    repeat(1000) {
        system.addParticle(
            x = it % 100,
            y = it / 100,
            color = if (it % 2 == 0) "red" else "blue",
            sprite = "circle",
            size = 5,
            velocity = (1 to -1)
        )
    }

    system.render()
}
```

### Explanation


**Explanation**:

- **Intrinsic state** (Character glyph, Particle appearance) is shared in flyweight
- **Extrinsic state** (position, velocity) is passed by client
- **Factory** manages flyweight pool, ensures sharing
- **Memory savings** - Instead of 1000 objects, only few shared types
- **Android**: Icon caches, string pools, typeface caching

## Применение

Use cases:

- **Text editors** - Glyph objects for characters
- **Game particles** - Shared particle types with different positions
- **Icon caching** - Shared bitmaps for repeated icons
- **String pools** - Shared string literals
- **Android resources** - Drawable/Bitmap caching

## Преимущества и недостатки

### Pros (Преимущества)


1. **Memory savings** - Drastically reduces memory usage
2. **Performance** - Fewer objects to create and garbage collect
3. **Scalability** - Can handle large numbers of objects
4. **Centralized management** - Factory controls object lifecycle

### Cons (Недостатки)


1. **Complexity** - Separating intrinsic/extrinsic state is complex
2. **CPU trade-off** - Saves RAM but may use more CPU for lookups
3. **Immutability** - Flyweights must be immutable
4. **Thread safety** - Factory must be thread-safe

## Best Practices

```kotlin
// - DO: Use for large numbers of similar objects
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

// - DO: Make flyweights immutable
data class Tile(val image: String, val walkable: Boolean) {
    fun draw(x: Int, y: Int) { /* ... */ }
}

// - DO: Use with weak references for cache
class ResourceCache {
    private val cache = WeakHashMap<String, Resource>()
}

// - DO: Combine with Factory pattern
object FontCache {
    private val fonts = mutableMapOf<Pair<String, Int>, Typeface>()

    fun getFont(name: String, size: Int): Typeface {
        return fonts.getOrPut(name to size) {
            // Create font
        }
    }
}

// - DON'T: Use for mutable objects
// - DON'T: Use when objects aren't reused
// - DON'T: Share extrinsic state
```

**English**: **Flyweight** is a structural pattern that minimizes memory by sharing data among similar objects. **Problem**: Large numbers of similar objects consume excessive memory. **Solution**: Share intrinsic (common) state in flyweights, pass extrinsic (unique) state from client. **Use when**: (1) App uses large numbers of objects, (2) Memory is limited, (3) Objects have shared state. **Android**: Icon/bitmap caching, string pools, typeface cache. **Pros**: memory savings, performance, scalability. **Cons**: complexity, CPU overhead, immutability required. **Examples**: Text editor characters, game particles, tile maps, icon caches.

## Links

- [Flyweight pattern](https://en.wikipedia.org/wiki/Flyweight_pattern)
- [Flyweight Design Pattern](https://howtodoinjava.com/design-patterns/structural/flyweight-design-pattern/)

## Further Reading

- [Flyweight](https://refactoring.guru/design-patterns/flyweight)
- [Flyweight Design Pattern](https://sourcemaking.com/design_patterns/flyweight)

---
*Source: Kirchhoff Android Interview Questions*


## Ответ (RU)

### Определение

**Flyweight (Легковес)** - это объект, который **минимизирует использование памяти путем совместного использования максимального количества данных с другими похожими объектами**. Это способ использования объектов в большом количестве, когда простое повторяющееся представление потребует неприемлемого объема памяти. Часто некоторые части состояния объекта могут быть разделены, и принято хранить их во внешних структурах данных и передавать временно при использовании.

### Проблемы, которые решает

Паттерн проектирования Flyweight решает такие проблемы:

1. **Необходимость эффективной поддержки большого количества объектов**
2. **Необходимость избегать создания большого количества объектов**

Например, при представлении больших текстовых документов создание объекта для каждого символа приведет к огромному количеству объектов, которые не могут быть обработаны эффективно.

### Решение

Определите объекты **`Flyweight`**, которые:

- Хранят **внутреннее (инвариантное) состояние**, которое может быть разделено
- Предоставляют интерфейс, через который может быть передано **внешнее (вариантное) состояние**

Это позволяет клиентам (1) повторно использовать (разделять) объекты Flyweight и (2) передавать внешнее состояние при вызове операции Flyweight. Это значительно уменьшает количество физически созданных объектов.

### Объяснение

**Пояснение**:

- **Внутреннее состояние** (глиф символа, внешний вид частицы) разделяется в flyweight
- **Внешнее состояние** (позиция, скорость) передается клиентом
- **Factory** управляет пулом flyweight, обеспечивает разделение
- **Экономия памяти** - Вместо 1000 объектов только несколько разделяемых типов
- **Android**: Кэши иконок, пулы строк, кэширование шрифтов

### Pros (Преимущества)

1. **Экономия памяти** - Значительно уменьшает использование памяти
2. **Производительность** - Меньше объектов для создания и сборки мусора
3. **Масштабируемость** - Может обрабатывать большое количество объектов
4. **Централизованное управление** - Factory контролирует жизненный цикл объектов

### Cons (Недостатки)

1. **Сложность** - Разделение внутреннего/внешнего состояния сложно
2. **Компромисс CPU** - Экономит RAM, но может использовать больше CPU для поиска
3. **Неизменяемость** - Flyweight должны быть неизменяемыми
4. **Потокобезопасность** - Factory должна быть потокобезопасной


---

## Related Questions

### Hub
- [[q-design-patterns-types--design-patterns--medium]] - Design pattern categories overview

### Advanced Patterns
- [[q-bridge-pattern--design-patterns--hard]] - Bridge pattern
- [[q-interpreter-pattern--design-patterns--hard]] - Interpreter pattern
- [[q-visitor-pattern--design-patterns--hard]] - Visitor pattern

