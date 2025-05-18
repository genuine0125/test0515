import ee
import geemap
import random

# 初始化 Earth Engine
ee.Initialize()

# 中心點：彰師大進德校區
center = ee.Geometry.Point([120.5583462887228, 24.081653403304525])

# Sentinel-2 Harmonized 影像：過濾時間、雲量、小範圍
s2 = ee.ImageCollection('COPERNICUS/S2_HARMONIZED') \
    .filterDate('2021-01-01', '2022-01-01') \
    .filterBounds(center) \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 1)) \
    .median()

# 選取所有 B 開頭的波段
bands = s2.bandNames().filter(ee.Filter.stringStartsWith('item', 'B'))
s2 = s2.select(bands)

# 從影像隨機取 10,000 點作為訓練樣本
samples = s2.sample(
    region=center.buffer(1000),
    scale=10,
    numPixels=10000,
    seed=42
)

# 建立 KMeans 模型並訓練（10 群）
clusterer = ee.Clusterer.wekaKMeans(10).train(samples)

# 對整張圖進行分類
classified = s2.cluster(clusterer)

# 顏色與標籤
palette = [
    'ff0000', '00ff00', '0000ff', 'ffff00', 'ff00ff',
    '00ffff', 'ffa500', '800080', '008000', '808080'
]
labels = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']

# 建立地圖並顯示
Map = geemap.Map(center=[24.081653403304525, 120.5583462887228], zoom=15)

# 可見光影像 (RGB)
rgb_vis = {
    'bands': ['B4', 'B3', 'B2'],
    'min': 0,
    'max': 3000
}

# 加入滑動視窗地圖：左 RGB，右 分群
left_layer = geemap.ee_tile_layer(s2.visualize(**rgb_vis), {}, 'Sentinel-2 RGB')
right_layer = geemap.ee_tile_layer(classified.visualize(min=0, max=9, palette=palette), {}, 'Clustered Land Cover')

Map.split_map(left_layer, right_layer)

# 加入圖例
Map.add_legend(
    title="Cluster Groups",
    labels=labels,
    colors=palette
)

Map
