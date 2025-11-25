---
id: android-380
title: "Vulkan RenderScript / Vulkan и RenderScript"
aliases: ["Vulkan RenderScript / Vulkan и RenderScript", "Vulkan RenderScript"]
topic: android
subtopics: [performance-rendering]
question_kind: theory
difficulty: hard
original_language: en
language_tags: [en, ru]
status: draft
moc: moc-android
related: [c-performance, q-surfaceview-rendering--android--medium]
created: 2024-10-15
updated: 2025-11-10
tags: [android/performance-rendering, difficulty/hard]
date created: Saturday, November 1st 2025, 12:47:06 pm
date modified: Tuesday, November 25th 2025, 8:53:56 pm
---

# Вопрос (RU)
> Как использовать Vulkan для низкоуровневых операций на GPU в Android? Какие существуют альтернативы устаревшему RenderScript? Как реализовать compute-шейдеры и GPU-ускоренную обработку изображений?

# Question (EN)
> How do you use Vulkan for low-level GPU operations in Android? What are the alternatives to deprecated RenderScript? How do you implement compute shaders and GPU-accelerated image processing?

## Ответ (RU)
С устареванием RenderScript в Android 12 нужны современные подходы к вычислениям на GPU. На Android для этого применяют `Vulkan` (низкоуровневый доступ), compute-шейдеры в `OpenGL ES 3.1+` и высокооптимизированные CPU/NDK решения. Примеры ниже концептуальны и опускают детали продакшн-кода (жизненный цикл, обработка ошибок, полный пайплайн). См. также [[c-performance]].

#### 1. Базовые Шаги Vulkan Для Android (концептуально)

Для вычислений или обработки изображений с помощью `Vulkan`:

1. Создать `VkInstance`.
2. Выбрать физическое устройство с поддержкой нужных очередей и фич.
3. Создать логическое устройство и получить compute/graphics очередь.
4. Для графики — создать Android-surface через `VK_KHR_android_surface`; для чистого compute surface не нужен.
5. Создать буферы/изображения и выделить/привязать память.
6. Описать `descriptor set layout`, `pipeline layout` и создать compute-pipeline со `SPIR-V` compute-шейдером.
7. Выделить command buffer, записать `vkCmdBindPipeline` / `vkCmdBindDescriptorSets` / `vkCmdDispatch`.
8. Отправить команды в очередь, синхронизироваться (fence/барьеры).
9. При необходимости считать результаты на CPU.

