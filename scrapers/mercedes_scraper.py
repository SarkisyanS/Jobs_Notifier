import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, ElementClickInterceptedException, NoSuchElementException
from webdriver_manager.firefox import GeckoDriverManager


def get_total_jobs(driver):
    try:
        heading = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'wb-heading.mjp-title.wb-heading'))
        )
        text = heading.text.strip()
        total_jobs = int(text.split()[0])
        return total_jobs
    except Exception:
        print("Failed to get total jobs count")
        return None


def click_load_more_inside_shadow(driver):
    try:
        clicked = driver.execute_script("""
            const host = document.querySelector("wb-button[aria-label='Load More Jobs']");
            if (!host || !host.shadowRoot) return false;
            const btn = host.shadowRoot.querySelector("button");
            if (!btn) return false;
            btn.click();
            return true;
        """)
        return clicked
    except Exception as e:
        print(f"Could not click 'Load More' button inside shadow root: {e}")
        return False



def click_load_more_until_all_loaded(driver, total_jobs):
    while True:
        job_cards = driver.find_elements(By.CSS_SELECTOR, 'a.mjp-job-ad-card__link')
        jobs_loaded = len(job_cards)
        print(f"Jobs loaded: {jobs_loaded} / {total_jobs}")

        if jobs_loaded >= total_jobs:
            print("All jobs loaded.")
            break

        clicked = click_load_more_inside_shadow(driver)
        if not clicked:
            print("No more 'Load More' button or could not click it.")
            break

        time.sleep(3)


def parse_job_cards(driver):
    job_cards = driver.find_elements(By.CSS_SELECTOR, 'a.mjp-job-ad-card__link')
    jobs = []

    for card in job_cards:
        title = driver.execute_script(
            "return arguments[0].querySelector('.mjp-job-ad-card__title-text')?.textContent?.trim();", card
        )
        location = driver.execute_script(
            "return arguments[0].querySelector('.mjp-job-ad-card__location span')?.textContent?.trim();", card
        )
        link = card.get_attribute('href') or ''

        jobs.append({
            'title': title or '',
            'location': location or '',
            'link': f"https://jobs.mercedes-benz.com{link}" if link.startswith("/") else link,
            'company': 'Mercedes'
        })

    return jobs


def save_jobs_to_csv(jobs, filepath='data/jobs_mercedes.csv'):
    df = pd.DataFrame(jobs)
    df.to_csv(filepath, index=False, encoding='utf-8')


def scrape_mercedes_jobs():
    options = Options()
    options.headless = False  # Set to True for silent run
    service = Service(GeckoDriverManager().install())
    driver = webdriver.Firefox(service=service, options=options)

    try:
        url = "https://jobs.mercedes-benz.com/enUS?TargetGroup.Code=2&CareerLevel.Code=25"
        driver.get(url)

        WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'wb-heading.mjp-title.wb-heading'))
        )

        total_jobs = get_total_jobs(driver)
        if total_jobs is None:
            print("Cannot determine total jobs count. Proceeding with fallback.")
            total_jobs = 1000  # fallback

        click_load_more_until_all_loaded(driver, total_jobs)
        jobs = parse_job_cards(driver)

        print(f"\nTotal jobs scraped: {len(jobs)}")
        save_jobs_to_csv(jobs)
        print(f"Saved jobs to jobs_mercedes.csv")

    finally:
        driver.quit()


if __name__ == "__main__":
    scrape_mercedes_jobs()
