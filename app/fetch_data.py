import yfinance as yf

def fetch_stock_data(stock, start_date, end_date):
    """
    Fetch daily stock data (OHLCV) from Yahoo Finance.
    """
    return yf.download(stock, start=start_date, end=end_date)
