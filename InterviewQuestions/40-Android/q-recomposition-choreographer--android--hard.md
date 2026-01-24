---
id: android-165
title: Recomposition Choreographer / Рекомпозиция и Choreographer
aliases:
- Recomposition Choreographer
- Рекомпозиция и Choreographer
topic: android
subtopics:
- coroutines
- performance-rendering
- ui-compose
question_kind: theory
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-android
related:
- c-compose-recomposition
- c-jetpack-compose
- c-recomposition
- q-compose-performance-optimization--android--hard
- q-compose-stability-skippability--android--hard
- q-recomposition-compose--android--medium
created: 2025-10-15
updated: 2025-11-10
sources: []
tags:
- android/coroutines
- android/performance-rendering
- android/ui-compose
- choreographer
- difficulty/hard
- vsync
anki_cards:
- slug: android-165-0-en
  language: en
  anki_id: 1768418239756
  synced_at: '2026-01-23T16:45:05.503643'
- slug: android-165-0-ru
  language: ru
  anki_id: 1768418239774
  synced_at: '2026-01-23T16:45:05.504869'
---
# Вопрос (RU)

> Рекомпозиция происходит в рандомное время или по команде Choreographer?

# Question (EN)

> Does recomposition happen at random times or on command from Choreographer?

## Ответ (RU)

Рекомпозиция в Compose запускается **рантаймом Compose** в ответ на изменения состояния и координируется с **Android Choreographer**, который синхронизирован с сигналами **VSYNC** (вертикальная синхронизация) для отрисовки кадров. Это не случайный процесс.

**Упрощённый процесс:**
1. Изменение `MutableState` помечает соответствующие composable-области как "невалидные" (требуют рекомпозиции).
2. Рантайм Compose планирует задачу рекомпозиции; для отображения на экране изменения обычно синхронизируются с кадровыми колбэками `Choreographer`.
3. На очередном кадре (колбэк `Choreographer`, выровненный по VSYNC) выполняется рекомпозиция для помеченных областей и подготавливается обновлённое дерево для отрисовки.
4. Обновлённый UI передаётся в систему отрисовки; перерисовываются только те composable-области, которые были инвалидированы (Compose использует пропуски/skip-группы и целенаправленную инвалидацию, а не полный diff всех элементов как в виртуальном DOM).

**Важно:** Choreographer не "управляет" логикой Compose напрямую, он предоставляет VSYNC-синхронизированные колбэки, которые Compose использует для планирования применения изменений и рисования кадров.

**Choreographer** — системный компонент Android, координирующий обработку ввода, layout/traversal и рендеринг с частотой дисплея (например, 60Hz или 120Hz). Это помогает добиться плавности, энергоэффективности и батчинга изменений. Jetpack Compose опирается на этот механизм через интеграцию с платформой.

**Бюджет кадра (пример):**
- 60Hz: ~16.67ms
- 120Hz: ~8.33ms

В этот бюджет входят: обработка ввода, рекомпозиция, измерение, размещение и рисование.

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) { // ✅ Изменение попадает в список инвалидаций и будет обработано до ближайшего VSYNC-выравненного кадра
        Text("Счетчик: $count")
    }
}

