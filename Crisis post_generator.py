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
                         lon: float) -> str:
    """
    Create 3–4 urgent first‑person sentences describing the crisis.
    """
    prompt = f"""
        You are a Hamburg resident live‑posting on social media.
        A {crisis_event} is unfolding near {place} (coordinates: {lat:.5f}, {lon:.5f}).
        Write 3–4 short, urgent sentences in the first person to describe the situation.

        During parsing, please follow German addresses into structured components:
        1. "Street_or_Landmark": The most specific location such as a street name, square, or known landmark (e.g., "Achtern Born", "Waltershofer Damm", "Am Stadtrand").
        2. "District_or_Suburb": The local subdistrict or neighborhood within the city (e.g., "Osdorf", "Sasel", "Waltershof").
        3. "City_District": The city district name within larger cities such as Hamburg (e.g., "Altona", "Wandsbek", "Hamburg-Mitte").
        4. "City": The main city name (e.g., "Hamburg").
        5. "Postal_Code": The 5-digit German postal code (e.g., "22393", "21037").
        6. "Country": Always return "Deutschland".

        Example input:
        "Redder, Sasel, Wandsbek, Hamburg, 22393, Deutschland" 
        """

    response = client.chat.completions.create(
        model=model,
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
    )
    return response.choices[0].message.content.strip()


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
