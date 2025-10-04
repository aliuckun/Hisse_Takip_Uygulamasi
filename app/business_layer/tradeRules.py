import sys
import os
import time
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data_layer.downloadDatas import get_stock_data
from data_layer.models import Stock, Indicators

class TradeRules:
    def __init__(self, stock: Stock, indicators: Indicators):
        self.stock = stock
        self.ind = indicators
        self.signalPower = 0  # sinyal gücü (pozitifse alım baskısı, negatifse satım baskısı)
        self.signalType = []  # hangi sinyaller geldi

    def check_buy_signal_by_indicators(self) -> bool:
        """Alım sinyali koşulları"""
        if (
            self.ind.rsi > self.ind.rsiPrevious and
            self.ind.macd > self.ind.macdSignal and
            self.stock.price > self.ind.ema5 > self.ind.ema10
        ):
            self.signalPower += 1
            self.signalType.append("AL: Indikatör (rsi + macd + ema5*10)")
            return True
        return False

    def check_buy_signal_by_price(self) -> bool:
        """Fiyata göre alım sinyali (destek seviyesine yakınlık)"""
        if not self.stock.supports:
            return False
        nearest_support = max([s for s in self.stock.supports if s <= self.stock.price], default=None)
        if nearest_support is None:
            return False  # uygun destek bulunamadı
        if self.stock.price <= nearest_support * 1.005:
            self.signalPower += 1
            self.signalType.append("AL: Fiyat/Destek/tradingviewFibIndikator)")
            return True
        return False

    def check_sell_signal_by_indicators(self) -> bool:
        """Satım sinyali koşulları"""
        if (
            self.ind.rsi < self.ind.rsiPrevious and
            self.ind.macd < self.ind.macdSignal and
            self.stock.price < self.ind.ema5 < self.ind.ema10
        ):
            self.signalPower -= 1
            self.signalType.append("SAT: Indikatör (rsi + macd + ema5*10)")
            return True
        return False

    def check_sell_signal_by_price(self) -> bool:
        """Fiyata göre satım sinyali (direnç seviyesine )"""
        if not self.stock.resistances:
            return False
        nearest_resistance = min([r for r in self.stock.resistances if r >= self.stock.price], default=None)
        if nearest_resistance is None:
            return False  # uygun destek bulunamadı
        if self.stock.price >= nearest_resistance * 0.995:
            self.signalPower -= 1
            self.signalType.append("SAT: Fiyat/Direnc/tradingviewFibIndikator")
            return True
        return False

    def check_trend(self) -> str:
        """Trend analizi"""
        #fiyat sma altında ve adx az sa, fiyqat üstünde ve adx fazlaysa, 
        if self.stock.price > self.ind.sma200 and self.ind.adx >24:
            return "AL: Uzun vadeli yükseliş trendi, (price > sma ve adx >24)"
        elif self.stock.price < self.ind.sma200 and self.ind.adx < 14:
            return "AL: Uzun vadeli yükselis trendi baslangic (price < sma ve adx < 14)"
        elif self.stock.price < self.ind.sma200 and self.ind.adx > 36:
            return "AL: Kisa vadeli yükselis trendi, fiyat sismis (price < sma ve adx > 35)"
        elif self.stock.price > self.ind.sma200 and self.ind.adx > 36:
            return "SAT: Kisa vadeli dusus trendi, fiyat sismis (price > sma ve adx >36)"
        elif self.stock.price > self.ind.sma200 and self.ind.adx < 14:
            return "SAT: Uzun vadeli dusus trendi baslangici(price > sma ve adx <14)"
        else:
            return "Nötr"

    def check_signal_by_bollinger(self) -> str:
        """Bollinger bantlarına göre sinyal üretir."""
        price = self.stock.price
        lower = self.ind.bbLower
        middle = self.ind.bbMiddle
        upper = self.ind.bbUpper

        if price < lower:
            self.signalPower += 2
            self.signalType.append("GÜÇLÜ AL: Bollinger")
            return "GÜÇLÜ AL"
        elif price <= lower * 1.007:
            self.signalPower += 1
            self.signalType.append("AL: Bollinger")
            return "AL"

        if price > upper:
            self.signalPower -= 2
            self.signalType.append("GÜÇLÜ SAT: Bollinger")
            return "GÜÇLÜ SAT"
        elif price >= upper * 0.993:
            self.signalPower -= 1
            self.signalType.append("SAT: Bollinger")
            return "SAT"

        if abs(price - middle) <= middle * 0.005:
            if price < middle:
                self.signalPower -= 1
                self.signalType.append("SAT: Bollinger")
                return "SAT"
            elif price > middle:
                self.signalPower += 1
                self.signalType.append("AL: Bollinger")
                return "AL"

        return False

    def summary(self) -> str:
        """Özet rapor (puanlama + sinyaller)"""
        # Reset puanlar
        self.signalPower = 0
        self.signalType = []

        # Sinyalleri kontrol et
        self.check_buy_signal_by_indicators()
        self.check_sell_signal_by_indicators()
        self.check_buy_signal_by_price()
        self.check_sell_signal_by_price()
        bb_signal = self.check_signal_by_bollinger()
        trend = self.check_trend()

        # Sonuç
        if self.signalPower > 0:
            return f"{self.stock.symbol}: AL sinyali | Güç: {self.signalPower} | Kaynaklar: {', '.join(self.signalType)} | Trend: {trend}"
        elif self.signalPower < 0:
            return f"{self.stock.symbol}: SAT sinyali | Güç: {self.signalPower} | Kaynaklar: {', '.join(self.signalType)} | Trend: {trend}"
        else:
            return f"{self.stock.symbol}: BEKLE | Trend: {trend}"


