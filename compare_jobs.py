import os
import pandas as pd

def normalize(text):
    return str(text).strip().lower()

def compare_and_save_new_jobs(company_name):
    """
    Compare newly scraped jobs for a company with all previously saved jobs,
    using the job link as unique ID, save new jobs and update global file.

    Parameters:
    - company_name: str, like 'sap' or 'bosch'

    Returns:
    - DataFrame of new unique jobs
    """
    global_jobs_filepath='data/jobs.csv'
    company_jobs_filepath='data/jobs_' + company_name + '.csv'
    new_jobs_filepath='data/new_jobs_' + company_name + '.csv'

    os.makedirs(os.path.dirname(global_jobs_filepath), exist_ok=True)

    if not os.path.exists(company_jobs_filepath):
        raise FileNotFoundError(f"No job file found for company: {company_jobs_filepath}")

    new_jobs_df = pd.read_csv(company_jobs_filepath)

    if os.path.exists(global_jobs_filepath):
        old_jobs_df = pd.read_csv(global_jobs_filepath)
    else:
        old_jobs_df = pd.DataFrame(columns=new_jobs_df.columns)

    # Normalize links and create unique_key from link
    if 'unique_key' not in new_jobs_df.columns:
        new_jobs_df['unique_key'] = new_jobs_df['link'].apply(normalize)
    else:
        new_jobs_df['unique_key'] = new_jobs_df['unique_key'].apply(normalize)

    if 'unique_key' not in old_jobs_df.columns:
        if not old_jobs_df.empty and 'link' in old_jobs_df.columns:
            old_jobs_df['unique_key'] = old_jobs_df['link'].apply(normalize)
        else:
            old_jobs_df['unique_key'] = []

    # Drop duplicates within new jobs based on unique_key (link)
    new_jobs_df = new_jobs_df.drop_duplicates(subset='unique_key')

    # Filter out jobs already present in old jobs by unique_key
    new_jobs_df_unique = new_jobs_df[~new_jobs_df['unique_key'].isin(old_jobs_df['unique_key'])]

    if not new_jobs_df_unique.empty:
        new_jobs_df_unique.to_csv(new_jobs_filepath, index=False)
        updated_jobs = pd.concat([old_jobs_df, new_jobs_df_unique], ignore_index=True)
        updated_jobs.to_csv(global_jobs_filepath, index=False)
        print(f"✅ Saved {len(new_jobs_df_unique)} new {company_name} jobs to {new_jobs_filepath}")
    else:
        print(f"ℹ️ No new jobs found for {company_name}.")
        if os.path.exists(new_jobs_filepath):
            os.remove(new_jobs_filepath)

    return new_jobs_df_unique


if __name__ == "__main__":
    for company in ["sap", "bosch", "schwarz_jobs"]:
        compare_and_save_new_jobs(company)