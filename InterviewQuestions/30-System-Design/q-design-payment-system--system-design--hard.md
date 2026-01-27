---
id: sysdes-077
title: Design Payment System
aliases:
- Payment System
- Payment Gateway
- Payment Processing
topic: system-design
subtopics:
- fintech
- distributed-transactions
- reliability
question_kind: system-design
difficulty: hard
original_language: en
language_tags:
- en
- ru
status: draft
moc: moc-system-design
related:
- q-saga-pattern--system-design--hard
- q-idempotency--system-design--medium
- q-acid-properties--system-design--medium
- q-two-phase-commit--system-design--hard
created: 2025-01-26
updated: 2025-01-26
tags:
- system-design
- difficulty/hard
- fintech
- distributed-transactions
---
# Question (EN)
> How would you design a payment processing system like Stripe or PayPal?

# Vopros (RU)
> Как бы вы спроектировали платёжную систему, подобную Stripe или PayPal?

---

## Answer (EN)

### Requirements

**Functional:**
- Process credit/debit card payments
- Support multiple currencies
- Handle refunds and chargebacks
- Provide merchant dashboard and APIs
- Store payment methods securely
- Generate invoices and receipts
- Support recurring payments (subscriptions)

**Non-Functional:**
- 99.999% availability (5 nines = ~5 min downtime/year)
- Exactly-once payment processing
- PCI DSS Level 1 compliance
- <500ms payment authorization latency
- Complete audit trail for all transactions
- Multi-region disaster recovery

**Scale Estimates:**
- 1M merchants, 100M transactions/day
- Peak: 10K transactions/second
- $10B+ daily transaction volume

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           API Gateway                                    │
│                 (Rate limiting, Auth, SSL termination)                   │
└──────────────────────────────┬──────────────────────────────────────────┘
                               │
        ┌──────────────────────┼──────────────────────┐
        │                      │                      │
        ▼                      ▼                      ▼
┌───────────────┐    ┌─────────────────┐    ┌─────────────────┐
│ Payment API   │    │  Merchant API   │    │  Webhook API    │
│ Service       │    │  Service        │    │  Service        │
└───────┬───────┘    └────────┬────────┘    └────────┬────────┘
        │                     │                      │
        └─────────────────────┼──────────────────────┘
                              │
              ┌───────────────▼───────────────┐
              │       Payment Orchestrator     │
              │   (Saga coordinator, state)    │
              └───────────────┬───────────────┘
                              │
     ┌────────────────────────┼────────────────────────┐
     │                        │                        │
     ▼                        ▼                        ▼
┌──────────┐           ┌──────────────┐         ┌──────────────┐
│  Fraud   │           │   Risk       │         │   Ledger     │
│  Detection│           │   Engine     │         │   Service    │
└──────────┘           └──────────────┘         └──────────────┘
                              │
              ┌───────────────▼───────────────┐
              │     Payment Gateway Router     │
              │   (Intelligent routing)        │
              └───────────────┬───────────────┘
                              │
        ┌─────────────────────┼─────────────────────┐
        │                     │                     │
        ▼                     ▼                     ▼
  ┌───────────┐        ┌───────────┐        ┌───────────┐
  │   Visa    │        │MasterCard │        │   AMEX    │
  │  Network  │        │  Network  │        │  Network  │
  └───────────┘        └───────────┘        └───────────┘
```

### Payment Flow (Authorization + Capture)

```
Payment Flow States:

INITIATED → AUTHORIZED → CAPTURED → SETTLED
    │            │            │
    ▼            ▼            ▼
 FAILED    AUTH_FAILED   CAPTURE_FAILED
                              │
                              ▼
                          REFUNDED