// Упрощённая временная шкала (60Hz):
// 0ms: onClick → count++ → соответствующие области помечены для рекомпозиции
// До ~16.67ms: рантайм планирует рекомпозицию, чтобы применить изменения к следующему VSYNC-кадру
// ~16.67ms: Choreographer кадр → выполняется рекомпозиция помеченных composable и последующий draw
// Если всё укладывается в бюджет, обновлённый кадр отображается без джанка
```

**Ключевые эффекты VSYNC-координации:**
- **Плавность:** выравнивание под VSYNC снижает вероятность разрывов и рывков.
- **Батчинг:** несколько изменений состояния до следующего кадра могут быть обработаны в одной волне рекомпозиции.
- **Энергоэффективность:** работа по обновлению UI концентрируется вокруг кадров, избегая лишних пробуждений.

**Dropped frames (пропущенные кадры):**

```kotlin
@Composable
fun SlowComposition() {
    var count by remember { mutableStateOf(0) }

    val result = remember(count) {
        Thread.sleep(20) // ❌ Блокирует главный поток во время рекомпозиции > бюджета кадра → джанк
        count * 2
    }
    Text("Результат: $result")
}
```

Если суммарное время рекомпозиции + layout + draw (и другого кода на главном потоке) превышает бюджет кадра, кадр будет пропущен.

**Важно:** Для дисплеев 120Hz (бюджет ~8.33ms) критично, чтобы вся работа кадра на главном потоке (включая рекомпозицию) укладывалась в этот интервал. Это не жёсткое правило "рекомпозиция < 8ms", а практический ориентир: не допускайте тяжёлой логики в рекомпозиции на главном потоке.

## Answer (EN)

In Compose, recomposition is started by the **Compose runtime** in response to state changes and is coordinated with **Android Choreographer**, which is synchronized with **VSYNC** signals for frame rendering. It is not random.

**Simplified process:**
1. A `MutableState` change marks the corresponding composable scopes as invalid and needing recomposition.
2. The Compose runtime schedules recomposition work; for what affects what you see on screen, this work is generally aligned with `Choreographer` frame callbacks.
3. On the next frame (`Choreographer` callback aligned with VSYNC), the invalidated composables are recomposed and an updated tree is prepared.
4. The updated UI is sent into the rendering pipeline; only invalidated composable regions are recomposed and redrawn (Compose uses skip groups/targeted invalidation rather than a full virtual DOM diff).

**Important:** Choreographer does not directly "control" Compose logic; it provides VSYNC-aligned callbacks that Compose uses to schedule applying changes and drawing frames.

**Choreographer** is an Android system component that coordinates input, layout/traversal, and rendering with the display refresh rate (e.g., 60Hz or 120Hz). This improves smoothness, power efficiency, and batching. Jetpack Compose leverages this mechanism through the platform.

**Frame budget (example):**
- 60Hz: ~16.67ms
- 120Hz: ~8.33ms

This budget covers input processing, recomposition, measure, layout, and drawing.

```kotlin
@Composable
fun Counter() {
    var count by remember { mutableStateOf(0) }

    Button(onClick = { count++ }) { // ✅ Change is enqueued as invalidation and applied for the next VSYNC-aligned frame
        Text("Count: $count")
    }
}

// Simplified timeline (60Hz):
// 0ms: onClick → count++ → corresponding scopes are marked invalid
// Until ~16.67ms: runtime schedules recomposition so that changes are ready for the next VSYNC frame
// ~16.67ms: Choreographer frame → invalidated composables are recomposed and then drawn
// If all work fits the budget, the updated frame is shown without jank
```

**Key effects of VSYNC coordination:**
- **Smoothness:** VSYNC alignment reduces tearing and visible jank.
- **Batching:** multiple state changes before the next frame can be handled in a single recomposition pass.
- **Energy efficiency:** UI work is concentrated around frame boundaries instead of waking up arbitrarily.

**Dropped frames:**

```kotlin
@Composable
fun SlowComposition() {
    var count by remember { mutableStateOf(0) }

    val result = remember(count) {
        Thread.sleep(20) // ❌ Blocks the main thread during recomposition beyond the frame budget → jank
        count * 2
    }
    Text("Result: $result")
}
```

If the total time for recomposition + layout + draw (and other main-thread work) exceeds the frame budget, the frame is skipped.

**Important:** For 120Hz displays (~8.33ms budget), the entire main-thread frame work, including recomposition, needs to stay within that time. This is a practical guideline rather than a strict "recomposition must always be < 8ms" rule; avoid heavy blocking work inside recomposition on the main thread.

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
