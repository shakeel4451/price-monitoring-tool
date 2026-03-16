from playwright.sync_api import sync_playwright
import pandas as pd
import json
import os
import time
from datetime import datetime

HISTORY_FILE="daraz_price_history.json"

TARGET_PRODUCTS=[
  "https://www.daraz.pk/catalog/?q=laptops",
  "https://www.daraz.pk/catalog/?q=ear%20buds"
]

def load_history():
  if os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE,"r") as file:
      return json.load(file)
  return {}

def save_history(history_data):
  with open(HISTORY_FILE,"w") as file:
    json.dump(history_data,file,indent=4)