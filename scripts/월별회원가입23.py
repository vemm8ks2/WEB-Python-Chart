import matplotlib.pyplot as plt
import matplotlib
import io
import os
import pandas as pd
from dotenv import load_dotenv
from scripts.db_connection import create_connection

load_dotenv()

def 월별회원가입23(chart=True):
    # 한글 폰트 설정
    matplotlib.rcParams['font.family'] = 'Malgun Gothic'  # 윈도우용 폰트 (예: 'Malgun Gothic')
    matplotlib.rcParams['axes.unicode_minus'] = False  # 음수 기호가 깨지는 문제 해결
    # DB 연결
    connection = create_connection()
    connection.start_transaction()
    cursor = connection.cursor()

    cursor.execute("select * from users")
    order_list = cursor.fetchall()

    order_all = []

    for order in order_list:
        order_all.append([order[2]])

    df1 = pd.DataFrame(order_all, columns=['회원가입일'])

    df1 = df1[df1['회원가입일'].dt.year == 2023]

    # '회원가입일' 컬럼을 datetime 형식으로 변환
    df1['회원가입일'] = pd.to_datetime(df1['회원가입일'], errors='coerce')

    # '회원가입일'에서 연도와 월을 추출
    df1['년월'] = df1['회원가입일'].dt.to_period('M')

    # 월별 회원가입 수 계산
    monthly_signup = df1['년월'].value_counts().sort_index()

    if not chart:
        monthly_signup = pd.DataFrame(monthly_signup)
        monthly_signup = monthly_signup.rename(columns=({'count':'명'}))
        save_folder = os.getenv("REPORT_PREPROCESS_PWD")
        return monthly_signup.to_csv(save_folder + "/월별회원가입23.csv", encoding='utf-8')

    # 월만 추출 (연도-월에서 월만 추출)
    monthly_signup.index = monthly_signup.index.month

    # 그라데이션 색상 사용
    colors = plt.cm.Blues(monthly_signup.values / monthly_signup.max())  # 색상 맵

    # 시각화 - 바 차트 (그라데이션 색상 적용)
    plt.figure(figsize=(10, 6))
    monthly_signup.plot(kind='bar', color=colors)

    # 차트 제목 및 레이블 설정
    plt.title('2023년 월 별 회원 가입 수', fontsize=16)
    plt.xlabel('가입일(월)', fontsize=12)
    plt.ylabel('가입자 수(명)', fontsize=12)

    # x축 레이블 회전
    plt.xticks(rotation=0)

    # 그래프 표시
    plt.tight_layout()  # 레이아웃 조정 (레이블이 잘리지 않도록)

    # 차트를 메모리 버퍼에 저장 (SVG 형식으로)
    svg_buf = io.StringIO()  # 텍스트 형식의 StringIO 버퍼 사용
    plt.savefig(svg_buf, format='svg')  # SVG 형식으로 저장
    svg_buf.seek(0)  # 버퍼의 시작 지점으로 이동

    # SVG 태그를 반환
    return svg_buf.getvalue()  # SVG XML 문자열 반환