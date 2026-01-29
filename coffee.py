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
    # 데이터가 있을 경우 숫자 변환 처리
    if not df.empty:
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

# --- 3. [기능 2] 수거 트렌드 차트 ---
if not df.empty:
    st.subheader("📊 일별 수거 트렌드")
    # 날짜별로 수거량 합산 (시간 제외하고 날짜만 추출)
    df_chart = df.copy()
    df_chart['날짜'] = pd.to_datetime(df_chart['요청날짜']).dt.date
    trend_data = df_chart.groupby('날짜')['수거량'].sum().reset_index()
    
    # 막대 그래프 출력
    st.bar_chart(trend_data.set_index('날짜'), color="#4B2C20") # 커피색(브라운) 그래프


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
    st.progress(progress)

# --- 5. [기능 1] 관리자 메뉴 (데이터 수정/삭제) ---
st.sidebar.title("🔐 관리자 전용")
admin_pw = st.sidebar.text_input("비밀번호", type="password")

if admin_pw == "1234":
    st.divider()
    st.subheader("⚙️ 데이터 관리 (수정 및 삭제)")
    st.write("💡 표에서 직접 내용을 수정하거나, 행을 선택 후 'Delete' 키로 지울 수 있습니다.")
    
    # st.data_editor를 사용하여 직접 수정 가능하게 함
    edited_df = st.data_editor(
        df, 
        num_rows="dynamic", # 행 추가/삭제 가능 모드
        use_container_width=True,
        key="data_editor"
    )
    
    if st.button("💾 변경사항 저장하기"):
        try:
            conn.update(spreadsheet=SHEET_URL, data=edited_df)
            st.success("구글 시트에 성공적으로 저장되었습니다!")
            st.rerun()
        except Exception as e:
            st.error(f"저장 중 오류 발생: {e}")
