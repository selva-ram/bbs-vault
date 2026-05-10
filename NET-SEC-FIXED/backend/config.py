# ─────────────────────────────────────────────
# OTP Settings
# ─────────────────────────────────────────────
OTP_LENGTH = 6
OTP_EXPIRY_SECONDS = 120        # 2 minutes; frontend timer must match
MAX_ATTEMPTS = 3
MAX_GENERATE_PER_MINUTE = 5     # rate-limit per user_id

# ─────────────────────────────────────────────
# BBS Settings
# ─────────────────────────────────────────────
BBS_ITERATIONS = 32             # more squarings → more diffusion

# BBS requires primes p, q where p ≡ 3 (mod 4) AND q ≡ 3 (mod 4).
# Using larger safe primes for better security.
# All values below satisfy: n % 4 == 3
PRIMES = [
    1000000007,   # ≡ 3 (mod 4)  — 1e9+7
    1000000403,   # ≡ 3 (mod 4)
    998244353,    # ≡ 1 (mod 4)  — skip at runtime
    999999751,    # ≡ 3 (mod 4)
    1000000931,   # ≡ 3 (mod 4)
    999998927,    # ≡ 3 (mod 4)
    1000001011,   # ≡ 3 (mod 4)
    999999893,    # ≡ 1 (mod 4)  — skip at runtime
    1000003631,   # ≡ 3 (mod 4)
    999997219,    # ≡ 3 (mod 4)
]

# Filter to only those ≡ 3 (mod 4) at import time so bbs.py never has
# to worry about it.
BBS_PRIMES = [p for p in PRIMES if p % 4 == 3]
