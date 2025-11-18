import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

st.title("🚇 2025년 10월 지하철 승·하차 분석")

# CSV 불러오기
@st.cache_data
def load_data():
    return pd.read_csv("dubbongispig.csv", encoding="cp949")

df = load_data()

# 날짜 목록 만들기
df['사용일자'] = df['사용일자'].astype(str)
unique_dates = sorted(df['사용일자'].unique())

# 호선 목록
lines = sorted(df["노선명"].unique())

# 사용자 입력
col1, col2 = st.columns(2)
with col1:
    selected_date = st.selectbox("📅 날짜 선택 (2025년 10월)", unique_dates)

with col2:
    selected_line = st.selectbox("🚈 호선 선택", lines)

# 필터링
filtered = df[(df["사용일자"] == selected_date) & (df["노선명"] == selected_line)].copy()

# 승·하차 총합 계산
filtered["총승하차"] = filtered["승차총승객수"] + filtered["하차총승객수"]
filtered = filtered.sort_values("총승하차", ascending=False)

# 색상 설정: 1등은 빨간색, 나머지는 파란색 그라데이션
colors = []
blue_base = np.array([0, 0, 255])    # 파란색
red = "rgb(255,0,0)"

if len(filtered) > 0:
    for i in range(len(filtered)):
        if i == 0:
            colors.append(red)
        else:
            ratio = i / len(filtered)
            blue_tone = blue_base * (1 - ratio)
            colors.append(f"rgb({int(blue_tone[0])},{int(blue_tone[1])},{int(blue_tone[2])})")

# Plotly 그래프
fig = px.bar(
    filtered,
    x="역명",
    y="총승하차",
    title=f"{selected_date} · {selected_line} 승·하차 TOP 역",
)

# 색 적용
fig.update_traces(marker_color=colors)

fig.update_layout(
    xaxis_title="역명",
    yaxis_title="승·하차 총합",
    title_font_size=22,
    template="plotly_white",
)

st.plotly_chart(fig, use_container_width=True)

