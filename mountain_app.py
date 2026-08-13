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
    [out:json][timeout:60];
    (
      node["natural"="peak"](21.8, 119.3, 25.4, 122.1);
    );
    out body;
    """

  # 加上 User-Agent 避免 406 錯誤
  headers = {"User-Agent": "AmazonMountainApp/1.0 (Contact: user@example.com)"}

  try:
    response = requests.get(
        overpass_url,
        params={"data": overpass_query},
        headers=headers,
        timeout=60,
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

  output_df = pd.DataFrame({
      "品牌/協會": "亞馬遜國家山岳協會",
      "名稱": df_points["名稱"],
      "WGS_X": df_points["WGS_X"],
      "WGS_Y": df_points["WGS_Y"],
  })

  return output_df, "資料載入成功！"


# 執行載入
with st.spinner("正在向系統載入台灣山岳資料，請稍候..."):
  df, msg = load_mountain_data()

# 側邊欄顯示狀態
st.sidebar.header("⚙️ 系統狀態")
st.sidebar.info(msg)

if df.empty:
  st.warning(
      "目前沒有可顯示的資料。請至網頁右上角點選三個點 (⋮) 選擇 **Clear"
      " cache** 然後重新整理網頁！"
  )
else:
  st.success(f"資料載入完成！總共包含 {len(df)} 筆山岳資料。")

  # 顯示即時查詢表格
  st.subheader(
      f"📊 查詢結果 (顯示筆數：{len(df)} / 品牌：亞馬遜國家山岳協會)"
  )
  st.dataframe(df, use_container_width=True, height=450)

  # 匯出按鈕
  csv_data = df.to_csv(index=False, encoding="utf-8-sig")
  st.download_button(
      label="📥 下載山岳資料為 CSV 檔案",
      data=csv_data,
      file_name="amazon_mountain_data.csv",
      mime="text/csv",
  )
