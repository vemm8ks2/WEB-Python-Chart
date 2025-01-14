import io
import os
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from matplotlib import font_manager
import seaborn as sns
from scripts.db_connection import create_connection

load_dotenv()

def 여성구매(chart=True):
    # 한글 폰트를 설정 (예: 맑은 고딕)
    font_path = 'C:\\Windows\\Fonts\\malgun.ttf'  # 윈도우의 경우
    font_prop = font_manager.FontProperties(fname=font_path)

    # 한글 폰트를 설정
    plt.rcParams['font.family'] = font_prop.get_name()
    
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
        "select u.gender, p.title, oi.quantity from orders o, users u, order_items oi, products p where o.user_id = u.id and o.id = oi.order_id and oi.product_id = p.id")

    fetch_order_list = cursor.fetchall()

    order_list = []

    for order in fetch_order_list:
        order_list.append([order[0], order[1], order[2]])

    order_df = pd.DataFrame(order_list, columns=['성별', '상품명', '수량'])

    # 여성 데이터 필터링
    male_data = order_df[order_df['성별'] == 'FEMALE']

    grouped_data_male = male_data.groupby(['성별', '상품명'])['수량'].sum().reset_index()

    top_10_products_male = grouped_data_male.sort_values(['수량'], ascending=False).head(10).reset_index(drop=True)

    if not chart:
        save_folder = os.getenv("REPORT_PREPROCESS_PWD")
        return top_10_products_male.to_csv(save_folder + "/여성구매.csv", index=False, encoding='utf-8')

    # 시각화
    plt.figure(figsize=(12, 8))

    # `hue=None`을 명시적으로 설정하여 경고를 해결
    ax = sns.barplot(x='수량', y='상품명', data=top_10_products_male, palette='Reds_d', hue='상품명')

    # 제목, 레이블 설정
    plt.title('여성 상위 10개 구매 상품', fontsize=16)
    plt.xlabel('구매 수량', fontsize=12)
    plt.ylabel('상품명', fontsize=12)

    # 각 막대의 중앙에 구매 수량 표시
    for p in ax.patches:
        x_position = p.get_x() + p.get_width() / 2
        y_position = p.get_y() + p.get_height() / 2
        ax.text(x_position, y_position,
                f'{int(p.get_width())}',  # 수량 표시
                ha='center', va='center', fontsize=12, color='black')

    # 그래프 레이아웃
    plt.tight_layout()

    # 차트를 메모리 버퍼에 저장 (SVG 형식으로)
    svg_buf = io.StringIO()  # 텍스트 형식의 StringIO 버퍼 사용
    plt.savefig(svg_buf, format='svg')  # SVG 형식으로 저장
    svg_buf.seek(0)  # 버퍼의 시작 지점으로 이동

    # SVG 태그를 반환
    return svg_buf.getvalue()  # SVG XML 문자열 반환