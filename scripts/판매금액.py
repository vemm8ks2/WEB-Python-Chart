import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from matplotlib import font_manager
from matplotlib.lines import Line2D
from matplotlib.ticker import FuncFormatter
import io
from scripts.db_connection import create_connection


def 판매금액():
    # 한글 폰트를 설정
    font_path = 'C:\\Windows\\Fonts\\malgun.ttf'  # 윈도우의 경우
    font_prop = font_manager.FontProperties(fname=font_path)

    # 한글 폰트를 설정
    plt.rcParams['font.family'] = font_prop.get_name()

    # 데이터베이스에서 데이터 가져오기
    connection =create_connection()
    cursor = connection.cursor()
    cursor.execute('SELECT * FROM orders')

    fetch_order_list = cursor.fetchall()

    order_list = []

    for order in fetch_order_list:
        order_list.append([order[1], order[6]])

    # DataFrame 생성
    order_df = pd.DataFrame(order_list, columns=['배송일', '총 금액'])

    # 배송일 컬럼을 datetime 형식으로 변환
    order_df['배송일'] = pd.to_datetime(order_df['배송일'])

    # 기술 통계 계산
    stats = order_df['총 금액'].describe()

    # 천 단위 구분 기호 추가 함수
    def format_with_comma(x):
        return f'{x:,.0f}'

    # 전체 팔린 총 금액
    plt.figure(figsize=(12, 6))

    # 박스플롯 생성
    box_plot = sns.boxplot(data=order_df, y='총 금액', color='lightblue', fliersize=8, width=0.5, linewidth=2)

    # 박스플롯 꾸미기
    box_plot.set_title('전체 팔린 금액', fontsize=18, fontweight='bold')
    box_plot.set_ylabel('금액', fontsize=14)
    box_plot.set_xlabel('전체 판매 금액', fontsize=14)
    box_plot.grid(True, linestyle='--', alpha=0.6)
    box_plot.set_facecolor('whitesmoke')

    # 레전드 추가
    legend_labels = [
        f"최솟값: {format_with_comma(stats['min'])}",
        f"1사분위수: {format_with_comma(stats['25%'])}",
        f"중앙값: {format_with_comma(stats['50%'])}",
        f"3사분위수: {format_with_comma(stats['75%'])}",
        f"최댓값: {format_with_comma(stats['max'])}",
        f"평균: {format_with_comma(stats['mean'])}",
        f"표준편차: {format_with_comma(stats['std'])}"
    ]

    # 레전드 항목 생성
    legend_elements = [
        Line2D([0], [0], color='lightblue', lw=4, label='박스플롯'),
        Line2D([0], [0], marker='o', markersize=8, label='이상치'),
        Line2D([0], [0], lw=2, label='중앙값')
    ]

    # 박스플롯의 
    for stat in legend_labels:
        legend_elements.append(Line2D([0], [0], color='black', lw=0, label=stat))

    # 레전드 위치 설정
    plt.legend(handles=legend_elements, loc='upper right', fontsize=12)

    # y축 값에 천 단위 구분 기호 추가
    formatter = FuncFormatter(lambda x, pos: f'{x:,.0f}')
    box_plot.yaxis.set_major_formatter(formatter)

    # 레이아웃 설정
    plt.tight_layout()

    # 차트를 메모리 버퍼에 저장 (SVG 형식으로)
    svg_buf = io.StringIO()  # 텍스트 형식의 StringIO 버퍼 사용
    plt.savefig(svg_buf, format='svg')  # SVG 형식으로 저장
    svg_buf.seek(0)  # 버퍼의 시작 지점으로 이동

    # SVG 태그를 반환
    return svg_buf.getvalue()  # SVG XML 문자열 반환