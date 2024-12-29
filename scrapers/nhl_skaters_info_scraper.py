import os
import time
import pandas as pd
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from datetime import datetime
from supabase import create_client, Client

# Constants
ACTIVE_PLAYERS_URL = "https://www.nhl.com/stats/skaters?report=bios&reportType=season&seasonFrom=20242025&seasonTo=20242025&gameType=2&sort=a_skaterFullName&page={page}&pageSize=100"
HISTORICAL_PLAYERS_URL = "https://www.nhl.com/stats/skaters?report=bios&reportType=season&seasonFrom=20082009&seasonTo=20242025&gameType=2&filter=gamesPlayed,gte,5&sort=a_skaterFullName&page={page}&pageSize=100"
TABLE_XPATH = '//*[@id="season-tabpanel"]/span/div/div[2]/table'

def setup_driver():
    options = Options()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    return driver

# Function to scrape one page from NHL stats page
def scrape_nhl_page(driver, url, is_active):
    driver.get(url)
    
    # Wait for the table to load
    try:
        table = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, TABLE_XPATH))
        )
    except Exception as e:
        print(f"Error: Table not found on page {url}")
        return []

    table_html = table.get_attribute('outerHTML')
    soup = BeautifulSoup(table_html, 'html.parser')
    rows = soup.find_all('tr')

    player_data = []
    for row in rows[1:]:  # skip header
        cells = row.find_all('td')
        if len(cells) > 1: 
            player_name = cells[1].text.strip()
            player_id = cells[1].find('a')['href'].split('/')[-1]

            if len(cells) == 21: # active player (current season)
                team = cells[2].text.strip()
                position = cells[4].text.strip()
                dob = cells[5].text.strip()
            elif len(cells) == 20: # active or retired player (historical data)
                team = None
                position = cells[3].text.strip()
                dob = cells[4].text.strip()
            else:
                continue

            player = {
                'id': player_id,
                'full_name': player_name,
                'position': position,
                'dob': dob,
                'team': team,
                'is_active': is_active
            }
            player_data.append(player)

    return player_data


# wrapper to scrape multiple pages
def scrape_multiple_pages(url_template, is_active, start_page, end_page):
    driver = setup_driver()
    all_players = []

    for page in range(start_page, end_page + 1):
        print(f"Scraping page {page}...")
        url = url_template.format(page=page)
        players = scrape_nhl_page(driver, url, is_active)
        all_players.extend(players)

    driver.quit()
    return all_players

# connect to Supabase
def connect_to_supabase():
    load_dotenv(dotenv_path="../.env") 
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    supabase: Client = create_client(url, key)
    return supabase

# insert/update Supabase
def update_supabase_with_players(players, supabase):
    for player in players:
        # Check if the player ID exists in the database
        response = supabase.table('players').select('id').eq('id', player['id']).execute()

        if response.data:
            if player['is_active']: # update is active
                supabase.table('players').update({'is_active': True}).eq('id', player['id']).execute()
                print(f"Updated {player['full_name']} to active.")
        else:
            # insert new players
            supabase.table('players').insert(player).execute()
            print(f"Inserted {player['full_name']} with ID {player['id']}.")

# run scraper
def run():
    supabase = connect_to_supabase()

    # scrape active players
    active_players = scrape_multiple_pages(ACTIVE_PLAYERS_URL, True, 0, 7)
    update_supabase_with_players(active_players, supabase)

    # scrape historical players
    historical_players = scrape_multiple_pages(HISTORICAL_PLAYERS_URL, False, 0, 26)
    update_supabase_with_players(historical_players, supabase)

    print("done")


# testing function
def test_scrape_nhl_page():
    driver = setup_driver()

    # test active players
    print("Testing active players scraping...")
    active_test_url = ACTIVE_PLAYERS_URL.format(page=0)
    active_players = scrape_nhl_page(driver, active_test_url, is_active=True)
    print(f"Active players scraped: {len(active_players)}")
    if active_players:
        print("Sample active player:", active_players[0])

    # test historical players
    print("\nTesting historical players scraping...")
    historical_test_url = HISTORICAL_PLAYERS_URL.format(page=0)
    historical_players = scrape_nhl_page(driver, historical_test_url, is_active=False)
    print(f"Historical players scraped: {len(historical_players)}")
    if historical_players:
        print("Sample historical player:", historical_players[0])

    driver.quit()

def quick_test_scrape_historical_data():
    driver = setup_driver()
    test_season_url = HISTORICAL_PLAYERS_URL.format(season=20002001, page=0)  # Test with a single season and page

    try:
        print("Quick testing historical data scraping...")

        # Navigate to the test URL
        driver.get(test_season_url)
        time.sleep(2)  # Shortened wait time for testing purposes

        # Attempt to find the table
        try:
            table = driver.find_element(By.XPATH, TABLE_XPATH)
            table_html = table.get_attribute('outerHTML')
            soup = BeautifulSoup(table_html, 'html.parser')
            rows = soup.find_all('tr')

            if not rows:
                print("No rows found in the historical data table.")
                return

            # Parse only the first few rows for quick testing
            test_rows = rows[1:3]  # Limit to two rows for speed
            for row in test_rows:
                cells = row.find_all('td')
                if len(cells) > 1:
                    print("Sample historical row data:")
                    print([cell.text.strip() for cell in cells])
                else:
                    print("Row is missing expected data.")
        except Exception as e:
            print(f"Error finding or parsing the table: {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    # test_scrape_nhl_page()
    # quick_test_scrape_historical_data()
    run()