```

**1. Authorization (Real-time)**
```
1. Merchant calls POST /payments with card details
2. Idempotency check (prevent double-charge)
3. Fraud detection score
4. Risk engine evaluation
5. Route to card network (Visa, MC)
6. Card network → Issuing bank
7. Bank approves/declines
8. Store authorization code
9. Return auth result to merchant
```

**2. Capture (Can be delayed)**
```
1. Merchant calls POST /payments/{id}/capture
2. Validate authorization is still valid (typically 7 days)
3. Send capture request to network
4. Update ledger with actual charge
5. Queue for settlement
```

**3. Settlement (Batch, daily)**
```
1. Aggregate day's captures by merchant
2. Initiate ACH/wire transfers
3. Transfer funds to merchant accounts
4. Generate settlement reports
```

### Idempotency & Double-Spend Prevention

**Critical for payments** - must prevent charging twice.

```python
class PaymentService:
    def create_payment(self, request: PaymentRequest) -> Payment:
        # 1. Check idempotency key (client-provided)
        idempotency_key = request.idempotency_key
        existing = self.cache.get(f"idem:{idempotency_key}")
        if existing:
            return existing  # Return cached result

        # 2. Create payment record with PENDING status
        payment = Payment(
            id=generate_uuid(),
            idempotency_key=idempotency_key,
            amount=request.amount,
            status=PaymentStatus.PENDING,
            created_at=now()
        )

        # 3. Atomic insert (DB unique constraint on idempotency_key)
        try:
            self.db.insert(payment)
        except UniqueConstraintViolation:
            # Another request already processing
            return self.wait_for_result(idempotency_key)

        # 4. Process payment
        result = self.process_payment(payment)

        # 5. Cache result for idempotency
        self.cache.set(f"idem:{idempotency_key}", result, ttl=48h)

        return result
```

**Database Schema for Idempotency:**
```sql
CREATE TABLE payments (
    id UUID PRIMARY KEY,
    idempotency_key VARCHAR(255) UNIQUE NOT NULL,
    merchant_id UUID NOT NULL,
    amount DECIMAL(19,4) NOT NULL,
    currency CHAR(3) NOT NULL,
    status VARCHAR(20) NOT NULL,
    authorization_code VARCHAR(50),
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL,

    INDEX idx_merchant_created (merchant_id, created_at),
    INDEX idx_status (status)
);
```

### Ledger & Double-Entry Bookkeeping

Every transaction creates balanced ledger entries.

```sql
-- Ledger entries (immutable, append-only)
CREATE TABLE ledger_entries (
    id BIGSERIAL PRIMARY KEY,
    transaction_id UUID NOT NULL,
    account_id UUID NOT NULL,
    entry_type ENUM('DEBIT', 'CREDIT') NOT NULL,
    amount DECIMAL(19,4) NOT NULL,
    currency CHAR(3) NOT NULL,
    created_at TIMESTAMP NOT NULL,

    INDEX idx_account_time (account_id, created_at)
);

-- Example: $100 payment from customer to merchant
-- Entry 1: DEBIT customer_liability $100 (what we owe customer)
-- Entry 2: CREDIT merchant_payable $100 (what we owe merchant)
-- Sum of all entries = 0 (balanced)
```

```python
class LedgerService:
    def record_payment(self, payment: Payment):
        entries = [
            LedgerEntry(
                transaction_id=payment.id,
                account_id=payment.customer_account_id,
                entry_type=EntryType.DEBIT,
                amount=payment.amount,
                currency=payment.currency
            ),
            LedgerEntry(
                transaction_id=payment.id,
                account_id=payment.merchant_account_id,
                entry_type=EntryType.CREDIT,
                amount=payment.amount,
                currency=payment.currency
            )
        ]

        # Atomic insert - both or neither
        self.db.insert_batch(entries)
```

### Failure Handling & Retries

**Payment Saga with Compensations:**

```python
class PaymentSaga:
    steps = [
        SagaStep(
            name="fraud_check",
            action=check_fraud,
            compensation=None  # No compensation needed
        ),
        SagaStep(
            name="authorize",
            action=authorize_with_network,
            compensation=void_authorization
        ),
        SagaStep(
            name="record_ledger",
            action=create_ledger_entries,
            compensation=reverse_ledger_entries
        ),
        SagaStep(
            name="notify_merchant",
            action=send_webhook,
            compensation=None  # Best effort
        ),
    ]
