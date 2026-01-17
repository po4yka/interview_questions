---
id: android-383
anki_cards:
  - slug: android-383-0-en
    front: "What are the key components for OpenGL ES rendering in Android?"
    back: |
      **Core components:**
      - **GLSurfaceView + Renderer** - manages OpenGL context
      - **ShaderProgram** - vertex + fragment shaders
      - **VAO/VBO/EBO** - vertex data management
      - **Texture** - with mipmaps and filtering
      - **FBO** - render-to-texture for post-processing

      **Best practices:** Cache shaders, use VAOs, generate mipmaps, minimize state changes.
    tags:
      - android_views
      - difficulty::medium
  - slug: android-383-0-ru
    front: "Какие ключевые компоненты для OpenGL ES рендеринга в Android?"
    back: |
      **Основные компоненты:**
      - **GLSurfaceView + Renderer** - управляет OpenGL контекстом
      - **ShaderProgram** - вершинный + фрагментный шейдеры
      - **VAO/VBO/EBO** - управление вершинными данными
      - **Texture** - с mipmaps и фильтрацией
      - **FBO** - render-to-texture для пост-обработки

      **Лучшие практики:** Кешировать шейдеры, использовать VAO, генерировать mipmaps, минимизировать смену состояний.
    tags:
      - android_views
      - difficulty::medium
title: "OpenGL Advanced Rendering / Продвинутый рендеринг OpenGL"
aliases: ["OpenGL Advanced Rendering", "Продвинутый рендеринг OpenGL"]
topic: android
subtopics: [performance-rendering, profiling, ui-graphics]
question_kind: android
difficulty: medium
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-android-surfaces, q-custom-view-animation--android--medium]
created: 2025-10-15
updated: 2025-11-10
sources: []
tags: [3d-graphics, android/performance-rendering, android/profiling, android/ui-graphics, difficulty/medium, opengl-es, rendering, shaders]
---\
# Вопрос (RU)

> Как реализовать продвинутые техники рендеринга с использованием OpenGL ES в Android? Каковы лучшие практики для управления текстурами, framebuffer objects и пользовательских шейдеров?

# Question (EN)

> How do you implement advanced rendering techniques using OpenGL ES in Android? What are best practices for texture management, framebuffer objects, and custom shaders?

---

## Ответ (RU)

OpenGL ES — основной API Android для 3D-графики и продвинутого 2D-рендеринга. Понимание продвинутых техник (буферные объекты, FBO, сложные шейдеры, post-processing) критично для высокопроизводительных графических приложений.

См. также: [[c-android-surfaces]].

Ниже примеры ориентированы на OpenGL ES 3.0+ (GLES30): используются VAO и индексный тип `GL_UNSIGNED_INT`.

### Основные Компоненты

**GLSurfaceView и Renderer:**
Управление OpenGL контекстом через GLSurfaceView с кастомным Renderer.

```kotlin
class CustomRenderer(private val context: Context) : GLSurfaceView.Renderer {
    private lateinit var shader: ShaderProgram
    private lateinit var mesh: Mesh
    private val mvpMatrix = FloatArray(16)

    override fun onSurfaceCreated(gl: GL10?, config: EGLConfig?) {
        // ✅ Enable essential features
        GLES30.glEnable(GLES30.GL_DEPTH_TEST)
        GLES30.glEnable(GLES30.GL_BLEND)
        GLES30.glBlendFunc(GLES30.GL_SRC_ALPHA, GLES30.GL_ONE_MINUS_SRC_ALPHA)

        shader = ShaderProgram(loadShader("vertex.glsl"), loadShader("fragment.glsl"))
        mesh = Mesh.createCube()
    }

    override fun onDrawFrame(gl: GL10?) {
        GLES30.glClear(GLES30.GL_COLOR_BUFFER_BIT or GLES30.GL_DEPTH_BUFFER_BIT)
        shader.use()
        shader.setMatrix4("uMVPMatrix", mvpMatrix)
        mesh.draw(shader)
    }
}
```

**Пользовательские шейдеры:**
ShaderProgram — обёртка для компиляции и управления шейдерами.

