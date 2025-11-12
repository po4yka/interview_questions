---
id: android-019
title: How to implement Voice/Video Call in Android? / Как реализовать голосовой/видеозвонок в Android?
aliases:
- Voice Video Call Android
- WebRTC Android
- Голосовой видеозвонок Android
topic: android
subtopics:
- media
- networking-http
- websockets
question_kind: coding
difficulty: hard
original_language: en
language_tags:
- en
- ru
sources:
- "https://github.com/amitshekhariitbhu/android-interview-questions"
status: draft
moc: moc-android
related:
- q-http-protocols-comparison--android--medium
- q-parallel-network-calls-coroutines--kotlin--medium
created: 2025-10-06
updated: 2025-10-31
tags:
- android/media
- android/networking-http
- android/websockets
- difficulty/hard
---

# Вопрос (RU)
> Как бы вы реализовали функции голосовых и видеозвонков в Android приложении?

# Question (EN)
> How would you implement voice and video calling features in an Android application?

---

## Ответ (RU)

**Подход**: Использование WebRTC для peer-to-peer аудио/видео связи с низкой задержкой (при необходимости с ретрансляцией через TURN). WebRTC требует:
- сигнального канала (обычно WebSocket/HTTP),
- STUN/TURN серверов для обхода NAT,
- корректной интеграции с Android-аудио/жизненным циклом.

**Ключевые компоненты**:
- **PeerConnection** — управление P2P соединением и медиа-треками
- **MediaStream/MediaTracks** — обработка аудио/видео (в современном API упор на треки)
- **ICE/STUN/TURN** — проход через NAT/файрволы
- **Signaling Server** — обмен SDP и ICE-кандидатами (обычно WebSocket, с идентификацией пиров)

**Архитектура**:
```
Устройство А                    Устройство Б
    ↓                                ↓
Signaling Server ← WebSocket → Offer/Answer/ICE
    ↓                                ↓
Media P2P (WebRTC) ←──────────→ Audio/Video Stream
    ↓
STUN/TURN Server (NAT traversal)
```

### Основная Реализация

(Упрощённый пример, фокус на идее сигнального обмена и WebRTC, а не на полном продакшн-коде.)

