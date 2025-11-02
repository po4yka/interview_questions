---
id: ivm-20251018-140000
title: Security — MOC
kind: moc
created: 2025-10-18
updated: 2025-10-18
tags: [moc, topic/security]
date created: Saturday, October 18th 2025, 2:45:12 pm
date modified: Saturday, November 1st 2025, 5:43:22 pm
---

# Security — Map of Content

## Overview
This MOC covers security topics in software development, with a focus on Android security, cryptography, secure data storage, network security, and security best practices for mobile applications.

## By Difficulty

### Easy
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
WHERE topic = "security" AND difficulty = "easy"
SORT file.name ASC
LIMIT 100
```

### Medium
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
WHERE topic = "security" AND difficulty = "medium"
SORT file.name ASC
LIMIT 100
```

### Hard
```dataview
TABLE file.link AS "Question", subtopics AS "Subtopics", tags AS "Tags"
WHERE topic = "security" AND difficulty = "hard"
SORT file.name ASC
LIMIT 100
```

## By Subtopic

### Android Security Best Practices

**Key Questions** (Curated Learning Path):

#### Security Fundamentals
- [[q-cleartext-traffic-android--android--easy]] - What is cleartext traffic?
- [[q-android-security-best-practices--android--medium]] - Android security overview
- [[q-android-security-practices-checklist--android--medium]] - Security practices checklist
- [[q-app-security-best-practices--android--medium]] - App security best practices
- [[q-data-safety-play-console--android--hard]] - Play Data Safety end-to-end workflow

**All Android Security Questions:**
```dataview
TABLE difficulty, status
WHERE contains(tags, "security") AND topic = "android"
SORT difficulty ASC, file.name ASC
```

### Cryptography & Encryption

**Key Questions**:

#### Keystore & Key Management
- [[q-android-keystore-system--security--medium]] - Android Keystore system
- [[q-data-encryption-at-rest--android--medium]] - Data encryption at rest

#### File & Database Encryption
- [[q-encrypted-file-storage--android--medium]] - Encrypted file storage
- [[q-database-encryption-android--android--medium]] - Database encryption

**All Encryption Questions:**
```dataview
TABLE difficulty, status
WHERE contains(tags, "encryption") OR contains(tags, "keystore") OR contains(file.name, "encrypt")
SORT difficulty ASC, file.name ASC
```

### Network Security

**Key Questions**:

#### HTTPS & TLS
- [[q-cleartext-traffic-android--android--easy]] - Cleartext traffic and HTTPS enforcement
- [[q-certificate-pinning--security--medium]] - Certificate pinning implementation
- [[q-network-security-hardening--android--hard]] - Hardened TLS, pinning, and mTLS strategy

**All Network Security Questions:**
```dataview
TABLE difficulty, status
WHERE (contains(tags, "networking") OR contains(tags, "certificate-pinning") OR contains(tags, "ssl-tls")) AND (topic = "security" OR contains(tags, "security"))
SORT difficulty ASC, file.name ASC
```

### Authentication & Authorization

**Key Questions**:

#### Biometric Authentication
- [[q-biometric-authentication--android--medium]] - Biometric authentication implementation

**All Authentication Questions:**
```dataview
TABLE difficulty, status
WHERE contains(tags, "authentication") OR contains(tags, "biometric") OR contains(file.name, "auth")
SORT difficulty ASC, file.name ASC
```

### Code Protection & Obfuscation

**Key Questions**:

#### ProGuard & R8
- [[q-proguard-r8-rules--security--medium]] - ProGuard/R8 obfuscation and shrinking

**All Code Protection Questions:**
```dataview
TABLE difficulty, status
WHERE contains(tags, "proguard") OR contains(tags, "r8") OR contains(file.name, "obfuscat")
SORT difficulty ASC, file.name ASC
```

### Privacy & Data Protection

**Key Questions**:

#### Privacy APIs & Compliance
- [[q-privacy-sandbox-sdk-runtime--privacy--hard]] - Privacy Sandbox SDK Runtime
- [[q-play-app-signing--android--medium]] - Play App Signing
- [[q-fileprovider-secure-sharing--android--medium]] - FileProvider secure file sharing
- [[q-sensitive-data-lifecycle--android--hard]] - Managing sensitive data lifecycle

