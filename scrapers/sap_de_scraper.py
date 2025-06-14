import time
import urllib.parse
import pandas as pd

from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
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


def apply_student_job_filters(driver, wait):
    try:
        wait.until(EC.presence_of_element_located((By.ID, "optionsFacetsDD_customfield3")))
        wait.until(EC.presence_of_element_located((By.ID, "optionsFacetsDD_country")))

        wait.until(lambda d: "Studenten" in [
            o.get_attribute("value") for o in Select(
                d.find_element(By.ID, "optionsFacetsDD_customfield3")
            ).options
        ])

        karrierelevel_select = Select(driver.find_element(By.ID, "optionsFacetsDD_customfield3"))
        karrierelevel_select.select_by_value("Studenten")
        time.sleep(1)

        country_select = Select(driver.find_element(By.ID, "optionsFacetsDD_country"))
        country_select.select_by_value("DE")
        time.sleep(1)

        # Click "Suche starten"
        search_button = driver.find_element(By.CSS_SELECTOR, "input[type='submit'][value='Suche starten']")
        search_button.click()

        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.data-row")))
    except Exception as e:
        print("Could not apply job filters:", e)


def scrape_sap_de_jobs():
    options = Options()
    options.headless = True
    options.binary_location = "/Applications/Firefox.app/Contents/MacOS/firefox"


    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    wait = WebDriverWait(driver, 5)

    jobs = []
    url = 'https://jobs.sap.com/?locale=de_DE'
    page_size = 25

    driver.get(url)
    dismiss_cookie_banner(driver, wait)
    apply_student_job_filters(driver, wait)

    # Extract filtered URL
    filtered_url = driver.current_url
    parsed = urllib.parse.urlparse(filtered_url)
    filtered_params = urllib.parse.parse_qs(parsed.query)
    filtered_params.pop("startrow", None)  # remove old startrow if present
    flattened_params = {k: v[0] for k, v in filtered_params.items()}
    base_url = f"{parsed.scheme}://{parsed.netloc}{parsed.path}"

    # Determine total pages
    try:
        wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "a.paginationItemLast")))
        last_page_button = driver.find_element(By.CSS_SELECTOR, "a.paginationItemLast")
        last_page_url = last_page_button.get_attribute("href")
        last_startrow = int(urllib.parse.parse_qs(urllib.parse.urlparse(last_page_url).query)["startrow"][0])
        total_pages = last_startrow // page_size + 1
    except Exception:
        total_pages = 1

    print(f"Total pages: {total_pages}")

    # Iterate through all pages using filtered URL and manual pagination
    for page in range(total_pages):
        startrow = page * page_size
        paginated_params = flattened_params.copy()
        paginated_params["startrow"] = startrow
        paginated_url = base_url + "?" + urllib.parse.urlencode(paginated_params)
        driver.get(paginated_url)

        try:
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "tr.data-row")))
            rows = driver.find_elements(By.CSS_SELECTOR, "tr.data-row")
            for row in rows:
                try:
                    title = row.find_element(By.CSS_SELECTOR, "td.colTitle a.jobTitle-link").text.strip()
                    location = row.find_element(By.CSS_SELECTOR, "td.colLocation span.jobLocation").text.strip()
                    link = row.find_element(By.CSS_SELECTOR, "td.colTitle a.jobTitle-link").get_attribute("href")
                    jobs.append({"title": title, "location": location, "link": link, "company": "SAP"})
                except Exception:
                    continue
        except Exception:
            continue

    driver.quit()
    return pd.DataFrame(jobs)


if __name__ == "__main__":
    df = scrape_sap_de_jobs()
    df.to_csv("data/jobs_sap_de.csv", index=False)
    print(f"Scraped {len(df)} SAP_de jobs and saved to data/jobs_sap_de.csv")