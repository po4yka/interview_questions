---
id: ivc-20251102-016
title: On-device ML (TensorFlow Lite) / On-device ML (TensorFlow Lite)
aliases:
  - On-device ML
  - TensorFlow Lite Android
  - NNAPI Acceleration
kind: concept
summary: Deploying and accelerating machine learning models on Android with TensorFlow Lite, GPU/NNAPI delegates, and model management
links: []
created: 2025-11-02
updated: 2025-11-02
tags:
  - android
  - concept
  - ml
  - tflite
  - nnapi
---

# Summary (EN)

On-device machine learning on Android primarily uses **TensorFlow Lite**, accelerated by GPU, NNAPI, or Hexagon delegates. Key concerns include model quantization, dynamic updates (ML Model Binding / Firebase ML), memory footprint, and thread scheduling.

# Сводка (RU)

On-device ML на Android в основном использует **TensorFlow Lite**, ускоряемый через GPU, NNAPI или Hexagon-точную обработку. Важные аспекты: квантизация моделей, динамические обновления (ML Model Binding / Firebase ML), следы памяти и планирование потоков.

## Core Components

- `Interpreter`, `InterpreterApi`, `Task Library`
- Delegates: GPU, NNAPI, Hexagon (DSP), Core ML (ChromeOS)
- Model optimization: quantization (int8), pruning, sparsity
- Model management: model files, A/B updates, Firebase ML, Model Downloader

## Considerations

- Нужно выполнять inference на worker-потоке; избегайте UI блокировки.
- Делегаты требуют совместимых драйверов; fallback на CPU.
- Следите за размером модели и памятью (mapped ByteBuffer).
