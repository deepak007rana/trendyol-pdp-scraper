import asyncio
import json
from playwright.async_api import async_playwright, TimeoutError

COUNTRY_MAP = {
    "ae": "United Arab Emirates",
    "sa": "Saudi Arabia"
}

MAX_RETRIES = 2


async def extract_product_json(page):
    locator = page.locator('div[fragment-partial="flash-sales-banner"] script').first
    await locator.wait_for(state="attached", timeout=20000)

    script_content = await locator.text_content()
    if not script_content:
        raise ValueError("Script tag is empty")

    json_text = script_content.split("=", 1)[1].rsplit(";", 1)[0]
    return json.loads(json_text)


def build_output_json(data):
    product = data["product"]
    variants = []

    for v in product.get("variants", []):
        variants.append({"value": v.get("value"),"inStock": v.get("inStock", False)})

    rating_avg = product["ratingScore"].get("averageRating", 0)
    rating_avg = round(rating_avg, 1)

    english_data = product.get("englishTranslation", {})

    if english_data:
        prod_name = english_data.get("productName") or "-"
        brand = english_data.get("brandName") or "-"

        categories = (english_data.get("webBrandCategoryGenders", {}).get("categories", []))
        cat_path = "/".join(cat.get("name")for cat in reversed(categories) if cat.get("name")) or "-"

    else:
        prod_name = product.get("name") or "-"
        brand = product.get("brand", {}).get("name") or "-"
        cat_path = product.get("category", {}).get("hierarchy") or "-"

    output = {
        "product_title": prod_name,
        "brand": brand,
        "review": product["ratingScore"].get("totalCount") or "-",
        "rating": rating_avg,
        "category_path": cat_path,
        "variants": {"size": variants},
        "msrp": product.get("merchantListing", {})
            .get("winnerVariant", {})
            .get("price", {})
            .get("sellingPrice", {})
            .get("value", "") or "-",
        "price": product.get("merchantListing", {})
            .get("winnerVariant", {})
            .get("price", {})
            .get("discountedPrice", {})
            .get("value") or "-",
        "seller_name": product.get("merchantListing", {})
            .get("merchant", {})
            .get("name", "") or "-"
    }

    return output


async def scrape_product(sku_url, country_code):
    country_name = COUNTRY_MAP[country_code]

    async with async_playwright() as playwright:
        for attempt in range(1, MAX_RETRIES + 1):
            browser = None
            try:
                browser = await playwright.chromium.launch(
                    headless=True,
                    args=[
                        "--disable-blink-features=AutomationControlled",
                        "--no-sandbox",
                        "--disable-dev-shm-usage",
                    ]
                )

                context = await browser.new_context(
                    user_agent=(
                        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                        "AppleWebKit/537.36 (KHTML, like Gecko) "
                        "Chrome/120.0.0.0 Safari/537.36"
                    ),
                    locale="en-US",
                )

                page = await context.new_page()
                await page.goto(sku_url,timeout=60000, wait_until="domcontentloaded")

                try:
                    await page.locator('button[id="onetrust-reject-all-handler"]').wait_for(timeout=10000)
                    await page.click('button[id="onetrust-reject-all-handler"]')
                except TimeoutError:
                    pass

                await asyncio.sleep(1)
                try:
                    await page.locator('select[id="country-select"]').wait_for(timeout=10000)
                    await page.select_option('select[id="country-select"]', label=country_name)
                    await page.click('button[data-testid="country-select-btn-desktop"]')
                except TimeoutError:
                    pass

                await asyncio.sleep(1)
                raw_json = await extract_product_json(page)
                output = build_output_json(raw_json)

                await browser.close()
                return output
            except Exception as e:
                if browser:
                    await browser.close()
                if attempt == MAX_RETRIES:
                    print(f"Got Error while getting the data: {e}")
                    raise

async def main():
    sku = input("Enter SKU Id or URL: ").strip()
    if not "trendyol.com" in sku:
        sku = f"https://www.trendyol.com/en/ispartalilar/9999-full-orthopedic-black-white-high-sole-women-s-sports-shoes-water-resistant-p-{sku}"

    country_code = input("Enter Country code: ").strip().lower()

    if country_code not in ("ae", "sa"):
        print("Invalid SKU url or country code")
        return

    result = await scrape_product(sku, country_code)

    print("FINAL OUTPUT JSON")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(main())