**Менеджер WebRTC**:
```kotlin
class WebRTCManager(
    private val context: Context,
    private val signalingClient: SignalingClient,
    private val peerConnectionFactory: PeerConnectionFactory,
    private val eglBase: EglBase
) {
    private var peerConnection: PeerConnection? = null
    private var localVideoTrack: VideoTrack? = null
    private var localAudioTrack: AudioTrack? = null
    private var videoCapturer: VideoCapturer? = null

    private val _callState = MutableStateFlow(CallState())
    val callState = _callState.asStateFlow()

    fun startCall(isVideoCall: Boolean, remotePeerId: String) {
        createPeerConnection(remotePeerId)
        createMediaTracks(isVideoCall)

        val constraints = MediaConstraints()
        peerConnection?.createOffer(object : SdpObserver {
            override fun onCreateSuccess(sdp: SessionDescription) {
                // Устанавливаем локальное SDP и отправляем через signaling
                peerConnection?.setLocalDescription(object : SdpObserver {
                    override fun onSetSuccess() {
                        signalingClient.sendOffer(remotePeerId, sdp)
                    }
                    override fun onSetFailure(p0: String?) {}
                    override fun onCreateSuccess(p0: SessionDescription?) {}
                    override fun onCreateFailure(p0: String?) {}
                }, sdp)
            }
            override fun onSetSuccess() {}
            override fun onCreateFailure(error: String?) {}
            override fun onSetFailure(error: String?) {}
        }, constraints)
    }

    private fun createPeerConnection(remotePeerId: String) {
        val iceServers = listOf(
            // STUN для определения публичного IP
            PeerConnection.IceServer.builder("stun:stun.l.google.com:19302").createIceServer(),
            // TURN для прохода через строгие NAT (обязателен для продакшена)
            PeerConnection.IceServer.builder("turn:your-turn-server.com:3478")
                .setUsername("username")
                .setPassword("password")
                .createIceServer()
        )

        val rtcConfig = PeerConnection.RTCConfiguration(iceServers).apply {
            sdpSemantics = PeerConnection.SdpSemantics.UNIFIED_PLAN
        }

        peerConnection = peerConnectionFactory.createPeerConnection(
            rtcConfig,
            object : PeerConnection.Observer {
                override fun onIceCandidate(candidate: IceCandidate) {
                    // Отправка кандидата удалённому пиру (упрощённо)
                    signalingClient.sendIceCandidate(remotePeerId, candidate)
                }
                override fun onIceConnectionChange(newState: PeerConnection.IceConnectionState) {
                    when (newState) {
                        PeerConnection.IceConnectionState.CONNECTED ->
                            _callState.value = _callState.value.copy(isConnected = true)

                        PeerConnection.IceConnectionState.FAILED,
                        PeerConnection.IceConnectionState.DISCONNECTED -> {
                            _callState.value = _callState.value.copy(isConnected = false)
                            endCall()
                        }

                        else -> Unit
                    }
                }
                override fun onTrack(transceiver: RtpTransceiver?) {
                    // Здесь получаем remoteVideoTrack/remoteAudioTrack из transceiver.receiver.track
                    // и пробрасываем их в UI-слой
                }
                // Остальные методы опущены для краткости
            }
        )
    }

    private fun createMediaTracks(isVideoCall: Boolean) {
        // Аудио трек (всегда)
        val audioSource = peerConnectionFactory.createAudioSource(MediaConstraints())
        localAudioTrack = peerConnectionFactory.createAudioTrack("audio", audioSource)
        localAudioTrack?.setEnabled(true)
        peerConnection?.addTrack(localAudioTrack)

        // Видео трек (опционально)
        if (isVideoCall) {
            videoCapturer = createVideoCapturer() // реализация зависит от требований (Camera1/2); опущено
            val videoSource = peerConnectionFactory.createVideoSource(false)
            videoCapturer?.initialize(
                SurfaceTextureHelper.create("CaptureThread", eglBase.eglBaseContext),
                context,
                videoSource.capturerObserver
            )
            videoCapturer?.startCapture(1280, 720, 30)

            localVideoTrack = peerConnectionFactory.createVideoTrack("video", videoSource)
            localVideoTrack?.setEnabled(true)
            peerConnection?.addTrack(localVideoTrack)
        }
    }

    fun toggleMute() {
        val muted = !_callState.value.isMuted
        localAudioTrack?.setEnabled(!muted)
        _callState.value = _callState.value.copy(isMuted = muted)
    }

    fun toggleVideo() {
        val enabled = !_callState.value.isVideoEnabled
        _callState.value = _callState.value.copy(isVideoEnabled = enabled)
        localVideoTrack?.setEnabled(enabled)
    }

    fun endCall() {
        videoCapturer?.run {
            try { stopCapture() } catch (_: Exception) {}
            dispose()
        }
        videoCapturer = null

        localVideoTrack?.dispose()
        localVideoTrack = null

        localAudioTrack?.dispose()
        localAudioTrack = null

        peerConnection?.close()
        peerConnection = null

        _callState.value = CallState()
    }
}
```

**Signaling через WebSocket** (упрощённо; структура сообщений зависит от сервера):
```kotlin
class SignalingClient(
    private val okHttpClient: OkHttpClient,
    private val json: Json,
    private val scope: CoroutineScope
) {
    private var webSocket: WebSocket? = null
    private val _messages = MutableSharedFlow<SignalingMessage>()
    val messages = _messages.asSharedFlow()

    fun connect(userId: String) {
        val request = Request.Builder()
            .url("wss://your-server.com/ws?userId=$userId")
            .build()

        webSocket = okHttpClient.newWebSocket(request, object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                val message = json.decodeFromString<SignalingMessage>(text)
                scope.launch { _messages.emit(message) }
            }
        })
    }

    fun sendOffer(remotePeerId: String, sdp: SessionDescription) {
        val msg = SignalingMessage.Offer(to = remotePeerId, sdp = sdp.description)
        send(msg)
    }

    fun sendAnswer(remotePeerId: String, sdp: SessionDescription) {
        val msg = SignalingMessage.Answer(to = remotePeerId, sdp = sdp.description)
        send(msg)
    }

    fun sendIceCandidate(remotePeerId: String, candidate: IceCandidate) {
        val msg = SignalingMessage.IceCandidate(
            to = remotePeerId,
            sdpMid = candidate.sdpMid ?: "",
            sdpMLineIndex = candidate.sdpMLineIndex,
            sdp = candidate.sdp
        )
        send(msg)
    }

    private fun send(message: SignalingMessage) {
        val jsonText = json.encodeToString(SignalingMessage.serializer(), message)
        webSocket?.send(jsonText)
    }
}

@Serializable
sealed class SignalingMessage {
    @Serializable
    data class Offer(val to: String, val sdp: String) : SignalingMessage()

    @Serializable
    data class Answer(val to: String, val sdp: String) : SignalingMessage()

    @Serializable
    data class IceCandidate(
        val to: String,
        val sdpMid: String,
        val sdpMLineIndex: Int,
        val sdp: String
    ) : SignalingMessage()
}
```

