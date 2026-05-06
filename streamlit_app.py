import streamlit as st
import json
import os
from lib.fund_service import FundService

st.set_page_config(page_title="基金限购监控", layout="wide")
st.title("基金限购监控")

DATA_FILE = "monitored_funds.json"
fund_service = FundService()

# 初始化
if 'msg' not in st.session_state:
    st.session_state.msg = ""

# 加载数据
def load_funds():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_funds(funds):
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(funds, f, ensure_ascii=False, indent=2)

# 按钮区域
col1, col2, col3 = st.columns([1,1,6])
with col1:
    if st.button("刷新"):
        st.rerun()
with col2:
    if st.button("添加"):
        st.session_state.show_add = True

# 添加区域
if st.session_state.get('show_add', False):
    with st.form("add_form"):
        code = st.text_input("基金代码（6位）")
        submitted = st.form_submit_button("确定")
        if submitted and code:
            funds = load_funds()
            if code in funds:
                st.session_state.msg = f'<p style="color:orange">已存在</p>'
            else:
                info = fund_service.get_fund_limit(code)
                if info:
                    funds.append(code)
                    save_funds(funds)
                    st.session_state.msg = f'<p style="color:green">已添加: {info.name}</p>'
                else:
                    st.session_state.msg = f'<p style="color:red">未找到</p>'
            st.session_state.show_add = False
            st.rerun()

# 显示消息
if st.session_state.msg:
    st.markdown(st.session_state.msg, unsafe_allow_html=True)
    st.session_state.msg = ""

# 显示基金列表
funds = load_funds()
if not funds:
    st.info("点击 添加 按钮添加基金")
else:
    cols = st.columns(3)
    for i, code in enumerate(funds):
        info = fund_service.get_fund_limit(code)
        if info:
            limit = f"{info.daily_limit:,.0f}" if info.daily_limit and info.daily_limit < 1e12 else "无限额"
            c = "orange" if info.daily_limit and info.daily_limit < 1e12 else "green"
            sc = "red" if "暂停" in info.status else "green"
            with cols[i % 3]:
                st.markdown(f"""
                **{info.name}**  
                `{info.code}`  
                <span style='color:{c}'><b>日限购: {limit}</b></span>  
                <span style='color:{sc}'>{info.status}</span>
                """, unsafe_allow_html=True)
                st.divider()
