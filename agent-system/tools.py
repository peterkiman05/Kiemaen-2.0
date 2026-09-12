import yfinance as yf


def get_live_market_data(symbol: str) -> str:
    try:
        ticker = yf.Ticker(symbol)
        df = ticker.history(period="1d")
        if df.empty:
            return f"No live price data found for symbol: {symbol}"

        latest = df.iloc[-1]
        return (
            f"Live Market Data for {symbol}:\n"
            f"- Open: {latest['Open']:.5f}\n"
            f"- High: {latest['High']:.5f}\n"
            f"- Low: {latest['Low']:.5f}\n"
            f"- Close: {latest['Close']:.5f}\n"
            f"- Volume: {int(latest['Volume'])}"
        )
    except Exception as e:
        return f"Error fetching market data for {symbol}: {str(e)}"
