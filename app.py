import streamlit as st
import pandas as pd
import requests
from datetime import datetime

# إعدادات واجهة المستخدم الاحترافية للأسواق الحية
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

# 🔑 تثبيت الـ API المفعل الجديد
API_KEY = "A272cbbc1bee42a49d19a1582631cc92"

# قائمة أزواج العملات الثمانية الكاملة
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

# دالة جلب البيانات مع إرسال الـ API Key بطريقة آمنة
def fetch_safe_live_data(sym, api_key):
    try:
        url = f"https://api.twelvedata.com/time_series?symbol={sym}&interval=1min&outputsize=15&apikey={api_key}"
        headers = {"Authorization": f"apikey {api_key}"}
        response = requests.get(url, headers=headers).json()
        
        if "status" in response and response["status"] == "error":
            return None, None, f"❌ خطأ من السيرفر: {response['message']}"
            
        if "values" in response and len(response["values"]) > 0:
            df_data = pd.DataFrame(response["values"])
            df_data["close"] = df_data["close"].astype(float)
            current_price = df_data["close"].iloc[0]
            
            # حساب مؤشر RSI داخلي
            delta = df_data["close"].iloc[::-1].diff()
            gain = delta.where(delta > 0, 0).rolling(window=10, min_periods=1).mean().iloc[-1]
            loss = (-delta.where(delta < 0, 0)).rolling(window=10, min_periods=1).mean().iloc[-1]
            
            rsi_val = 50.0 if loss == 0 else 100 - (100 / (1 + (gain / loss)))
            return current_price, rsi_val, "success"
        else:
            return None, None, "⚠️ استجابة فارغة، يرجى المحاولة بعد لحظات."
    except Exception as e:
        return None, None, f"❌ خطأ اتصال: {str(e)}"

if st.button("🔄 اقتناص الإشارة الحية الآن"):
    with st.spinner("جاري جلب البيانات..."):
        price, rsi, status_message = fetch_safe_live_data(symbol, API_KEY)

    if status_message == "success" and price is not None:
        st.success(f"📡 متصل بنجاح! | **السعر الحالي:** `{price:.5f}` | **RSI المحسوب:** `{rsi:.2f}`")
        
        if rsi < 40:
            signal_type = "CALL 🟢 (شراء فوراً)"
            bg_class = "buy-bg"
            action_note = "رصد تشبع بيعي لحظي - توقع صعود فوري للشمعة الحالية"
        elif rsi > 60:
            signal_type = "PUT 🔴 (بيع فوراً)"
            bg_class = "sell-bg"
            action_note = "رصد تشبع شرائي لحظي - توقع هبوط فوري للشمعة الحالية"
        else:
            signal_type = "WAIT 🟡 (انتظر فرصة أقوى)"
            bg_class = "wait-bg"
            action_note = "المؤشر مستقر في منطقة حيادية، انتظر حركة سيولة جديدة"
            
        st.markdown(f'<div class="signal-card {bg_class}">🎯 التوصية الحية: {signal_type} <br><span style="font-size:17px;">⏱️ مدة الصفقة: 1 MIN | 🕒 وقت التحديث: {datetime.now().strftime("%H:%M:%S")} <br> 📝 التحليل اللحظي: {action_note}</span></div>', unsafe_allow_html=True)
    else:
        st.error(status_message)
else:
    st.info("💡 المنصة جاهزة وآمنة تماماً. اضغط على الزر بالأعلى لجلب الإشارة الحية فوراً.")
