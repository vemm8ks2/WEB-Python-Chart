import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import io
import os
from dotenv import load_dotenv
from matplotlib import font_manager
from scripts.db_connection import create_connection

load_dotenv()

# 나이대 그룹화 함수
def age_group(age):
    if age < 20:
        return '10대'
    elif 20 <= age < 30:
        return '20대'
    elif 30 <= age < 40:
        return '30대'
    elif 40 <= age < 50:
        return '40대'
    elif 50 <= age < 60:
        return '50대'
    else:
        return '60대 이상'

def 나이대별생년분포(chart=True):
    # 한글 폰트를 설정 (예: 맑은 고딕)
    font_path = 'C:\\Windows\\Fonts\\malgun.ttf'  # 윈도우의 경우
    font_prop = font_manager.FontProperties(fname=font_path)

    # 한글 폰트를 설정
    plt.rcParams['font.family'] = font_prop.get_name()

    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute("SELECT * FROM USERS")

    fetch_order_list = cursor.fetchall()

    order_list = []

    for order in fetch_order_list:
        order_list.append([order[1]])

    df = pd.DataFrame(order_list, columns=['유저_생일'])
    # 생일에서 연도 추출
    df['유저_생일'] = pd.to_datetime(df['유저_생일'])

    # 현재 연도
    current_year = datetime.now().year

    # 나이 계산
    df['나이'] = current_year - df['유저_생일'].dt.year

    # 나이대별로 그룹화
    df['나이대'] = df['나이'].apply(age_group)

    # 나이대별 생일 수 계산
    age_group_counts = df['나이대'].value_counts()

    if not chart:
        age_group_counts = pd.DataFrame(age_group_counts)
        age_group_counts = age_group_counts.rename(columns=({'count':'명'}))
        save_folder = os.getenv("REPORT_PREPROCESS_PWD")
        return age_group_counts.to_csv(save_folder + "/나이대별생년분포.csv", encoding='utf-8')

    # 그래프 크기 설정
    plt.figure(figsize=(8, 6))

    # 막대 그래프 그리기
    sns.barplot(x=age_group_counts.index, y=age_group_counts.values, palette='Set2', hue=age_group_counts.index)

    # 그래프 제목과 라벨 설정
    plt.title("나이대별 유저 생일 분포", fontsize=16)
    plt.xlabel("나이대", fontsize=12)
    plt.ylabel("생일 수", fontsize=12)

    # 그래프 표시
    plt.tight_layout()  # 레이아웃 조정

    # 차트를 메모리 버퍼에 저장 (SVG 형식으로)
    svg_buf = io.StringIO()  # 텍스트 형식의 StringIO 버퍼 사용
    plt.savefig(svg_buf, format='svg')  # SVG 형식으로 저장
    svg_buf.seek(0)  # 버퍼의 시작 지점으로 이동

    # SVG 태그를 반환
    return svg_buf.getvalue()  # SVG XML 문자열 반환