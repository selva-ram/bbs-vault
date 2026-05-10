# NET-SEC — Cryptographic OTP Vault

Blum Blum Shub CSPRNG-based One-Time Password system.

---

## Quick Start

```bash
cd backend
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000` in your browser.

---

## How It Works

1. User enters their User ID and clicks **Generate OTP**.
2. Backend generates an OTP using the Blum Blum Shub CSPRNG seeded with `SHA-256(user_id + timestamp_ns)`.
3. OTP is stored server-side; in production it would be delivered via SMS/email.
4. User enters the OTP within 120 seconds and clicks **Verify OTP**.
5. Backend verifies using constant-time comparison. Max 3 attempts.

---

## Security Fixes (vs original)

| # | Issue | Fix |
|---|-------|-----|
| 1 | **OTP returned in API response** — anyone sniffing traffic gets the OTP | OTP is never sent to the client |
| 2 | **BBS primes not Blum primes** — tiny primes like 101 don't satisfy p ≡ 3 (mod 4) | Large primes (≈1e9) all satisfying `p % 4 == 3` |
| 3 | **BBS seed could be 0 or 1** — trivial fixed points | `find_valid_seed()` ensures gcd(seed, M)=1 and seed ∉ {0,1,M-1} |
| 4 | **Timing attack on OTP comparison** — `==` leaks length/content timing | `hmac.compare_digest()` (constant-time) |
| 5 | **No rate-limiting on /generate-otp** — OTP flooding possible | Max 5 generates/minute per user_id; 429 response |
| 6 | **No input validation** on user_id | Regex `^[A-Za-z0-9_-]{1,64}$`; length capped |
| 7 | **CORS wildcard** — any origin can call the API | Configurable allow-list via env var `ALLOWED_ORIGINS` |
| 8 | **Timer mismatch** — frontend 120 s, backend 240 s | Both set to 120 s (single source of truth) |
| 9 | **Memory leak** — expired OTPs never cleaned up | Background cleanup thread removes stale records every 60 s |
| 10| **`alert()` for UI feedback** — blocks JS thread, bad UX | Inline status box with success/error/info styles |
| 11| **Fragile timer selector** (`.text-2xl`) — breaks if HTML changes | Timer element has explicit `id="timer-count"` |
| 12| **No security headers** | `X-Content-Type-Options`, `X-Frame-Options`, `Referrer-Policy`, `Cache-Control: no-store` |
| 13| **`debug=True` hardcoded** | Debug only enabled when `FLASK_DEBUG=true` env var is set |
| 14| **`time.time()` for duration** — vulnerable to clock adjustments | Switched to `time.monotonic()` for expiry checks |
| 15| **No paste support** on OTP boxes | Paste handler distributes digits across all 6 boxes |

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `ALLOWED_ORIGINS` | `http://localhost:5000,http://127.0.0.1:5000` | Comma-separated CORS origins |
| `FLASK_DEBUG` | `false` | Set to `true` for debug mode (dev only) |

---

## Project Structure

```
NET-SEC/
├── backend/
│   ├── app.py           — Flask routes, CORS, security headers
│   ├── bbs.py           — Blum Blum Shub CSPRNG
│   ├── config.py        — All tuneable constants
│   ├── otp_service.py   — OTP generation, verification, rate-limiting
│   └── requirements.txt
└── frontend/
    ├── index.html
    ├── css/style.css
    └── js/script.js
```