**UI (Jetpack Compose)** (идея подключения SurfaceViewRenderer к VideoTrack):
```kotlin
@Composable
fun VideoCallScreen(viewModel: CallViewModel) {
    val callState by viewModel.callState.collectAsState()
    val localVideo by viewModel.localVideoTrack.collectAsState()
    val remoteVideo by viewModel.remoteVideoTrack.collectAsState()

    Box(modifier = Modifier.fillMaxSize()) {
        // Удалённое видео (полный экран)
        remoteVideo?.let { track ->
            AndroidView(
                factory = { context ->
                    SurfaceViewRenderer(context).apply {
                        init(viewModel.eglBase.eglBaseContext, null)
                        track.addSink(this)
                    }
                },
                modifier = Modifier.fillMaxSize()
            )
        }

        // Локальное видео (PiP)
        localVideo?.let { track ->
            AndroidView(
                factory = { context ->
                    SurfaceViewRenderer(context).apply {
                        init(viewModel.eglBase.eglBaseContext, null)
                        setZOrderMediaOverlay(true)
                        track.addSink(this)
                    }
                },
                modifier = Modifier
                    .size(120.dp, 160.dp)
                    .align(Alignment.TopEnd)
                    .padding(16.dp)
            )
        }

        // Элементы управления
        Row(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(32.dp)
        ) {
            CallButton(
                icon = if (callState.isMuted) Icons.Default.MicOff else Icons.Default.Mic,
                isActive = callState.isMuted,
                onClick = { viewModel.toggleMute() }
            )

            CallButton(
                icon = Icons.Default.CallEnd,
                isActive = true,
                onClick = { viewModel.endCall() }
            )

            CallButton(
                icon = if (callState.isVideoEnabled) Icons.Default.Videocam
                       else Icons.Default.VideocamOff,
                isActive = !callState.isVideoEnabled,
                onClick = { viewModel.toggleVideo() }
            )
        }
    }
}
```

### Лучшие Практики

**1. Серверная инфраструктура**:
- STUN серверы для определения публичного IP
- TURN серверы для прохода через строгие NAT (критично для реальных условий)
- Signaling сервер для обмена SDP и ICE-кандидатами (WebSocket/HTTP + аутентификация и адресация получателей)

**2. Управление ресурсами и интеграция с Android**:
- Остановка/приостановка видео при переходе в фон (или по требованиям продукта)
- Корректное освобождение треков, источников, capturer и PeerConnection
- Управление audio focus и режимами через AudioManager / AudioAttributes / AudioFocusRequest
- Использование foreground service + постоянного уведомления для активного звонка (особенно при работе в фоне)

**3. Производительность**:
- Адаптивный битрейт и разрешение в зависимости от сети
- Использование FLAG_KEEP_SCREEN_ON для экрана во время звонка
- Мониторинг качества соединения (ICE state, RTT, packet loss)

**4. Обработка ошибок**:
```kotlin
override fun onIceConnectionChange(state: PeerConnection.IceConnectionState) {
    when (state) {
        PeerConnection.IceConnectionState.CONNECTED ->
            _callState.value = _callState.value.copy(isConnected = true)

        PeerConnection.IceConnectionState.FAILED,
        PeerConnection.IceConnectionState.DISCONNECTED -> {
            _callState.value = _callState.value.copy(isConnected = false)
            endCall()
        }

        else -> Unit
    }
}
```

