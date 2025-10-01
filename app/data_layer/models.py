from dataclasses import dataclass, field
from typing import List

@dataclass
class Stock:
    symbol: str
    price: float
    middle: float
    supports: List[float] = field(default_factory=list)  # Destek seviyeleri
    resistances: List[float] = field(default_factory=list)  # Direnç seviyeleri
    

@dataclass
class Indicators:
    rsi: float
    rsiPrevious: float
    stockK: float
    stockD: float
    macd: float
    macdSignal: float
    bbLower: float
    bbMiddle: float
    bbUpper: float
    ema5: float
    ema10: float
    sma50: float
    sma100: float
    sma200: float
    

