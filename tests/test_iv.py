from src.iv import bs_price, calc_iv


def test_bs_call_price():
    """Test Black-Scholes call price against known value."""
    # S=100, K=100, T=1, r=0.05, sigma=0.20 -> ~10.45
    price = bs_price(100, 100, 1, 0.05, 0.20, "call")
    assert 10.0 < price < 11.0


def test_bs_put_price():
    """Test Black-Scholes put price."""
    price = bs_price(100, 100, 1, 0.05, 0.20, "put")
    assert 5.0 < price < 7.0


def test_calc_iv_call():
    """Test IV recovery: price a call at known vol, then recover it."""
    S, K, T, r, sigma = 100, 100, 1, 0.05, 0.30
    price = bs_price(S, K, T, r, sigma, "call")
    recovered_iv = calc_iv(price, S, K, T, r, "call")
    assert recovered_iv is not None
    assert abs(recovered_iv - sigma) < 0.001


def test_calc_iv_put():
    """Test IV recovery for put."""
    S, K, T, r, sigma = 100, 110, 0.5, 0.05, 0.40
    price = bs_price(S, K, T, r, sigma, "put")
    recovered_iv = calc_iv(price, S, K, T, r, "put")
    assert recovered_iv is not None
    assert abs(recovered_iv - sigma) < 0.001


def test_calc_iv_high_vol():
    """Test IV calculation with high volatility (Argentine market)."""
    S, K, T, r, sigma = 1000, 1200, 0.25, 0.40, 2.0
    price = bs_price(S, K, T, r, sigma, "call")
    recovered_iv = calc_iv(price, S, K, T, r, "call")
    assert recovered_iv is not None
    assert abs(recovered_iv - sigma) < 0.01


def test_calc_iv_invalid_inputs():
    """Test that invalid inputs return None."""
    assert calc_iv(0, 100, 100, 1, 0.05) is None
    assert calc_iv(10, 0, 100, 1, 0.05) is None
    assert calc_iv(10, 100, 100, 0, 0.05) is None
    assert calc_iv(10, 100, 100, -1, 0.05) is None
