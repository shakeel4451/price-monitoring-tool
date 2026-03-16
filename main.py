from playwright.sync_api import sync_playwright
import pandas as pd
import json
import os
import time
from datetime import datetime

HISTORY_FILE="daraz_price_history.json"

TARGET_PRODUCTS=[
  "https://www.daraz.pk/products/100-i3127508-s12470300.html",
  "https://www.daraz.pk/products/-i541554565-s2534895720.html",
  "https://www.daraz.pk/products/1-900-i4157310-s27320176.html",
  "https://www.daraz.pk/products/samsung-galaxy-s26-ultra-512-gb-get-free-galaxy-tab-a11-i1947943383-s14011679656.html"
]

def load_history():
  if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE,"r") as file:
      return json.load(file)
  return {}

def save_history(history_data):
  with open(HISTORY_FILE,"w") as file:
    json.dump(history_data,file,indent=4)

def run_daraz_monitor():
  print("🔍 Launching Daraz Live Price Monitor...")
  history=load_history()
  alerts=[]

  with sync_playwright() as p:
    browser=p.chromium.launch(headless=False)
    page=browser.new_page()

    for url in TARGET_PRODUCTS:
      print(f"📡 Scanning Daraz Product...")
      try:
        page.goto(url,timeout=6000)
        page.wait_for_selector(".pdp-price_type_normal", timeout=15000)
        title=page.locator(".pdp-mod-product-badge-title").inner_text()
        price_text = page.locator(".pdp-price_type_normal").first.inner_text()

        clean_price_string=price_text.replace("Rs.","").replace(",","").strip()
        current_price=clean_price_string

        if title in history:
          old_price=history[title]
          price_diff=current_price - old_price

          if price_diff<0:
            status="📉 Price dropped"
          elif price_diff>0:
            status="📈 Price Increased"
          else:
            status="➖ NO CHANGE"
          print(f"   ↳ {title[:30]}... | Old: Rs.{old_price} | New: Rs.{current_price} | {status}")

          if price_diff<0:
            alerts.append({
              "Product" : title,
              "Old Price (Rs)": old_price,
              "New Price (Rs)": current_price,
              "Drop Amount": abs(price_diff),
              "Date Detected": datetime.now().strftime("%Y-%m-%d %H:%M"),
              "Link": url
            })
          else:
            print(f"   ↳ 🆕 New product logged: {title[:30]}... | Baseline price: Rs.{current_price}")

          history[title]=current_price
          time.sleep(3)
      except Exception as e:
        print(f"⚠️ Failed to scrape product. Reason: {e}")
        continue
    browser.close()
  
  save_history(history)
  print("\n💾 Daraz Memory Bank (JSON) Updated.")
  if alerts:
    df=pd.DataFrame(alerts)
    report_name = f"Daraz_Price_Drops_{datetime.now().strftime('%Y%m%d')}.xlsx"
    df.to_excel(report_name, index=False)
    print(f"🚨 ALERT: Price drops detected! Report generated: {report_name}")
  else:
    print("✅ No price drops detected today.")

if __name__=="__main__":
  run_daraz_monitor()