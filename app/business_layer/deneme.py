import sys
import os
# "uygulama" klasörünü path'e ekle
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from data_layer.downloadDatas import get_stock_data

symbol = "THYAO"
stock_obj, ind_obj = get_stock_data(symbol)
print(stock_obj)
print(ind_obj)
