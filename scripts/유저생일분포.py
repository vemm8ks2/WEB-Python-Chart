import io
import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from dotenv import load_dotenv
from matplotlib import font_manager
from scripts.db_connection import create_connection

load_dotenv()

def 유저생일분포(chart=True):
    # 한글 폰트를 설정 (예: 맑은 고딕)
    font_path = 'C:\\Windows\\Fonts\\malgun.ttf'  # 윈도우의 경우
    font_prop = font_manager.FontProperties(fname=font_path)

    # 한글 폰트를 설정
    plt.rcParams['font.family'] = font_prop.get_name()

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM users")

    fetch_order_list = cursor.fetchall()

    order_list = []

    for order in fetch_order_list:
        order_list.append([order[1]])

    df = pd.DataFrame(order_list, columns=['유저_생일'])

    # 생일에서 연도 추출
    df['연도'] = pd.to_datetime(df['유저_생일']).dt.year

    # 연도별 생일 수 계산
    year_counts = df['연도'].value_counts().sort_index()

    year_counts.index = year_counts.index.astype(int)

    if not chart:
        year_counts = pd.DataFrame(year_counts)
        year_counts = year_counts.rename(columns=({'count':'명'}))
        save_folder = os.getenv("REPORT_PREPROCESS_PWD")
        return year_counts.to_csv(save_folder + "/유저생일분포.csv", encoding='utf-8')

    # 그래프 크기 설정
    plt.figure(figsize=(12, 6))

    # 막대 그래프 그리기
    sns.barplot(x=year_counts.index, y=year_counts.values, palette='viridis', hue=year_counts.index)

    # 그래프 제목과 라벨 설정
    plt.title("연도별 유저 생일 분포", fontsize=16)
    plt.xlabel("연도", fontsize=12)
    plt.ylabel("생일 수", fontsize=12)

    # 그래프 표시
    plt.xticks(rotation=45)  # x축 레이블 회전
    plt.tight_layout()  # 레이아웃 조정

    # 차트를 메모리 버퍼에 저장 (SVG 형식으로)
    svg_buf = io.StringIO()  # 텍스트 형식의 StringIO 버퍼 사용
    plt.savefig(svg_buf, format='svg')  # SVG 형식으로 저장
    svg_buf.seek(0)  # 버퍼의 시작 지점으로 이동

    # SVG 태그를 반환
    return svg_buf.getvalue()  # SVG XML 문자열 반환
