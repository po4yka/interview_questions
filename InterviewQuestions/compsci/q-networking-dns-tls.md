---
id: cs-net-dns-tls
title: Networking - DNS and TLS
topic: networking
difficulty: medium
tags:
- cs_networking
- dns
- security
anki_cards:
- slug: cs-net-dns-0-en
  language: en
  anki_id: 1769160674324
  synced_at: '2026-01-23T13:31:18.813208'
- slug: cs-net-dns-0-ru
  language: ru
  anki_id: 1769160674350
  synced_at: '2026-01-23T13:31:18.815025'
- slug: cs-net-dns-1-en
  language: en
  anki_id: 1769160674374
  synced_at: '2026-01-23T13:31:18.817231'
- slug: cs-net-dns-1-ru
  language: ru
  anki_id: 1769160674399
  synced_at: '2026-01-23T13:31:18.818851'
---
# DNS and TLS

## DNS (Domain Name System)

**Purpose**: Translate domain names to IP addresses.

### DNS Hierarchy

```
                    . (root)
                   /|\
                  / | \
               com org net ...
              / |    |
         google amazon ...
            |
          www
```

### DNS Resolution Process

```
1. Browser cache
2. OS cache
3. Resolver (ISP/configured)
4. Root nameserver
5. TLD nameserver (.com)
6. Authoritative nameserver
7. Return IP to client
```

**Recursive query**: Resolver does all work.
**Iterative query**: Resolver gets referrals.

### DNS Record Types

| Type | Purpose | Example |
|------|---------|---------|
| A | IPv4 address | example.com -> 93.184.216.34 |
| AAAA | IPv6 address | example.com -> 2606:2800:... |
| CNAME | Canonical name (alias) | www.example.com -> example.com |
| MX | Mail exchange | example.com -> mail.example.com |
| NS | Nameserver | example.com -> ns1.example.com |
| TXT | Text record | SPF, DKIM, verification |
| SOA | Start of authority | Zone admin info |
| PTR | Reverse lookup | IP -> domain |
| SRV | Service location | _sip._tcp.example.com |
| CAA | Certificate authority | Allowed CAs |

### DNS Query

```
Query:
  Name: www.example.com
  Type: A
  Class: IN (Internet)

Response:
  www.example.com  300  IN  A  93.184.216.34
                   ^TTL     ^Type
```

### DNS Caching

**TTL (Time to Live)**: How long to cache response.

```
Caching layers:
1. Browser DNS cache
2. OS DNS cache
3. Resolver cache
4. Authoritative server cache
```

### DNS Security Issues

**DNS spoofing**: Attacker provides fake DNS response.
**DNS hijacking**: Redirect queries to malicious server.
**DNS amplification**: DDoS using DNS reflection.

### DNSSEC

Adds cryptographic signatures to DNS records.

```
DNS Record + Digital Signature = Verified Origin
```

**Records**:
- RRSIG: Signature of record set
- DNSKEY: Public key
- DS: Delegation signer (chain of trust)

## TLS (Transport Layer Security)

**Purpose**: Encryption, authentication, integrity for network communication.

### TLS Goals

1. **Confidentiality**: Data encrypted
2. **Integrity**: Detect tampering
3. **Authentication**: Verify server (and optionally client)

### TLS Handshake (TLS 1.2)

```
Client                              Server
   |                                   |
   |---- ClientHello ----------------->|
   |     (versions, cipher suites,     |
   |      random, extensions)          |
   |                                   |
   |<--- ServerHello -----------------|
   |     (chosen cipher, random)       |
   |<--- Certificate -----------------|
   |     (server's X.509 cert)         |
   |<--- ServerKeyExchange -----------|
   |     (DH params if needed)         |
   |<--- ServerHelloDone -------------|
   |                                   |
   |---- ClientKeyExchange ----------->|
   |     (encrypted pre-master secret) |
   |---- ChangeCipherSpec ------------>|
   |---- Finished -------------------->|
   |                                   |
   |<--- ChangeCipherSpec ------------|
   |<--- Finished --------------------|
   |                                   |
   |    [Application Data]             |
```

### TLS 1.3 (Faster)

**1-RTT handshake**:
```
Client                              Server
   |                                   |
   |---- ClientHello + KeyShare ------>|
   |                                   |
   |<--- ServerHello + KeyShare -------|
   |<--- {EncryptedExtensions} --------|
   |<--- {Certificate} ---------------|
   |<--- {CertificateVerify} ---------|
   |<--- {Finished} ------------------|
   |                                   |
   |---- {Finished} ------------------>|
   |                                   |
   |    [Application Data]             |
```

**0-RTT resumption**: Send data with first message using cached keys.

### Certificate Chain

```
Root CA (trusted, in browser/OS)
    |
    v
Intermediate CA (signed by root)
    |
    v
Server Certificate (signed by intermediate)
```

**Verification**:
1. Check certificate not expired
2. Verify signature chain up to trusted root
3. Check hostname matches certificate
4. Check revocation (CRL or OCSP)

### Cipher Suites

```
TLS_ECDHE_RSA_WITH_AES_256_GCM_SHA384
    ^      ^           ^        ^
    |      |           |        |
Key exchange  Auth   Encryption  MAC
```

**Modern recommended**: ECDHE + ECDSA/RSA + AES-GCM + SHA-256/384

### Perfect Forward Secrecy (PFS)

**Problem**: If long-term key is compromised, all past traffic can be decrypted.

**Solution**: Ephemeral keys (ECDHE, DHE).
- New key pair for each session
- Compromise of long-term key doesn't affect past sessions

### Certificate Types

| Type | Validation | Trust |
|------|------------|-------|
| DV (Domain) | Domain control only | Low |
| OV (Organization) | Business verification | Medium |
| EV (Extended) | Extensive verification | High |

### Common Issues

**Certificate errors**:
- Expired certificate
- Hostname mismatch
- Self-signed (not trusted)
- Incomplete chain

**Mixed content**: HTTPS page loading HTTP resources.

## mTLS (Mutual TLS)

Both client and server present certificates.

**Use cases**:
- Service-to-service authentication
- API security
- Zero trust networks

```
Normal TLS:  Server proves identity
mTLS:        Both client and server prove identity
```

## Certificate Pinning

Pin expected certificate/public key in application.

**Benefits**: Prevents MITM even with compromised CA.
**Drawbacks**: Hard to rotate, can lock out users.

## HSTS (HTTP Strict Transport Security)

Force browsers to use HTTPS.

```
Strict-Transport-Security: max-age=31536000; includeSubDomains; preload
```

**Preload list**: Browsers ship with list of HSTS sites.

## Interview Questions

1. **How does DNS work?**
   - Recursive resolution through hierarchy
   - Caching at multiple levels
   - Returns IP address for domain

2. **What prevents MITM attacks in TLS?**
   - Certificate verification (signed by trusted CA)
   - Hostname validation
   - Certificate pinning (optional)

3. **Why use TLS 1.3 over 1.2?**
   - Faster (1-RTT vs 2-RTT)
   - Removed weak ciphers
   - Mandatory PFS
   - 0-RTT resumption

4. **What is certificate chain?**
   - Root CA (trusted by OS/browser)
   - Intermediate CA (signed by root)
   - End certificate (signed by intermediate)
   - Each verifies next level
