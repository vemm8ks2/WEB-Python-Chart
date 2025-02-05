import matplotlib.pyplot as plt
import io
import os
import pandas as pd
from dotenv import load_dotenv
from matplotlib import font_manager
from scripts.db_connection import create_connection

load_dotenv()

def 유저별주문(chart=True):
    # 한글 폰트를 설정 (예: 맑은 고딕)
    font_path = 'C:\\Windows\\Fonts\\malgun.ttf'  # 윈도우의 경우
    font_prop = font_manager.FontProperties(fname=font_path)

    # 한글 폰트를 설정
    plt.rcParams['font.family'] = font_prop.get_name()

    connection = create_connection()
    connection.start_transaction()
    cursor = connection.cursor()

    cursor.execute("select username from orders o join users u on o.user_id = u.id")
    order_list = cursor.fetchall()

    # 데이터를 합칠 리스트
    data_frames = []

    for order in order_list:
        data_frames.append(order[0])

    # 모든 데이터프레임을 하나로 합침
    data = pd.DataFrame(data_frames, columns=['유저 아이디'])

    # 유저별 주문 건수 (내림차순 정렬)
    user_order_count = data.groupby('유저 아이디').size().sort_values(ascending=False)

    # 유저별 주문 건수 상위 10개를 원 그래프로 시각화
    top_user_order_count = user_order_count.head(10)

    if not chart:
        top_user_order_count = pd.DataFrame(top_user_order_count)
        top_user_order_count = top_user_order_count.rename(columns=({0: '주문건수'}))
        save_folder = os.getenv("REPORT_PREPROCESS_PWD")
        return top_user_order_count.to_csv(save_folder + "/유저별주문.csv", encoding='utf-8')

    # 퍼센트와 주문 건수를 표시하는 함수 정의
    def func(pct, allvals):
        absolute = round(pct / 100. * sum(allvals))
        return f"{absolute}건\n({pct:.1f}%)"

    # 색상 팔레트
    colors = ['#FFB3BA', '#FFCCBA', '#FFEB99', '#D9F9B7', '#C2F0C2', '#A8E6CF', '#80C6E1', '#A3B9FF', '#B2A7FF',
              '#C39BD3']

    # 원 그래프 (파이 차트)
    plt.figure(figsize=(8, 8))
    plt.pie(top_user_order_count,
            labels=top_user_order_count.index,
            autopct=lambda pct: func(pct, top_user_order_count),
            startangle=90,
            colors=colors)
    plt.title('유저별 주문 건수 상위 10명')

    # 차트를 메모리 버퍼에 저장 (SVG 형식으로)
    svg_buf = io.StringIO()  # 텍스트 형식의 StringIO 버퍼 사용
    plt.savefig(svg_buf, format='svg')  # SVG 형식으로 저장
    svg_buf.seek(0)  # 버퍼의 시작 지점으로 이동

    # SVG 태그를 반환
    return svg_buf.getvalue()  # SVG XML 문자열 반환