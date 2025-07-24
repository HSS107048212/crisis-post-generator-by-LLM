# ===== 1. Basic Setup =====
from openai import OpenAI
import pandas as pd
import time
from tqdm.auto import tqdm  # Progress bar

api_key   = ""
base_url  = "https://chat-ai.academiccloud.de/v1"
model     = "qwen3-32b"      # Can be replaced with other models available from GWDG
temperature = 0.8            # Creativity level (adjustable)

client = OpenAI(api_key=api_key, base_url=base_url)

# ===== 2. Custom Function: Generate Crisis Post =====
def generate_crisis_post(place: str,
                         crisis_event: str,
                         lat: float,
                         lon: float,
                         Amenities: str) -> str:
    """
    Create 3–4 urgent first‑person sentences describing the crisis.
    """
    prompt = f"""
      You are a Hamburg resident live-posting on social media.

      A **{crisis_event}** is unfolding near **{place}**. There are several amenities: {Amenities} in this area — please make sure your description stays **within the vicinity of this location**, based on these surroundings.

      Write a short and urgent **first-person** social media post in **English**, consisting of **3 to 4 vivid, emotional sentences**.

      Make sure a **clear reference to the location** in the style of German addresses. Internally follow this structured hierarchy for reference only:
      - Street_or_Landmark (e.g., "Achtern Born")
      - District_or_Suburb (e.g., "Osdorf")
      - City_District (e.g., "Altona")
      - City = "Hamburg"

      Do **not** output the address structure itself — just write the **natural post** as a local would. Focus on **urgency, chaos, atmosphere, and personal reaction**. 
      Sound natural, realistic, and emotionally expressive

      """

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()



# ===== 3. 範例 DataFrame (`df`) 應包含下列欄位 =====
# df = pd.read_csv("your_locations.csv")  # 或任何方式載入
# 必須具備：Latitude, Longitude, Place, Crisis_Event

# ===== 4. 實際批次呼叫並新增新欄位 =====
posts = []
for _, row in tqdm(df.iterrows(), total=len(df), desc="Generating posts"):
    try:
        post_text = generate_crisis_post(
            place        = row["Place"],
            crisis_event = row["Crisis_Event"],
            lat          = row["Latitude"],
            lon          = row["Longitude"],
        )
    except Exception as e:
        # 若 API 超時或配額不足，可在這裡做重試或填入空字串
        print(f"⚠️  Row {_}: {e}")
        post_text = ""
    posts.append(post_text)
    time.sleep(0.4)     # 視情況調整，避免触發速度限制

df["Crisis_Post"] = posts



# ===== 3. Example DataFrame (`df`) should contain the following columns =====
# df = pd.read_csv("your_locations.csv")  # Or load it any way you prefer
# Required columns: Latitude, Longitude, Place, Crisis_Event

# ===== 4. Run the generation in batch and add a new column =====
posts = []
for _, row in tqdm(df.iterrows(), total=len(df), desc="Generating posts"):
    try:
        post_text = generate_crisis_post(
            place        = row["Place"],
            crisis_event = row["Crisis_Event"],
            lat          = row["Latitude"],
            lon          = row["Longitude"],
        )
    except Exception as e:
        # If API times out or quota exceeded, handle it here (e.g., retry or assign an empty string)
        print(f"⚠️  Row {_}: {e}")
        post_text = ""
    posts.append(post_text)
    time.sleep(0.4)  # Adjust as needed to avoid rate limits

df["Crisis_Post"] = posts

# Extract text after </think> (specific to Qwen model output)
df["Crisis_Post"] = df["Crisis_Post"].apply(lambda x: x.split("</think>", 1)[-1] if isinstance(x, str) and "</think>" in x else x)

# ===== 5. (Optional) Save or view =====
df.to_excel("locations_with_posts.xlsx", index=False)
df.head()
