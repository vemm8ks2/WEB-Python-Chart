import matplotlib.pyplot as plt
import io
import pandas as pd
import numpy as np
import matplotlib.ticker as ticker
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_squared_error, r2_score
from matplotlib import rcParams
from scripts.db_connection import create_connection

def 월별예측():
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM orders")

    fetch_order_list = cursor.fetchall()

    order_list = []

    for order in fetch_order_list:
        order_list.append([order[1], order[6]])

    order_df = pd.DataFrame(order_list, columns=['배송일', '결제금액'])

    order_df['배송일'] = pd.to_datetime(order_df['배송일'])
    order_df_by_month = order_df.groupby(order_df['배송일'].dt.to_period('M'))['결제금액'].sum().reset_index()

    order_df_by_month['월'] = np.arange(len(order_df_by_month))

    # ========================
    # 모델 생성
    # ========================
    # 독립 변수 (경과된 월수), 종속 변수 (매출액)
    X_monthly = order_df_by_month[['월']]  # 독립 변수
    y_monthly = order_df_by_month['결제금액']  # 종속 변수

    # 훈련 세트와 테스트 세트로 분할
    X_train_monthly, X_test_monthly, y_train_monthly, y_test_monthly = train_test_split(X_monthly, y_monthly,
                                                                                        test_size=0.2, random_state=42)

    # 다항식 차수 설정
    poly = PolynomialFeatures(degree=3)  # 3차 다항 회귀
    X_poly = poly.fit_transform(X_train_monthly)

    # 선형 회귀 모델 생성
    model_monthly = LinearRegression()

    # 모델 훈련
    model_monthly.fit(X_poly, y_train_monthly)

    # 전체 데이터에 대해 예측
    X_poly_test = poly.transform(X_test_monthly)
    y_pred_test = model_monthly.predict(X_poly_test)
    y_pred_full = model_monthly.predict(poly.transform(X_monthly))

    # ========================
    # 미래 예측
    # ========================
    # **미래 예측을 위한 월별 날짜 범위 설정**
    future_months_since = np.array(range(order_df_by_month['월'].max() + 1,
                                         order_df_by_month['월'].max() + 4)).reshape(-1, 1)  # 미래 3개월 예측

    # 미래 데이터를 다항 특성으로 변환
    x_poly_future = poly.transform(pd.DataFrame(future_months_since, columns=['월']))

    # 미래 예측값
    future_sales_pred = model_monthly.predict(x_poly_future)

    future_dates = pd.date_range(order_df_by_month['배송일'].max().start_time, periods=3, freq='ME')
    future_dates = future_dates + pd.DateOffset(months=1)

    df_future = pd.DataFrame({'배송일': future_dates.to_period('M'), '매출액 예측': future_sales_pred})

    # 기존 데이터와 미래 예측 데이터 결합
    df_combined = pd.concat([order_df_by_month[['배송일', '결제금액']], df_future], ignore_index=True)

    # 매출액 예측이 NaN인 행들 중 마지막 행 선택
    last_row = df_combined[df_combined['매출액 예측'].isna()].iloc[-1]

    # 마지막 NaN 행의 '매출액 예측' 값을 채우기 (예측 선이 이어지게 하려는 용도)
    df_combined.loc[last_row.name, '매출액 예측'] = y_pred_full[-1]

    # ========================
    # 시각화
    # ========================
    rcParams['font.family'] = 'Malgun Gothic'  # 윈도우에서 기본적으로 제공되는 한글 글꼴

    # 월별 예측 그래프
    plt.figure(figsize=(20, 7))
    ax = plt.gca()  # 현재 축을 가져옴

    # 원본 데이터와 예측 데이터 시각화
    plt.scatter(order_df_by_month['배송일'].astype(str), order_df_by_month['결제금액'], label='실제 값')
    plt.plot(order_df_by_month['배송일'].astype(str), y_pred_full, color='orange', label='예측 값 (다항 회귀)')
    plt.plot(df_combined['배송일'].astype(str), df_combined['매출액 예측'], label='예상 매출액', linestyle='--',
             color='red')  # 미래 예측 매출액 데이터

    plt.title(
        f"월별 매출액 예측\n[ R²(결정계수): {r2_score(y_test_monthly, y_pred_test)},  MSE: {mean_squared_error(y_test_monthly, y_pred_test)} ]")
    plt.xlabel('날짜')
    plt.ylabel('매출액')

    plt.legend()
    plt.xticks(rotation=45)
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))

    plt.grid(True)

    # 차트를 메모리 버퍼에 저장 (SVG 형식으로)
    svg_buf = io.StringIO()  # 텍스트 형식의 StringIO 버퍼 사용
    plt.savefig(svg_buf, format='svg')  # SVG 형식으로 저장
    svg_buf.seek(0)  # 버퍼의 시작 지점으로 이동

    # SVG 태그를 반환
    return svg_buf.getvalue()  # SVG XML 문자열 반환