```

**Retry Strategy:**
```python
def authorize_with_retry(payment: Payment, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = card_network.authorize(payment)
            if result.success:
                return result
            if result.code in PERMANENT_FAILURES:
                # Declined, insufficient funds - don't retry
                return result
        except NetworkTimeout:
            # Check if authorization went through
            existing = card_network.query_authorization(payment.id)
            if existing:
                return existing

            delay = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)

    return AuthResult(success=False, code="RETRY_EXHAUSTED")
```

### Reconciliation System

Daily process to ensure consistency:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│  Our Ledger     │    │  Bank Statement │    │  Card Network   │
│  Records        │    │  (ACH/Wire)     │    │  Reports        │
└────────┬────────┘    └────────┬────────┘    └────────┬────────┘
         │                      │                      │
         └──────────────────────┼──────────────────────┘
                                ▼
                    ┌───────────────────────┐
                    │  Reconciliation Engine │
                    │  - Match transactions  │
                    │  - Identify gaps       │
                    │  - Flag anomalies      │
                    └───────────────────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
             ┌───────────┐           ┌───────────┐
             │ Matched   │           │ Exceptions│
             │ (Auto)    │           │ (Manual)  │
             └───────────┘           └───────────┘
```

### PCI DSS Compliance

**Key Requirements:**
1. **Tokenization**: Never store raw card numbers
2. **Encryption**: TLS 1.3 everywhere, encrypt at rest
3. **Network segmentation**: Card data in isolated VPC
4. **Access control**: Role-based, audit logs
5. **Vulnerability scanning**: Regular pen tests

```
Tokenization Flow:

Card Number: 4111 1111 1111 1111
                    │
                    ▼
           ┌─────────────────┐
           │  Token Vault    │
           │  (HSM-backed)   │
           └────────┬────────┘
                    │
                    ▼
Token: tok_1234abcd5678efgh  ← Stored in application DB
```

### Fraud Detection

**Multi-Layer Approach:**

```python
class FraudDetector:
    def evaluate(self, payment: Payment) -> FraudScore:
        signals = []

        # Rule-based checks
        signals.append(self.check_velocity(payment))       # Too many txns
        signals.append(self.check_geolocation(payment))    # Impossible travel
        signals.append(self.check_device_fingerprint(payment))
        signals.append(self.check_amount_pattern(payment)) # Unusual amount

        # ML model
        ml_score = self.ml_model.predict(payment.features())
        signals.append(ml_score)

        # Aggregate
        final_score = self.aggregate(signals)

        # Decision
        if final_score > 0.9:
            return FraudScore(action=Action.BLOCK, score=final_score)
        elif final_score > 0.7:
            return FraudScore(action=Action.REVIEW, score=final_score)
        else:
            return FraudScore(action=Action.ALLOW, score=final_score)
```

### Multi-Currency Support

```sql
-- Exchange rates (updated hourly)
CREATE TABLE exchange_rates (
    from_currency CHAR(3),
    to_currency CHAR(3),
    rate DECIMAL(19,8),
    valid_from TIMESTAMP,
    valid_to TIMESTAMP,
    PRIMARY KEY (from_currency, to_currency, valid_from)
);

-- Payment with currency conversion
CREATE TABLE payments (
    -- ...
    original_amount DECIMAL(19,4),
    original_currency CHAR(3),
    settled_amount DECIMAL(19,4),
    settled_currency CHAR(3),
    exchange_rate DECIMAL(19,8),
    -- ...
);
```

### Scaling Considerations

| Component | Strategy |
|-----------|----------|
| API Gateway | Horizontal scaling, geographic distribution |
| Payment DB | Sharding by merchant_id, read replicas |
| Ledger | Append-only, partitioned by date |
| Token Vault | HSM cluster, multi-region |
| Fraud Detection | Pre-computed features, streaming ML |

---

## Otvet (RU)

### Требования

**Функциональные:**
- Обработка платежей кредитными/дебетовыми картами
- Поддержка нескольких валют
- Обработка возвратов и чарджбэков
- Дашборд и API для мерчантов
- Безопасное хранение платёжных методов
- Генерация счетов и чеков
- Поддержка рекуррентных платежей (подписки)

