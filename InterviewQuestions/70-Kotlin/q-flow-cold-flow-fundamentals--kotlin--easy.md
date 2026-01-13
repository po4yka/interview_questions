---
anki_cards:
- slug: q-flow-cold-flow-fundamentals--kotlin--easy-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-flow-cold-flow-fundamentals--kotlin--easy-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
## Дополнительные Вопросы (RU)

1. В чём различия между горячими потоками (`SharedFlow`, `StateFlow`) и холодным `Flow` с точки зрения жизненного цикла и подписчиков?
2. Как преобразовать холодный `Flow` в горячий поток с помощью `shareIn` или `stateIn`?
3. Какие типичные ошибки возникают при сборе `Flow` в Android (жизненный цикл, отмена)?
4. Как работает «backpressure» (контроль скорости) в `Flow` и его операторах?
5. В каких случаях следует предпочесть `Flow` вместо `suspend`-функций или `Sequence`?

## Follow-ups

1. How do hot flows (`SharedFlow`, `StateFlow`) differ from cold `Flow` in terms of lifecycle and subscribers?
2. How can you convert a cold `Flow` to a hot stream using `shareIn` or `stateIn`?
3. What are common pitfalls when collecting `Flow` in Android (lifecycle, cancellation)?
4. How does backpressure work with `Flow` and its operators?
5. When should you prefer `Flow` over `suspend` functions or sequences?

## Ссылки (RU)

- [[c-kotlin]]
- [[c-flow]]
- Официальная документация "Kotlin Coroutines" по `Flow`
- Справочник по API `Flow` из kotlinx.coroutines

## References

- [[c-kotlin]]
- [[c-flow]]
- "Kotlin Coroutines" official documentation on `Flow`
- kotlinx.coroutines `Flow` API reference

## Связанные Вопросы (RU)

### Тот Же Уровень (Easy)
- [[q-flow-basics--kotlin--easy]] - основы и создание `Flow`

### Следующие Шаги (Medium)
- [[q-hot-cold-flows--kotlin--medium]] - горячие vs холодные потоки
- [[q-cold-vs-hot-flows--kotlin--medium]] - различия холодных и горячих потоков
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - сравнение `Flow` и `LiveData`
- [[q-channels-vs-flow--kotlin--medium]] - каналы против `Flow`

### Продвинутый Уровень (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - тестирование операторов `Flow`
- [[q-flow-backpressure--kotlin--hard]] - управление потоком данных в `Flow`
- [[q-flow-testing-advanced--kotlin--hard]] - продвинутое тестирование `Flow`

### Предпосылки (Easier)
- [[q-flow-basics--kotlin--easy]] - основы `Flow`

### Похожие Вопросы (Same Level)
- [[q-catch-operator-flow--kotlin--medium]] - оператор `catch` в `Flow`
- [[q-flow-operators-map-filter--kotlin--medium]] - операторы `map`/`filter` в `Flow`
- [[q-hot-cold-flows--kotlin--medium]] - горячие и холодные потоки
- [[q-channel-flow-comparison--kotlin--medium]] - сравнение каналов и `Flow`

### Хаб
- [[q-kotlin-flow-basics--kotlin--medium]] - обзор основ `Flow`

## Related Questions

### Same Level (Easy)
- [[q-flow-basics--kotlin--easy]] - `Flow` basics and creation

### Next Steps (Medium)
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold flows
- [[q-cold-vs-hot-flows--kotlin--medium]] - Cold vs Hot flows explained
- [[q-flow-vs-livedata-comparison--kotlin--medium]] - `Flow` vs `LiveData`
- [[q-channels-vs-flow--kotlin--medium]] - Channels vs `Flow`

### Advanced (Harder)
- [[q-testing-flow-operators--kotlin--hard]] - Testing `Flow` operators
- [[q-flow-backpressure--kotlin--hard]] - Backpressure and flow control in `Flow`
- [[q-flow-testing-advanced--kotlin--hard]] - Advanced `Flow` testing

### Prerequisites (Easier)
- [[q-flow-basics--kotlin--easy]] - `Flow`

### Related (Same Level)
- [[q-catch-operator-flow--kotlin--medium]] - `catch` operator in `Flow`
- [[q-flow-operators-map-filter--kotlin--medium]] - `map`/`filter` operators in `Flow`
- [[q-hot-cold-flows--kotlin--medium]] - Hot vs Cold flows overview
- [[q-channel-flow-comparison--kotlin--medium]] - Channels vs `Flow`

### Hub
- [[q-kotlin-flow-basics--kotlin--medium]] - Comprehensive `Flow` introduction
