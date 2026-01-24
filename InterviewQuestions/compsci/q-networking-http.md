---
id: cs-net-http
title: Networking - HTTP and Web Protocols
topic: networking
difficulty: medium
tags:
- cs_networking
- http
- web
anki_cards:
- slug: cs-net-http-0-en
  language: en
  anki_id: 1769160677274
  synced_at: '2026-01-24T10:34:05.612386'
- slug: cs-net-http-0-ru
  language: ru
  anki_id: 1769160677299
  synced_at: '2026-01-24T10:34:05.616418'
- slug: cs-net-http-1-en
  language: en
  anki_id: 1769160677324
  synced_at: '2026-01-24T10:34:05.618798'
- slug: cs-net-http-1-ru
  language: ru
  anki_id: 1769160677351
  synced_at: '2026-01-24T10:34:05.621495'
- slug: cs-net-http-2-en
  language: en
  anki_id: 1769160677374
  synced_at: '2026-01-24T10:34:05.623728'
- slug: cs-net-http-2-ru
  language: ru
  anki_id: 1769160677399
  synced_at: '2026-01-24T10:34:05.625914'
---
# HTTP and Web Protocols

## HTTP Basics

**HTTP** (Hypertext Transfer Protocol): Application layer protocol for web communication.

**Request-Response model**: Client sends request, server sends response.

### HTTP/1.1 Request

```
GET /index.html HTTP/1.1
Host: www.example.com
User-Agent: Mozilla/5.0
Accept: text/html
Accept-Language: en-US
Connection: keep-alive

[optional body for POST/PUT]
```

### HTTP/1.1 Response

```
HTTP/1.1 200 OK
Content-Type: text/html; charset=UTF-8
Content-Length: 1234
Date: Mon, 23 Jan 2024 12:00:00 GMT
Server: Apache/2.4
Connection: keep-alive

<!DOCTYPE html>
<html>...
```

## HTTP Methods

| Method | Purpose | Idempotent | Safe |
|--------|---------|------------|------|
| GET | Retrieve resource | Yes | Yes |
| POST | Create resource | No | No |
| PUT | Update/replace resource | Yes | No |
| PATCH | Partial update | No | No |
| DELETE | Remove resource | Yes | No |
| HEAD | GET without body | Yes | Yes |
| OPTIONS | Get allowed methods | Yes | Yes |

**Idempotent**: Same request = same result (can retry safely).
**Safe**: No side effects (read-only).

## Status Codes

| Range | Category | Examples |
|-------|----------|----------|
| 1xx | Informational | 100 Continue |
| 2xx | Success | 200 OK, 201 Created, 204 No Content |
| 3xx | Redirection | 301 Moved Permanently, 302 Found, 304 Not Modified |
| 4xx | Client Error | 400 Bad Request, 401 Unauthorized, 403 Forbidden, 404 Not Found |
| 5xx | Server Error | 500 Internal Server Error, 502 Bad Gateway, 503 Service Unavailable |

### Common Status Codes

```
200 OK                - Request successful
201 Created           - Resource created (POST)
204 No Content        - Success, no body (DELETE)
301 Moved Permanently - URL changed permanently
302 Found             - Temporary redirect
304 Not Modified      - Use cached version
400 Bad Request       - Invalid syntax
401 Unauthorized      - Authentication required
403 Forbidden         - No permission
404 Not Found         - Resource doesn't exist
405 Method Not Allowed- Method not supported
409 Conflict          - Resource conflict
429 Too Many Requests - Rate limited
500 Internal Server Error - Server failure
502 Bad Gateway       - Invalid response from upstream
503 Service Unavailable - Server overloaded/maintenance
504 Gateway Timeout   - Upstream server timeout
```

## HTTP Headers

### Request Headers

```
Host: www.example.com           # Required in HTTP/1.1
User-Agent: Mozilla/5.0         # Browser/client info
Accept: text/html, application/json  # Acceptable content types
Accept-Language: en-US          # Preferred language
Accept-Encoding: gzip, deflate  # Compression support
Authorization: Bearer <token>   # Authentication
Cookie: session=abc123          # Client cookies
Content-Type: application/json  # Body format (POST/PUT)
Content-Length: 348             # Body size
Cache-Control: no-cache         # Caching directive
If-None-Match: "etag123"        # Conditional request
```

### Response Headers

```
Content-Type: application/json  # Response body format
Content-Length: 256             # Response size
Content-Encoding: gzip          # Compression used
Set-Cookie: session=xyz; HttpOnly  # Set client cookie
Cache-Control: max-age=3600     # Caching instructions
ETag: "abc123"                  # Resource version
Last-Modified: Wed, 21 Oct...   # Last change time
Location: /new-url              # Redirect target
Access-Control-Allow-Origin: *  # CORS header
```

## HTTP Versions

