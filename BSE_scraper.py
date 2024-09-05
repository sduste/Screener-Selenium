import csv
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Retrieve credentials from environment variables
username = os.getenv('SCREENER_USERNAME')
password = os.getenv('SCREENER_PASSWORD')

if not username or not password:
    raise ValueError("Please ensure SCREENER_USERNAME and SCREENER_PASSWORD are set in the .env file.")

# Function to read company names and alternative names from CSV
def read_company_names(csv_file):
    company_names = []
    try:
        with open(csv_file, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file)
            for row in reader:
                company_name = row.get('company_name')
                alternative_name = row.get('alternative_name')
                if company_name:
                    company_names.append((company_name, alternative_name))
                else:
                    print(f"Skipping row due to missing 'company_name': {row}")
        return company_names
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return []

# Initialize the WebDriver
browser = webdriver.Chrome()
browser.get('https://www.screener.in/')

# Login to Screener.in
login_button = browser.find_element(By.CLASS_NAME, 'account')
login_button.click()

# Fill in the login form
email_input = browser.find_element(By.NAME, 'username')
email_input.send_keys(username)
password_input = browser.find_element(By.NAME, 'password')
password_input.send_keys(password)
password_input.send_keys(Keys.RETURN)

# Wait for login to complete
time.sleep(5)

# Read company names and alternative names from CSV
company_names = read_company_names('companies.csv')

for company, alternative in company_names:
    urls_to_try = [
        f'https://www.screener.in/company/{company}/consolidated/',
        f'https://www.screener.in/company/{company}/',
        f'https://www.screener.in/company/{alternative}/consolidated/' if alternative else None,
        f'https://www.screener.in/company/{alternative}/' if alternative else None
    ]

    success = False
    for url in urls_to_try:
        if url is None:
            continue
        
        # Load the URL
        browser.get(url)
        time.sleep(8)  # Adding a delay to ensure the page loads

        # Try to find and click the "Export to Excel" button
        try:
            export_button = browser.find_element(By.CLASS_NAME, 'hide-on-mobile')
            export_button.click()
            print(f"Downloaded Excel file for {company} (or {alternative})")
            
            # Wait a few seconds to ensure the download starts
            time.sleep(5)
            success = True
            break
        except Exception as e:
            print(f"Failed to download for {company} (or {alternative}) at {url}: {e}")

    if not success:
        print(f"Could not download data for {company} or its alternative name.")

# Close the browser once done
browser.quit()
