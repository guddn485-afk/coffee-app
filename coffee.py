import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime, timedelta, timezone
import os

# 0. 기본 설정
st.set_page_config(page_title="커피-리 수거 플랫폼", layout="wide", page_icon="☕")

# 구글 시트 연결
SHEET_URL = "https://docs.google.com/spreadsheets/d/1Fb15MZHNoXfBhQ8OE2zPv1flPh5ktZxi46R8L7-iw50/edit"
conn = st.connection("gsheets", type=GSheetsConnection)

# --- 1. 헤더 섹션 (로고) ---
if os.path.exists("logo.png"):
    st.image("logo.png", use_container_width=True)
else:
    st.markdown("<h1 style='text-align: center;'>☕ 커피-리 수거 플랫폼</h1>", unsafe_allow_html=True)

# --- 2. 데이터 불러오기 및 대시보드 지표 ---
try:
    df = conn.read(spreadsheet=SHEET_URL, ttl=0)
    if not df.empty:
        # 수거량 숫자 변환
        df["수거량"] = pd.to_numeric(df["수거량"], errors='coerce').fillna(0)
except Exception as e:
    df = pd.DataFrame(columns=["카페이름", "수거량", "요청날짜"])

col1, col2, col3 = st.columns(3)
with col1:
    st.metric("총 수거 요청", f"{len(df)}건")
with col2:
    total_kg = df["수거량"].sum() if not df.empty else 0
    st.metric("누적 수거량", f"{total_kg} kg")
with col3:
    num_cafes = df['카페이름'].nunique() if not df.empty else 0
    st.metric("참여 카페", f"{num_cafes}곳")

st.divider()

# --- 3. [수정됨] 수거 트렌드 차트 (에러 방지 로직 적용) ---
if not df.empty:
    st.subheader("📊 일별 수거 트렌드")
    df_chart = df.copy()
    
    # errors='coerce'를 써서 날짜가 아닌 데이터는 NaT(빈값)로 바꿉니다.
    df_chart['날짜_dt'] = pd.to_datetime(df_chart['요청날짜'], errors='coerce')
    
    # 날짜 변환에 성공한 데이터만 남깁니다.
    df_chart = df_chart.dropna(subset=['날짜_dt'])
    
    if not df_chart.empty:
        df_chart['날짜'] = df_chart['날짜_dt'].dt.date
        trend_data = df_chart.groupby('날짜')['수거량'].sum().reset_index()
        st.bar_chart(trend_data.set_index('날짜'), color="#4B2C20")
    else:
        st.info("차트를 그릴 수 있는 날짜 데이터가 없습니다.")

# --- 4. 메인 레이아웃 (입력 폼) ---
left_col, right_col = st.columns([1, 1])

with left_col:
    st.subheader("📝 수거 요청하기")
    with st.form("my_form", clear_on_submit=True):
        name = st.text_input("카페 이름", placeholder="예: 스타벅스 제주점")
        qty = st.number_input("오늘의 수거량(kg)", min_value=1, step=1)
        submit = st.form_submit_button("🚀 지금 접수하기")
        
        if submit:
            if name:
                kst = timezone(timedelta(hours=9))
                now_kst = datetime.now(kst).strftime("%Y-%m-%d %H:%M")
                new_data = pd.DataFrame([{"카페이름": name, "수거량": qty, "요청날짜": now_kst}])
                updated_df = pd.concat([df, new_data], ignore_index=True)
                conn.update(spreadsheet=SHEET_URL, data=updated_df)
                st.success("접수가 완료되었습니다!")
                st.balloons()
                st.rerun()
            else:
                st.error("카페 이름을 입력해 주세요.")

with right_col:
    st.subheader("📢 알림 사항")
    st.info("- **수거 시간:** 매일 오전 10시 ~ 오후 2시")
    
    goal = 1000
    progress = min(float(total_kg / goal), 1.0) if goal > 0 else 0
    st.write(f"🌿 **목표 달성도 ({total_kg}kg / {goal}kg)**")
    st.progress

    with right_col:
    st.subheader("📢 알림 사항")
    st.info("- **수거 시간:** 매일 오전 10시 ~ 오후 2시")
    
    # 목표 달성 계산
    goal = 1000
    progress_value = min(float(total_kg / goal), 1.0) if goal > 0 else 0
    
    # 공식 문서 스타일 적용: 텍스트를 프로그레스 바 위에 바로 표시
    progress_text = f"🌿 **목표 달성도: {total_kg}kg / {goal}kg ({int(progress_value * 100)}%)**"
    st.progress(progress_value, text=progress_text)
