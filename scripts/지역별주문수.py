import os.path
import pandas as pd
from dotenv import load_dotenv
from mapboxgl.viz import *
import folium
from folium import plugins
import matplotlib.font_manager as fm
from scripts.db_connection import create_connection

fontpath = '/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf'
font = fm.FontProperties(fname=fontpath, size=9)

load_dotenv()

def 지역별주문수(chart=True):
    # DB 연결
    connection = create_connection()
    connection.start_transaction()
    cursor = connection.cursor()

    cursor.execute("select * from orders")
    order_list = cursor.fetchall()

    order_all = []

    for order in order_list:
        order_all.append([order[5]])

    orders = pd.DataFrame(order_all,columns=['배송지'])
    df_pop = pd.DataFrame(orders['배송지'].value_counts()).reset_index()
    df_pop = df_pop.rename(columns=({'배송지': 'region', 'count': 'pop'}))
    sig = pd.read_csv(f"{os.getenv("PWD")}/data/Population_SIG.csv")
    sig = sig[['code', 'region']]
    df_pop = df_pop.merge(sig)
    df_pop = df_pop[['code', 'region', 'pop']]
    df_pop['code'] = df_pop['code'].astype(str)

    geo = json.load(open(f"{os.getenv("PWD")}/data/SIG.geojson", encoding='UTF-8'))

    for idx, sigun_dict in enumerate(geo['features']):
        sigun_id = sigun_dict['properties']['SIG_CD']

        # 조건에 맞는 데이터가 있는지 확인
        region_data = df_pop.loc[df_pop.code == sigun_id, 'region']
        pop_data = df_pop.loc[df_pop.code == sigun_id, 'pop']

        if not region_data.empty and not pop_data.empty:
            sigun_nmm = region_data.iloc[0]  # 해당 sigun_id에 맞는 지역 이름
            risk = pop_data.iloc[0]  # 구매자 수
            txt = f'<b><h4>{sigun_nmm}</h4></b>총구매자수(명) : {risk}'
        else:
            # region이 없을 경우 geo 데이터에서 SIG_KOR_NM을 가져오거나 기본값을 설정
            sigun_nmm = sigun_dict['properties'].get('SIG_KOR_NM', '알 수 없음')  # 지역 이름을 가져오되 없으면 '알 수 없음'으로 설정
            risk = 0  # 구매자 수는 0
            txt = f'<b><h4>{sigun_nmm}</h4></b>총구매자수(명) : {risk}'

        # geo 데이터에 텍스트 값 추가
        geo['features'][idx]['properties']['SIG_KOR_NM'] = txt

    # 지도 불러들어오기 중심점 좌표 서울
    m = folium.Map(location=[35.8, 127.6], tiles="OpenStreetMap", zoom_start=8)

    if not chart:
        df_pop = df_pop[['region','pop']]
        df_pop = df_pop.rename(columns=({'region':'지역', 'pop':'주문 수'}))
        save_folder = os.getenv("REPORT_PREPROCESS_PWD")
        return df_pop.to_csv(save_folder + "/지역별주문수.csv", index=False, encoding='utf-8')

    # 지도에 색 적용 및 데이터 연결
    choropleth = folium.Choropleth(
        geo_data=geo,
        data=df_pop,
        columns=('code', 'pop'),
        key_on='feature.properties.SIG_CD',
        fill_color='RdYlGn',
        fill_opacity=0.7,
        line_opacity=0.5,
        legend_name='지역별 주문수'
    ).add_to(m)

    # 지도 전체화면 추가코드
    plugins.Fullscreen(position='topright',
                       title='Click to Expand',
                       title_cancel='Click to Exit',
                       force_separate_button=True).add_to(m)

    # 지도 스크롤 가능
    plugins.MousePosition().add_to(m)

    # 지도에 원하는 변수 이름 나오게 하는 코드
    choropleth.geojson.add_child(folium.features.GeoJsonTooltip(['SIG_KOR_NM'], labels=False))
    m.get_root().html.add_child(folium.Element())
    folium.LayerControl().add_to(m)

    return m._repr_html_()