**Нефункциональные:**
- Доступность 99.999% (5 девяток = ~5 мин простоя/год)
- Exactly-once обработка платежей
- Соответствие PCI DSS Level 1
- Латентность авторизации <500мс
- Полный audit trail всех транзакций
- Мульти-региональное disaster recovery

**Оценка масштаба:**
- 1M мерчантов, 100M транзакций/день
- Пик: 10K транзакций/секунду
- $10B+ дневного объёма транзакций

### Поток платежа (Авторизация + Захват)

```
Состояния платежа:

INITIATED → AUTHORIZED → CAPTURED → SETTLED
    │            │            │
    ▼            ▼            ▼
 FAILED    AUTH_FAILED   CAPTURE_FAILED
                              │
                              ▼
                          REFUNDED
```

**1. Авторизация (Real-time)**
```
1. Мерчант вызывает POST /payments с данными карты
2. Проверка идемпотентности (предотвращение двойного списания)
3. Оценка fraud detection
4. Оценка риск-движка
5. Маршрутизация в карточную сеть (Visa, MC)
6. Карточная сеть → Банк-эмитент
7. Банк одобряет/отклоняет
8. Сохранение кода авторизации
9. Возврат результата мерчанту
```

**2. Захват (Может быть отложен)**
```
1. Мерчант вызывает POST /payments/{id}/capture
2. Проверка валидности авторизации (обычно 7 дней)
3. Отправка capture-запроса в сеть
4. Обновление леджера фактическим списанием
5. Постановка в очередь на settlement
```

**3. Расчёт (Batch, ежедневно)**
```
1. Агрегация дневных захватов по мерчантам
2. Инициация ACH/wire переводов
3. Перевод средств на счета мерчантов
4. Генерация отчётов о расчётах
```

### Идемпотентность и предотвращение двойного списания

**Критично для платежей** - нужно предотвратить двойное списание.

```python
class PaymentService:
    def create_payment(self, request: PaymentRequest) -> Payment:
        # 1. Проверка idempotency key (от клиента)
        idempotency_key = request.idempotency_key
        existing = self.cache.get(f"idem:{idempotency_key}")
        if existing:
            return existing  # Возврат закешированного результата

        # 2. Создание записи платежа со статусом PENDING
        payment = Payment(
            id=generate_uuid(),
            idempotency_key=idempotency_key,
            amount=request.amount,
            status=PaymentStatus.PENDING,
            created_at=now()
        )

        # 3. Атомарная вставка (уникальное ограничение БД)
        try:
            self.db.insert(payment)
        except UniqueConstraintViolation:
            # Другой запрос уже обрабатывает
            return self.wait_for_result(idempotency_key)

        # 4. Обработка платежа
        result = self.process_payment(payment)

        # 5. Кеширование результата для идемпотентности
        self.cache.set(f"idem:{idempotency_key}", result, ttl=48h)

        return result
```

### Леджер и двойная бухгалтерия

Каждая транзакция создаёт сбалансированные записи в леджере.

```sql
-- Записи леджера (неизменяемые, только добавление)
CREATE TABLE ledger_entries (
    id BIGSERIAL PRIMARY KEY,
    transaction_id UUID NOT NULL,
    account_id UUID NOT NULL,
    entry_type ENUM('DEBIT', 'CREDIT') NOT NULL,
    amount DECIMAL(19,4) NOT NULL,
    currency CHAR(3) NOT NULL,
    created_at TIMESTAMP NOT NULL
);

-- Пример: платёж $100 от клиента мерчанту
-- Запись 1: DEBIT customer_liability $100 (что мы должны клиенту)
-- Запись 2: CREDIT merchant_payable $100 (что мы должны мерчанту)
-- Сумма всех записей = 0 (сбалансировано)
```

### Обработка сбоев и retry

**Payment Saga с компенсациями:**