**5. Разрешения (упрощённый пример)**:
```kotlin
val permissions = arrayOf(
    Manifest.permission.CAMERA,
    Manifest.permission.RECORD_AUDIO
)
// В продакшене использовать Activity Result API; здесь вызов requestPermissions приведён как упрощённый вариант
requestPermissions(permissions, REQUEST_CODE)
```

### Типичные Ошибки

**❌ Нет TURN сервера**:
- Звонки не работают за NAT/файрволом
- Решение: всегда настраивать TURN в дополнение к STUN

**❌ Неполный/неадресованный signaling**:
- Отправка ICE/SDP без указания целевого peerId
- Решение: в сообщениях signaling всегда указывать от кого и кому

**❌ Не запрошены runtime-разрешения или игнорирование результатов**

**❌ Утечки ресурсов**:
```kotlin
fun endCall() {
    videoCapturer?.run {
        try { stopCapture() } catch (_: Exception) {}
        dispose()
    }
    videoCapturer = null

    localVideoTrack?.dispose()
    localVideoTrack = null

    localAudioTrack?.dispose()
    localAudioTrack = null

    peerConnection?.close()
    peerConnection = null
}
```

**❌ Игнорирование интеграции с платформой**:
- Нет foreground service/уведомления для активного звонка
- Не настроен audio focus/route (динамик/гарнитура/Bluetooth)
- Нет обработки входящих звонков (push + звонковый экран)

---

## Answer (EN)

**Approach**: Use WebRTC for low-latency peer-to-peer audio/video communication (with TURN relay when direct P2P is not possible). A realistic solution needs:
- a signaling channel (WebSocket/HTTP) to exchange SDP and ICE,
- STUN/TURN infrastructure for NAT traversal,
- proper integration with Android audio, permissions, lifecycle, and foreground services.

**Core Components**:
- **PeerConnection** - manages the peer connection and media tracks
- **MediaStream/MediaTracks** - handle audio/video (modern APIs focus on tracks)
- **ICE/STUN/TURN** - NAT traversal
- **Signaling Server** - exchanges SDP and ICE candidates (typically via WebSocket, with peer addressing)

**Architecture**:
```
Device A                        Device B
    ↓                               ↓
Signaling Server ← WebSocket → Offer/Answer/ICE
    ↓                               ↓
Media P2P (WebRTC) ←──────────→ Audio/Video Stream
    ↓
STUN/TURN Server (NAT traversal)
```

### Core Implementation

(Simplified example focusing on architecture; not full production-ready code.)

