import streamlit as st
import pandas as pd

# إعدادات الصفحة
st.set_page_config(page_title="QUOTEX AI DASHBOARD", page_icon="📈", layout="wide")

# عنوان الموقع
st.title("🏆 QUOTEX AI LIVE TRADING DASHBOARD")
st.markdown("---")

# بيانات تجريبية حية
if 'history' not in st.session_state:
    st.session_state.history = [
        {"time": "14:30", "pair": "EUR/USD", "type": "CALL 🟢", "result": "WIN ✅"},
        {"time": "14:45", "pair": "USD/JPY", "type": "PUT 🔴", "result": "WIN ✅"},
        {"time": "15:02", "pair": "GBP/USD", "type": "CALL 🟢", "result": "LOSS ❌"},
    ]

# حساب الإحصائيات آلياً
history_df = pd.DataFrame(st.session_state.history)
total_trades = len(history_df)
wins = len(history_df[history_df['result'] == "WIN ✅"])
win_rate = int((wins / total_trades) * 100) if total_trades > 0 else 0

# عرض المؤشرات في كروت مزيانة
col1, col2, col3 = st.columns(3)
with col1:
    st.metric(label="📊 إجمالي الصفقات", value=total_trades)
with col2:
    st.metric(label="✅ الصفقات الناجحة", value=wins)
with col3:
    st.metric(label="🎯 نسبة النجاح (Win Rate)", value=f"{win_rate}%")

st.markdown("---")

# سجل الصفقات الأخيرة
st.subheader("🕒 سجل الصفقات الأخيرة")
st.dataframe(history_df, use_container_width=True)

# زر التحديث
if st.button("🔄 تحديث البيانات الحية"):
    st.rerun()
