import pandas as pd
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.service import Service as FirefoxService
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.firefox import GeckoDriverManager
from bs4 import BeautifulSoup

firstname = 'Faisal'
lastname = 'Malik'
joblink = []
maxcount = 50
keywords = ['aws devops', 'devops', 'cloud', 'aws']
location = ['india', 'remote', 'delhi', 'ncr']
applied = 0
failed = 0
applied_list = []

profile_path = "/Users/faisalmalik/Library/Application Support/Firefox/Profiles/cnjnyp58.naukri"

options = Options()
options.profile = profile_path

try:
    driver = webdriver.Firefox(service=FirefoxService(GeckoDriverManager().install()), options=options)
except Exception as e:
    print('Webdriver exception:', e)
    exit()

time.sleep(10)
for k in keywords:
    for loc in location:
        for i in range(1, 3):  # Loop through 2 pages per keyword and location
            url = f"https://www.naukri.com/{k.lower().replace(' ', '-')}-jobs-in-{loc.lower().replace(' ', '-')}-{i}"
            
            driver.get(url)
            print(f"Scraping URL: {url}")
            time.sleep(3)

            page_source = driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')

            # Find job link containers
            job_elems = soup.find_all('div', class_='sjw__tuple')
            
            for job_elem in job_elems:
                link_elem = job_elem.find('a', class_='title')
                if link_elem:
                    joblink.append(link_elem.get('href'))

# Apply for jobs
for job_url in joblink:
    if applied >= maxcount:
        print('Max job apply limit reached.')
        break
    
    driver.get(job_url)
    time.sleep(3)
    
    try:
        # Wait for the apply button to be clickable
        wait = WebDriverWait(driver, 10)
        apply_button = wait.until(EC.element_to_be_clickable((By.XPATH, '//*[@id="apply-button"]')))
        apply_button.click()
        time.sleep(2)
        
        if driver.current_url != job_url:
            applied += 1
            applied_list.append({'status': 'passed', 'url': job_url})
            print(f"Applied for job: {job_url}")
        else:
            failed += 1
            applied_list.append({'status': 'failed', 'url': job_url})
            print(f"Failed to apply for job: {job_url}")
    
    except Exception as e:
        failed += 1
        applied_list.append({'status': 'failed', 'url': job_url})
        print(f"Exception occurred while applying for job: {job_url}")
        print(e)

# Close the browser
print('Completed applying, closing browser, saving in applied jobs csv')
driver.quit()

# Save applied jobs to CSV
csv_file = "naukri_applied_jobs.csv"
df = pd.DataFrame(applied_list)
df.to_csv(csv_file, index=False)
print(f"Saved applied jobs to {csv_file}")
