import json
import os

# 檔案直接在根目錄，請把下方引號內的名稱改成您的實際檔名
input_filename = "osm_peaks.json"  # <-- 請修改這裡的檔名
output_filename = "peaks_fixed.geojson"

if not os.path.exists(input_filename):
  print(f"找不到檔案：{input_filename}，請確認檔名是否正確！")
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
        # 提取海拔高度，若無則標記為「未知」
        ele = tags.get("ele", "未知")
        # 提取中文名稱
        name = tags.get("name:zh", tags.get("name", "未命名"))

        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [
                    float(lon),
                    float(lat),
                ],  # GeoJSON 標準格式：[經度(X), 緯度(Y)]，修正座標偏移
            },
            "properties": {
                "name": name,
                "ele": ele,
                "lat": lat,
                "lon": lon,
                **tags,  # 保留所有原始標籤
            },
        }
        features.append(feature)

  # 排序邏輯：
  # 1. 由北到南：緯度 (lat) 由大到小降冪排序
  # 2. 由西到東：經度 (lon) 由小到大升冪排序
  features.sort(key=lambda x: (-x["properties"]["lat"], x["properties"]["lon"]))

  # 建立 GeoJSON 結構
  geojson = {"type": "FeatureCollection", "features": features}

  # 儲存檔案
  with open(output_filename, "w", encoding="utf-8") as f:
    json.dump(geojson, f, ensure_ascii=False, indent=2)

  print(f"處理成功！已產生成果檔案：{output_filename}")
