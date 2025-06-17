import asyncio
from scrapers.sap_scraper import scrape_sap_jobs
from scrapers.sap_de_scraper import scrape_sap_de_jobs
from scrapers.bosch_scraper import scrape_bosch_jobs
from scrapers.schwarz_digits_scraper import scrape_digits_jobs
from scrapers.mercedes_scraper import scrape_mercedes_jobs


from compare_jobs import compare_and_save_new_jobs
from bot.send_jobs import send_jobs  

def main():
    sap_jobs = scrape_sap_jobs()
    sap_de_jobs = scrape_sap_de_jobs()
    bosch_jobs = scrape_bosch_jobs()
    schwarz_jobs = scrape_digits_jobs()
    mercedes_jobs = scrape_mercedes_jobs()



    for company in ["sap", "sap_de", "bosch", "schwarz_digits", "mercedes"]:
        compare_and_save_new_jobs(company)

    asyncio.run(send_jobs())

if __name__ == "__main__":
    main()