Пример упрощённого процессора Vulkan (псевдо-Kotlin; зависит от конкретных binding'ов):

```kotlin
class VulkanComputeProcessor {
    // Псевдокод: реальные типы и функции зависят от выбранной Vulkan-библиотеки для Android.

    fun initVulkanForCompute() {
        // 1) Создать instance
        // 2) Выбрать физическое устройство с compute-очередью
        // 3) Создать логическое устройство и получить compute-queue
        // 4) Создать descriptor set layout, pipeline layout
        // 5) Создать compute-pipeline из SPIR-V шейдера
    }

    fun executeCompute(width: Int, height: Int) {
        // Выделить и записать command buffer:
        // - привязать compute-pipeline
        // - привязать descriptor sets (input/output images или buffers)
        // - вызвать vkCmdDispatch(groupCountX, groupCountY, 1)
        // Отправить в очередь и дождаться выполнения (fence)
    }
}
```

Пример GLSL compute-шейдера (простое box blur):

```glsl
#version 450

layout (local_size_x = 16, local_size_y = 16) in;

layout (binding = 0, rgba8) uniform readonly image2D inputImage;
layout (binding = 1, rgba8) uniform writeonly image2D outputImage;

void main() {
    ivec2 pos = ivec2(gl_GlobalInvocationID.xy);
    ivec2 size = imageSize(inputImage);

    if (pos.x >= size.x || pos.y >= size.y) {
        return;
    }

    // Simple box blur
    vec4 color = vec4(0.0);
    int radius = 2;
    int count = 0;

    for (int y = -radius; y <= radius; y++) {
        for (int x = -radius; x <= radius; x++) {
            ivec2 samplePos = pos + ivec2(x, y);
            if (samplePos.x >= 0 && samplePos.x < size.x &&
                samplePos.y >= 0 && samplePos.y < size.y) {
                color += imageLoad(inputImage, samplePos);
                count++;
            }
        }
    }

    color /= float(count);
    imageStore(outputImage, pos, color);
}
```

Важно:
- Использовать реальные Vulkan bindings под Android/NDK, а не desktop LWJGL.
- `VK_KHR_android_surface` нужен только при работе с Android UI surface.

#### 2. Альтернативы RenderScript

RenderScript помечен как `deprecated` (Android 12+), новые решения должны опираться на:

- `Vulkan` compute-пайплайны — максимум контроля и производительности.
- Compute-шейдеры в `OpenGL ES 3.1+` — проще, часто достаточно.
- Оптимизированный CPU-код и/или NDK-библиотеки — для fallback и небольших задач.

Пример (устаревший RenderScript — только для legacy-устройств):

```kotlin
class RenderScriptProcessor(private val context: Context) {

    private val renderScript = RenderScript.create(context)

    fun blurBitmap(input: Bitmap, radius: Float): Bitmap {
        val output = Bitmap.createBitmap(input.width, input.height, input.config)

        val inputAllocation = Allocation.createFromBitmap(renderScript, input)
        val outputAllocation = Allocation.createFromBitmap(renderScript, output)

        val blurScript = ScriptIntrinsicBlur.create(
            renderScript,
            Element.U8_4(renderScript)
        )

        blurScript.setRadius(radius.coerceIn(0f, 25f))
        blurScript.setInput(inputAllocation)
        blurScript.forEach(outputAllocation)

        outputAllocation.copyTo(output)

        inputAllocation.destroy()
        outputAllocation.destroy()
        blurScript.destroy()

        return output
    }

    fun cleanup() {
        renderScript.destroy()
    }
}
```

#### 3. Compute-шейдеры В OpenGL ES 3.1

`OpenGL ES 3.1+` даёт compute-шейдеры и обычно проще в интеграции, чем `Vulkan`:

- Создать EGL-контекст ES 3.1.
- Собрать программу с compute-шейдером.
- Привязать текстуры как `image2D` через `glBindImageTexture`.
- Вызвать `glDispatchCompute` и `glMemoryBarrier`.

Пример упрощённого процессора (структура совпадает с EN):

```kotlin
class OpenGLES31ComputeProcessor : ImageProcessor {

    private var computeProgram = 0

    fun init() {
        // Создать EGL-контекст (ES 3.1), затем:
        computeProgram = createComputeProgram(COMPUTE_SHADER_SOURCE)
    }

    override fun blur(input: Bitmap, radius: Float): Bitmap {
        // 1) Загрузить Bitmap во входную текстуру (image unit 0, READ_ONLY)
        // 2) Создать выходную текстуру (image unit 1, WRITE_ONLY)
        // 3) glUseProgram(computeProgram); передать radius
        // 4) glDispatchCompute(...); glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)
        // 5) Считать данные через glReadPixels из FBO в Bitmap
        return input
    }

    override fun convolve(input: Bitmap, kernel: FloatArray): Bitmap {
        // Аналогично, но с использованием свёрточного ядра как uniform или SSBO.
        return input
    }

    override fun cleanup() {
        if (computeProgram != 0) {
            GLES31.glDeleteProgram(computeProgram)
        }
        // Освободить EGL-контекст/поверхность, если создавались здесь.
    }
}
```

Ключевые моменты:
- Не использовать `glGetTexImage` в `OpenGL ES`.
- Все вызовы GLES делать только при текущем EGL-контексте.

#### 4. CPU Fallback

Наличие CPU-реализации важно:

- для устройств без `Vulkan`/`OpenGL ES 3.1`;
- для небольших изображений, где накладные расходы GPU не окупаются.

Пример CPU-реализации (упрощённый, наивный blur и 3x3 convolution — демонстрационные, не оптимизированы под продакшн):

```kotlin
class CPUImageProcessor : ImageProcessor {

    override fun blur(input: Bitmap, radius: Float): Bitmap {
        val r = radius.toInt().coerceAtLeast(1)
        val w = input.width
        val h = input.height
        val pixels = IntArray(w * h)
        input.getPixels(pixels, 0, w, 0, 0, w, h)

        val out = IntArray(w * h)

        for (y in 0 until h) {
            for (x in 0 until w) {
                var red = 0
                var green = 0
                var blue = 0
                var alpha = 0
                var count = 0

                for (ky in -r..r) {
                    for (kx in -r..r) {
                        val px = (x + kx).coerceIn(0, w - 1)
                        val py = (y + ky).coerceIn(0, w - 1)
                        val p = pixels[py * w + px]
                        alpha += Color.alpha(p)
                        red += Color.red(p)
                        green += Color.green(p)
                        blue += Color.blue(p)
                        count++
                    }
                }

                out[y * w + x] = Color.argb(
                    alpha / count,
                    red / count,
                    green / count,
                    blue / count
                )
            }
        }

        val output = Bitmap.createBitmap(w, h, input.config)
        output.setPixels(out, 0, w, 0, 0, w, h)
        return output
    }

    override fun convolve(input: Bitmap, kernel: FloatArray): Bitmap {
        require(kernel.size == 9) { "Only 3x3 kernels supported" }

        val w = input.width
        val h = input.height
        val src = IntArray(w * h)
        input.getPixels(src, 0, w, 0, 0, w, h)
        val dst = IntArray(w * h)

        for (y in 1 until h - 1) {
            for (x in 1 until w - 1) {
                var ri = 0f
                var gi = 0f
                var bi = 0f
                var ki = 0

                for (ky in -1..1) {
                    for (kx in -1..1) {
                        val p = src[(y + ky) * w + (x + kx)]
                        val k = kernel[ki++]
                        ri += Color.red(p) * k
                        gi += Color.green(p) * k
                        bi += Color.blue(p) * k
                    }
                }

                dst[y * w + x] = Color.rgb(
                    ri.toInt().coerceIn(0, 255),
                    gi.toInt().coerceIn(0, 255),
                    bi.toInt().coerceIn(0, 255)
                )
            }
        }

        val output = Bitmap.createBitmap(w, h, input.config)
        output.setPixels(dst, 0, w, 0, 0, w, h)
        return output
    }

    override fun cleanup() { /* no-op */ }
}
```

#### 5. Выбор Между Vulkan, OpenGL ES И CPU / NDK

Рекомендации при миграции с RenderScript:

```kotlin
class GPUComputeProcessor(private val context: Context) {

    private val processor: ImageProcessor = when {
        isVulkanSupported() -> VulkanBackedProcessor()    // концептуальный placeholder
        isOpenGLES31Supported() -> OpenGLES31ComputeProcessor()
        else -> CPUImageProcessor()
    }

    fun blurBitmap(input: Bitmap, radius: Float): Bitmap =
        processor.blur(input, radius)

    fun applyConvolution(input: Bitmap, kernel: FloatArray): Bitmap =
        processor.convolve(input, kernel)

    private fun isVulkanSupported(): Boolean {
        // Упрощённая проверка: наличие Vulkan-уровня.
        // В реальном коде дополнительно проверяйте версии, feature level и нужные queue families/расширения.
        return context.packageManager.hasSystemFeature("android.hardware.vulkan.level")
    }

    private fun isOpenGLES31Supported(): Boolean {
        val am = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
        // Минимальная проверка на поддержку ES 3.1; для точной информации учитывайте фактическую конфигурацию устройства.
        return am.deviceConfigurationInfo.reqGlEsVersion >= 0x00030001
    }

    fun cleanup() {
        processor.cleanup()
    }
}
```

Ключевые моменты:
- Проверять поддержку `Vulkan` (level/version/фичи) и версии `OpenGL ES` в рантайме; наличие feature-флага не гарантирует, что устройство подходит под все требования конкретного пайплайна.
- Инкапсулировать реализацию за интерфейсом `ImageProcessor` для удобства fallback.

### Лучшие Практики (RU)

1. Правильный выбор API:
   - `Vulkan` — максимум контроля и минимальные накладные расходы, но высокая сложность.
   - `OpenGL ES 3.1+` — compute-шейдеры с более простым API.
   - CPU/NDK — надёжный fallback.
2. Миграция с RenderScript:
   - Не использовать RenderScript для нового кода.
   - Оценивать возможности устройства и всегда иметь CPU fallback.
3. Производительность:
   - Подбирать подходящий размер work group (8x8, 16x16 и т.п.).
   - Минимизировать передачи данных между CPU и GPU.
   - Переиспользовать пайплайны/ресурсы.
4. Память и ресурсы:
   - Корректно освобождать Vulkan/GL/EGL-ресурсы.
5. Синхронизация:
   - Использовать барьеры и fence'ы, корректно ждать завершения GPU.

### Распространённые Ошибки (RU)

1. Не проверять поддержку `Vulkan`/`OpenGL ES` → падения на устройствах без нужных фич.
2. Использовать desktop-only API (LWJGL, `glGetTexImage`) на Android → некорректная работа.
3. Отсутствие синхронизации → гонки и артефакты.
4. Не освобождать ресурсы → утечки памяти на GPU.
5. Выбор неоптимальных размеров work group или частого чтения с GPU → низкая производительность.
6. Отсутствие CPU fallback → невозможность работы на части устройств.

### Резюме (RU)

После устаревания RenderScript для GPU-вычислений в Android используют `Vulkan` compute, compute-шейдеры `OpenGL ES 3.1+` и эффективные CPU/NDK решения. `Vulkan` даёт максимальную гибкость, но сложен; `OpenGL ES` проще и часто достаточно; CPU-реализация необходима как резервный путь. Важно понимать архитектуру пайплайна, проверки возможностей устройства, синхронизацию и управление ресурсами.

## Answer (EN)
With RenderScript deprecated in Android 12, developers need modern approaches for GPU computing. On Android, typical options are `Vulkan` for low-level GPU access, compute shaders in `OpenGL ES 3.1+`, and highly optimized CPU/NDK implementations as reliable fallbacks. Examples below are conceptual and omit full production details (lifecycle, error handling, complete pipelines).

#### 1. Vulkan Basics for Android (Conceptual)

High-level steps for using `Vulkan` for compute or image processing on Android:

1. Create a `VkInstance`.
2. Select a physical device that supports required queue families and features.
3. Create a logical device and obtain compute/graphics queues.
4. For graphics, create an Android surface via `VK_KHR_android_surface`; for pure compute, no surface is required.
5. Create buffers/images and allocate/bind memory.
6. Define descriptor set layouts, pipeline layout, and create a compute pipeline with a `SPIR-V` compute shader.
7. Allocate a command buffer, record `vkCmdBindPipeline` / `vkCmdBindDescriptorSets` / `vkCmdDispatch`.
8. Submit to a queue and synchronize via fences/barriers.
9. Read results back on the CPU if needed.

Example (simplified, pseudo-Kotlin using Vulkan bindings; not directly copy-pastable with the standard Android SDK):

```kotlin
class VulkanComputeProcessor {
    // Pseudo-code: types and functions depend on the chosen Vulkan binding for Android.

    fun initVulkanForCompute() {
        // 1) Create instance
        // 2) Pick physical device with a compute-capable queue
        // 3) Create logical device and get compute queue
        // 4) Create descriptor set layout, pipeline layout
        // 5) Create compute pipeline from SPIR-V shader
    }

    fun executeCompute(width: Int, height: Int) {
        // Allocate and record command buffer:
        // - bind compute pipeline
        // - bind descriptor sets (input/output images or buffers)
        // - vkCmdDispatch(groupCountX, groupCountY, 1)
        // Submit to queue and wait/fence
    }
}
```

Example compute shader (GLSL, simple box blur):

```glsl
#version 450

layout (local_size_x = 16, local_size_y = 16) in;

layout (binding = 0, rgba8) uniform readonly image2D inputImage;
layout (binding = 1, rgba8) uniform writeonly image2D outputImage;

void main() {
    ivec2 pos = ivec2(gl_GlobalInvocationID.xy);
    ivec2 size = imageSize(inputImage);

    if (pos.x >= size.x || pos.y >= size.y) {
        return;
    }

    // Simple box blur
    vec4 color = vec4(0.0);
    int radius = 2;
    int count = 0;

    for (int y = -radius; y <= radius; y++) {
        for (int x = -radius; x <= radius; x++) {
            ivec2 samplePos = pos + ivec2(x, y);
            if (samplePos.x >= 0 && samplePos.x < size.x &&
                samplePos.y >= 0 && samplePos.y < size.y) {
                color += imageLoad(inputImage, samplePos);
                count++;
            }
        }
    }

    color /= float(count);
    imageStore(outputImage, pos, color);
}
```

Key points:
- Use a Vulkan binding that works on Android/NDK (not desktop-only libraries).
- `VK_KHR_android_surface` is needed only when rendering to Android UI surfaces.

#### 2. RenderScript Alternatives

RenderScript is deprecated starting with Android 12. New and migrated code should rely on:

- `Vulkan` compute pipelines for maximum control and performance.
- `OpenGL ES 3.1+` compute shaders as a simpler GPU option.
- Optimized CPU and/or NDK libraries as a fallback and for smaller workloads.

Legacy example (RenderScript, for existing devices only):

```kotlin
class RenderScriptProcessor(private val context: Context) {

    private val renderScript = RenderScript.create(context)

    fun blurBitmap(input: Bitmap, radius: Float): Bitmap {
        val output = Bitmap.createBitmap(input.width, input.height, input.config)

        val inputAllocation = Allocation.createFromBitmap(renderScript, input)
        val outputAllocation = Allocation.createFromBitmap(renderScript, output)

        val blurScript = ScriptIntrinsicBlur.create(
            renderScript,
            Element.U8_4(renderScript)
        )

        blurScript.setRadius(radius.coerceIn(0f, 25f))
        blurScript.setInput(inputAllocation)
        blurScript.forEach(outputAllocation)

        outputAllocation.copyTo(output)

        inputAllocation.destroy()
        outputAllocation.destroy()
        blurScript.destroy()

        return output
    }

    fun cleanup() {
        renderScript.destroy()
    }
}
```

#### 3. OpenGL ES 3.1 Compute Shaders

`OpenGL ES 3.1+` provides compute shaders and is often easier to integrate than `Vulkan`:

- Create an EGL context targeting ES 3.1.
- Build a program with a compute shader.
- Bind images/textures via `glBindImageTexture`.
- Call `glDispatchCompute` and `glMemoryBarrier`.

Example (simplified):

```kotlin
class OpenGLES31ComputeProcessor : ImageProcessor {

    private var computeProgram = 0

    fun init() {
        // Create EGL context (ES 3.1), then:
        computeProgram = createComputeProgram(COMPUTE_SHADER_SOURCE)
    }

    override fun blur(input: Bitmap, radius: Float): Bitmap {
        // 1) Upload Bitmap to input texture (image unit 0, READ_ONLY)
        // 2) Create output texture (image unit 1, WRITE_ONLY)
        // 3) glUseProgram(computeProgram); pass radius
        // 4) glDispatchCompute(...); glMemoryBarrier(GL_SHADER_IMAGE_ACCESS_BARRIER_BIT)
        // 5) Read pixels back from an FBO into a Bitmap
        return input
    }

    override fun convolve(input: Bitmap, kernel: FloatArray): Bitmap {
        // Same idea, with convolution kernel as uniform or SSBO.
        return input
    }

    override fun cleanup() {
        if (computeProgram != 0) {
            GLES31.glDeleteProgram(computeProgram)
        }
        // Destroy EGL context/surface if created here.
    }
}
```

Key points:
- Do not use `glGetTexImage` on Android/`OpenGL ES`.
- Ensure an EGL context is current on the calling thread before GLES calls.

#### 4. CPU Fallback Implementation

CPU implementations matter for devices without required GPU features or for cases where GPU overhead is too high for the workload size.

```kotlin
class CPUImageProcessor : ImageProcessor {

    override fun blur(input: Bitmap, radius: Float): Bitmap {
        val r = radius.toInt().coerceAtLeast(1)
        val w = input.width
        val h = input.height
        val pixels = IntArray(w * h)
        input.getPixels(pixels, 0, w, 0, 0, w, h)

        val out = IntArray(w * h)

        for (y in 0 until h) {
            for (x in 0 until w) {
                var red = 0
                var green = 0
                var blue = 0
                var alpha = 0
                var count = 0

                for (ky in -r..r) {
                    for (kx in -r..r) {
                        val px = (x + kx).coerceIn(0, w - 1)
                        val py = (y + ky).coerceIn(0, w - 1)
                        val p = pixels[py * w + px]
                        alpha += Color.alpha(p)
                        red += Color.red(p)
                        green += Color.green(p)
                        blue += Color.blue(p)
                        count++
                    }
                }

                out[y * w + x] = Color.argb(
                    alpha / count,
                    red / count,
                    green / count,
                    blue / count
                )
            }
        }

        val output = Bitmap.createBitmap(w, h, input.config)
        output.setPixels(out, 0, w, 0, 0, w, h)
        return output
    }

    override fun convolve(input: Bitmap, kernel: FloatArray): Bitmap {
        require(kernel.size == 9) { "Only 3x3 kernels supported" }

        val w = input.width
        val h = input.height
        val src = IntArray(w * h)
        input.getPixels(src, 0, w, 0, 0, w, h)
        val dst = IntArray(w * h)

        for (y in 1 until h - 1) {
            for (x in 1 until w - 1) {
                var ri = 0f
                var gi = 0f
                var bi = 0f
                var ki = 0

                for (ky in -1..1) {
                    for (kx in -1..1) {
                        val p = src[(y + ky) * w + (x + kx)]
                        val k = kernel[ki++]
                        ri += Color.red(p) * k
                        gi += Color.green(p) * k
                        bi += Color.blue(p) * k
                    }
                }

                dst[y * w + x] = Color.rgb(
                    ri.toInt().coerceIn(0, 255),
                    gi.toInt().coerceIn(0, 255),
                    bi.toInt().coerceIn(0, 255)
                )
            }
        }

        val output = Bitmap.createBitmap(w, h, input.config)
        output.setPixels(dst, 0, w, 0, 0, w, h)
        return output
    }

    override fun cleanup() { /* no-op */ }
}
```

#### 5. Choosing Between Vulkan, OpenGL ES, and CPU / NDK

A practical migration strategy from RenderScript:

```kotlin
class GPUComputeProcessor(private val context: Context) {

    private val processor: ImageProcessor = when {
        isVulkanSupported() -> VulkanBackedProcessor()    // conceptual placeholder
        isOpenGLES31Supported() -> OpenGLES31ComputeProcessor()
        else -> CPUImageProcessor()
    }

    fun blurBitmap(input: Bitmap, radius: Float): Bitmap =
        processor.blur(input, radius)

    fun applyConvolution(input: Bitmap, kernel: FloatArray): Bitmap =
        processor.convolve(input, kernel)

    private fun isVulkanSupported(): Boolean {
        // Simplified check: presence of a Vulkan level feature.
        // In real-world code, also verify supported versions, feature levels, queue families, and required extensions.
        return context.packageManager.hasSystemFeature("android.hardware.vulkan.level")
    }

    private fun isOpenGLES31Supported(): Boolean {
        val am = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
        // Minimal check for ES 3.1 support; actual supported version depends on device configuration.
        return am.deviceConfigurationInfo.reqGlEsVersion >= 0x00030001
    }

    fun cleanup() {
        processor.cleanup()
    }
}
```

Key notes:
- Always check device capabilities for `Vulkan` and `OpenGL ES` (including versions and required features); a feature flag alone does not guarantee suitability for your specific pipeline.
- Hide backend details behind an `ImageProcessor` interface to simplify fallbacks.

### Best Practices (EN)

1. API choice:
   - `Vulkan` for maximum control and minimal overhead, at the cost of higher complexity.
   - `OpenGL ES 3.1+` for compute shaders with a simpler API.
   - CPU/NDK as a reliable fallback path.
2. Migration from RenderScript:
   - Do not use RenderScript for new code.
   - Detect device capabilities and always provide a CPU fallback.
3. Performance:
   - Choose appropriate work group sizes (e.g., 8x8, 16x16).
   - Minimize CPU↔GPU data transfers.
   - Reuse pipelines and GPU resources where possible.
4. Memory and resources:
   - Correctly release Vulkan/GL/EGL resources.
5. Synchronization:
   - Use proper barriers and fences; wait for GPU completion correctly.

### Common Pitfalls (EN)

1. Skipping runtime checks for `Vulkan`/`OpenGL ES` support → crashes on unsupported devices.
2. Using desktop-only APIs (e.g., LWJGL, `glGetTexImage`) on Android → undefined/incorrect behavior.
3. Missing synchronization → race conditions and visual artifacts.
4. Not releasing resources → GPU memory leaks.
5. Poor work group sizing or excessive GPU readbacks → bad performance.
6. No CPU fallback → app unusable on some devices.

### Summary (EN)

After RenderScript deprecation, practical GPU compute on Android is built on `Vulkan` compute pipelines, `OpenGL ES 3.1+` compute shaders, and efficient CPU/NDK implementations. `Vulkan` offers maximum flexibility but is complex; `OpenGL ES` is easier and often sufficient; CPU remains essential as a fallback. Understanding the pipeline architecture, capability checks, synchronization, and resource management is critical for robust solutions.

## Дополнительные Вопросы (RU)

- Как спроектировать абстракцию (например, интерфейс `ImageProcessor`), чтобы можно было прозрачно переключаться между реализациями на Vulkan, OpenGL ES и CPU без изменения кода вызова?
- Как профилировать и сравнивать end-to-end задержку (включая копирование данных) между Vulkan, OpenGL ES compute и CPU для реального пайплайна обработки изображений на целевых классах устройств?
- [[q-surfaceview-rendering--android--medium]]

## Follow-ups

- How would you design an abstraction layer (e.g., `ImageProcessor` interface) so you can swap between Vulkan, OpenGL ES, and CPU implementations without changing call sites?
- How do you profile and compare end-to-end latency (including memory transfers) between Vulkan, OpenGL ES compute, and CPU for a real image-processing pipeline on a target device class?
- [[q-surfaceview-rendering--android--medium]]

## Ссылки (RU)

- [Rendering Performance](https://developer.android.com/topic/performance/rendering)

## References

- [Rendering Performance](https://developer.android.com/topic/performance/rendering)

## Связанные Вопросы (RU)

- [[q-dagger-field-injection--android--medium]]
- [[q-accessibility-compose--android--medium]]
- [[q-compose-compiler-plugin--android--hard]]

## Related Questions

- [[q-dagger-field-injection--android--medium]]
- [[q-accessibility-compose--android--medium]]
- [[q-compose-compiler-plugin--android--hard]]