```kotlin
class ShaderProgram(vertexCode: String, fragmentCode: String) {
    private val programId: Int
    private val uniformLocations = mutableMapOf<String, Int>()

    init {
        val vertexShader = compileShader(GLES30.GL_VERTEX_SHADER, vertexCode)
        val fragmentShader = compileShader(GLES30.GL_FRAGMENT_SHADER, fragmentCode)

        // ✅ Always validate shader compilation
        checkShaderCompileStatus(vertexShader, "vertex")
        checkShaderCompileStatus(fragmentShader, "fragment")

        programId = GLES30.glCreateProgram()
        GLES30.glAttachShader(programId, vertexShader)
        GLES30.glAttachShader(programId, fragmentShader)
        GLES30.glLinkProgram(programId)

        // ✅ Always validate linking
        val linkStatus = IntArray(1)
        GLES30.glGetProgramiv(programId, GLES30.GL_LINK_STATUS, linkStatus, 0)
        if (linkStatus[0] == GLES30.GL_FALSE) {
            val infoLog = GLES30.glGetProgramInfoLog(programId)
            GLES30.glDeleteProgram(programId)
            throw RuntimeException("Shader linking failed: $infoLog")
        }

        GLES30.glDeleteShader(vertexShader)
        GLES30.glDeleteShader(fragmentShader)
    }

    private fun checkShaderCompileStatus(shaderId: Int, stage: String) {
        val status = IntArray(1)
        GLES30.glGetShaderiv(shaderId, GLES30.GL_COMPILE_STATUS, status, 0)
        if (status[0] == GLES30.GL_FALSE) {
            val infoLog = GLES30.glGetShaderInfoLog(shaderId)
            GLES30.glDeleteShader(shaderId)
            throw RuntimeException("$stage shader compilation failed: $infoLog")
        }
    }

    fun use() {
        GLES30.glUseProgram(programId)
    }

    fun setMatrix4(name: String, matrix: FloatArray) {
        val location = uniformLocations.getOrPut(name) {
            GLES30.glGetUniformLocation(programId, name)
        }
        if (location >= 0) {
            GLES30.glUniformMatrix4fv(location, 1, false, matrix, 0)
        }
    }
}
```

**VAO/VBO/EBO для геометрии:**
Эффективное управление вершинными данными через Vertex `Array` Objects и индексированные draw calls.

```kotlin
class Mesh(vertices: FloatArray, indices: IntArray, private val stride: Int = 8) {
    private val vao: Int
    private val vbo: Int
    private val ebo: Int
    private val indexCount = indices.size

    init {
        val buffers = IntArray(3)
        GLES30.glGenVertexArrays(1, buffers, 0)
        GLES30.glGenBuffers(2, buffers, 1)
        vao = buffers[0]
        vbo = buffers[1]
        ebo = buffers[2]

        GLES30.glBindVertexArray(vao)

        // ✅ Upload vertex data once
        val vertexBuffer = ByteBuffer.allocateDirect(vertices.size * 4)
            .order(ByteOrder.nativeOrder())
            .asFloatBuffer()
        vertexBuffer.put(vertices).position(0)

        GLES30.glBindBuffer(GLES30.GL_ARRAY_BUFFER, vbo)
        GLES30.glBufferData(
            GLES30.GL_ARRAY_BUFFER,
            vertices.size * 4,
            vertexBuffer,
            GLES30.GL_STATIC_DRAW
        )

        // ✅ Upload index data (requires ES 3.0+ for GL_UNSIGNED_INT)
        val indexBuffer = ByteBuffer.allocateDirect(indices.size * 4)
            .order(ByteOrder.nativeOrder())
            .asIntBuffer()
        indexBuffer.put(indices).position(0)

        GLES30.glBindBuffer(GLES30.GL_ELEMENT_ARRAY_BUFFER, ebo)
        GLES30.glBufferData(
            GLES30.GL_ELEMENT_ARRAY_BUFFER,
            indices.size * 4,
            indexBuffer,
            GLES30.GL_STATIC_DRAW
        )

        // Position (3) + Normal (3) + TexCoord (2) in одном интерливнутом буфере
        val strideBytes = stride * 4
        // attribute 0: position
        GLES30.glEnableVertexAttribArray(0)
        GLES30.glVertexAttribPointer(0, 3, GLES30.GL_FLOAT, false, strideBytes, 0)
        // attribute 1: normal
        GLES30.glEnableVertexAttribArray(1)
        GLES30.glVertexAttribPointer(1, 3, GLES30.GL_FLOAT, false, strideBytes, 3 * 4)
        // attribute 2: texCoord
        GLES30.glEnableVertexAttribArray(2)
        GLES30.glVertexAttribPointer(2, 2, GLES30.GL_FLOAT, false, strideBytes, 6 * 4)

        GLES30.glBindVertexArray(0)
    }

    fun draw(shader: ShaderProgram) {
        shader.use()
        GLES30.glBindVertexArray(vao)
        GLES30.glDrawElements(GLES30.GL_TRIANGLES, indexCount, GLES30.GL_UNSIGNED_INT, 0)
        GLES30.glBindVertexArray(0)
    }
}
```

