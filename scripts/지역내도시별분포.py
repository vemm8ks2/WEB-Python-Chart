import pandas as pd
import matplotlib.pyplot as plt
import math
import os
import io
from dotenv import load_dotenv
from matplotlib import font_manager
from scripts.db_connection import create_connection

load_dotenv()

def 지역내도시별분포(chart=True):
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

    # 대분류 지역 추출
    regions = df["배송지"].str.split().str[0].unique()

    # 서브플롯 레이아웃 계산
    n_regions = len(regions)
    n_cols = 2  # 열의 수 (한 줄에 표시할 그래프 수)
    n_rows = math.ceil(n_regions / n_cols)  # 행의 수 계산

    # 서브플롯 생성
    fig, axes = plt.subplots(n_rows, n_cols, figsize=(20, 5 * n_rows))
    axes = axes.flatten()  # 배열을 평탄화하여 인덱싱 편리하게

    # 각 지역별 그래프 생성
    for i, region in enumerate(regions):
        # 해당 지역의 데이터 필터링
        region_data = df[df["배송지"].str.startswith(region)]
        city_counts = region_data["배송지"].value_counts()

        # 현재 서브플롯에 그래프 그리기
        axes[i].bar(city_counts.index, city_counts.values, color='skyblue', edgecolor='black')
        axes[i].set_title(f'{region} 지역 내 도시별 분포', fontsize=14)
        axes[i].tick_params(axis='x', rotation=45, labelsize=10)
        axes[i].set_xlabel('도시', fontsize=12)
        axes[i].set_ylabel('배송지 개수', fontsize=12)

     # 빈 서브플롯 숨기기
    for j in range(i + 1, len(axes)):
        axes[j].axis('off')

    # 전체 레이아웃 조정 및 표시
    plt.tight_layout()

    if not chart:
        # 결과를 담을 빈 리스트 생성
        result_list = []

        for i, region in enumerate(regions):
            # 해당 지역의 데이터 필터링
            region_data = df[df["배송지"].str.startswith(region)]
            city_counts = region_data["배송지"].value_counts()

            # city_counts는 Series이므로 이를 DataFrame으로 변환하여 추가
            temp_df = city_counts.reset_index()
            temp_df.columns = ["배송지", "count"]

            # 결과 리스트에 추가
            result_list.append(temp_df)

        # 모든 데이터를 하나의 DataFrame으로 합치기
        final_df = pd.concat(result_list, ignore_index=True)
        final_df = pd.DataFrame(final_df).rename(columns=({'count':'주문 수'}))
        save_folder = os.getenv("REPORT_PREPROCESS_PWD")
        return final_df.to_csv(save_folder + "/지역내도시별분포.csv", index=False, encoding='utf-8')

    # 차트를 메모리 버퍼에 저장 (SVG 형식으로)
    svg_buf = io.StringIO()  # 텍스트 형식의 StringIO 버퍼 사용
    plt.savefig(svg_buf, format='svg')  # SVG 형식으로 저장
    svg_buf.seek(0)  # 버퍼의 시작 지점으로 이동

    # SVG 태그를 반환
    return svg_buf.getvalue()  # SVG XML 문자열 반환