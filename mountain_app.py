import json
import os

# 讀取與輸出路徑
input_path = "data/osm_peaks.json"
output_path = "data/peaks_sorted.geojson"

if not os.path.exists(input_path):
    print(f"找不到原始檔案: {input_path}")
else:
    with open(input_path, "r", encoding="utf-8") as f:
        osm_data = json.load(f)

    features = []

    for element in osm_data.get("elements", []):
        if element.get("type") == "node":
            lat = element.get("lat")
            lon = element.get("lon")
            tags = element.get("tags", {})
            
            if lat and lon:
                feature = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [lon, lat]
                    },
                    "properties": {
                        "id": element.get("id"),
                        "name": tags.get("name", "未命名"),
                        "name:zh": tags.get("name:zh", tags.get("name", "未命名")),
                        "ele": tags.get("ele"),
                        "ref": tags.get("ref"),
                        **tags
                    }
                }
                features.append(feature)

    # 依照地理位置排序：
    # 1. 由北到南：緯度 (lat) 由大到小降冪排序
    # 2. 由西到東：經度 (lon) 由小到大升冪排序
    features.sort(key=lambda x: (-x["geometry"]["coordinates"][1], x["geometry"]["coordinates"][0]))

    geojson = {
        "type": "FeatureCollection",
        "features": features
    }

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(geojson, f, ensure_ascii=False, indent=2)

    print(f"處理完成！已成功排序並儲存至: {output_path}")
