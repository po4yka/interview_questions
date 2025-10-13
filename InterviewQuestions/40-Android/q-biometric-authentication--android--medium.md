---
id: 20251012-400003
title: "Biometric Authentication / Биометрическая аутентификация"
slug: biometric-authentication-android-medium
topic: android
subtopics:
  - security
  - biometric
  - authentication
  - fingerprint
  - face-recognition
status: draft
difficulty: medium
moc: moc-android
date_created: 2025-10-12
date_updated: 2025-10-12
related_questions:
  - q-encrypted-shared-preferences--security--medium
  - q-keystore-api--security--hard
  - q-certificate-pinning--security--hard
tags:
  - android
  - security
  - biometric
  - authentication
  - androidx-biometric
---

# Biometric Authentication

## English Version

### Problem Statement

Biometric authentication (fingerprint, face, iris) provides secure and convenient user authentication. The AndroidX Biometric library offers a unified API for implementing biometric authentication across different Android versions and devices.

**The Question:** How do you implement biometric authentication in Android? What are BiometricPrompt, CryptoObject, and different authenticator types? How do you handle fallback authentication?

### Detailed Answer

---

### BIOMETRIC LIBRARY BASICS

**Add dependency:**
```gradle
dependencies {
    implementation "androidx.biometric:biometric:1.2.0-alpha05"
}
```

**Basic implementation:**
```kotlin
class BiometricActivity : ComponentActivity() {
    private lateinit var biometricPrompt: BiometricPrompt
    private lateinit var promptInfo: BiometricPrompt.PromptInfo

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        setupBiometricPrompt()
        setupPromptInfo()
    }

    private fun setupBiometricPrompt() {
        val executor = ContextCompat.getMainExecutor(this)

        biometricPrompt = BiometricPrompt(
            this,
            executor,
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(
                    result: BiometricPrompt.AuthenticationResult
                ) {
                    super.onAuthenticationSucceeded(result)
                    Toast.makeText(
                        this@BiometricActivity,
                        "Authentication succeeded!",
                        Toast.LENGTH_SHORT
                    ).show()
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    super.onAuthenticationError(errorCode, errString)
                    Toast.makeText(
                        this@BiometricActivity,
                        "Authentication error: $errString",
                        Toast.LENGTH_SHORT
                    ).show()
                }

                override fun onAuthenticationFailed() {
                    super.onAuthenticationFailed()
                    Toast.makeText(
                        this@BiometricActivity,
                        "Authentication failed",
                        Toast.LENGTH_SHORT
                    ).show()
                }
            }
        )
    }

    private fun setupPromptInfo() {
        promptInfo = BiometricPrompt.PromptInfo.Builder()
            .setTitle("Biometric Authentication")
            .setSubtitle("Log in using your biometric credential")
            .setNegativeButtonText("Use account password")
            .build()
    }

    fun authenticate() {
        biometricPrompt.authenticate(promptInfo)
    }
}
```

---

### CHECKING BIOMETRIC AVAILABILITY

```kotlin
class BiometricManager(private val context: Context) {
    private val biometricManager = androidx.biometric.BiometricManager.from(context)

    fun canAuthenticate(): BiometricStatus {
        return when (biometricManager.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG)) {
            BiometricManager.BIOMETRIC_SUCCESS ->
                BiometricStatus.Available

            BiometricManager.BIOMETRIC_ERROR_NO_HARDWARE ->
                BiometricStatus.NoHardware

            BiometricManager.BIOMETRIC_ERROR_HW_UNAVAILABLE ->
                BiometricStatus.HardwareUnavailable

            BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED ->
                BiometricStatus.NoneEnrolled

            BiometricManager.BIOMETRIC_ERROR_SECURITY_UPDATE_REQUIRED ->
                BiometricStatus.SecurityUpdateRequired

            BiometricManager.BIOMETRIC_ERROR_UNSUPPORTED ->
                BiometricStatus.Unsupported

            BiometricManager.BIOMETRIC_STATUS_UNKNOWN ->
                BiometricStatus.Unknown

            else -> BiometricStatus.Unknown
        }
    }

    fun canAuthenticateWithDeviceCredential(): Boolean {
        val authenticators = BiometricManager.Authenticators.BIOMETRIC_STRONG or
                BiometricManager.Authenticators.DEVICE_CREDENTIAL

        return biometricManager.canAuthenticate(authenticators) ==
                BiometricManager.BIOMETRIC_SUCCESS
    }
}

sealed class BiometricStatus {
    object Available : BiometricStatus()
    object NoHardware : BiometricStatus()
    object HardwareUnavailable : BiometricStatus()
    object NoneEnrolled : BiometricStatus()
    object SecurityUpdateRequired : BiometricStatus()
    object Unsupported : BiometricStatus()
    object Unknown : BiometricStatus()
}
```

