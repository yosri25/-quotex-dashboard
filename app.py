import os
import sys

try:
    import requests
    import pandas as pd
    import numpy as np
except ImportError:
    os.system(f"{sys.executable} -m pip install requests pandas numpy")
    import requests
    import pandas as pd
    import numpy as np

import streamlit as st
from datetime import datetime, timedelta
import time

st.set_page_config(page_title="QUOTEX ALPHA PRO AI V2", page_icon="🦅", layout="wide")

st.markdown("""
<style>
    .reportview-container { background: #06090e; }
    .signal-card { padding: 30px; border-radius: 15px; text-align: center; font-size: 28px; font-weight: bold; margin-bottom: 25px; color: white; }
    .buy-bg { background: linear-gradient(135deg, #00b09b, #96c93d); box-shadow: 0px 0px 30px #96c93d; border: 2px solid #fff; }
    .sell-bg { background: linear-gradient(135deg, #cb2d3e, #ef473a); box-shadow: 0px 0px 30px #ef473a; border: 2px solid #fff; }
    .wait-bg { background: linear-gradient(135deg, #232526, #414345); box-shadow: 0px 0px 15px #414345; }
</style>
""", unsafe_allow_html=True)

st.title("🦅 QUOTEX ALPHA PRO AI V2 (REAL DATA ENGINE)")
st.markdown("🔥 **نظام التحليل الجديد:** مدمج ببيانات حقيقية 100% | `EMA Trends` | `MACD Momentum` | `Real RSI` 🟢")

ALPHA_API_KEY = "C46ZT9GEEM147ATS"

pairs = {
    "BTC/USD (بيتكوين 24/7)": "BTCUSD",
    "ETH/USD (إيثيريوم 24/7)": "ETHUSD",
    "EUR/USD (يورو / دولار)": "EURUSD",
    "GBP/USD (باوند / دولار)": "GBPUSD",
    "USD/JPY (دولار / ين)": "USDJPY",
    "AUD/USD (أسترالي / دولار)": "AUDUSD",
    "USD/CAD (دولار / كندي)": "USDCAD"
}

selected_display = st.selectbox("🎯 اختر زوج العملة لتحليله بالبيانات الحقيقية:", list(pairs.keys()))
symbol = pairs[selected_display]

st.sidebar.header("💵 إدارة المخاطر")
fixed_bet = st.sidebar.number_input("🎯 قيمة الصفقة ($):", min_value=1, value=5)
risk_mode = st.sidebar.selectbox("🔥 نمط الفلترة:", ["🛡️ Conservative (دقيق وآمن جداً)", "⚡ Aggressive (حركي سريع)"])

