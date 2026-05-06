import streamlit as st
import json
import os
from datetime import datetime
from lib.fund_service import FundService

st.set_page_config(page_title="基金限购监控", layout="wide")

fund_service = FundService()
DATA_FILE = "monitored_funds.json"
SEARCH_HISTORY_FILE = "search_history.json"
ADD_HISTORY_FILE = "add_history.json"

# 加载数据函数
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

def load_search_history():
    if os.path.exists(SEARCH_HISTORY_FILE):
        try:
            with open(SEARCH_HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_search_history(history):
    with open(SEARCH_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

def load_add_history():
    if os.path.exists(ADD_HISTORY_FILE):
        try:
            with open(ADD_HISTORY_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_add_history(history):
    with open(ADD_HISTORY_FILE, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# 标签页
tab1, tab2, tab3 = st.tabs(["基金监控", "搜索基金", "历史记录"])

with tab1:
    st.title("基金限购监控")
    
    # 加载基金数据
    funds = load_funds()
    
    # 刷新按钮
    if st.button("刷新"):
        st.rerun()
    
    # 添加基金表单
    with st.expander("添加基金", expanded=False):
        with st.form("add_form"):
            code = st.text_input("基金代码（6位）", key="add_code")
            submitted = st.form_submit_button("确定")
            if submitted and code:
                if code in funds:
                    st.warning("已存在")
                else:
                    info = fund_service.get_fund_limit(code)
                    if info:
                        funds.append(code)
                        save_funds(funds)
                        # 记录添加历史
                        add_history = load_add_history()
                        add_history.append({
                            "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "基金代码": info.code,
                            "基金名称": info.name,
                            "日限购": f"{info.daily_limit:,.0f}" if info.daily_limit and info.daily_limit < 1e12 else "无限额",
                            "状态": info.status
                        })
                        save_add_history(add_history)
                        st.success(f"已添加: {info.name}")
                        st.rerun()
                    else:
                        st.error("未找到")
    
    # 显示基金列表
    if not funds:
        st.info("点击上方'添加基金'添加基金")
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

with tab2:
    st.title("搜索基金")
    
    search_term = st.text_input("输入基金名称或代码搜索", key="search_term")
    
    if st.button("搜索") and search_term:
        try:
            df = fund_service.search_funds(search_term)
            if not df.empty:
                # 记录搜索历史
                search_history = load_search_history()
                for _, r in df.iterrows():
                    search_history.append({
                        "搜索时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        "搜索关键词": search_term,
                        "基金代码": r['基金代码'],
                        "基金简称": r['基金简称'],
                        "申购状态": r['申购状态']
                    })
                save_search_history(search_history)
                
                # 显示搜索结果
                st.dataframe(df[['基金代码', '基金简称', '申购状态']].head(20), use_container_width=True)
                
                # 点击添加到监控
                st.subheader("添加到监控")
                selected_code = st.selectbox("选择基金代码添加", df['基金代码'].tolist())
                if st.button("添加选中基金"):
                    funds = load_funds()
                    if selected_code in funds:
                        st.warning("已存在")
                    else:
                        info = fund_service.get_fund_limit(selected_code)
                        if info:
                            funds.append(selected_code)
                            save_funds(funds)
                            # 记录添加历史
                            add_history = load_add_history()
                            add_history.append({
                                "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                                "基金代码": info.code,
                                "基金名称": info.name,
                                "日限购": f"{info.daily_limit:,.0f}" if info.daily_limit and info.daily_limit < 1e12 else "无限额",
                                "状态": info.status
                            })
                            save_add_history(add_history)
                            st.success(f"已添加: {info.name}")
                            st.rerun()
            else:
                st.info("未找到相关基金")
        except Exception as e:
            st.error(f"搜索出错: {e}")

with tab3:
    st.title("历史记录")
    
    history_tab1, history_tab2 = st.tabs(["搜索历史", "添加历史"])
    
    with history_tab1:
        st.subheader("搜索历史")
        search_history = load_search_history()
        if search_history:
            st.dataframe(search_history, use_container_width=True)
            if st.button("清空搜索历史"):
                save_search_history([])
                st.success("已清空")
                st.rerun()
        else:
            st.info("暂无搜索历史")
    
    with history_tab2:
        st.subheader("添加历史")
        add_history = load_add_history()
        if add_history:
            st.dataframe(add_history, use_container_width=True)
            if st.button("清空添加历史"):
                save_add_history([])
                st.success("已清空")
                st.rerun()
        else:
            st.info("暂无添加历史")
