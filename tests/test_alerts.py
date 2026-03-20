from unittest.mock import patch
from src.alerts import _check_pct_change, _check_abs_change, _check_iv_cross


def _make_rule(**kwargs):
    defaults = {
        "id": 1, "name": "Test", "type": "price_pct_change",
        "symbol": "GGAL", "mercado": "bCBA", "direction": "any",
        "threshold": 5.0, "cooldown_minutes": 60,
    }
    defaults.update(kwargs)
    return defaults


class TestPctChange:
    def test_triggers_on_drop(self):
        rule = _make_rule(direction="down", threshold=5.0)
        quote = {"cierreAnterior": 100.0}
        msg = _check_pct_change(rule, 94.0, quote)
        assert msg is not None
        assert "-6.00%" in msg

    def test_no_trigger_below_threshold(self):
        rule = _make_rule(direction="any", threshold=5.0)
        quote = {"cierreAnterior": 100.0}
        msg = _check_pct_change(rule, 97.0, quote)
        assert msg is None

    def test_triggers_on_rise(self):
        rule = _make_rule(direction="up", threshold=3.0)
        quote = {"cierreAnterior": 100.0}
        msg = _check_pct_change(rule, 104.0, quote)
        assert msg is not None

    def test_direction_filter(self):
        rule = _make_rule(direction="up", threshold=5.0)
        quote = {"cierreAnterior": 100.0}
        # Price dropped 6% but rule is "up" only
        msg = _check_pct_change(rule, 94.0, quote)
        assert msg is None

    def test_no_prev_close(self):
        rule = _make_rule()
        quote = {}
        msg = _check_pct_change(rule, 100.0, quote)
        assert msg is None


class TestAbsChange:
    def test_triggers_on_rise(self):
        rule = _make_rule(type="price_abs_change", direction="up", threshold=500)
        quote = {"cierreAnterior": 1000.0}
        msg = _check_abs_change(rule, 1600.0, quote)
        assert msg is not None

    def test_no_trigger(self):
        rule = _make_rule(type="price_abs_change", direction="any", threshold=500)
        quote = {"cierreAnterior": 1000.0}
        msg = _check_abs_change(rule, 1200.0, quote)
        assert msg is None


class TestIvCross:
    def test_cross_above(self):
        rule = _make_rule(type="iv_threshold", threshold=0.50, condition="above")
        msg = _check_iv_cross(rule, 0.55, 0.45)
        assert msg is not None
        assert "SUBE" in msg

    def test_cross_below(self):
        rule = _make_rule(type="iv_threshold", threshold=0.50, condition="below")
        msg = _check_iv_cross(rule, 0.45, 0.55)
        assert msg is not None
        assert "BAJA" in msg

    def test_no_cross(self):
        rule = _make_rule(type="iv_threshold", threshold=0.50, condition="above")
        msg = _check_iv_cross(rule, 0.48, 0.45)
        assert msg is None

    def test_no_prev_iv(self):
        rule = _make_rule(type="iv_threshold", threshold=0.50, condition="above")
        msg = _check_iv_cross(rule, 0.55, None)
        assert msg is None
