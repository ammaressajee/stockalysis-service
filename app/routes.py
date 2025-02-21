from app.stock_data import *
from flask import jsonify, request, Blueprint
from flask_cors import cross_origin
from app import db
from app.models import Contact
from flask import Flask, request, jsonify
import yfinance as yf



routes = Blueprint("routes", __name__)

@routes.route('/contact', methods=['GET'])
@cross_origin(origins=["http://localhost:4200", "https://d1qfccnfz6gou3.cloudfront.net"], supports_credentials=True)
def get_contacts():
    contacts = Contact.query.all()
    return jsonify([contact.to_dict() for contact in contacts])

@routes.route('/contact', methods=['POST'])
@cross_origin(origins=["http://localhost:4200", "https://d1qfccnfz6gou3.cloudfront.net"], supports_credentials=True)
def create_contact():
    data = request.json
    new_contact = Contact(fname=data["fname"], lname=data["lname"], email=data["email"], message=data["message"], contact_number=data["contact_number"])

    db.session.add(new_contact)
    db.session.commit()

    return jsonify({"message": "Contact saved successfully!"}), 201

@routes.route('/analyze', methods=['GET'])
@cross_origin(origins=["http://localhost:4200", "https://d1qfccnfz6gou3.cloudfront.net"], supports_credentials=True)
def analyze_stock():
    ticker = request.args.get('ticker', '').upper()

    if not ticker:
        return jsonify({"error": "Ticker symbol is required"}), 400

    try:
        df = fetch_stock_data(ticker)

        # Compute indicators
        df['SMA50'] = calculate_sma(df, 50)
        df['SMA200'] = calculate_sma(df, 200)
        df['EMA50'] = calculate_ema(df, 50)
        df['EMA200'] = calculate_ema(df, 200)
        df['RSI'] = calculate_rsi(df)
        calculate_macd(df)
        calculate_bollinger_bands(df)
        fib_levels = calculate_fibonacci_levels(df)
        volume_spike = analyze_volume(df)

        # Get the latest values
        last_close = df['Close'].iloc[-1]
        sma50 = df['SMA50'].iloc[-1]
        sma200 = df['SMA200'].iloc[-1]
        ema50 = df['EMA50'].iloc[-1]
        ema200 = df['EMA200'].iloc[-1]
        rsi = df['RSI'].iloc[-1]
        macd = df['MACD'].iloc[-1]
        signal_line = df['Signal_Line'].iloc[-1]
        upper_band = df['Upper_Band'].iloc[-1]
        lower_band = df['Lower_Band'].iloc[-1]

        # Initialize logging messages
        log = []
        log.append(f"Stock: {ticker}")
        log.append(f"Full Stock Name: {yf.Ticker(ticker).info.get('longName', 'N/A')}")
        log.append(f"Last Close Price: {last_close}")
        log.append(f"50-Day Simple Moving Average (SMA50): {sma50} - Used to gauge short-term trend direction.")
        log.append(f"200-Day Simple Moving Average (SMA200): {sma200} - Used for long-term trend analysis.")
        log.append(f"50-Day Exponential Moving Average (EMA50): {ema50} - Reacts more quickly to price changes.")
        log.append(f"200-Day Exponential Moving Average (EMA200): {ema200} - Provides a smoother long-term trend.")
        log.append(f"Relative Strength Index (RSI): {rsi} - Indicates overbought (>70) or oversold (<30) conditions.")
        log.append(f"MACD Value: {macd} - Measures trend strength and momentum.")
        log.append(f"Signal Line: {signal_line} - Used to detect MACD crossovers for trend confirmation.")
        log.append(f"Upper Bollinger Band: {upper_band} - Acts as a resistance level in an uptrend.")
        log.append(f"Lower Bollinger Band: {lower_band} - Acts as a support level in a downtrend.")
        log.append(f"Fibonacci Levels: {fib_levels} - Identifies potential support and resistance zones.")
        log.append(f"Volume Spike Detected: {volume_spike} - High volume suggests strong buying/selling pressure.")

        # Decision Logic with explanations
        decision = "PASS"
        reason = "No strong buy or sell signals detected."
# Strong Buy (High Confidence)
        if macd > signal_line and rsi < 65 and last_close > sma50:
            if volume_spike:
                decision = "STRONG_BUY"
                reason = ("MACD crossover confirms bullish momentum. RSI is below 65 (not overbought). "
                        "Price is above SMA50, confirming an uptrend. Volume spike adds confidence.")
            else:
                decision = "BUY_CONSIDERATION"
                reason = ("MACD crossover and price above SMA50 suggest an uptrend, but no volume spike. "
                        "Consider waiting for higher volume or further confirmation.")

        # Regular Buy (Moderate Confidence)
        elif macd > signal_line and rsi < 70 and last_close > ema50:
            decision = "BUY"
            reason = ("MACD is above the Signal Line, indicating bullish momentum. "
                    "RSI is below overbought levels, and price is above EMA50, showing upward strength.")

        # Buy Dip (RSI-Based Reversal Play)
        elif macd < signal_line and rsi < 40:
            decision = "BUY_DIP"
            reason = ("RSI near oversold levels (<40) and MACD weakness suggest a potential rebound opportunity.")

        # Trim Position (Reduce Holdings but Don’t Fully Exit)
        elif rsi > 75 or (last_close >= upper_band and rsi > 70):
            decision = "TRIM_POSITION"
            reason = ("RSI is in overbought territory (>75), suggesting potential pullback. "
                    "Consider taking partial profits or monitoring for a reversal.")

        # Full Sell (Confirmed Downtrend)
        elif (sma50 < sma200 or ema50 < ema200) and macd < signal_line:
            decision = "SELL"
            reason = ("SMA50 and EMA50 are below long-term averages, suggesting a weakening trend. "
                    "MACD below Signal Line confirms bearish momentum.")

        # HOLD (No Strong Signals)
        else:
            decision = "HOLD"
            reason = "No strong buy or sell signals detected. Monitor for trend confirmation."

        log.append(f"Decision: {decision} - {reason}")

        return jsonify({
            "ticker": ticker,
            "full_name": yf.Ticker(ticker).info.get('longName', 'N/A'), 
            "last_close_price": last_close,
            "SMA50": sma50,
            "SMA200": sma200,
            "EMA50": ema50,
            "EMA200": ema200,
            "RSI": rsi,
            "MACD": macd,
            "Signal_Line": signal_line,
            "Upper_Bollinger_Band": upper_band,
            "Lower_Bollinger_Band": lower_band,
            "Fibonacci_Levels": fib_levels,
            "Volume_Spike": bool(volume_spike),
            "decision": decision,
            "reason": reason,
            "log": log
        })
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
@routes.route('/predict', methods=['GET'])
@cross_origin(origins=["http://localhost:4200", "https://d1qfccnfz6gou3.cloudfront.net"], supports_credentials=True)
def predict_price():
    # Extract query parameters
    ticker = request.args.get('ticker')
    days = request.args.get('days', type=int)

    # Validate input
    if not ticker or not days:
        return jsonify({"error": "Missing required parameters 'ticker' or 'days'"}), 400

    # Call your prediction function
    predictions = predict_stock_price(ticker, days)

    # Convert DataFrame to JSON response
    return predictions.to_json(orient="records")
