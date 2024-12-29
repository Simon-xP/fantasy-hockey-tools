import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager

def setup_driver():
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver


# scrape table from Moneypuck.com
def scrape_moneypuck_table():
    driver = setup_driver()

    try:
        url = "https://moneypuck.com/stats.htm"
        driver.get(url)
    
        time.sleep(10)
        
        table_xpath = '//*[@id="includedContent"]/table'
        table = driver.find_element(By.XPATH, table_xpath)
        
        rows = table.find_elements(By.TAG_NAME, "tr")
        
        for i, row in enumerate(rows[:1]):
            cells = row.find_elements(By.TAG_NAME, "td")
            row_data = [cell.text for cell in cells]
            print(f"Row {i + 1}: {row_data}")
    
    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_moneypuck_table()
