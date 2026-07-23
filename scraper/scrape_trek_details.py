import time
import pandas as pd
from playwright.sync_api import sync_playwright

INPUT_CSV = "uttarakhand_treks.csv"
OUTPUT_CSV = "uttarakhand_treks_full.csv"

df = pd.read_csv(INPUT_CSV)

columns = [
    "Price",
    "Duration",
    "Max Altitude",
    "Trekking Distance",
    "Grade",
    "Best Time",
    "Overview"
]

for col in columns:
    if col not in df.columns:
        df[col] = ""

with sync_playwright() as p:

    browser = p.chromium.launch(headless=False)

    page = browser.new_page(
        viewport={"width": 1400, "height": 1000}
    )

    for idx, row in df.iterrows():

        print(f"\nScraping {idx+1}/{len(df)}")
        print(row["Trek"])

        try:

            page.goto(row["URL"], wait_until="networkidle")
            page.wait_for_timeout(3000)

            # -----------------------------
            # PRICE
            # -----------------------------

            try:
                price = page.locator("span.text-4xl").first.inner_text().strip()
            except:
                price = ""

            # -----------------------------
            # DETAILS
            # -----------------------------

            duration = ""
            distance = ""
            altitude = ""
            grade = ""
            months = ""

            cards = page.locator("div.flex.flex-wrap.items-start.gap-2.text-gray-800")

            for i in range(cards.count()):

                card = cards.nth(i)

                try:
                    label = (
                        card.locator("span.font-semibold")
                        .first
                        .inner_text()
                        .replace(":", "")
                        .strip()
                    )

                    value = (
                        card.locator("span.flex-1")
                        .first
                        .inner_text()
                        .strip()
                    )

                    if label == "Days":
                        duration = value

                    elif label == "Distance":
                        distance = value

                    elif label == "Altitude":
                        altitude = value

                    elif label == "Grade":
                        grade = value

                    elif label == "Months":
                        months = value

                except:
                    pass

            # -----------------------------
            # OVERVIEW
            # -----------------------------

            overview = ""

            try:

                container = page.locator("div.whythistrek").first

                paragraphs = container.locator("p")

                text = []

                for i in range(paragraphs.count()):

                    para = paragraphs.nth(i).inner_text().strip()

                    if len(para) > 40:
                        text.append(para)

                overview = "\n\n".join(text)

            except:
                overview = ""

            # -----------------------------
            # SAVE
            # -----------------------------

            df.at[idx, "Price"] = price
            df.at[idx, "Duration"] = duration
            df.at[idx, "Max Altitude"] = altitude
            df.at[idx, "Trekking Distance"] = distance
            df.at[idx, "Grade"] = grade
            df.at[idx, "Best Time"] = months
            df.at[idx, "Overview"] = overview

            print("Price:", price)
            print("Days:", duration)
            print("Distance:", distance)
            print("Altitude:", altitude)
            print("Grade:", grade)
            print("Months:", months)
            print("Overview Length:", len(overview))

        except Exception as e:
            print("ERROR:", e)

        df.to_csv(
            OUTPUT_CSV,
            index=False,
            encoding="utf-8-sig"
        )

        time.sleep(1)

    browser.close()

print("\nFinished!")
print(f"Saved to {OUTPUT_CSV}")