import asyncio
from scrapers.sap_scraper import scrape_sap_jobs
from scrapers.sap_de_scraper import scrape_sap_de_jobs
from scrapers.bosch_scraper import scrape_bosch_jobs
from scrapers.schwarz_digits_scraper import scrape_digits_jobs
from scrapers.mercedes_scraper import scrape_mercedes_jobs
from compare_and_send_jobs import compare_and_send


from compare_and_send_jobs import compare_and_send

def main():
    scrape_sap_jobs()
    scrape_sap_de_jobs()
    scrape_bosch_jobs()
    scrape_digits_jobs()
    scrape_mercedes_jobs()

    compare_and_send(["sap", "sap_de", "bosch", "schwarz_digits", "mercedes"])

if __name__ == "__main__":
    main()
