"""
Asset Configuration - Complete metadata for financial assets
"""

# Asset categories with icons and colors
ASSET_CATEGORIES = {
    "stocks": {
        "icon": "📈", 
        "name": "Stocks", 
        "color": "#4CAF50",
        "description": "Acciones de empresas"
    },
    "etfs": {
        "icon": "🏦", 
        "name": "ETFs", 
        "color": "#2196F3",
        "description": "Fondos cotizados"
    },
    "indices": {
        "icon": "📊", 
        "name": "Indices", 
        "color": "#FF9800",
        "description": "Índices bursátiles"
    },
    "crypto": {
        "icon": "₿", 
        "name": "Crypto", 
        "color": "#FFC107",
        "description": "Criptomonedas"
    }
}

# Sector categories
SECTORS = {
    "Technology": {"icon": "💻", "color": "#2196F3"},
    "Finance": {"icon": "🏛️", "color": "#4CAF50"},
    "Healthcare": {"icon": "🏥", "color": "#E91E63"},
    "Consumer": {"icon": "🛒", "color": "#FF9800"},
    "Energy": {"icon": "⚡", "color": "#FFC107"},
    "Automotive": {"icon": "🚗", "color": "#9C27B0"},
    "Entertainment": {"icon": "🎬", "color": "#F44336"},
    "Broad Market": {"icon": "📊", "color": "#607D8B"},
    "Small Cap": {"icon": "📈", "color": "#795548"},
    "Commodities": {"icon": "🏆", "color": "#FFD700"},
    "Bonds": {"icon": "📜", "color": "#4CAF50"},
    "Volatility": {"icon": "📉", "color": "#F44336"},
    "Cryptocurrency": {"icon": "₿", "color": "#FFC107"}
}

# Complete asset database
ASSETS_DATABASE = {
    # Technology Stocks
    "AAPL": {
        "name": "Apple Inc.",
        "category": "stocks",
        "sector": "Technology",
        "description": "Empresa de tecnología líder en dispositivos móviles y software",
        "market_cap": "3.2T",
        "pe_ratio": 28.5
    },
    "GOOGL": {
        "name": "Alphabet Inc.",
        "category": "stocks",
        "sector": "Technology",
        "description": "Empresa de tecnología líder en búsqueda y publicidad digital",
        "market_cap": "1.8T",
        "pe_ratio": 25.2
    },
    "MSFT": {
        "name": "Microsoft Corp.",
        "category": "stocks",
        "sector": "Technology",
        "description": "Empresa de software y servicios en la nube",
        "market_cap": "2.9T",
        "pe_ratio": 32.1
    },
    "NVDA": {
        "name": "NVIDIA Corp.",
        "category": "stocks",
        "sector": "Technology",
        "description": "Empresa líder en GPUs y inteligencia artificial",
        "market_cap": "1.2T",
        "pe_ratio": 45.8
    },
    "META": {
        "name": "Meta Platforms",
        "category": "stocks",
        "sector": "Technology",
        "description": "Empresa de redes sociales y realidad virtual",
        "market_cap": "850B",
        "pe_ratio": 22.3
    },
    
    # Consumer Stocks
    "TSLA": {
        "name": "Tesla Inc.",
        "category": "stocks",
        "sector": "Automotive",
        "description": "Empresa de vehículos eléctricos y energía renovable",
        "market_cap": "750B",
        "pe_ratio": 65.2
    },
    "AMZN": {
        "name": "Amazon.com Inc.",
        "category": "stocks",
        "sector": "Consumer",
        "description": "Empresa de comercio electrónico y servicios en la nube",
        "market_cap": "1.6T",
        "pe_ratio": 35.7
    },
    "NFLX": {
        "name": "Netflix Inc.",
        "category": "stocks",
        "sector": "Entertainment",
        "description": "Empresa de streaming de contenido audiovisual",
        "market_cap": "250B",
        "pe_ratio": 28.9
    },
    
    # ETFs
    "SPY": {
        "name": "SPDR S&P 500 ETF",
        "category": "etfs",
        "sector": "Broad Market",
        "description": "ETF que replica el índice S&P 500",
        "expense_ratio": 0.0945,
        "aum": "400B"
    },
    "QQQ": {
        "name": "Invesco QQQ Trust",
        "category": "etfs",
        "sector": "Technology",
        "description": "ETF que replica el índice NASDAQ-100",
        "expense_ratio": 0.20,
        "aum": "200B"
    },
    "DIA": {
        "name": "SPDR Dow Jones ETF",
        "category": "etfs",
        "sector": "Broad Market",
        "description": "ETF que replica el índice Dow Jones Industrial Average",
        "expense_ratio": 0.16,
        "aum": "30B"
    },
    "IWM": {
        "name": "iShares Russell 2000 ETF",
        "category": "etfs",
        "sector": "Small Cap",
        "description": "ETF que replica el índice Russell 2000 (small caps)",
        "expense_ratio": 0.19,
        "aum": "60B"
    },
    "GLD": {
        "name": "SPDR Gold Shares",
        "category": "etfs",
        "sector": "Commodities",
        "description": "ETF que replica el precio del oro",
        "expense_ratio": 0.40,
        "aum": "60B"
    },
    "TLT": {
        "name": "iShares 20+ Year Treasury",
        "category": "etfs",
        "sector": "Bonds",
        "description": "ETF de bonos del Tesoro a largo plazo",
        "expense_ratio": 0.15,
        "aum": "40B"
    },
    
    # Indices
    "VIX": {
        "name": "CBOE Volatility Index",
        "category": "indices",
        "sector": "Volatility",
        "description": "Índice de volatilidad del mercado (miedo y codicia)",
        "calculation": "Basado en opciones del S&P 500"
    },
    
    # Cryptocurrencies
    "BTC-USD": {
        "name": "Bitcoin",
        "category": "crypto",
        "sector": "Cryptocurrency",
        "description": "Primera y más grande criptomoneda",
        "market_cap": "800B",
        "circulating_supply": "19.5M"
    },
    "ETH-USD": {
        "name": "Ethereum",
        "category": "crypto",
        "sector": "Cryptocurrency",
        "description": "Plataforma de contratos inteligentes y DeFi",
        "market_cap": "300B",
        "circulating_supply": "120M"
    }
}

