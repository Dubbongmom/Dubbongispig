import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd
import math

# 기본 설정
st.set_page_config(page_title="서울 관광지도", page_icon="🗺️", layout="wide")

# 헤더
st.title("🗺️ 외국인이 좋아하는 서울 관광지 Top 10")
st.markdown("서울의 대표 명소들을 지도와 함께 살펴보고, 나만의 여행 일정을 만들어보세요! 🌸")

# 관광지 데이터
locations = [
    {"name": "경복궁", "lat": 37.579617, "lon": 126.977041,
     "desc": "조선시대의 대표 궁궐로, 한국의 역사와 문화를 느낄 수 있는 명소입니다.",
     "subway": "3호선 경복궁역"},
    {"name": "명동", "lat": 37.563757, "lon": 126.982684,
     "desc": "쇼핑과 길거리 음식의 천국으로 외국인 관광객이 가장 많이 찾는 곳입니다.",
     "subway": "4호선 명동역"},
    {"name": "남산타워", "lat": 37.551169, "lon": 126.988227,
     "desc": "서울의 중심에서 시내 전경을 한눈에 볼 수 있는 명소입니다.",
     "subway": "4호선 명동역"},
    {"name": "북촌한옥마을", "lat": 37.582604, "lon": 126.983998,
     "desc": "전통 한옥이 밀집된 지역으로, 한국의 고즈넉한 분위기를 느낄 수 있습니다.",
     "subway": "3호선 안국역"},
    {"name": "인사동", "lat": 37.574011, "lon": 126.984834,
     "desc": "한국 전통문화와 예술이 살아있는 거리로, 전통 찻집과 갤러리가 많습니다.",
     "subway": "3호선 안국역"},
    {"name": "홍대", "lat": 37.556316, "lon": 126.922623,
     "desc": "젊음과 예술의 거리로, 음악, 패션, 자유분위기가 공존합니다.",
     "subway": "2호선 홍대입구역"},
    {"name": "동대문디자인플라자(DDP)", "lat": 37.566495, "lon": 127.009044,
     "desc": "미래적인 건축물과 전시, 야경이 아름다운 서울의 랜드마크입니다.",
     "subway": "2호선 동대문역사문화공원역"},
    {"name": "청계천", "lat": 37.570157, "lon": 126.978577,
     "desc": "도심 속의 힐링 산책로로, 낮과 밤 모두 다른 매력을 느낄 수 있습니다.",
     "subway": "1호선 종각역"},
    {"name": "롯데월드타워", "lat": 37.512544, "lon": 127.102567,
     "desc": "123층 초고층 타워로 전망대, 쇼핑몰, 수족관이 한곳에 모여 있습니다.",
     "subway": "2호선 잠실역"},
    {"name": "이태원", "lat": 37.534849, "lon": 126.994416,
     "desc": "다양한 문화와 세계 각국의 음식을 즐길 수 있는 다국적 거리입니다.",
     "subway": "6호선 이태원역"}
]

# 지도 생성
m = folium.Map(location=[37.5665, 126.9780], zoom_start=12)

# 빨간색 마커 추가
for loc in locations:
    popup_html = f"""
    <b>{loc['name']}</b><br>
    {loc['desc']}<br>
    🚇 {loc['subway']}
    """
    folium.Marker(
        [loc["lat"], loc["lon"]],
        popup=popup_html,
        tooltip=loc["name"],
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(m)

# 지도 표시 (70%)
st_data = st_folium(m, width=630, height=420)

# 관광지 요약 테이블
st.subheader("📍 관광지 요약")
df = pd.DataFrame(
    [{"명소": loc["name"], "가까운 전철역": loc["subway"], "설명": loc["desc"]} for loc in locations]
)
st.dataframe(df, use_container_width=True, hide_index=True)

# 일정 생성기
st.subheader("🧳 나만의 여행 일정 만들기")
days = st.slider("여행 일수를 선택하세요 (1~3일)", 1, 3, 2)

# 일정 나누기
per_day = math.ceil(len(locations) / days)
schedule = [locations[i:i+per_day] for i in range(0, len(locations), per_day)]

for i, day in enumerate(schedule, start=1):
    st.markdown(f"### 📅 Day {i}")
    for loc in day:
        st.markdown(f"- **{loc['name']}** ({loc['subway']}) — {loc['desc']}")

# 하단 표시 제거 (Streamlit 메뉴/푸터 숨김)
hide_streamlit_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    </style>
"""
st.markdown(hide_streamlit_style, unsafe_allow_html=True)
