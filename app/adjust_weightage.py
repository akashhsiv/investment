import pandas_ta as ta

def adjust_weightage_with_rsi(data, initial_weightage):
    """
    Adjust stock weightage dynamically based on RSI.
    """
    data['RSI'] = ta.rsi(data['Close'], length=14)  # Compute RSI
    adjusted_weightage = initial_weightage

    for index, row in data.iterrows():
        if row['RSI'] > 90:
            adjusted_weightage *= 0.7
        elif row['RSI'] > 80:
            adjusted_weightage *= 0.8
        elif row['RSI'] > 70:
            adjusted_weightage *= 0.9
        elif row['RSI'] < 30:
            adjusted_weightage *= 1.3
        elif row['RSI'] < 20:
            adjusted_weightage *= 1.2
        elif row['RSI'] < 10:
            adjusted_weightage *= 1.1

    data['Adjusted Weightage'] = adjusted_weightage
    return data
