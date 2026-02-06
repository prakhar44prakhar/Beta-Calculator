import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

st.set_page_config(page_title="Professional Beta Tool", layout="wide")
st.title("📊 Universal Beta Calculator")
st.caption("Enter exact Yahoo Finance tickers (e.g., RELIANCE.NS, AAPL, TSLA, ^NSEI)")

# Sidebar for Dates and Benchmark
st.sidebar.header("Configuration")
start_date = st.sidebar.date_input("Start Date", datetime.now() - timedelta(days=730))
end_date = st.sidebar.date_input("End Date", datetime.now())

# Inputs
benchmark = st.sidebar.text_input("Benchmark Ticker", "^NSEI")
target_stock = st.text_input("Target Stock Ticker", "RELIANCE.NS")

if st.button("Analyze Risk & Beta"):
    with st.spinner(f"Downloading {target_stock} and {benchmark}..."):
        # 1. Download data
        # We download both together to ensure the timeline matches
        data = yf.download([target_stock, benchmark], start=start_date, end=end_date, auto_adjust=True)
        
        if not data.empty and 'Close' in data:
            # 2. Handle missing dates (Holidays/Weekends)
            # ffill() carries the last known price forward
            prices = data['Close'].ffill().dropna()
            
            # Check if both columns exist in the result
            if target_stock in prices.columns and benchmark in prices.columns:
                # 3. Calculate Daily Returns
                returns = prices.pct_change().dropna()
                
                # 4. Beta Calculation (Covariance / Benchmark Variance)
                cov_matrix = np.cov(returns[target_stock], returns[benchmark])
                beta = cov_matrix[0, 1] / cov_matrix[1, 1]
                
                # 5. Display Results
                col1, col2 = st.columns(2)
                col1.metric("Calculated Beta", round(beta, 2))
                
                # Annualized Volatility
                vol = returns[target_stock].std() * np.sqrt(252)
                col2.metric("Annualized Volatility", f"{round(vol*100, 2)}%")
                
                # 6. Comparison Chart (Normalized to 100)
                st.subheader("Performance Comparison")
                normalized_df = (prices / prices.iloc[0]) * 100
                st.line_chart(normalized_df)
                
            else:
                st.error(f"One of the tickers ({target_stock} or {benchmark}) returned no data. Check the spelling on Yahoo Finance.")
        else:
            st.error("No data found for the selected date range.")