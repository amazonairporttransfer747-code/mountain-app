import urllib.parse
import folium
import pandas as pd
import requests
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(
    page_title="台灣山岳查詢與地圖系統", page_icon="🏔️", layout="wide"
)

st.title("🏔️ 亞馬遜國家山岳協會 - 台灣山岳地圖與查詢系統")
st.markdown("---")


# 根據經緯度自動判斷台灣縣市與山區鄉鎮的輔助函數
def get_location_info(lat, lon):
  if lat is None or lon is None:
    return "台灣地區", "未分類"

  if lat > 24.8:
    if lon < 121.4:
      return "新北市", "淡水/三芝區"
    else:
      return "新北市", "瑞芳/貢寮區"
  elif lat > 24.5:
    if lon < 121.2:
      return "桃園市", "復興區"
    elif lon < 121.5:
      return "新北市", "烏來區"
    else:
      return "宜蘭縣", "大同鄉"
  elif lat > 24.0:
    if lon < 120.9:
      return "苗栗縣", "泰安鄉"
    elif lon < 121.2:
      return "臺中市", "和平區"
    else:
      return "南投縣", "仁愛鄉"
  elif lat > 23.5:
    if lon < 120.8:
      return "嘉義縣", "阿里山鄉"
    else:
      return "花蓮縣", "秀林鄉"
  elif lat > 22.8:
    if lon < 120.7:
      return "高雄市", "桃源區"
    else:
      return "臺東縣", "海端鄉"
  else:
    return "屏東縣", "霧台鄉"


@st.cache_data(ttl=86400)
def load_mountain_data():
  overpass_url = "https://overpass-api.de/api/interpreter"
  overpass_query = """
    [out:json][timeout:60];
    (
      node["natural"="peak"](21.8, 119.3, 25.4, 122.1);
    );
    out body;
    """
  headers = {"User-Agent": "AmazonMountainApp/1.0"}
  try:
    response = requests.get(
        overpass_url,
        params={"data": overpass_query},
        headers=headers,
        timeout=60,
    )
    data = response.json()
    rows = []
    for element in data.get("elements", []):
      tags = element.get("tags", {})
      name = tags.get("name", "未命名山峰")
      lat = element.get("lat")
      lon = element.get("lon")

      if lat and lon:
        city, town = get_location_info(lat, lon)
        rows.append({
            "品牌/協會": "亞馬遜國家山岳協會",
            "名稱": name,
            "縣市": city,
            "鄉鎮市區": town,
            "WGS_X": lon,
            "WGS_Y": lat,
        })
    df = pd.DataFrame(rows)
    return df
  except Exception as e:
    return pd.DataFrame()


df = load_mountain_data()

if df.empty:
  st.error("資料載入失敗或逾時，請至右上角點選 Clear cache 後重新整理。")
else:
  st.sidebar.header("🔍 查詢與篩選面板")

  # 1. 手動輸入山名
  search_name = st.sidebar.text_input("手動輸入山名關鍵字", "")

  # 2. 縣市選項 (包含 ALL)
  cities = ["ALL"] + sorted(df["縣市"].unique().tolist())
  selected_city = st.sidebar.selectbox("選擇縣市", cities)

  # 3. 鄉鎮市選項 (包含 ALL)
  if selected_city == "ALL":
    towns = ["ALL"] + sorted(df["鄉鎮市區"].unique().tolist())
  else:
    towns = ["ALL"] + sorted(
        df[df["縣市"] == selected_city]["鄉鎮市區"].unique().tolist()
    )
  selected_town = st.sidebar.selectbox("選擇鄉鎮市區", towns)

  # 尚未篩選時，列表與地圖不陳列
  is_filtered = (
      bool(search_name.strip())
      or (selected_city != "ALL")
      or (selected_town != "ALL")
  )

  if not is_filtered:
    st.info(
        "📌 目前尚未進行篩選。請在左側輸入山名、選擇縣市或鄉鎮市來顯示山岳列表與地圖。"
    )
  else:
    filtered_df = df.copy()
    if search_name.strip():
      filtered_df = filtered_df[
          filtered_df["名稱"].str.contains(search_name.strip(), na=False)
      ]
    if selected_city != "ALL":
      filtered_df = filtered_df[filtered_df["縣市"] == selected_city]
    if selected_town != "ALL":
      filtered_df = filtered_df[filtered_df["鄉鎮市區"] == selected_town]

    st.success(f"查詢成功！共找到 {len(filtered_df)} 筆符合條件的山岳資料。")

    # 顯示表格（包含品牌、名稱、縣市、鄉鎮、經緯度欄位）
    st.subheader("📊 山岳資料列表")
    st.dataframe(filtered_df, use_container_width=True, height=300)

    # 匯出按鈕
    csv_data = filtered_df.to_csv(index=False, encoding="utf-8-sig")
    st.download_button(
        label="📥 下載篩選後的 CSV 檔案",
        data=csv_data,
        file_name="filtered_mountain_data.csv",
        mime="text/csv",
    )

    st.markdown("---")
    st.subheader("🗺️ 台灣地圖檢視 (含多圖層與 Google GPX 連結)")

    if not filtered_df.empty:
      center_lat = filtered_df["WGS_Y"].mean()
      center_lon = filtered_df["WGS_X"].mean()

      # 建立地圖
      m = folium.Map(location=[center_lat, center_lon], zoom_start=9, tiles=None)

      # 加入圖層：OSM、衛星圖、等高線地形圖
      folium.TileLayer("OpenStreetMap", name="標準地圖 (OSM)").add_to(m)
      folium.TileLayer(
          "https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}",
          attr="Esri",
          name="衛星地圖",
      ).add_to(m)
      folium.TileLayer(
          "https://{s}.tile.opentopomap.org/{z}/{x}/{y}.png",
          attr="OpenTopoMap",
          name="等高線地形圖",
      ).add_to(m)

      # 加入標記與 Google 搜尋 GPX 連結
      for _, row in filtered_df.iterrows():
        m_name = row["名稱"]
        lat = row["WGS_Y"]
        lon = row["WGS_X"]
        c_name = row["县市" if "县市" in row else "縣市"]
        t_name = row["鄉鎮市區"]

        encoded_query = urllib.parse.quote(f"{m_name} GPX")
        google_url = "https://www.google.com/search?q=" + encoded_query

        popup_html = f"""
                <div style="width:200px">
                    <h4><b>{m_name}</b></h4>
                    <p><b>{c_name} {t_name}</b><br>經度: {lon}<br>緯度: {lat}</p>
                    <a href="{google_url}" target="_blank" style="color: blue; font-weight: bold;">🔍 點選 Google 搜尋 GPX</a>
                </div>
                """

        folium.Marker(
            location=[lat, lon],
            popup=folium.Popup(popup_html, max_width=300),
            tooltip=m_name,
            icon=folium.Icon(color="red", icon="mountain", prefix="fa"),
        ).add_to(m)

      folium.LayerControl().add_to(m)
      st_folium(m, width="100%", height=500)
    else:
      st.warning("沒有符合該條件的座標點可顯示在地圖上。")
