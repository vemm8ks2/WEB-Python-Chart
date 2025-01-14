import pandas as pd
import io
import os
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from dotenv import load_dotenv
from matplotlib import rcParams
from statsmodels.tsa.arima.model import ARIMA
from scripts.db_connection import create_connection

load_dotenv()

def 월별매출예측_ARIMA(chart=True):
    rcParams['font.family'] = 'Malgun Gothic'  # 윈도우에서 기본적으로 제공되는 한글 글꼴

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM orders")

    fetch_order_list = cursor.fetchall()

    order_list = []

    for order in fetch_order_list:
        order_list.append([order[1], order[6]])

    order_df = pd.DataFrame(order_list, columns=['배송일', '결제금액'])

    order_df['배송일'] = pd.to_datetime(order_df['배송일'])
    order_df['월별'] = order_df['배송일'].dt.to_period('M')
    order_df_monthly = order_df.groupby('월별')['결제금액'].sum().reset_index()

    order_df_monthly['월별'] = order_df_monthly['월별'].dt.to_timestamp()

    model = ARIMA(order_df_monthly['결제금액'], order=(2, 1, 0))
    model_fit = model.fit()

    forecast = model_fit.forecast(steps=6)
    future_dates = pd.date_range(order_df_monthly['월별'].max(), periods=7, freq='ME')[1:]

    if not chart:
        data = pd.DataFrame({'월별':future_dates, '매출액 예측':forecast})
        # 기존 데이터와 미래 예측 데이터 결합
        df_combined = pd.concat([order_df_monthly[['월별', '결제금액']], data], ignore_index=True)

        save_folder = os.getenv("REPORT_PREPROCESS_PWD")
        return df_combined.to_csv(save_folder + "/월별매출예측_ARIMA.csv", index=False, encoding='utf-8')

    # 시각화
    plt.figure(figsize=(10, 6))
    ax = plt.gca()  # 현재 축을 가져옴

    # 실제 월별 데이터 시각화
    plt.plot(order_df_monthly['월별'], order_df_monthly['결제금액'], label='실제 데이터', color='#1f77b4')

    # 예측된 월별 데이터 시각화
    plt.plot(future_dates, forecast, label='예측', color='#d62728')

    # 그래프 제목 및 레이블 설정
    plt.title('과거 월별 총 결제금액 및 미래 예측', fontsize=15)
    plt.xlabel('월', fontsize=12)
    plt.ylabel('결제금액 (원)', fontsize=12)

    # y축의 천 단위 구분 기호 추가
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))

    # y축 그리드 선 제거
    ax.grid(axis='x')

    # 차트를 메모리 버퍼에 저장 (SVG 형식으로)
    svg_buf = io.StringIO()  # 텍스트 형식의 StringIO 버퍼 사용
    plt.savefig(svg_buf, format='svg')  # SVG 형식으로 저장
    svg_buf.seek(0)  # 버퍼의 시작 지점으로 이동

    # SVG 태그를 반환
    return svg_buf.getvalue()  # SVG XML 문자열 반환