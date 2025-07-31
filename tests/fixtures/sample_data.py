"""Sample data for testing."""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def get_sample_price_data(symbol: str = "AAPL", days: int = 30) -> pd.DataFrame:
    dates = pd.date_range(start=datetime.now() - timedelta(days=days), periods=days, freq='D')
    prices = 150 + np.cumsum(np.random.randn(days) * 0.5)
    
    return pd.DataFrame({
        'Close': prices,
        'Open': prices * 0.99,
        'High': prices * 1.02,
        'Low': prices * 0.98,
        'Volume': np.random.randint(100000, 1000000, days)
    }, index=dates)