**Управление текстурами:**
Загрузка текстур с mipmaps и правильными параметрами фильтрации.

```kotlin
class Texture private constructor(val textureId: Int) {
    fun bind(unit: Int = 0) {
        GLES30.glActiveTexture(GLES30.GL_TEXTURE0 + unit)
        GLES30.glBindTexture(GLES30.GL_TEXTURE_2D, textureId)
    }

    companion object {
        fun loadFromBitmap(bitmap: Bitmap, recycle: Boolean = true): Texture {
            val textureIds = IntArray(1)
            GLES30.glGenTextures(1, textureIds, 0)
            val id = textureIds[0]
            GLES30.glBindTexture(GLES30.GL_TEXTURE_2D, id)

            // ✅ Set filtering for quality
            GLES30.glTexParameteri(
                GLES30.GL_TEXTURE_2D,
                GLES30.GL_TEXTURE_MIN_FILTER,
                GLES30.GL_LINEAR_MIPMAP_LINEAR
            )
            GLES30.glTexParameteri(
                GLES30.GL_TEXTURE_2D,
                GLES30.GL_TEXTURE_MAG_FILTER,
                GLES30.GL_LINEAR
            )

            GLUtils.texImage2D(GLES30.GL_TEXTURE_2D, 0, bitmap, 0)
            GLES30.glGenerateMipmap(GLES30.GL_TEXTURE_2D)

            // Опционально: задать wrapping-режимы
            // GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D, GLES30.GL_TEXTURE_WRAP_S, GLES30.GL_REPEAT)
            // GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D, GLES30.GL_TEXTURE_WRAP_T, GLES30.GL_REPEAT)

            GLES30.glBindTexture(GLES30.GL_TEXTURE_2D, 0)
            if (recycle) bitmap.recycle()
            return Texture(id)
        }

        // Текстура для использования в качестве render target
        fun createRenderTexture(width: Int, height: Int): Texture {
            val textureIds = IntArray(1)
            GLES30.glGenTextures(1, textureIds, 0)
            val id = textureIds[0]
            GLES30.glBindTexture(GLES30.GL_TEXTURE_2D, id)

            GLES30.glTexImage2D(
                GLES30.GL_TEXTURE_2D,
                0,
                GLES30.GL_RGBA,
                width,
                height,
                0,
                GLES30.GL_RGBA,
                GLES30.GL_UNSIGNED_BYTE,
                null
            )

            GLES30.glTexParameteri(
                GLES30.GL_TEXTURE_2D,
                GLES30.GL_TEXTURE_MIN_FILTER,
                GLES30.GL_LINEAR
            )
            GLES30.glTexParameteri(
                GLES30.GL_TEXTURE_2D,
                GLES30.GL_TEXTURE_MAG_FILTER,
                GLES30.GL_LINEAR
            )

            GLES30.glBindTexture(GLES30.GL_TEXTURE_2D, 0)
            return Texture(id)
        }
    }
}
```

**Framebuffer Objects (FBO):**
Render-to-texture для пост-обработки и эффектов.

