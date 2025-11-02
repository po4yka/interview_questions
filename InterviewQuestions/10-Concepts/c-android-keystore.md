---
id: ivc-20251030-143000
title: Android Keystore / Android Keystore
aliases: [Android Keystore, AndroidKeyStore, Keystore System]
kind: concept
summary: Secure hardware-backed key storage system for cryptographic keys
links: []
created: 2025-10-30
updated: 2025-10-30
tags: [android, concept, encryption, keystore, security]
date created: Thursday, October 30th 2025, 12:29:18 pm
date modified: Saturday, November 1st 2025, 5:43:38 pm
---

# Summary (EN)

**Android Keystore** is a secure system for storing and managing cryptographic keys on Android devices. It provides hardware-backed key storage (when available) that makes keys nearly impossible to extract from the device, even with root access. The system allows applications to generate, store, and use cryptographic keys without exposing the key material.

**Core Features**:
- **Hardware-backed security**: Keys stored in Trusted Execution Environment (TEE) or Secure Element
- **Key isolation**: Keys never leave the secure hardware during cryptographic operations
- **Key attestation**: Proof that keys were generated in secure hardware
- **User authentication binding**: Keys can require biometric or device credential authentication
- **StrongBox**: Enhanced security using dedicated security chip (Android 9+)

**Key Types**:
- Symmetric keys (AES, HMAC)
- Asymmetric key pairs (RSA, EC)
- Secret keys for encryption/decryption
- Key pairs for signing/verification

# Сводка (RU)

**Android Keystore** - это защищенная система для хранения и управления криптографическими ключами на Android-устройствах. Она обеспечивает аппаратное хранение ключей (при наличии поддержки), что делает извлечение ключей практически невозможным даже при наличии root-доступа. Система позволяет приложениям генерировать, хранить и использовать криптографические ключи без раскрытия ключевого материала.

**Основные возможности**:
- **Аппаратная защита**: Ключи хранятся в Trusted Execution Environment (TEE) или Secure Element
- **Изоляция ключей**: Ключи никогда не покидают защищенное оборудование во время криптографических операций
- **Аттестация ключей**: Подтверждение того, что ключи были сгенерированы в защищенном оборудовании
- **Привязка к аутентификации**: Ключи могут требовать биометрическую или парольную аутентификацию
- **StrongBox**: Усиленная безопасность с использованием выделенного чипа безопасности (Android 9+)

**Типы ключей**:
- Симметричные ключи (AES, HMAC)
- Асимметричные пары ключей (RSA, EC)
- Секретные ключи для шифрования/дешифрования
- Пары ключей для подписи/верификации

## Use Cases / Trade-offs

**Use Cases**:
- Encrypting sensitive user data (passwords, tokens, PII)
- Securing HTTPS/TLS certificates for network communication
- Biometric authentication (fingerprint, face unlock)
- Digital signatures for data integrity verification
- Payment card tokenization and secure transactions
- App-to-app secure communication

**Trade-offs**:
- **Pro**: Keys cannot be extracted from hardware
- **Pro**: Automatic key rotation and attestation support
- **Pro**: Integration with biometric authentication
- **Con**: Hardware-backed storage not available on all devices (fallback to software)
- **Con**: Keys lost if device is factory reset (unless backed up)
- **Con**: Performance overhead for hardware operations vs in-memory keys

**Hardware-backed vs Software-backed**:
- Hardware-backed: Keys in TEE/Secure Element, stronger security, slower operations
- Software-backed: Keys in Android OS keystore, faster but less secure, extractable with root

## Code Example

```kotlin
import android.security.keystore.KeyGenParameterSpec
import android.security.keystore.KeyProperties
import java.security.KeyStore
import javax.crypto.Cipher
import javax.crypto.KeyGenerator
import javax.crypto.SecretKey

class KeystoreExample {
    private val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
    private val keyAlias = "my_secret_key"

    // Generate AES key in Keystore
    fun generateKey() {
        val keyGenerator = KeyGenerator.getInstance(
            KeyProperties.KEY_ALGORITHM_AES,
            "AndroidKeyStore"
        )

        val keySpec = KeyGenParameterSpec.Builder(
            keyAlias,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_GCM)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_NONE)
            .setUserAuthenticationRequired(true) // Require biometric/PIN
            .setUserAuthenticationValidityDurationSeconds(30)
            .setRandomizedEncryptionRequired(true)
            .build()

        keyGenerator.init(keySpec)
        keyGenerator.generateKey()
    }

    // Encrypt data using Keystore key
    fun encrypt(data: ByteArray): ByteArray {
        val cipher = Cipher.getInstance("AES/GCM/NoPadding")
        val key = keyStore.getKey(keyAlias, null) as SecretKey
        cipher.init(Cipher.ENCRYPT_MODE, key)
        return cipher.doFinal(data)
    }
}
```

## Best Practices

**Security**:
- Always use hardware-backed keys for sensitive operations
- Enable key attestation to verify hardware-backed storage
- Use StrongBox Keymaster when available (Android 9+)
- Bind keys to user authentication for sensitive operations
- Set appropriate key validity periods

**Implementation**:
- Check hardware support: `KeyInfo.isInsideSecureHardware()`
- Handle `UserNotAuthenticatedException` for auth-required keys
- Use appropriate key sizes (AES-256, RSA-2048+, EC-256+)
- Implement proper exception handling for device compatibility
- Test on devices with/without hardware-backed keystore

**Key Management**:
- Use unique aliases for different purposes
- Implement key rotation strategy
- Don't store key aliases in plain text
- Consider key backup strategy for critical data
- Delete keys when no longer needed

## References

- [Android Keystore System Documentation](https://developer.android.com/training/articles/keystore)
- [Key Attestation Guide](https://developer.android.com/training/articles/security-key-attestation)
- [StrongBox Overview](https://developer.android.com/training/articles/keystore#HardwareSecurityModule)
- [Biometric Authentication with Keystore](https://developer.android.com/training/sign-in/biometric-auth)
