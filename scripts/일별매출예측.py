import io
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from matplotlib import rcParams
from scripts.db_connection import create_connection


def 일별매출예측():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM orders")

    fetch_order_list = cursor.fetchall()

    order_list = []

    for order in fetch_order_list:
        order_list.append([order[1], order[6]])

    order_df = pd.DataFrame(order_list, columns=['배송일', '결제금액'])

    order_df['배송일'] = pd.to_datetime(order_df['배송일'])
    order_df_by_day = order_df.groupby(order_df['배송일'].dt.date)['결제금액'].sum().reset_index()
    order_df_by_day['배송일'] = pd.to_datetime(order_df_by_day['배송일'])

    order_df_by_day['일'] = (
                pd.to_datetime(order_df_by_day['배송일']) - pd.to_datetime(order_df_by_day['배송일']).min()).dt.days

    # ========================
    # 모델 생성
    # ========================
    # 독립 변수 (경과된 일수), 종속 변수 (매출액)
    X = order_df_by_day[['일']]  # 독립 변수
    y = order_df_by_day['결제금액']  # 종속 변수

    # 훈련 세트와 테스트 세트로 분할
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # 선형 회귀 모델 생성
    model = LinearRegression()

    # 모델 훈련
    model.fit(X_train, y_train)

    # 예측
    y_pred = model.predict(X_test)

    # ========================
    # 미래 예측
    # ========================
    # **미래 예측을 위한 날짜 범위 설정**
    future_dates = pd.date_range(order_df_by_day['배송일'].max(), periods=50, freq='D')  # 50일 후까지 예측

    # 경과된 일수를 계산
    future_days_since = (pd.to_datetime(future_dates) - pd.to_datetime(order_df_by_day['배송일'].min())).days

    # **future_days_since를 NumPy 배열로 변환한 후 reshape() 적용**
    future_days_since = np.array(future_days_since).reshape(-1, 1)

    # 미래 날짜에 대한 예측값 계산
    future_sales_pred = model.predict(pd.DataFrame(future_days_since, columns=['일']))

    # **기존 데이터와 미래 예측 데이터 결합**
    df_future = pd.DataFrame({'배송일': future_dates, '매출액 예측': future_sales_pred})

    # 기존 데이터와 미래 예측 데이터 결합
    df_combined = pd.concat([order_df_by_day[['배송일', '결제금액']], df_future], ignore_index=True)

    # ========================
    # 시각화
    # ========================
    rcParams['font.family'] = 'Malgun Gothic'  # 윈도우에서 기본적으로 제공되는 한글 글꼴

    # 일별 예측 그래프
    plt.figure(figsize=(20, 7))
    ax = plt.gca()  # 현재 축을 가져옴

    plt.plot(order_df_by_day['배송일'], order_df_by_day['결제금액'], label='실제 매출액')  # 기존 매출액 데이터
    plt.plot(order_df_by_day['배송일'], model.predict(order_df_by_day[['일']]), label='예측 매출액', linestyle='--')
    plt.plot(df_combined['배송일'], df_combined['매출액 예측'], label='예측 매출액', linestyle='--', color='red')  # 미래 예측 매출액 데이터

    plt.title(f"일별 매출액 예측\n[ R²(결정계수): {r2_score(y_test, y_pred)},  MSE: {mean_squared_error(y_test, y_pred)} ]")
    plt.xlabel('날짜')
    plt.ylabel('매출액')

    plt.legend()
    plt.xticks(pd.date_range(df_combined['배송일'].min(), df_combined['배송일'].max(), freq='MS'), rotation=45)
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))

    plt.grid(True)

    # 차트를 메모리 버퍼에 저장 (SVG 형식으로)
    svg_buf = io.StringIO()  # 텍스트 형식의 StringIO 버퍼 사용
    plt.savefig(svg_buf, format='svg')  # SVG 형식으로 저장
    svg_buf.seek(0)  # 버퍼의 시작 지점으로 이동

    # SVG 태그를 반환
    return svg_buf.getvalue()  # SVG XML 문자열 반환