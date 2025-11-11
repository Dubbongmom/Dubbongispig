import streamlit as st
import folium
from streamlit_folium import st_folium
import pandas as pd

st.set_page_config(page_title="서울 관광지도", page_icon="🗺️", layout="wide")

st.title("🗺️ 외국인이 좋아하는 서울 관광지 Top 10")
st.markdown("서울의 대표적인 명소들을 Folium 지도로 만나보세요! 🌸")

# 서울 관광명소 데이터 (위도, 경도, 설명)
locations = [
    {"name": "경복궁 (Gyeongbokgung Palace)", "lat": 37.579617, "lon": 126.977041, "desc": "조선시대의 대표 궁궐 🇰🇷"},
    {"name": "명동 (Myeongdong)", "lat": 37.563757, "lon": 126.982684, "desc": "쇼핑과 길거리 음식의 천국 🛍️"},
    {"name": "남산타워 (N Seoul Tower)", "lat": 37.551169, "lon": 126.988227, "desc": "서울의 전망 명소 🌆"},
    {"name": "북촌한옥마을 (Bukchon Hanok Village)", "lat": 37.582604, "lon": 126.983998, "desc": "전통과 현대의 조화 🏯"},
    {"name": "인사동 (Insadong)", "lat": 37.574011, "lon": 126.984834, "desc": "한국 전통문화 거리 🎎"},
    {"name": "홍대 (Hongdae)", "lat": 37.556316, "lon": 126.922623, "desc": "젊음과 예술의 거리 🎶"},
    {"name": "동대문디자인플라자 (DDP)", "lat": 37.566495, "lon": 127.009044, "desc": "미래적 디자인의 명소 🛸"},
    {"name": "청계천 (Cheonggyecheon Stream)", "lat": 37.570157, "lon": 126.978577, "desc": "도심 속 힐링 산책로 🌿"},
    {"name": "롯데월드타워 (Lotte World Tower)", "lat": 37.512544, "lon": 127.102567, "desc": "서울의 초고층 랜드마크 🏙️"},
    {"name": "이태원 (Itaewon)", "lat": 37.534849, "lon": 126.994416, "desc": "다문화와 음식의 거리 🌍"}
]

# 지도 생성
m = folium.Map(location=[37.5665, 126.9780], zoom_start=12)

# 마커 추가 (빨간색)
for loc in locations:
    folium.Marker(
        [loc["lat"], loc["lon"]],
        popup=f"<b>{loc['name']}</b><br>{loc['desc']}",
        tooltip=loc["name"],
        icon=folium.Icon(color="red", icon="info-sign"),
    ).add_to(m)

# 지도 출력 (70% 크기)
st_data = st_folium(m, width=630, height=420)

# 하단에 관광지 설명 표 표시
st.subheader("📍 관광지 요약")
df = pd.DataFrame(
    [{"명소 이름": loc["name"], "설명": loc["desc"]} for loc in locations]
)
st.dataframe(df, use_container_width=True, hide_index=True)