---

### AUTHENTICATOR TYPES

```kotlin
// 1. BIOMETRIC_STRONG
// - Class 3 biometric (highest security)
// - Fingerprint, Face, Iris
// - Can be used with CryptoObject
val strongBiometric = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Strong Biometric")
    .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
    .setNegativeButtonText("Cancel")
    .build()

// 2. BIOMETRIC_WEAK
// - Class 2 biometric
// - Lower security, faster
val weakBiometric = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Weak Biometric")
    .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_WEAK)
    .setNegativeButtonText("Cancel")
    .build()

// 3. DEVICE_CREDENTIAL
// - PIN, Pattern, Password
// - No biometric required
val deviceCredential = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Device Credential")
    .setAllowedAuthenticators(BiometricManager.Authenticators.DEVICE_CREDENTIAL)
    .build()  // No negative button needed

// 4. BIOMETRIC + DEVICE_CREDENTIAL
// - Biometric with fallback to PIN/Pattern/Password
val biometricOrCredential = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Authenticate")
    .setSubtitle("Use biometric or device credential")
    .setAllowedAuthenticators(
        BiometricManager.Authenticators.BIOMETRIC_STRONG or
        BiometricManager.Authenticators.DEVICE_CREDENTIAL
    )
    .build()  // No negative button - fallback is automatic
```

**When to use each:**
```
BIOMETRIC_STRONG:
 Financial transactions
 Accessing encrypted data
 High security requirements
 Use with CryptoObject

BIOMETRIC_WEAK:
 Quick app unlock
 Non-critical operations
 Better availability

DEVICE_CREDENTIAL:
 Fallback option
 When biometric not available
 Wider device support

BIOMETRIC_STRONG | DEVICE_CREDENTIAL:
 Best user experience
 Automatic fallback
 Recommended for most cases
```

---

### CRYPTO-BACKED AUTHENTICATION

**Using CryptoObject for secure authentication:**

