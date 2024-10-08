from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from tabulate import tabulate
import time
import sqlite3
from datetime import datetime
import re

chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")
chrome_options.add_argument("--disable-extensions")
chrome_options.add_argument("--proxy-server='direct://'")
chrome_options.add_argument("--proxy-bypass-list=*")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-setuid-sandbox")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

def extract_order_number(strings):
    pattern = r'(\d+)\s*orders'
    for string in strings:
        match = re.search(pattern, string)
        if match:
            return int(match.group(1))
    return None
    
data = {
    "compra":[],
    "venta":[]
}

for opt, url in zip(["venta", "compra"], ["https://p2p.binance.com/en/trade/sell/USDT?fiat=BOB&payment=all-payments","https://p2p.binance.com/trade/all-payments/USDT?fiat=BOB"]):
    driver.get(url)
    driver.implicitly_wait(10)
    attempts = 3
    for _ in range(attempts):
        try:
            rows = driver.find_elements(By.CSS_SELECTOR, 'tr')  
            for row in rows:
                cols = [col.text for col in row.find_elements(By.CSS_SELECTOR, 'td')]
                orders = extract_order_number(cols)
                if cols and orders > 100:
                    data[opt].append(cols)
        except StaleElementReferenceException:
            time.sleep(1)  

driver.quit()
sell_price = sum([float(row[1].split('\n')[0]) for row in data["venta"]]) / len(data["venta"])
buy_price = sum([float(row[1].split('\n')[0]) for row in data["compra"]]) / len(data["compra"])

print(f"USTD -> BOB: {sell_price:.2f}")
print(f"BOB -> USTD: {buy_price:.2f}")

conn = sqlite3.connect('prices.db')

cursor = conn.cursor()

for price, name in zip([sell_price, buy_price],["USDT2BS", "BS2USTD"]):
    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS {name} (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        price INTEGER,
        date DATETIME,
        source TEXT
    )
    ''')
    cursor.execute(f'''
    INSERT INTO {name} (price, date, source)
    VALUES (?, ?, ?)
    ''', (f"{price:.2f}", datetime.now(), "binance"))
    conn.commit()
    print(f"{name} Data Saved")

conn.close()
print("Data inserted successfully.")