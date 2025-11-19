import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

# 1. 파일 로드 및 데이터 전처리 함수
@st.cache_data
def load_data(file_path):
    """CSV 파일을 로드하고 컬럼명을 정리하며 데이터 타입을 변환합니다."""
    
    # Pathlib을 사용하여 현재 스크립트 위치 기준, 루트 폴더의 파일 경로를 찾습니다.
    # pages/analysis_page.py -> pages/ -> 루트 폴더/dubbongispig.csv
    data_file_path = Path(__file__).parent.parent / file_path 
    
    if not data_file_path.exists():
        st.error(f"❌ 파일을 찾을 수 없습니다: {data_file_path}. CSV 파일이 **루트 폴더**에 있는지 확인해 주세요.")
        return pd.DataFrame()
        
    # 파일 인코딩 처리
    try:
        df = pd.read_csv(data_file_path, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(data_file_path, encoding='cp949')
        except Exception:
            df = pd.read_csv(data_file_path, encoding='euc-kr')

    # 컬럼명 클리닝
    column_mapping = {
        '순번': 'ID', '품종': 'Species', '시도': 'Sido', '시군': 'Sigungu', '년도': 'Year',
        '전체호수': 'Total_Farms', '전체두수': 'Total_Heads',
        '5000두 이상(호수)': '5k_up_Farms', '5000두 이상(두수)': '5k_up_Heads',
        '5000두-2000두 이상(호수)': '5k_2k_Farms', '5000두-2000두 이상(두수)': '5k_2k_Heads',
        '2000두-1000두 이상(호수)': '2k_1k_Farms', '2000두-1000두 이상(두수)': '2k_1k_Heads',
        '1000두-500두 이상(호수)': '1k_500_Farms', '1000두-500두 이상(두수)': '1k_500_Heads',
        '500두-100두 이상(호수)': '500_100_Farms', '500두-100두 이상(두수)': '500_100_Heads',
        '100두-20두 이상(호수)': '100_20_Farms', '100두-20두 이상(두수)': '100_20_Heads',
        '20두-0두 이상(호수)': '20_0_Farms', '20두-0두 이상(두수)': '20_0_Heads',
    }
    df.rename(columns=column_mapping, inplace=True)

    # 데이터 타입 변환
    numeric_cols = [col for col in df.columns if 'Heads' in col or 'Farms' in col or col in ['ID', 'Year']]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
    return df

# 2. Plotly 막대 그래프 생성 함수 (1등 빨강, 그라데이션 적용)
def create_custom_bar_chart(df_filtered, year):
    
    df_plot = df_filtered.groupby('Sigungu')['Total_Heads'].sum().reset_index()
    df_plot = df_plot.sort_values(by='Total_Heads', ascending=False)
    
    if df_plot.empty:
        return go.Figure()

    # 색상 설정 로직
    colors = []
    max_heads = df_plot['Total_Heads'].max()
    gradient_colors = px.colors.sequential.Blues_r
    non_max_count = (df_plot['Total_Heads'] < max_heads).sum()
    gradient_index = 0
    
    for heads in df_plot['Total_Heads']:
        if heads == max_heads:
            colors.append('#FF0000')  # 1등(최대값)은 빨간색
        else:
            if non_max_count > 0:
                color_index = int(gradient_index / non_max_count * (len(gradient_colors) - 1))
                colors.append(gradient_colors[color_index])
                gradient_index += 1
            else:
                colors.append('#3776ab')
            

    # Plotly 인터랙티브 막대 그래프 생성
    fig = go.Figure(data=[go.Bar(
        x=df_plot['Sigungu'],
        y=df_plot['Total_Heads'],
        marker_color=colors,
        text=df_plot['Total_Heads'].apply(lambda x: f'{x:,}'),
        textposition='auto',
        hovertemplate="**%{x}**<br>전체 두수: %{y:,.0f}두<extra></extra>",
    )])

    # 레이아웃 설정
    fig.update_layout(
        title=f"**{year}년도 시군별 전체 두수 순위** (총 {df_plot['Total_Heads'].sum():,}두)",
        xaxis_title="시/군",
        yaxis_title="전체 두수 (두)",
        xaxis={'categoryorder': 'total descending'}
    )
    
    return fig

# 3. Streamlit 메인 앱 구성
def main():
    st.set_page_config(layout="wide", page_title="가축 사육 현황 분석 (Streamlit/Plotly)")
    
    st.title("🐇 가축 사육 현황 분석 (토끼) - Streamlit 대시보드")
    st.markdown("---")

    # 데이터 로드
    df = load_data('dubbongispig.csv')

    if df.empty:
        st.stop()
        
    data_years = df['Year'].unique()
    latest_year = df['Year'].max()
    
    # --- 1. Pandas 데이터 분석 요약 ---
    st.header("1. 꼼꼼한 Pandas 데이터 분석 요약")
    
    col1, col2, col3 = st.columns(3)
    
    col1.metric("데이터 레코드 수", f"{len(df):,}개")
    col2.metric("총 두수 (전 기간 합산)", f"{df['Total_Heads'].sum():,}두")
    col3.metric("데이터 기간", f"{min(data_years)}년 ~ {latest_year}년")

    st.subheader(f"규모별 사육 현황 ({latest_year}년 기준)")
    df_latest_summary = df[df['Year'] == latest_year]
    
    if not df_latest_summary.empty:
        size_cols_heads = [col for col in df_latest_summary.columns if 'Heads' in col and col != 'Total_Heads']
        size_summary = df_latest_summary[size_cols_heads].sum().sort_values(ascending=False)
        
        st.dataframe(
            size_summary.rename(lambda x: x.replace('_Heads', ' 이상 두수')),
            column_config={"value": st.column_config.NumberColumn("두수 (전체 합)", format="%d두")},
            use_container_width=True,
            hide_index=False
        )
    
    st.markdown("---")


    # --- 2. Plotly 시각화: 요청하신 2024년 10월 기록 시각화 ---
    st.header("2. Plotly 인터랙티브 막대 그래프 시각화")

    # **(A) 요청하신 2024년 필터링 결과**
    requested_year = 2024 # 2025년에서 2024년으로 변경
    st.subheader(f"✅ 요청하신 **{requested_year}년도 10월** 기록 시각화 (데이터를 {requested_year}년으로 필터링)")
    
    df_2024 = df[df['Year'] == requested_year] 
    fig_2024 = create_custom_bar_chart(df_2024, f"{requested_year}년")
    
    if fig_2024.data:
        st.plotly_chart(fig_2024, use_container_width=True)
        st.caption("✅ **큰 값부터 정렬**, **1등**은 **빨간색**, **나머지**는 **파란색 계열 그라데이션**으로 처리되었습니다.")
    else:
        # 이 부분이 실행되는 경우는 없어야 하지만, 혹시 모를 에러 방지
        st.error(f"❌ **{requested_year}년도** 데이터가 존재하지 않아 그래프를 그릴 수 없습니다.")

    st.markdown("---")
    
    # 이전 단계에서 보여주던 2024년 시연 그래프는 요청하신 2024년 필터링으로 대체되어 제거했습니다.
    

if __name__ == '__main__':
    main()