```kotlin
class Framebuffer(width: Int, height: Int) {
    val framebufferId: Int
    val colorTexture: Texture
    private val depthRenderbuffer: Int

    init {
        val fboIds = IntArray(1)
        GLES30.glGenFramebuffers(1, fboIds, 0)
        framebufferId = fboIds[0]
        GLES30.glBindFramebuffer(GLES30.GL_FRAMEBUFFER, framebufferId)

        // Color attachment
        colorTexture = Texture.createRenderTexture(width, height)
        GLES30.glFramebufferTexture2D(
            GLES30.GL_FRAMEBUFFER,
            GLES30.GL_COLOR_ATTACHMENT0,
            GLES30.GL_TEXTURE_2D,
            colorTexture.textureId,
            0
        )

        // Depth attachment (for depth testing). For stencil, use a depth-stencil format.
        val rboIds = IntArray(1)
        GLES30.glGenRenderbuffers(1, rboIds, 0)
        depthRenderbuffer = rboIds[0]
        GLES30.glBindRenderbuffer(GLES30.GL_RENDERBUFFER, depthRenderbuffer)
        GLES30.glRenderbufferStorage(
            GLES30.GL_RENDERBUFFER,
            GLES30.GL_DEPTH_COMPONENT16,
            width,
            height
        )
        GLES30.glFramebufferRenderbuffer(
            GLES30.GL_FRAMEBUFFER,
            GLES30.GL_DEPTH_ATTACHMENT,
            GLES30.GL_RENDERBUFFER,
            depthRenderbuffer
        )

        // ✅ Always check completeness
        if (GLES30.glCheckFramebufferStatus(GLES30.GL_FRAMEBUFFER)
            != GLES30.GL_FRAMEBUFFER_COMPLETE
        ) {
            throw RuntimeException("Framebuffer incomplete")
        }
        GLES30.glBindFramebuffer(GLES30.GL_FRAMEBUFFER, 0)
    }
}
```

### Лучшие Практики

**Управление шейдерами:**
- Кешируйте скомпилированные программы
- Валидируйте компиляцию и линковку (и логируйте info log)
- Минимизируйте обновления uniform-переменных

**Вершинные данные:**
- Используйте VAO для эффективного управления атрибутами (ES 3.0+ или расширение)
- Чередуйте атрибуты в одном буфере
- Используйте индексы для устранения дублирования вершин

**Текстуры:**
- Генерируйте mipmaps для фильтрованных текстур
- Используйте сжатие (ETC2, ASTC) для экономии памяти (учитывая поддержку устройств)
- Применяйте texture atlas для мелких текстур

**Производительность рендеринга:**
- Минимизируйте изменения состояния OpenGL
- Группируйте draw call-ы
- Используйте frustum culling для отсечения невидимых объектов

**FBO:**
- Переиспользуйте framebuffer-ы когда возможно
- Используйте renderbuffer для depth/stencil при необходимости
- Проверяйте completeness после создания

### Распространённые Ошибки

- ❌ Не проверять компиляцию шейдеров — тихие сбои
- ❌ Забывать привязывать текстуры — чёрный экран
- ❌ Не освобождать GL ресурсы — утечки памяти / context leaks
- ❌ Загрязнение GL состояния — неожиданный рендеринг
- ❌ Неэффективные draw calls — низкая производительность

---

## Answer (EN)

OpenGL ES is Android's primary API for 3D graphics and advanced 2D rendering. Understanding advanced techniques (buffer objects, FBOs, complex shaders, post-processing) is critical for high-performance graphics applications.

See also: [[c-android-surfaces]].

Examples below target OpenGL ES 3.0+ (GLES30), as they use VAOs and `GL_UNSIGNED_INT` indices.

### Core Components

**GLSurfaceView and Renderer:**
Manage OpenGL context through GLSurfaceView with a custom Renderer.

```kotlin
class CustomRenderer(private val context: Context) : GLSurfaceView.Renderer {
    private lateinit var shader: ShaderProgram
    private lateinit var mesh: Mesh
    private val mvpMatrix = FloatArray(16)

    override fun onSurfaceCreated(gl: GL10?, config: EGLConfig?) {
        // ✅ Enable essential features
        GLES30.glEnable(GLES30.GL_DEPTH_TEST)
        GLES30.glEnable(GLES30.GL_BLEND)
        GLES30.glBlendFunc(GLES30.GL_SRC_ALPHA, GLES30.GL_ONE_MINUS_SRC_ALPHA)

        shader = ShaderProgram(loadShader("vertex.glsl"), loadShader("fragment.glsl"))
        mesh = Mesh.createCube()
    }

    override fun onDrawFrame(gl: GL10?) {
        GLES30.glClear(GLES30.GL_COLOR_BUFFER_BIT or GLES30.GL_DEPTH_BUFFER_BIT)
        shader.use()
        shader.setMatrix4("uMVPMatrix", mvpMatrix)
        mesh.draw(shader)
    }
}
```

**Custom Shaders:**
ShaderProgram wrapper for compiling and managing shaders.

