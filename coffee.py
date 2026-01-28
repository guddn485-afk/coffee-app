import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="커피박 수거 플랫폼", layout="wide")

# 1. 구글 시트 주소 (본인 것으로 유지)
SHEET_URL = "https://docs.google.com/spreadsheets/d/1Fb15MZHNoXfBhQ8OE2zPv1flPh5ktZxi46R8L7-iw50/edit"

conn = st.connection("gsheets", type=GSheetsConnection)

# --- 사이드바: 관리자 로그인 ---
st.sidebar.title("🔐 관리자 메뉴")
admin_password = st.sidebar.text_input("비밀번호를 입력하세요", type="password")

# --- 메인 화면: 누구나 보는 접수창 ---
st.title("☕ 커피박 수거 접수")
st.write("카페에서 발생한 커피박 수거를 요청해 주세요.")

with st.form("my_form", clear_on_submit=True):
    name = st.text_input("카페 이름")
    qty = st.number_input("수거량(kg)", min_value=1)
    submit = st.form_submit_button("접수하기")
    
    if submit:
        if name:
            try:
                existing_df = conn.read(spreadsheet=SHEET_URL, ttl=0)
            except:
                existing_df = pd.DataFrame(columns=["카페이름", "수거량", "요청날짜"])

            new_data = pd.DataFrame([{
                "카페이름": name, 
                "수거량": qty, 
                "요청날짜": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }])

            updated_df = pd.concat([existing_df, new_data], ignore_index=True)
            conn.update(spreadsheet=SHEET_URL, data=updated_df)
            
            st.success(f"✅ {name}님, 접수가 완료되었습니다!")
            st.balloons()
        else:
            st.error("카페 이름을 입력해주세요.")

# --- 관리자 전용 섹션: 비밀번호가 맞을 때만 보임 ---
# 비밀번호를 '1234' 대신 본인이 원하는 숫자로 바꾸세요!
if admin_password == "1234":
    st.divider()
    st.subheader("📊 [관리자 전용] 실시간 수거 목록")
    
    # 최신 데이터 읽어오기
    df = conn.read(spreadsheet=SHEET_URL, ttl=0)
    st.dataframe(df, use_container_width=True)
    
    # 간단한 통계 추가
    total_qty = df["수거량"].sum() if not df.empty else 0
    st.metric("총 수거량", f"{total_qty} kg")
else:
    # 비밀번호가 틀렸거나 입력 전일 때 안내문 (선택 사항)
    if admin_password:
        st.sidebar.error("비밀번호가 틀렸습니다.")
