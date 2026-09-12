import urllib.request
import json


class MarketEngine:
    @staticmethod
    def analyze_live_market(symbol: str, timeframe: str):
        try:
            sym = symbol.upper().strip()

            # Map common trading symbols to Yahoo Finance tickers correctly
            if sym == "XAUUSD" or sym == "GOLD":
                ticker_symbol = "GC=F"
            elif "BTC" in sym or "ETH" in sym:
                ticker_symbol = sym if "-" in sym else f"{sym}-USD"
            else:
                # Forex pairs (e.g. EURUSD -> EURUSD=X)
                clean_sym = sym.replace("=", "").replace("-", "")
                ticker_symbol = f"{clean_sym}=X"

            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker_symbol}?interval=1d"

            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})

            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read().decode())
                result = data["chart"]["result"][0]
                current_price = result["meta"]["regularMarketPrice"]

            tf = timeframe.lower()
            if "m" in tf:
                sl_distance = current_price * 0.002
                tp_distance = sl_distance * 2.0
            elif "h" in tf:
                sl_distance = current_price * 0.006
                tp_distance = sl_distance * 2.5
            else:
                sl_distance = current_price * 0.015
                tp_distance = sl_distance * 3.0

            buy_sl = round(current_price - sl_distance, 4)
            buy_tp1 = round(current_price + tp_distance, 4)
            buy_tp2 = round(current_price + (tp_distance * 1.5), 4)

            sell_sl = round(current_price + sl_distance, 4)
            sell_tp1 = round(current_price - tp_distance, 4)
            sell_tp2 = round(current_price - (tp_distance * 1.5), 4)

            return {
                "symbol": symbol.upper(),
                "timeframe": timeframe.upper(),
                "current_price": round(current_price, 4),
                "buy_setup": {"sl": buy_sl, "tp1": buy_tp1, "tp2": buy_tp2},
                "sell_setup": {"sl": sell_sl, "tp1": sell_tp1, "tp2": sell_tp2},
            }
        except Exception as e:
            return {"error": f"Could not fetch live price: {str(e)}"}
