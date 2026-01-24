---
id: sysdes-046
title: Design Netflix
aliases:
- Design Netflix
- Video Streaming Service
- Content Delivery System
topic: system-design
subtopics:
- design-problems
- video-streaming
- personalization
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-design-youtube--system-design--hard
- q-cdn--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- design-problems
- difficulty/hard
- video-streaming
- system-design
anki_cards:
- slug: sysdes-046-0-en
  language: en
  anki_id: 1769159521244
  synced_at: '2026-01-23T13:49:17.793260'
- slug: sysdes-046-0-ru
  language: ru
  anki_id: 1769159521268
  synced_at: '2026-01-23T13:49:17.794809'
---
# Question (EN)
> Design a video streaming service like Netflix. Focus on content delivery, personalization, and global scale.

# Vopros (RU)
> Спроектируйте сервис видеостриминга типа Netflix. Фокус на доставке контента, персонализации и глобальном масштабе.

---

## Answer (EN)

### Requirements

**Functional**: Browse catalog, stream video, personalized recommendations, multi-device playback
**Non-functional**: 99.99% availability, <200ms start time, global delivery, adaptive quality

### Netflix vs YouTube Key Differences

| Aspect | Netflix | YouTube |
|--------|---------|---------|
| Content | Licensed, original | User-generated |
| Upload | Internal workflow | Public API |
| Quality focus | Premium 4K HDR | Variable |
| Monetization | Subscription | Ads |

### High-Level Architecture

```
┌──────────────────────────────────────────────────────────┐
│                     Client Apps                          │
│          (Smart TV, Mobile, Browser, Console)           │
└────────────────────────┬─────────────────────────────────┘
                         │
┌────────────────────────▼─────────────────────────────────┐
│                 Open Connect CDN                         │
│      (Netflix's own CDN - ISP-embedded servers)         │
└────────────────────────┬─────────────────────────────────┘
                         │ (API calls)
┌────────────────────────▼─────────────────────────────────┐
│                    AWS Backend                           │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌────────────┐  │
│  │ Playback │ │Recommend │ │ Catalog  │ │ User       │  │
│  │ Service  │ │ Service  │ │ Service  │ │ Service    │  │
│  └──────────┘ └──────────┘ └──────────┘ └────────────┘  │
└──────────────────────────────────────────────────────────┘
```

### Open Connect CDN

```
Netflix's CDN Strategy:
- 15,000+ servers worldwide
- Deployed inside ISPs (no transit cost)
- Pre-positioned content during off-peak hours
- 95% of traffic served from ISP-local servers

Cache Strategy:
1. Popular content → Every edge server
2. Regional content → Regional servers
3. Long-tail → Origin or nearest regional
```

### Playback Flow

```
1. User clicks Play
2. Client → Playback Service: "Get stream URL for title X"
3. Playback Service:
   - Check entitlement
   - Select best CDN server (latency, load)
   - Generate secure signed URL
4. Client → CDN: Fetch manifest
5. Client → CDN: Fetch video chunks (adaptive)
6. Playback starts in <200ms
```

### Recommendation System

```
Components:
┌─────────────────────────────────────────────┐
│           Recommendation Pipeline           │
├─────────────────────────────────────────────┤
│ 1. Data Collection                          │
│    - Watch history, ratings, browse behavior│
│    - Time of day, device type              │
│                                            │
│ 2. Offline Processing (Spark, Flink)       │
│    - Collaborative filtering               │
│    - Content-based similarity              │
│    - Train ML models                       │
│                                            │
│ 3. Online Serving                          │
│    - Personalized ranking                  │
│    - A/B testing different algorithms      │
│    - Real-time updates                     │
└─────────────────────────────────────────────┘

Result: 80% of watched content comes from recommendations
```

### Key Technical Choices

| Component | Technology | Why |
|-----------|------------|-----|
| CDN | Open Connect | Control, cost, quality |
| Backend | AWS (multi-region) | Reliability |
| Data Processing | Spark, Flink | Scale |
| Storage | S3, Cassandra | Durability, scale |
| Streaming | Adaptive bitrate | Quality vs bandwidth |

---

## Otvet (RU)

### Требования

**Функциональные**: Просмотр каталога, стриминг видео, персонализированные рекомендации
**Нефункциональные**: 99.99% доступность, <200мс до начала воспроизведения, глобальная доставка

### Open Connect CDN

```
Стратегия CDN Netflix:
- 15,000+ серверов по всему миру
- Развёрнуты внутри ISP (нет транзитных расходов)
- Контент размещается заранее в непиковые часы
- 95% трафика обслуживается с локальных серверов ISP

Стратегия кеширования:
1. Популярный контент → Каждый edge сервер
2. Региональный контент → Региональные серверы
3. Long-tail → Origin или ближайший региональный
```

### Поток воспроизведения

```
1. Пользователь нажимает Play
2. Клиент → Playback Service: "Получить URL для title X"
3. Playback Service:
   - Проверить права доступа
   - Выбрать лучший CDN сервер (задержка, нагрузка)
   - Сгенерировать подписанный URL
4. Клиент → CDN: Получить манифест
5. Клиент → CDN: Получить чанки видео (адаптивно)
6. Воспроизведение начинается за <200мс
```

### Система рекомендаций

```
Компоненты:
1. Сбор данных
   - История просмотров, рейтинги, поведение
   - Время суток, тип устройства

2. Offline обработка (Spark, Flink)
   - Коллаборативная фильтрация
   - Content-based similarity
   - Обучение ML моделей

3. Online выдача
   - Персонализированное ранжирование
   - A/B тестирование алгоритмов

Результат: 80% просмотренного контента из рекомендаций
```

### Ключевые технические решения

| Компонент | Технология | Почему |
|-----------|------------|--------|
| CDN | Open Connect | Контроль, стоимость, качество |
| Backend | AWS (multi-region) | Надёжность |
| Storage | S3, Cassandra | Durability, масштаб |

---

## Follow-ups

- How does Netflix handle regional content licensing?
- What is the difference between Open Connect and traditional CDN?
- How does Netflix implement download for offline viewing?
