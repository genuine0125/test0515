import streamlit as st
import ee
from google.oauth2 import service_account
import geemap.foliumap as geemap

# -------- GEE 授權 ---------------
service_account_info = st.secrets["GEE_SERVICE_ACCOUNT"]
credentials = service_account.Credentials.from_service_account_info(
    service_account_info,
    scopes=["https://www.googleapis.com/auth/earthengine"]
)
ee.Initialize(credentials)

# -------- Streamlit 設定 ----------
st.set_page_config(layout="wide")
st.title("🏫 彰師大進德校區 Sentinel-2 分群分類分析")

# -------- 中心座標與區域 ----------
center = [24.081653403304525, 120.5583462887228]
point = ee.Geometry.Point(center)

# -------- Sentinel-2 資料處理 -------
s2 = ee.ImageCollection("COPERNICUS/S2_HARMONIZED") \
    .filterDate("2021-01-01", "2022-01-01") \
    .filterBounds(point) \
    .filter(ee.Filter.lt("CLOUDY_PIXEL_PERCENTAGE", 1)) \
    .median()

bands = s2.bandNames().filter(ee.Filter.stringStartsWith("item", "B"))
s2 = s2.select(bands)

# -------- 抽樣並分群 ----------
samples = s2.sample(
    region=point.buffer(1000),
    scale=10,
    numPixels=10000,
    seed=42
)

clusterer = ee.Clusterer.wekaKMeans(10).train(samples)
classified = s2.cluster(clusterer)

# -------- 顏色與圖例 ----------
palette = [
    "ff0000", "00ff00", "0000ff", "ffff00", "ff00ff",
    "00ffff", "ffa500", "800080", "008000", "808080"
]
labels = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']

rgb = s2.select(["B4", "B3", "B2"]).visualize(min=0, max=3000)
clustered = classified.visualize(min=0, max=9, palette=palette)

# -------- 地圖顯示 ----------
Map = geemap.Map(center=center, zoom=13)
Map.split_map(
    left_layer=geemap.ee_tile_layer(rgb, {}, "RGB"),
    right_layer=geemap.ee_tile_layer(clustered, {}, "Clustered")
)
Map.add_legend(title="Land Cover Cluster (KMeans)", labels=labels, colors=palette)
Map.to_streamlit(height=600)
