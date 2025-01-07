import io
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager
from scripts.db_connection import create_connection

def 시간대별():
    # 한글 폰트를 설정 (예: 맑은 고딕)
    font_path = 'C:\\Windows\\Fonts\\malgun.ttf'  # 윈도우의 경우
    font_prop = font_manager.FontProperties(fname=font_path)

    # 한글 폰트를 설정
    plt.rcParams['font.family'] = font_prop.get_name()

    connection = create_connection()
    connection.start_transaction()
    cursor = connection.cursor()

    cursor.execute("select * from orders")
    order_list = cursor.fetchall()

    # 데이터를 합칠 리스트
    data_frames = []

    for order in order_list:
        data_frames.append(order[1])

    # 모든 데이터프레임을 하나로 합침
    data = pd.DataFrame(data_frames, columns=['배송일'])

    # 배송일을 datetime 형식으로 변환
    data['배송일'] = pd.to_datetime(data['배송일'])
    # 배송일에서 시간만 추출
    data['시간대'] = data['배송일'].dt.hour

    # 시간대별 주문 건수
    hourly_order_count = data.groupby('시간대').size()

    # 시간대별 주문 건수 시각화
    plt.figure(figsize=(12, 6))
    hourly_order_count.plot(kind='bar', color='lightgreen')
    plt.title('시간대별 주문 건수', fontsize=16, fontweight='bold', color='#333333')
    plt.xlabel('시간대', fontsize=14, fontweight='bold', color='#555555')
    plt.ylabel('주문 건수', fontsize=14, fontweight='bold', color='#555555')
    plt.xticks(rotation=45)
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.gca().set_facecolor('#f9f9f9')
    plt.tight_layout()

    # 차트를 메모리 버퍼에 저장 (SVG 형식으로)
    svg_buf = io.StringIO()  # 텍스트 형식의 StringIO 버퍼 사용
    plt.savefig(svg_buf, format='svg')  # SVG 형식으로 저장
    svg_buf.seek(0)  # 버퍼의 시작 지점으로 이동

    # SVG 태그를 반환
    return svg_buf.getvalue()  # SVG XML 문자열 반환