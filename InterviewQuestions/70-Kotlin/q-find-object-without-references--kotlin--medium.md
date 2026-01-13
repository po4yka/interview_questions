---
anki_cards:
- slug: q-find-object-without-references--kotlin--medium-0-en
  language: en
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
- slug: q-find-object-without-references--kotlin--medium-0-ru
  language: ru
  difficulty: 0.5
  tags:
  - Kotlin
  - difficulty::medium
---
---\
id: lang-071
title: "Find Object Without References / Поиск объектов без ссылок"
aliases: [Find Object Without References, Поиск объектов без ссылок]
topic: kotlin
subtopics: [debugging, memory-management, profiling]
question_kind: theory
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-kotlin
related: [c-memory-management]
created: 2025-10-15
updated: 2025-11-09
tags: [debugging, difficulty/medium, memory-management, memory-profiler, profiling, programming-languages]
---\
# Вопрос (RU)
> Как найти объект, если на него нет ссылок?

---

# Question (EN)
> How to find an object if there are no references to it?

## Ответ (RU)

Важно уточнить терминологию: в средах с GC (Kotlin/JVM, Android) объект, на который нет достижимых ссылок от GC roots, считается недостижимым и подлежит сборке. Такой объект "найти" уже нельзя — его память может быть освобождена.

На практике этот вопрос обычно означает одно из двух:
- вы "потеряли" ссылку в коде и хотите найти соответствующий логический объект в куче;
- вы подозреваете утечку: объект, который должен быть уничтожен, всё ещё удерживается ссылками.

Для решения используют профилирование памяти и анализ heap dump (Kotlin/JVM или Android):

1. Создайте heap dump (Android Studio):
   - Откройте Android Profiler.
   - Выберите вкладку Memory.
   - Нажмите "Dump Java heap" и дождитесь загрузки.

2. Проанализируйте heap dump (Android Studio или внешний инструмент):
   - Используйте просмотрщик heap в Android Studio или внешние инструменты (например, Memory Analyzer Tool, профайлеры JVM и т.п.).
   - Ищите нужные объекты по типу или специфическим значениям полей.
   - Для подозрительных экземпляров смотрите:
     - `Path` to GC Roots: какие ссылки делают объект достижимым.
     - Shallow size и retained size.
     - Dominator Tree / retained set, чтобы увидеть объекты, удерживающие большие подграфы.
   - Это помогает понять, почему объект всё ещё существует, или убедиться, что его больше нет в куче.

3. Memory Analyzer Tool (MAT):
   - Откройте heap dump в MAT.
   - Используйте Histogram для поиска экземпляров нужного класса.
   - Используйте отчёты `Path` to GC Roots и Dominator Tree, чтобы понять, за счёт каких ссылок объект удерживается.

4. LeakCanary (Android):
   - Интегрируйте LeakCanary в debug-сборки.
   - Он автоматически обнаруживает удерживаемые объекты, которые должны быть собраны GC, и показывает цепочку ссылок от GC roots.

Ключевая идея: вы не можете восстановить объект, у которого действительно нет ссылок; вместо этого вы:
- подтверждаете, что его нет (нет экземпляров в heap dump), или
- выясняете, почему он всё ещё жив, анализируя цепочки ссылок от GC roots в профилировщиках.

См. также: [[c-memory-management]], [[c-kotlin]].

## Answer (EN)

First, clarify terminology: in GC-based runtimes (Kotlin/JVM, Android), if an object has no reachable references from any GC root, it is unreachable and eligible for collection. Such an object cannot be "found" anymore — its memory may already be reclaimed.

In practice, this question usually means one of two things:
- You "lost" a reference in code and want to locate that logical object in the heap.
- You suspect a leak: an object that should be gone is still kept alive by some references.

You solve this via heap dumps and memory profiling (Kotlin/JVM or Android):

1. Take a heap dump (Android Studio)
   - Open Android Profiler.
   - Select the Memory tab.
   - Click "Dump Java heap" and wait for it to load.

2. Analyze the heap dump
   - Use Android Studio's heap viewer or an external tool.
   - Search for the target class/objects by type or specific field values.
   - For any suspicious instance, inspect:
     - `Path` to GC Roots: which references keep it reachable.
     - Shallow size and retained size.
     - Dominator tree / retained set to see which objects retain large subgraphs.
   - This tells you why the object still exists (who holds it), or helps you confirm it's no longer present.

3. Memory Analyzer Tool (MAT)
   - Open the heap dump in MAT.
   - Use "Histogram" to find instances of the desired class.
   - Use "`Path` to GC Roots" and "Dominator Tree" reports to understand retention.

4. LeakCanary (Android)
   - Integrate LeakCanary in debug builds.
   - It automatically detects retained objects that should have been GC'd and shows the reference chain from GC roots.

Key idea: you cannot retrieve an object that truly has no references; you instead:
- Confirm that it's gone (no instances in the heap dump), or
- Find why it's still there by examining reference chains from GC roots in profiling tools.

## Дополнительные Вопросы (RU)

- В чём ключевые отличия этого процесса в обычной Java и в Kotlin на Android?
- Чем отличаются GC roots в JVM (desktop/server) и Android Runtime (ART)?
- Когда вы выберете профилировщик Android Studio, а когда MAT или LeakCanary?
- Каковы типичные ошибки при интерпретации heap dump и GC roots?

## Follow-ups

- What are the key differences between this process in plain Java and in Kotlin on Android?
- How do GC roots differ between JVM desktop/server and Android Runtime (ART)?
- When would you choose Android Studio profiler vs MAT vs LeakCanary?
- What are common pitfalls when interpreting heap dumps and GC roots?

## Ссылки (RU)

- [Kotlin Документация](https://kotlinlang.org/docs/home.html)

## References

- [Kotlin Documentation](https://kotlinlang.org/docs/home.html)

## Связанные Вопросы (RU)

- q-garbage-collector-basics--programming-languages--medium

## Related Questions

- q-garbage-collector-basics--programming-languages--medium
