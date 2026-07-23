import pandas as pd
import re

INPUT_FILE = "uttarakhand_treks_full.csv"
OUTPUT_FILE = "clean_treks.csv"

df = pd.read_csv(INPUT_FILE)

# ----------------------------
# Remove duplicate treks
# ----------------------------
df = df.drop_duplicates(subset=["Trek"]).reset_index(drop=True)

# ----------------------------
# Price
# ₹9,950 -> 9950
# ----------------------------
def clean_price(x):
    if pd.isna(x):
        return None

    x = str(x)
    x = x.replace("₹", "")
    x = x.replace(",", "")

    m = re.search(r"\d+", x)

    return int(m.group()) if m else None


# ----------------------------
# Days
# "6" / "6 Days" -> 6
# ----------------------------
def clean_days(x):
    if pd.isna(x):
        return None

    m = re.search(r"\d+", str(x))

    return int(m.group()) if m else None


# ----------------------------
# Distance
# "37 km" -> 37
# ----------------------------
def clean_distance(x):
    if pd.isna(x):
        return None

    m = re.search(r"[\d.]+", str(x))

    return float(m.group()) if m else None


# ----------------------------
# Altitude
# "14100 FT" -> 14100
# ----------------------------
def clean_altitude(x):
    if pd.isna(x):
        return None

    x = str(x).replace(",", "")

    m = re.search(r"\d+", x)

    return int(m.group()) if m else None


# ----------------------------
# Grade
# ----------------------------
def clean_grade(x):
    if pd.isna(x):
        return ""

    return str(x).strip().title()


# ----------------------------
# Months
# ----------------------------
def clean_months(x):
    if pd.isna(x):
        return ""

    return (
        str(x)
        .replace("|", ",")
        .replace(" ,", ",")
        .strip()
    )


# ----------------------------
# Apply cleaning
# ----------------------------

df["Price"] = df["Price"].apply(clean_price)
df["Duration"] = df["Duration"].apply(clean_days)
df["Trekking Distance"] = df["Trekking Distance"].apply(clean_distance)
df["Max Altitude"] = df["Max Altitude"].apply(clean_altitude)
df["Grade"] = df["Grade"].apply(clean_grade)
df["Best Time"] = df["Best Time"].apply(clean_months)

# ----------------------------
# Remove rows missing essentials
# ----------------------------

df = df.dropna(
    subset=[
        "Price",
        "Duration",
        "Trekking Distance",
        "Max Altitude",
    ]
)

# ----------------------------
# Sort by price
# ----------------------------

df = df.sort_values("Price").reset_index(drop=True)

# ----------------------------
# Save
# ----------------------------

df.to_csv(OUTPUT_FILE, index=False)

print("=" * 40)
print("Cleaning Complete!")
print("=" * 40)
print("Treks:", len(df))
print("Columns:")
print(df.columns.tolist())
print()
print(df.head())

print(f"\nSaved as {OUTPUT_FILE}")