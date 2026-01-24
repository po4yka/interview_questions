---
id: android-lc-012
title: Doze and Standby Effects / Влияние Doze и Standby
aliases: []
topic: android
subtopics:
- lifecycle
- background
question_kind: theory
difficulty: medium
original_language: en
language_tags:
- en
- ru
source_note: Android interview preparation
status: draft
moc: moc-android
related:
- c-lifecycle
- c-background
created: 2025-01-23
updated: 2025-01-23
tags:
- android/lifecycle
- android/background
- difficulty/medium
anki_cards:
- slug: android-lc-012-0-en
  language: en
  anki_id: 1769172239335
  synced_at: '2026-01-23T16:45:05.359325'
- slug: android-lc-012-0-ru
  language: ru
  anki_id: 1769172239360
  synced_at: '2026-01-23T16:45:05.361353'
---
# Question (EN)
> How do Doze mode and App Standby affect app lifecycle and background work?

# Vopros (RU)
> Как Doze mode и App Standby влияют на lifecycle приложения и фоновую работу?

---

## Answer (EN)

**Doze mode** and **App Standby** are power-saving features that restrict background work when device or app is idle.

**Doze mode (API 23+):**
Activated when device is:
- Unplugged
- Stationary
- Screen off for extended time

**Restrictions in Doze:**
- Network access suspended
- Wake locks ignored
- AlarmManager deferred (except `setAndAllowWhileIdle`)
- JobScheduler deferred
- Wi-Fi scans stopped
- Sync adapters blocked

**Maintenance windows:**
```
[IDLE] -----> [MAINTENANCE] -----> [IDLE] -----> ...
   ^              |
   |              v
 Doze         Brief window for:
 active       - Deferred jobs
              - Network access
              - Syncs
```

**App Standby (API 23+):**
Individual app restriction when app is not used. Buckets (API 28+):
- **Active**: Currently in use
- **Working set**: Used regularly
- **Frequent**: Often used, not daily
- **Rare**: Rarely used
- **Restricted**: Minimal resources (API 30+)

**Impact by bucket:**
```kotlin
// Active: No restrictions
// Working set: Deferred jobs, limited
// Frequent: Jobs heavily restricted
// Rare: Network restricted, jobs very limited
// Restricted: Almost no background work
```

**Exemptions:**
```kotlin
// Check if app is exempt from battery optimizations
val pm = getSystemService(PowerManager::class.java)
val isIgnoringBattery = pm.isIgnoringBatteryOptimizations(packageName)

// Request exemption (rare cases only)
startActivity(Intent(Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS))
```

**Working with Doze:**
```kotlin
// Deferred alarm (respects Doze)
alarmManager.set(AlarmManager.RTC, time, pendingIntent)

// Important alarm (fires during Doze, but infrequent)
alarmManager.setAndAllowWhileIdle(AlarmManager.RTC, time, pendingIntent)

// Exact alarm (API 31+ needs SCHEDULE_EXACT_ALARM permission)
alarmManager.setExactAndAllowWhileIdle(AlarmManager.RTC, time, pendingIntent)
```

**Best practices:**
- Use WorkManager (respects all power modes)
- FCM high-priority for critical messages
- Foreground services for user-visible work
- Avoid requesting battery exemptions

## Otvet (RU)

**Doze mode** и **App Standby** - функции энергосбережения, которые ограничивают фоновую работу когда устройство или приложение простаивает.

**Doze mode (API 23+):**
Активируется когда устройство:
- Отключено от зарядки
- Неподвижно
- Экран выключен продолжительное время

**Ограничения в Doze:**
- Сетевой доступ приостановлен
- Wake locks игнорируются
- AlarmManager отложен (кроме `setAndAllowWhileIdle`)
- JobScheduler отложен
- Wi-Fi сканирование остановлено
- Sync адаптеры заблокированы

**Окна обслуживания:**
```
[IDLE] -----> [MAINTENANCE] -----> [IDLE] -----> ...
   ^              |
   |              v
 Doze         Короткое окно для:
 активен      - Отложенных jobs
              - Сетевого доступа
              - Синхронизаций
```

**App Standby (API 23+):**
Индивидуальное ограничение приложения когда оно не используется. Группы (API 28+):
- **Active**: Сейчас используется
- **Working set**: Используется регулярно
- **Frequent**: Часто используется, не ежедневно
- **Rare**: Редко используется
- **Restricted**: Минимальные ресурсы (API 30+)

**Влияние по группам:**
```kotlin
// Active: Нет ограничений
// Working set: Jobs отложены, ограничены
// Frequent: Jobs сильно ограничены
// Rare: Сеть ограничена, jobs очень ограничены
// Restricted: Почти нет фоновой работы
```

**Исключения:**
```kotlin
// Проверить исключено ли приложение из оптимизации батареи
val pm = getSystemService(PowerManager::class.java)
val isIgnoringBattery = pm.isIgnoringBatteryOptimizations(packageName)

// Запросить исключение (только в редких случаях)
startActivity(Intent(Settings.ACTION_IGNORE_BATTERY_OPTIMIZATION_SETTINGS))
```

**Работа с Doze:**
```kotlin
// Отложенный alarm (уважает Doze)
alarmManager.set(AlarmManager.RTC, time, pendingIntent)

// Важный alarm (срабатывает в Doze, но нечасто)
alarmManager.setAndAllowWhileIdle(AlarmManager.RTC, time, pendingIntent)

// Точный alarm (API 31+ требует разрешение SCHEDULE_EXACT_ALARM)
alarmManager.setExactAndAllowWhileIdle(AlarmManager.RTC, time, pendingIntent)
```

**Лучшие практики:**
- Используйте WorkManager (уважает все режимы питания)
- FCM high-priority для критичных сообщений
- Foreground services для видимой пользователю работы
- Избегайте запросов исключений из батареи

---

## Follow-ups
- How to test Doze mode during development?
- What is the difference between Doze and light Doze?
- How does FCM high-priority work with Doze?

## References
- [[c-lifecycle]]
- [[c-background]]
- [[moc-android]]
