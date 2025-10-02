import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data_layer.downloadDatas import get_stock_data
from data_layer.models import Stock, Indicators
# symbol = "THYAO"
# stock_obj, ind_obj = get_stock_data(symbol)
# print(stock_obj)
# print(ind_obj)


class TradeRules:
    def __init__(self, stock: Stock, indicators: Indicators):
        self.stock = stock
        self.ind = indicators

    def check_buy_signal_by_indicators(self) -> bool:
        """Alım sinyali koşulları"""
        return (
            self.ind.rsi > self.ind.rsiPrevious and
            self.ind.macd > self.ind.macdSignal and
            self.stock.price > self.ind.ema5 > self.ind.ema10
        )
    def check_buy_signal_by_price(self) -> bool:
        """Fiyata göre alım sinyali (destek seviyesine yakınlık)"""
        if not self.stock.supports:
            return False
        nearest_support = max(self.stock.supports)  # en yakın (en yüksek) destek seviyesi
        return self.stock.price <= nearest_support * 1.005  # %0.5 yakınlık

    def check_sell_signal_by_indicators(self) -> bool:
        """Satım sinyali koşulları"""
        return (
            self.ind.rsi < self.ind.rsiPrevious and
            self.ind.macd < self.ind.macdSignal and
            self.stock.price < self.ind.ema5 < self.ind.ema10
        )
        
    def check_sell_signal_by_price(self) -> bool:
        """Fiyata göre satım sinyali (direnç seviyesine yakınlık)"""
        if not self.stock.resistances:
            return False
        nearest_resistance = min(self.stock.resistances)  # en yakın (en düşük) direnç seviyesi
        return self.stock.price >= nearest_resistance * 0.995  # %0.5 yakınlık

    def check_trend(self) -> str:
        """Trend analizi"""
        if self.stock.price > self.ind.sma200:
            return "Uzun vadeli yükseliş trendi"
        elif self.stock.price < self.ind.sma200:
            return "Uzun vadeli düşüş trendi"
        else:
            return "Nötr"

    def check_signal_by_bollinger(self) -> str:
        """
        Bollinger bantlarına göre sinyal üretir.
        - Fiyat bbLower altındaysa: GÜÇLÜ AL
        - Fiyat bbLower yakınsa (%1): AL
        - Fiyat bbUpper üstündeyse: GÜÇLÜ SAT
        - Fiyat bbUpper yakınsa (%1): SAT
        - Fiyat bbMiddle yakınsa:
            - Altındaysa: SAT
            - Üstündeyse: AL
        - Aksi durumda: False (sinyal yok)
        """
        price = self.stock.price
        lower = self.ind.bbLower
        middle = self.ind.bbMiddle
        upper = self.ind.bbUpper

        # Alt bant kontrolleri
        if price < lower:
            return "GÜÇLÜ AL"
        elif price <= lower * 1.005:
            return "AL"

        # Üst bant kontrolleri
        if price > upper:
            return "GÜÇLÜ SAT"
        elif price >= upper * 0.995:
            return "SAT"

        # Orta bant kontrolleri
        if abs(price - middle) <= middle * 0.005:  # %1 yakınlık
            if price < middle:
                return "SAT"
            elif price > middle:
                return "AL"

        return False

    def summary(self) -> str:
        """Özet rapor (öncelik: indikatörler -> fiyat -> Bollinger -> bekle)"""
        buy_ind = self.check_buy_signal_by_indicators()
        sell_ind = self.check_sell_signal_by_indicators()
        buy_price = self.check_buy_signal_by_price()
        sell_price = self.check_sell_signal_by_price()
        bb_signal = self.check_signal_by_bollinger()  # Yeni eklenen BB fonksiyonu
        trend = self.check_trend()

        if buy_ind:
            return f"{self.stock.symbol}: AL sinyali (indikatörlere göre) - {trend}"
        elif sell_ind:
            return f"{self.stock.symbol}: SAT sinyali (indikatörlere göre) - {trend}"
        elif buy_price:
            return f"{self.stock.symbol}: AL sinyali (fiyata göre) - {trend}"
        elif sell_price:
            return f"{self.stock.symbol}: SAT sinyali (fiyata göre) - {trend}"
        elif bb_signal:
            return f"{self.stock.symbol}: {bb_signal} (Bollinger bantına göre) - {trend}"
        else:
            return f"{self.stock.symbol}: BEKLE - {trend}"

        

import pandas as pd

symbols = ["AEFES", "ALFAS", "ALTNY", "ASTOR", "CIMSA", "DOAS", 
           "EBEBK", "EKGYO", "ENJSA", "FROTO", "GWIND", "ISCTR", 
           "MAVI", "MIATK", "PGSUS", "TCELL", "TTRAK", "TUKAS",
           "TKNSA", "THYAO", "TUPRS", "ULKER"]

results = []


for symbol in symbols:
    
    stock, ind = get_stock_data(symbol)   # Veriyi çek
    rules = TradeRules(stock, ind)        # Kuralları uygula
    
    # Sonucu direkt yazdır
    print(f"{symbol} -> {rules.summary()}")
    time.sleep(5)  # 2 saniye bekleme
