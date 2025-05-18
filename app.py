import ee
import geemap

# 初始化 Earth Engine
ee.Initialize()

# 中心點
center = ee.Geometry.Point([120.5583462887228, 24.081653403304525])

# Sentinel-2 Harmonized
s2 = ee.ImageCollection('COPERNICUS/S2_HARMONIZED') \
    .filterDate('2021-01-01', '2022-01-01') \
    .filterBounds(center) \
    .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 1)) \
    .median()

# 選取 B 開頭的波段
bands = s2.bandNames().filter(ee.Filter.stringStartsWith('item', 'B'))
s2 = s2.select(bands)

# 訓練樣本
samples = s2.sample(
    region=center.buffer(1000),
    scale=10,
    numPixels=10000,
    seed=42
)

# 建立分群器
clusterer = ee.Clusterer.wekaKMeans(10).train(samples)

# 分群分類
classified = s2.cluster(clusterer)

# 顏色與標籤
palette = [
    'ff0000', '00ff00', '0000ff', 'ffff00', 'ff00ff',
    '00ffff', 'ffa500', '800080', '008000', '808080'
]
labels = ['zero', 'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine']

# 建立地圖（僅適用於 Notebook）
Map = geemap.Map(center=[24.081653403304525, 120.5583462887228], zoom=15)

# 滑動分割圖層
left = s2.visualize(bands=['B4', 'B3', 'B2'], min=0, max=3000)
right = classified.visualize(min=0, max=9, palette=palette)

Map.split_map(
    left_layer=geemap.ee_tile_layer(left, {}, 'RGB'),
    right_layer=geemap.ee_tile_layer(right, {}, 'Clustered')
)

Map.add_legend(title="Cluster Groups", labels=labels, colors=palette)
Map
right_layer = geemap.ee_tile_layer(classified.visualize(min=0, max=9, palette=palette), {}, 'Clustered Land Cover')

Map.split_map(left_layer, right_layer)

# 加入圖例
Map.add_legend(
    title="Cluster Groups",
    labels=labels,
    colors=palette
)

Map
