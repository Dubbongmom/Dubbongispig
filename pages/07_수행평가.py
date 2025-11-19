import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 1. 파일 로드 및 데이터 전처리 함수
@st.cache_data
def load_data(file_path):
    # CSV 파일 로드 (encoding='cp949' 또는 'euc-kr'이 일반적이나, 'utf-8'로 시도 후 에러 시 변경)
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_path, encoding='cp949')
        except Exception as e:
            st.error(f"파일 로드 중 에러 발생: {e}")
            return pd.DataFrame()

    # 컬럼명 클리닝
    column_mapping = {
        '순번': 'ID',
        '품종': 'Species',
        '시도': 'Sido',
        '시군': 'Sigungu',
        '년도': 'Year',
        '전체호수': 'Total_Farms',
        '전체두수': 'Total_Heads',
        '5000두 이상(호수)': '5k_up_Farms',
        '5000두 이상(두수)': '5k_up_Heads',
        '5000두-2000두 이상(호수)': '5k_2k_Farms',
        '5000두-2000두 이상(두수)': '5k_2k_Heads',
        '2000두-1000두 이상(호수)': '2k_1k_Farms',
        '2000두-1000두 이상(두수)': '2k_1k_Heads',
        '1000두-500두 이상(호수)': '1k_500_Farms',
        '1000두-500두 이상(두수)': '1k_500_Heads',
        '500두-100두 이상(호수)': '500_100_Farms',
        '500두-100두 이상(두수)': '500_100_Heads',
        '100두-20두 이상(호수)': '100_20_Farms',
        '100두-20두 이상(두수)': '100_20_Heads',
        '20두-0두 이상(호수)': '20_0_Farms',
        '20두-0두 이상(두수)': '20_0_Heads',
    }
    df.rename(columns=column_mapping, inplace=True)

    # 데이터 타입 변환 (숫자 컬럼)
    numeric_cols = [col for col in df.columns if 'Heads' in col or 'Farms' in col or col in ['ID', 'Year']]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        
    return df

# 2. Plotly 막대 그래프 생성 함수 (요청 사항 반영)
def create_custom_bar_chart(df_filtered, title):
    
    # 막대 그래프용 데이터 집계: 시군별 전체두수 합산
    df_plot = df_filtered.groupby('Sigungu')['Total_Heads'].sum().reset_index()
    df_plot = df_plot.sort_values(by='Total_Heads', ascending=False)
    
    # 데이터가 비어있는 경우 처리
    if df_plot.empty:
        st.warning(f"⚠️ **{title}**에 해당하는 데이터가 없습니다. (필터링 조건: {title} 10월)")
        return go.Figure()

    # 5. 그래프 색상 설정 (1등은 빨간색, 나머지는 그라데이션)
    # Plotly 기본 Blue 그라데이션 (2등부터 사용)
    num_bars = len(df_plot)
    colors = ['#FF0000'] + px.colors.sequential.Sunset_r[1:num_bars] 
    
    # 1등이 하나가 아닐 수 있으므로, 최대값과 같은 값은 모두 빨간색으로 처리
    max_heads = df_plot['Total_Heads'].max()
    
    # 동률 1등 처리: 최대값과 같은 값은 모두 빨간색, 나머지는 그라데이션
    colors = []
    gradient_colors = px.colors.sequential.Blues_r
    
    # 그라데이션을 적용할 나머지 항목의 수
    non_max_count = (df_plot['Total_Heads'] < max_heads).sum()
    gradient_index = 0
    
    for heads in df_plot['Total_Heads']:
        if heads == max_heads:
            colors.append('#FF0000')  # 1등은 빨간색
        else:
            # 나머지 항목에 그라데이션 적용 (Blues_r을 역순으로 사용해 큰 값에 진한 색)
            if non_max_count > 0:
                color_index = int(gradient_index / non_max_count * (len(gradient_colors) - 1))
                colors.append(gradient_colors[color_index])
                gradient_index += 1
            else:
                # 안전 장치 (모든 값이 동일할 경우)
                colors.append('#3776ab')
            

    # Plotly 막대 그래프 생성
    fig = go.Figure(data=[go.Bar(
        x=df_plot['Sigungu'],
        y=df_plot['Total_Heads'],
        marker_color=colors,
        text=df_plot['Total_Heads'],
        textposition='auto',
        hovertemplate="**%{x}**<br>전체 두수: %{y:,.0f}두<extra></extra>",
    )])

    # 레이아웃 설정
    fig.update_layout(
        title=f"**{title}** - 시군별 전체 두수 순위 (총 {df_plot['Total_Heads'].sum():,}두)",
        xaxis_title="시/군",
        yaxis_title="전체 두수 (두)",
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        xaxis={'categoryorder': 'total descending'} # X축을 값에 따라 정렬 (큰 값부터)
    )
    
    return fig

