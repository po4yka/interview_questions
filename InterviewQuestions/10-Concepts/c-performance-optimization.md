---\
id: "20251030-143000"
title: "Performance Optimization / Оптимизация производительности"
aliases: ["Android Performance", "Performance Optimization", "Оптимизация производительности"]
summary: "Strategies and tools for optimizing Android app performance"
topic: "android"
subtopics: ["optimization", "performance", "profiling"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-android"
related: []
created: "2025-10-30"
updated: "2025-10-30"
tags: ["android", "concept", "optimization", "performance", "profiling", "difficulty/medium"]
---\

# Summary (EN)

Performance optimization in Android focuses on delivering smooth, responsive user experiences through efficient resource usage. The core areas include startup time (cold/warm/hot starts), rendering performance (maintaining 60fps/120fps), memory management, and battery efficiency.

**Key Performance Metrics**:
- **Startup Time**: Time to initial display (TTID), time to fully drawn
- **Rendering**: Frame time (<16ms for 60fps), jank percentage
- **Memory**: Heap size, allocation rate, GC frequency
- **Battery**: CPU wake locks, network calls, sensor usage

**Profiling Tools**:
- **Android Profiler**: Real-time CPU, memory, network, energy monitoring
- **Systrace/Perfetto**: System-level tracing for frame drops and ANRs
- **Layout Inspector**: `View` hierarchy analysis for overdraw
- **Memory Profiler**: Heap dumps, allocation tracking, leak detection

**Common Performance Issues**:
1. **Overdraw**: Multiple layers painted unnecessarily
2. **Memory Leaks**: Retained objects preventing GC
3. **Jank**: Frame drops causing stuttering UI
4. **ANRs**: `Application` Not Responding (blocked main thread)
5. **Slow Startup**: Heavy initialization on main thread

**Optimization Strategies**:

*Startup Optimization*:
- Lazy initialization of non-critical components
- Avoid heavy work in `Application`.onCreate()
- Use content providers initialization lazily
- Implement splash screens properly (Android 12+)

*Rendering Optimization*:
- Reduce view hierarchy depth (`ConstraintLayout`, Compose)
- Enable hardware acceleration
- Use `RecyclerView` with `ViewHolder` pattern
- Implement efficient image loading (Coil, Glide)
- Avoid overdraw (Debug GPU Overdraw tool)

*Memory Optimization*:
- Use memory-efficient data structures (ArrayMap, SparseArray)
- Implement proper lifecycle-aware cleanup
- Avoid context leaks (WeakReference for listeners)
- Use LeakCanary for detection
- Optimize bitmap usage (downsampling, caching)

*Threading Optimization*:
- Move long operations off main thread
- Use Kotlin coroutines with appropriate dispatchers
- Implement `WorkManager` for background tasks
- Avoid blocking I/O on main thread

*Battery Optimization*:
- Batch network requests
- Use JobScheduler/WorkManager for deferred work
- Minimize wake locks
- Implement Doze mode compatibility

**Benchmarking**:
- Use Macrobenchmark for app startup and jank
- Use Microbenchmark for individual code paths
- Establish baseline metrics before optimization
- Profile on real devices, not just emulators

# Сводка (RU)

Оптимизация производительности в Android направлена на обеспечение плавного, отзывчивого пользовательского опыта через эффективное использование ресурсов. Основные области включают время запуска (холодный/теплый/горячий старт), производительность отрисовки (поддержка 60fps/120fps), управление памятью и энергоэффективность.

**Ключевые метрики производительности**:
- **Время запуска**: Время до первого отображения (TTID), время до полной отрисовки
- **Отрисовка**: Время кадра (<16мс для 60fps), процент "подвисаний"
- **Память**: Размер кучи, скорость аллокации, частота GC
- **Батарея**: Wake locks процессора, сетевые вызовы, использование сенсоров

**Инструменты профилирования**:
- **Android Profiler**: Мониторинг CPU, памяти, сети, энергопотребления в реальном времени
- **Systrace/Perfetto**: Системная трассировка для анализа пропусков кадров и ANR
- **Layout Inspector**: Анализ иерархии представлений для overdraw
- **Memory Profiler**: Дампы кучи, отслеживание аллокаций, обнаружение утечек

**Частые проблемы производительности**:
1. **Overdraw**: Многократная отрисовка одних и тех же пикселей
2. **Утечки памяти**: Удерживаемые объекты, препятствующие GC
3. **Jank**: Пропуски кадров, вызывающие "подвисания" UI
4. **ANR**: `Application` Not Responding (заблокированный главный поток)
5. **Медленный запуск**: Тяжелая инициализация на главном потоке

**Стратегии оптимизации**:

*Оптимизация запуска*:
- Ленивая инициализация некритичных компонентов
- Избегать тяжелой работы в `Application`.onCreate()
- Использовать ленивую инициализацию content providers
- Правильно реализовывать splash screens (Android 12+)

*Оптимизация отрисовки*:
- Уменьшение глубины иерархии представлений (`ConstraintLayout`, Compose)
- Включение аппаратного ускорения
- Использование `RecyclerView` с паттерном `ViewHolder`
- Эффективная загрузка изображений (Coil, Glide)
- Избегать overdraw (инструмент Debug GPU Overdraw)

*Оптимизация памяти*:
- Использование эффективных структур данных (ArrayMap, SparseArray)
- Правильная очистка с учетом жизненного цикла
- Избегать утечек контекста (WeakReference для слушателей)
- Использование LeakCanary для обнаружения утечек
- Оптимизация работы с `Bitmap` (downsampling, кеширование)

*Оптимизация потоков*:
- Перенос длительных операций с главного потока
- Использование Kotlin coroutines с подходящими диспетчерами
- Применение `WorkManager` для фоновых задач
- Избегать блокирующего I/O на главном потоке

*Оптимизация батареи*:
- Группировка сетевых запросов
- Использование JobScheduler/WorkManager для отложенной работы
- Минимизация wake locks
- Реализация совместимости с режимом Doze

**Бенчмаркинг**:
- Использование Macrobenchmark для запуска приложения и jank
- Использование Microbenchmark для отдельных участков кода
- Установка базовых метрик перед оптимизацией
- Профилирование на реальных устройствах, а не только на эмуляторах

## Use Cases / Trade-offs

**When to Optimize**:
- App startup takes >2 seconds
- Frame rate drops below 60fps during animations
- Memory usage grows unbounded
- Battery drain complaints from users
- ANRs or crashes in production

**Optimization Trade-offs**:
- **Code complexity vs performance**: Optimized code may be harder to maintain
- **Memory vs speed**: Caching improves speed but increases memory usage
- **Development time**: Premature optimization wastes resources
- **Feature richness vs performance**: Some features may need to be simplified

**Best Practice**: Profile first, optimize bottlenecks, measure impact. Don't optimize based on assumptions.

## References

- [Android Performance Best Practices](https://developer.android.com/topic/performance)
- [Android Profiler Guide](https://developer.android.com/studio/profile)
- [Perfetto Tracing](https://perfetto.dev/)
- [Macrobenchmark Guide](https://developer.android.com/topic/performance/benchmarking/macrobenchmark-overview)
- [Memory Management](https://developer.android.com/topic/performance/memory)
- [LeakCanary](https://square.github.io/leakcanary/)
