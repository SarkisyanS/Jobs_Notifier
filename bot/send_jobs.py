import os
import glob
import pandas as pd
import asyncio
from telegram import Bot
from telegram.error import TelegramError

TOKEN = input("YOUR API TOKEN")
CHAT_ID = "965785315"
NEW_JOBS_GLOB = "data/new_jobs_*.csv"

def load_new_jobs(filepath):
    if os.path.exists(filepath):
        return pd.read_csv(filepath)
    else:
        return pd.DataFrame()

def format_job_message(job):
    title = job.get('title', 'No title')
    company = job.get('company', 'No company')
    location = job.get('location', 'No location')
    link = job.get('link', None)

    if link:
        return f"💼 *{title}*\n🏢 {company}\n📍 {location}\n🔗 [link]({link})"
    else:
        return f"💼 *{title}*\n🏢 {company}\n📍 {location}"


async def send_jobs():
    bot = Bot(token=TOKEN)

    job_files = glob.glob(NEW_JOBS_GLOB)
    if not job_files:
        print("No new jobs files to send.")
        return

    total_sent = 0
    for filepath in job_files:
        jobs_df = load_new_jobs(filepath)
        if jobs_df.empty:
            print(f"No jobs in {filepath}")
            continue

        for _, job in jobs_df.iterrows():
            message = format_job_message(job)
            try:
                await bot.send_message(chat_id=CHAT_ID, text=message, parse_mode='Markdown')
                print(f"Sent job: {job.get('title')} from {filepath}")
                total_sent += 1
            except TelegramError as e:
                print(f"Failed to send job {job.get('title')} from {filepath}: {e}")

        os.remove(filepath)
        print(f"Cleared sent jobs file: {filepath}")

    if total_sent == 0:
        print("No new jobs sent.")
    else:
        print(f"Total jobs sent: {total_sent}")

if __name__ == "__main__":
    asyncio.run(send_jobs())
