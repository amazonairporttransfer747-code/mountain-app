import json
import os

# 設定路徑
input_path = "data/osm_peaks.json"
output_path = "data/peaks_fixed.geojson"

def process_data():
    if not os.path.exists(input_path):
        print(f"錯誤：找不到檔案 {input_path}")
        return

    with open(input_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    features = []
    
    for item in data.get("elements", []):
        if item.get("type") == "node":
            tags = item.get("tags", {})
            # 確保有海拔資料，若無則顯示 '未知'
            ele = tags.get("ele", "未知")
            
            # GeoJSON 規範：先經度(lon/X)，後緯度(lat/Y)
            # 若原始資料 XY 軸偏掉，這裡確保 geometry 格式正確
            lon = item.get("lon")
            lat = item.get("lat")
            
            if lon and lat:
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [float(lon), float(lat)]
                    },
                    "properties": {
                        "name": tags.get("name:zh", tags.get("name", "未命名")),
                        "ele": ele,
                        "lat": lat,
                        "lon": lon
                    }
                }
                features.append(feature)

    # 排序邏輯：由北到南 (lat降序)，由西到東 (lon升序)
    features.sort(key=lambda x: (-x["properties"]["lat"], x["properties"]["lon"]))

    # 封裝
    geojson = {"type": "FeatureCollection", "features": features}

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)
    
    print(f"處理完成！修正後的資料已儲存至: {output_path}")

process_data()
