import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

st.set_page_config(page_title="커피박 수거 플랫폼", layout="wide", page_icon="☕")


SHEET_URL = "https://docs.google.com/spreadsheets/d/1Fb15MZHNoXfBhQ8OE2zPv1flPh5ktZxi46R8L7-iw50/edit"
conn = st.connection("gsheets", type=GSheetsConnection)



try:
   
    left_empty, mid, right_empty = st.columns([1, 1, 1])
    with mid:
        st.image("logo.png", width=200) 
except:
    
    st.title("☕")

st.markdown("<h1 style='text-align: center;'>커피-리(Lee) 수거 플랫폼</h1>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; color: gray;'>우리의 작은 실천이 깨끗한 환경을 만듭니다.</p>", unsafe_allow_html=True)

st.title("☕ 커피-리(Lee) 수거 플랫폼")
st.caption("우리의 작은 실천이 깨끗한 환경을 만듭니다. 제주 커피박 자원순환 네트워크")


try:
    df = conn.read(spreadsheet=SHEET_URL, ttl=0)
except:
    df = pd.DataFrame(columns=["카페이름", "수거량", "요청날짜"])

# 2. 상단 지표 (대시보드 느낌)
st.divider()
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("총 수거 요청", f"{len(df)}건")
with col2:
    total_kg = df["수거량"].sum() if not df.empty else 0
    st.metric("누적 수거량", f"{total_kg} kg", delta="▲ 계속 증가 중")
with col3:
    st.metric("참여 카페", f"{df['카페이름'].nunique()}곳")

# 3. 메인 레이아웃 (좌측: 입력창 / 우측: 안내문)
st.divider()
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
                st.success(f"감사합니다! {name} 사장님, 접수가 완료되었습니다.")
                st.balloons()
                st.rerun()
            else:
                st.warning("카페 이름을 입력해 주세요!")

with right_col:
    st.subheader("📢 알림 사항")
    st.info("""
    - **수거 시간:** 매일 오전 10시 ~ 오후 2시
    - **주의 사항:** 이물질이 섞이지 않도록 주의해 주세요.
    - **문의 사항:** 010-XXXX-XXXX (커피-리 팀)
    """)
    # 진행 상황바 (목표 수거량 1000kg 달성용)
    goal = 1000
    progress = min(total_kg / goal, 1.0)
    st.write(f"🌿 **목표 달성도 (현재 {total_kg}kg / 목표 {goal}kg)**")
    st.progress(progress)

# 4. 관리자 메뉴 (하단에 숨김)
st.sidebar.title("🔐 관리자 전용")
admin_pw = st.sidebar.text_input("비밀번호", type="password")
if admin_pw == "1234":
    st.divider()
    st.subheader("📊 전체 수거 목록")
    st.dataframe(df, use_container_width=True)
