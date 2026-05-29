import streamlit as st
import pandas as pd
import requests
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

st.title("👑 QUOTEX AI LIVE ALGO (TWELVE DATA)")
st.markdown("🔗 **إدارة الحساب:** `صفقات ثابتة آمنة 🛡️` | **مزود البيانات:** `Twelve Data Live 🟢` ")

# 🔑 مفتاح الـ API الجديد والكامل بعد تفعيل الإيميل
API_KEY = "A272cbbc1bee42a49d19a1582631cc92"

# قائمة الـ 8 أزواج عملات الحية المتاحة كاملة
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

# القائمة الجانبية لإدارة المال
st.sidebar.header("💵 إدارة رأس المال")
fixed_bet = st.sidebar.number_input("🎯 قيمة الصفقة الثابتة ($):", min_value=1, value=5)

# دالة جلب البيانات بنظام الـ Time Series الآمن بطلب واحد خفيف
def fetch_fast_data(sym, api_key):
    try:
        url = f"https://api.twelvedata.com/time_series?symbol={sym}&interval=1min&outputsize=25&apikey={api_key}"
        response = requests.get(url).json()
        
        # كشف الأخطاء المباشر من السيرفر
        if "status" in response and response["status"] == "error":
            return None, None, f"❌ خطأ من سيرفر البيانات: {response['message']}"
            
        if "values" in response:
            df_data = pd.DataFrame(response["values"])
            df_data["close"] = df_data["close"].astype(float)
            
            # السعر الحالي المباشر
            current_price = df_data["close"].iloc[0]
            
            # حساب مؤشر RSI داخلياً لتفادي الـ Rate Limit
            delta = df_data["close"].iloc[::-1].diff()
            gain = delta.where(delta > 0, 0).rolling(window=14).mean().iloc[-1]
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean().iloc[-1]
            
            if loss == 0:
                rsi_val = 50.0
            else:
                rs = gain / loss
                rsi_val = 100 - (100 / (1 + rs))
                
            return current_price, rsi_val, "success"
        else:
            return None, None, "⚠️ السيرفر رجع استجابة فارغة، تفقد حالة الحساب."
    except Exception as e:
        return None, None, f"❌ خطأ غير متوقع: {str(e)}"

price, rsi, status_message = fetch_fast_data(symbol, API_KEY)

if status_message == "success" and price is not None:
    st.success(f"📡 متصل بنجاح! | **السعر الحالي:** `{price:.5f}` | **RSI المحسوب لايف:** `{rsi:.2f}`")
    
    if rsi < 35:
        signal_type = "CALL 🟢 (شراء فوراً)"
        bg_class = "buy-bg"
        duration = "1 MIN (دقيقة واحدة)"
        action_note = "تشبع بيعي قوي - السعر يتجه للصعود"
    elif rsi > 65:
        signal_type = "PUT 🔴 (بيع فوراً)"
        bg_class = "sell-bg"
        duration = "1 MIN (دقيقة واحدة)"
        action_note = "تشبع شرائي قوي - السعر يتجه للهبوط"
    else:
        signal_type = "WAIT 🟡 (تذبذب - انتظر صفقة مضمونة)"
        bg_class = "wait-bg"
        duration = "--"
        action_note = "المؤشر في منطقة مستقرة، انتظر فرصة أقوى"
        
    st.markdown(f'<div class="signal-card {bg_class}">🎯 التوصية الحية: {signal_type} <br><span style="font-size:17px;">⏱️ مدة الصفقة: {duration} | 🕒 التوقيت: {datetime.now().strftime("%H:%M:%S")} <br> 📝 التحليل الفني: {action_note}</span></div>', unsafe_allow_html=True)
else:
    st.error(status_message)

st.markdown("---")

# دفتر الصفقات يدوياً
st.subheader("🕒 دفتر صفقاتك الحية المقتنصة")
if 'live_history' not in st.session_state:
    st.session_state.live_history = []

col_c1, col_c2 = st.columns(2)
with col_c1:
    if st.button("✅ قيدت هذه الصفقة وطلعت رابحة (WIN)"):
        now_str = datetime.now().strftime("%H:%M:%S")
        st.session_state.live_history.insert(0, {"توقيت الدخول": now_str, "الزوج": selected_display, "النوع": "LIVE", "المبلغ": f"${fixed_bet}", "النتيجة": "WIN ✅", "الصافي": f"+${int(fixed_bet*0.85)}"})
        st.rerun()
with col_c2:
    if st.button("❌ قيدت هذه الصفقة وطلعت خاسرة (LOSS)"):
        now_str = datetime.now().strftime("%H:%M:%S")
        st.session_state.live_history.insert(0, {"توقيت الدخول": now_str, "الزوج": selected_display, "النوع": "LIVE", "المبلغ": f"${fixed_bet}", "النتيجة": "LOSS ❌", "الصافي": f"-${int(fixed_bet)}"})
        st.rerun()

if len(st.session_state.live_history) > 0:
    st.dataframe(pd.DataFrame(st.session_state.live_history), use_container_width=True)
