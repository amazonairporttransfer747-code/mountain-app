import pandas as pd
import requests
import streamlit as st

st.set_page_config(page_title="台灣山岳查詢系統", layout="wide")

@st.cache_data(ttl=86400)
def load_mountain_data():
    overpass_url = "https://overpass-api.de/api/interpreter"
    # 擴大範圍包含全台，並設定 Headers 防止 406
    overpass_query = """
    [out:json][timeout:60];
    (node["natural"="peak"](21.8, 119.3, 25.4, 122.1););
    out body;
    """
    headers = {"User-Agent": "AmazonApp/1.0"}
    try:
        response = requests.get(overpass_url, params={"data": overpass_query}, headers=headers, timeout=60)
        data = response.json()
        rows = [{"名稱": e["tags"].get("name", "未命名"), "WGS_X": e["lon"], "WGS_Y": e["lat"]} for e in data.get("elements", [])]
        df = pd.DataFrame(rows)
        # 模擬分區 (由於 API 無直接地址，這裡先標註為 '台灣'，後續可串接逆向編碼)
        df["縣市"] = "全台灣"
        df["鄉鎮市區"] = "各地區"
        return df
    except:
        return pd.DataFrame()

df = load_mountain_data()

st.title("🏔️ 亞馬遜國家山岳協會 - 山岳篩選器")

if df.empty:
    st.error("資料載入失敗，請檢查網路。")
else:
    # 側邊欄篩選器
    st.sidebar.header("篩選條件")
    
    # 建立選單 (包含 ALL)
    cities = ["ALL"] + sorted(df["縣市"].unique().tolist())
    selected_city = st.sidebar.selectbox("選擇縣市", cities)
    
    # 根據縣市過濾鄉鎮
    if selected_city == "ALL":
        towns = ["ALL"] + sorted(df["鄉鎮市區"].unique().tolist())
    else:
        towns = ["ALL"] + sorted(df[df["縣市"] == selected_city]["鄉鎮市區"].unique().tolist())
    
    selected_town = st.sidebar.selectbox("選擇鄉鎮市區", towns)

    # 執行篩選邏輯
    filtered_df = df.copy()
    if selected_city != "ALL":
        filtered_df = filtered_df[filtered_df["縣市"] == selected_city]
    if selected_town != "ALL":
        filtered_df = filtered_df[filtered_df["鄉鎮市區"] == selected_town]

    st.success(f"目前顯示: {len(filtered_df)} 筆山岳")
    st.dataframe(filtered_df, use_container_width=True)
    
    csv = filtered_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button("📥 下載篩選後的 CSV", csv, "mountain_data.csv", "text/csv")
