from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
import json
import time

# Load companies from JSON file
with open('companies.json', 'r') as file:
    companies = json.load(file)['companies']

def fetch_job_listings(url):
    # Set up Selenium WebDriver with Chromium
    chrome_options = Options()
    chrome_options.binary_location = r'C:\Users\sange\Downloads\chrome-win64\chrome.exe'  # Path to Chromium executable
    chrome_options.add_argument("--headless")  # Run in headless mode (no GUI)
    
    # Update path to your ChromeDriver executable
    service = Service(r'C:\path\to\chromedriver\chromedriver.exe')  # Path to your ChromeDriver executable
    driver = webdriver.Chrome(service=service, options=chrome_options)

    try:
        driver.get(url)  # Open the URL

        # Wait for the page to load completely
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.TAG_NAME, "body"))
        )
        
        # DEBUG: Print the page source for inspection
        page_source = driver.page_source
        print(f"Fetched HTML content from {url}:\n", page_source[:1000])  # Print the first 1000 characters for inspection

        # Use BeautifulSoup to parse the page source
        soup = BeautifulSoup(page_source, 'html.parser')

        # Find job listings in the parsed HTML
        # Adjust the selector based on the actual HTML structure of the job listings page
        jobs = soup.find_all('div', class_='job-card')  # Example class name, adjust as needed

        if not jobs:
            print(f"No jobs found in the HTML content from {url}")
            return []

        job_listings = []
        for job in jobs:
            title = job.find('h2').text if job.find('h2') else 'No Title'
            description = job.find('p').text if job.find('p') else 'No Description'
            date_posted_str = job.find('span', class_='job-date').text if job.find('span', class_='job-date') else 'No Date'

            try:
                date_posted = datetime.strptime(date_posted_str, '%Y-%m-%d').date()
            except ValueError:
                date_posted = datetime.today().date()  # Fallback to today's date if date parsing fails

            job_listings.append({
                'title': title,
                'description': description,
                'date_posted': date_posted
            })

        return job_listings

    finally:
        driver.quit()  # Close the browser

def filter_new_job_listings(job_listings, days=30):
    cutoff_date = datetime.today().date() - timedelta(days=days)
    return [job for job in job_listings if job['date_posted'] >= cutoff_date]

def main():
    for company in companies:
        print(f"Fetching jobs for {company['name']}...")
        job_listings = fetch_job_listings(company['url'])
        new_job_listings = filter_new_job_listings(job_listings)
        if new_job_listings:
            print(f"Company: {company['name']}")
            for job in new_job_listings:
                print(f"Title: {job['title']}")
                print(f"Description: {job['description']}")
                print(f"Date Posted: {job['date_posted']}")
                print("-" * 40)
        else:
            print(f"No new job listings found for {company['name']}.")
        print()

if __name__ == "__main__":
    main()
