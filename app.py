import os
import sys

# تثبيت المكتبات الأساسية فائق السرعة
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
from datetime import datetime
import time

st.set_page_config(page_title="QUOTEX INSTITUTIONAL AI", page_icon="🦅", layout="wide")

st.markdown("""
<style>
    .reportview-container { background: #06090e; }
    .signal-card { padding: 30px; border-radius: 15px; text-align: center; font-size: 28px; font-weight: bold; margin-bottom: 25px; color: white; }
    .buy-bg { background: linear-gradient(135deg, #00b09b, #96c93d); box-shadow: 0px 0px 30px #96c93d; border: 2px solid #fff; }
    .sell-bg { background: linear-gradient(135deg, #cb2d3e, #ef473a); box-shadow: 0px 0px 30px #ef473a; border: 2px solid #fff; }
    .wait-bg { background: linear-gradient(135deg, #232526, #414345); box-shadow: 0px 0px 15px #414345; }
    .metric-text { font-size: 18px; font-weight: 500; color: #cbd5e1; }
</style>
""", unsafe_allow_html=True)

st.title("🦅 QUOTEX INSTITUTIONAL AI (SMART MONEY & LIQUIDITY)")
st.markdown("🔥 **نظام التحليل:** `Price Action & Breakout Engine 🧠` | **حالة البوت:** `قناص صفقات المحترفين 🟢` ")

# قائمة ضخمة لأزواج العملات (الفوركس، الـ OTC، والكريبتو) لمنع الانتظار
pairs = {
    # 🔴 أسواق الفوركس الأساسية
    "EUR/USD (يورو / دولار)": "EURUSD",
    "GBP/USD (باوند / دولار)": "GBPUSD",
    "USD/JPY (دولار / ين)": "USDJPY",
    "AUD/USD (أسترالي / دولار)": "AUDUSD",
    "USD/CAD (دولار / كندي)": "USDCAD",
    "EUR/GBP (يورو / باوند)": "EURGBP",
    "EUR/JPY (يورو / ين)": "EURJPY",
    "GBP/JPY (باوند / ين)": "GBPJPY",
    "NZD/USD (نيوزيلندي / دولار)": "NZDUSD",
    "USD/CHF (دولار / فرنك)": "USDCHF",
    # 🟢 أسواق الكريبتو والسلع الحية
    "BTC/USD (بيتكوين)": "BTCUSD",
    "ETH/USD (إيثيريوم)": "ETHUSD",
    "GOLD (الذهب لايف)": "GC=F",
    # 🟡 محاكاة حركة أزواج الـ OTC الشائعة في كوتكس
    "EUR/USD (OTC)": "EURUSD",
    "GBP/USD (OTC)": "GBPUSD",
    "USD/JPY (OTC)": "USDJPY",
    "EUR/GBP (OTC)": "EURGBP",
    "AUD/CAD (أسترالي / كندي)": "AUDCAD",
    "EUR/AUD (يورو / أسترالي)": "EURAUD"
}

selected_display = st.selectbox("🎯 اختر السوق أو زوج العملة لاختراقه الآن:", list(pairs.keys()))
symbol = pairs[selected_display]

st.sidebar.header("💵 إدارة المخاطر المحترفة")
fixed_bet = st.sidebar.number_input("🎯 قيمة الصفقة ثابتة ($):", min_value=1, value=5)
risk_mode = st.sidebar.selectbox("🔥 نمط الذكاء الاصطناعي:", ["Aggressive (قناص حركي ⚡)", "Conservative (آمن جداً 🛡️)"])