```kotlin
class ShaderProgram(vertexCode: String, fragmentCode: String) {
    private val programId: Int
    private val uniformLocations = mutableMapOf<String, Int>()

    init {
        val vertexShader = compileShader(GLES30.GL_VERTEX_SHADER, vertexCode)
        val fragmentShader = compileShader(GLES30.GL_FRAGMENT_SHADER, fragmentCode)

        // ✅ Always validate shader compilation
        checkShaderCompileStatus(vertexShader, "vertex")
        checkShaderCompileStatus(fragmentShader, "fragment")

        programId = GLES30.glCreateProgram()
        GLES30.glAttachShader(programId, vertexShader)
        GLES30.glAttachShader(programId, fragmentShader)
        GLES30.glLinkProgram(programId)

        // ✅ Always validate linking
        val linkStatus = IntArray(1)
        GLES30.glGetProgramiv(programId, GLES30.GL_LINK_STATUS, linkStatus, 0)
        if (linkStatus[0] == GLES30.GL_FALSE) {
            val infoLog = GLES30.glGetProgramInfoLog(programId)
            GLES30.glDeleteProgram(programId)
            throw RuntimeException("Shader linking failed: $infoLog")
        }

        GLES30.glDeleteShader(vertexShader)
        GLES30.glDeleteShader(fragmentShader)
    }

    private fun checkShaderCompileStatus(shaderId: Int, stage: String) {
        val status = IntArray(1)
        GLES30.glGetShaderiv(shaderId, GLES30.GL_COMPILE_STATUS, status, 0)
        if (status[0] == GLES30.GL_FALSE) {
            val infoLog = GLES30.glGetShaderInfoLog(shaderId)
            GLES30.glDeleteShader(shaderId)
            throw RuntimeException("$stage shader compilation failed: $infoLog")
        }
    }

    fun use() {
        GLES30.glUseProgram(programId)
    }

    fun setMatrix4(name: String, matrix: FloatArray) {
        val location = uniformLocations.getOrPut(name) {
            GLES30.glGetUniformLocation(programId, name)
        }
        if (location >= 0) {
            GLES30.glUniformMatrix4fv(location, 1, false, matrix, 0)
        }
    }
}
```

**VAO/VBO/EBO for Geometry:**
Efficient vertex data management via Vertex `Array` Objects and indexed draw calls.

```kotlin
class Mesh(vertices: FloatArray, indices: IntArray, private val stride: Int = 8) {
    private val vao: Int
    private val vbo: Int
    private val ebo: Int
    private val indexCount = indices.size

    init {
        val buffers = IntArray(3)
        GLES30.glGenVertexArrays(1, buffers, 0)
        GLES30.glGenBuffers(2, buffers, 1)
        vao = buffers[0]
        vbo = buffers[1]
        ebo = buffers[2]

        GLES30.glBindVertexArray(vao)

        // ✅ Upload vertex data once
        val vertexBuffer = ByteBuffer.allocateDirect(vertices.size * 4)
            .order(ByteOrder.nativeOrder())
            .asFloatBuffer()
        vertexBuffer.put(vertices).position(0)

        GLES30.glBindBuffer(GLES30.GL_ARRAY_BUFFER, vbo)
        GLES30.glBufferData(
            GLES30.GL_ARRAY_BUFFER,
            vertices.size * 4,
            vertexBuffer,
            GLES30.GL_STATIC_DRAW
        )

        // ✅ Upload index data (requires ES 3.0+ for GL_UNSIGNED_INT)
        val indexBuffer = ByteBuffer.allocateDirect(indices.size * 4)
            .order(ByteOrder.nativeOrder())
            .asIntBuffer()
        indexBuffer.put(indices).position(0)

        GLES30.glBindBuffer(GLES30.GL_ELEMENT_ARRAY_BUFFER, ebo)
        GLES30.glBufferData(
            GLES30.GL_ELEMENT_ARRAY_BUFFER,
            indices.size * 4,
            indexBuffer,
            GLES30.GL_STATIC_DRAW
        )

        // Position (3) + Normal (3) + TexCoord (2) in a single interleaved buffer
        val strideBytes = stride * 4
        // attribute 0: position
        GLES30.glEnableVertexAttribArray(0)
        GLES30.glVertexAttribPointer(0, 3, GLES30.GL_FLOAT, false, strideBytes, 0)
        // attribute 1: normal
        GLES30.glEnableVertexAttribArray(1)
        GLES30.glVertexAttribPointer(1, 3, GLES30.GL_FLOAT, false, strideBytes, 3 * 4)
        // attribute 2: texCoord
        GLES30.glEnableVertexAttribArray(2)
        GLES30.glVertexAttribPointer(2, 2, GLES30.GL_FLOAT, false, strideBytes, 6 * 4)

        GLES30.glBindVertexArray(0)
    }

    fun draw(shader: ShaderProgram) {
        shader.use()
        GLES30.glBindVertexArray(vao)
        GLES30.glDrawElements(GLES30.GL_TRIANGLES, indexCount, GLES30.GL_UNSIGNED_INT, 0)
        GLES30.glBindVertexArray(0)
    }
}
```