### HTTP/1.0

- One request per connection
- Connection closed after response

### HTTP/1.1

- Persistent connections (keep-alive)
- Pipelining (send multiple requests without waiting)
- Host header required
- Chunked transfer encoding

**Head-of-line blocking**: Responses must come in request order.

### HTTP/2

- Binary protocol (not text)
- Multiplexing: Multiple streams over single connection
- Header compression (HPACK)
- Server push
- Stream prioritization

```
Single TCP Connection
        |
   +----+----+----+
   |    |    |    |
Stream1 Stream2 Stream3
   |    |    |    |
```

### HTTP/3

- Uses QUIC (UDP-based)
- No head-of-line blocking at transport
- Faster connection establishment
- Built-in encryption

## HTTPS

HTTP over TLS/SSL.

### TLS Handshake

```
Client                          Server
   |                              |
   |------ Client Hello -------->|  (supported ciphers, random)
   |                              |
   |<----- Server Hello ---------|  (chosen cipher, certificate)
   |                              |
   |  [Verify certificate]        |
   |                              |
   |------ Key Exchange -------->|  (encrypted pre-master secret)
   |                              |
   |<----- Finished -------------|
   |------ Finished ------------>|
   |                              |
   |  [Encrypted communication]   |
```

### TLS 1.3

- 1-RTT handshake (was 2-RTT)
- 0-RTT resumption
- Removed weak ciphers
- Forward secrecy required

## Cookies

Small data stored in browser, sent with every request to domain.

```
Set-Cookie: session=abc123;
    Domain=example.com;
    Path=/;
    Expires=Wed, 09 Jun 2024;
    HttpOnly;
    Secure;
    SameSite=Strict
```

**Attributes**:
- **Domain**: Cookie sent to this domain and subdomains
- **Path**: Cookie sent for this path
- **Expires/Max-Age**: Expiration time
- **HttpOnly**: Not accessible via JavaScript
- **Secure**: Only sent over HTTPS
- **SameSite**: CSRF protection (Strict/Lax/None)

## Sessions and Authentication

### Session-Based Auth

```
1. User logs in (username/password)
2. Server creates session, stores in database
3. Server sends session ID in cookie
4. Client sends cookie with each request
5. Server looks up session, authenticates
```

### Token-Based Auth (JWT)

```
1. User logs in
2. Server creates JWT (signed token)
3. Client stores token (localStorage or cookie)
4. Client sends token in Authorization header
5. Server verifies signature, extracts claims
```

**JWT Structure**:
```
header.payload.signature

Header: {"alg": "HS256", "typ": "JWT"}
Payload: {"sub": "user123", "exp": 1234567890}
Signature: HMACSHA256(base64(header) + "." + base64(payload), secret)
```

## Caching

### Cache-Control Directives

```
Cache-Control: public, max-age=3600      # Cache for 1 hour
Cache-Control: private, max-age=600      # Browser only
Cache-Control: no-cache                   # Validate before use
Cache-Control: no-store                   # Never cache
Cache-Control: must-revalidate           # Revalidate after expiry
```

### Conditional Requests

**ETag-based**:
```
Request:  If-None-Match: "abc123"
Response: 304 Not Modified (if unchanged)
```

**Date-based**:
```
Request:  If-Modified-Since: Wed, 21 Oct...
Response: 304 Not Modified (if unchanged)
```

## CORS (Cross-Origin Resource Sharing)

Controls cross-domain requests in browsers.

**Simple requests**: GET, HEAD, POST with simple headers.

**Preflight request** (OPTIONS):
```
OPTIONS /api/resource HTTP/1.1
Origin: https://example.com
Access-Control-Request-Method: PUT
Access-Control-Request-Headers: Content-Type

Response:
Access-Control-Allow-Origin: https://example.com
Access-Control-Allow-Methods: GET, PUT, POST
Access-Control-Allow-Headers: Content-Type
Access-Control-Max-Age: 86400
```

## REST Principles

1. **Stateless**: No server-side session state
2. **Uniform interface**: Standard HTTP methods
3. **Resource-based**: URLs represent resources
4. **Representations**: JSON, XML, etc.

```
GET    /users        - List users
GET    /users/123    - Get user 123
POST   /users        - Create user
PUT    /users/123    - Update user 123
DELETE /users/123    - Delete user 123
```

## Interview Questions

1. **What happens when you type URL in browser?**
   - DNS lookup
   - TCP connection
   - TLS handshake (if HTTPS)
   - HTTP request
   - Server processes
   - HTTP response
   - Browser renders

2. **How does HTTP/2 improve performance?**
   - Multiplexing (parallel requests)
   - Header compression
   - Binary protocol
   - Server push

3. **What's the difference between 401 and 403?**
   - 401: Not authenticated (needs login)
   - 403: Authenticated but not authorized
