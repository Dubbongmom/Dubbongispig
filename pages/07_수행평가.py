import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 파일 로드 및 데이터 전처리 함수
@st.cache_data
def load_data(file_path):
    """CSV 파일을 로드하고 컬럼명을 정리하며 데이터 타입을 변환합니다."""
    
    # 파일 인코딩 처리 (utf-8 시도 후 cp949 또는 euc-kr 시도)
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except FileNotFoundError:
        # 파일 경로 에러가 발생하면 Streamlit에서 에러 메시지 출력 후 빈 DataFrame 반환
        st.error(f"❌ 파일을 찾을 수 없습니다: {file_path}. CSV 파일이 루트 폴더에 있는지 확인해 주세요.")
        return pd.DataFrame()
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_path, encoding='cp949')
        except Exception:
            df = pd.read_csv(file_path, encoding='euc-kr')

    # 컬럼명 클리닝 (가독성 및 사용 편의성 향상)
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

    # 데이터 타입 변환
    numeric_cols = [col for col in df.columns if 'Heads' in col or 'Farms' in col or col in ['ID', 'Year']]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
    return df

# 2. Plotly 막대 그래프 생성 함수 (큰 값 정렬, 1등 빨강, 나머지 그라데이션)
def create_custom_bar_chart(df_filtered, year):
    
    # 시군별 전체두수 합산 및 큰 값부터 정렬
    df_plot = df_filtered.groupby('Sigungu')['Total_Heads'].sum().reset_index()
    df_plot = df_plot.sort_values(by='Total_Heads', ascending=False)
    
    if df_plot.empty:
        return go.Figure()

    # 색상 설정 로직
    colors = []
    max_heads = df_plot['Total_Heads'].max()
    
    # 그라데이션 시퀀스: 파란색 계열을 사용하며, 큰 값에 진한 색 적용 (Blues_r)
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
        xaxis={'categoryorder': 'total descending'} # X축을 값에 따라 정렬
    )
    
    return fig

# 3. Streamlit 메인 앱 구성
def main():
    st.set_page_config(layout="wide", page_title="가축 사육 현황 분석 (Streamlit/Plotly)")
    
    st.title("🐇 가축 사육 현황 분석 (토끼) - Streamlit 대시보드")
    st.markdown("---")

    # 데이터 로드 (상위 폴더에 있는 CSV 파일을 지정)
    df = load_data('../dubbongispig.csv')

    if df.empty:
        st.stop()
        
    data_years = df['Year'].unique()
    
    # --- 1. Pandas 데이터 분석 요약 ---
    st.header("1. 꼼꼼한 Pandas 데이터 분석 요약")
    
    col1, col2, col3 = st.columns(3)
    
    col1.metric("데이터 레코드 수", f"{len(df):,}개")
    col2.metric("총 두수 (전 기간 합산)", f"{df['Total_Heads'].sum():,}두")
    col3.metric("데이터 기간", f"{min(data_years)}년 ~ {max(data_years)}년")

    st.subheader("규모별 사육 현황 (최신 연도 기준)")
    # 최신 연도 기준 규모별 사육 현황 테이블
    latest_year = df['Year'].max()
    df_latest_summary = df[df['Year'] == latest_year]
    
    if not df_latest_summary.empty:
        size_cols_heads = [col for col in df_latest_summary.columns if 'Heads' in col and col != 'Total_Heads']
        size_summary = df_latest_summary[size_cols_heads].sum().sort_values(ascending=False)
        
        st.dataframe(
            size_summary.rename(lambda x: x.replace('_Heads', ' 이상 두수')),
            column_config={
                "index": st.column_config.TextColumn("사육 규모", help="규모별 토끼 수"),
                "value": st.column_config.NumberColumn("두수 (전체 합)", format="%d두"),
            },
            use_container_width=True,
            height=300
        )
    
    st.markdown("---")


    # --- 2. Plotly 시각화 ---
    st.header("2. Plotly 인터랙티브 막대 그래프 시각화")

    # **(A) 요청하신 2025년 필터링 결과**
    requested_year = 2025
    st.subheader(f"⚠️ 요청하신 **{requested_year}년도 10월** 기록 시각화")
    
    # 10월 필터링이 가능하도록 연월 컬럼을 만들어야 하나, CSV 파일에 월 정보가 없으므로 연도만 필터링합니다.
    df_2025 = df[df['Year'] == requested_year] 
    fig_2025 = create_custom_bar_chart(df_2025, f"{requested_year}년")
    
    if fig_2025.data:
        st.plotly_chart(fig_2025, use_container_width=True)
    else:
        st.error(f"❌ **{requested_year}년도** 데이터가 파일에 존재하지 않아 그래프를 그릴 수 없습니다. (데이터 범위: {min(data_years)}년 ~ {max(data_years)}년)")

    st.markdown("---")

    # **(B) 시각화 작동 시연 (데이터가 있는 최신 연도)**
    latest_year = df['Year'].max()
    st.subheader(f"✅ 시각화 작동 시연 (데이터가 있는 **최신 연도: {latest_year}년** 기준)")
    
    df_latest = df[df['Year'] == latest_year]
    fig_latest = create_custom_bar_chart(df_latest, latest_year)
    
    st.plotly_chart(fig_latest, use_container_width=True)
    st.caption("✅ **큰 값부터 정렬**, **1등**은 **빨간색**, **나머지**는 **파란색 계열 그라데이션**으로 처리되었습니다.")
    

if __name__ == '__main__':
    main()