**Texture Management:**
Loading textures with mipmaps and proper filtering parameters.

```kotlin
class Texture private constructor(val textureId: Int) {
    fun bind(unit: Int = 0) {
        GLES30.glActiveTexture(GLES30.GL_TEXTURE0 + unit)
        GLES30.glBindTexture(GLES30.GL_TEXTURE_2D, textureId)
    }

    companion object {
        fun loadFromBitmap(bitmap: Bitmap, recycle: Boolean = true): Texture {
            val textureIds = IntArray(1)
            GLES30.glGenTextures(1, textureIds, 0)
            val id = textureIds[0]
            GLES30.glBindTexture(GLES30.GL_TEXTURE_2D, id)

            // ✅ Set filtering for quality
            GLES30.glTexParameteri(
                GLES30.GL_TEXTURE_2D,
                GLES30.GL_TEXTURE_MIN_FILTER,
                GLES30.GL_LINEAR_MIPMAP_LINEAR
            )
            GLES30.glTexParameteri(
                GLES30.GL_TEXTURE_2D,
                GLES30.GL_TEXTURE_MAG_FILTER,
                GLES30.GL_LINEAR
            )

            GLUtils.texImage2D(GLES30.GL_TEXTURE_2D, 0, bitmap, 0)
            GLES30.glGenerateMipmap(GLES30.GL_TEXTURE_2D)

            // Optional: set wrapping modes as needed
            // GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D, GLES30.GL_TEXTURE_WRAP_S, GLES30.GL_REPEAT)
            // GLES30.glTexParameteri(GLES30.GL_TEXTURE_2D, GLES30.GL_TEXTURE_WRAP_T, GLES30.GL_REPEAT)

            GLES30.glBindTexture(GLES30.GL_TEXTURE_2D, 0)
            if (recycle) bitmap.recycle()
            return Texture(id)
        }

        // Texture configured as a render target
        fun createRenderTexture(width: Int, height: Int): Texture {
            val textureIds = IntArray(1)
            GLES30.glGenTextures(1, textureIds, 0)
            val id = textureIds[0]
            GLES30.glBindTexture(GLES30.GL_TEXTURE_2D, id)

            GLES30.glTexImage2D(
                GLES30.GL_TEXTURE_2D,
                0,
                GLES30.GL_RGBA,
                width,
                height,
                0,
                GLES30.GL_RGBA,
                GLES30.GL_UNSIGNED_BYTE,
                null
            )

            GLES30.glTexParameteri(
                GLES30.GL_TEXTURE_2D,
                GLES30.GL_TEXTURE_MIN_FILTER,
                GLES30.GL_LINEAR
            )
            GLES30.glTexParameteri(
                GLES30.GL_TEXTURE_2D,
                GLES30.GL_TEXTURE_MAG_FILTER,
                GLES30.GL_LINEAR
            )

            GLES30.glBindTexture(GLES30.GL_TEXTURE_2D, 0)
            return Texture(id)
        }
    }
}
```

**Framebuffer Objects (FBO):**
Render-to-texture for post-processing and effects.

