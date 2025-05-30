gap-fill-analysis/
├── data/
│   └── sp500.db              # SQLite database file (auto-generated)
├── scripts/
│   ├── fetch_prices.py       # Gets daily SPY data from Polygon
│   ├── detect_gaps.py        # Analyzes if there's a gap today
│   ├── check_fill.py         # Analyzes intraday data to see if gap filled
│   └── utils.py              # Shared helper functions
├── queries/
│   └── reports.sql           # SQL scripts to generate summary reports
├── .github/
│   └── workflows/
│       └── daily.yml         # GitHub Action to run daily at 22:30
├── .gitignore
├── requirements.txt
├── README.md
└── config.json 