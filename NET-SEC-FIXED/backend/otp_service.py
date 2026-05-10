"""
OTP Service
───────────
Fixes applied vs original:
  • OTP is NEVER returned to the caller (must be delivered out-of-band)
  • Constant-time string comparison to prevent timing attacks
  • Rate-limiting on generate (MAX_GENERATE_PER_MINUTE per user_id)
  • Background cleanup thread removes stale records (no memory leak)
  • BBS seed validated before use (no trivial cycles)
  • Input length capped to prevent DoS via huge user_id strings
"""

import time
import hmac
import hashlib
import threading
from bbs import generate_modulus, find_valid_seed, bbs_generate
from config import (
    OTP_LENGTH,
    OTP_EXPIRY_SECONDS,
    MAX_ATTEMPTS,
    MAX_GENERATE_PER_MINUTE,
    BBS_ITERATIONS,
)

# ─── In-memory stores ────────────────────────────────────────────────────────

_lock = threading.Lock()

# { user_id: { "otp": str, "time": float, "attempts": int } }
_otp_store: dict[str, dict] = {}

# { user_id: [timestamp, timestamp, …] }  — for rate-limiting
_generate_log: dict[str, list[float]] = {}

# ─── Background cleanup ───────────────────────────────────────────────────────

def _cleanup_expired() -> None:
    """Periodically remove expired OTP records and old rate-limit entries."""
    while True:
        time.sleep(60)
        now = time.monotonic()
        with _lock:
            expired_otps = [
                uid for uid, rec in _otp_store.items()
                if now - rec["time"] > OTP_EXPIRY_SECONDS
            ]
            for uid in expired_otps:
                del _otp_store[uid]

            old_logs = [
                uid for uid, timestamps in _generate_log.items()
                if all(now - t > 60 for t in timestamps)
            ]
            for uid in old_logs:
                del _generate_log[uid]


_cleanup_thread = threading.Thread(target=_cleanup_expired, daemon=True)
_cleanup_thread.start()

# ─── Rate limiting ────────────────────────────────────────────────────────────

def _check_rate_limit(user_id: str) -> bool:
    """Return True if the user may generate a new OTP, False if rate-limited."""
    now = time.monotonic()
    with _lock:
        timestamps = _generate_log.get(user_id, [])
        # Keep only timestamps within the last 60 seconds
        timestamps = [t for t in timestamps if now - t <= 60]
        if len(timestamps) >= MAX_GENERATE_PER_MINUTE:
            _generate_log[user_id] = timestamps
            return False
        timestamps.append(now)
        _generate_log[user_id] = timestamps
        return True

# ─── Public API ───────────────────────────────────────────────────────────────

MAX_USER_ID_LEN = 64


def generate_otp(user_id: str) -> dict:
    """
    Generate and store an OTP for *user_id*.

    Returns:
        {"ok": True}  on success  — OTP is stored internally only.
        {"ok": False, "message": str}  on failure.

    The OTP is intentionally NOT returned; the caller must deliver it
    via a trusted out-of-band channel (SMS, email, etc.).
    """
    if len(user_id) > MAX_USER_ID_LEN:
        return {"ok": False, "message": "user_id too long"}

    if not _check_rate_limit(user_id):
        return {"ok": False, "message": "Rate limit exceeded. Try again later."}

    # ── BBS generation ────────────────────────────────────────────────────────
    p, q, M = generate_modulus()

    seed_input = f"{user_id}{time.time_ns()}"          # ns timestamp for uniqueness
    seed_hash  = hashlib.sha256(seed_input.encode()).hexdigest()
    candidate  = int(seed_hash, 16) % M
    seed       = find_valid_seed(candidate, M)

    random_number = bbs_generate(seed, M, BBS_ITERATIONS)

    otp = str(random_number % (10 ** OTP_LENGTH)).zfill(OTP_LENGTH)

    # ── Store ─────────────────────────────────────────────────────────────────
    with _lock:
        _otp_store[user_id] = {
            "otp":      otp,
            "time":     time.monotonic(),   # use monotonic for duration checks
            "attempts": 0,
        }

    return {"ok": True}


def verify_otp(user_id: str, user_otp: str) -> dict:
    """
    Verify *user_otp* against the stored OTP for *user_id*.

    Returns:
        {"status": True,  "message": str}  on success.
        {"status": False, "message": str}  on failure.
    """
    if len(user_id) > MAX_USER_ID_LEN:
        return {"status": False, "message": "Invalid request"}

    with _lock:
        record = _otp_store.get(user_id)

        if record is None:
            return {"status": False, "message": "No OTP found for this user"}

        # ── Expiry ────────────────────────────────────────────────────────────
        if time.monotonic() - record["time"] > OTP_EXPIRY_SECONDS:
            del _otp_store[user_id]
            return {"status": False, "message": "OTP expired"}

        # ── Attempt limit (checked before comparison) ─────────────────────────
        if record["attempts"] >= MAX_ATTEMPTS:
            del _otp_store[user_id]
            return {"status": False, "message": "Too many failed attempts"}

        record["attempts"] += 1

        # ── Constant-time comparison (prevents timing oracle) ─────────────────
        match = hmac.compare_digest(
            user_otp.encode("utf-8"),
            record["otp"].encode("utf-8"),
        )

        if match:
            del _otp_store[user_id]
            return {"status": True, "message": "Access granted"}

        # Delete after final failed attempt
        if record["attempts"] >= MAX_ATTEMPTS:
            del _otp_store[user_id]

        return {"status": False, "message": "Invalid OTP"}
