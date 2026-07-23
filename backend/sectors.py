# GICS 11 sectors mapped to their SPDR Select Sector ETF, with approximate
# S&P 500 sector market-cap weights (updated periodically) used to compute
# the confidence-weighted overall market score.

SECTORS = [
    "Technology",
    "Healthcare",
    "Financials",
    "Consumer Discretionary",
    "Communication Services",
    "Industrials",
    "Consumer Staples",
    "Energy",
    "Utilities",
    "Real Estate",
    "Materials",
]

SECTOR_ETF = {
    "Technology": "XLK",
    "Healthcare": "XLV",
    "Financials": "XLF",
    "Consumer Discretionary": "XLY",
    "Communication Services": "XLC",
    "Industrials": "XLI",
    "Consumer Staples": "XLP",
    "Energy": "XLE",
    "Utilities": "XLU",
    "Real Estate": "XLRE",
    "Materials": "XLB",
}

# Approximate S&P 500 sector weights (%), used to weight the overall market
# score. These drift over time; close enough for a directional composite.
SECTOR_WEIGHT = {
    "Technology": 32.0,
    "Healthcare": 10.5,
    "Financials": 13.5,
    "Consumer Discretionary": 10.5,
    "Communication Services": 9.5,
    "Industrials": 8.5,
    "Consumer Staples": 5.5,
    "Energy": 3.5,
    "Utilities": 2.5,
    "Real Estate": 2.0,
    "Materials": 2.0,
}
