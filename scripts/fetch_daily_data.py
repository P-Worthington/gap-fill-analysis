import os
import requests
from datetime import datetime, timedelta
from dotenv import load_dotenv

# Load environment variables from .env file (e.g., your API key)
load_dotenv()

# Alpha Vantage API setup
API_KEY = os.getenv("ALPHA_VANTAGE_API_KEY")
SYMBOL = "SPY"  # We're using the SPY ETF as a proxy for the S&P 500
API_URL = "https://www.alphavantage.co/query"

def get_daily_data():
    # Define API parameters to get daily time series (last 100 days)
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": SYMBOL,
        "apikey": API_KEY,
        "outputsize": "compact"  # only returns recent ~100 data points
    }

    # Make the API request
    response = requests.get(API_URL, params=params)
    data = response.json()

    # Extract the daily prices dictionary
    time_series = data.get("Time Series (Daily)", {})
    if not time_series:
        raise Exception("Failed to fetch daily time series data.")

    # Get the most recent two trading dates (sorted in reverse chronological order)
    dates = sorted(time_series.keys(), reverse=True)
    if len(dates) < 2:
        raise Exception("Not enough data to calculate gap.")

    today_str, yesterday_str = dates[0], dates[1]

    # Extract today’s open and yesterday’s close
    today_open = float(time_series[today_str]["1. open"])
    previous_close = float(time_series[yesterday_str]["4. close"])

    # Determine the gap type
    if today_open > previous_close:
        gap_type = "up"
    elif today_open < previous_close:
        gap_type = "down"
    else:
        gap_type = "none"

    # Return all relevant data
    return {
        "date": today_str,
        "previous_close": previous_close,
        "open": today_open,
        "gap_type": gap_type
    }

# If this script is run directly, fetch and print the gap data
if __name__ == "__main__":
    gap_info = get_daily_data()
    print("Gap Data:")
    for k, v in gap_info.items():
        print(f"{k}: {v}")