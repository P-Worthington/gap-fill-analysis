import yfinance as yf
import sqlite3
import os
from datetime import datetime, timedelta

# Set up the path to the database
DB_PATH = os.path.join("data", "sp500.db")

# Connect to the SQLite database
conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# Fetch all rows where gap_filled is still NULL
c.execute("SELECT date, previous_close, gap_type FROM sp500_gaps WHERE gap_filled IS NULL")
rows = c.fetchall()

print(f"Analyzing {len(rows)} gaps...")

for row in rows:
    date_str, prev_close, gap_type = row
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    next_day = date_obj + timedelta(days=1)

    # Fetch 1-day data for that trading day
    spy = yf.Ticker("SPY")
    daily_data = spy.history(interval="1d", start=date_str, end=(next_day + timedelta(days=1)).strftime("%Y-%m-%d"))

    if daily_data.empty:
        print(f"No daily data for {date_str}.")
        continue

    day_data = daily_data.loc[date_str] if date_str in daily_data.index else daily_data.iloc[0]
    day_high = day_data["High"]
    day_low = day_data["Low"]

    gap_filled = 0
    filled_time = None

    if gap_type == "up" and day_low <= prev_close:
        gap_filled = 1
    elif gap_type == "down" and day_high >= prev_close:
        gap_filled = 1

    # If gap filled and it's recent (within 60 days), try to get exact time from 5m intraday data
    if gap_filled:
        if (datetime.today() - date_obj).days <= 60:
            intraday = spy.history(interval="5m", start=date_str, end=next_day.strftime("%Y-%m-%d"))
            for ts, bar in intraday.iterrows():
                if gap_type == "up" and bar["Low"] <= prev_close:
                    filled_time = ts.strftime("%H:%M")
                    break
                elif gap_type == "down" and bar["High"] >= prev_close:
                    filled_time = ts.strftime("%H:%M")
                    break
        else:
            filled_time = "UNKNOWN"

    # Update the database
    c.execute("""
        UPDATE sp500_gaps
        SET gap_filled = ?, filled_time = ?
        WHERE date = ?
    """, (gap_filled, filled_time, date_str))

    print(f"{date_str}: gap {'filled' if gap_filled else 'not filled'}{' at ' + filled_time if filled_time else ''}.")

conn.commit()
conn.close()

print("Gap analysis complete.")