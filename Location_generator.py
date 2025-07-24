import random
import time
import requests
import pandas as pd
import re

# 定義 Hamburg 的地理邊界（概略範圍）
MIN_LAT, MAX_LAT = 53.45, 53.65
MIN_LON, MAX_LON = 9.8, 10.3

CRISIS_EVENTS = ["flood", "fire", "protest", "blackout"]

NOMINATIM_URL = "https://nominatim.openstreetmap.org/reverse"
OVERPASS_URL = "https://overpass-api.de/api/interpreter"
HEADERS = {"User-Agent": "hamburg-crisis-bot/1.0"}

results = []

def clean_place(text):
    text = re.sub(r",\s*\d{5}", "", text)
    text = re.sub(r",\s*Deutschland", "", text)
    return text.strip()

def get_nearby_amenities(lat, lon):
    query = f"""
    [out:json][timeout:25];
    (
      node
        (around:1000,{lat},{lon})
        ["amenity"];
      way
        (around:1000,{lat},{lon})
        ["amenity"];
      relation
        (around:1000,{lat},{lon})
        ["amenity"];
    );
    out center 10;
    """
    try:
        response = requests.post(OVERPASS_URL, data=query, headers=HEADERS)
        response.raise_for_status()
        data = response.json()
        amenities = []
        for element in data.get("elements", []):
            tags = element.get("tags", {})
            name = tags.get("name")
            amenity_type = tags.get("amenity")
            if name:
                amenities.append(f"{name} ({amenity_type})")
            elif amenity_type:
                amenities.append(f"[Unnamed] ({amenity_type})")
            if len(amenities) >= 10:
                break
        return amenities
    except Exception as e:
        return [f"Error fetching amenities: {e}"]

# 產生地點並查詢
for i in range(5):
    lat = round(random.uniform(MIN_LAT, MAX_LAT), 6)
    lon = round(random.uniform(MIN_LON, MAX_LON), 6)

    # 查詢地址
    try:
        response = requests.get(NOMINATIM_URL, params={
            "lat": lat,
            "lon": lon,
            "format": "json",
            "zoom": 17,
            "addressdetails": 1
        }, headers=HEADERS)
        data = response.json()
        place_name = clean_place(data.get("display_name", "未知地點"))
    except Exception as e:
        place_name = f"查詢失敗: {e}"

    # 隨機事件
    crisis = random.choice(CRISIS_EVENTS)

    # 查詢周邊基礎設施
    amenities = get_nearby_amenities(lat, lon)

    results.append({
        "Index": i + 1,
        "Latitude": lat,
        "Longitude": lon,
        "Place": place_name,
        "Crisis_Event": crisis,
        "Amenities": "; ".join(amenities)
    })

    print(f"[{i+1}/5] {place_name} - {crisis}")
    time.sleep(1)



# 儲存為 DataFrame
df = pd.DataFrame(results)

import re
# 使用正則表達式移除5碼郵遞區號與德國
def clean_place(text):
    text = re.sub(r",\s*\d{5}", "", text)  # 移除郵遞區號，如 ", 22549"
    text = re.sub(r",\s*Deutschland", "", text)  # 移除 ", Deutschland"
    return text.strip()
# 套用轉換
df["Place"] = df["Place"].apply(clean_place)

def clean_amenities(text):
    time.sleep(2)
    items = text.split(";")
    named = []
    unnamed = []
    for item in items:
        item = item.strip()
        if match := re.match(r"(.+?) \((.+?)\)", item):
            name, category = match.groups()
            if name == "[Unnamed]":
                unnamed.append(category)
            else:
                named.append(f"{name} ({category})")
    
    if named:
        return "; ".join(named)
    else:
        return "; ".join(unnamed)

# 套用至 DataFrame 欄位
df["Amenities"] = df["Amenities"].apply(clean_amenities)

df
