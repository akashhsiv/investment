from fastapi import FastAPI, HTTPException, File, UploadFile
from pydantic import BaseModel
import pandas as pd
import yfinance as yf
from datetime import datetime
from io import StringIO

# FastAPI instance
app = FastAPI()

# Define the input model for the API
class InvestmentRequest(BaseModel):
    total_investment: float
    start_date: str
    end_date: str

# Function to calculate RSI
def calculate_rsi(data, periods=14):
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

# Main function to process the investment data
def process_investment(total_investment, start_date, end_date, stocks):
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

        # Append results with additional investment details
        for index, row in data.iterrows():
            results.append(
                {
                    "Ticker": ticker,
                    "Date": index.date(),
                    "Weightage": weightage,
                    "Adjusted Weightage": row["Adjusted Weightage"],
                    "Open": row["Open"],
                    "Close": row["Close"],
                    "RSI": row["RSI"],
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
    
    return summary

# FastAPI route to handle investment requests
@app.post("/process-investment/")
async def process_investment_endpoint(
    request: InvestmentRequest, 
    file: UploadFile = File(...)
):
    try:
        # Read the CSV file contents
        contents = await file.read()
        csv_string = contents.decode("utf-8")
        # Convert CSV string to pandas DataFrame
        stocks_df = pd.read_csv(StringIO(csv_string))
        
        if 'Ticker' not in stocks_df.columns or 'Weightage' not in stocks_df.columns:
            raise HTTPException(status_code=400, detail="CSV file must contain 'Ticker' and 'Weightage' columns.")
        
        # Convert input dates from string to datetime
        start_date = pd.to_datetime(request.start_date)
        end_date = pd.to_datetime(request.end_date) + pd.Timedelta(days=1)

        if start_date >= end_date:
            raise HTTPException(status_code=400, detail="Start date must be earlier than the end date.")
        
        # Process the investment data
        result_df = process_investment(
            total_investment=request.total_investment,
            start_date=start_date,
            end_date=end_date,
            stocks=stocks_df.to_dict(orient="records")
        )
        
        # Save the summary to CSV
        result_df.to_csv("investment_summary.csv", index=False)
        
        return {"message": "Summary processed successfully", "data": result_df.to_dict(orient="records")}
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run with uvicorn in the command line:
# uvicorn main:app --reload