```kotlin
class CryptoAuthenticator(private val context: Context) {
    private val keyStore = KeyStore.getInstance("AndroidKeyStore").apply { load(null) }
    private val keyGenerator = KeyGenerator.getInstance(
        KeyProperties.KEY_ALGORITHM_AES,
        "AndroidKeyStore"
    )

    companion object {
        private const val KEY_NAME = "biometric_key"
    }

    // Generate key in Android Keystore
    fun generateSecretKey() {
        val keyGenParameterSpec = KeyGenParameterSpec.Builder(
            KEY_NAME,
            KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT
        )
            .setBlockModes(KeyProperties.BLOCK_MODE_CBC)
            .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_PKCS7)
            .setUserAuthenticationRequired(true)  //  Requires biometric
            .setInvalidatedByBiometricEnrollment(true)  //  Invalidate on new biometric
            .build()

        keyGenerator.init(keyGenParameterSpec)
        keyGenerator.generateKey()
    }

    // Get cipher for encryption
    fun getEncryptCipher(): Cipher {
        val cipher = Cipher.getInstance(
            "${KeyProperties.KEY_ALGORITHM_AES}/" +
            "${KeyProperties.BLOCK_MODE_CBC}/" +
            "${KeyProperties.ENCRYPTION_PADDING_PKCS7}"
        )

        val secretKey = keyStore.getKey(KEY_NAME, null) as SecretKey
        cipher.init(Cipher.ENCRYPT_MODE, secretKey)

        return cipher
    }

    // Get cipher for decryption
    fun getDecryptCipher(iv: ByteArray): Cipher {
        val cipher = Cipher.getInstance(
            "${KeyProperties.KEY_ALGORITHM_AES}/" +
            "${KeyProperties.BLOCK_MODE_CBC}/" +
            "${KeyProperties.ENCRYPTION_PADDING_PKCS7}"
        )

        val secretKey = keyStore.getKey(KEY_NAME, null) as SecretKey
        cipher.init(Cipher.DECRYPT_MODE, secretKey, IvParameterSpec(iv))

        return cipher
    }

    // Authenticate and encrypt data
    fun authenticateAndEncrypt(
        data: String,
        biometricPrompt: BiometricPrompt,
        onSuccess: (ByteArray, ByteArray) -> Unit,
        onError: (String) -> Unit
    ) {
        try {
            val cipher = getEncryptCipher()
            val cryptoObject = BiometricPrompt.CryptoObject(cipher)

            val promptInfo = BiometricPrompt.PromptInfo.Builder()
                .setTitle("Encrypt Data")
                .setSubtitle("Authenticate to encrypt sensitive data")
                .setNegativeButtonText("Cancel")
                .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
                .build()

            biometricPrompt.authenticate(
                promptInfo,
                cryptoObject
            )

            // In callback:
            // val encryptedData = cipher.doFinal(data.toByteArray())
            // val iv = cipher.iv
            // onSuccess(encryptedData, iv)

        } catch (e: Exception) {
            onError(e.message ?: "Unknown error")
        }
    }

    // Authenticate and decrypt data
    fun authenticateAndDecrypt(
        encryptedData: ByteArray,
        iv: ByteArray,
        biometricPrompt: BiometricPrompt,
        onSuccess: (String) -> Unit,
        onError: (String) -> Unit
    ) {
        try {
            val cipher = getDecryptCipher(iv)
            val cryptoObject = BiometricPrompt.CryptoObject(cipher)

            val promptInfo = BiometricPrompt.PromptInfo.Builder()
                .setTitle("Decrypt Data")
                .setSubtitle("Authenticate to access sensitive data")
                .setNegativeButtonText("Cancel")
                .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
                .build()

            biometricPrompt.authenticate(
                promptInfo,
                cryptoObject
            )

            // In callback:
            // val decryptedData = cipher.doFinal(encryptedData)
            // onSuccess(String(decryptedData))

        } catch (e: Exception) {
            onError(e.message ?: "Unknown error")
        }
    }
}
```

---

### COMPLETE EXAMPLE WITH CRYPTO