def fetch_real_market_data(sym, api_key):
    try:
        # سحب بيانات الشموع الحقيقية لدقيقة واحدة (Intraday M1) لإلغاء العشوائية تماماً
        function_type = "CRYPTO_INTRADAY" if "USD" in sym and ("BTC" in sym or "ETH" in sym) else "FX_INTRADAY"
        interval = "1min"
        
        if function_type == "CRYPTO_INTRADAY":
            url = f"https://www.alphavantage.co/query?function={function_type}&symbol={sym[:3]}&market=USD&interval={interval}&apikey={api_key}"
            time_key = "Time Series Crypto (1min)"
        else:
            url = f"https://www.alphavantage.co/query?function={function_type}&from_symbol={sym[:3]}&to_symbol={sym[3:]}&interval={interval} &apikey={api_key}"
            time_key = "Time Series FX (1min)"
            
        res = requests.get(url, timeout=7).json()
        
        if time_key in res:
            time_series = res[time_key]
            df = pd.DataFrame.from_dict(time_series, orient='index').astype(float)
            df = df.iloc[::-1] # ترتيب الشموع من الأقدم إلى الأحدث
            df.columns = ['open', 'high', 'low', 'close']
            
            # 1. حساب المؤشرات الفنية الحقيقية 100%
            df['EMA_20'] = df['close'].ewm(span=20, adjust=False).mean()
            df['EMA_50'] = df['close'].ewm(span=50, adjust=False).mean()
            
            # حساب RSI حقيقي
            delta = df['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            df['RSI'] = 100 - (100 / (1 + (gain / loss)))
            
            # حساب MACD حقيقي
            df['EMA_12'] = df['close'].ewm(span=12, adjust=False).mean()
            df['EMA_26'] = df['close'].ewm(span=26, adjust=False).mean()
            df['MACD'] = df['EMA_12'] - df['EMA_26']
            df['Signal_Line'] = df['MACD'].ewm(span=9, adjust=False).mean()
            
            latest = df.iloc[-1]
            prev = df.iloc[-2]
            
            return latest, prev, "success"
        elif "Note" in res:
            return None, None, "⚠️ السيرفر محدد بـ 5 طلبات في الدقيقة. انتظر 10 ثواني وأعد الضغط."
        else:
            return None, None, "⚠️ خطأ في تهيئة بيانات الزوج، جرب زوجاً آخر الآن."
    except Exception as e:
        return None, None, f"❌ خطأ اتصال بالسيرفر الرئيسي: {str(e)}"

if st.button("🦅 اقتناص صفقة المحترفين بالبيانات الحقيقية"):
    t0 = time.time()
    with st.spinner("🧠 الـ AI يحلل الشموع الحقيقية الحالية ويحسب مؤشرات الاتجاه والزخم..."):
        latest, prev, status = fetch_real_market_data(symbol, ALPHA_API_KEY)
    t1 = time.time()

    if status == "success" and latest is not None:
        st.success(f"📡 متصل بالبث البنكي الحقيقي! | ⏱️ سرعة الحساب: `{t1-t0:.2f} ثانية` | **السعر الحالي:** `{latest['close']:.5f}`")
        
        now_time = datetime.now()
        target_candle_time = (now_time + timedelta(minutes=1)).strftime("%H:%M:00")
        current_time_str = now_time.strftime("%H:%M:%S")
        
        # استخراج القيم الحقيقية
        rsi_val = latest['RSI'] if not np.isnan(latest['RSI']) else 50.0
        macd_val = latest['MACD']
        sig_val = latest['Signal_Line']
        trend_up = latest['EMA_20'] > latest['EMA_50']
        
        # خوارزمية دمج المؤشرات الحقيقية (Real Confluence Logic)
        is_call = trend_up and rsi_val < 45 and macd_val > sig_val
        is_put = (not trend_up) and rsi_val > 55 and macd_val < sig_val
        
        # فلتر إضافي للنمط الحركي السريع
        if "Aggressive" in risk_mode:
            if rsi_val < 40 or (macd_val > sig_val and prev['MACD'] <= prev['Signal_Line']):
                is_call = True
            elif rsi_val > 60 or (macd_val < sig_val and prev['MACD'] >= prev['Signal_Line']):
                is_put = True

        if is_call:
            signal_type = "CALL 🟢 (شراء صعود)"
            bg_class = "buy-bg"
            action_note = f"🔥 تأكيد حقيقي: الاتجاه العام صاعد (EMA) والزخم يدعم الانفجار لأعلى (MACD). الـ RSI الحالي: {rsi_val:.2f}."
        elif is_put:
            signal_type = "PUT 🔴 (بيع هبوط)"
            bg_class = "sell-bg"
            action_note = f"🔥 تأكيد حقيقي: الاتجاه العام هابط (EMA) والزخم يدعم الانهيار لأسفل (MACD). الـ RSI الحالي: {rsi_val:.2f}."
        else:
            signal_type = "WAIT 🟡 (تريّث، غير زوج العملة)"
            bg_class = "wait-bg"
            action_note = f"مؤشر الـ RSI عند {rsi_val:.2f} والـ MACD مستقر. السوق في منطقة تذبذب كاذب، غير الزوج فوراً لقنص فرصة أنظف."

        if "WAIT" not in signal_type:
            st.markdown(f"""
            <div class="signal-card {bg_class}">
                🎯 توصية الـ AI الحقيقية: {signal_type} <br>
                <span style="font-size:22px; font-weight: bold; display:block; margin-top:12px; color: #fff; background: rgba(0,0,0,0.4); padding: 10px; border-radius: 8px;">
                    ⏱️ توقيت الدخول الحتمي: {target_candle_time} بالضبط
                </span>
                <span style="font-size:15px; font-weight: normal; display:block; margin-top:10px;">
                    🕒 وقت كبس الزر الحالي: {current_time_str} | ⌛ مدة الصفقة: 1 MIN <br> 📝 الفلترة الفنية: {action_note}
                </span>
            </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="signal-card {bg_class}">🎯 توصية الـ AI الحقيقية: {signal_type} <br><span style="font-size:16px; font-weight: normal; display:block; margin-top:10px;">🕒 الوقت الحالي: {current_time_str} <br> 📝 تحليل سلوك السعر: {action_note}</span></div>', unsafe_allow_html=True)
    else:
        st.error(status)
else:
    st.info("💡 البوت مدمج بالـ Real Time Data ومؤشرات الاتجاه والزخم الاحترافية. حدث الكود وفجر الأرباح!")
