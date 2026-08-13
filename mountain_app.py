import pandas as pd
import requests
import streamlit as st


# =============================
# Streamlit 頁面設定
# =============================

st.set_page_config(
    page_title="台灣 OSM 山峰查詢工具",
    page_icon="🏔️",
    layout="wide",
)


# =============================
# 基本設定
# =============================

APP_NAME = "亞馬遜國家山岳協會"

OVERPASS_URL = "https://overpass-api.de/api/interpreter"

# 台灣及離島的大致範圍
SOUTH = 21.8
WEST = 119.3
NORTH = 25.4
EAST = 122.1

# Overpass 查詢
# 順序：南界、 西界、 北界、 東界
OVERPASS_QUERY = f"""
[out:json][timeout:120];

node
  ["natural"="peak"]
  ({SOUTH},{WEST},{NORTH},{EAST});

out body;
"""

# 請將 email 改成你自己的聯絡信箱
HEADERS = {
    "User-Agent": (
        "TaiwanMountainQuery/1.0 "
        "(contact: your-email@example.com)"
    )
}


# =============================
# 取得 OSM 山峰資料
# =============================

@st.cache_data(ttl=86400, show_spinner=False)
def load_mountain_data():
    try:
        response = requests.post(
            OVERPASS_URL,
            data={"data": OVERPASS_QUERY},
            headers=HEADERS,
            timeout=180,
        )

        response.raise_for_status()
        data = response.json()

    except requests.exceptions.Timeout:
        return pd.DataFrame(), "Overpass API 連線逾時，請稍後再試。"

    except requests.exceptions.RequestException as error:
        return pd.DataFrame(), f"Overpass API 連線錯誤：{error}"

    except ValueError:
        return pd.DataFrame(), "API 回傳內容不是有效的 JSON。"

    elements = data.get("elements", [])

    if not elements:
        return pd.DataFrame(), "API 沒有回傳任何山峰資料。"

    rows = []

    for element in elements:
        tags = element.get("tags", {})

        latitude = element.get("lat")
        longitude = element.get("lon")

        # 沒有座標就跳過
        if latitude is None or longitude is None:
            continue

        # OSM 的 ele 通常代表海拔，單位為公尺
        raw_elevation = tags.get("ele")

        try:
            elevation = float(raw_elevation) if raw_elevation else None
        except (TypeError, ValueError):
            elevation = None

        osm_id = element.get("id")

        rows.append({
            "品牌/協會": APP_NAME,
            "名稱": tags.get("name", "未命名"),
            "中文名稱": tags.get("name:zh", ""),
            "英文名稱": tags.get("name:en", ""),

            # WGS_X = 經度
            # WGS_Y = 緯度
            "WGS_X": float(longitude),
            "WGS_Y": float(latitude),

            "經度": float(longitude),
            "緯度": float(latitude),
            "海拔_m": elevation,

            "OSM_ID": osm_id,
            "Wikidata": tags.get("wikidata", ""),
            "Wikipedia": tags.get("wikipedia", ""),

            "OSM連結": (
                f"https://www.openstreetmap.org/node/{osm_id}"
                if osm_id
                else ""
            ),
        })

    if not rows:
        return pd.DataFrame(), "沒有取得有效的經緯度點位。"

    df = pd.DataFrame(rows)

    # 依 OSM_ID 去除重複資料
    df = df.drop_duplicates(
        subset=["OSM_ID"]
    )

    # 依海拔由高到低排序
    # 沒有海拔資料的山峰排在最後
    df = df.sort_values(
        by=["海拔_m", "名稱"],
        ascending=[False, True],
        na_position="last",
    )

    df = df.reset_index(drop=True)

    return df, f"資料載入成功，共 {len(df)} 筆。"


# =============================
# 載入資料
# =============================

st.title("🏔️ 台灣 OSM 山峰查詢工具")

st.caption(
    "資料來源：OpenStreetMap / Overpass API；"
    "查詢條件：natural=peak"
)

st.markdown("---")

with st.spinner("正在從 OpenStreetMap 取得山峰資料..."):
    df, message = load_mountain_data()


# =============================
# 側邊欄狀態
# =============================

st.sidebar.header("⚙️ 系統狀態")
st.sidebar.info(message)

if df.empty:
    st.error(message)

    if st.button("清除快取並重新載入"):
        st.cache_data.clear()
        st.rerun()

    st.stop()


# =============================
# 顯示資料載入狀態
# =============================

st.success(
    f"資料載入完成，共 {len(df)} 筆山峰資料。"
)


# =============================
# 查詢條件
# =============================

st.subheader("🔍 查詢條件")

col1, col2, col3 = st.columns(3)

with col1:
    keyword = st.text_input(
        "搜尋名稱",
        placeholder="例如：玉山、雪山",
    )

with col2:
    min_elevation = st.number_input(
        "最低海拔（公尺）",
        min_value=0,
        value=0,
        step=100,
    )

with col3:
    only_named = st.checkbox(
        "只顯示有名稱的山峰",
        value=False,
    )


# =============================
# 套用篩選
# =============================

result = df.copy()

# 名稱搜尋
if keyword:
    name_columns = [
        "名稱",
        "中文名稱",
        "英文名稱",
    ]

    name_mask = pd.Series(
        False,
        index=result.index,
    )

    for column in name_columns:
        name_mask = (
            name_mask
            | result[column]
            .astype(str)
            .str.contains(
                keyword,
                case=False,
                na=False,
            )
        )

    result = result[name_mask]

# 最低海拔篩選
if min_elevation > 0:
    result = result[
        result["海拔_m"].fillna(0) >= min_elevation
    ]

# 只顯示有名稱的山峰
if only_named:
    result = result[
        result["名稱"].notna()
        & (
            result["名稱"]
            .astype(str)
            .str.strip()
            != ""
        )
        & (result["名稱"] != "未命名")
    ]


# =============================
# 顯示查詢結果
# =============================

st.subheader(
    f"📊 查詢結果：{len(result)} 筆"
)

st.dataframe(
    result,
    use_container_width=True,
    height=500,
    hide_index=True,
    column_config={
        "OSM連結": st.column_config.LinkColumn(
            "OSM 地圖",
            display_text="開啟 OSM",
        ),

        "WGS_X": st.column_config.NumberColumn(
            "WGS_X 經度",
            format="%.6f",
        ),

        "WGS_Y": st.column_config.NumberColumn(
            "WGS_Y 緯度",
            format="%.6f",
        ),

        "經度": st.column_config.NumberColumn(
            "經度",
            format="%.6f",
        ),

        "緯度": st.column_config.NumberColumn(
            "緯度",
            format="%.6f",
        ),

        "海拔_m": st.column_config.NumberColumn(
            "海拔（公尺）",
            format="%.1f",
        ),
    },
)


# =============================
# CSV 下載
# =============================

csv_data = result.to_csv(
    index=False,
    encoding="utf-8-sig",
)

st.download_button(
    label="📥 下載查詢結果 CSV",
    data=csv_data,
    file_name="taiwan_osm_mountains.csv",
    mime="text/csv",
)


# =============================
# 座標欄位說明
# =============================

with st.expander("座標欄位說明"):
    st.markdown(
        """
        - `WGS_X`：WGS84 經度 longitude
        - `WGS_Y`：WGS84 緯度 latitude
        - `經度`：同 WGS_X
        - `緯度`：同 WGS_Y
        - `海拔_m`：OSM ele 標籤，單位通常為公尺
        - `OSM_ID`：OpenStreetMap 節點編號
        - 座標系統：EPSG:4326 / WGS 84
        """
    )
