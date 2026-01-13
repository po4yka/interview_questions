---
anki_cards:
- slug: q-hot-cold-flows--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-hot-cold-flows--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
# Question (EN)
> What's the difference between hot and cold Flows? Explain `Flow` (cold), `SharedFlow`, `StateFlow` (hot), when to use each, and how to convert between them.

## Ответ (RU)

`Flow` можно категоризировать как "холодные" или "горячие" в зависимости от того, когда они начинают производить значения и зависят ли они от подписчиков.

### Холодный Flow

```kotlin
val coldFlow = flow {
    println("Started")
    emit(1)
}
// Блок выполняется заново для КАЖДОГО collect(). Значения начинают производиться
// только при наличии подписчика; без collect() ничего не происходит.
```

Ключевые свойства:
- ленивый: не производит значения без collect()
- per-collector: каждый новый collector получает свой независимый поток значений

### Горячие Flows (`SharedFlow`, `StateFlow`)

```kotlin
val hotFlow = MutableSharedFlow<Int>()
// Общий для всех подписчиков. Эмиссии зависят от emit(),
// а не от появления нового collector. Collector получает только
// актуальные/повторённые (replay) значения с момента подписки.
```

- `SharedFlow` — обобщенный горячий поток с настраиваемым `replay`, буфером и правилами при переполнении.
- `StateFlow` — специализированный `SharedFlow` для состояния:
  - всегда имеет текущее значение (`value`)
  - `replay = 1` и значения консолидируются (conflated) до последнего
  - идеально подходит для представления актуального состояния (например, UI).

### Когда Использовать

- `Flow` (холодный):
  - запросы к базе данных, API вызовы
  - вычисления по требованию, когда каждый collector должен инициировать и получить свой результат
- `SharedFlow` (горячий):
  - одноразовые события, широковещание данных нескольким подписчикам
  - события навигации, analytics-события, "fire-and-forget" нотификации
- `StateFlow` (горячий):
  - долгоживущее состояние UI, которое должно быть всегда доступно как последнее актуальное значение
  - связь `ViewModel` → UI (Compose/Views)

### Как Конвертировать Холодный В Горячий (кратко)

- Используйте `shareIn` для преобразования `Flow` в `SharedFlow`.
- Используйте `stateIn` для получения `StateFlow` из холодного `Flow`.

---

## Answer (EN)

Flows can be categorized as "cold" or "hot" based on when they start producing values and whether emission depends on collectors.

### Cold Flow

```kotlin
val coldFlow = flow {
    println("Started")
    emit(1)
}
// The block is executed for EACH collect(). Values are produced only when
// there is an active collector; without collect(), nothing happens.
```

Key properties:
- lazy: does not produce values without collect()
- per-collector: each collector gets its own independent sequence of values

### Hot Flows (`SharedFlow`, `StateFlow`)

```kotlin
val hotFlow = MutableSharedFlow<Int>()
// Shared between collectors. Emissions are driven by emit(), not by new collectors.
// A collector receives only currently replayed/active values from its subscription point.
```

- `SharedFlow`: general-purpose hot flow with configurable `replay`, buffer, and overflow behavior.
- `StateFlow`: specialized `SharedFlow` for state:
  - always has a current `value`
  - effectively `replay = 1` with conflation to the latest value
  - ideal for representing always-available state (e.g., UI state).

### When to Use

- `Flow` (cold):
  - database queries, API calls
  - on-demand computations where each collector should independently trigger and receive the result
- `SharedFlow` (hot):
  - events, broadcasting to multiple collectors
  - navigation events, analytics, one-off signals
- `StateFlow` (hot):
  - UI state that should expose the latest value at any time
  - `ViewModel` → UI data streams

### How to Convert Cold to Hot (brief)

- Use `shareIn` to convert a cold `Flow` into a `SharedFlow`.
- Use `stateIn` to obtain a `StateFlow` from a cold `Flow`.

---

## Дополнительные Вопросы (RU)

1. Что такое стратегия `SharingStarted` и как она влияет на поведение `shareIn`/`stateIn`?
2. Как выбрать между `SharedFlow` и `StateFlow` в конкретном сценарии (события vs состояние)?
3. Как правильно выбирать `CoroutineScope` для `shareIn`/`stateIn` в `ViewModel` и других слоях?
4. Как обрабатывать ошибки и отмену при работе с горячими потоками, чтобы не допустить утечек?
5. Как тестировать поведение `SharedFlow` и `StateFlow` (replay, состояние, коллекция несколькими подписчиками)?

---

## Follow-ups

1. What is `SharingStarted` strategy and how does it affect `shareIn`/`stateIn` behavior?
2. How to choose between `SharedFlow` and `StateFlow` for a given use case (events vs state)?
3. How to correctly choose a `CoroutineScope` for `shareIn`/`stateIn` in a `ViewModel` and other layers?
4. How to handle errors and cancellation with hot flows to avoid leaks?
5. How to test `SharedFlow` and `StateFlow` behavior (replay, state, multiple collectors)?

---

## Ссылки (RU)

- [[c-kotlin]]
- [[c-flow]]
- [SharedFlow Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/)

---

## References

- [[c-kotlin]]
- [[c-flow]]
- [SharedFlow Documentation](https://kotlinlang.org/api/kotlinx.coroutines/kotlinx-coroutines-core/kotlinx.coroutines.flow/-shared-flow/)

---

## Связанные Вопросы (RU)

### Средний Уровень
- [[q-cold-vs-hot-flows--kotlin--medium]]
- [[q-flow-cold-flow-fundamentals--kotlin--easy]]
- [[q-testing-stateflow-sharedflow--kotlin--medium]]
- [[q-testing-viewmodel-coroutines--kotlin--medium]]

### Продвинутый Уровень
- [[q-testing-flow-operators--kotlin--hard]]

### Хаб
- [[q-kotlin-flow-basics--kotlin--medium]]

---

## Related Questions

### Related (Medium)
- [[q-cold-vs-hot-flows--kotlin--medium]] - `Flow`
- [[q-flow-cold-flow-fundamentals--kotlin--easy]] - Coroutines
- [[q-testing-stateflow-sharedflow--kotlin--medium]] - Coroutines
- [[q-testing-viewmodel-coroutines--kotlin--medium]] - Testing

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Coroutines

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive `Flow` introduction
