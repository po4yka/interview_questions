---
id: "20251110-124631"
title: "Multipart Form Data / Multipart Form Data"
aliases: ["Multipart Form Data"]
summary: "Foundational concept for interview preparation"
topic: "programming-languages"
subtopics: ["general"]
question_kind: "theory"
difficulty: "medium"
original_language: "en"
language_tags: ["en", "ru"]
sources: []
status: "draft"
moc: "moc-cs"
related: ["c-http-client", "c-networking", "c-rest-api", "c-serialization", "c-okhttp-architecture"]
created: "2025-11-10"
updated: "2025-11-10"
tags: [concept, difficulty/medium, programming-languages]
---

# Summary (EN)

Multipart/form-data is an HTTP content type used to submit web form data, especially files and mixed binary/text fields, as a set of distinct parts in a single request body. Each part has its own headers (such as Content-Disposition and Content-Type) and is separated by a boundary, allowing servers to reliably parse multiple fields and files. It is widely used in browser form submissions, REST APIs, and upload endpoints where application/x-www-form-urlencoded is insufficient.

*This concept file was auto-generated. Please expand with detailed information.*

# Краткое Описание (RU)

multipart/form-data — это тип содержимого HTTP, используемый для отправки данных веб-форм, особенно файлов и смешанных бинарных/текстовых полей, как набора отдельных частей в одном теле запроса. У каждой части есть собственные заголовки (например, Content-Disposition и Content-Type) и границы-разделители (boundary), что позволяет серверу корректно разобрать несколько полей и файлов. Широко используется при отправке форм из браузера, в REST API и эндпоинтах загрузки, когда application/x-www-form-urlencoded недостаточен.

*Этот файл концепции был создан автоматически. Пожалуйста, дополните его подробной информацией.*

## Key Points (EN)

- Structured payload: Encodes the request body as multiple parts separated by a boundary, enabling transmission of multiple named fields and files in a single HTTP request.
- Content-Disposition: Each part typically includes a Content-Disposition header with a "form-data" type, a field "name", and optionally a "filename" for file uploads.
- Mixed types: Supports both text and binary data, making it the standard choice for file uploads (images, documents, etc.) from HTML forms and many HTTP clients.
- Parsing requirements: Servers must stream and parse multipart content incrementally (often using libraries/framework support) to handle potentially large payloads efficiently.
- Comparison: Preferred over application/x-www-form-urlencoded when dealing with large data, binary content, or complex form structures.

## Ключевые Моменты (RU)

- Структурированное тело: Кодирует тело запроса как несколько частей, разделённых boundary, что позволяет передавать несколько именованных полей и файлов в одном HTTP-запросе.
- Content-Disposition: Каждая часть обычно содержит заголовок Content-Disposition с типом "form-data", именем поля (name) и при необходимости именем файла (filename) для загрузок.
- Смешанные типы данных: Поддерживает текстовые и бинарные данные, поэтому является стандартом для загрузки файлов (изображения, документы и т.п.) из HTML-форм и многих HTTP-клиентов.
- Требования к парсингу: Сервер должен построчно/поточно разбирать multipart-контент (обычно через стандартные библиотеки/фреймворки), чтобы эффективно обрабатывать большие объёмы данных.
- Сравнение: Предпочтительнее application/x-www-form-urlencoded при работе с большими данными, бинарным содержимым или сложными формами.

## References

- RFC 7578: Returning Values from Forms: multipart/form-data
- MDN Web Docs: "multipart/form-data" (form enctype and HTTP requests)
