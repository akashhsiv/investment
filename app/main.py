import os
import pandas as pd
import yfinance as yf
from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from app.calculate_investment import calculate_rsi, adjust_weightage

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files and templates
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")
templates = Jinja2Templates(directory="frontend/templates")

DATA_FOLDER = "data/"
OUTPUT_FOLDER = "output/"
os.makedirs(DATA_FOLDER, exist_ok=True)
os.makedirs(OUTPUT_FOLDER, exist_ok=True)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    """
    Render the homepage with a form for user input.
    """
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload-stocks/")
async def process_stocks(
    request: Request,
    file: UploadFile = File(...),
    investment_amount: float = 10000.0,
    start_date: str = "2024-01-01",
    end_date: str = "2024-12-31",
):
    """
    Process the uploaded CSV file and calculate investment summaries.
    """
    try:
        # Save the uploaded file
        file_path = os.path.join(DATA_FOLDER, file.filename)
        with open(file_path, "wb") as f:
            f.write(await file.read())

        # Load the CSV into a dataframe
        stocks = pd.read_csv(file_path)

        # Validate CSV content
        if "stock" not in stocks.columns or "weightage" not in stocks.columns:
            return templates.TemplateResponse(
                "index.html",
                {
                    "request": request,
                    "error": "CSV must contain 'stock' and 'weightage' columns.",
                },
            )

        if stocks["weightage"].sum() != 1.0:
            return templates.TemplateResponse(
                "index.html",
                {"request": request, "error": "The sum of weightages must equal 1.0."},
            )

        # Fetch and process stock data
        final_summary = []
        for index, row in stocks.iterrows():
            ticker = row["stock"]
            weightage = row["weightage"]
            stock_investment = investment_amount * weightage

            # Fetch stock data using Yahoo Finance
            stock_data = yf.download(
                ticker, start=start_date, end=end_date, progress=False
            )
            if stock_data.empty:
                return templates.TemplateResponse(
                    "index.html",
                    {"request": request, "error": f"No data found for stock: {ticker}"},
                )

            # Calculate shares for each day
            for date, data in stock_data.iterrows():
                closing_price = data["Close"]
                shares_bought = stock_investment / closing_price
                rsi = calculate_rsi(stock_data)  # Use a function to calculate RSI
                adjusted_weightage = adjust_weightage(weightage, rsi)

                # Add to the final summary
                final_summary.append(
                    {
                        "Ticker": ticker,
                        "Date": date.strftime("%Y-%m-%d"),
                        "Weightage": weightage,
                        "Adjusted Weightage": adjusted_weightage,
                        "Open": data["Open"],
                        "Close": closing_price,
                        "RSI": rsi,
                        "Shares Bought": shares_bought,
                    }
                )

        # Save and render the summary
        summary_df = pd.DataFrame(final_summary)
        output_file = os.path.join(OUTPUT_FOLDER, "investment_summary.csv")
        summary_df.to_csv(output_file, index=False)

        return templates.TemplateResponse(
            "result.html",
            {
                "request": request,
                "summary": final_summary,
                "file_url": f"/static/{output_file}",
            },
        )

    except Exception as e:
        return templates.TemplateResponse(
            "index.html", {"request": request, "error": str(e)}
        )


@app.get("/download-summary/")
async def download_summary():
    """
    Endpoint to download the generated investment summary CSV file.
    """
    file_path = os.path.join(OUTPUT_FOLDER, "investment_summary.csv")
    if os.path.exists(file_path):
        return FileResponse(
            file_path, media_type="text/csv", filename="investment_summary.csv"
        )
    return {"error": "No summary file found. Please process stocks first."}


@app.get("/healthcheck/")
async def healthcheck():
    """
    Endpoint to check the health of the application.
    """
    return {"status": "healthy", "message": "Application is running smoothly."}
