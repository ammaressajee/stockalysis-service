import yfinance as yf
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from tvDatafeed import TvDatafeed, Interval

def fetch_colombo_stock_data(ticker):
    # Initialize TradingView datafeed (no login required for public data)
    tv = TvDatafeed()

    # Fetch the last 40 days of historical data from CSE
    df = tv.get_hist(symbol=ticker, exchange="CSELK", interval=Interval.in_daily, n_bars=500)

    if df is None or df.empty:
        print(f"No data found for {ticker}. Check if the symbol is correct.")
        return None

    # Rename columns to match yfinance format
    df.rename(columns={
        "open": "Open",
        "high": "High",
        "low": "Low",
        "close": "Close",
        "volume": "Volume"
    }, inplace=True)

    # Convert index to datetime (TradingView returns it as DateTimeIndex already)
    df.index = pd.to_datetime(df.index)

    # Ensure numerical columns are in float format
    df = df.astype({"Open": float, "High": float, "Low": float, "Close": float, "Volume": float})

    # Add missing columns to match yfinance (set as NaN or 0)
    df["Dividends"] = 0.0
    df["Stock Splits"] = 0.0

    print(df.head())  # Preview the formatted data
    return df

def fetch_us_stock_data(ticker):
    """Fetches historical stock data for the given ticker."""
    stock = yf.Ticker(ticker)
    df = stock.history(period="2y")  # Get last 2 years of data
    return df

def calculate_sma(df, period):
    """Calculates Simple Moving Average (SMA)."""
    return df['Close'].rolling(window=period).mean()

def calculate_ema(df, period):
    """Calculates Exponential Moving Average (EMA)."""
    return df['Close'].ewm(span=period, adjust=False).mean()

def calculate_rsi(df, period=14):
    """Calculates the Relative Strength Index (RSI)."""
    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calculate_macd(df):
    """Calculates MACD (12-day EMA - 26-day EMA) and Signal Line (9-day EMA of MACD)."""
    short_ema = df['Close'].ewm(span=12, adjust=False).mean()
    long_ema = df['Close'].ewm(span=26, adjust=False).mean()
    df['MACD'] = short_ema - long_ema
    df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()

def calculate_bollinger_bands(df, period=20):
    """Calculates Bollinger Bands (Upper, Lower, and Middle Band)."""
    df['SMA20'] = df['Close'].rolling(window=period).mean()
    df['STD20'] = df['Close'].rolling(window=period).std()
    df['Upper_Band'] = df['SMA20'] + (df['STD20'] * 2)
    df['Lower_Band'] = df['SMA20'] - (df['STD20'] * 2)

def calculate_fibonacci_levels(df):
    """Calculates Fibonacci retracement levels based on the last 6 months high and low."""
    recent_data = df[-126:]  # 126 trading days ≈ 6 months
    high = recent_data['Close'].max()
    low = recent_data['Close'].min()

    levels = {
        "23.6%": high - (0.236 * (high - low)),
        "38.2%": high - (0.382 * (high - low)),
        "50.0%": high - (0.5 * (high - low)),
        "61.8%": high - (0.618 * (high - low)),
    }
    return levels

def analyze_volume(df):
    """Checks if the current trading volume is significantly higher than the 50-day average."""
    avg_volume = df['Volume'].rolling(window=50).mean()
    return df['Volume'].iloc[-1] > avg_volume.iloc[-1] * 1.5  # 50% above average volume

def predict_stock_price(ticker, days_ahead):
    """Predicts stock price using a simple linear regression model based on historical closing prices."""
    df = fetch_stock_data(ticker)  # Fetch 2 years of stock data

    # Prepare data for linear regression
    df['Days'] = np.arange(len(df))  # Convert date index into numerical format
    X = df[['Days']]  # Independent variable
    y = df['Close']   # Dependent variable (price)

    # Train linear regression model
    model = LinearRegression()
    model.fit(X, y)

    # Predict future prices
    future_days = np.array([[df['Days'].max() + i] for i in range(1, days_ahead + 1)])
    predictions = model.predict(future_days)

    # Return predictions as DataFrame
    future_dates = pd.date_range(start=df.index[-1], periods=days_ahead + 1, freq='B')[1:]  # Business days only
    return pd.DataFrame({'Date': future_dates, 'Predicted_Close': predictions})