import os
import pandas as pd
from telegram import Bot
from telegram.error import TelegramError
import asyncio

DATA_DIR = "data"
GLOBAL_JOBS_PATH = os.path.join(DATA_DIR, "jobs.csv")
CHAT_ID = "965785315"
TOKEN = input("TELEGRAM_API_TOKEN: ")  

def normalize(text):
    return str(text).strip().lower()

def escape_markdown(text):
    """
    Escapes Telegram Markdown special characters.
    """
    if not isinstance(text, str):
        text = str(text)
    for ch in r"_*[]()~`>#+-=|{}.!":
        text = text.replace(ch, f"\\{ch}")
    return text

def format_job_message(job):
    title = escape_markdown(job.get('title', 'No title'))
    company = escape_markdown(job.get('company', 'No company'))
    location = escape_markdown(job.get('location', 'No location'))
    link = job.get('link', None)

    if link:
        return f"💼 *{title}*\n🏢 {company}\n📍 {location}\n🔗 [link]({link})"
    else:
        return f"💼 *{title}*\n🏢 {company}\n📍 {location}"


def load_company_jobs(company_name):
    path = os.path.join(DATA_DIR, f"jobs_{company_name}.csv")
    if os.path.exists(path):
        df = pd.read_csv(path)
        df['unique_key'] = df['link'].apply(normalize)
        return df
    else:
        print(f"⚠ No scraped jobs found for {company_name}")
        return pd.DataFrame()

def load_global_jobs():
    if os.path.exists(GLOBAL_JOBS_PATH):
        df = pd.read_csv(GLOBAL_JOBS_PATH)
        if 'unique_key' not in df.columns and 'link' in df.columns:
            df['unique_key'] = df['link'].apply(normalize)
        return df
    else:
        return pd.DataFrame(columns=["title", "location", "link", "company", "unique_key"])

async def send_jobs(jobs_df):
    if jobs_df.empty:
        print("ℹ No new jobs to send.")
        return

    bot = Bot(token=TOKEN)
    total_sent = 0

    for _, job in jobs_df.iterrows():
        message = format_job_message(job)
        try:
            await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
            print(f"✅ Sent: {job.get('title')} at {job.get('company')}")
            total_sent += 1
        except TelegramError as e:
            print(f"❌ Failed to send job: {e}")

    print(f"📤 Total jobs sent: {total_sent}")

def compare_and_send(company_list):
    global_jobs_df = load_global_jobs()
    new_all_jobs = []

    for company in company_list:
        company_df = load_company_jobs(company)
        if company_df.empty:
            continue

        company_df = company_df.drop_duplicates(subset='unique_key')
        new_jobs = company_df[~company_df['unique_key'].isin(global_jobs_df['unique_key'])]

        if not new_jobs.empty:
            new_all_jobs.append(new_jobs)
            global_jobs_df = pd.concat([global_jobs_df, new_jobs], ignore_index=True)

    # Save updated global file
    if new_all_jobs:
        updated = pd.concat(new_all_jobs, ignore_index=True)
        asyncio.run(send_jobs(updated))
        global_jobs_df.to_csv(GLOBAL_JOBS_PATH, index=False)
    else:
        print("🔁 All jobs already sent before. Nothing new.")

if __name__ == "__main__":
    compare_and_send(["sap", "sap_de", "bosch", "schwarz_digits", "mercedes"])
