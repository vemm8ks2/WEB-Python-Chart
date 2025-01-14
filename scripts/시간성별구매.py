import os
import pandas as pd
import io
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from matplotlib import font_manager
from scripts.db_connection import create_connection

load_dotenv()

def 시간성별구매(chart=True):
    # 한글 폰트를 설정
    font_path = 'C:\\Windows\\Fonts\\malgun.ttf'
    font_prop = font_manager.FontProperties(fname=font_path)

    # 한글 폰트를 설정
    plt.rcParams['font.family'] = font_prop.get_name()

    # 데이터베이스에서 데이터 가져오기
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
        'select o.delivered_at, u.gender, oi.quantity from orders o, users u, order_items oi where o.user_id = u.id and o.id = oi.order_id')

    fetch_order_list = cursor.fetchall()

    order_list = []

    for order in fetch_order_list:
        order_list.append([order[0], order[1], order[2]])

        # DataFrame 생성
    order_df = pd.DataFrame(order_list, columns=['배송일', '성별', '수량'])

    # 'OTHER' 성별 제외
    order_df = order_df[order_df['성별'] != 'OTHER']

    # 배송일 컬럼을 datetime 형식으로 변환
    order_df['배송일'] = pd.to_datetime(order_df['배송일'])

    # 시간별로 그룹화: '배송일'을 시간대로 그룹화
    order_df['시간'] = order_df['배송일'].dt.hour

    # 성별별 수량 합계 구하기
    order_grouped = order_df.groupby(['시간', '성별'])['수량'].sum().unstack().reset_index()

    # NaN 값을 0으로 채우기
    order_grouped = order_grouped.fillna(0)

    if not chart:
        save_folder = os.getenv("REPORT_PREPROCESS_PWD")
        return order_grouped.to_csv(save_folder + "/시간성별구매.csv", index=False, encoding='utf-8')

    # 시간별 성별 구매 수량을 누적 막대 그래프로 나타내기
    plt.figure(figsize=(12, 6))

    # 성별별 수량을 누적해서 그리기
    bars_male = plt.bar(order_grouped['시간'], order_grouped['MALE'], label='남성', color='lightblue')
    bars_female = plt.bar(order_grouped['시간'], order_grouped['FEMALE'], label='여성', bottom=order_grouped['MALE'],
                          color='lightcoral')

    # 중간에 수치 표시
    for i, bar in enumerate(bars_male):
        yval = bar.get_height()
        if yval > 0:
            plt.text(bar.get_x() + bar.get_width() / 2, yval / 2, int(yval), ha='center', va='center', fontsize=10,
                     color='black')

    for i, bar in enumerate(bars_female):
        yval = bar.get_height()
        if yval > 0:
            plt.text(bar.get_x() + bar.get_width() / 2, order_grouped['MALE'][i] + yval / 2, int(yval), ha='center',
                     va='center', fontsize=10, color='black')

    # 그래프 제목 및 축 레이블 설정
    plt.title('시간별 성별에 따른 구매 수량', fontsize=16)
    plt.xlabel('시간', fontsize=12)
    plt.ylabel('구매 수량', fontsize=12)
    plt.legend(title='성별')
    plt.xticks(range(7, 22))

    # 차트를 메모리 버퍼에 저장 (SVG 형식으로)
    svg_buf = io.StringIO()  # 텍스트 형식의 StringIO 버퍼 사용
    plt.savefig(svg_buf, format='svg')  # SVG 형식으로 저장
    svg_buf.seek(0)  # 버퍼의 시작 지점으로 이동

    # SVG 태그를 반환
    return svg_buf.getvalue()  # SVG XML 문자열 반환