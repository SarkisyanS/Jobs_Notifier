import time
import math
import re
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
        reject_btn = wait.until(EC.element_to_be_clickable((By.ID, "onetrust-reject-all-handler")))
        reject_btn.click()
        time.sleep(1)
    except Exception:
        pass


def scrape_digits_jobs():
    options = Options()
    options.headless = True
    options.binary_location = "/Applications/Firefox.app/Contents/MacOS/firefox"


    driver = webdriver.Firefox(service=Service(GeckoDriverManager().install()), options=options)
    wait = WebDriverWait(driver, 10)

    base_url = "https://it.schwarz/jobsearch?"
    driver.get(base_url)
    dismiss_cookie_banner(driver, wait)

    # Get total number of jobs
    total_jobs_text = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR, "h2.digits-headline.digits-search__result-headline")
        )
    ).text  # e.g. "Unsere Stellenangebote (353)"

    match = re.search(r"\((\d+)\)", total_jobs_text)
    total_jobs = int(match.group(1)) if match else 0
    print(f"Total jobs found: {total_jobs}")

    page_size = 10  # Adjust if the website shows a different number of jobs per page
    total_pages = math.ceil(total_jobs / page_size)
    print(f"Total pages: {total_pages}")

    jobs = []

    for page in range(1, total_pages + 1):
        url = f"{base_url}?page={page}"
        print(f"Scraping page {page} - {url}")
        driver.get(url)
        dismiss_cookie_banner(driver, wait)
        time.sleep(2)  # Wait for jobs to load

        wait.until(EC.presence_of_all_elements_located((By.CLASS_NAME, "digits-list-job-item")))
        job_cards = driver.find_elements(By.CLASS_NAME, "digits-list-job-item")

        for card in job_cards:
            try:
                title = card.find_element(By.TAG_NAME, "h3").text.strip()
                meta = card.find_element(By.TAG_NAME, "p").text.strip()
                link = card.get_attribute("href")
                full_link = "https://schwarz-digits.de" + link if link.startswith("/") else link

                jobs.append({
                    "title": title,
                    "meta": meta,
                    "link": full_link,
                    "company": "Schwarz Digits"
                })
            except Exception as e:
                print(f"Error scraping a job card: {e}")
                continue

        time.sleep(1)  # be polite to server

    driver.quit()
    df = pd.DataFrame(jobs)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/jobs_schwarz_digits.csv", index=False)
    print(f"✅ Scraped {len(df)} schwarz_digits jobs and saved to data/jobs_sap.csv")

    return df


if __name__ == "__main__":
    scrape_digits_jobs()
    