"""Tests for strategies."""
import pytest
import numpy as np
from options_analyzer.core.options_strategies import BullCallSpread

def test_bull_call_spread_creation():
    strategy = BullCallSpread(150.0)
    assert strategy.underlying_price == 150.0
    assert strategy.strategy_name == "Bull Call Spread"

def test_bull_call_spread_analysis(sample_bull_call_spread):
    results = sample_bull_call_spread.analyze()
    assert results.strategy_name == "Bull Call Spread"
    assert isinstance(results.max_profit, (int, float))
    assert isinstance(results.max_loss, (int, float))
