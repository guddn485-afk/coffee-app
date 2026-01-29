import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import os

# 0. 기본 설정
st.set_page_config(page_title="커피-리 수거 플랫폼", layout="wide", page_icon="☕")

# 구글 시트 연결
SHEET_URL = "https://docs.google.com/spreadsheets/d/1Fb15MZHNoXfBhQ8OE2zPv1flPh5ktZxi46R8L7-iw50/edit"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 1. 헤더 섹션 (로고 및 제목) ---
if os.path.exists("logo.png"):
    # 로고를 화면 너비에 맞춰 꽉 채웁니다.
    # 만약 이미지 양옆에 빈 공간이 많다면 이미지 파일을 '자르기(Crop)' 해야 합니다.
    st.image("logo.png", use_container_width=True)
else:
    st.markdown("<h1 style='text-align: center;'>☕ 커피-리 수거 플랫폼</h1>", unsafe_allow_html=True)

st.markdown("<h3 style='text-align: center; color: gray;'>환경을 생각하는 커피박 수거 서비스</h3>", unsafe_allow_html=True)

# --- 2. 상단 지표 (대시보드) ---
try:
    df = conn.read(spreadsheet=SHEET_URL, ttl=0)
except Exception as e:
    df = pd.DataFrame(columns=["카페이름", "수거량", "요청날짜"])

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("총 수거 요청", f"{len(df)}건")
with col2:
    # 데이터가 비어있을 경우를 대비한 처리
    if not df.empty and "수거량" in df.columns:
        total_kg = pd.to_numeric(df["수거량"]).sum()
    else:
        total_kg = 0
    st.metric("누적 수거량", f"{total_kg} kg")
with col3:
    num_cafes = df['카페이름'].nunique() if not df.empty else 0
    st.metric("참여 카페", f"{num_cafes}곳")

st.divider()

# --- 3. 메인 레이아웃 ---
left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("📝 수거 요청하기")
    with st.form("my_form", clear_on_submit=True):
        name = st.text_input("카페 이름", placeholder="예: 스타벅스 제주점")
        qty = st.number_input("오늘의 수거량(kg)", min_value=1, step=1)
        submit = st.form_submit_button("🚀 지금 접수하기")
        
        if submit:
            if name:
                new_data = pd.DataFrame([{"카페이름": name, "수거량": qty, "요청날짜": datetime.now().strftime("%Y-%m-%d %H:%M")}])
                updated_df = pd.concat([df, new_data], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, data=updated_df)
                st.success(f"접수가 완료되었습니다!")
                st.balloons()
                st.rerun()
            else:
                st.error("카페 이름을 입력해 주세요.")

with right_col:
    st.subheader("📢 알림 사항")
    st.info("""
    - **수거 시간:** 매일 오전 10시 ~ 오후 2시
    - **문의 사항:** 010-XXXX-XXXX (커피-리 팀)
    """)
    goal = 1000
    progress = min(float(total_kg / goal), 1.0)
    st.write(f"🌿 **목표 달성도 ({total_kg}kg / {goal}kg)**")
    st.progress(progress)

# --- 4. 관리자 메뉴 ---
st.sidebar.title("🔐 관리자 전용")
admin_pw = st.sidebar.text_input("비밀번호", type="password")
if admin_pw == "1234":
    st.divider()
    st.subheader("📊 전체 수거 목록")
    st.dataframe(df, use_container_width=True)
