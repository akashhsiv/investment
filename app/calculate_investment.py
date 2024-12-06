import pandas_ta as ta


def calculate_rsi(data, period=14):
    """
    Calculate RSI (Relative Strength Index) using pandas_ta library.
    """
    data["RSI"] = ta.rsi(data["Close"], length=period)
    return data["RSI"].iloc[-1]  # Return the latest RSI value


def adjust_weightage(weightage, rsi):
    """
    Adjust the weightage based on RSI thresholds.
    """
    if rsi > 90:
        return weightage * 0.7
    elif rsi > 80:
        return weightage * 0.8
    elif rsi > 70:
        return weightage * 0.9
    elif rsi < 30:
        return weightage * 1.3
    elif rsi < 20:
        return weightage * 1.2
    elif rsi < 10:
        return weightage * 1.1
    return weightage
