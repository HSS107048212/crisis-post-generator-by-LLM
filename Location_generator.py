import random
import time
import requests
import pandas as pd

# 定義 Hamburg 的地理邊界（概略範圍）
MIN_LAT, MAX_LAT = 53.45, 53.65
MIN_LON, MAX_LON = 9.8, 10.3

# 危機事件類型清單
CRISIS_EVENTS = ["flood", "fire", "protest", "blackout"]

# Nominatim 設定
NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
HEADERS = {"User-Agent": "hamburg-crisis-bot/1.0"}

# 儲存結果
results = []

# 產生地點座標
for i in range(5):
    lat = round(random.uniform(MIN_LAT, MAX_LAT), 6)
    lon = round(random.uniform(MIN_LON, MAX_LON), 6)

    # 呼叫 Nominatim 取得地點名稱
    params = {
        "lat": lat,
        "lon": lon,
        "format": "json",
        "zoom": 17,
        "addressdetails": 1
    }

    try:
        response = requests.get(NOMINATIM_URL, params=params, headers=HEADERS)
        data = response.json()
        place_name = data.get("display_name", "未知地點")
    except Exception as e:
        place_name = f"查詢失敗: {e}"

    # 隨機產生事件
    crisis = random.choice(CRISIS_EVENTS)

    # 存入清單
    results.append({
        "Index": i + 1,
        "Latitude": lat,
        "Longitude": lon,
        "Place": place_name,
        "Crisis_Event": crisis
    })

    print(f"[{i+1}/5] {place_name} - {crisis}")
    time.sleep(1)  # Nominatim usage policy 建議每秒不超過 1 次

import re
# 使用正則表達式移除5碼郵遞區號與德國
def clean_place(text):
    text = re.sub(r",\s*\d{5}", "", text)  # 移除郵遞區號，如 ", 22549"
    text = re.sub(r",\s*Deutschland", "", text)  # 移除 ", Deutschland"
    return text.strip()

# 儲存為 DataFrame
df = pd.DataFrame(results)
# 套用轉換
df["Place"] = df["Place"].apply(clean_place)
df
