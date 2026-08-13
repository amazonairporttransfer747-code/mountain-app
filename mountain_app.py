cat > mountain_app.py <<'PYTHON'
import pandas as pd
import requests
import streamlit as st

from st_copy import copy_button


st.set_page_config(
page_title="台灣 OSM 山峰座標查詢",
page_icon="🏔️",
layout="wide",
)


APP_NAME = "亞馬遜國家山岳協會"

OVERPASS_URLS = [
https://overpass-api.de/api/interpreter,
https://overpass.kumi.systems/api/interpreter,
https://overpass.private.coffee/api/interpreter,
]

HEADERS = {
User-Agent: (
TaiwanMountainQuery/1.0 
(contact: your-email@example.com)
),
Accept: "*/*",
Content-Type: "application/x-www-form-urlencoded",
}


ADMIN_AREAS = {
基隆市: [
中正區, "七堵區", "暖暖區", "仁愛區",
中山區, "安樂區", "信義區",
],
臺北市: [
中正區, "大同區", "中山區", "松山區",
大安區, "萬華區", "信義區", "士林區",
北投區, "內湖區", "南港區", "文山區",
],
新北市: [
板橋區, "三重區", "中和區", "永和區",
新莊區, "新店區", "樹林區", "鶯歌區",
三峽區, "淡水區", "汐止區", "瑞芳區",
土城區, "蘆洲區", "五股區", "泰山區",
林口區, "深坑區", "石碇區", "坪林區",
三芝區, "石門區", "八里區", "平溪區",
雙溪區, "貢寮區", "金山區", "萬里區",
烏來區,
],
桃園市: [
桃園區, "中壢區", "平鎮區", "八德區",
楊梅區, "蘆竹區", "大溪區", "龜山區",
大園區, "觀音區", "新屋區", "龍潭區",
復興區,
],
新竹市: [
東區, "北區", "香山區",
],
新竹縣: [
竹北市, "竹東鎮", "新埔鎮", "關西鎮",
湖口鄉, "新豐鄉", "芎林鄉", "橫山鄉",
北埔鄉, "寶山鄉", "峨眉鄉", "尖石鄉",
五峰鄉,
],
苗栗縣: [
苗栗市, "苑裡鎮", "通霄鎮", "竹南鎮",
頭份市, "後龍鎮", "卓蘭鎮", "大湖鄉",
公館鄉, "銅鑼鄉", "南庄鄉", "三義鄉",
造橋鄉, "三灣鄉", "獅潭鄉", "西湖鄉",
頭屋鄉, "泰安鄉",
],
臺中市: [
中區, "東區", "南區", "西區", "北區",
北屯區, "西屯區", "南屯區", "太平區",
大里區, "霧峰區", "烏日區", "豐原區",
后里區, "石岡區", "東勢區", "和平區",
新社區, "潭子區", "大雅區", "神岡區",
大肚區, "沙鹿區", "龍井區", "梧棲區",
清水區, "大甲區", "外埔區", "大安區",
],
彰化縣: [
彰化市, "員林市", "鹿港鎮", "和美鎮",
溪湖鎮, "二林鎮", "田中鎮", "北斗鎮",
花壇鄉, "芬園鄉", "大村鄉", "永靖鄉",
社頭鄉, "田尾鄉", "埤頭鄉", "芳苑鄉",
大城鄉, "竹塘鄉", "溪州鄉", "線西鄉",
伸港鄉, "福興鄉", "秀水鄉", "埔鹽鄉",
埔心鄉,
],
南投縣: [
南投市, "埔里鎮", "草屯鎮", "竹山鎮",
集集鎮, "名間鄉", "鹿谷鄉", "中寮鄉",
魚池鄉, "國姓鄉", "水里鄉", "信義鄉",
仁愛鄉,
],
雲林縣: [
斗六市, "斗南鎮", "虎尾鎮", "西螺鎮",
土庫鎮, "北港鎮", "古坑鄉", "大埤鄉",
莿桐鄉, "林內鄉", "二崙鄉", "崙背鄉",
麥寮鄉, "東勢鄉", "褒忠鄉", "臺西鄉",
元長鄉, "四湖鄉", "口湖鄉", "水林鄉",
],
嘉義市: [
東區, "西區",
],
嘉義縣: [
太保市, "朴子市", "布袋鎮", "大林鎮",
民雄鄉, "溪口鄉", "新港鄉", "六腳鄉",
東石鄉, "義竹鄉", "鹿草鄉", "水上鄉",
中埔鄉, "竹崎鄉", "梅山鄉", "番路鄉",
大埔鄉, "阿里山鄉",
],
臺南市: [
中西區, "東區", "南區", "北區", "安平區",
安南區, "永康區", "歸仁區", "新化區",
左鎮區, "玉井區", "楠西區", "南化區",
仁德區, "關廟區", "龍崎區", "官田區",
麻豆區, "佳里區", "西港區", "七股區",
將軍區, "學甲區", "北門區", "新營區",
後壁區, "白河區", "東山區", "六甲區",
下營區, "柳營區", "鹽水區", "善化區",
大內區, "山上區", "新市區", "安定區",
],
高雄市: [
新興區, "前金區", "苓雅區", "鹽埕區",
鼓山區, "旗津區", "前鎮區", "三民區",
左營區, "楠梓區", "小港區", "鳳山區",
大寮區, "仁武區", "鳥松區", "岡山區",
橋頭區, "燕巢區", "田寮區", "阿蓮區",
路竹區, "湖內區", "茄萣區", "永安區",
彌陀區, "梓官區", "旗山區", "美濃區",
六龜區, "甲仙區", "杉林區", "內門區",
茂林區, "桃源區", "那瑪夏區",
],
屏東縣: [
屏東市, "潮州鎮", "東港鎮", "恆春鎮",
萬丹鄉, "長治鄉", "麟洛鄉", "九如鄉",
里港鄉, "鹽埔鄉", "高樹鄉", "萬巒鄉",
內埔鄉, "竹田鄉", "新埤鄉", "枋寮鄉",
新園鄉, "崁頂鄉", "林邊鄉", "南州鄉",
佳冬鄉, "琉球鄉", "車城鄉", "滿州鄉",
枋山鄉, "三地門鄉", "霧臺鄉", "瑪家鄉",
泰武鄉, "來義鄉", "春日鄉", "獅子鄉",
牡丹鄉,
],
宜蘭縣: [
宜蘭市, "羅東鎮", "蘇澳鎮", "頭城鎮",
礁溪鄉, "壯圍鄉", "員山鄉", "冬山鄉",
五結鄉, "三星鄉", "大同鄉", "南澳鄉",
],
花蓮縣: [
花蓮市, "鳳林鎮", "玉里鎮", "新城鄉",
吉安鄉, "壽豐鄉", "光復鄉", "豐濱鄉",
瑞穗鄉, "富里鄉", "秀林鄉", "萬榮鄉",
卓溪鄉,
],
臺東縣: [
臺東市, "成功鎮", "關山鎮", "卑南鄉",
鹿野鄉, "池上鄉", "東河鄉", "長濱鄉",
太麻里鄉, "大武鄉", "綠島鄉", "蘭嶼鄉",
延平鄉, "海端鄉", "達仁鄉", "金峰鄉",
],
澎湖縣: [
馬公市, "湖西鄉", "白沙鄉", "西嶼鄉",
望安鄉, "七美鄉",
],
金門縣: [
金城鎮, "金湖鎮", "金沙鎮", "金寧鄉",
烈嶼鄉, "烏坵鄉",
],
連江縣: [
南竿鄉, "北竿鄉", "莒光鄉", "東引鄉",
],
}