# Popular asset combinations for different strategies
ASSET_COMBINATIONS = {
    "tech_leaders": ["AAPL", "GOOGL", "MSFT", "NVDA", "META"],
    "growth_stocks": ["TSLA", "AMZN", "NFLX", "NVDA", "META"],
    "value_stocks": ["AAPL", "GOOGL", "MSFT", "AMZN"],
    "etf_portfolio": ["SPY", "QQQ", "DIA", "IWM", "GLD", "TLT"],
    "crypto_portfolio": ["BTC-USD", "ETH-USD"],
    "defensive": ["SPY", "GLD", "TLT"],
    "aggressive": ["QQQ", "NVDA", "TSLA"]
}

# Asset recommendations by market condition
MARKET_RECOMMENDATIONS = {
    "bull_market": {
        "stocks": ["AAPL", "GOOGL", "MSFT", "NVDA", "TSLA"],
        "etfs": ["SPY", "QQQ"],
        "description": "Mercado alcista - enfoque en crecimiento"
    },
    "bear_market": {
        "stocks": ["AAPL", "GOOGL", "MSFT"],
        "etfs": ["GLD", "TLT"],
        "description": "Mercado bajista - enfoque defensivo"
    },
    "sideways_market": {
        "stocks": ["AAPL", "GOOGL", "MSFT", "AMZN"],
        "etfs": ["SPY", "IWM"],
        "description": "Mercado lateral - diversificación"
    },
    "high_volatility": {
        "stocks": ["AAPL", "GOOGL", "MSFT"],
        "etfs": ["GLD", "TLT"],
        "description": "Alta volatilidad - activos defensivos"
    }
}

def get_asset_info(symbol: str) -> dict:
    """Get complete asset information."""
    return ASSETS_DATABASE.get(symbol, {
        "name": symbol,
        "category": "stocks",
        "sector": "Unknown",
        "description": "Información no disponible"
    })

def get_category_assets(category: str) -> list:
    """Get all assets in a specific category."""
    return [symbol for symbol, info in ASSETS_DATABASE.items() 
            if info["category"] == category]

def get_sector_assets(sector: str) -> list:
    """Get all assets in a specific sector."""
    return [symbol for symbol, info in ASSETS_DATABASE.items() 
            if info["sector"] == sector]

def get_popular_assets(limit: int = 10) -> list:
    """Get most popular assets."""
    return list(ASSETS_DATABASE.keys())[:limit]

def get_recommendations(market_condition: str) -> dict:
    """Get asset recommendations for market condition."""
    return MARKET_RECOMMENDATIONS.get(market_condition, MARKET_RECOMMENDATIONS["sideways_market"]) 