```python
class PaymentSaga:
    steps = [
        SagaStep(
            name="fraud_check",
            action=check_fraud,
            compensation=None  # Компенсация не нужна
        ),
        SagaStep(
            name="authorize",
            action=authorize_with_network,
            compensation=void_authorization
        ),
        SagaStep(
            name="record_ledger",
            action=create_ledger_entries,
            compensation=reverse_ledger_entries
        ),
        SagaStep(
            name="notify_merchant",
            action=send_webhook,
            compensation=None  # Best effort
        ),
    ]
```

**Стратегия retry:**
```python
def authorize_with_retry(payment: Payment, max_retries=3):
    for attempt in range(max_retries):
        try:
            result = card_network.authorize(payment)
            if result.success:
                return result
            if result.code in PERMANENT_FAILURES:
                # Отклонено, недостаточно средств - не повторять
                return result
        except NetworkTimeout:
            # Проверить, прошла ли авторизация
            existing = card_network.query_authorization(payment.id)
            if existing:
                return existing

            delay = (2 ** attempt) + random.uniform(0, 1)
            time.sleep(delay)

    return AuthResult(success=False, code="RETRY_EXHAUSTED")
```

### Система реконсиляции

Ежедневный процесс для обеспечения согласованности:

```
1. Сравнение записей леджера с выписками банков
2. Сопоставление с отчётами карточных сетей
3. Автоматическое сопоставление совпадающих транзакций
4. Выделение исключений для ручной проверки
5. Генерация отчётов о расхождениях
```

### Соответствие PCI DSS

**Ключевые требования:**
1. **Токенизация**: Никогда не хранить сырые номера карт
2. **Шифрование**: TLS 1.3 везде, шифрование в покое
3. **Сегментация сети**: Данные карт в изолированном VPC
4. **Контроль доступа**: Ролевой доступ, audit logs
5. **Сканирование уязвимостей**: Регулярные пентесты

```
Поток токенизации:

Номер карты: 4111 1111 1111 1111
                    │
                    ▼
           ┌─────────────────┐
           │  Token Vault    │
           │  (на базе HSM)  │
           └────────┬────────┘
                    │
                    ▼
Токен: tok_1234abcd5678efgh  ← Хранится в БД приложения
```

### Обнаружение мошенничества

**Многоуровневый подход:**

```python
class FraudDetector:
    def evaluate(self, payment: Payment) -> FraudScore:
        signals = []

        # Правила
        signals.append(self.check_velocity(payment))       # Слишком много txn
        signals.append(self.check_geolocation(payment))    # Невозможное перемещение
        signals.append(self.check_device_fingerprint(payment))
        signals.append(self.check_amount_pattern(payment)) # Нетипичная сумма

        # ML модель
        ml_score = self.ml_model.predict(payment.features())
        signals.append(ml_score)

        # Агрегация
        final_score = self.aggregate(signals)

        # Решение
        if final_score > 0.9:
            return FraudScore(action=Action.BLOCK, score=final_score)
        elif final_score > 0.7:
            return FraudScore(action=Action.REVIEW, score=final_score)
        else:
            return FraudScore(action=Action.ALLOW, score=final_score)
```

### Масштабирование

| Компонент | Стратегия |
|-----------|-----------|
| API Gateway | Горизонтальное масштабирование, географическое распределение |
| Payment DB | Шардинг по merchant_id, read replicas |
| Ledger | Append-only, партиционирование по дате |
| Token Vault | HSM кластер, мульти-регион |
| Fraud Detection | Предвычисленные фичи, streaming ML |

---

## Follow-ups

- How do you handle chargebacks and disputes?
- How do you implement subscription billing with prorations?
- How do you route payments across multiple processors for higher approval rates?
- How do you handle cross-border payments and currency hedging?

## Related Questions

### Prerequisites (Easier)
- [[q-idempotency--system-design--medium]] - Idempotency patterns
- [[q-acid-properties--system-design--medium]] - ACID properties

### Related (Same Level)
- [[q-saga-pattern--system-design--hard]] - Distributed transactions
- [[q-two-phase-commit--system-design--hard]] - 2PC pattern
- [[q-design-uber--system-design--hard]] - Similar complexity

### Advanced (Harder)
- [[q-byzantine-fault-tolerance--system-design--hard]] - BFT for critical systems
