import streamlit as st
import ee
from google.oauth2 import service_account
import geemap.foliumap as geemap

# 從 Streamlit Secrets 讀取 GEE 服務帳戶金鑰 JSON
service_account_info = st.secrets["GEE_SERVICE_ACCOUNT"]

# 使用 google-auth 進行 GEE 授權
credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/earthengine"]
)

# 初始化 GEE
ee.Initialize(credentials)


###############################################


# ----------- Streamlit 頁面設定 -----------
st.set_page_config(layout="wide")
st.title("🌿 彰師大進德校區 Sentinel-2 分群分類")

# ----------- 分析設定 -----------
center = [24.081653403304525, 120.5583462887228]
point = ee.Geometry.Point(center)

# 讀取 Sentinel-2 Harmonized 影像
s2 = ee.ImageCollection("COPERNICUS/S2_HARMONIZED") \
    .filterDate("2021-01-01", "2022-01-01") \
    .filterBounds(point) \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 1)) \
    .median()

# 選取所有以 B 開頭的波段
bands = s2.bandNames().filter(ee.Filter.stringStartsWith('item', 'B'))
s2 = s2.select(bands)

# ----------- 抽樣與分群模型訓練 -----------
samples = s2.sample(
    region=point.buffer(1000),  # 抽樣半徑 1 公里
    scale=10,
    numPixels=10000,
    seed=42
)

clusterer = ee.Clusterer.wekaKMeans(10).train(samples)
classified = s2.cluster(clusterer)

# ----------- 分類顯示設定 -----------
palette = [
    'ff0000', '00ff00', '0000ff', 'ffff00', 'ff00ff',
    '00ffff', 'ffa500', '800080', '008000', '808080'
]
labels = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']

# 可見光 RGB 合成
rgb_vis = s2.visualize(bands=['B4', 'B3', 'B2'], min=0, max=3000)
class_vis = classified.visualize(min=0, max=9, palette=palette)

# ----------- 顯示地圖（滑動分割） -----------
Map = geemap.Map(center=center, zoom=15)
Map.split_map(
    left_layer=geemap.ee_tile_layer(rgb_vis, {}, "RGB"),
    right_layer=geemap.ee_tile_layer(class_vis, {}, "Clustered")
)
Map.add_legend(title="Land Cover Clusters", labels=labels, colors=palette)
Map.to_streamlit(height=600)
