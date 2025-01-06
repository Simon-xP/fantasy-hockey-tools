import os
import time
from dotenv import load_dotenv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
from supabase import create_client, Client


def connect_to_supabase():
    load_dotenv(dotenv_path="../.env")
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_KEY")
    return create_client(url, key)

# returns an array of all player ids we have to visit in moneypuck
def get_player_ids(supabase: Client):
    response = supabase.table("players").select("id").execute()
    return [player['id'] for player in response.data]


def scrape_and_store_historical_data(player_url, supabase: Client):
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(player_url)
        time.sleep(5)
        
        table_xpath = '//*[@id="includedContent"]'
        table = driver.find_element(By.XPATH, table_xpath)
        rows = table.find_elements(By.TAG_NAME, "tr")

        for row in rows[1:]:
            season_th = row.find_elements(By.TAG_NAME, "th") # extract season from <th> tag
            season = season_th[0].text if season_th else ""

            cells = row.find_elements(By.TAG_NAME, "td") # extract other data from <td> tags
            data = [cell.text for cell in cells]

            # parse data
            faceoff_win_pct = data[23] if len(data) > 23 else None
            expected_goals = data[3] if len(data) > 3 else None
            shooting_pct_unblocked = data[30] if len(data) > 30 else None
            expected_shooting_pct_unblocked = data[31] if len(data) > 31 else None
            high_danger_unblocked_shot_atmpts = data[40] if len(data) > 40 else None
            med_danger_unblocked_shot_atmpts = data[41] if len(data) > 41 else None
            low_danger_unblocked_shot_atmpts = data[42] if len(data) > 42 else None
            on_ice_goals_pct = data[48] if len(data) > 48 else None
            on_ice_expected_goals_pct = data[49] if len(data) > 49 else None
            off_ice_expected_goals_pct = data[50] if len(data) > 50 else None
            shooting_talent_adjusted_exp_goals = data[67] if len(data) > 67 else None
            goals_above_shooting_talent = data[68] if len(data) > 68 else None

            # prepare data for insertion
            record = {
                "season": season,
                "faceoff_win_pct": float(faceoff_win_pct.replace("%", "")) if faceoff_win_pct else None,
                "expected_goals": float(expected_goals) if expected_goals else None,
                "shooting_pct_unblocked_shots": float(shooting_pct_unblocked.replace("%", "")) if shooting_pct_unblocked else None,
                "expected_shooting_pct_unblocked_shots": float(expected_shooting_pct_unblocked.replace("%", "")) if expected_shooting_pct_unblocked else None,
                "high_danger_unblocked_shot_atmpts": int(high_danger_unblocked_shot_atmpts) if high_danger_unblocked_shot_atmpts else None,
                "med_danger_unblocked_shot_atmpts": int(med_danger_unblocked_shot_atmpts) if med_danger_unblocked_shot_atmpts else None,
                "low_danger_unblocked_shot_atmpts": int(low_danger_unblocked_shot_atmpts) if low_danger_unblocked_shot_atmpts else None,
                "on_ice_goals_pct": float(on_ice_goals_pct.replace("%", "")) if on_ice_goals_pct else None,
                "on_ice_expected_goals_pct": float(on_ice_expected_goals_pct.replace("%", "")) if on_ice_expected_goals_pct else None,
                "off_ice_expected_goals_pct": float(off_ice_expected_goals_pct.replace("%", "")) if off_ice_expected_goals_pct else None,
                "shooting_talent_adjusted_exp_goals": float(shooting_talent_adjusted_exp_goals) if shooting_talent_adjusted_exp_goals else None,
                "goals_above_shooting_talent": float(goals_above_shooting_talent) if goals_above_shooting_talent else None,
            }

            # insert into supabase
            supabase.table("skaters_advanced_stats").insert(record).execute()
    
    finally:
        driver.quit()


