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
st.set_page_config(layout="wide")
st.title("🌍 使用服務帳戶連接 GEE 的 Streamlit App")


# 地理區域
point = ee.Geometry.Point([120.5583462887228, 24.081653403304525])

# 擷取 Landsat NDVI
my_img = (
    ee.ImageCollection('COPERNICUS/S2_HARMONIZED')
    .filterDate('2021-01-01', '2022-01-01')
    .sort('CLOUDY_PIXEL_PERCENTAGE')
    .first()
    .select('B.*')
)

vis_params = {'min':100, 'max': 3500, 'bands': ['B11',  'B8',  'B3']}

my_Map.centerObject(my_img, 10)
my_Map.addLayer(my_img, vis_params, "Sentinel-2")
my_Map

geemap.get_info(my_img)
my_img.get('HYBRID').getInfo()
my_img.get('CLOUDY_PIXEL_PERCENTAGE').getInfo()

# 顯示地圖
Map = geemap.Map(center=[25.03, 121.56], zoom=10)
Map.addLayer(ndvi, {"min": 0, "max": 1, "palette": ["white", "green"]}, "NDVI")
Map.to_streamlit(height=600)