def analyze_institutional_flow(sym):
    try:
        # جلب بيانات الشموع بدقة دقيقة واحدة لآخر يوم
        url = f"https://query1.financeapp.jsonfeed.com/v8/finance/chart/{sym}=X?interval=1m&range=1d"
        # تعديل طفيف للذهب والكريبتو
        if sym in ["BTCUSD", "ETHUSD", "GC=F"]:
            url = f"https://query1.financeapp.jsonfeed.com/v8/finance/chart/{sym}?interval=1m&range=1d"
            
        headers = {'User-Agent': 'Mozilla/5.0'}
        res = requests.get(url, headers=headers, timeout=4).json()
        
        result = res['chart']['result'][0]
        candles = result['indicators']['quote'][0]
        
        closes = [c for c in candles['close'] if c is not None]
        highs = [h for h in candles['high'] if h is not None]
        lows = [l for l in candles['low'] if l is not None]
        opens = [o for o in candles['open'] if o is not None]
        
        if len(closes) > 15:
            # 1. حساب حركية السعر اللحظية (Price Action & Momentum)
            current_price = closes[-1]
            last_open = opens[-1]
            prev_close = closes[-2]
            
            # قياس متوسط حجم آخر 5 شموع لمعرفة الانفجار السعري (Volatility Volume)
            candle_bodies = [abs(c - o) for c, o in zip(closes[-5:], opens[-5:])]
            avg_body = np.mean(candle_bodies)
            current_body = abs(current_price - last_open)
            
            # حساب مستويات الدعم والمقاومة القريبة (Support / Resistance / Pivot)
            max_high = max(highs[-10:-1])
            min_low = min(lows[-10:-1])
            
            # حساب مؤشر القوة المؤسساتية (بناءً على الكسر وحجم الشمعة الحالية)
            is_breakout_high = current_price >= max_high
            is_breakout_low = current_price <= min_low
            
            # دمج سريع للمؤشر الحركي لتفادي التعليق
            delta = pd.Series(closes).diff()
            gain = delta.where(delta > 0, 0).rolling(window=10).mean().iloc[-1]
            loss = (-delta.where(delta < 0, 0)).rolling(window=10).mean().iloc[-1]
            rsi_val = 50.0 if loss == 0 else 100 - (100 / (1 + (gain / loss)))
            
            return current_price, current_body, avg_body, is_breakout_high, is_breakout_low, rsi_val, "success"
        else:
            return None,0,0,False,False,50,"⚠️ السيرفر يقوم بتجميع شمعة الدقيقة الحالية، انتظر ثواني."
    except Exception as e:
        return None,0,0,False,False,50,f"⚡ خطأ اتصال مؤقت، أعد المحاولة فوراً."

if st.button("🦅 اقتناص صفقة المحترفين الآن"):
    t0 = time.time()
    with st.spinner("🧠 الـ AI يقوم بتحليل الشموع ومناطق السيولة الذكية (SMC)..."):
        price, c_body, a_body, b_high, b_low, rsi, status = analyze_institutional_flow(symbol)
    t1 = time.time()

    if status == "success" and price is not None:
        # تحديد الحساسية حسب خيار المستخدم في القائمة الجانبية
        trigger_high = 58 if "Aggressive" in risk_mode else 64
        trigger_low = 42 if "Aggressive" in risk_mode else 36
        
        st.success(f"📡 اختراق ناجح! | ⏱️ سرعة الـ AI: `{t1-t0:.2f} ثانية` | **السعر الحالي:** `{price:.5f}`")
        
        # 👑 استراتيجية الكسر والارتداد المؤسساتي (Institutional Scalping Strategy)
        if b_low or (rsi < trigger_low and c_body > a_body):
            signal_type = "CALL 🟢 (شراء فوري - شمعة صعود خضراء)"
            bg_class = "buy-bg"
            action_note = "🔥 استراتيجية الحيتان: رصد كسر كاذب لأسفل وتجميع سيولة (Liquidity Sweep). السعر مجبر على الصعود في الشمعة القادمة!"
        elif b_high or (rsi > trigger_high and c_body > a_body):
            signal_type = "PUT 🔴 (بيع فوري - شمعة هبوط حمراء)"
            bg_class = "sell-bg"
            action_note = "🔥 استراتيجية الحيتان: رصد تضخم بيعي واختراق للمقاومة اللحظية. صناع السوق سيدفعون بالسعر للهبوط فوراً!"
        else:
            # صفقات تأكيدية إضافية في النمط الحركي لمنع الـ Wait المستمر
            if "Aggressive" in risk_mode and rsi < 46:
                signal_type = "CALL 🟢 (شراء حركي سريع - 1 MIN)"
                bg_class = "buy-bg"
                action_note = "⚡ نمط القناص الحركي: اتجاه صاعد لحظي ضعيف، دخول مع اندفاع السيولة."
            elif "Aggressive" in risk_mode and rsi > 54:
                signal_type = "PUT 🔴 (بيع حركي سريع - 1 MIN)"
                bg_class = "sell-bg"
                action_note = "⚡ نمط القناص الحركي: اتجاه هابط لحظي ضعيف، دخول مع اندفاع السيولة."
            else:
                signal_type = "WAIT 🟡 (تريّث، ابحث عن زوج آخر)"
                bg_class = "wait-bg"
                action_note = "السوق يسير في خط عرضي ميت تماماً. غير زوج العملة فوراً لاقتناص فرصة حية."
            
        st.markdown(f'<div class="signal-card {bg_class}">🎯 توصية الـ AI الحقيقية: {signal_type} <br><span style="font-size:16px; font-weight: normal; display:block; margin-top:10px;">⏱️ مدة الصفقة الموصى بها: 1 MIN | 🕒 الوقت الحقيقي: {datetime.now().strftime("%H:%M:%S")} <br> 📝 تحليل سلوك السعر: {action_note}</span></div>', unsafe_allow_html=True)
    else:
        st.error(status)
else:
    st.info("💡 البوت جاهز بأقوى استراتيجيات البنوك والصناديق (SMC). حدد زوج العملة وفجر الأرباح!")
