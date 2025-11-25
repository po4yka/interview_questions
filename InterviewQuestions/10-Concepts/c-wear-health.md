---
id: ivc-20251102-004
title: Wear OS Health Stack / Стек здоровья Wear OS
aliases: [Health Connect Wear, Wear OS Health Services]
kind: concept
summary: APIs for collecting health data on Wear OS including Health Services, Health Connect and permissions
links: []
created: 2025-11-02
updated: 2025-11-02
tags: [android, concept, health, sensors, wear]
date created: Thursday, November 6th 2025, 4:39:51 pm
date modified: Tuesday, November 25th 2025, 8:54:02 pm
---

# Summary (EN)

The **Wear OS health stack** consists of Health Services (on-device sensor APIs) and Health Connect (data sharing hub between apps). Health Services provides energy-efficient access to sensors (heart rate, steps, calories) with batching and goal sessions, while Health Connect synchronizes data to companion devices and enforces fine-grained permissions.

# Сводка (RU)

**Стек здоровья Wear OS** включает Health Services (доступ к сенсорам на устройстве) и Health Connect (централизованный обмен данными между приложениями). Health Services предоставляет энергетически эффективный доступ к сердечному ритму, шагам, калориям и т.д., а Health Connect отвечает за синхронизацию данных с другими приложениями и строгие разрешения.

## Core Components

- `HealthServicesClient` / `MeasureClient`, `ExerciseClient`, `PassiveMonitoringClient`
- Goal-based sessions с `ExerciseUpdateCallback`
- Health Connect permissions (e.g., `Permission.HEART_RATE_READ`)
- Data types: raw vs aggregated, permissions scopes (read/write)

## Considerations

- Health Services предпочитает batching и требует foreground service для интенсивных сессий.
- Health Connect требует отдельного consent UI и может работать offline с последующей синхронизацией.
- Производительность критична: используйте passive monitoring для фоновых сценариев.

