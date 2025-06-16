import time
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


def dismiss_cookie_banner(driver):
    try:
        driver.execute_script("""
            let overlay = document.querySelector('dock-privacy-settings');
            if (overlay) {
                overlay.style.display = 'none';
            }
        """)
        time.sleep(1)
    except Exception:
        pass


def scrape_bosch_jobs():
    options = Options()
    options.headless = True
    options.binary_location = "/Applications/Firefox.app/Contents/MacOS/firefox"


    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)
    wait = WebDriverWait(driver, 10)

    url = "https://jobs.bosch.de/?filter=locations.state%3ABaden-W%C3%BCrttemberg%2CentryLevel%3AStudent*in%2CjobField%3AForschung_IN_+Voraus-+und+Technologieentwicklung%2CjobField%3AInformationstechnologie%2CjobField%3ATechnik%2FIngenieurwesen"
    driver.get(url)
    dismiss_cookie_banner(driver)

    jobs = []

    try:
        total_jobs_text = wait.until(EC.presence_of_element_located((
            By.XPATH, "/html/body/div[1]/div/section[3]/div[2]/h1/span"
        ))).text
        total_jobs = int(total_jobs_text.replace(".", "").strip())
        print(f"Total jobs available: {total_jobs}")
    except Exception as e:
        print("Could not get total jobs count:", e)
        total_jobs = 0

    loaded_jobs = 20 
    while loaded_jobs < total_jobs:
        try:
            load_more_button = wait.until(EC.element_to_be_clickable((
                By.XPATH, "/html/body/div[1]/div/section[3]/div[2]/div[2]/button"
            )))
            load_more_button.click()
            print("Clicked 'Weitere Ergebnisse laden' button, waiting for jobs to load...")
            time.sleep(2)  

            btn_text = load_more_button.text
            match = re.search(r"\((\d+) von (\d+)\)", btn_text)
            if match:
                loaded_jobs = int(match.group(1))
                print(f"Loaded jobs updated: {loaded_jobs} / {total_jobs}")
            else:
                print("Could not parse loaded jobs count from button text. Exiting load loop.")
                break
        except Exception:
            print("No more 'Load More' button or error, stopping load.")
            break

    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.group.flex.flex-col")))
        time.sleep(2)  
        job_cards = driver.find_elements(By.CSS_SELECTOR, "a.group.flex.flex-col")

        print(f"Found {len(job_cards)} job cards.\n")

        for card in job_cards:
            try:
                title = card.find_element(By.CSS_SELECTOR, "p.font-bold.text-primary.text-xl.md\\:text-2xl").text.strip()
            except:
                title = "N/A"

            try:
                location = card.find_element(By.CSS_SELECTOR, "div.gap-1.font-bold.md\\:flex.md\\:font-normal.lg\\:block").get_attribute("textContent").replace("Standort:", "").strip()
            except:
                location = "N/A"

            try:
                link = card.get_attribute("href")
            except:
                link = "N/A"

            jobs.append({
                "title": title,
                "location": location,
                "link": link,
                "company": "Bosch"
            })
    except Exception as e:
        print("Error scraping job cards:", e)

    df = pd.DataFrame(jobs)
    os.makedirs("data", exist_ok=True)
    df.to_csv("data/jobs_bosch.csv", index=False)
    print(f"Scraped {len(df)} BOSCH jobs and saved to data/jobs_sap.csv")

    return df


if __name__ == "__main__":
    scrape_bosch_jobs()

