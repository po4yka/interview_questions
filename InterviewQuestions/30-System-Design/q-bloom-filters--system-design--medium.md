---
id: sysdes-036
title: Bloom Filters
aliases:
- Bloom Filter
- Probabilistic Data Structure
topic: system-design
subtopics:
- data-structures
- databases
- optimization
question_kind: system-design
difficulty: medium
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-database-indexing--system-design--medium
- q-caching-strategies--system-design--medium
created: 2025-01-23
updated: 2025-01-23
tags:
- data-structures
- difficulty/medium
- optimization
- system-design
anki_cards:
- slug: sysdes-036-0-en
  language: en
  anki_id: 1769159521045
  synced_at: '2026-01-23T13:49:17.776997'
- slug: sysdes-036-0-ru
  language: ru
  anki_id: 1769159521069
  synced_at: '2026-01-23T13:49:17.778904'
---
# Question (EN)
> What is a Bloom filter? How does it work, and when would you use it in system design?

# Vopros (RU)
> Что такое фильтр Блума? Как он работает и когда его использовать в проектировании систем?

---

## Answer (EN)

**Bloom filter** is a space-efficient probabilistic data structure that tests whether an element is a member of a set.

### Key Properties

- **False positives possible**: "Maybe in set"
- **False negatives impossible**: "Definitely not in set"
- **Space efficient**: Much smaller than storing actual elements
- **No deletion**: Standard bloom filters don't support removal

### How It Works

```
1. Create bit array of size m, all zeros
2. Use k hash functions

Add element:
  hash1("apple") = 3  → set bit 3
  hash2("apple") = 7  → set bit 7
  hash3("apple") = 1  → set bit 1

Check element:
  hash1("apple") → bit 3 = 1? ✓
  hash2("apple") → bit 7 = 1? ✓
  hash3("apple") → bit 1 = 1? ✓
  All bits set → "Probably in set"

  hash1("banana") → bit 5 = 0? ✗
  At least one 0 → "Definitely not in set"
```

### False Positive Rate

```
FPR ≈ (1 - e^(-kn/m))^k

m = bit array size
n = number of elements
k = number of hash functions

Example: m=1M bits, n=100K elements, k=7
FPR ≈ 0.8% (1 in 125 false positives)
```

### Use Cases

| Use Case | Why Bloom Filter |
|----------|------------------|
| Database: avoid disk reads | Check if key might exist before disk I/O |
| Cache: check before expensive lookup | Avoid network call if definitely not cached |
| Spam filter | Quick check against blocklist |
| Duplicate detection | "Have we seen this before?" |
| CDN | Check if content is cached at edge |

### Example: Database Optimization

```
Without Bloom Filter:
Query → Check disk (expensive) → Not found

With Bloom Filter:
Query → Check bloom filter (cheap) → "Not in set" → Skip disk
Query → Check bloom filter → "Maybe in set" → Check disk
```

### Counting Bloom Filter

Variant that supports deletion:
- Use counters instead of bits
- Increment on add, decrement on remove
- Uses more space (typically 4 bits per counter)

---

## Otvet (RU)

**Фильтр Блума** - пространственно-эффективная вероятностная структура данных для проверки принадлежности элемента множеству.

### Ключевые свойства

- **Ложноположительные возможны**: "Возможно в множестве"
- **Ложноотрицательные невозможны**: "Точно не в множестве"
- **Эффективно по памяти**: Гораздо меньше хранения самих элементов
- **Без удаления**: Стандартные фильтры Блума не поддерживают удаление

### Как это работает

```
1. Создаем битовый массив размера m, все нули
2. Используем k хеш-функций

Добавление элемента:
  hash1("apple") = 3  → устанавливаем бит 3
  hash2("apple") = 7  → устанавливаем бит 7
  hash3("apple") = 1  → устанавливаем бит 1

Проверка элемента:
  hash1("apple") → бит 3 = 1? ✓
  hash2("apple") → бит 7 = 1? ✓
  hash3("apple") → бит 1 = 1? ✓
  Все биты установлены → "Вероятно в множестве"

  hash1("banana") → бит 5 = 0? ✗
  Хотя бы один 0 → "Точно не в множестве"
```

### Частота ложноположительных

```
FPR ≈ (1 - e^(-kn/m))^k

m = размер битового массива
n = количество элементов
k = количество хеш-функций
```

### Применение

| Случай | Зачем Bloom Filter |
|--------|-------------------|
| БД: избежать чтения с диска | Проверить существование ключа до I/O |
| Кеш: проверка перед дорогим поиском | Избежать сетевого вызова |
| Спам-фильтр | Быстрая проверка по блок-листу |
| Детекция дубликатов | "Видели ли мы это раньше?" |
| CDN | Проверить закеширован ли контент на edge |

---

## Follow-ups

- What is a Counting Bloom Filter?
- How does HyperLogLog compare to Bloom filters?
- What is a Cuckoo filter?
