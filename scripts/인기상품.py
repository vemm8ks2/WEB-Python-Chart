import io
import os
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from matplotlib import font_manager
from scripts.db_connection import create_connection

load_dotenv()

def 인기상품(chart=True):
    # 한글 폰트를 설정 (예: 맑은 고딕)
    font_path = 'C:\\Windows\\Fonts\\malgun.ttf'  # 윈도우의 경우
    font_prop = font_manager.FontProperties(fname=font_path)

    # 한글 폰트를 설정
    plt.rcParams['font.family'] = font_prop.get_name()

    # DB 연결
    connection = create_connection()
    connection.start_transaction()
    cursor = connection.cursor()

    cursor.execute("select quantity, title from order_items o join products p on o.product_id = p.id")
    order_list = cursor.fetchall()

    # 데이터를 합칠 리스트
    data_frames = []

    for order in order_list:
        data_frames.append([order[0], order[1]])

    # 모든 데이터프레임을 하나로 합침
    data = pd.DataFrame(data_frames, columns=['수량', '상품명'])

    # 인기 상품 분석 (상품명별 판매 수량)
    popular_products = data.groupby('상품명')['수량'].sum().sort_values(ascending=False)

    # 내림차순으로 정렬 후 상위 10개 상품 선택
    top_10_products = popular_products.head(10)

    if not chart:
        save_folder = os.getenv("REPORT_PREPROCESS_PWD")
        return top_10_products.to_csv(save_folder + "/인기상품.csv", encoding='utf-8')

    # 수평 롤리팝 차트로 시각화
    plt.figure(figsize=(10, 8))

    # 수평선 그리기
    plt.hlines(top_10_products.index, 0, top_10_products.values, color='#B39DDB', linewidth=3)

    # 원 마커 그리기
    plt.plot(top_10_products.values, top_10_products.index, 'o', color='#B39DDB', markersize=8)

    # 원 마커 위에 판매 수량 텍스트 표시
    for i, value in enumerate(top_10_products.values):
        # 텍스트를 원 마커 바로 위에 표시
        plt.text(value, i + 0.2, str(value), ha='center', va='center', fontweight='bold')

    # 제목 및 레이블 추가
    plt.title('상위 10개 인기 상품', fontsize=14, fontweight='bold')
    plt.xlabel('판매 수량', fontsize=12)
    plt.ylabel('상품명', fontsize=12)

    # x축의 범위 조정 (0보다 작은 값이 포함되지 않도록 설정)
    plt.xlim(left=0)

    # x축을 2씩 증가하도록 설정
    plt.xticks(range(0, int(top_10_products.max()) + 3, 5))

    plt.tight_layout()

    # 차트를 메모리 버퍼에 저장 (SVG 형식으로)
    svg_buf = io.StringIO()  # 텍스트 형식의 StringIO 버퍼 사용
    plt.savefig(svg_buf, format='svg')  # SVG 형식으로 저장
    svg_buf.seek(0)  # 버퍼의 시작 지점으로 이동

    # SVG 태그를 반환
    return svg_buf.getvalue()  # SVG XML 문자열 반환