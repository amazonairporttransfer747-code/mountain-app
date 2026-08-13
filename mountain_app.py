import urllib.parse
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

st.set_page_config(page_title="台灣山岳查詢與地圖系統", page_icon="🏔️", layout="wide")

st.title("🏔️ 亞馬遜國家山岳協會 - 台灣山岳地圖與查詢系統")
st.markdown("---")

@st.cache_data
def load_mountain_data():
    try:
        df = pd.read_csv("filtered_mountain_data.csv", encoding="utf-8-sig")
        if "品牌/協會" in df.columns:
            df = df.drop(columns=["品牌/協會"])
        # 強制座標糾正
        if "WGS_X" in df.columns and "WGS_Y" in df.columns:
            if df["WGS_X"].mean() < 30:
                df["WGS_X"], df["WGS_Y"] = df["WGS_Y"], df["WGS_X"]
        return df
    except Exception as e:
        st.error(f"讀取檔案失敗: {e}")
        return pd.DataFrame()

df = load_mountain_data()

if df.empty:
    st.warning("目前沒有資料，請確認 `filtered_mountain_data.csv` 是否已上傳。")
else:
    st.sidebar.header("🔍 查詢與篩選面板")

    # 1. 縣市選項 (固定全域)
    all_cities = ["-- 請選擇 --", "ALL"] + sorted(df["縣市"].dropna().unique().tolist())
    selected_city = st.sidebar.selectbox("選擇縣市", all_cities)

    # 2. 鄉鎮選項 (根據所選縣市動態變更)
    if selected_city == "-- 請選擇 --" or selected_city == "ALL":
        town_options = ["-- 請選擇 --", "ALL"] + sorted(df["鄉鎮市區"].dropna().unique().tolist())
    else:
        # 只取出該縣市內的所有鄉鎮
        town_options = ["-- 請選擇 --", "ALL"] + sorted(df[df["縣市"] == selected_city]["鄉鎮市區"].dropna().unique().tolist())
    
    selected_town = st.sidebar.selectbox("選擇鄉鎮市區", town_options)
    
    # 3. 手動輸入山名
    search_name = st.sidebar.text_input("手動輸入山名關鍵字", "")

    # 判斷篩選狀態
    is_filtered = (bool(search_name.strip()) or selected_city != "-- 請選擇 --")

    if not is_filtered:
        st.info("📌 目前尚未進行篩選。請在左側輸入條件來顯示資料。")
    else:
        filtered_df = df.copy()

        if search_name.strip():
            filtered_df = filtered_df[filtered_df["名稱"].str.contains(search_name.strip(), na=False)]
        
        if selected_city != "-- 請選擇 --" and selected_city != "ALL":
            filtered_df = filtered_df[filtered_df["縣市"] == selected_city]
            
        if selected_town != "-- 請選擇 --" and selected_town != "ALL":
            filtered_df = filtered_df[filtered_df["鄉鎮市區"] == selected_town]

        filtered_df = filtered_df.reset_index(drop=True)
        filtered_df.insert(0, "NO.", range(1, len(filtered_df) + 1))

        # 新增搜尋連結
        filtered_df["Google GPX 搜尋"] = filtered_df["名稱"].apply(
            lambda x: f"https://www.google.com/search?q={urllib.parse.quote(str(x) + ' GPX')}"
        )

        st.success(f"查詢成功！共找到 {len(filtered_df)} 筆資料")
        
        st.subheader("📊 山岳資料列表")
        st.dataframe(
            filtered_df,
            use_container_width=True,
            height=300,
            hide_index=True,
            column_config={
                "NO.": st.column_config.NumberColumn("NO.", width="small"),
                "Google GPX 搜尋": st.column_config.LinkColumn("搜尋 GPX", display_text="🔍 搜尋 GPX"),
            },
        )

        # 地圖呈現
        if not filtered_df.empty:
            m = folium.Map(location=[filtered_df["WGS_Y"].mean(), filtered_df["WGS_X"].mean()], zoom_start=9)
            for _, row in filtered_df.iterrows():
                folium.Marker(
                    location=[row["WGS_Y"], row["WGS_X"]],
                    popup=f"{row['名稱']}<br><a href='{row['Google GPX 搜尋']}' target='_blank'>🔍 搜尋 GPX</a>",
                    tooltip=row["名稱"],
                    icon=folium.Icon(color="red", icon="mountain", prefix="fa")
                ).add_to(m)
            st_folium(m, width="100%", height=500)
