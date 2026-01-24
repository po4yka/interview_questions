---
id: cs-sec-crypto
title: Security - Cryptography Fundamentals
topic: security
difficulty: hard
tags:
- cs_security
- cryptography
anki_cards:
- slug: cs-sec-crypto-0-en
  language: en
  anki_id: 1769160675725
  synced_at: '2026-01-23T13:31:18.889882'
- slug: cs-sec-crypto-0-ru
  language: ru
  anki_id: 1769160675750
  synced_at: '2026-01-23T13:31:18.891134'
- slug: cs-sec-crypto-1-en
  language: en
  anki_id: 1769160675774
  synced_at: '2026-01-23T13:31:18.893396'
- slug: cs-sec-crypto-1-ru
  language: ru
  anki_id: 1769160675799
  synced_at: '2026-01-23T13:31:18.894724'
---
# Cryptography Fundamentals

## Symmetric Encryption

Same key for encryption and decryption.

**Fast, used for bulk data.**

### AES (Advanced Encryption Standard)

Block cipher, industry standard.

**Key sizes**: 128, 192, or 256 bits.
**Block size**: 128 bits.

**Modes of operation**:

| Mode | Description | Use Case |
|------|-------------|----------|
| ECB | Each block independent | Never use (patterns visible) |
| CBC | Chain blocks with XOR | Legacy, needs IV |
| CTR | Counter mode, parallelizable | Disk encryption |
| GCM | Galois/Counter Mode, authenticated | TLS, recommended |

```python
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
import os

key = os.urandom(32)  # 256-bit key
iv = os.urandom(12)   # 96-bit IV for GCM

cipher = Cipher(algorithms.AES(key), modes.GCM(iv))
encryptor = cipher.encryptor()
ciphertext = encryptor.update(plaintext) + encryptor.finalize()
tag = encryptor.tag  # Authentication tag
```

### ChaCha20

Stream cipher, alternative to AES.

**Advantages**: Fast in software, no timing attacks.
**Used in**: TLS 1.3, WireGuard.

## Asymmetric Encryption

Different keys for encryption (public) and decryption (private).

**Slow, used for key exchange and signatures.**

### RSA

Based on factoring large primes.

**Key sizes**: 2048, 3072, 4096 bits.

```
Key generation:
1. Choose two large primes p, q
2. n = p * q
3. phi(n) = (p-1)(q-1)
4. Choose e (commonly 65537)
5. d = e^(-1) mod phi(n)

Public key: (n, e)
Private key: (n, d)

Encrypt: c = m^e mod n
Decrypt: m = c^d mod n
```

**Use cases**: Key exchange, digital signatures.

### Elliptic Curve Cryptography (ECC)

Based on elliptic curve discrete logarithm problem.

**Advantages**: Smaller keys, faster operations.
- 256-bit ECC ~ 3072-bit RSA

**Common curves**: P-256, P-384, Curve25519.

### Diffie-Hellman Key Exchange

Establish shared secret over insecure channel.

```
Alice                           Bob
  |                              |
  | g, p (public parameters)     |
  |----------------------------->|
  |                              |
  | a = random                   | b = random
  | A = g^a mod p               | B = g^b mod p
  |                              |
  |<---------- B ----------------|
  |----------- A --------------->|
  |                              |
  | secret = B^a mod p          | secret = A^b mod p
  | = g^(ab) mod p              | = g^(ab) mod p
  |                              |
  |    Both have same secret!    |
```

**ECDH**: Elliptic curve version, more efficient.

## Hashing

One-way function producing fixed-size output.

**Properties**:
- Deterministic
- Fast to compute
- Infeasible to reverse
- Small change = completely different hash
- Collision resistant

### Hash Algorithms

| Algorithm | Output | Status |
|-----------|--------|--------|
| MD5 | 128 bits | Broken, don't use |
| SHA-1 | 160 bits | Deprecated |
| SHA-256 | 256 bits | Secure, widely used |
| SHA-384/512 | 384/512 bits | Secure |
| SHA-3 | Variable | Secure, different design |
| BLAKE2 | Variable | Fast, secure |

### Password Hashing

Use slow, memory-hard functions with salt.

| Function | Description |
|----------|-------------|
| bcrypt | Adaptive, widely supported |
| scrypt | Memory-hard |
| Argon2 | Winner of PHC, recommended |

```python
import bcrypt

# Hash password
password = b"secret"
salt = bcrypt.gensalt(rounds=12)  # Work factor
hashed = bcrypt.hashpw(password, salt)

# Verify
bcrypt.checkpw(password, hashed)  # Returns True/False
```

### Salt

Random data added before hashing.

**Prevents**:
- Rainbow table attacks
- Identical passwords having same hash

```
Without salt:
  "password" -> hash1
  "password" -> hash1  (same!)

With salt:
  "password" + salt1 -> hash1
  "password" + salt2 -> hash2  (different!)
```

## Message Authentication Code (MAC)

Verify message integrity and authenticity.

### HMAC

Hash-based MAC.

```python
import hmac
import hashlib

key = b"secret_key"
message = b"message"

# Create MAC
mac = hmac.new(key, message, hashlib.sha256).digest()

# Verify
hmac.compare_digest(mac, received_mac)  # Timing-safe comparison
```

## Digital Signatures

Prove message came from specific sender.

**Process**:
```
Signing:
1. Hash the message
2. Encrypt hash with private key = signature

Verification:
1. Decrypt signature with public key
2. Hash the message
3. Compare hashes
```

### Algorithms

- **RSA Signatures**: Sign with private key
- **ECDSA**: Elliptic curve signatures (Bitcoin)
- **Ed25519**: Modern, fast (SSH, Signal)

## Key Derivation Functions (KDF)

Derive keys from passwords or other keys.

| Function | Use Case |
|----------|----------|
| PBKDF2 | Password to key |
| HKDF | Key to multiple keys |
| Argon2 | Password hashing/key derivation |

```python
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

kdf = PBKDF2HMAC(
    algorithm=hashes.SHA256(),
    length=32,
    salt=salt,
    iterations=100000,
)
key = kdf.derive(password)
```

## Cryptographic Best Practices

1. **Don't roll your own crypto**: Use established libraries
2. **Use authenticated encryption**: GCM, ChaCha20-Poly1305
3. **Generate random keys properly**: Use cryptographic RNG
4. **Use constant-time comparisons**: Prevent timing attacks
5. **Rotate keys**: Limit exposure from compromise
6. **Use appropriate key sizes**: 256-bit symmetric, 2048+ RSA

## Common Vulnerabilities

| Vulnerability | Description | Prevention |
|---------------|-------------|------------|
| Weak keys | Predictable or short | Use crypto RNG, proper size |
| ECB mode | Patterns visible | Use GCM or CTR |
| No authentication | Malleable ciphertext | Use AEAD |
| Timing attacks | Time reveals info | Constant-time operations |
| Key reuse | Same key + IV = broken | Unique IV per message |

## Interview Questions

1. **Symmetric vs asymmetric encryption?**
   - Symmetric: Same key, fast, for bulk data
   - Asymmetric: Key pair, slow, for key exchange/signatures

2. **Why salt passwords?**
   - Prevents rainbow tables
   - Same password has different hash
   - Salt must be unique per password

3. **What is authenticated encryption?**
   - Encryption + integrity check
   - Detects tampering
   - Examples: AES-GCM, ChaCha20-Poly1305

4. **How does HTTPS use cryptography?**
   - Asymmetric (RSA/ECDH) for key exchange
   - Symmetric (AES) for data encryption
   - Certificates for server authentication
   - MAC for integrity
