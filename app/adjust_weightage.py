import pandas_ta as ta


def adjust_weightage_with_rsi(data, initial_weightage):
    """
    Adjust stock weightage dynamically based on RSI for each day.
    """
    data["RSI"] = ta.rsi(data["Close"], length=14)  # Compute RSI

    # Initialize a list to hold adjusted weightages for each row
    adjusted_weightages = []

    for index, row in data.iterrows():
        # Default adjusted weightage is the initial weightage
        adjusted_weightage = initial_weightage

        # Apply adjustments based on RSI thresholds
        if row["RSI"] > 90:
            adjusted_weightage *= 0.7
        elif row["RSI"] > 80:
            adjusted_weightage *= 0.8
        elif row["RSI"] > 70:
            adjusted_weightage *= 0.9
        elif row["RSI"] < 30:
            adjusted_weightage *= 1.3
        elif row["RSI"] < 20:
            adjusted_weightage *= 1.2
        elif row["RSI"] < 10:
            adjusted_weightage *= 1.1

        # Append the adjusted weightage for this row
        adjusted_weightages.append(adjusted_weightage)

    # Add adjusted weightage column to the dataframe
    data["Adjusted Weightage"] = adjusted_weightages
    return data
