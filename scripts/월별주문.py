import matplotlib.pyplot as plt
import os
import io
import pandas as pd
from dotenv import load_dotenv
from matplotlib import font_manager
from scripts.db_connection import create_connection

load_dotenv()

def 월별주문(chart=True):
    # 한글 폰트를 설정 (예: 맑은 고딕)
    font_path = 'C:\\Windows\\Fonts\\malgun.ttf'  # 윈도우의 경우
    font_prop = font_manager.FontProperties(fname=font_path)

    # 한글 폰트를 설정
    plt.rcParams['font.family'] = font_prop.get_name()

    # DB 연결
    connection = create_connection()
    connection.start_transaction()
    cursor = connection.cursor()

    cursor.execute("select * from orders")
    order_list = cursor.fetchall()

    # 데이터를 합칠 리스트
    data_frames = []

    for order in order_list:
        data_frames.append([order[1]])

    # 모든 데이터프레임을 하나로 합침
    data = pd.DataFrame(data_frames, columns=['배송일'])

    # 배송일을 datetime 형식으로 변환
    data['배송일'] = pd.to_datetime(data['배송일'])

    # 월별 주문 건수
    monthly_order_count = data.groupby(data['배송일'].dt.to_period('M')).size()

    if not chart:
        monthly_order_count = pd.DataFrame(monthly_order_count)
        monthly_order_count = monthly_order_count.rename(columns=({0: '주문건수'}))
        save_folder = os.getenv("REPORT_PREPROCESS_PWD")
        return monthly_order_count.to_csv(save_folder + "/월별주문.csv", encoding='utf-8')

    # 월별 주문 건수 시각화
    plt.figure(figsize=(12, 6))

    # 막대 차트 그리기
    monthly_order_count.plot(kind='bar', color='#ff7a36', edgecolor='black', linewidth=1.2)

    # 제목과 축 라벨 설정
    plt.title('월별 주문 건수', fontsize=16, fontweight='bold', color='#333333')
    plt.xlabel('날짜', fontsize=14, fontweight='bold', color='#555555')
    plt.ylabel('주문 건수', fontsize=14, fontweight='bold', color='#555555')
    plt.xticks(rotation=45, ha='right', fontsize=12)
    plt.yticks(fontsize=12)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.gca().set_facecolor('#f9f9f9')
    plt.tight_layout()

    # 차트를 메모리 버퍼에 저장 (SVG 형식으로)
    svg_buf = io.StringIO()  # 텍스트 형식의 StringIO 버퍼 사용
    plt.savefig(svg_buf, format='svg')  # SVG 형식으로 저장
    svg_buf.seek(0)  # 버퍼의 시작 지점으로 이동

    # SVG 태그를 반환
    return svg_buf.getvalue()  # SVG XML 문자열 반환