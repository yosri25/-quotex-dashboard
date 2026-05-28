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
    .live-indicator { background-color: #1e3a8a; color: #93c5fd; padding: 10px; border-radius: 8px; text-align: center; font-weight: bold; margin-bottom: 15px; }
</style>
""", unsafe_allow_html=True)

st.title("👑 QUOTEX AI LIVE ALGO (TWELVE DATA EDITION)")
st.markdown("🔗 **إدارة الحساب:** `صفقات ثابتة آمنة 🛡️` | **مزود البيانات:** `Twelve Data Live API 🟢` ")

st.markdown('<div class="live-indicator">📡 الرادار متصل الآن بـ Twelve Data ويقرأ المؤشرات الفنية لايف بالثانية!</div>', unsafe_allow_html=True)
st.markdown("---")

# وضع مفتاحك الخاص هنا
API_KEY = "De43c307396941f4a5a2cda2c51c3018"

# قائمة العملات المتاحة بعد الزيادة والتوسيع لفرص أكثر
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
st.sidebar.markdown("---")
st.sidebar.info("📌 تذكر: البوت يعطيك التوقيت والمدة الحالية بناءً على حركة السوق الفورية.")

# دالة جلب السعر والـ RSI الحقيقي من Twelve Data
def fetch_twelve_data(sym, api_key):
    try:
        # جلب السعر الحالي
        price_url = f"https://api.twelvedata.com/price?symbol={sym}&apikey={api_key}"
        price_res = requests.get(price_url).json()
        current_price = float(price_res['price'])
        
        # جلب مؤشر RSI الحقيقي لدقيقة واحدة
        rsi_url = f"https://api.twelvedata.com/rsi?symbol={sym}&interval=1min&time_period=14&apikey={api_key}"
        rsi_res = requests.get(rsi_url).json()
        rsi_val = float(rsi_res['values'][0]['rsi'])
        
        return current_price, rsi_val, True
    except:
        return None, None, False

# تشغيل الجلب والتحليل المباشر
price, rsi, success = fetch_twelve_data(symbol, API_KEY)

if success and price is not None:
    st.write(f"📊 **السعر الفوري الحالي:** `{price:.5f}` | **مؤشر RSI الحقيقي:** `{rsi:.2f}`")
    
    # استراتيجية التشبع الاحترافية للإشارات الحية
    if rsi < 32:
        signal_type = "CALL 🟢 (شراء فوراً)"
        bg_class = "buy-bg"
        duration = "1 MIN (دقيقة واحدة)"
        action_note = "السوق هبط تحت منطقة الدعم - توقع صعود فوري"
    elif rsi > 68:
        signal_type = "PUT 🔴 (بيع فوراً)"
        bg_class = "sell-bg"
        duration = "1 MIN (دقيقة واحدة)"
        action_note = "السوق صعد فوق منطقة المقاومة - توقع هبوط فوري"
    else:
        signal_type = "WAIT 🟡 (تذبذب - انتظر صفقة مضمونة)"
        bg_class = "wait-bg"
        duration = "--"
        action_note = "مؤشر RSI مستقر في الوسط، انتظر خروج السعر من منطقة التردد"
        
    # عرض كرت الإشارة الحي الكبير والتوقيت بالثانية
    st.markdown(f'<div class="signal-card {bg_class}">🎯 التوصية الحية: {signal_type} <br><span style="font-size:17px;">⏱️ مدة الصفقة: {duration} | 🕒 توقيت الإشارة الفوري: {datetime.now().strftime("%H:%M:%S")} <br> 📝 التحليل الفني: {action_note}</span></div>', unsafe_allow_html=True)
else:
    st.warning("⚠️ جاري الاتصال بسيرفر Twelve Data وجلب الأسعار الحية... أعمل تحديث (Refresh) بعد ثوانٍ قليلة.")

st.markdown("---")

# دفتر صفقاتك الحية المقتنصة يدوياً
st.subheader("🕒 دفتر صفقاتك الحية المقتنصة")

if 'live_history' not in st.session_state:
    st.session_state.live_history = []

col_c1, col_c2 = st.columns(2)
with col_c1:
    if st.button("✅ قيدت هذه الصفقة وطلعت رابحة (WIN)"):
        now_str = datetime.now().strftime("%H:%M:%S")
        st.session_state.live_history.insert(0, {
            "توقيت الدخول": now_str, "الزوج": selected_display, "النوع": "CALL" if "CALL" in signal_type else "PUT", "المبلغ": f"${fixed_bet}", "النتيجة": "WIN ✅", "الصافي": f"+${int(fixed_bet*0.85)}"
        })
        st.rerun()

with col_c2:
    if st.button("❌ قيدت هذه الصفقة وطلعت خاسرة (LOSS)"):
        now_str = datetime.now().strftime("%H:%M:%S")
        st.session_state.live_history.insert(0, {
            "توقيت الدخول": now_str, "الزوج": selected_display, "النوع": "CALL" if "CALL" in signal_type else "PUT", "المبلغ": f"${fixed_bet}", "النتيجة": "LOSS ❌", "الصافي": f"-${int(fixed_bet)}"
        })
        st.rerun()

# حساب الإحصائيات الحقيقية للجلسة
if len(st.session_state.live_history) > 0:
    df_live = pd.DataFrame(st.session_state.live_history)
    t_trades = len(df_live)
    w_trades = len(df_live[df_live['النتيجة'] == "WIN ✅"])
    w_rate = int((w_trades / t_trades) * 100)
    
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown(f'<div class="metric-box"><h3>📊 صفقات اليوم</h3><h2>{t_trades}</h2></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-box"><h3 style="color:#38ef7d;">🎯 Win Rate الحالي</h3><h2>{w_rate}%</h2></div>', unsafe_allow_html=True)
    with c3:
        net_prof = 0
        for h in st.session_state.live_history:
            val = int(h["الصافي"].replace("+$", "").replace("-$", ""))
            net_prof += val if "+$" in h["الصافي"] else -val
        color = "#38ef7d" if net_prof >= 0 else "#ff5858"
        st.markdown(f'<div class="metric-box"><h3>💵 الصافي الحقيقي</h3><h2 style="color:{color};">${net_prof}</h2></div>', unsafe_allow_html=True)

    st.markdown("---")
    st.dataframe(df_live, use_container_width=True)
else:
    st.info("💡 بمجرد دخولك الصفقة في كوتكس بناءً على الإشارة الفوقانية، اضغط على أزرار التقييد لتسجيل نتائجك ومراقبة أرباحك الحية!")