def test_scrape_and_store_historical_data(player_url):
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        driver.get(player_url)
        time.sleep(5)
        
        # locate table
        table_xpath = '//*[@id="includedContent"]'
        table = driver.find_element(By.XPATH, table_xpath)
        rows = table.find_elements(By.TAG_NAME, "tr")
        
        headers = [header.text for header in rows[0].find_elements(By.TAG_NAME, "th")]

        max_rows = 12  # number of rows to test
        for i, row in enumerate(rows[1:]):
            if i >= max_rows:
                break
            
            # extract data
            season_th = row.find_elements(By.TAG_NAME, "th")
            season = season_th[0].text if season_th else ""
            cells = row.find_elements(By.TAG_NAME, "td")
            data = [cell.text for cell in cells]

            # parse data
            faceoff_win_pct = data[23] if len(data) > 23 else None
            expected_goals = data[3] if len(data) > 3 else None
            shooting_pct_unblocked = data[30] if len(data) > 30 else None
            expected_shooting_pct_unblocked = data[31] if len(data) > 31 else None
            high_danger_unblocked_shot_atmpts = data[40] if len(data) > 40 else None
            med_danger_unblocked_shot_atmpts = data[41] if len(data) > 41 else None
            low_danger_unblocked_shot_atmpts = data[42] if len(data) > 42 else None
            on_ice_goals_pct = data[48] if len(data) > 48 else None
            on_ice_expected_goals_pct = data[49] if len(data) > 49 else None
            off_ice_expected_goals_pct = data[50] if len(data) > 51 else None
            shooting_talent_adjusted_exp_goals = data[67] if len(data) > 67 else None
            goals_above_shooting_talent = data[68] if len(data) > 68 else None
            
            # prepare data
            record = {
                "season": season,
                "faceoff_win_pct": float(faceoff_win_pct.replace("%", "")) if faceoff_win_pct else None,
                "expected_goals": float(expected_goals) if expected_goals else None,
                "shooting_pct_unblocked_shots": float(shooting_pct_unblocked.replace("%", "")) if shooting_pct_unblocked else None,
                "expected_shooting_pct_unblocked_shots": float(expected_shooting_pct_unblocked.replace("%", "")) if expected_shooting_pct_unblocked else None,
                "high_danger_unblocked_shot_atmpts": int(high_danger_unblocked_shot_atmpts) if high_danger_unblocked_shot_atmpts else None,
                "med_danger_unblocked_shot_atmpts": int(med_danger_unblocked_shot_atmpts) if med_danger_unblocked_shot_atmpts else None,
                "low_danger_unblocked_shot_atmpts": int(low_danger_unblocked_shot_atmpts) if low_danger_unblocked_shot_atmpts else None,
                "on_ice_goals_pct": float(on_ice_goals_pct.replace("%", "")) if on_ice_goals_pct else None,
                "on_ice_expected_goals_pct": float(on_ice_expected_goals_pct.replace("%", "")) if on_ice_expected_goals_pct else None,
                "off_ice_expected_goals_pct": float(off_ice_expected_goals_pct.replace("%", "")) if off_ice_expected_goals_pct else None,
                "shooting_talent_adjusted_exp_goals": float(shooting_talent_adjusted_exp_goals) if shooting_talent_adjusted_exp_goals else None,
                "goals_above_shooting_talent": float(goals_above_shooting_talent) if goals_above_shooting_talent else None,
            }
            
            print(f"Row {i + 1} Record:", record)
    
    finally:
        driver.quit()


# Main execution
if __name__ == "__main__":

    """
    test_player_url = "https://moneypuck.com/player.htm?p=8477492"
    test_scrape_and_store_historical_data(test_player_url)
    """


    supabase_client = connect_to_supabase()
    for player_id in get_player_ids(supabase_client):
        player_stats_url = f"https://moneypuck.com/player.htm?p={player_id}"
        scrape_and_store_historical_data(player_stats_url, supabase_client)