**All Privacy Questions:**
```dataview
TABLE difficulty, status
WHERE contains(tags, "privacy") OR contains(file.name, "privacy")
SORT difficulty ASC, file.name ASC
```

## All Security Questions

```dataview
TABLE difficulty, subtopics, status, tags
WHERE topic = "security" OR contains(tags, "security")
SORT difficulty ASC, file.name ASC
```

## Statistics

```dataview
TABLE length(rows) as "Count"
WHERE topic = "security" OR contains(tags, "security")
GROUP BY difficulty
SORT difficulty ASC
```

## Related MOCs
- [[moc-android]]
- [[moc-backend]]
- [[moc-cs]]

## Security Topics Covered

### Authentication & Authorization
- Biometric authentication (fingerprint, face, iris)
- Android Keystore integration
- User authentication patterns
- Session management

### Cryptography
- Android Keystore system
- AES encryption/decryption
- RSA key pairs
- Key generation and storage
- Cipher operations

### Data Protection
- Encryption at rest
- Encrypted file storage
- Database encryption
- Secure SharedPreferences
- Key attestation

### Network Security
- HTTPS enforcement
- Certificate pinning (OkHttp, NetworkSecurityConfig)
- TLS/SSL configuration
- Cleartext traffic policies
- Certificate rotation handling

### Code Protection
- ProGuard/R8 obfuscation
- Code shrinking
- Resource optimization
- Reverse engineering protection

### Privacy
- Privacy Sandbox
- SDK Runtime
- Data minimization
- Privacy-preserving APIs
- FileProvider secure sharing
- Play App Signing

### Security Best Practices
- Security checklists
- Threat modeling
- Vulnerability assessment
- Secure coding guidelines
- Security testing

## Security Guidelines Summary

### CRITICAL - Always Use
1. HTTPS everywhere (no cleartext traffic in production)
2. Android Keystore for key storage
3. Certificate pinning for sensitive APIs
4. Biometric authentication for sensitive operations
5. Encryption for sensitive data at rest
6. ProGuard/R8 for code obfuscation

### RECOMMENDED - Best Practices
1. Network Security Configuration for granular control
2. Key attestation for critical apps
3. Regular security audits
4. Secure file sharing with FileProvider
5. Privacy Sandbox APIs for user privacy
6. Play App Signing for secure key management

### AVOID - Security Risks
1. Cleartext traffic (HTTP) in production
2. Hardcoded secrets in code
3. Storing sensitive data in plain text
4. Ignoring certificate validation
5. Using weak encryption algorithms
6. Disabling security features for convenience

## Common Security Vulnerabilities

### Network Layer
- Man-in-the-middle attacks (MITM)
- Certificate validation bypass
- Insecure protocols (HTTP, FTP)
- DNS spoofing
- SSL stripping

### Data Storage
- Unencrypted sensitive data
- Insecure SharedPreferences
- World-readable files
- SQL injection
- Path traversal

### Authentication
- Weak password policies
- Broken session management
- Insufficient authentication
- Credential storage in plain text
- Missing re-authentication

### Code Security
- Reverse engineering
- Code injection
- Binary patching
- Tampering detection bypass
- Debug information leakage

## Security Testing Approaches

### Static Analysis
- Code review
- ProGuard/R8 configuration validation
- Dependency vulnerability scanning
- Secrets detection
- Lint security checks

### Dynamic Analysis
- Penetration testing
- Man-in-the-middle testing (Charles Proxy)
- Biometric bypass attempts
- Root detection testing
- Runtime manipulation testing

### Compliance Testing
- OWASP Mobile Top 10
- Privacy compliance (GDPR, CCPA)
- Data protection regulations
- Industry standards (PCI DSS for payments)
- Security certifications

## Tools & Libraries

### Android Security
- AndroidX Biometric
- Android Keystore
- SafetyNet / Play Integrity API
- EncryptedSharedPreferences
- EncryptedFile

### Network Security
- OkHttp CertificatePinner
- NetworkSecurityConfig
- Conscrypt (BoringSSL)
- Certificate Transparency

### Testing & Analysis
- OWASP ZAP
- Burp Suite
- Frida
- Objection
- MobSF (Mobile Security Framework)

### Code Protection
- ProGuard
- R8
- DexGuard (commercial)

---

**Last Updated**: 2025-10-18
**Status**: Draft
**Total Security Questions**: See statistics query above