```kotlin
@Composable
fun BiometricAuthScreen() {
    val context = LocalContext.current
    val activity = context as ComponentActivity

    var authStatus by remember { mutableStateOf("Not authenticated") }
    var encryptedData by remember { mutableStateOf<ByteArray?>(null) }
    var iv by remember { mutableStateOf<ByteArray?>(null) }

    val cryptoAuthenticator = remember { CryptoAuthenticator(context) }

    // Initialize key
    LaunchedEffect(Unit) {
        try {
            cryptoAuthenticator.generateSecretKey()
        } catch (e: Exception) {
            authStatus = "Key generation failed: ${e.message}"
        }
    }

    // Biometric prompt for encryption
    val encryptPrompt = remember {
        BiometricPrompt(
            activity,
            ContextCompat.getMainExecutor(context),
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(
                    result: BiometricPrompt.AuthenticationResult
                ) {
                    result.cryptoObject?.cipher?.let { cipher ->
                        try {
                            val data = "Secret data"
                            encryptedData = cipher.doFinal(data.toByteArray())
                            iv = cipher.iv
                            authStatus = "Data encrypted successfully"
                        } catch (e: Exception) {
                            authStatus = "Encryption failed: ${e.message}"
                        }
                    }
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    authStatus = "Error: $errString"
                }

                override fun onAuthenticationFailed() {
                    authStatus = "Authentication failed"
                }
            }
        )
    }

    // Biometric prompt for decryption
    val decryptPrompt = remember {
        BiometricPrompt(
            activity,
            ContextCompat.getMainExecutor(context),
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(
                    result: BiometricPrompt.AuthenticationResult
                ) {
                    result.cryptoObject?.cipher?.let { cipher ->
                        try {
                            encryptedData?.let { data ->
                                val decrypted = cipher.doFinal(data)
                                authStatus = "Decrypted: ${String(decrypted)}"
                            }
                        } catch (e: Exception) {
                            authStatus = "Decryption failed: ${e.message}"
                        }
                    }
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    authStatus = "Error: $errString"
                }

                override fun onAuthenticationFailed() {
                    authStatus = "Authentication failed"
                }
            }
        )
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(16.dp)
    ) {
        Text(
            text = "Biometric Authentication",
            style = MaterialTheme.typography.headlineMedium
        )

        Text(
            text = authStatus,
            style = MaterialTheme.typography.bodyLarge
        )

        Button(
            onClick = {
                try {
                    val cipher = cryptoAuthenticator.getEncryptCipher()
                    val cryptoObject = BiometricPrompt.CryptoObject(cipher)

                    val promptInfo = BiometricPrompt.PromptInfo.Builder()
                        .setTitle("Encrypt Data")
                        .setSubtitle("Authenticate to encrypt")
                        .setNegativeButtonText("Cancel")
                        .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
                        .build()

                    encryptPrompt.authenticate(promptInfo, cryptoObject)
                } catch (e: Exception) {
                    authStatus = "Error: ${e.message}"
                }
            },
            enabled = encryptedData == null
        ) {
            Text("Encrypt Data")
        }

        Button(
            onClick = {
                try {
                    iv?.let { ivBytes ->
                        val cipher = cryptoAuthenticator.getDecryptCipher(ivBytes)
                        val cryptoObject = BiometricPrompt.CryptoObject(cipher)

                        val promptInfo = BiometricPrompt.PromptInfo.Builder()
                            .setTitle("Decrypt Data")
                            .setSubtitle("Authenticate to decrypt")
                            .setNegativeButtonText("Cancel")
                            .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
                            .build()

                        decryptPrompt.authenticate(promptInfo, cryptoObject)
                    }
                } catch (e: Exception) {
                    authStatus = "Error: ${e.message}"
                }
            },
            enabled = encryptedData != null
        ) {
            Text("Decrypt Data")
        }
    }
}
```

---

### ERROR HANDLING

```kotlin
fun handleBiometricError(errorCode: Int, errString: CharSequence): String {
    return when (errorCode) {
        BiometricPrompt.ERROR_HW_UNAVAILABLE ->
            "Biometric hardware unavailable"

        BiometricPrompt.ERROR_UNABLE_TO_PROCESS ->
            "Unable to process biometric"

        BiometricPrompt.ERROR_TIMEOUT ->
            "Timeout - please try again"

        BiometricPrompt.ERROR_NO_SPACE ->
            "Not enough storage space"

        BiometricPrompt.ERROR_CANCELED ->
            "Authentication canceled"

        BiometricPrompt.ERROR_LOCKOUT ->
            "Too many attempts - locked out"

        BiometricPrompt.ERROR_LOCKOUT_PERMANENT ->
            "Permanently locked - use device credential"

        BiometricPrompt.ERROR_USER_CANCELED ->
            "User canceled authentication"

        BiometricPrompt.ERROR_NO_BIOMETRICS ->
            "No biometric enrolled - please enroll"

        BiometricPrompt.ERROR_HW_NOT_PRESENT ->
            "No biometric hardware"

        BiometricPrompt.ERROR_NEGATIVE_BUTTON ->
            "User pressed negative button"

        BiometricPrompt.ERROR_NO_DEVICE_CREDENTIAL ->
            "No device credential set up"

        BiometricPrompt.ERROR_SECURITY_UPDATE_REQUIRED ->
            "Security update required"

        else -> "Unknown error: $errString"
    }
}
```