```kotlin
class Framebuffer(width: Int, height: Int) {
    val framebufferId: Int
    val colorTexture: Texture
    private val depthRenderbuffer: Int

    init {
        val fboIds = IntArray(1)
        GLES30.glGenFramebuffers(1, fboIds, 0)
        framebufferId = fboIds[0]
        GLES30.glBindFramebuffer(GLES30.GL_FRAMEBUFFER, framebufferId)

        // Color attachment
        colorTexture = Texture.createRenderTexture(width, height)
        GLES30.glFramebufferTexture2D(
            GLES30.GL_FRAMEBUFFER,
            GLES30.GL_COLOR_ATTACHMENT0,
            GLES30.GL_TEXTURE_2D,
            colorTexture.textureId,
            0
        )

        // Depth attachment (for depth testing). For stencil, use a depth-stencil format.
        val rboIds = IntArray(1)
        GLES30.glGenRenderbuffers(1, rboIds, 0)
        depthRenderbuffer = rboIds[0]
        GLES30.glBindRenderbuffer(GLES30.GL_RENDERBUFFER, depthRenderbuffer)
        GLES30.glRenderbufferStorage(
            GLES30.GL_RENDERBUFFER,
            GLES30.GL_DEPTH_COMPONENT16,
            width,
            height
        )
        GLES30.glFramebufferRenderbuffer(
            GLES30.GL_FRAMEBUFFER,
            GLES30.GL_DEPTH_ATTACHMENT,
            GLES30.GL_RENDERBUFFER,
            depthRenderbuffer
        )

        // ✅ Always check completeness
        if (GLES30.glCheckFramebufferStatus(GLES30.GL_FRAMEBUFFER)
            != GLES30.GL_FRAMEBUFFER_COMPLETE
        ) {
            throw RuntimeException("Framebuffer incomplete")
        }
        GLES30.glBindFramebuffer(GLES30.GL_FRAMEBUFFER, 0)
    }
}
```

### Best Practices

**Shader Management:**
- Cache compiled programs
- Validate compilation and linking (and log info logs)
- Minimize uniform updates

**Vertex Data:**
- Use VAOs for efficient attribute management (ES 3.0+ or extension)
- Interleave attributes in a single buffer
- Use indices to eliminate vertex duplication

**Textures:**
- Generate mipmaps for filtered textures
- Use compression (ETC2, ASTC) to save memory (respect device support)
- Apply texture atlases for small textures

**Rendering Performance:**
- Minimize OpenGL state changes
- Batch draw calls
- Use frustum culling to cull invisible objects

**FBO:**
- Reuse framebuffers when possible
- Use renderbuffers for depth/stencil where needed
- Check completeness after creation

### Common Pitfalls

- ❌ Not checking shader compilation — silent failures
- ❌ Forgetting to bind textures — black screen
- ❌ Not releasing GL resources — memory / context leaks
- ❌ GL state pollution — unexpected rendering
- ❌ Inefficient draw calls — poor performance

---

## Дополнительные Вопросы (RU)

- Как реализовать instanced rendering для повторяющейся геометрии (в ES 3.0+ или через соответствующие расширения)?
- В чем различия между GLSL ES и десктопным GLSL?
- Как отлаживать проблемы рендеринга в OpenGL ES?
- Какие форматы сжатия текстур поддерживаются на разных Android-устройствах?
- Как реализовать deferred shading в OpenGL ES (учитывая ограничения и необходимость нескольких рендер-таргетов)?

## Follow-ups

- How do you implement instanced rendering for repeated geometry (in ES 3.0+ or via extensions)?
- What are the differences between GLSL ES and desktop GLSL?
- How do you debug OpenGL ES rendering issues?
- What compression formats are supported across different Android devices?
- How do you implement deferred shading in OpenGL ES (considering limitations and use of multiple render targets)?

## Ссылки (RU)

- OpenGL ES 3.0 Programming Guide
- Android OpenGL ES документация

## References

- OpenGL ES 3.0 Programming Guide
- Android OpenGL ES documentation

## Связанные Вопросы (RU)

### Базовые Знания
- [[q-custom-view-animation--android--medium]] — Рендеринг 2D на `Canvas`

### Связанные
- [[q-jank-detection-frame-metrics--android--medium]] — Мониторинг производительности

### Продвинутое
- (Требуются заметки о compute shaders и PBR-рендеринге для поддерживаемых API/расширений, когда будут доступны)

## Related Questions

### Prerequisites
- [[q-custom-view-animation--android--medium]] — `Canvas`-based 2D rendering

### Related
- [[q-jank-detection-frame-metrics--android--medium]] — Performance monitoring

### Advanced
- (Requires notes on compute shaders and PBR rendering for supported APIs/extensions once available)