import pandas as pd

symbols = ["AEFES", "ALFAS", "ALTNY", "ASTOR", "CIMSA", "DOAS", 
           "EBEBK", "EKGYO", "ENJSA", "FROTO", "GWIND", "ISCTR", 
           "MAVI", "MIATK", "PGSUS", "TCELL", "TTRAK", "TUKAS",
           "TKNSA", "THYAO", "TUPRS", "ULKER"]


results = []


# for symbol in symbols:
    
#     stock, ind = get_stock_data(symbol)   # Veriyi çek
#     rules = TradeRules(stock, ind)        # Kuralları uygula
    
#     # Sonucu direkt yazdır
#     print(f"{symbol} -> {rules.summary()}")
#     time.sleep(5)  # 2 saniye bekleme



from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet
import datetime

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Table, TableStyle, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import datetime
import re

def colorize_text(text):
    """
    Metin içindeki AL ve SAT kelimelerini renkli yapar.
    AL -> yeşil, SAT -> kırmızı
    """
    if not text:
        return "-"
    # AL kelimesi
    text = re.sub(r"\bAL\b", "<font color='green'><b>AL</b></font>", text)
    # SAT kelimesi
    text = re.sub(r"\bSAT\b", "<font color='red'><b>SAT</b></font>", text)
    return text

def create_stock_report(results, filename="stock_report.pdf"):
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()
    normal = styles["Normal"]
    normal.fontSize = 10
    normal.leading = 13
    heading = styles["Heading2"]

    elements = []

    # Başlık
    title = Paragraph("<b>📊 Günlük Teknik Analiz Raporu</b>", styles["Title"])
    date = Paragraph(f"Tarih: {datetime.datetime.now().strftime('%d.%m.%Y %H:%M:%S')}", normal)
    elements += [title, date, Spacer(1, 12)]

    # Güce göre sıralama
    results = sorted(results, key=lambda x: x["power"] if x["power"] is not None else -999, reverse=True)

    for result in results:
        stock = result["symbol"]
        signal = result["signal"]
        power = result["power"]
        trend = colorize_text(result["trend"])
        details = colorize_text(result["details"])

        # Sinyal rengi
        if signal == "AL":
            signal_color = "green"
        elif signal == "SAT":
            signal_color = "red"
        else:
            signal_color = "gray"

        elements.append(Paragraph(f"<b>{stock}</b>", heading))

        # Hücreleri Paragraph ile HTML biçimlendirme
        data = [
            [Paragraph("<b>Sinyal</b>", normal),
             Paragraph(f"<font color='{signal_color}'><b>{signal}</b></font>", normal)],
            [Paragraph("<b>Güç</b>", normal),
             Paragraph(f"<b>{power}</b>", normal)],
            [Paragraph("<b>Trend</b>", normal),
             Paragraph(trend, normal)],
            [Paragraph("<b>Kaynaklar</b>", normal),
             Paragraph(details, normal)],
        ]

        table = Table(data, colWidths=[80, 400])
        table.setStyle(TableStyle([
            ("BOX", (0, 0), (-1, -1), 0.6, colors.grey),
            ("INNERGRID", (0, 0), (-1, -1), 0.25, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND", (0, 0), (0, -1), colors.whitesmoke),
            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ]))
        elements += [table, Spacer(1, 12)]

    # Özet
    total_stocks = len(results)
    buy_count = sum(1 for r in results if r["signal"] == "AL")
    sell_count = sum(1 for r in results if r["signal"] == "SAT")
    neutral_count = total_stocks - buy_count - sell_count

    summary_text = (
        f"<b>Toplam Hisse:</b> {total_stocks} | "
        f"<font color='green'><b>AL:</b></font> {buy_count} | "
        f"<font color='red'><b>SAT:</b></font> {sell_count} | "
        f"<b>BEKLE:</b> {neutral_count}"
    )
    elements.append(Spacer(1, 20))
    elements.append(Paragraph(summary_text, ParagraphStyle("Summary", fontSize=11, leading=14)))

    doc.build(elements)
    print(f"✅ PDF raporu oluşturuldu: {filename}")



results = []

for symbol in symbols:
    stock, ind = get_stock_data(symbol)
    rules = TradeRules(stock, ind)
    summary = rules.summary()

    results.append({
        "symbol": symbol,
        "signal": "AL" if rules.signalPower > 0 else "SAT" if rules.signalPower < 0 else "BEKLE",
        "power": rules.signalPower,
        "trend": rules.check_trend(),
        "details": ", ".join(rules.signalType)
    })
    
results.sort(key=lambda x: x["power"], reverse=True)

# Şu anki tarih ve saat
now = datetime.datetime.now()
# Örneğin: 04_10_2025_15_30_45
timestamp = now.strftime("%d_%m_%Y_%H_%M_%S")

# Dinamik dosya adı
filename = f"stock_report_{timestamp}.pdf"

# PDF oluştur
create_stock_report(results, filename=filename)