**WebRTC Manager**:
```kotlin
class WebRTCManager(
    private val context: Context,
    private val signalingClient: SignalingClient,
    private val peerConnectionFactory: PeerConnectionFactory,
    private val eglBase: EglBase
) {
    private var peerConnection: PeerConnection? = null
    private var localVideoTrack: VideoTrack? = null
    private var localAudioTrack: AudioTrack? = null
    private var videoCapturer: VideoCapturer? = null

    private val _callState = MutableStateFlow(CallState())
    val callState = _callState.asStateFlow()

    fun startCall(isVideoCall: Boolean, remotePeerId: String) {
        createPeerConnection(remotePeerId)
        createMediaTracks(isVideoCall)

        val constraints = MediaConstraints()
        peerConnection?.createOffer(object : SdpObserver {
            override fun onCreateSuccess(sdp: SessionDescription) {
                // Set local SDP and send it via signaling
                peerConnection?.setLocalDescription(object : SdpObserver {
                    override fun onSetSuccess() {
                        signalingClient.sendOffer(remotePeerId, sdp)
                    }
                    override fun onSetFailure(p0: String?) {}
                    override fun onCreateSuccess(p0: SessionDescription?) {}
                    override fun onCreateFailure(p0: String?) {}
                }, sdp)
            }
            override fun onSetSuccess() {}
            override fun onCreateFailure(error: String?) {}
            override fun onSetFailure(error: String?) {}
        }, constraints)
    }

    private fun createPeerConnection(remotePeerId: String) {
        val iceServers = listOf(
            // STUN for public IP discovery
            PeerConnection.IceServer.builder("stun:stun.l.google.com:19302").createIceServer(),
            // TURN for strict NAT traversal (required for production)
            PeerConnection.IceServer.builder("turn:your-turn-server.com:3478")
                .setUsername("username")
                .setPassword("password")
                .createIceServer()
        )

        val rtcConfig = PeerConnection.RTCConfiguration(iceServers).apply {
            sdpSemantics = PeerConnection.SdpSemantics.UNIFIED_PLAN
        }

        peerConnection = peerConnectionFactory.createPeerConnection(
            rtcConfig,
            object : PeerConnection.Observer {
                override fun onIceCandidate(candidate: IceCandidate) {
                    // Send candidate to remote peer (simplified)
                    signalingClient.sendIceCandidate(remotePeerId, candidate)
                }
                override fun onIceConnectionChange(newState: PeerConnection.IceConnectionState) {
                    when (newState) {
                        PeerConnection.IceConnectionState.CONNECTED ->
                            _callState.value = _callState.value.copy(isConnected = true)

                        PeerConnection.IceConnectionState.FAILED,
                        PeerConnection.IceConnectionState.DISCONNECTED -> {
                            _callState.value = _callState.value.copy(isConnected = false)
                            endCall()
                        }

                        else -> Unit
                    }
                }
                override fun onTrack(transceiver: RtpTransceiver?) {
                    // Obtain remote tracks from transceiver.receiver.track
                    // and expose them to the UI layer
                }
                // Other callbacks omitted for brevity
            }
        )
    }

    private fun createMediaTracks(isVideoCall: Boolean) {
        // Audio track (always)
        val audioSource = peerConnectionFactory.createAudioSource(MediaConstraints())
        localAudioTrack = peerConnectionFactory.createAudioTrack("audio", audioSource)
        localAudioTrack?.setEnabled(true)
        peerConnection?.addTrack(localAudioTrack)

        // Video track (optional)
        if (isVideoCall) {
            videoCapturer = createVideoCapturer() // implementation (Camera1/Camera2/etc.) is omitted for brevity
            val videoSource = peerConnectionFactory.createVideoSource(false)
            videoCapturer?.initialize(
                SurfaceTextureHelper.create("CaptureThread", eglBase.eglBaseContext),
                context,
                videoSource.capturerObserver
            )
            videoCapturer?.startCapture(1280, 720, 30)

            localVideoTrack = peerConnectionFactory.createVideoTrack("video", videoSource)
            localVideoTrack?.setEnabled(true)
            peerConnection?.addTrack(localVideoTrack)
        }
    }

    fun toggleMute() {
        val muted = !_callState.value.isMuted
        localAudioTrack?.setEnabled(!muted)
        _callState.value = _callState.value.copy(isMuted = muted)
    }

    fun toggleVideo() {
        val enabled = !_callState.value.isVideoEnabled
        _callState.value = _callState.value.copy(isVideoEnabled = enabled)
        localVideoTrack?.setEnabled(enabled)
    }

    fun endCall() {
        videoCapturer?.run {
            try { stopCapture() } catch (_: Exception) {}
            dispose()
        }
        videoCapturer = null

        localVideoTrack?.dispose()
        localVideoTrack = null

        localAudioTrack?.dispose()
        localAudioTrack = null

        peerConnection?.close()
        peerConnection = null

        _callState.value = CallState()
    }
}
```

