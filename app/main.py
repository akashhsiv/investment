from fastapi import FastAPI, File, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from app.fetch_data import fetch_stock_data
from app.calculate_investment import calculate_investment, calculate_shares
from app.adjust_weightage import adjust_weightage_with_rsi
import pandas as pd
import os

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount the frontend directory
app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")

DATA_FOLDER = "data/"
OUTPUT_FOLDER = "output/"

# Ensure directories exist
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

@app.post("/upload-stocks/")
async def upload_stocks(file: UploadFile = File(...), investment_amount: float = 10000.0, start_date: str = "2024-01-01", end_date: str = "2024-12-31"):
    """
    Upload a CSV file containing stocks and their weightage, and process it.
    """
    # Save the uploaded file
    file_path = os.path.join(DATA_FOLDER, file.filename)
    with open(file_path, "wb") as f:
        f.write(await file.read())

    # Load the CSV file
    stocks = pd.read_csv(file_path)

    # Fetch stock data
    stock_data = {}
    for stock in stocks['stock']:
        stock_data[stock] = fetch_stock_data(stock, start_date, end_date)

    # Calculate investments
    stocks = calculate_investment(stocks, investment_amount)

    # Apply calculations for each stock
    
    final_summary = []
    for stock in stock_data.keys():
        stock_data[stock] = calculate_shares(stock_data[stock], stocks.loc[stocks['stock'] == stock, 'investment'].values[0])
        stock_data[stock] = adjust_weightage_with_rsi(stock_data[stock], stocks.loc[stocks['stock'] == stock, 'weightage'].values[0])

        # Append to final summary
        for date, row in stock_data[stock].iterrows():
            final_summary.append({
                "Date": date,
                "Stock": stock,
                "Closing Price": row['Close'],
                "Shares Bought": row['Shares'],
                "Adjusted Weightage": row['Adjusted Weightage']
            })

    # Save the summary to a CSV file
    summary_df = pd.DataFrame(final_summary)
    output_path = os.path.join(OUTPUT_FOLDER, "investment_summary.csv")
    summary_df.to_csv(output_path, index=False)

    return {"message": "Stocks processed successfully", "summary_file": output_path}


@app.get("/download-summary/")
def download_summary():
    """
    Endpoint to download the generated investment summary CSV file.
    """
    file_path = os.path.join(OUTPUT_FOLDER, "investment_summary.csv")
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="text/csv", filename="investment_summary.csv")
    return {"error": "No summary file found. Please process stocks first."}
