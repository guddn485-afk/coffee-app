import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

SHEET_URL = "https://docs.google.com/spreadsheets/d/1Fb15MZHNoXfBhQ8OE2zPv1flPh5ktZxi46R8L7-iw50/edit"

conn = st.connection("gsheets", type=GSheetsConnection)

st.title("☕ 커피박 수거 관리 시스템")

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
            
            st.success(f"✅ {name}님 접수 완료! 현재 총 {len(updated_df)}건 저장됨")
            st.rerun()
        else:
            st.error("카페 이름을 입력해주세요.")

st.divider()
st.subheader("📊 실시간 누적 목록")
st.dataframe(conn.read(spreadsheet=SHEET_URL, ttl=0), use_container_width=True)
