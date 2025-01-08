import pandas as pd
import io
import matplotlib.pyplot as plt
from matplotlib import font_manager
from scripts.db_connection import create_connection


def 카테고리성별구매():
    # 한글 폰트를 설정 (예: 맑은 고딕)
    font_path = 'C:\\Windows\\Fonts\\malgun.ttf'  # 윈도우의 경우
    font_prop = font_manager.FontProperties(fname=font_path)

    # 한글 폰트를 설정
    plt.rcParams['font.family'] = font_prop.get_name()

    # 데이터베이스에서 데이터 가져오기
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
        'select u.gender, c.name, oi.quantity from orders o, users u, order_items oi, products p, category c where o.user_id = u.id and o.id = oi.order_id and oi.product_id = p.id and p.category_id = c.id')
    fetch_order_list = cursor.fetchall()

    order_list = []

    for order in fetch_order_list:
        order_list.append([order[0], order[1], order[2]])

        # DataFrame 생성
    order_df = pd.DataFrame(order_list, columns=['성별', '카테고리', '수량'])

    # 'OTHER' 성별 제외
    order_df = order_df[order_df['성별'] != 'OTHER']

    # 성별과 카테고리별로 수량을 집계
    category_gender_sales = order_df.groupby(['카테고리', '성별'])['수량'].sum().unstack(fill_value=0)

    # 성별별 색상 지정 (보기 좋은 색상)
    color_map = {
        'MALE': '#4A90E2',  # 부드러운 Piston Blue
        'FEMALE': '#D84B8D',  # 부드러운 Piston Pink
    }

    # 그래프 생성
    ax = category_gender_sales.plot(kind='bar', stacked=True, figsize=(20, 7), color=[
        color_map.get(gender, '#9B59B6') for gender in category_gender_sales.columns
    ])

    # 각 성별 그래프 안에 값 추가 (0은 제외)
    for p in ax.patches:
        height = p.get_height()
        if height > 0:  # 수량이 0인 경우 값 표시하지 않기
            x = p.get_x() + p.get_width() / 2
            y = p.get_y() + height / 2
            ax.text(x, y, f'{height:.0f}', ha='center', va='center', fontsize=10, color='black')

    # 제목 및 레이블 설정
    plt.title('카테고리별 성별 구매 분석', fontsize=16)
    plt.xlabel('카테고리', fontsize=12)
    plt.ylabel('구매 수량', fontsize=12)
    # 카테고리 레이블 각도 조절
    plt.xticks(rotation=45, ha='right')

    # 차트를 메모리 버퍼에 저장 (SVG 형식으로)
    svg_buf = io.StringIO()  # 텍스트 형식의 StringIO 버퍼 사용
    plt.savefig(svg_buf, format='svg')  # SVG 형식으로 저장
    svg_buf.seek(0)  # 버퍼의 시작 지점으로 이동

    # SVG 태그를 반환
    return svg_buf.getvalue()  # SVG XML 문자열 반환