---

### VIEWMODEL INTEGRATION

```kotlin
class BiometricViewModel : ViewModel() {
    private val _authState = MutableStateFlow<AuthState>(AuthState.Idle)
    val authState: StateFlow<AuthState> = _authState.asStateFlow()

    fun onAuthenticationSucceeded() {
        _authState.value = AuthState.Success
    }

    fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
        _authState.value = AuthState.Error(errorCode, errString.toString())
    }

    fun onAuthenticationFailed() {
        _authState.value = AuthState.Failed
    }

    fun resetAuth() {
        _authState.value = AuthState.Idle
    }
}

sealed class AuthState {
    object Idle : AuthState()
    object Success : AuthState()
    object Failed : AuthState()
    data class Error(val code: Int, val message: String) : AuthState()
}

@Composable
fun BiometricScreen(viewModel: BiometricViewModel = viewModel()) {
    val authState by viewModel.authState.collectAsState()
    val context = LocalContext.current
    val activity = context as ComponentActivity

    val biometricPrompt = remember {
        BiometricPrompt(
            activity,
            ContextCompat.getMainExecutor(context),
            object : BiometricPrompt.AuthenticationCallback() {
                override fun onAuthenticationSucceeded(
                    result: BiometricPrompt.AuthenticationResult
                ) {
                    viewModel.onAuthenticationSucceeded()
                }

                override fun onAuthenticationError(errorCode: Int, errString: CharSequence) {
                    viewModel.onAuthenticationError(errorCode, errString)
                }

                override fun onAuthenticationFailed() {
                    viewModel.onAuthenticationFailed()
                }
            }
        )
    }

    Column(
        modifier = Modifier
            .fillMaxSize()
            .padding(16.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.Center
    ) {
        when (val state = authState) {
            is AuthState.Idle -> {
                Button(onClick = {
                    val promptInfo = BiometricPrompt.PromptInfo.Builder()
                        .setTitle("Authenticate")
                        .setSubtitle("Log in to your account")
                        .setAllowedAuthenticators(
                            BiometricManager.Authenticators.BIOMETRIC_STRONG or
                            BiometricManager.Authenticators.DEVICE_CREDENTIAL
                        )
                        .build()

                    biometricPrompt.authenticate(promptInfo)
                }) {
                    Text("Authenticate")
                }
            }

            is AuthState.Success -> {
                Text("Authentication successful!", color = Color.Green)
                Button(onClick = { viewModel.resetAuth() }) {
                    Text("Authenticate Again")
                }
            }

            is AuthState.Failed -> {
                Text("Authentication failed", color = Color.Red)
                Button(onClick = { viewModel.resetAuth() }) {
                    Text("Try Again")
                }
            }

            is AuthState.Error -> {
                Text("Error: ${state.message}", color = Color.Red)
                Button(onClick = { viewModel.resetAuth() }) {
                    Text("Try Again")
                }
            }
        }
    }
}
```

---

### BEST PRACTICES

