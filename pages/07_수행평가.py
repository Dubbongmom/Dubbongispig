import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 파일 로드 및 데이터 전처리 함수 (Pandas 분석의 시작)
@st.cache_data
def load_data(file_path):
    """CSV 파일을 로드하고 컬럼명을 정리하며 데이터 타입을 변환합니다."""
    # 파일 인코딩 처리
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='cp949')

    # 컬럼명 클리닝
    column_mapping = {
        '순번': 'ID', '품종': 'Species', '시도': 'Sido', '시군': 'Sigungu', '년도': 'Year',
        '전체호수': 'Total_Farms', '전체두수': 'Total_Heads',
        # 규모별 컬럼명 단순화
        '5000두 이상(호수)': '5k_up_Farms', '5000두 이상(두수)': '5k_up_Heads',
        '5000두-2000두 이상(호수)': '5k_2k_Farms', '5000두-2000두 이상(두수)': '5k_2k_Heads',
        '2000두-1000두 이상(호수)': '2k_1k_Farms', '2000두-1000두 이상(두수)': '2k_1k_Heads',
        '1000두-500두 이상(호수)': '1k_500_Farms', '1000두-500두 이상(두수)': '1k_500_Heads',
        '500두-100두 이상(호수)': '500_100_Farms', '500두-100두 이상(두수)': '500_100_Heads',
        '100두-20두 이상(호수)': '100_20_Farms', '100두-20두 이상(두수)': '100_20_Heads',
        '20두-0두 이상(호수)': '20_0_Farms', '20두-0두 이상(두수)': '20_0_Heads',
    }
    df.rename(columns=column_mapping, inplace=True)

    # 데이터 타입 변환 (숫자 컬럼)
    numeric_cols = [col for col in df.columns if 'Heads' in col or 'Farms' in col or col in ['ID', 'Year']]
    for col in numeric_cols:
        # 문자열이 섞인 경우를 대비하여 에러를 무시하고 변환, 결측치는 0으로 채움
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
    return df

# 2. Plotly 막대 그래프 생성 함수 (3, 4, 5번 요청 핵심)
def create_custom_bar_chart(df_filtered, year):
    
    # 4. 큰 값부터 막대 그래프를 그리기 위한 데이터 집계 및 정렬
    df_plot = df_filtered.groupby('Sigungu')['Total_Heads'].sum().reset_index()
    df_plot = df_plot.sort_values(by='Total_Heads', ascending=False)
    
    # 데이터가 비어있는 경우 처리 (2025년 필터링 결과)
    if df_plot.empty:
        return go.Figure()

    # 5. 그래프 색상 설정 (1등은 빨간색, 나머지는 그라데이션)
    colors = []
    max_heads = df_plot['Total_Heads'].max()
    
    # Plotly 기본 Blue 그라데이션 시퀀스를 사용
    gradient_colors = px.colors.sequential.Blues_r
    non_max_count = (df_plot['Total_Heads'] < max_heads).sum()
    gradient_index = 0
    
    for heads in df_plot['Total_Heads']:
        if heads == max_heads:
            colors.append('#FF0000')  # 1등은 빨간색
        else:
            # 나머지 항목에 그라데이션 적용: 큰 값일수록 진한 파란색
            if non_max_count > 0:
                # 0부터 len(gradient_colors)-1 범위로 정규화하여 인덱스 사용
                color_index = int(gradient_index / non_max_count * (len(gradient_colors) - 1))
                colors.append(gradient_colors[color_index])
                gradient_index += 1
            else:
                colors.append('#3776ab') # 안전 장치
            

    # Plotly 인터랙티브 막대 그래프 생성
    fig = go.Figure(data=[go.Bar(
        x=df_plot['Sigungu'],
        y=df_plot['Total_Heads'],
        marker_color=colors,
        text=df_plot['Total_Heads'].apply(lambda x: f'{x:,}'), # 텍스트에 쉼표 추가
        textposition='auto',
        hovertemplate="**%{x}**<br>전체 두수: %{y:,.0f}두<extra></extra>",
    )])

    # 레이아웃 설정
    fig.update_layout(
        title=f"**{year}년도 시군별 전체 두수 순위** (총 {df_plot['Total_Heads'].sum():,}두)",
        xaxis_title="시/군",
        yaxis_title="전체 두수 (두)",
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        xaxis={'categoryorder': 'total descending'} # X축을 값에 따라 정렬
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
        st.error("데이터 파일을 로드할 수 없거나 파일이 비어 있습니다. `dubbongispig.csv` 파일이 루트 폴더에 있는지 확인하세요.")
        st.stop()
        
    data_years = df['Year'].unique()
    
    # --- 1. 꼼꼼한 Pandas 데이터 분석 요약 ---
    st.header("1. Pandas 데이터 분석 요약")
    
    col1, col2, col3 = st.columns(3)
    
    col1.metric("데이터 레코드 수", f"{len(df):,}개")
    col2.metric("총 두수 (전 기간 합산)", f"{df['Total_Heads'].sum():,}두")
    col3.metric("데이터 기간", f"{min(data_years)}년 ~ {max(data_years)}년")

    st.subheader("지역별 사육 규모 (전 기간)")
    # 상위 10개 지역 표
    top10_sigungu = df.groupby('Sigungu')['Total_Heads'].sum().nlargest(10).reset_index()
    top10_sigungu.columns = ['시군', '전체두수 (누적)']

    st.dataframe(
        top10_sigungu,
        column_config={
            "시군": st.column_config.TextColumn("시/군"),
            "전체두수 (누적)": st.column_config.NumberColumn("전체두수 (누적)", format="%d두"),
        },
        use_container_width=True,
        hide_index=True
    )
    st.caption("2017년부터 2024년까지의 **누적 전체 두수** 기준 상위 10개 지역입니다.")
    
    st.markdown("---")


    # --- 2. Plotly 시각화 ---
    st.header("2. Plotly 시각화: 시군별 전체 두수 막대 그래프")

    # **(A) 요청하신 2025년 필터링 결과 (4번 요청)**
    requested_year = 2025
    st.subheader(f"⚠️ 요청하신 **{requested_year}년도** 기록 시각화")
    
    df_2025 = df[df['Year'] == requested_year]
    fig_2025 = create_custom_bar_chart(df_2025, requested_year)
    
    if fig_2025.data:
        st.plotly_chart(fig_2025, use_container_width=True)
    else:
        st.warning(f"❌ **{requested_year}년도** 데이터가 파일에 존재하지 않아 그래프를 그릴 수 없습니다. (파일에는 {min(data_years)}년 ~ {max(data_years)}년 데이터만 포함)")

    st.markdown("---")

    # **(B) 시각화 작동 시연 (데이터가 있는 최신 연도: 2024년)**
    latest_year = df['Year'].max()
    st.subheader(f"✅ 시각화 작동 시연 (데이터가 있는 **최신 연도: {latest_year}년** 기준)")
    
    df_latest = df[df['Year'] == latest_year]
    fig_latest = create_custom_bar_chart(df_latest, latest_year)
    
    st.plotly_chart(fig_latest, use_container_width=True)
    st.caption("✅ **큰 값부터 정렬**되었고, **1등**은 **빨간색**으로, **나머지**는 **파란색 계열 그라데이션**으로 처리되었습니다. (요청 5번 반영)")
    

if __name__ == '__main__':
    main()
