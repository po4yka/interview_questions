---
id: android-626
title: Power Profiling with Battery Historian / Профилирование энергии с Battery Historian
aliases:
  - Power Profiling with Battery Historian
  - Профилирование энергии с Battery Historian
topic: android
subtopics:
  - performance
  - power
  - energy
question_kind: android
difficulty: medium
original_language: ru
language_tags:
  - ru
  - en
status: draft
moc: moc-android
related:
  - c-power-profiling
  - q-android-coverage-gaps--android--hard
created: 2025-11-02
updated: 2025-11-02
tags:
  - android/power
  - android/performance
  - battery
  - difficulty/medium
sources:
  - url: https://developer.android.com/topic/performance/power/battery-historian
    note: Battery Historian guide
---

# Вопрос (RU)
> Как провести анализ энергопотребления приложения с помощью Battery Historian и Energy Profiler: сбор данных, интерпретация wakelock, сетевой активности и план устранения проблем?

# Question (EN)
> How do you analyze an app’s power usage using Battery Historian and the Energy Profiler, capturing data, interpreting wakelocks/network activity, and planning remediation?

---

## Ответ (RU)

### 1. Подготовка

- Сбросьте статистику: `adb shell dumpsys batterystats --reset`.
- Запустите сценарий (обычно 15–30 минут), включающий foreground/background операции.
- Снимите bugreport: `adb bugreport bugreport.zip`.
- Откройте Battery Historian (`./historian.py` или онлайн сервис), загрузите bugreport.

### 2. Анализ Battery Historian

- **Wakelock** граф: ищите длинные PARTIAL wakelocks (приложение держит CPU).
- **JobScheduler/AlarmManager**: частые срабатывания → нарушение квот.
- **Network**: spikes в `Mobile radio` → проверьте batching запросов.
- **Device idle/App standby**: убедитесь, что приложение уважает Doze.

### 3. Energy Profiler (Android Studio)

- Подключите устройство, включите Energy профайлер.
- Захватывайте `System Events`, `Network`, `Location`, `Wakelock`.
- Сравните с логами/метриками для pinpoint проблемного фрагмента кода.

### 4. План действий

- **Wakelock leaks**: убедитесь, что `wakeLock.release()` в `finally`, используйте `withTimeout`.
- **Network batching**: объединяйте запросы, включайте HTTP/2, используйте WorkManager с `setRequiredNetworkType`.
- **Location**: переключите на `PRIORITY_BALANCED_POWER_ACCURACY`, используйте геозоны вместо polling.
- **Background tasks**: используйте WorkManager/JobScheduler вместо ручных сервисов.

### 5. Мониторинг

- Внедрите runtime метрики (`PowerMetrics`, custom logs).
- Настройте regression-тесты (macrobenchmark + energy).
- Регулярно проверяйте `dumpsys batterystats --enable full-wake-history`.

---

## Answer (EN)

- Reset batterystats, exercise representative scenarios, capture a bugreport, and load it into Battery Historian.
- Inspect wakelock durations, JobScheduler/Alarm usage, and network spikes; correlate with app logs.
- Use Android Studio Energy Profiler to localize code paths causing excessive wakeups or radio usage.
- Implement fixes: ensure wake locks release, batch network calls, optimize location updates, and migrate background work to WorkManager.
- Monitor regressions with automated energy profiling and runtime metrics.

---

## Follow-ups
- Как измерять энергопотребление на уровне функций (on-device power rails)?
- Как анализировать влияние foreground services на Doze?
- Как автоматизировать energy regression тесты в CI?

## References
- [[c-power-profiling]]
- [[q-android-coverage-gaps--android--hard]]
- https://developer.android.com/topic/performance/power/battery-historian

## Related Questions

- [[c-power-profiling]]
- [[q-android-coverage-gaps--android--hard]]