def normalize_admin_name(name):
result = str(name).strip()

replacements = {
台北: "臺北",
台中: "臺中",
台南: "臺南",
台東: "臺東",
}

for old_name, new_name in replacements.items():
result = result.replace(old_name, new_name)

return result


def build_overpass_query(county, township):
county_name = normalize_admin_name(county)
township_name = normalize_admin_name(township)

if township_name == "全部":
area_query = f"""
area
["boundary"="administrative"]
["admin_level"="6"]
["name"="{county_name}"]
->.searchArea;
"""
    else:
        area_query = f"""
area
["boundary"="administrative"]
["admin_level"="8"]
["name"="{township_name}"]
(area
["boundary"="administrative"]
["admin_level"="6"]
["name"="{county_name}"]
)
->.searchArea;
"""

    return f"""
[out:json][timeout:120];

{area_query}

node
["natural"="peak"]
(area.searchArea);

out body;
"""


@st.cache_data(ttl=86400, show_spinner=False)
def query_mountains(county, township):
    query = build_overpass_query(county, township)

    data = None
    last_error = ""

    for overpass_url in OVERPASS_URLS:
        try:
            response = requests.post(
                overpass_url,
                data=query.encode("utf-8"),
headers=HEADERS,
timeout=180,
)

if response.status_code == 200:
data = response.json()
break

last_error = (
f"{overpass_url} 回傳 HTTP "
f"{response.status_code}: "
f"{response.text[:300]}"
)

except requests.exceptions.Timeout:
last_error = (
f"{overpass_url} 連線逾時。"
)

except requests.exceptions.RequestException as error:
last_error = (
f"{overpass_url} 連線錯誤：{error}"
)

except ValueError:
last_error = (
f"{overpass_url} 回傳內容不是有效 JSON。"
)

if data is None:
return pd.DataFrame(), (
"所有 Overpass 伺服器都無法使用。

"
f"最後錯誤：{last_error}"
)

elements = data.get("elements", [])

