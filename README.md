# Trendyol PDP Scraper (AE & SA)

## Overview
This project extracts Product Detail Page (PDP) information from Trendyol for the
United Arab Emirates (AE) and Saudi Arabia (SA) marketplaces.

The scraper accepts a product SKU or full PDP URL and returns a single clean JSON
object containing the required product fields.

---

## Extracted Fields
- product_title  
- brand  
- review  
- rating  
- category_path  
- variants  
- msrp  
- price  
- seller_name  

---

## Why Playwright?
Trendyol PDP data is dynamically rendered and may not reliably return structured content
through standard HTTP clients such as requests or Scrapy, which do not execute JavaScript.
While third-party rendering proxy services can provide JS rendering using Requests.
Here Playwright is used to directly control browser execution and ensure reliable extraction across both AE and SA
marketplaces.

---

## Requirements
- Python 3.9+
- Playwright

---

## Installation

```bash

git clone https://github.com/deepak007rana/trendyol-pdp-scraper.git
cd trendyol-pdp-scraper
pip install -r requirements.txt
playwright install