**Signaling via WebSocket** (simplified; actual schema depends on your backend):
```kotlin
class SignalingClient(
    private val okHttpClient: OkHttpClient,
    private val json: Json,
    private val scope: CoroutineScope
) {
    private var webSocket: WebSocket? = null
    private val _messages = MutableSharedFlow<SignalingMessage>()
    val messages = _messages.asSharedFlow()

    fun connect(userId: String) {
        val request = Request.Builder()
            .url("wss://your-server.com/ws?userId=$userId")
            .build()

        webSocket = okHttpClient.newWebSocket(request, object : WebSocketListener() {
            override fun onMessage(webSocket: WebSocket, text: String) {
                val message = json.decodeFromString<SignalingMessage>(text)
                scope.launch { _messages.emit(message) }
            }
        })
    }

    fun sendOffer(remotePeerId: String, sdp: SessionDescription) {
        send(SignalingMessage.Offer(to = remotePeerId, sdp = sdp.description))
    }

    fun sendAnswer(remotePeerId: String, sdp: SessionDescription) {
        send(SignalingMessage.Answer(to = remotePeerId, sdp = sdp.description))
    }

    fun sendIceCandidate(remotePeerId: String, candidate: IceCandidate) {
        send(
            SignalingMessage.IceCandidate(
                to = remotePeerId,
                sdpMid = candidate.sdpMid ?: "",
                sdpMLineIndex = candidate.sdpMLineIndex,
                sdp = candidate.sdp
            )
        )
    }

    private fun send(message: SignalingMessage) {
        val jsonText = json.encodeToString(SignalingMessage.serializer(), message)
        webSocket?.send(jsonText)
    }
}

@Serializable
sealed class SignalingMessage {
    @Serializable
    data class Offer(val to: String, val sdp: String) : SignalingMessage()

    @Serializable
    data class Answer(val to: String, val sdp: String) : SignalingMessage()

    @Serializable
    data class IceCandidate(
        val to: String,
        val sdpMid: String,
        val sdpMLineIndex: Int,
        val sdp: String
    ) : SignalingMessage()
}
```

**UI (Jetpack Compose)**:
```kotlin
@Composable
fun VideoCallScreen(viewModel: CallViewModel) {
    val callState by viewModel.callState.collectAsState()
    val localVideo by viewModel.localVideoTrack.collectAsState()
    val remoteVideo by viewModel.remoteVideoTrack.collectAsState()

    Box(modifier = Modifier.fillMaxSize()) {
        // Remote video (full screen)
        remoteVideo?.let { track ->
            AndroidView(
                factory = { context ->
                    SurfaceViewRenderer(context).apply {
                        init(viewModel.eglBase.eglBaseContext, null)
                        track.addSink(this)
                    }
                },
                modifier = Modifier.fillMaxSize()
            )
        }

        // Local video (PiP)
        localVideo?.let { track ->
            AndroidView(
                factory = { context ->
                    SurfaceViewRenderer(context).apply {
                        init(viewModel.eglBase.eglBaseContext, null)
                        setZOrderMediaOverlay(true)
                        track.addSink(this)
                    }
                },
                modifier = Modifier
                    .size(120.dp, 160.dp)
                    .align(Alignment.TopEnd)
                    .padding(16.dp)
            )
        }

        // Call controls
        Row(
            modifier = Modifier
                .align(Alignment.BottomCenter)
                .padding(32.dp)
        ) {
            CallButton(
                icon = if (callState.isMuted) Icons.Default.MicOff else Icons.Default.Mic,
                isActive = callState.isMuted,
                onClick = { viewModel.toggleMute() }
            )

            CallButton(
                icon = Icons.Default.CallEnd,
                isActive = true,
                onClick = { viewModel.endCall() }
            )

            CallButton(
                icon = if (callState.isVideoEnabled) Icons.Default.Videocam
                       else Icons.Default.VideocamOff,
                isActive = !callState.isVideoEnabled,
                onClick = { viewModel.toggleVideo() }
            )
        }
    }
}
```

### Best Practices

**1. Server Infrastructure**:
- STUN servers for public IP discovery
- TURN servers for strict NAT traversal (critical in real-world scenarios)
- Signaling server for exchanging SDP and ICE candidates (WebSocket/HTTP with authentication and proper peer routing)

**2. Resource Management and Android Integration**:
- Pause/stop video when app goes to background (per product requirements)
- Properly release tracks, sources, capturer, and PeerConnection
- Manage audio focus and routing with AudioManager / AudioAttributes / AudioFocusRequest
- Use a foreground service + persistent notification for active calls (especially when running in background)

**3. Performance**:
- Adaptive bitrate and resolution based on network conditions
- Use FLAG_KEEP_SCREEN_ON while in active call
- Monitor connection quality (ICE state, RTT, packet loss)

**4. Error Handling**:
```kotlin
override fun onIceConnectionChange(state: PeerConnection.IceConnectionState) {
    when (state) {
        PeerConnection.IceConnectionState.CONNECTED ->
            _callState.value = _callState.value.copy(isConnected = true)

        PeerConnection.IceConnectionState.FAILED,
        PeerConnection.IceConnectionState.DISCONNECTED -> {
            _callState.value = _callState.value.copy(isConnected = false)
            endCall()
        }

        else -> Unit
    }
}
```

