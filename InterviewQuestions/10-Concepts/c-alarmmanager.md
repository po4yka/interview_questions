---
id: "20251110-135440"
title: "Alarmmanager / Alarmmanager"
aliases: ["Alarmmanager"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
status: "draft"
moc: "moc-kotlin"
related: []
created: "2025-11-10"
updated: "2025-11-10"
tags: ["programming-languages", "concept", "difficulty/medium", "auto-generated"]
---

# Summary (EN)

AlarmManager is an Android system service that schedules your app's operations to run at specific times or intervals, even when the app is not in the foreground. It is used for time-based tasks such as reminders, periodic syncs, or deferred work that must trigger via system-managed alarms. Correct use of AlarmManager helps balance reliability with battery efficiency, especially when combined with exact/inexact alarms and device idle modes.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

AlarmManager — это системный сервис Android для планирования выполнения операций приложения в определённое время или с заданным интервалом, включая случаи, когда приложение не находится на переднем плане. Он используется для задач, завязанных на время: напоминания, периодическая синхронизация, отложенные действия, которые должны запускаться через системные «будильники». Корректное использование AlarmManager важно для надёжности и экономии батареи, особенно с учётом точных/неточных будильников и режимов энергосбережения устройства.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Types of alarms: supports exact, inexact, repeating, and idle/boot-aware alarms via methods like set(), setExact(), setRepeating(), setWindow(), and setAndAllowWhileIdle().
- Persistence and process independence: alarms are managed by the system; they can wake the app or device even if the process is killed (subject to API level and flags).
- Power and API constraints: from Android 6.0+, Doze and App Standby restrict alarms; exact alarms are limited and require careful use to avoid battery drain.
- Common usage: used for time-based triggers (e.g., calendar alerts), but non-urgent or network/background work is often better handled by WorkManager or JobScheduler.
- Permissions and boot handling: waking the device or surviving reboots may require USE_EXACT_ALARM (on newer APIs), SCHEDULE_EXACT_ALARM, WAKE_LOCK (historically), and handling BOOT_COMPLETED to reschedule alarms.

## Ключевые Моменты (RU)

- Типы будильников: поддерживает точные, неточные, повторяющиеся и учитывающие простои/перезагрузку будильники через методы set(), setExact(), setRepeating(), setWindow(), setAndAllowWhileIdle().
- Управление системой: будильники планируются и хранятся системой; они могут запускать приложение или будить устройство даже после убийства процесса (с учётом версии Android и флагов).
- Ограничения энергосбережения: начиная с Android 6.0+, Doze и App Standby ограничивают срабатывание будильников; точные будильники лимитируются и должны использоваться осторожно, чтобы не разряжать батарею.
- Типичные сценарии: триггер напоминаний, сигналов календаря, тайм-аутов; для фоновой/сетевой работы без жёстких временных требований предпочтительнее WorkManager или JobScheduler.
- Разрешения и после перезагрузки: для пробуждения устройства или сохранения поведения после перезагрузки могут потребоваться USE_EXACT_ALARM / SCHEDULE_EXACT_ALARM, WAKE_LOCK (ранее) и обработка BOOT_COMPLETED для повторного планирования будильников.

## References

- Android Developers: AlarmManager API reference — https://developer.android.com/reference/android/app/AlarmManager
- Android Developers: Guides on background work and alarms — https://developer.android.com/guide/background
