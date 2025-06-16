import time
import urllib.parse
import pandas as pd
import os

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager


def dismiss_cookie_banner(driver, wait):
    try:
        overlay = wait.until(
            EC.presence_of_element_located((By.ID, "trustarc-banner-overlay"))
        )
        decline_button = wait.until(
            EC.element_to_be_clickable((By.ID, "truste-consent-required"))
        )
        if "ablehnen" in decline_button.text.lower():
            decline_button.click()
            wait.until_not(EC.presence_of_element_located((By.ID, "trustarc-banner-overlay")))
            time.sleep(1)
    except Exception:
        pass


def scrape_sap_jobs():
    options = Options()
    options.headless = True

    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    wait = WebDriverWait(driver, 5)

    base_url = "https://jobs.sap.com/search/"
    base_params = {
        "q": "",
        "sortColumn": "referencedate",
        "sortDirection": "desc",
        "optionsFacetsDD_customfield3": "Student",
        "optionsFacetsDD_country": "DE",
        "scrollToTable": "true"
    }

    jobs = []
    page_size = 25
    params = base_params.copy()
    params["startrow"] = 0
    url = base_url + "?" + urllib.parse.urlencode(params)

    driver.get(url)
    dismiss_cookie_banner(driver, wait)

    try:
        last_page_button = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "a.paginationItemLast"))
        )
        last_page_url = last_page_button.get_attribute("href")
        last_startrow = int(urllib.parse.parse_qs(urllib.parse.urlparse(last_page_url).query)["startrow"][0])
        total_pages = last_startrow // page_size + 1
    except Exception:
        total_pages = 1

    for page in range(total_pages):
        startrow = page * page_size
        params["startrow"] = startrow
        url = base_url + "?" + urllib.parse.urlencode(params)
        driver.get(url)
        time.sleep(1)

        try:
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.data-row")))
            rows = driver.find_elements(By.CSS_SELECTOR, "tr.data-row")
            for row in rows:
                try:
                    title = row.find_element(By.CSS_SELECTOR, "td.colTitle a.jobTitle-link").text.strip()
                    location = row.find_element(By.CSS_SELECTOR, "td.colLocation span.jobLocation").text.strip()
                    link = row.find_element(By.CSS_SELECTOR, "td.colTitle a.jobTitle-link").get_attribute("href")
                    jobs.append({
                        "title": title,
                        "location": location,
                        "link": link,
                        "company": "SAP"
                    })
                except Exception:
                    continue
        except Exception:
            continue

        time.sleep(1)

    driver.quit()

    df = pd.DataFrame(jobs)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/jobs_sap.csv", index=False)
    print(f"Scraped {len(df)} SAP jobs and saved to data/jobs_sap.csv")

    return df


if __name__ == "__main__":
    scrape_sap_jobs()
