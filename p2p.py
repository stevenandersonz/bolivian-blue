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


chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode
chrome_options.add_argument("--disable-gpu")  # Disable GPU hardware acceleration (optional)
chrome_options.add_argument("--no-sandbox")  # Bypass OS security model (optional)
chrome_options.add_argument("--disable-dev-shm-usage")
# Use webdriver-manager to handle ChromeDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Load the page
url = "https://p2p.binance.com/en/trade/sell/USDT?fiat=BOB&payment=all-payments"
driver.get(url)

# Wait for the JavaScript to execute and for the content to be loaded
driver.implicitly_wait(10)  # Waits up to 10 seconds

# Function to retry fetching elements
def fetch_trade_rows():
    attempts = 3  # Number of retry attempts
    for _ in range(attempts):
        try:
            trade_rows = []
            rows = driver.find_elements(By.CSS_SELECTOR, 'tr')  # Update selector based on the content
            for row in rows:
                cols = [col.text for col in row.find_elements(By.CSS_SELECTOR, 'td')]
                if cols:
                    trade_rows.append(cols)
            return trade_rows
        except StaleElementReferenceException:
            time.sleep(1)  # Wait briefly before retrying
    return []  # Return empty if unable to fetch

# Get trade rows with retry mechanism
trade_rows = fetch_trade_rows()

avg_price = sum([float(row[1].split('\n')[0]) for row in trade_rows]) / len(trade_rows)
print(f"USTD -> BOB: {avg_price:.2f}")

# Close the browser
driver.quit()


# Define the price data as a Python object (dictionary)
price_data = {
    'price': f"{avg_price:.2f}",  # Example price
    'date': datetime.now(),  # Current date and time
    'source': 'Binance'  # Example source
}

# Step 1: Connect to the SQLite database (or create it if it doesn't exist)
conn = sqlite3.connect('prices.db')

# Step 2: Create a cursor object to execute SQL commands
cursor = conn.cursor()

# Step 3: Create the table (if it doesn't exist)
cursor.execute('''
CREATE TABLE IF NOT EXISTS USTD2BS (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    price INTEGER,
    date DATETIME,
    source TEXT
)
''')

# Step 4: Insert the data into the table
cursor.execute('''
INSERT INTO USTD2BS (price, date, source)
VALUES (?, ?, ?)
''', (price_data['price'], price_data['date'], price_data['source']))

# Step 5: Commit the transaction
conn.commit()

# Step 6: Close the connection
conn.close()

print("Data inserted successfully.")