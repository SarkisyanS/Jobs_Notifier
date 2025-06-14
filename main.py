import asyncio
from scrapers.sap_scraper import scrape_sap_jobs
from scrapers.sap_de_scraper import scrape_sap_de_jobs
from scrapers.bosch_scraper import scrape_bosch_jobs
from compare_jobs import compare_and_save_new_jobs
from bot.send_jobs import send_jobs  # async function

def main():
    # Step 1: Scrape SAP jobs
    sap_jobs = scrape_sap_jobs()
    sap_de_jobs = scrape_sap_de_jobs()
    bosch_jobs = scrape_bosch_jobs()
    schwarz_jobs = scrape_bosch_jobs()



    # Step 2: Compare with old jobs and save new ones
    for company in ["sap", "sap_de", "bosch", "schwarz_digits"]:
        compare_and_save_new_jobs(company)

    # Step 3: Send new jobs via Telegram bot (async)
    asyncio.run(send_jobs())

if __name__ == "__main__":
    main()

