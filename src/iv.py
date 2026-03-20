from math import log, sqrt, exp, pi


def _norm_cdf(x):
    """Approximation of the cumulative normal distribution (Abramowitz & Stegun)."""
    a1, a2, a3, a4, a5 = (
        0.254829592, -0.284496736, 1.421413741, -1.453152027, 1.061405429
    )
    p = 0.3275911
    sign = 1 if x >= 0 else -1
    x = abs(x) / sqrt(2)
    t = 1.0 / (1.0 + p * x)
    y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * exp(-x * x)
    return 0.5 * (1.0 + sign * y)


def bs_price(S, K, T, r, sigma, option_type="call"):
    """Black-Scholes option price."""
    if T <= 0 or sigma <= 0:
        return 0.0
    d1 = (log(S / K) + (r + 0.5 * sigma ** 2) * T) / (sigma * sqrt(T))
    d2 = d1 - sigma * sqrt(T)
    if option_type == "call":
        return S * _norm_cdf(d1) - K * exp(-r * T) * _norm_cdf(d2)
    else:
        return K * exp(-r * T) * _norm_cdf(-d2) - S * _norm_cdf(-d1)


def calc_iv(option_price, S, K, T, r, option_type="call"):
    """Calculate implied volatility using Brent's method (manual implementation).

    Returns IV as a decimal (e.g., 0.50 = 50%) or None if no solution found.
    Uses bisection as a simple, dependency-free approach.
    Upper bound 10.0 (1000% annualized) for Argentine market.
    """
    if T <= 0 or option_price <= 0 or S <= 0 or K <= 0:
        return None

    lo, hi = 0.01, 10.0
    target = option_price

    # Check bounds
    if bs_price(S, K, T, r, lo, option_type) > target:
        return None
    if bs_price(S, K, T, r, hi, option_type) < target:
        return None

    # Bisection: 100 iterations gives precision ~1e-30, more than enough
    for _ in range(100):
        mid = (lo + hi) / 2.0
        price = bs_price(S, K, T, r, mid, option_type)
        if price < target:
            lo = mid
        else:
            hi = mid
        if hi - lo < 1e-6:
            break

    return (lo + hi) / 2.0
