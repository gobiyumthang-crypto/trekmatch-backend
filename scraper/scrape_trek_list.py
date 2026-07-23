from playwright.sync_api import sync_playwright
import pandas as pd

URL = "https://trekthehimalayas.com/region/uttarakhand"

with sync_playwright() as p:
    browser = p.chromium.launch(headless=False)
    page = browser.new_page(viewport={"width": 1400, "height": 1000})

    page.goto(URL, wait_until="networkidle")

    # Scroll to load all trek cards
    previous_height = 0

    while True:
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)

        height = page.evaluate("document.body.scrollHeight")

        if height == previous_height:
            break

        previous_height = height

    cards = page.locator("a.group")

    print(f"Found {cards.count()} trek cards")

    data = []

    for i in range(cards.count()):
        card = cards.nth(i)

        try:
            name = card.locator("h3").inner_text().strip()

            href = card.get_attribute("href")
            url = "https://trekthehimalayas.com" + href

            image = card.locator("img").get_attribute("src")

            region = card.locator("span.line-clamp-1").inner_text().strip()

            spans = card.locator("div.mt-1 span.uppercase")

            duration = spans.nth(0).inner_text().replace("Duration:", "").strip()

            grade = spans.nth(1).inner_text().replace("Grade:", "").strip()

            data.append({
                "Trek": name,
                "URL": url,
                "Region": region,
                "Duration": duration,
                "Grade": grade,
                "Image": image
            })

            print(name)

        except Exception as e:
            print("Skipped:", e)

    browser.close()

df = pd.DataFrame(data)

df.drop_duplicates(subset=["URL"], inplace=True)

df.to_csv("uttarakhand_treks.csv", index=False)

print(df.head())
print(f"\nSaved {len(df)} treks")