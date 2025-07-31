"""Ejemplo básico de uso."""
import sys
from pathlib import Path

src_path = Path(__file__).parent.parent / "src"
sys.path.insert(0, str(src_path))

from options_analyzer.core.options_strategies import BullCallSpread
from options_analyzer.data.market_data import get_market_data

def example_bull_call_spread():
    print("🚀 Ejemplo: Bull Call Spread")
    
    # Crear estrategia
    strategy = BullCallSpread(150.0)
    strategy.add_legs(145.0, 155.0, 3.0, 1.0, "2024-12-20")
    
    # Analizar
    results = strategy.analyze()
    
    print(f"Max Profit: ${results.max_profit:.2f}")
    print(f"Max Loss: ${results.max_loss:.2f}")
    print(f"Breakevens: {results.breakeven_points}")

if __name__ == "__main__":
    example_bull_call_spread()
