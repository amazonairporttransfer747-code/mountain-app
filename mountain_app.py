import urllib.parse
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(
    page_title="台灣山岳查詢與地圖系統", page_icon="🏔️", layout="wide"
)

st.title("🏔️ 亞馬遜國家山岳協會 - 台灣山岳地圖與查詢系統")
st.markdown("---")


@st.cache_data
def load_mountain_data():
  try:
    # 讀取指定的 CSV 檔案
    df = pd.read_csv("filtered_mountain_data.csv", encoding="utf-8-sig")
    # 如果 CSV 裡面原本有品牌欄位則自動移除
    if "品牌/協會" in df.columns:
      df = df.drop(columns=["品牌/協會"])
    return df
  except Exception as e:
    st.error(
        f"讀取 `filtered_mountain_data.csv` 失敗，請檢查檔名或格式是否正確。"
        f" 錯誤訊息: {e}"
    )
    return pd.DataFrame()


df = load_mountain_data()

if df.empty:
  st.warning(
      "目前沒有資料，請確認是否已將 `filtered_mountain_data.csv` 檔案上傳至 GitHub"
      " 專案根目錄。"
  )
else:
  st.sidebar.header("🔍 查詢與篩選面板")

  # 1. 手動輸入山名
  search_name = st.sidebar.text_input("手動輸入山名關鍵字", "")

  # 2. 縣市選項 (包含 ALL)
  city_options = ["ALL"] + sorted(df["縣市"].dropna().unique().tolist())
  selected_city = st.sidebar.selectbox("選擇縣市", city_options)

  # 3. 鄉鎮市選項 (包含 ALL)
  if selected_city == "ALL":
    town_options = ["ALL"] + sorted(df["鄉鎮市區"].dropna().unique().tolist())
  else:
    town_options = ["ALL"] + sorted(
        df[df["縣市"] == selected_city]["鄉鎮市區"]
        .dropna()
        .unique()
        .tolist()
    )
  selected_town = st.sidebar.selectbox("選擇鄉鎮市區", town_options)

  # 執行篩選邏輯
  filtered_df = df.copy()

  if search_name.strip():
    filtered_df = filtered_df[
        filtered_df["名稱"].str.contains(search_name.strip(), na=False)
    ]

  if selected_city != "ALL":
    filtered_df = filtered_df[filtered_df["縣市"] == selected_city]

  if selected_town != "ALL":
    filtered_df = filtered_df[filtered_df["鄉鎮市區"] == selected_town]

  # 在最右邊動態加入 Google GPX 搜尋網址欄位
  filtered_df["Google GPX 搜尋"] = filtered_df["名稱"].apply(
      lambda x: f"https://www.google.com/search?q={urllib.parse.quote(str(x) + ' GPX')}"
  )

  st.success(f"目前顯示筆數：{len(filtered_df)} 筆山岳資料")

  # 顯示表格與超連結欄位設定
  st.subheader("📊 山岳資料列表")
  st.dataframe(
      filtered_df,
      use_container_width=True,
      height=300,
      column_config={
          "Google GPX 搜尋": st.column_config.LinkColumn(
              "Google GPX 搜尋",
              help="點擊直接前往 Google 搜尋該山的 GPX 網頁",
              display_text="🔍 搜尋 GPX",
          )
      },
  )

  # 匯出按鈕
  csv_data = filtered_df.to_csv(index=False, encoding="utf-8-sig")
  st.download_button(
      label="📥 下載目前的山岳資料為 CSV 檔案",
      data=csv_data,
      file_name="filtered_mountain_data.csv",
      mime="text/csv",
  )

  st.markdown("---")
  st.subheader("🗺️ 台灣地圖檢視 (含多圖層與 Google GPX 連結)")

  if (
      not filtered_df.empty
      and "WGS_Y" in filtered_df.columns
      and "WGS_X" in filtered_df.columns
  ):
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
      m_name = row.get("名稱", "未命名")
      lat = row.get("WGS_Y")
      lon = row.get("WGS_X")
      c_name = row.get("縣市", "")
      t_name = row.get("鄉鎮市區", "")

      if pd.notna(lat) and pd.notna(lon):
        google_url = row["Google GPX 搜尋"]

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
