from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from datetime import datetime
from zoneinfo import ZoneInfo
import google_sheets
import time

URLS = [
      "https://chartink.com/screener/copy-bearish-engulifing-see-after-3-15-pm-for-next-day-trade-5168",	
      "https://chartink.com/screener/copy-bearish-maribozu-337",
       "https://chartink.com/screener/copy-yesterday-and-today-ema3-without-open-high-bearish-55",
       "https://chartink.com/screener/copy-bearish-engulfing-moderate-478",
      "https://chartink.com/screener/agp-bearong-2",
      "https://chartink.com/screener/shesha-bearish1",
      "https://chartink.com/screener/agp-shesha-bearish-2",
      "https://chartink.com/screener/one-rupee-sidh-f-0-sell",
      "https://chartink.com/screener/copy-f-o-weak-stocks-2",
      "https://chartink.com/screener/svp2-closing-3-up-since-3-days",
      "https://chartink.com/screener/copy-copy-how-to-find-future-and-option-stocks-buy-entry-future-3",
      "https://chartink.com/screener/copy-stocks-in-downtrend-1959",
      "https://chartink.com/screener/copy-w6-f-o-2",
      "https://chartink.com/screener/copy-1week-sell-twist",
      "https://chartink.com/screener/copy-weekly-bollinger-sell-3",
      "https://chartink.com/screener/sell-postesttttttttttttttttt",
      "https://chartink.com/screener/copy-cci-below-100-62",
      "https://chartink.com/screener/copy-bearish-rsi-stoc-1215",
      "https://chartink.com/screener/srf-narayana-futures-positional-bearish",
      "https://chartink.com/screener/sell-bollinger-band-weekly-15",
      "https://chartink.com/screener/copy-bolinger-band-bearish-reversal-aps-401",
      "https://chartink.com/screener/copy-ut-sell-eod-basis-5",
      "https://chartink.com/screener/copy-sell-f-0",
      "https://chartink.com/screener/copy-perfect-bearish-3266",
      "https://chartink.com/screener/50-bearish-engulifing-see-after-3-15-pm-for-next-day-trade"
     ]
       
sheet_id = "1k-MQ6VNDgE-twtGytv5uIQlQAgVX_RTExeNoZZiNlaA"
worksheet_name = ["p1","p2","p3","p4","p5","p6","p7","p8","p9","p10","p11","p12","p13","p14","p15","p16","p17","p18","p19","p20","p21","p22","p23","p24","p25"]

def scrape_chartink(url, worksheet_name):
    print(f"\n🚀 Starting scrape for '{worksheet_name}'")
    print(f"🌐 Loading URL: {url}")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
        )
        page = context.new_page()

        headers = ["Sr", "Stock Name", "Symbol", "close", "Change", "Price", "Volume"]

        try:
            page.goto(url, wait_until="domcontentloaded")
            time.sleep(1)

            rows = []

            if page.is_visible("text='No records found'"):
                print(f"⚠️ No records found at {url}. Writing blank row.")
                rows = [[""]]
            else:
                try:
                    page.wait_for_selector(
                        "tbody tr",
                        timeout=10000
                    )

                    table_rows = page.query_selector_all(
                        "tbody tr"
                    )

                    print(f"📥 Extracted {len(table_rows)} rows.")

                    for row in table_rows:
                        sr = row.query_selector('td[data-field="sr"]')
                        stock = row.query_selector('td[data-field="name"]')
                        symbol = row.query_selector('td[data-field="nsecode"]')
                        close = row.query_selector('td[data-field="scan-column-default-close"]')
                        change = row.query_selector('td[data-field="scan-column-default-percent-change"]')
                        volume = row.query_selector('td[data-field="scan-column-default-volume"]')

                        rows.append([
                            sr.text_content().strip() if sr else "",
                            stock.text_content().strip() if stock else "",
                            symbol.text_content().strip() if symbol else "",
                            close.text_content().strip() if close else "",
                            change.text_content().strip() if change else "",
                            volume.text_content().strip() if volume else ""
                        ])

                    if len(rows) == 0:
                        print("⚠️ Table found but no rows present.")
                        rows = [[""]]

                except PlaywrightTimeoutError:
                    print(f"❌ Table not found at {url}.")
                    rows = [[""]]

                google_sheets.update_google_sheet_by_name(
                    sheet_id, worksheet_name, headers, rows
                )

        except PlaywrightTimeoutError:
            print(f"❌ Timeout error at {url}. Writing blank row.")
            google_sheets.update_google_sheet_by_name(
                sheet_id, worksheet_name, headers, [[""]]
            )

        except Exception as e:
            print(f"❌ Unexpected error: {e}. Writing blank row.")
            google_sheets.update_google_sheet_by_name(
                sheet_id, worksheet_name, headers, [[""]]
            )

        now = datetime.now(ZoneInfo("Asia/Kolkata")).strftime("Last updated on: %Y-%m-%d %H:%M:%S")
        google_sheets.append_footer(sheet_id, worksheet_name, [now])

        print(f"✅ Worksheet '{worksheet_name}' updated.")

for index, url in enumerate(URLS):
    scrape_chartink(url, worksheet_name[index])
    print(f"⏱️ Finished updating '{worksheet_name[index]}'")