```kotlin
class BiometricBestPractices {
    // 1. Check availability before showing UI
    fun checkAndShowBiometric(context: Context) {
        val biometricManager = BiometricManager.from(context)

        when (biometricManager.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG)) {
            BiometricManager.BIOMETRIC_SUCCESS -> {
                // Show biometric option
            }
            BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED -> {
                // Prompt user to enroll
                val intent = Intent(Settings.ACTION_BIOMETRIC_ENROLL).apply {
                    putExtra(
                        Settings.EXTRA_BIOMETRIC_AUTHENTICATORS_ALLOWED,
                        BiometricManager.Authenticators.BIOMETRIC_STRONG
                    )
                }
                context.startActivity(intent)
            }
            else -> {
                // Fall back to other authentication
            }
        }
    }

    // 2. Use appropriate authenticator strength
    fun getPromptForUseCase(useCase: String): BiometricPrompt.PromptInfo {
        return when (useCase) {
            "payment" -> BiometricPrompt.PromptInfo.Builder()
                .setTitle("Confirm Payment")
                .setSubtitle("Authenticate to complete transaction")
                .setAllowedAuthenticators(BiometricManager.Authenticators.BIOMETRIC_STRONG)
                .setNegativeButtonText("Cancel")
                .build()

            "app_unlock" -> BiometricPrompt.PromptInfo.Builder()
                .setTitle("Unlock App")
                .setAllowedAuthenticators(
                    BiometricManager.Authenticators.BIOMETRIC_WEAK or
                    BiometricManager.Authenticators.DEVICE_CREDENTIAL
                )
                .build()

            else -> throw IllegalArgumentException("Unknown use case")
        }
    }

    // 3. Handle re-authentication after background
    fun shouldReauthenticate(lastAuthTime: Long, timeout: Long = 30_000): Boolean {
        return System.currentTimeMillis() - lastAuthTime > timeout
    }

    // 4. Secure sensitive data
    fun secureUserSession(userId: String, cipher: Cipher): String {
        val encrypted = cipher.doFinal(userId.toByteArray())
        return Base64.encodeToString(encrypted, Base64.NO_WRAP)
    }
}
```

---

## Answer (EN)

### Overview

**Biometric authentication** (fingerprint, face, iris) provides secure and convenient user authentication. The **AndroidX Biometric library** offers a unified API for implementing biometric authentication across different Android versions and devices.

### Key Components

**1. BiometricManager**
- Checks if biometric authentication is available

**2. BiometricPrompt**
- Manages the biometric authentication dialog

**3. CryptoObject**
- Associates biometric authentication with cryptographic operations

### Implementation Steps

**1. Add Dependency**
```gradle
dependencies {
    implementation "androidx.biometric:biometric:1.2.0-alpha05"
}
```

**2. Check Availability**
```kotlin
val biometricManager = BiometricManager.from(this)
when (biometricManager.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG)) {
    BiometricManager.BIOMETRIC_SUCCESS ->
        // App can authenticate with biometrics
    BiometricManager.BIOMETRIC_ERROR_NO_HARDWARE ->
        // No biometric features available
    BiometricManager.BIOMETRIC_ERROR_HW_UNAVAILABLE ->
        // Biometric features are currently unavailable
    BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED ->
        // User hasn't enrolled any biometrics
}
```

**3. Create BiometricPrompt**
```kotlin
val executor = ContextCompat.getMainExecutor(this)
val biometricPrompt = BiometricPrompt(this, executor,
    object : BiometricPrompt.AuthenticationCallback() {
        override fun onAuthenticationSucceeded(
            result: BiometricPrompt.AuthenticationResult) {
            super.onAuthenticationSucceeded(result)
            // Authentication successful
        }

        override fun onAuthenticationError(errorCode: Int, 
            errString: CharSequence) {
            super.onAuthenticationError(errorCode, errString)
            // Authentication error
        }

        override fun onAuthenticationFailed() {
            super.onAuthenticationFailed()
            // Authentication failed
        }
    })
```

**4. Create PromptInfo**
```kotlin
val promptInfo = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Biometric login")
    .setSubtitle("Log in using your biometric credential")
    .setNegativeButtonText("Use account password")
    .build()
```

**5. Authenticate**
```kotlin
biometricPrompt.authenticate(promptInfo)
```

### Crypto-based Authentication

For higher security, use `CryptoObject` to tie authentication to a cryptographic key.

