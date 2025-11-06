---
id: ivc-20251102-013
title: Power Profiling on Android / Профилирование потребления энергии на Android
aliases:
  - Battery Historian
  - Android Energy Profiler
kind: concept
summary: Tools and techniques for analyzing power consumption including Battery Historian, Energy Profiler, and wake lock audits
links: []
created: 2025-11-02
updated: 2025-11-02
tags:
  - android
  - concept
  - performance
  - power
  - energy
---

# Summary (EN)

Android power profiling combines Battery Historian, Android Studio Energy Profiler, and system dumps (`dumpsys batterystats`, `wakelock`) to identify energy drains, wake lock misuse, and network spikes.

# Сводка (RU)

Профилирование энергопотребления Android включает Battery Historian, Energy Profiler и системные дампы (`dumpsys batterystats`, `wakelock`) для выявления утечек энергии, неправильных wake lock и сетевых всплесков.

## Tools

- `adb bugreport` + Battery Historian (web UI)
- Android Studio Energy Profiler
- `adb shell dumpsys batterystats`, `adb shell dumpsys alarm`
- Power Profiler (Pixel hardware), Qualcomm Trepn Analyzer

## Considerations

- Необходимо сбрасывать batterystats (`adb shell dumpsys batterystats --reset`) перед замером.
- Сводить данные по категориям: CPU, wakelocks, net stats.
- На Android 13+ `JobScheduler` и `WorkManager` имеют quota, мониторинг важен.

