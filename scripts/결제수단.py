import io
import pandas as pd
import os
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from matplotlib import font_manager

from scripts.db_connection import create_connection

load_dotenv()

def 결제수단():
    # DB 연결
    connection = create_connection()
    connection.start_transaction()
    cursor = connection.cursor()

    cursor.execute("select * from orders")
    order_list = cursor.fetchall()

    # 데이터를 합칠 리스트
    data_frames = []

    for order in order_list:
        data_frames.append([order[2]])

    # 모든 데이터프레임을 하나로 합침
    data = pd.DataFrame(data_frames, columns=['결제 수단'])

    data['결제 수단'] = data['결제 수단'].replace('DIGITAL_WALLET', '간편 결제')
    data['결제 수단'] = data['결제 수단'].replace('CREDIT_OR_DEBIT_CARD', '신용/체크카드 결제')
    data['결제 수단'] = data['결제 수단'].replace('DEPOSIT_WITHOUT_PASSBOOK', '무통장 입금')

    # 결제 수단별 주문 건수
    payment_method_count = data['결제 수단'].value_counts()

    # 한글 폰트를 설정 (예: 맑은 고딕)
    font_path = 'C:\\Windows\\Fonts\\malgun.ttf'  # 윈도우의 경우
    font_prop = font_manager.FontProperties(fname=font_path)

    # 한글 폰트를 설정
    plt.rcParams['font.family'] = font_prop.get_name()

    # 결제 수단별 주문 건수 시각화
    plt.figure(figsize=(10, 6))
    payment_method_count.plot(kind='bar', color='skyblue')

    # 제목 및 레이블 설정
    plt.title('결제 수단별 주문 건수 분석')  # 제목 수정
    plt.xlabel('')
    plt.ylabel('주문 수')
    plt.xticks(rotation=0)

    # 차트를 메모리 버퍼에 저장 (SVG 형식으로)
    svg_buf = io.StringIO()  # 텍스트 형식의 StringIO 버퍼 사용
    plt.savefig(svg_buf, format='svg')  # SVG 형식으로 저장
    svg_buf.seek(0)  # 버퍼의 시작 지점으로 이동

    # SVG 태그를 반환
    return svg_buf.getvalue()  # SVG XML 문자열 반환