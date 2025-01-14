import io
import os
import pandas as pd
import matplotlib.pyplot as plt
from dotenv import load_dotenv
from matplotlib import font_manager
import seaborn as sns
from scripts.db_connection import create_connection

load_dotenv()

def translation(data):
    if data == 'FEMALE':
        return '여성'
    elif data == 'MALE':
        return '남성'
    elif data == 'OTHER':
        return '기타'
    else:
        return '알 수 없음'

def 성별별구매(chart=True):
    # 한글 폰트 설정
    font_path = 'C:\\Windows\\Fonts\\malgun.ttf'  # 윈도우의 경우
    font_prop = font_manager.FontProperties(fname=font_path)

    # 한글 폰트 설정
    plt.rcParams['font.family'] = font_prop.get_name()

    # 데이터 가져오기
    connection = create_connection()
    cursor = connection.cursor()
    cursor.execute(
        "select u.gender, p.title, oi.quantity from orders o, users u, order_items oi, products p where o.user_id = u.id and o.id = oi.order_id and oi.product_id = p.id")

    fetch_order_list = cursor.fetchall()

    order_list = []

    for order in fetch_order_list:
        order_list.append([order[0], order[1], order[2]])

    order_df = pd.DataFrame(order_list, columns=['성별', '상품명', '수량'])

    # 성별, 상품명, 수량을 기준으로 그룹화하여 구매 수량 합산
    grouped_data = order_df.groupby(['성별', '상품명'])['수량'].sum().reset_index()

    # 성별별로 가장 많이 구매한 상품 상위 5개씩 추출
    top_5_products_by_gender = grouped_data.sort_values(['성별', '수량'], ascending=[True, False]) \
        .groupby('성별').head(5).reset_index(drop=True)
    
    if not chart:
        save_folder = os.getenv("REPORT_PREPROCESS_PWD")
        return top_5_products_by_gender.to_csv(save_folder + "/성별별구매.csv", index=False, encoding='utf-8')

    # 성별별로 상위 5개 상품을 따로 추출
    female_data = top_5_products_by_gender[top_5_products_by_gender['성별'] == 'FEMALE'].copy()
    male_data = top_5_products_by_gender[top_5_products_by_gender['성별'] == 'MALE'].copy()
    other_data = top_5_products_by_gender[top_5_products_by_gender['성별'] == 'OTHER'].copy()

    # 성별에 맞는 색상 팔레트
    palette = {'FEMALE': '#F9A8D4', 'MALE': '#A7C7E7', 'OTHER': '#C1E1DC'}

    # 그래프 크기 설정
    plt.figure(figsize=(15, 10))

    # 성별별로 상위 5개 상품을 나란히 표시
    for gender, data in zip(['FEMALE', 'MALE', 'OTHER'], [female_data, male_data, other_data]):
        # 'y' 값에 성별에 맞는 오프셋을 추가하여 표시
        data['y_offset'] = data['상품명'] + ' (' + translation(gender) + ')'

        sns.barplot(x='수량', y='y_offset', data=data, errorbar=None, label=gender, color=palette[gender])

    # 제목, 레이블 설정
    plt.title('성별별로 가장 많이 구매한 상품 Top 5', fontsize=16)
    plt.xlabel('구매 수량', fontsize=12)
    plt.ylabel('상품명', fontsize=12)

    # 범례 추가
    plt.legend(title="성별", loc='upper left')

    # 수치 추가
    for ax in plt.gca().patches:
        if ax.get_width() != 0:
            x_position = ax.get_x() + ax.get_width() / 2
            y_position = ax.get_y() + ax.get_height() / 2
            plt.text(x_position, y_position, f'{int(ax.get_width())}', ha='center', va='center', fontsize=12,
                     color='black')

    # 그래프 표시
    plt.tight_layout()

    # 차트를 메모리 버퍼에 저장 (SVG 형식으로)
    svg_buf = io.StringIO()  # 텍스트 형식의 StringIO 버퍼 사용
    plt.savefig(svg_buf, format='svg')  # SVG 형식으로 저장
    svg_buf.seek(0)  # 버퍼의 시작 지점으로 이동

    # SVG 태그를 반환
    return svg_buf.getvalue()  # SVG XML 문자열 반환