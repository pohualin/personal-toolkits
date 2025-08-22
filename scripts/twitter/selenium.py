import time
import csv
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

# Configure Chrome options for stable scraping
chrome_options = Options()
# chrome_options.add_argument("--headless")  # Uncomment to run headless
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("--window-size=1920,1080")

# Initialize WebDriver
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

# Target tweet URL on X
url = 'https://x.com/Cristiano/status/1922957070048874841'

driver.get(url)

# Wait for tweet text element to load
wait = WebDriverWait(driver, 15)
wait.until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="tweetText"]')))
time.sleep(2)  # Allow extra JS to load

try:
    # Extract tweet text
    tweet_text_elems = driver.find_elements(By.XPATH, '//div[@data-testid="tweetText"]')
    tweet_text = ' '.join([elem.text for elem in tweet_text_elems])
    print("Tweet Text:", tweet_text)
    

    # Engagement stats elements
    stats_elems = driver.find_elements(By.XPATH, '//span[@data-testid="app-text-transition-container"]/span/span')
    stats_list = [elem.text for elem in stats_elems]
    
    print("stats_list:", stats_list)

    views = stats_list[0] if len(stats_list) > 0 else None
    replies = stats_list[10] if len(stats_list) > 1 else None
    reposts = stats_list[11] if len(stats_list) > 2 else None
    likes = stats_list[12] if len(stats_list) > 3 else None
    bookmarks = stats_list[13] if len(stats_list) > 4 else None

    # Print extracted data
    print("Views:", views)
    print("Replies:", replies)
    print("Reposts:", reposts)
    print("Likes:", likes)
    print("Bookmarks:", bookmarks)

    # Save data to CSV
    with open('tweet_data.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['tweet_text', 'views', 'replies', 'reposts', 'likes', 'bookmarks'])
        writer.writerow([tweet_text, views, replies, reposts, likes, bookmarks])
    
    print("Data saved to tweet_data.csv")

except Exception as e:
    print("Error:", e)

driver.quit()
