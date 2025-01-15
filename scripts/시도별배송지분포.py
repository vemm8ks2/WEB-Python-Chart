import pandas as pd
import matplotlib.pyplot as plt
import os
import io
from dotenv import load_dotenv
from matplotlib import font_manager
from scripts.db_connection import create_connection

load_dotenv()

def 시도별배송지분포(chart=True):
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

    order_all = []

    for order in order_list:
        order_all.append([order[5]])

    df = pd.DataFrame(order_all, columns=['배송지'])

    # 시/도 데이터 추출
    df["시도"] = df["배송지"].str.split().str[0]  # 시/도 추출

    # 시/도별 데이터 개수 세기
    sido_counts = df["시도"].value_counts()

    if not chart:
        sido_counts = pd.DataFrame(sido_counts)
        sido_counts = sido_counts.rename(columns={'count':'배송지 개수'})
        save_folder = os.getenv("REPORT_PREPROCESS_PWD")
        return sido_counts.to_csv(save_folder + "/시도별배송지분포.csv", encoding='utf-8')

    # 그래프 크기를 데이터 크기에 맞게 설정
    num_regions = len(sido_counts)  # 데이터 항목 수
    plt.figure(figsize=(num_regions * 1.5, 6))  # 가로 크기를 항목 수에 비례하도록 설정

    # 막대 그래프 생성
    plt.bar(sido_counts.index, sido_counts.values, color='lightblue', edgecolor='black')
    plt.title('시/도별 배송지 분포', fontsize=16)
    plt.xlabel('시/도', fontsize=14)
    plt.ylabel('배송지 개수', fontsize=14)
    plt.xticks(fontsize=12)  # 라벨 각도 조정
    plt.tight_layout()

    # 차트를 메모리 버퍼에 저장 (SVG 형식으로)
    svg_buf = io.StringIO()  # 텍스트 형식의 StringIO 버퍼 사용
    plt.savefig(svg_buf, format='svg')  # SVG 형식으로 저장
    svg_buf.seek(0)  # 버퍼의 시작 지점으로 이동

    # SVG 태그를 반환
    return svg_buf.getvalue()  # SVG XML 문자열 반환