if not elements:
return pd.DataFrame(), (
該行政區沒有找到 natural=peak 山峰節點。
)

rows = []

for element in elements:
tags = element.get("tags", {})

latitude = element.get("lat")
longitude = element.get("lon")

if latitude is None or longitude is None:
continue

name = (
tags.get("name")
or tags.get("name:zh")
or tags.get("name:en")
or "未命名"
)

osm_id = element.get("id")

rows.append({
品牌/協會: APP_NAME,
縣市: county,
鄉鎮市區: township,
名稱: name,
WGS_X: float(longitude),
WGS_Y: float(latitude),
OSM_ID: osm_id,
OSM連結: (
f"https://www.openstreetmap.org/node/{osm_id}"
if osm_id
else ""
),
})

if not rows:
return pd.DataFrame(), (
沒有取得有效的山峰座標。
)

result = pd.DataFrame(rows)

result = result.drop_duplicates(
subset=["OSM_ID"]
)

result = result.sort_values(
by=["名稱"],
ascending=True,
)

result = result.reset_index(drop=True)

return result, (
f"查詢成功，共 {len(result)} 筆山峰座標。"
)


st.title("🏔️ 台灣 OSM 山峰座標查詢")

st.caption(
依縣市與鄉鎮市區查詢 OSM natural=peak 山峰節點
)

st.markdown("---")

st.subheader("📍 選擇查詢範圍")

col1, col2 = st.columns(2)

with col1:
selected_county = st.selectbox(
選擇縣市,
options=list(ADMIN_AREAS.keys()),
)

with col2:
township_options = [
全部
] + ADMIN_AREAS[selected_county]

selected_township = st.selectbox(
選擇鄉鎮市區,
options=township_options,
)

keyword = st.text_input(
名稱關鍵字，可留空,
placeholder="例如：山、峰、岳、嶺、玉山、雪山",
)

st.caption(
名稱篩選會在行政區查詢完成後執行。
)

search_button = st.button(
🔍 開始查詢,
type="primary",
)


if search_button:
with st.spinner(
f"正在查詢 {selected_county} "
f"{selected_township} 的山峰資料..."
):
df, message = query_mountains(
selected_county,
selected_township,
)

st.sidebar.header("⚙️ 查詢狀態")
st.sidebar.info(message)

if df.empty:
st.warning(message)
st.stop()

if keyword:
df = df[
df["名稱"].str.contains(
keyword,
case=False,
na=False,
)
].reset_index(drop=True)

if df.empty:
st.warning(
查詢到山峰資料，但沒有符合名稱關鍵字的結果。
)
st.stop()

st.success(
f"查詢完成，共 {len(df)} 筆山峰資料。"
)

st.subheader(
f"📊 查詢結果：{len(df)} 筆"
)

st.dataframe(
df,
use_container_width=True,
height=500,
hide_index=True,
column_config={
OSM連結: st.column_config.LinkColumn(
OSM 地圖,
display_text="開啟 OSM",
),
WGS_X: st.column_config.NumberColumn(
WGS_X 經度,
format="%.6f",
),
WGS_Y: st.column_config.NumberColumn(
WGS_Y 緯度,
format="%.6f",
),
},
)

st.markdown("---")

left_space, right_area = st.columns(
[8, 2],
)

copy_text = df.to_csv(
index=False,
sep="\t",
)

csv_data = df.to_csv(
index=False,
encoding="utf-8-sig",
)

with right_area:
copy_button(
text=copy_text,
tooltip="複製山峰資料",
copied_label="已複製",
icon="st",
key="copy_mountain_data",
)

st.download_button(
label="📥 下載 CSV",
data=csv_data,
file_name=(
f"{selected_county}_"
f"{selected_township}_"
mountains.csv
),
mime="text/csv",
use_container_width=True,
)

st.subheader("🗺️ 山峰位置")

map_df = df.rename(
columns={
WGS_Y: "latitude",
WGS_X: "longitude",
}
)

st.map(
map_df[
[
latitude,
longitude,
]
]
)


with st.expander("📖 使用說明"):
st.markdown(
"""
        1. 選擇縣市。
        2. 選擇鄉鎮市區，或選擇「全部」。
        3. 可輸入山峰名稱關鍵字。
        4. 按下「開始查詢」。
        5. 系統只查詢該行政區內的 OSM 山峰節點。
        6. 查詢結果右下方有複製資料按鈕。
        7. 查詢結果右下方有 CSV 下載按鈕。
        8. 地圖會顯示山峰位置。

        座標定義：

        - `WGS_X`：WGS84 經度 longitude
        - `WGS_Y`：WGS84 緯度 latitude
        - 座標系統：EPSG:4326 / WGS 84

        OSM 查詢條件：

        - `natural=peak`
        - 查詢物件類型：node
        - 查詢範圍：選定縣市或鄉鎮市區
        """
)
PYTHON

























































































































































































































































































































































































































































































































