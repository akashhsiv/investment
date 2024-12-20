import pandas as pd
import yfinance as yf

# Get user inputs
try:
    total_investment = float(input("Enter the total investment amount (e.g., 100000): "))
    start_date = input("Enter the start date in YYYY-MM-DD format (e.g., 2024-05-01): ")
    end_date = input("Enter the end date in YYYY-MM-DD format (e.g., 2024-05-30): ")

    # Validate date inputs
    start_date = pd.to_datetime(start_date)
    end_date = pd.to_datetime(end_date) + pd.Timedelta(days=1)

    if start_date >= end_date:
        raise ValueError("Start date must be earlier than the end date.")

except ValueError as e:
    print(f"Input error: {e}")
    exit(1)

# Load stock data from CSV file
try:
    stocks_df = pd.read_csv('data/Stocks.csv')  # Assuming your CSV file is named 'stocks.csv'
    if 'Ticker' not in stocks_df.columns or 'Weightage' not in stocks_df.columns:
        raise ValueError("CSV file must contain 'Ticker' and 'Weightage' columns.")
    stocks = stocks_df.to_dict(orient='records')  # Convert the DataFrame into a list of dictionaries
except Exception as e:
    print(f"Error reading CSV file: {e}")
    exit(1)


# Function to calculate RSI
def calculate_rsi(data, periods=14):
    """
    Calculates the Relative Strength Index (RSI) for a given DataFrame.

    Args:
        data: pandas DataFrame containing the 'Close' price data.
        periods: Number of periods for RSI calculation (default: 14).

    Returns:
        pandas Series containing the RSI values.
    """
    delta = data["Close"].diff()
    gain = delta.where(delta > 0, 0).fillna(0)
    loss = (-delta.where(delta < 0, 0)).fillna(0)

    avg_gain = gain.rolling(window=periods).mean()
    avg_loss = loss.rolling(window=periods).mean()

    rs = avg_gain / avg_loss
    rsi = 100 - (100 / (1 + rs))

    return rsi

# Adjust weightage based on RSI
def adjust_weightage_by_rsi(weightage, rsi):
    if rsi > 90:
        return weightage - 0.003
    elif rsi > 80:
        return weightage - 0.002
    elif rsi > 70:
        return weightage - 0.001
    elif rsi < 20:
        return weightage + 0.003
    elif rsi < 30:
        return weightage + 0.002
    elif rsi <= 70:
        return weightage + 0.001
    return weightage

# Adjusted start date for RSI calculation
adjusted_start_date = start_date - pd.Timedelta(days=24)

# Daily investment (total investment divided by the number of days)
total_days = (end_date - start_date).days + 1
daily_investment = total_investment / total_days

# Results list for investment details
results = []

# Dictionary to store RSI data for all stocks
all_rsi = {}
for stock in stocks:
    ticker = stock["Ticker"]
    data = yf.download(ticker, start=adjusted_start_date, end=end_date)
    if data.empty:
        print(f"No data available for {ticker}. Skipping.")
        continue
    data["RSI"] = calculate_rsi(data, periods=14)
    all_rsi[ticker] = data[data.index >= start_date]

# Process each stock
for stock in stocks:
    ticker = stock["Ticker"]
    weightage = stock["Weightage"]

    if ticker not in all_rsi or all_rsi[ticker].empty:
        print(f"Data for {ticker} is not available. Skipping.")
        continue

    data = all_rsi[ticker]

    # Adjust weightage dynamically
    data["Adjusted Weightage"] = data["RSI"].apply(
        lambda x: adjust_weightage_by_rsi(weightage, x)
    )

    # Daily allocated investment (based on daily_investment)

    

    # Append results with additional investment details
    for index, row in data.iterrows():
        results.append(
            {
                "Ticker": ticker,
                "Date": index.date(),
                "Weightage": weightage,
                "Adjusted Weightage": row["Adjusted Weightage"].iloc[0],
                "Open": row["Open"].iloc[0],
                "Close": row["Close"].iloc[0],
                "RSI": row["RSI"].iloc[0],
            }
        )

# Convert results to DataFrame
summary = pd.DataFrame(results)

# Reorder and display columns
columns = [
    "Ticker",
    "Date",
    "Weightage",
    "Adjusted Weightage",
    "Open",
    "Close",
    "RSI",
]
summary = summary[columns]
# Calculate the sum of "Allocated Investment"
# Save the summary to CSV
summary.to_csv("investment_summarytst.csv", index=False)

print("\nSummary saved to 'investment_summarytst.csv'")
