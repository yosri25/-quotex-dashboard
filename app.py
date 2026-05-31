import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime

st.set_page_config(
    page_title="Quotex Analyzer PRO v6",
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
    high_close = np.abs(df["High"] - df["Close"].shift())
    low_close = np.abs(df["Low"] - df["Close"].shift())
    
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(period).mean()

# --------------------
# SIGNAL ENGINE
# --------------------

def analyze(df):
    # حساب المؤشرات وإضافتها للجدول
    df["EMA20"] = ema(df["Close"], 20)
    df["EMA50"] = ema(df["Close"], 50)
    df["EMA200"] = ema(df["Close"], 200)
    df["RSI"] = rsi(df["Close"])
    df["MACD"], df["MACD_SIGNAL"] = macd(df["Close"])
    df["ATR"] = atr(df)

    # التحديث الجديد: تعبئة القيم الفارغة بالطريقة المتوافقة مع النسخ الحديثة لـ Pandas
    df = df.bfill().ffill()

    # سحب آخر شمعة بأمان
    last = df.iloc[-1]
    
    score = 0
    reasons = []

    # تحويل القيم إلى أرقام فردية دقيقة لتفادي أخطاء المقارنة
    e20 = float(last["EMA20"].iloc[0] if isinstance(last["EMA20"], pd.Series) else last["EMA20"])
    e50 = float(last["EMA50"].iloc[0] if isinstance(last["EMA50"], pd.Series) else last["EMA50"])
    e200 = float(last["EMA200"].iloc[0] if isinstance(last["EMA200"], pd.Series) else last["EMA200"])
    rsi_val = float(last["RSI"].iloc[0] if isinstance(last["RSI"], pd.Series) else last["RSI"])
    macd_val = float(last["MACD"].iloc[0] if isinstance(last["MACD"], pd.Series) else last["MACD"])
    macd_sig = float(last["MACD_SIGNAL"].iloc[0] if isinstance(last["MACD_SIGNAL"], pd.Series) else last["MACD_SIGNAL"])
    atr_val = float(last["ATR"].iloc[0] if isinstance(last["ATR"], pd.Series) else last["ATR"])
    atr_mean = float(df["ATR"].mean().iloc[0] if isinstance(df["ATR"].mean(), pd.Series) else df["ATR"].mean())

    if np.isnan(rsi_val):
        rsi_val = 50.0

    # تحليل الاتجاه العام (Trend)
    if e20 > e50 > e200:
        score += 30
        reasons.append("Trend Bullish (اتجاه عام صاعد قوي)")
    elif e20 < e50 < e200:
        score += 30
        reasons.append("Trend Bearish (اتجاه عام هابط قوي)")

    # تحليل مؤشر الزخم RSI
    if 40 <= rsi_val <= 60:
        score += 20
        reasons.append(f"RSI Healthy ({rsi_val:.2f}) - منطقة زخم مستقرة")

    # تحليل تقاطع الماكد MACD
    if macd_val > macd_sig:
        score += 20
        reasons.append("MACD Bullish (تقاطع إيجابي للسيولة)")
    else:
        score += 20
        reasons.append("MACD Bearish (تقاطع سلبي للسيولة)")

    # تحليل السيولة ATR
    if atr_val > atr_mean:
        score += 20
        reasons.append("High Volatility (حركة سوق نشطة وممتازة)")

    # القرار النهائي
    signal = "WAIT 🟡"
    if e20 > e50 > e200 and macd_val > macd_sig:
        signal = "CALL 🟢 (صعود)"
    elif e20 < e50 < e200 and macd_val < macd_sig:
        signal = "PUT 🔴 (هبوط)"

    return signal, score, reasons

# --------------------
# UI / INTERFACE
# --------------------

st.title("📈 QUOTEX INSTITUTIONAL ANALYZER (V6 FIXED)")

pair = st.selectbox("🎯 اختر زوج العملة المتاحة:", list(PAIRS.keys()))
duration = st.selectbox("⏱️ مدة الصفقة الموصى بها:", [1, 2, 3, 5])

if st.button("🦅 ابدأ التحليل الفوري العالي الدقة"):
    symbol = PAIRS[pair]

    with st.spinner("📡 جلب تنبيهات الأسعار الفورية من الخادم..."):
        # سحب البيانات بفترة كافية لحساب المتوسطات
        data = yf.download(symbol, period="5d", interval="1m", progress=False)

    if data.empty:
        st.error("❌ عذراً، لم يتم إرجاع بيانات من السيرفر. تأكد أن سوق الفوركس مفتوح حالياً.")
    else:
        # تنظيف أعمدة الـ MultiIndex تماماً لتبسيط الجدول
        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)
        
        # تشغيل محرك التحليل المحمي
        try:
            signal, score, reasons = analyze(data)
            entry_time = datetime.now().strftime("%H:%M:%S")

            st.markdown("---")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("📊 الأداة المالية", pair)
            with col2:
                st.metric("🎯 التوصية الحالية", signal)
            with col3:
                st.metric("🔥 قوة الإشارة الفنية", f"{score}%")
            with col4:
                st.metric("⏱️ وقت دخول الصفقة", entry_time)

            st.write("### 📝 أسباب وتفاصيل القرار الفني:")
            for r in reasons:
                st.write("✅", r)

            st.write("### 📉 آخر الشموع التي تم تحليل سلوكها:")
            st.dataframe(data.tail(10))
            
        except Exception as e:
            st.error(f"⚠️ حدث خطأ أثناء الحساب الفني: {str(e)}. يرجى إعادة المحاولة.")
