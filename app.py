import streamlit as st
import pandas as pd
import requests
import time
from datetime import datetime

# إعدادات واجهة المستخدم الاحترافية VIP للأسواق الحية
st.set_page_config(page_title="QUOTEX LIVE TWELVE AI", page_icon="👑", layout="wide")

st.markdown("""
<style>
    .reportview-container { background: #0b0e14; }
    .metric-box { background: linear-gradient(135deg, #1f293d, #111827); padding: 20px; border-radius: 12px; text-align: center; border: 1px solid #374151; }
    .signal-card { padding: 30px; border-radius: 15px; text-align: center; font-size: 26px; font-weight: bold; margin-bottom: 25px; color: white; }
    .buy-bg { background: linear-gradient(135deg, #11998e, #38ef7d); box-shadow: 0px 0px 20px #38ef7d; }
    .sell-bg { background: linear-gradient(135deg, #ff416c, #ff4b2b); box-shadow: 0px 0px 20px #ff4b2b; }
    .wait-bg { background: linear-gradient(135deg, #1e293b, #334155); box-shadow: 0px 0px 15px #334155; }
</style>
""", unsafe_allow_html=True)

st.title("👑 QUOTEX AI LIVE ALGO (TWELVE DATA - FIXED)")
st.markdown("🔗 **إدارة الحساب:** `صفقات ثابتة آمنة 🛡️` | **مزود البيانات:** `Twelve Data Live 🟢` ")

# 🔑 مفتاح الـ API المفعل الجديد متاعك
API_KEY = "A272cbbc1bee42a49d19a1582631cc92"

# الـ 8 أزواج عملات كاملة
pairs = {
    "EUR/USD (يورو / دولار)": "EUR/USD",
    "GBP/USD (باوند / دولار)": "GBP/USD",
    "USD/JPY (دولار / ين)": "USD/JPY",
    "AUD/USD (أسترالي / دولار)": "AUD/USD",
    "EUR/GBP (يورو / باوند)": "EUR/GBP",
    "EUR/JPY (يورو / ين)": "EUR/JPY",
    "GBP/JPY (باوند / ين)": "GBP/JPY",
    "USD/CAD (دولار / كندي)": "USD/CAD"
}
selected_display = st.selectbox("🎯 اختر زوج العملات لقراءة حركته الحية الآن:", list(pairs.keys()))
symbol = pairs[selected_display]

st.sidebar.header("💵 إدارة رأس المال")
fixed_bet = st.sidebar.number_input("🎯 قيمة الصفقة الثابتة ($):", min_value=1, value=5)

# دالة جلب البيانات مع تطبيق حل الـ Agent (طلب خفيف لزوج واحد فقط عند الحاجة)
def fetch_safe_data(sym, api_key):
    try:
        # تقليص الـ outputsize لـ 15 شمعة فقط لتخفيف وزن الطلب على السيرفر
        url = f"https://api.twelvedata.com/time_series?symbol={sym}&interval=1min&outputsize=15&apikey={api_key}"
        response = requests.get(url).json()
        
        if "status" in response and response["status"] == "error":
            return None, None, f"❌ خطأ من السيرفر: {response['message']}"
            
        if "values" in response:
            df_data = pd.DataFrame(response["values"])
            df_data["close"] = df_data["close"].astype(float)
            current_price = df_data["close"].iloc[0]
            
            # حساب مؤشر RSI داخلي سريع ومبسط لتفادي كثرة الطلبات الخارجية
            delta = df_data["close"].iloc[::-1].diff()
            gain = delta.where(delta > 0, 0).rolling(window=10, min_periods=1).mean().iloc[-1]
            loss = (-delta.where(delta < 0, 0)).rolling(window=10, min_periods=1).mean().iloc[-1]
            
            rsi_val = 50.0 if loss == 0 else 100 - (100 / (1 + (gain / loss)))
            return current_price, rsi_val, "success"
        else:
            return None, None, "⚠️ استجابة فارغة، يرجى إعادة المحاولة."
    except Exception as e:
        return None, None, f"❌ خطأ: {str(e)}"

# 🛠️ الحل السحري: منع الـ Auto-refresh التلقائي وجعل الطلب يتم بالزر فقط لحماية الـ Limit
if st.button("🔄 اقتناص الإشارة الحية الآن"):
    with st.spinner("جاري الاتصال الآمن بالسيرفر..."):
        price, rsi, status_message = fetch_safe_data(symbol, API_KEY)

    if status_message == "success" and price is not None:
        st.success(f"📡 متصل بنجاح! | **السعر الحالي:** `{price:.5f}` | **RSI المحسوب:** `{rsi:.2f}`")
        
        # خوارزمية تحديد الإشارات بناءً على رصد السوق
        if rsi < 40:
            signal_type = "CALL 🟢 (شراء فوراً)"
            bg_class = "buy-bg"
            action_note = "رصد تشبع بيعي لحظي - توقع صعود فوري للشمعة"
        elif rsi > 60:
            signal_type = "PUT 🔴 (بيع فوراً)"
            bg_class = "sell-bg"
            action_note = "رصد تشبع شرائي لحظي - توقع هبوط فوري للشمعة"
        else:
            signal_type = "WAIT 🟡 (انتظر فرصة أقوى)"
            bg_class = "wait-bg"
            action_note = "المؤشر مستقر، انتظر دخول سيولة جديدة في السوق"
            
        st.markdown(f'<div class="signal-card {bg_class}">🎯 التوصية الحية: {signal_type} <br><span style="font-size:17px;">⏱️ مدة الصفقة: 1 MIN | 🕒 وقت التحديث: {datetime.now().strftime("%H:%M:%S")} <br> 📝 التحليل اللحظي: {action_note}</span></div>', unsafe_allow_html=True)
    else:
        st.error(status_message)
else:
    st.info("💡 المنصة جاهزة وآمنة. اختر زوج العملات ثم اضغط على الزر بالأعلى لجلب الإشارة فوراً بدون حظر.")

st.markdown("---")
st.subheader("🕒 دفتر صفقاتك الحية المقتنصة")
if 'live_history' not in st.session_state:
    st.session_state.live_history = []

col_c1, col_c2 = st.columns(2)
with col_c1:
    if st.button("✅ صفقات رابحة (WIN)"):
        st.session_state.live_history.insert(0, {"توقيت الدخول": datetime.now().strftime("%H:%M:%S"), "الزوج": selected_display, "النتيجة": "WIN ✅", "الصافي": f"+${int(fixed_bet*0.85)}"})
        st.rerun()
with col_c2:
    if st.button("❌ صفقات خاسرة (LOSS)"):
        st.session_state.live_history.insert(0, {"توقيت الدخول": datetime.now().strftime("%H:%M:%S"), "الزوج": selected_display, "النتيجة": "LOSS ❌", "الصافي": f"-${int(fixed_bet)}"})
        st.rerun()

if len(st.session_state.live_history) > 0:
    st.dataframe(pd.DataFrame(st.session_state.live_history), use_container_width=True)