# 3. Streamlit 메인 앱 구성
def main():
    st.set_page_config(layout="wide", page_title="Pandas/Plotly 분석 - 가축 사육 현황")
    
    st.title("🐇 가축 사육 현황 (토끼) 파일 분석 및 시각화")
    st.markdown("---")

    # 데이터 로드
    df = load_data('dubbongispig.csv')

    if df.empty:
        st.stop()

    # --- 1. 종합 분석 (Pandas) ---
    st.header("1. 꼼꼼한 Pandas 데이터 분석 요약")
    
    # 데이터 구조 요약
    col1, col2, col3 = st.columns(3)
    
    total_heads_all_years = df['Total_Heads'].sum()
    total_farms_all_years = df['Total_Farms'].sum()
    data_years = df['Year'].unique()
    
    col1.metric("총 데이터 레코드 수", f"{len(df):,}개")
    col2.metric("총 두수 (전 기간 합산)", f"{total_heads_all_years:,}두")
    col3.metric("데이터 기간", f"{min(data_years)}년 ~ {max(data_years)}년")

    st.subheader("💡 주요 통계 및 규모별 분포")
    
    # Top 5 시군 (전 기간)
    top5_sigungu = df.groupby('Sigungu')['Total_Heads'].sum().nlargest(5).index.tolist()
    st.info(f"**전 기간 (2017년~2024년) 기준, 전체 두수가 가장 많은 상위 5개 시/군:** {', '.join(top5_sigungu)}")

    # 규모별 사육 현황 (2024년 기준)
    df_2024 = df[df['Year'] == 2024]
    if not df_2024.empty:
        size_cols_heads = [col for col in df_2024.columns if 'Heads' in col and col != 'Total_Heads']
        size_summary = df_2024[size_cols_heads].sum().sort_values(ascending=False)
        
        st.dataframe(
            size_summary.rename(lambda x: x.replace('_Heads', ' 이상 두수')),
            column_config={
                "index": st.column_config.TextColumn("사육 규모", help="규모별 토끼 수"),
                "value": st.column_config.NumberColumn("두수 (전체 합)", format="%d두"),
            },
            use_container_width=True
        )
    
    st.markdown("---")


    # --- 2. 2025년도 10월 기록 시각화 요청 처리 (4, 5번 요청) ---
    st.header("2. Plotly 인터랙티브 막대 그래프")

    # **(A) 요청하신 2025년 필터링 (데이터 없음)**
    requested_year = 2025
    st.subheader(f"📊 요청하신 **{requested_year}년도 10월 기록** (시군별 전체 두수)")
    
    df_2025 = df[df['Year'] == requested_year]

    if df_2025.empty:
        st.error(f"❌ **{requested_year}년도** 데이터가 파일에 존재하지 않습니다. (파일에는 {min(data_years)}년 ~ {max(data_years)}년 데이터만 포함)")

    # Plotly 시각화 (데이터가 없으므로 빈 그래프를 반환하고 경고 메시지 출력)
    fig_2025 = create_custom_bar_chart(df_2025, f"{requested_year}년 기록")
    st.plotly_chart(fig_2025, use_container_width=True)

    st.markdown("---")

    # **(B) 실제 작동 시연 및 분석을 위한 2024년 데이터 시각화**
    latest_year = df['Year'].max()
    st.subheader(f"✅ 시각화 작동 시연 (데이터가 있는 **최신 연도: {latest_year}년** 기준)")
    
    df_latest = df[df['Year'] == latest_year]
    fig_latest = create_custom_bar_chart(df_latest, f"{latest_year}년 기록")
    
    st.plotly_chart(fig_latest, use_container_width=True)
    st.caption("✅ **큰 값부터 정렬**되었으며, **1등은 빨간색**으로, **나머지는 파란색 계열의 그라데이션**으로 처리되었습니다.")
    

if __name__ == '__main__':
    # Streamlit Cloud에서 파일 구조를 인식하게 하려면 main.py 또는 pages 폴더 내 파일을 메인으로 실행해야 합니다.
    # 사용자가 pages 폴더 밑에 코드를 요청했으므로 이 파일을 메인으로 가정합니다.
    main()
