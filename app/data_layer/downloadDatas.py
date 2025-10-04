from .models import Stock, Indicators
from tradingview_ta import TA_Handler, Interval

def get_stock_data(symbol: str, interval=Interval.INTERVAL_4_HOURS):
    # TradingView'den verileri çek
    handler = TA_Handler(
        symbol=symbol,
        screener="turkey",
        exchange="BIST",
        interval=interval
    )
    
    analysis = handler.get_analysis()
    indicators = analysis.indicators
    
    # Pivot Camarilla seviyeleri
    pivot_supports = [
        indicators.get("Pivot.M.Fibonacci.S3"),
        indicators.get("Pivot.M.Fibonacci.S2"),
        indicators.get("Pivot.M.Fibonacci.S1")
    ]
    pivot_resistances = [
        indicators.get("Pivot.M.Fibonacci.R1"),
        indicators.get("Pivot.M.Fibonacci.R2"),
        indicators.get("Pivot.M.Fibonacci.R3")
    ]
    pivot_middle = indicators.get("Pivot.M.Fibonacci.Middle")
    
    # Stock objesi
    stock = Stock(
        symbol=symbol,
        price=indicators.get("close"),
        middle=pivot_middle,
        supports=pivot_supports,
        resistances=pivot_resistances
    )
    
    # Indicators objesi
    ind = Indicators(
        rsi=indicators.get("RSI"),
        rsiPrevious=indicators.get("RSI[1]"),
        stockK=indicators.get("Stoch.K"),
        stockD=indicators.get("Stoch.D"),
        adx = indicators.get("ADX"),
        macd=indicators.get("MACD.macd"),
        macdSignal=indicators.get("MACD.signal"),
        bbLower=indicators.get("BB.lower"),
        bbMiddle=(indicators.get("BB.lower") + indicators.get("BB.upper"))/2,
        bbUpper=indicators.get("BB.upper"),
        ema5=indicators.get("EMA5"),
        ema10=indicators.get("EMA10"),
        sma50=indicators.get("SMA50"),
        sma100=indicators.get("SMA100"),
        sma200=indicators.get("SMA200")
    )
    
    return stock, ind
    # symbol = "THYAO"
    # stock_obj, ind_obj = get_stock_data(symbol)
    # print(stock_obj)
    # print(ind_obj)
    

    
# from tradingview_ta import TA_Handler, Interval, Exchange

# # Örnek parametreler
# symbol = "THYAO"        # İşlem yapmak istediğin hisse
# interval = Interval.INTERVAL_1_DAY  # Günlük veri

# # TradingView'den veri çek
# handler = TA_Handler(
#     symbol=symbol,
#     screener="turkey",
#     exchange="BIST",
#     interval=interval
# )

# analysis = handler.get_analysis()
# indicators = analysis.indicators

# # Gelen değerleri detaylı yazdır
# print("=== TradingView Analizi ===")
# print(f"Sembol: {symbol}")
# print(f"Zaman Aralığı: {interval}")
# print(f"Özet: {analysis.summary}")        # Genel sinyal (Buy, Sell, Neutral)
# print(f"Hareketli Ortalamalar: {analysis.moving_averages}")  
# print(f"Osilatörler: {analysis.oscillators}")
# print("\n--- Detaylı İndikatörler ---")
# for ind, val in indicators.items():
#     print(f"{ind}: {val}")