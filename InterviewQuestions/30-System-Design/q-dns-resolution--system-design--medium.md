---
id: sysdes-015
title: DNS and DNS Resolution
aliases:
- Domain Name System
- DNS Resolution
topic: system-design
subtopics:
- networking
- infrastructure
- dns
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-cdn-content-delivery-network--system-design--medium
- q-load-balancing-strategies--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- networking
- difficulty/medium
- infrastructure
- system-design
anki_cards:
- slug: sysdes-015-0-en
  language: en
  anki_id: 1769158890041
  synced_at: '2026-01-23T13:49:17.716563'
- slug: sysdes-015-0-ru
  language: ru
  anki_id: 1769158890066
  synced_at: '2026-01-23T13:49:17.718436'
---
# Question (EN)
> How does DNS work? Explain the DNS resolution process and its role in system design.

# Vopros (RU)
> Как работает DNS? Объясните процесс разрешения DNS и его роль в проектировании систем.

---

## Answer (EN)

**DNS (Domain Name System)** translates human-readable domain names (google.com) into IP addresses (142.250.80.46).

### DNS Resolution Process

```
User types "example.com"
         ↓
1. Browser Cache → Found? Return IP
         ↓ Not found
2. OS Cache → Found? Return IP
         ↓ Not found
3. Recursive Resolver (ISP) → Found? Return IP
         ↓ Not found
4. Root Name Server → Returns TLD server (.com)
         ↓
5. TLD Name Server → Returns authoritative NS
         ↓
6. Authoritative Name Server → Returns IP address
         ↓
Response cached at each level, IP returned to browser
```

### DNS Record Types

| Type | Purpose | Example |
|------|---------|---------|
| A | IPv4 address | example.com → 93.184.216.34 |
| AAAA | IPv6 address | example.com → 2606:2800:220:1:... |
| CNAME | Alias to another domain | www.example.com → example.com |
| MX | Mail server | example.com → mail.example.com |
| NS | Name server | example.com → ns1.example.com |
| TXT | Text records | SPF, DKIM, verification |

### DNS in System Design

**1. Load Balancing (DNS Round Robin)**
```
example.com → 192.168.1.1
           → 192.168.1.2
           → 192.168.1.3
(Rotates through IPs)
```

**2. Geographic Routing (GeoDNS)**
```
US user  → example.com → US datacenter IP
EU user  → example.com → EU datacenter IP
```

**3. Failover**
```
Primary healthy:   example.com → primary-ip (TTL: 60s)
Primary fails:     example.com → backup-ip  (health check triggers)
```

### TTL (Time To Live)

- Controls how long DNS records are cached
- **Low TTL (60s)**: Fast failover, more DNS queries
- **High TTL (86400s)**: Less queries, slower updates

**Trade-off:**
```
Faster failover ←──── TTL ────→ Less DNS load
    (low TTL)                    (high TTL)
```

### DNS Considerations for System Design

| Concern | Solution |
|---------|----------|
| Single point of failure | Multiple NS, anycast |
| Slow propagation | Lower TTL before changes |
| DDoS attacks | DNS providers with DDoS protection |
| Cache poisoning | DNSSEC |

---

## Otvet (RU)

**DNS (Domain Name System)** преобразует читаемые доменные имена (google.com) в IP-адреса (142.250.80.46).

### Процесс разрешения DNS

```
Пользователь вводит "example.com"
         ↓
1. Кеш браузера → Найден? Вернуть IP
         ↓ Не найден
2. Кеш ОС → Найден? Вернуть IP
         ↓ Не найден
3. Рекурсивный резолвер (ISP) → Найден? Вернуть IP
         ↓ Не найден
4. Корневой сервер имен → Возвращает TLD сервер (.com)
         ↓
5. TLD сервер имен → Возвращает авторитетный NS
         ↓
6. Авторитетный сервер имен → Возвращает IP-адрес
         ↓
Ответ кешируется на каждом уровне, IP возвращается браузеру
```

### Типы DNS-записей

| Тип | Назначение | Пример |
|-----|------------|--------|
| A | IPv4 адрес | example.com → 93.184.216.34 |
| AAAA | IPv6 адрес | example.com → 2606:2800:220:1:... |
| CNAME | Алиас на другой домен | www.example.com → example.com |
| MX | Почтовый сервер | example.com → mail.example.com |
| NS | Сервер имен | example.com → ns1.example.com |
| TXT | Текстовые записи | SPF, DKIM, верификация |

### DNS в проектировании систем

**1. Балансировка нагрузки (DNS Round Robin)**
```
example.com → 192.168.1.1
           → 192.168.1.2
           → 192.168.1.3
(Ротация через IP-адреса)
```

**2. Географическая маршрутизация (GeoDNS)**
```
US пользователь → example.com → IP датацентра в США
EU пользователь → example.com → IP датацентра в ЕС
```

**3. Отказоустойчивость**
```
Primary работает:  example.com → primary-ip (TTL: 60s)
Primary упал:      example.com → backup-ip  (срабатывает health check)
```

### TTL (Time To Live)

- Контролирует время кеширования DNS-записей
- **Низкий TTL (60s)**: Быстрый failover, больше DNS-запросов
- **Высокий TTL (86400s)**: Меньше запросов, медленнее обновления

**Компромисс:**
```
Быстрее failover ←──── TTL ────→ Меньше нагрузки на DNS
   (низкий TTL)                    (высокий TTL)
```

### DNS в проектировании систем

| Проблема | Решение |
|----------|---------|
| Единая точка отказа | Несколько NS, anycast |
| Медленное распространение | Снизить TTL перед изменениями |
| DDoS атаки | DNS-провайдеры с защитой от DDoS |
| Cache poisoning | DNSSEC |

---

## Follow-ups

- What is DNS anycast and how does it improve availability?
- How does DNS-based load balancing compare to hardware load balancers?
- What is DNSSEC and why is it important?

## Related Questions

### Prerequisites (Easier)
- [[q-horizontal-vertical-scaling--system-design--medium]] - Scaling basics

### Related (Same Level)
- [[q-cdn-content-delivery-network--system-design--medium]] - CDN
- [[q-load-balancing-strategies--system-design--medium]] - Load balancing

### Advanced (Harder)
- [[q-design-twitter--system-design--hard]] - System design example