```kotlin
// 1. Generate key
val keyGenerator = KeyGenerator.getInstance(
    KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")

val keyGenParameterSpec = KeyGenParameterSpec.Builder(
    "my_key",
    KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
    .setBlockModes(KeyProperties.BLOCK_MODE_CBC)
    .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_PKCS7)
    .setUserAuthenticationRequired(true)
    .build()

keyGenerator.init(keyGenParameterSpec)
keyGenerator.generateKey()

// 2. Create cipher
val cipher = Cipher.getInstance("AES/CBC/PKCS7Padding")
val secretKey = getSecretKey()
cipher.init(Cipher.ENCRYPT_MODE, secretKey)

// 3. Authenticate with CryptoObject
biometricPrompt.authenticate(
    promptInfo,
    BiometricPrompt.CryptoObject(cipher)
)

// 4. Use cipher after successful authentication
// result.cryptoObject.cipher.doFinal(data)
```

### Best Practices

- **Provide fallback**: Always offer password/PIN as alternative
- **Handle errors**: Inform user about authentication errors
- **Use appropriate strength**: `BIOMETRIC_STRONG` for sensitive data
- **Check availability**: Don't show biometric option if not available
- **Respect user choice**: Allow users to disable biometric login

## Ответ (RU)

### Обзор

**Биометрическая аутентификация** (отпечаток пальца, лицо, радужка) обеспечивает безопасную и удобную аутентификацию пользователя. Библиотека **AndroidX Biometric** предлагает унифицированный API для реализации биометрической аутентификации на разных версиях Android и устройствах.

### Ключевые компоненты

**1. BiometricManager**
- Проверяет доступность биометрической аутентификации

**2. BiometricPrompt**
- Управляет диалогом биометрической аутентификации

**3. CryptoObject**
- Связывает биометрическую аутентификацию с криптографическими операциями

### Шаги реализации

**1. Добавить зависимость**
```gradle
dependencies {
    implementation "androidx.biometric:biometric:1.2.0-alpha05"
}
```

**2. Проверить доступность**
```kotlin
val biometricManager = BiometricManager.from(this)
when (biometricManager.canAuthenticate(BiometricManager.Authenticators.BIOMETRIC_STRONG)) {
    BiometricManager.BIOMETRIC_SUCCESS ->
        // Приложение может аутентифицироваться с помощью биометрии
    BiometricManager.BIOMETRIC_ERROR_NO_HARDWARE ->
        // Нет доступных биометрических функций
    BiometricManager.BIOMETRIC_ERROR_HW_UNAVAILABLE ->
        // Биометрические функции в данный момент недоступны
    BiometricManager.BIOMETRIC_ERROR_NONE_ENROLLED ->
        // Пользователь не зарегистрировал биометрические данные
}
```

**3. Создать BiometricPrompt**
```kotlin
val executor = ContextCompat.getMainExecutor(this)
val biometricPrompt = BiometricPrompt(this, executor,
    object : BiometricPrompt.AuthenticationCallback() {
        override fun onAuthenticationSucceeded(
            result: BiometricPrompt.AuthenticationResult) {
            super.onAuthenticationSucceeded(result)
            // Аутентификация успешна
        }

        override fun onAuthenticationError(errorCode: Int, 
            errString: CharSequence) {
            super.onAuthenticationError(errorCode, errString)
            // Ошибка аутентификации
        }

        override fun onAuthenticationFailed() {
            super.onAuthenticationFailed()
            // Аутентификация не удалась
        }
    })
```

**4. Создать PromptInfo**
```kotlin
val promptInfo = BiometricPrompt.PromptInfo.Builder()
    .setTitle("Биометрический вход")
    .setSubtitle("Войдите, используя ваши биометрические данные")
    .setNegativeButtonText("Использовать пароль")
    .build()
```

**5. Аутентифицировать**
```kotlin
biometricPrompt.authenticate(promptInfo)
```

### Аутентификация с использованием криптографии

Для повышения безопасности используйте `CryptoObject`, чтобы связать аутентификацию с криптографическим ключом.

