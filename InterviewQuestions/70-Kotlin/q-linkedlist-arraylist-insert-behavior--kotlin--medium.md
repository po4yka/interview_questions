---
'---id': lang-006
title: LinkedList ArrayList Insert Behavior / Поведение вставки LinkedList и ArrayList
aliases:
- LinkedList ArrayList Insert Behavior
- Поведение вставки LinkedList и ArrayList
topic: kotlin
subtopics:
- c-collections
- c-data-structures
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-kotlin
related:
- c-aggregation
- c-app-signing
- c-backend
- c-binary-search
- c-binary-search-tree
- c-binder
- c-biometric-authentication
- c-bm25-ranking
- c-by-type
- c-cap-theorem
- c-ci-cd
- c-ci-cd-pipelines
- c-clean-code
- c-collections
- c-compiler-optimization
- c-compose-modifiers
- c-compose-phases
- c-compose-semantics
- c-computer-science
- c-concurrency
- c-cross-platform-development
- c-cross-platform-mobile
- c-cs
- c-data-classes
- c-data-loading
- c-debugging
- c-declarative-programming
- c-deep-linking
- c-density-independent-pixels
- c-dimension-units
- c-dp-sp-units
- c-dsl-builders
- c-dynamic-programming
- c-espresso-testing
- c-event-handling
- c-folder
- c-functional-programming
- c-gdpr-compliance
- c-gesture-detection
- c-gradle-build-cache
- c-gradle-build-system
- c-https-tls
- c-image-formats
- c-inheritance
- c-jit-aot-compilation
- c-kmm
- c-kotlin
- c-lambda-expressions
- c-lazy-grid
- c-lazy-initialization
- c-level
- c-load-balancing
- c-manifest
- c-memory-optimization
- c-memory-profiler
- c-microservices
- c-multipart-form-data
- c-multithreading
- c-mutablestate
- c-networking
- c-offline-first-architecture
- c-oop
- c-oop-concepts
- c-oop-fundamentals
- c-oop-principles
- c-play-console
- c-play-feature-delivery
- c-programming-languages
- c-properties
- c-real-time-communication
- c-references
- c-scaling-strategies
- c-scoped-storage
- c-security
- c-serialization
- c-server-sent-events
- c-shader-programming
- c-snapshot-system
- c-specific
- c-strictmode
- c-system-ui
- c-test-doubles
- c-test-sharding
- c-testing-pyramid
- c-testing-strategies
- c-theming
- c-to-folder
- c-token-management
- c-touch-input
- c-turbine-testing
- c-two-pointers
- c-ui-testing
- c-ui-ux-accessibility
- c-value-classes
- c-variable
- c-weak-references
- c-windowinsets
- c-xml
created: 2025-10-13
updated: 2025-11-09
tags:
- arraylist
- collections
- data-structures
- difficulty/medium
- kotlin
- linkedlist
- programming-languages
anki_cards:
- slug: q-linkedlist-arraylist-insert-behavior--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-linkedlist-arraylist-insert-behavior--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
# Вопрос (RU)
> Как будут вести себя `LinkedList` и `ArrayList`, если вставить в них элемент?

---

# Question (EN)
> How will `LinkedList` and `ArrayList` behave when inserting an element?

## Ответ (RU)

`LinkedList` и `ArrayList` представляют собой две разные реализации интерфейса `List` (на JVM это, как правило, `java.util.LinkedList` и `java.util.ArrayList`, которые используются и из Kotlin), и каждая из них имеет свои особенности поведения при вставке элементов.

- `ArrayList` основан на динамическом массиве.
  - Добавление элемента в конец списка в среднем выполняется за амортизированное время O(1), но при переполнении требуется расширение внутреннего массива, что занимает O(n).
  - Добавление элемента в произвольную позицию (включая "середину") требует сдвига части элементов и имеет временную сложность O(n) (формально — пропорционально количеству сдвигаемых элементов).
- `LinkedList` реализует структуру данных двусвязного списка.
  - Добавление элемента в начало или конец списка (при наличии ссылки на соответствующий узел) выполняется за O(1).
  - Добавление элемента по индексу в середину списка логически состоит из поиска нужного узла (O(n)) и последующей вставки (O(1)), в сумме даёт O(n).

Важно: в Kotlin интерфейсы `List`/`MutableList` не гарантируют конкретную реализацию; при выборе между `ArrayList` и `LinkedList` следует явно учитывать эти различия и реальные профили доступа. См. также [[c-collections]].

---

## Answer (EN)

`LinkedList` and `ArrayList` are two different implementations of the `List` interface (on the JVM they are typically `java.util.LinkedList` and `java.util.ArrayList`, also used from Kotlin), and each has its own insertion behavior.

- `ArrayList` is based on a dynamic array.
  - Adding an element to the end of the list takes amortized O(1) time, but when the backing array needs to grow, that resize operation takes O(n).
  - Inserting an element at an arbitrary position (including the "middle") requires shifting part of the elements and has O(n) time complexity (more precisely, proportional to the number of shifted elements).
- `LinkedList` implements a doubly-linked list.
  - Adding an element at the beginning or end of the list (given a reference to the corresponding node) is O(1).
  - Adding an element by index in the middle involves traversing to the target node (O(n)) and then inserting (O(1)), resulting in overall O(n).

Important: in Kotlin, the `List`/`MutableList` interfaces do not guarantee a specific concrete implementation; when choosing between `ArrayList` and `LinkedList` you should explicitly consider these differences and actual access patterns. See also [[c-collections]].

---

## Дополнительные Вопросы (RU)

- В чём ключевые отличия между поведением в Kotlin и Java в этом контексте?
- Когда на практике вы бы предпочли `ArrayList` вместо `LinkedList` и наоборот?
- Какие распространённые ошибки и заблуждения связаны с выбором структуры списка?

## Follow-ups

- What are the key differences between this behavior in Kotlin vs Java?
- When would you prefer `ArrayList` over `LinkedList` and vice versa in practice?
- What common misconceptions or pitfalls exist when choosing between these list implementations?

## Ссылки (RU)

- [Документация Kotlin](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

### Реализации И Структуры Данных
- [[q-kotlin-immutable-collections--kotlin--easy]]

## Related Questions

### Implementations and Data Structures
- [[q-kotlin-immutable-collections--kotlin--easy]]