**5. Permissions (simplified snippet)**:
```kotlin
val permissions = arrayOf(
    Manifest.permission.CAMERA,
    Manifest.permission.RECORD_AUDIO
)
// For modern apps prefer Activity Result APIs; requestPermissions is shown here as a minimal example
requestPermissions(permissions, REQUEST_CODE)
```

### Common Pitfalls

**❌ No TURN server configured**:
- Calls fail behind many NAT/firewall setups
- Solution: always configure TURN in addition to STUN

**❌ Incomplete/undirected signaling**:
- Sending ICE/SDP without target peer identification
- Solution: include from/to routing information in all signaling messages

**❌ Missing or mishandled runtime permissions**

**❌ Resource leaks**:
```kotlin
fun endCall() {
    videoCapturer?.run {
        try { stopCapture() } catch (_: Exception) {}
        dispose()
    }
    videoCapturer = null

    localVideoTrack?.dispose()
    localVideoTrack = null

    localAudioTrack?.dispose()
    localAudioTrack = null

    peerConnection?.close()
    peerConnection = null
}
```

**❌ Ignoring Android platform integration**:
- No foreground service/notification for ongoing calls
- No proper audio focus/route handling (speaker/headset/Bluetooth)
- No proper handling of incoming calls (e.g., via push + dedicated call UI)

---

## Дополнительные вопросы (RU)

- Как реализовать шаринг экрана во время видеозвонка?
- Как обрабатывать переподключение сети во время активного звонка?
- Как реализовать групповые видеозвонки (несколько участников)?
- Как оптимизировать расход батареи при длительных видеозвонках?
- Как адаптировать качество связи в зависимости от состояния сети?

## Follow-ups

- How to implement screen sharing during a video call?
- How to handle network reconnection during an active call?
- How to implement group video calls (multiple participants)?
- How to optimize battery consumption during long video calls?
- How to handle call quality adaptation based on network conditions?

## Ссылки (RU)

- [WebRTC Official](https://webrtc.org/)
- [WebRTC for Android](https://webrtc.github.io/webrtc-org/native-code/android/)
- [Google Codelabs - WebRTC](https://codelabs.developers.google.com/codelabs/webrtc-web)
- [STUN/TURN Server Setup](https://www.metered.ca/tools/openrelay/)

## References

- [WebRTC Official](https://webrtc.org/)
- [WebRTC for Android](https://webrtc.github.io/webrtc-org/native-code/android/)
- [Google Codelabs - WebRTC](https://codelabs.developers.google.com/codelabs/webrtc-web)
- [STUN/TURN Server Setup](https://www.metered.ca/tools/openrelay/)

## Связанные вопросы (RU)

### Предпосылки / Концепты

- [[c-android]]

### Предпосылки (Проще)
- [[q-http-protocols-comparison--android--medium]] - Понимание протоколов HTTP/WebSocket
- [[q-parallel-network-calls-coroutines--kotlin--medium]] - Асинхронные сетевые операции

### Родственные (Такой же уровень)
- [[q-design-instagram-stories--android--hard]] - Работа с медиа
- [[q-data-sync-unstable-network--android--hard]] - Надежность сети
- [[q-design-whatsapp-app--android--hard]] - Реал-тайм обмен сообщениями

### Продвинутые (Сложнее)
- Проектирование масштабируемой системы видеоконференций
- Реализация сквозного шифрования для видеозвонков

## Related Questions

### Prerequisites / Concepts

- [[c-android]]

### Prerequisites (Easier)
- [[q-http-protocols-comparison--android--medium]] - Understanding HTTP/WebSocket protocols
- [[q-parallel-network-calls-coroutines--kotlin--medium]] - Async network operations

### Related (Same Level)
- [[q-design-instagram-stories--android--hard]] - Media handling
- [[q-data-sync-unstable-network--android--hard]] - Network reliability
- [[q-design-whatsapp-app--android--hard]] - Real-time messaging

### Advanced (Harder)
- Design a scalable video conferencing system
- Implement end-to-end encryption for video calls
```
