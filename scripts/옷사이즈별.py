import io
import os
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from matplotlib import font_manager
from scripts.db_connection import create_connection

load_dotenv()

def 옷사이즈별(chart=True):
    # 한글 폰트를 설정 (예: 맑은 고딕)
    font_path = 'C:\\Windows\\Fonts\\malgun.ttf'  # 윈도우의 경우
    font_prop = font_manager.FontProperties(fname=font_path)

    # 한글 폰트를 설정
    plt.rcParams['font.family'] = font_prop.get_name()

    connection = create_connection()
    connection.start_transaction()
    cursor = connection.cursor()

    cursor.execute("select * from order_items")
    order_list = cursor.fetchall()

    # 데이터를 합칠 리스트
    data_frames = []

    for order in order_list:
        data_frames.append([order[3], order[2]])

    # 모든 데이터프레임을 하나로 합침
    order_items = pd.DataFrame(data_frames, columns=['사이즈', '수량'])

    order_items = order_items[['사이즈', '수량']]

    # 사이즈 230, 240, 250을 모두 같은 타입으로 변경
    order_items['사이즈'] = order_items['사이즈'].apply(lambda x: int(x) if x in ['230', '240', '250'] else x)

    # 옷사이즈별이므로 신발 사이즈는 drop해준다
    clothes = order_items.groupby('사이즈')['수량'].sum().reset_index().drop(order_items.index[0:3])

    # 모든 옷 수량 더하기
    clothes_total = clothes.set_index('사이즈')['수량'].sum()

    # 사이즈를 인덱스로 변경
    clothes = clothes.set_index('사이즈')

    # 백분율 구하기
    clothes_total_size = ((clothes / clothes_total) * 100)

    if not chart:
        shoes_total_size = clothes_total_size.rename(columns=({'수량':'판매율'}))
        save_folder = os.getenv("REPORT_PREPROCESS_PWD")
        return shoes_total_size.to_csv(save_folder + "/옷사이즈별.csv", encoding='utf-8')

    # 새로운 파스텔톤 색상 11개
    new_pastel_colors = [
        '#FFECBA',  # 부드러운 베이지색
        '#BAFFFB',  # 밝은 바다색
        '#C4FFBA',  # 연한 라임색
        '#FFBABA'  # 부드러운 빨간색
    ]

    # 데이터의 길이에 맞게 색상 수 조정
    colors_to_use = new_pastel_colors[:len(clothes_total_size)]

    # 파이 차트로 옷 사이즈별 판매율 시각화
    plt.figure(figsize=(8, 8))
    clothes_total_size.plot(kind='pie', autopct='%1.1f%%', startangle=90, colors=colors_to_use, subplots=True)
    plt.title('옷 사이즈별 판매율')
    plt.ylabel('')  # y축 라벨 제거

    plt.tight_layout()

    # 차트를 메모리 버퍼에 저장 (SVG 형식으로)
    svg_buf = io.StringIO()  # 텍스트 형식의 StringIO 버퍼 사용
    plt.savefig(svg_buf, format='svg')  # SVG 형식으로 저장
    svg_buf.seek(0)  # 버퍼의 시작 지점으로 이동

    # SVG 태그를 반환
    return svg_buf.getvalue()  # SVG XML 문자열 반환