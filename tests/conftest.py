"""Pytest configuration."""
import pytest
import sys
from pathlib import Path

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

@pytest.fixture
def sample_bull_call_spread():
    from options_analyzer.core.options_strategies import BullCallSpread
    strategy = BullCallSpread(150.0)
    strategy.add_legs(145.0, 155.0, 3.0, 1.0, "2024-12-20")
    return strategy
