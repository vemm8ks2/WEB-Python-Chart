import pandas as pd
import io
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker
from matplotlib import font_manager
from scripts.db_connection import create_connection


def 월별매출():
    # 한글 폰트를 설정 (예: 맑은 고딕)
    font_path = 'C:\\Windows\\Fonts\\malgun.ttf'  # 윈도우의 경우
    font_prop = font_manager.FontProperties(fname=font_path)

    # 한글 폰트를 설정
    plt.rcParams['font.family'] = font_prop.get_name()

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("select delivered_at, total_price from orders")

    fetch_order_list = cursor.fetchall()

    order_list = []

    for order in fetch_order_list:
        order_list.append([order[0], order[1]])

    order_df = pd.DataFrame(order_list, columns=['배송일', '매출'])

    order_df['배송일'] = pd.to_datetime(order_df['배송일'])
    order_df['월별'] = order_df['배송일'].dt.to_period('M')
    order_df_monthly = order_df.groupby('월별')['매출'].sum().reset_index()
    order_df_monthly['월별'] = order_df_monthly['월별'].astype(str)
    order_df_monthly['매출'] = order_df_monthly['매출'].astype(int)

    # 월별 매출 데이터를 선 그래프로 표시하는 코드
    plt.figure(figsize=(25, 15))
    ax = plt.gca()  # 현재 축을 가져옴

    # 실제 월별 데이터 시각화
    plt.plot(order_df_monthly['월별'], order_df_monthly['매출'], color='#1f77b4', marker='o')

    # 그래프 제목 및 레이블 설정 (글씨 크기 키우기)
    plt.title('월 마다 매출', fontsize=20)  # 제목 크기 키움
    plt.xlabel('날짜', fontsize=20)  # x축 레이블 크기 키움
    plt.ylabel('매출', fontsize=20)  # y축 레이블 크기 키움

    # y축의 천 단위 구분 기호 추가
    plt.gca().yaxis.set_major_formatter(ticker.FuncFormatter(lambda x, _: f'{int(x):,}'))

    # y축 그리드 선 제거
    ax.grid(axis='y')

    # x축과 y축 눈금 레이블 크기 조정
    plt.xticks(fontsize=20)  # x축 눈금 크기 키움
    plt.yticks(fontsize=20)  # y축 눈금 크기 키움

    # 그래프 출력
    plt.xticks(rotation=45)  # x축 레이블 회전 (가독성 향상)
    plt.tight_layout()  # 레이아웃 자동 조정

    # 차트를 메모리 버퍼에 저장 (SVG 형식으로)
    svg_buf = io.StringIO()  # 텍스트 형식의 StringIO 버퍼 사용
    plt.savefig(svg_buf, format='svg')  # SVG 형식으로 저장
    svg_buf.seek(0)  # 버퍼의 시작 지점으로 이동

    # SVG 태그를 반환
    return svg_buf.getvalue()  # SVG XML 문자열 반환