```kotlin
// 1. Сгенерировать ключ
val keyGenerator = KeyGenerator.getInstance(
    KeyProperties.KEY_ALGORITHM_AES, "AndroidKeyStore")

val keyGenParameterSpec = KeyGenParameterSpec.Builder(
    "my_key",
    KeyProperties.PURPOSE_ENCRYPT or KeyProperties.PURPOSE_DECRYPT)
    .setBlockModes(KeyProperties.BLOCK_MODE_CBC)
    .setEncryptionPaddings(KeyProperties.ENCRYPTION_PADDING_PKCS7)
    .setUserAuthenticationRequired(true)
    .build()

keyGenerator.init(keyGenParameterSpec)
keyGenerator.generateKey()

// 2. Создать шифр
val cipher = Cipher.getInstance("AES/CBC/PKCS7Padding")
val secretKey = getSecretKey()
cipher.init(Cipher.ENCRYPT_MODE, secretKey)

// 3. Аутентифицировать с CryptoObject
biometricPrompt.authenticate(
    promptInfo,
    BiometricPrompt.CryptoObject(cipher)
)

// 4. Использовать шифр после успешной аутентификации
// result.cryptoObject.cipher.doFinal(data)
```

### Лучшие практики

- **Предоставлять запасной вариант**: Всегда предлагайте пароль/PIN в качестве альтернативы
- **Обрабатывать ошибки**: Информируйте пользователя об ошибках аутентификации
- **Использовать соответствующую надежность**: `BIOMETRIC_STRONG` для конфиденциальных данных
- **Проверять доступность**: Не показывайте опцию биометрии, если она недоступна
- **Уважать выбор пользователя**: Позволяйте пользователям отключать биометрический вход

1. **BiometricPrompt** unified API for all biometric types
2. **Check availability** before showing biometric UI
3. **BIOMETRIC_STRONG** for sensitive operations, CryptoObject support
4. **BIOMETRIC | DEVICE_CREDENTIAL** for best UX with automatic fallback
5. **CryptoObject** ties authentication to cryptographic operations
6. **Handle errors** gracefully with proper user messaging
7. **Re-authenticate** after background/timeout for security
8. **Invalidate keys** on biometric enrollment changes
9. **Test on real devices** (emulator support limited)
10. **Provide alternative** authentication methods

---

## Russian Version

### Постановка задачи

Биометрическая аутентификация (отпечаток пальца, лицо, радужная оболочка) обеспечивает безопасную и удобную аутентификацию пользователя. Библиотека AndroidX Biometric предоставляет унифицированный API для реализации биометрической аутентификации на разных версиях Android и устройствах.

**Вопрос:** Как реализовать биометрическую аутентификацию в Android? Что такое BiometricPrompt, CryptoObject и различные типы аутентификаторов? Как обрабатывать резервную аутентификацию?

### Ключевые выводы

1. **BiometricPrompt** унифицированный API для всех типов биометрии
2. **Проверяйте доступность** перед показом биометрического UI
3. **BIOMETRIC_STRONG** для чувствительных операций, поддержка CryptoObject
4. **BIOMETRIC | DEVICE_CREDENTIAL** для лучшего UX с автоматическим fallback
5. **CryptoObject** привязывает аутентификацию к криптографическим операциям
6. **Обрабатывайте ошибки** gracefully с правильными сообщениями пользователю
7. **Повторная аутентификация** после background/timeout для безопасности
8. **Инвалидируйте ключи** при изменении биометрической регистрации
9. **Тестируйте на реальных устройствах** (эмулятор имеет ограничения)
10. **Предоставляйте альтернативные** методы аутентификации

## Follow-ups

1. How does BiometricPrompt work internally?
2. What is the difference between Class 2 and Class 3 biometrics?
3. How do you implement biometric authentication with Jetpack Compose?
4. What are the security implications of BIOMETRIC_WEAK?
5. How do you test biometric authentication?
6. What happens to encrypted data when user enrolls new biometric?
7. How do you implement time-based re-authentication?
8. What is the relationship between BiometricPrompt and KeyStore?
9. How do you handle biometric authentication in multi-user scenarios?
10. What are the privacy considerations for biometric data?