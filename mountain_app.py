import json
import os

# 修正：將檔名對應到您實際的檔案 export.json
input_filename = "export.json"
output_filename = "export.geojson"

if not os.path.exists(input_filename):
  print(f"找不到檔案：{input_filename}")
else:
  with open(input_filename, "r", encoding="utf-8") as f:
    data = json.load(f)

  features = []

  for item in data.get("elements", []):
    if item.get("type") == "node":
      lat = item.get("lat")
      lon = item.get("lon")
      tags = item.get("tags", {})

      if lat and lon:
        # 確保抓取海拔 (ele)，若無則顯示未知
        ele = tags.get("ele", "未知")
        name = tags.get("name:zh", tags.get("name", "未命名"))

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [float(lon), float(lat)],  # 確保 [經度, 緯度] 軸向正確
            },
            "properties": {
                "name": name,
                "ele": ele,
                "lat": lat,
                "lon": lon,
                **tags,
            },
        }
        features.append(feature)

  # 嚴格由北到南排序 (緯度由大到小)
  features.sort(key=lambda x: (-x["properties"]["lat"], x["properties"]["lon"]))

  geojson = {"type": "FeatureCollection", "features": features}

  with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(geojson, f, ensure_ascii=False, indent=2)

  print(f"成功處理並更新 {output_filename}！")
