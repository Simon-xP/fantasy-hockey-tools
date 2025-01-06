import scrapers.nhl_skaters_info_scraper as nhl_skaters_info_scraper
import moneypuck_skaters_scraper  # Replace with other scraper modules


# runs all scrapers
def main():
    print("Starting skaters main scraper...")
    nhl_skaters_info_scraper.run()
    print("Skaters main scraper completed.")

    print("Starting skaters basic stats scraper...")
    nhl_skaters_info_scraper.run()
    print("Skaters basic stats scraper completed.")

    print("Starting skaters MoneyPuck advanced stats scraper...")
    moneypuck_skaters_scraper.run()
    print("Skaters MoneyPuck advanced stats scraper completed.")

    print("Database updated successfully.")

if __name__ == "__main__":
    main()
