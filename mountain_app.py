import geopandas as gpd
import pandas as pd
import requests
import streamlit as st

# 設定網頁版面配置
st.set_page_config(
    page_title="亞馬遜國家山岳協會 - 台灣山岳查詢小工具",
    page_icon="🏔️",
    layout="wide",
)

st.title("🏔️ 亞馬遜國家山岳協會 - 台灣山岳與地名查詢小工具")
st.markdown("---")


@st.cache_data(ttl=86400)
def load_mountain_data():
  overpass_url = "https://overpass-api.de/api/interpreter"
  overpass_query = """
    [out:json][timeout:180];
    (
      node["natural"="peak"](21.8, 119.3, 25.4, 122.1);
      node["place"~"city|town|village"](21.8, 119.3, 25.4, 122.1);
    );
    out body;
    """

  try:
    response = requests.get(
        overpass_url, params={"data": overpass_query}, timeout=180
    )
    if response.status_code != 200:
      return pd.DataFrame(), f"API 錯誤狀態碼: {response.status_code}"
    data = response.json()
  except Exception as e:
    return pd.DataFrame(), f"API 連線異常: {e}"

  elements = data.get("elements", [])
  if not elements:
    return pd.DataFrame(), "API 回傳 0 筆資料"

  rows = []
  for element in elements:
    tags = element.get("tags", {})
    name = tags.get("name", "未命名")
    lat = element.get("lat")
    lon = element.get("lon")
    if lat is not None and lon is not None:
      rows.append({"名稱": name, "WGS_X": lon, "WGS_Y": lat})

  if not rows:
    return pd.DataFrame(), "沒有有效的經緯度點位"

  df_points = pd.DataFrame(rows)
  gdf_points = gpd.GeoDataFrame(
      df_points,
      geometry=gpd.points_from_xy(df_points.WGS_X, df_points.WGS_Y),
      crs="EPSG:4326",
  )

  # 載入行政區圖資
  town_geojson_url = (
      "https://raw.githubusercontent.com/g0v/Taiwan-geodata/master/json/towns.json"
  )
  try:
    gdf_towns = gpd.read_file(town_geojson_url)
  except Exception as e:
    df_points["品牌/協會"] = "亞馬遜國家山岳協會"
    df_points["縣市"] = "未知"
    df_points["鄉鎮"] = "未知"
    return (
        df_points[
            ["品牌/協會", "縣市", "鄉鎮", "名稱", "WGS_X", "WGS_Y"]
        ],
        f"行政區圖資載入失敗（已降級）：{e}",
    )

  if gdf_towns.crs != "EPSG:4326":
    gdf_towns = gdf_towns.to_crs("EPSG:4326")

  # 執行空間結合 (intersects，避免邊界稜線上的點漏判)
  gdf_merged = gpd.sjoin(gdf_points, gdf_towns, how="left", predicate="intersects")

  # 嚴格去重：避免落在縣市邊界稜線上的山峰因 intersects 產生重複列
  gdf_merged = gdf_merged[~gdf_merged.index.duplicated(keep="first")]

  # 動態對應欄位名稱
  county_col = next(
      (
          col
          for col in ["COUNTYNAME", "COUNTY", "countyname", "county"]
          if col in gdf_merged.columns
      ),
      None,
  )
  town_col = next(
      (
          col
          for col in ["TOWNNAME", "TOWN", "townname", "town"]
          if col in gdf_merged.columns
      ),
      None,
  )

  county_series = (
      gdf_merged[county_col].fillna("未知")
      if county_col
      else pd.Series("未知", index=gdf_merged.index)
  )
  town_series = (
      gdf_merged[town_col].fillna("未知")
      if town_col
      else pd.Series("未知", index=gdf_merged.index)
  )

  output_df = pd.DataFrame({
      "品牌/協會": "亞馬遜國家山岳協會",
      "縣市": county_series,
      "鄉鎮": town_series,
      "名稱": gdf_merged["名稱"],
      "WGS_X": gdf_merged["WGS_X"],
      "WGS_Y": gdf_merged["WGS_Y"],
  })

  debug_info = f"圖資欄位偵測成功 | 縣市欄位: {county_col}, 鄉鎮欄位: {town_col}"
  return output_df, debug_info


# 執行載入
with st.spinner("正在向系統載入台灣山岳與地名圖資，請稍候..."):
  df, msg = load_mountain_data()

# 側邊欄顯示狀態與偵測資訊（除錯用，正式上線可加 checkbox 隱藏）
st.sidebar.header("⚙️ 系統與偵測狀態")
st.sidebar.info(msg)

if df.empty:
  st.warning("目前沒有可顯示的資料，請檢查網路連線或稍後重新整理。")
else:
  st.success(f"資料載入完成！總共包含 {len(df)} 筆地理資料。")

  # 側邊欄地理位置篩選
  st.sidebar.header("🔍 地理位置篩選")
  counties = (
      ["全部"] + sorted(df["縣市"].dropna().unique().tolist())
      if "縣市" in df.columns
      else ["全部"]
  )
  selected_county = st.sidebar.selectbox("選擇縣市", counties)

  if selected_county != "全部":
    filtered_df = df[df["縣市"] == selected_county]
    towns = (
        ["全部"] + sorted(filtered_df["鄉鎮"].dropna().unique().tolist())
        if "鄉鎮" in filtered_df.columns
        else ["全部"]
    )
    selected_town = st.sidebar.selectbox("選擇鄉鎮", towns)
    if selected_town != "全部":
      filtered_df = filtered_df[filtered_df["鄉鎮"] == selected_town]
  else:
    filtered_df = df

  # 顯示即時查詢表格
  st.subheader(
      f"📊 查詢結果 (顯示筆數：{len(filtered_df)} / 品牌：亞馬遜國家山岳協會)"
  )
  st.dataframe(filtered_df, use_container_width=True, height=450)

  # 匯出按鈕
  csv_data = filtered_df.to_csv(index=False, encoding="utf-8-sig")
  st.download_button(
      label="📥 下載目前篩選結果為 CSV 檔案",
      data=csv_data,
      file_name="amazon_mountain_data.csv",
      mime="text/csv",
  )
