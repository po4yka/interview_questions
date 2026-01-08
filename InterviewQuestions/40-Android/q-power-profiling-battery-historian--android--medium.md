---\
id: android-626
title: Power Profiling with Battery Historian / Профилирование энергии с Battery Historian
aliases: [Power Profiling with Battery Historian, Профилирование энергии с Battery Historian]
topic: android
subtopics: [monitoring-slo, performance-battery, profiling]
question_kind: android
difficulty: medium
original_language: ru
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-profiling, q-android-performance-measurement-tools--android--medium, q-compose-core-components--android--medium, q-dagger-build-time-optimization--android--medium, q-data-sync-unstable-network--android--hard]
created: 2025-10-20
updated: 2025-11-10
tags: [android/monitoring-slo, android/performance-battery, android/profiling, battery, difficulty/medium]
sources:
  - "https://developer.android.com/topic/performance/power/battery-historian"
---\
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
- Запустите Battery Historian локально (web UI, например через `go run` или Docker в соответствии с официальной инструкцией) и загрузите bugreport.

### 2. Анализ Battery Historian

- **Wakelock** граф: ищите длинные PARTIAL wakelocks (приложение держит CPU).
- **JobScheduler/AlarmManager**: частые срабатывания → возможное нарушение квот и повышенное потребление.
- **Network**: пики в `Mobile radio` → проверьте batching запросов и избыточные вызовы.
- **Device idle/App standby**: убедитесь, что приложение уважает Doze и не держит устройство постоянно бодрствующим.

### 3. Energy Profiler (Android Studio)

- Подключите устройство, включите Energy профайлер.
- Захватывайте `System Events`, `Network`, `Location`, `Wakelock`.
- Сравните с логами/метриками, чтобы локализовать проблемные участки кода, вызывающие частые пробуждения или сетевую активность.

### 4. План Действий

- **Wakelock leaks**: убедитесь, что `wakeLock.release()` вызывается гарантированно (например, в `finally` или в коллбэке по завершении работы); не полагайтесь на таймауты/корутины как на автоматическое освобождение.
- **Network batching**: объединяйте запросы, используйте эффективные протоколы (например, HTTP/2), применяйте `WorkManager` с `setRequiredNetworkType` для фоновой синхронизации.
- **Location**: переключите на более экономичные режимы (например, `PRIORITY_BALANCED_POWER_ACCURACY`), используйте геозоны вместо частого polling, пересмотрите частоту обновлений.
- **Background tasks**: используйте WorkManager/JobScheduler вместо долгоживущих ручных сервисов и нецелевых foreground-сервисов.

### 5. Мониторинг

- Внедрите runtime метрики по энергопотреблению: длительность wakelock, частота задач, сетевые паттерны, собственные логи.
- Настройте regression-тесты (например, macrobenchmark с оценкой косвенных energy-показателей).
- Периодически анализируйте `dumpsys batterystats` и новые bugreport для отслеживания изменений во времени.

Также см. [[c-android-profiling]].

---

## Answer (EN)

### 1. Preparation

- Reset stats: `adb shell dumpsys batterystats --reset`.
- Run a representative scenario (typically 15–30 minutes) covering both foreground and background behavior.
- Capture a bugreport: `adb bugreport bugreport.zip`.
- Run the Battery Historian web UI locally (e.g., via `go run` or Docker as per the official guide) and upload the bugreport.

### 2. Battery Historian Analysis

- **Wakelock graph**: look for long partial wakelocks where the app holds the CPU.
- **JobScheduler/AlarmManager**: frequent triggers may violate quotas and waste power.
- **Network**: spikes in `Mobile radio` → check request batching and redundant calls.
- **Device idle/App standby**: ensure the app respects Doze/App Standby and doesn’t keep the device awake.

### 3. Energy Profiler (Android Studio)

- Attach a device and open the Energy Profiler.
- Capture `System Events`, `Network`, `Location`, `Wakelock`.
- Correlate with logs/metrics to pinpoint code paths causing frequent wakeups or network activity.

### 4. Action Plan

- **Wakelock leaks**: ensure `wakeLock.release()` is always called (e.g., in `finally` or completion callbacks); do not rely on timeouts/coroutines as automatic release mechanisms.
- **Network batching**: batch requests, use efficient protocols (e.g., HTTP/2), and schedule background sync via `WorkManager` with `setRequiredNetworkType` (or similar constraints) instead of ad-hoc background work.
- **Location**: switch to more power-friendly modes (e.g., `PRIORITY_BALANCED_POWER_ACCURACY`), use geofencing instead of frequent polling, and review update frequency.
- **Background tasks**: prefer WorkManager/JobScheduler over long-running manual services or unnecessary foreground services.

### 5. Monitoring

- Track runtime power-related metrics: wakelock durations, task frequencies, network patterns, custom logs.
- Add regression tests (e.g., macrobenchmark-style scenarios that observe indirect energy indicators).
- Periodically review `dumpsys batterystats` output and new bugreports to see trends over time.

---

## Дополнительные Вопросы (RU)
- Как измерять энергопотребление на уровне функций (on-device power rails)?
- Как анализировать влияние foreground services на Doze?
- Как автоматизировать energy regression тесты в CI?

## Follow-ups (EN)
- How can you measure power at the function level (on-device power rails)?
- How to analyze the impact of foreground services on Doze?
- How to automate energy regression tests in CI?

## Ссылки (RU)
- "https://developer.android.com/topic/performance/power/battery-historian"

## References
- https://developer.android.com/topic/performance/power/battery-historian

## Связанные Вопросы (RU)
- [[q-android-performance-measurement-tools--android--medium]]

## Related Questions
- [[q-android-performance-measurement-tools--android--medium]]
