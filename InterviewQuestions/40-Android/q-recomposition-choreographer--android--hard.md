---
id: 20251017-105224
title: "Recomposition Choreographer / Рекомпозиция и Choreographer"
aliases: ["Recomposition Choreographer", "Рекомпозиция и Choreographer"]
topic: android
subtopics: [ui-compose, performance-rendering, coroutines]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [q-compose-stability-skippability--android--hard, q-compose-performance-optimization--android--hard, q-recomposition-compose--android--medium]
created: 2025-10-15
updated: 2025-01-27
sources: []
tags: [android/ui-compose, android/performance-rendering, android/coroutines, choreographer, vsync, difficulty/hard]
---
# Вопрос (RU)

Рекомпозиция происходит в рандомное время или по команде Choreographer?

# Question (EN)

Does recomposition happen at random times or on command from Choreographer?

## Ответ (RU)

Рекомпозиция **контролируется Android Choreographer**, который синхронизирован с **VSYNC** (вертикальная синхронизация).

**Процесс:**
1. Изменение `MutableState` устанавливает флаг "UI требует перерисовки"
2. Choreographer ждет следующий сигнал VSYNC
3. При VSYNC запускается рекомпозиция (не случайно!)
4. Перерисовываются только измененные элементы

**Choreographer** — системный компонент Android, координирующий рендеринг с частотой дисплея (60Hz или 120Hz). Обеспечивает плавность (60fps), энергоэффективность и батчинг изменений. Тесно связан с [[c-jetpack-compose|Jetpack Compose]].

**Бюджет кадра:**
- 60Hz: 16.67ms
- 120Hz: 8.33ms

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) { // ✅ Изменение батчируется до VSYNC
        Text("Счетчик: $count")
    }
}

// Таймлайн:
// 0ms: count++ → флаг установлен
// 16.67ms: VSYNC → рекомпозиция только Text
// 33.34ms: кадр на экране
```

**Ключевые преимущества:**
- **Плавность:** VSYNC-синхронизация предотвращает рывки
- **Батчинг:** множественные изменения состояния → одна рекомпозиция
- **Энергоэффективность:** предсказуемые пробуждения CPU

**Dropped frames (пропущенные кадры):**

```kotlin
@Composable
fun SlowComposition() {
    var count by remember { mutableStateOf(0) }

    val result = remember(count) {
        Thread.sleep(20) // ❌ 20ms > бюджета 16.67ms → джанк!
        count * 2
    }
    Text("Результат: $result")
}
```

**Важно:** Держите рекомпозицию **< 8ms** для поддержки 120Hz дисплеев.

## Answer (EN)

Recomposition is **controlled by Android Choreographer**, synchronized with **VSYNC** (vertical sync) signals.

**Process:**
1. `MutableState` change sets a flag "UI needs redraw"
2. Choreographer waits for the next VSYNC signal
3. On VSYNC, recomposition is triggered (not random!)
4. Only changed UI elements are recomposed

**Choreographer** is Android's system component coordinating frame rendering with the display refresh rate (60Hz or 120Hz). It ensures smooth 60fps, battery efficiency, and batching of state changes. Tightly integrated with [[c-jetpack-compose|Jetpack Compose]].

**Frame budget:**
- 60Hz: 16.67ms
- 120Hz: 8.33ms

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) { // ✅ Change batched until VSYNC
        Text("Count: $count")
    }
}

// Timeline:
// 0ms: count++ → flag set
// 16.67ms: VSYNC → recompose only Text
// 33.34ms: frame displayed
```

**Key benefits:**
- **Smoothness:** VSYNC synchronization prevents jank
- **Batching:** multiple state changes → single recomposition
- **Energy efficiency:** predictable CPU wake-ups

**Dropped frames:**

```kotlin
@Composable
fun SlowComposition() {
    var count by remember { mutableStateOf(0) }

    val result = remember(count) {
        Thread.sleep(20) // ❌ 20ms > 16.67ms budget → jank!
        count * 2
    }
    Text("Result: $result")
}
```

**Important:** Keep recomposition **< 8ms** for smooth 120Hz display support.

---

## Follow-ups

- How does Choreographer prioritize CALLBACK_INPUT vs CALLBACK_TRAVERSAL?
- What happens when recomposition exceeds the VSYNC budget on 120Hz displays?
- Can you force immediate recomposition outside the VSYNC window?
- How do you measure recomposition timing in production apps?
- What is the relationship between Compose State and Choreographer callbacks?

## References

- [[c-jetpack-compose]] - Jetpack Compose fundamentals
- Android Choreographer documentation
- Jetpack Compose performance guide

## Related Questions

### Prerequisites (Easier)
- [[q-recomposition-compose--android--medium]] - Basic recomposition concepts
- [[q-how-does-jetpackcompose-work--android--medium]] - Compose architecture

### Related (Same Level)
- [[q-compose-stability-skippability--android--hard]] - Skipping recomposition
- [[q-compose-performance-optimization--android--hard]] - Performance optimization

### Advanced
- [[q-compose-slot-table-recomposition--android--hard]] - Slot table internals
