import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="Quotex Analyzer",
    page_icon="📈",
    layout="wide"
)

PAIRS = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X",
    "USD/CAD": "CAD=X",
    "EUR/JPY": "EURJPY=X"
}

# --------------------
# INDICATORS
# --------------------

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def rsi(close, period=14):
    delta = close.diff()

    gain = delta.where(delta > 0, 0)
    loss = -delta.where(delta < 0, 0)

    avg_gain = gain.rolling(period).mean()
    avg_loss = loss.rolling(period).mean()

    rs = avg_gain / avg_loss

    return 100 - (100 / (1 + rs))

def macd(close):
    ema12 = ema(close, 12)
    ema26 = ema(close, 26)

    line = ema12 - ema26
    signal = line.ewm(span=9, adjust=False).mean()

    return line, signal

def atr(df, period=14):

    high_low = df["High"] - df["Low"]

    high_close = np.abs(
        df["High"] - df["Close"].shift()
    )

    low_close = np.abs(
        df["Low"] - df["Close"].shift()
    )

    tr = pd.concat(
        [high_low, high_close, low_close],
        axis=1
    ).max(axis=1)

    return tr.rolling(period).mean()

# --------------------
# SIGNAL ENGINE
# --------------------

def analyze(df):

    df["EMA20"] = ema(df["Close"], 20)
    df["EMA50"] = ema(df["Close"], 50)
    df["EMA200"] = ema(df["Close"], 200)

    df["RSI"] = rsi(df["Close"])

    df["MACD"], df["MACD_SIGNAL"] = macd(
        df["Close"]
    )

    df["ATR"] = atr(df)

    last = df.iloc[-1]

    score = 0
    reasons = []

    # Trend
    if (
        last["EMA20"] >
        last["EMA50"] >
        last["EMA200"]
    ):
        score += 30
        reasons.append("Trend Bullish")

    elif (
        last["EMA20"] <
        last["EMA50"] <
        last["EMA200"]
    ):
        score += 30
        reasons.append("Trend Bearish")

    # RSI
    if 40 <= last["RSI"] <= 60:
        score += 20
        reasons.append("RSI Healthy")

    # MACD
    if last["MACD"] > last["MACD_SIGNAL"]:
        score += 20
        reasons.append("MACD Bullish")

    else:
        score += 20
        reasons.append("MACD Bearish")

    # ATR
    if last["ATR"] > df["ATR"].mean():
        score += 20
        reasons.append("High Volatility")

    signal = "WAIT"

    if (
        last["EMA20"] >
        last["EMA50"] >
        last["EMA200"]
        and last["MACD"] >
        last["MACD_SIGNAL"]
    ):
        signal = "CALL 🟢"

    elif (
        last["EMA20"] <
        last["EMA50"] <
        last["EMA200"]
        and last["MACD"] <
        last["MACD_SIGNAL"]
    ):
        signal = "PUT 🔴"

    return signal, score, reasons

# --------------------
# UI
# --------------------

st.title("📈 QUOTEX ANALYZER")

pair = st.selectbox(
    "اختر الزوج",
    list(PAIRS.keys())
)

duration = st.selectbox(
    "مدة الصفقة",
    [1, 2, 3, 5]
)

if st.button("تحليل"):

    symbol = PAIRS[pair]

    with st.spinner("جلب البيانات..."):

        data = yf.download(
            symbol,
            period="5d",
            interval="1m",
            progress=False
        )

    if len(data) < 250:

        st.error("لا توجد بيانات كافية")

    else:

        signal, score, reasons = analyze(data)

        entry_time = datetime.now().strftime(
            "%H:%M"
        )

        st.subheader(pair)

        st.metric(
            "الإشارة",
            signal
        )

        st.metric(
            "القوة",
            f"{score}%"
        )

        st.metric(
            "مدة الصفقة",
            f"{duration} دقيقة"
        )

        st.metric(
            "وقت الدخول",
            entry_time
        )

        st.write("### أسباب القرار")

        for r in reasons:
            st.write("✅", r)

        st.dataframe(
            data.tail(10)
        )
