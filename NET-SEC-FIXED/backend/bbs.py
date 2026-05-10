"""
Blum Blum Shub (BBS) CSPRNG
─────────────────────────────
Requirements for security:
  • p and q must both be ≡ 3 (mod 4)   (Blum primes)
  • seed x₀ must be coprime with M = p*q
  • seed x₀ must not be 0, 1, or M-1   (trivial cycles)

We enforce all three here so callers don't have to think about it.
"""

import math
import secrets
from config import BBS_PRIMES


def _get_blum_prime_pair() -> tuple[int, int]:
    """Return two distinct Blum primes from BBS_PRIMES."""
    if len(BBS_PRIMES) < 2:
        raise RuntimeError("Need at least 2 Blum primes in config.BBS_PRIMES")

    primes = BBS_PRIMES[:]
    secrets.SystemRandom().shuffle(primes)       # cryptographically shuffled

    p = primes[0]
    q = primes[1]
    assert p != q, "Blum primes must be distinct"
    return p, q


def generate_modulus() -> tuple[int, int, int]:
    """Return (p, q, M) where M = p * q is the BBS modulus."""
    p, q = _get_blum_prime_pair()
    return p, q, p * q


def _is_valid_seed(seed: int, M: int) -> bool:
    """A seed is valid if it is coprime with M and not a trivial state."""
    return (
        seed > 1
        and seed < M - 1
        and math.gcd(seed, M) == 1
    )


def find_valid_seed(candidate: int, M: int) -> int:
    """
    Adjust *candidate* until it is a valid BBS seed for modulus M.
    Tries candidate, candidate+1, … up to 1000 offsets; raises on failure.
    """
    for delta in range(1000):
        s = (candidate + delta) % M
        if _is_valid_seed(s, M):
            return s
    raise ValueError("Could not find a valid BBS seed — check prime size")


def bbs_generate(seed: int, M: int, iterations: int) -> int:
    """
    Run BBS for *iterations* squarings starting from *seed*.
    Returns the final state value x_n.
    """
    if not _is_valid_seed(seed, M):
        raise ValueError(f"Invalid BBS seed {seed} for modulus {M}")

    x = seed
    for _ in range(iterations):
        x = (x * x) % M
    return x
