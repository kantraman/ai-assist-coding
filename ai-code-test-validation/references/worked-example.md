# Worked Example: weak vs requirement-driven tests

**Requirements** (from the ticket)
- R1 Totals >= 100 get 10% off. R2 Gift cards are never discounted.
- R3 Negative totals raise ValueError. R4 Round half up to cents.

**AI-generated code** (typical: correct-looking, compiles, passes its own tests)

```python
def apply_discount(total, is_gift_card=False):
    if total < 0: raise ValueError("total must not be negative")
    if is_gift_card: return Decimal(total)
    if total >= 100:
        return (Decimal(total) * Decimal("0.90")).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
    return Decimal(total)
```

**Weak suite** (2 tests: `apply_discount(200) == 180`, `apply_discount(50) == 50`): green, looks reasonable.
Mutation check: **33%**. Survivors: `< 0`→`<= 0`, `< 0`→`< 1`, `>= 100`→`> 100`, `>= 100`→`>= 101`. The boundary and validation rules (R1 edge, R3) and gift-card rule (R2) are effectively untested: an off-by-one in the threshold would ship.

**Requirement-driven suite** (8 tests): 99.99 / 100 / 100.01 boundary triplet; gift card above and below threshold; -0.01 rejected with message; 0 accepted; 100.05 → 90.05 (half-up, computed by hand: 90.045).
Mutation check: **100%**.

**Lessons to reuse**
1. Green tests prove nothing until mutation-checked.
2. Boundary triplets and negative-space tests (gift card NOT discounted) kill the survivors.
3. Hand-computed expected values (90.045 → 90.05) verify rounding independently of the code.
4. If the baseline goes red after a mutation run, suspect stale caches (.pyc, build output) before suspecting the code; `scripts/mutate.py` clears them and re-verifies the suite at the end.
