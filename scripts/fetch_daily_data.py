import yfinance as yf
import sqlite3
import os
from datetime import datetime, timedelta

# Set up the path to the database
DB_PATH = os.path.join("data", "sp500.db")

# Ensure the data directory exists
os.makedirs("data", exist_ok=True)

# Connect to the SQLite database
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Create the table if it doesn't exist
c.execute("""
CREATE TABLE IF NOT EXISTS sp500_gaps (
    date TEXT PRIMARY KEY,
    previous_close REAL,
    open REAL,
    gap_size REAL,
    gap_type TEXT,
    gap_filled INTEGER,
    filled_time TEXT
);
""")

# Get the most recent date in the database
c.execute("SELECT MAX(date) FROM sp500_gaps")
result = c.fetchone()
last_date = result[0]

if last_date:
    print(f"Last recorded date: {last_date}")
    start_date = (datetime.strptime(last_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
else:
    print("No existing data found. Fetching 5 years of SPY data...")
    start_date = (datetime.today() - timedelta(days=5*365)).strftime("%Y-%m-%d")

# Download historical SPY data from the appropriate start date
spy = yf.Ticker("SPY")
hist = spy.history(start=start_date)

print(f"Fetched {len(hist)} rows of daily data starting from {start_date}.")

# Iterate through data and insert into DB
for i in range(1, len(hist)):
    today = hist.iloc[i]
    prev = hist.iloc[i - 1]

    date = today.name.strftime("%Y-%m-%d")
    previous_close = round(prev["Close"], 2)
    open_price = round(today["Open"], 2)
    gap_size = round(open_price - previous_close, 2)
    
    if gap_size > 0:
        gap_type = "up"
    elif gap_size < 0:
        gap_type = "down"
    else:
        gap_type = "none"

    # Insert or ignore if the date already exists
    c.execute("""
        INSERT OR IGNORE INTO sp500_gaps
        (date, previous_close, open, gap_size, gap_type, gap_filled, filled_time)
        VALUES (?, ?, ?, ?, ?, NULL, NULL)
    """, (date, previous_close, open_price, gap_size, gap_type))

# Commit and close
conn.commit()
conn.close()

print("Data written to database successfully.")
