import time
import random
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


def user_policy_check(driver):
    try:
        checkbox_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "tos_agree"))
        )
        # If the element exists, click the checkbox
        checkbox_button.click()
        time.sleep(1)
        submit_button = WebDriverWait(driver, 5).until(
            EC.element_to_be_clickable((By.ID, "accept_tos"))
        )
        submit_button.click()
        time.sleep(0.25)
    except NoSuchElementException:
        pass
    except TimeoutException:
        pass


def wait_until_loaded(driver):
    # Wait until the page is fully loaded before begin processing
    WebDriverWait(driver, 20).until(
        EC.presence_of_element_located((By.TAG_NAME, 'body'))
    )

def approve_mature_material(driver):
    try:
        caution_element = WebDriverWait(driver, 3).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'p.caution'))
        )
        # If the mature check exists, get and click the continue button
        continue_button = WebDriverWait(driver, 1).until(
            EC.element_to_be_clickable((By.LINK_TEXT, 'Yes, Continue'))
        )
        continue_button.click()
    except NoSuchElementException:
        pass
    except TimeoutException:
        pass

def get_stuff(all_titles, all_authors, all_kudos, all_summaries, all_fandoms, all_contents):
    # Summary
    summary = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.XPATH, '//div[@class="summary module"]'))
    )
    summary_text = summary.text
    # Concatenate the text into one line, removing newlines
    summary_text = ' '.join(summary_text.splitlines())
    print(summary_text)

    # Title
    title = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.XPATH, '//h2[@class="title heading"]'))
    )
    title_text = title.text
    print(title_text)

    # Author
    author = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.XPATH, '//h3[@class="byline heading"]'))
    )
    author_text = author.text
    print(author_text)

    # Kudos
    kudos = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.XPATH, '//dd[@class="kudos"]'))
    )
    kudos_text = kudos.text
    print(kudos_text)

    # Fandoms
    fandom = WebDriverWait(driver, 100).until(
        EC.presence_of_element_located((By.XPATH, '//dd[@class="fandom tags"]/ul[@class="commas"]'))
    )

    fandom_links = fandom.find_elements(By.XPATH, './li/a') # Find all <a> elements within the fandom overarching element

    fandom_text = ', '.join(link.text for link in fandom_links)

    print(fandom_text)

    # Content
    get_content(all_contents)

    # append all
    all_summaries.append(summary_text)
    all_titles.append(title_text)
    all_authors.append(author_text)
    all_kudos.append(kudos_text)
    all_fandoms.append(fandom_text)


def get_content(all_contents):
    fic_content = ""
    try:
        # Wait for the content to be present and add to total
        content = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, '//ul[@class="commas"]/li/a[@class="tag"]'))
        )
        # Extract the text content from all matched elements
        elements = driver.find_elements(By.XPATH, '//ul[@class="commas"]/li/a[@class="tag"]')
        fic_content = ' '.join(element.text.strip() for element in elements)
    except Exception as e:
        retry_count = 0
        max_retries = 10
        while retry_count < max_retries:
            driver.refresh()
            # Check if the page indicates to retry later
            if "retry later" in driver.page_source.lower():
                retry_count += 1
                print(f"Retry attempt {retry_count}/{max_retries}: Fandom skipped. Waiting before retry...")
                time.sleep(30)  # Introduce a delay before retrying
            else:
                # Page loaded successfully, get content and break
                content = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, '//ul[@class="commas"]/li/a[@class="tag"]'))
                )
                # Extract the text content from all matched elements
                elements = driver.find_elements(By.XPATH, '//ul[@class="commas"]/li/a[@class="tag"]')
                fic_content = ' '.join(element.text.strip() for element in elements)
                break

    # Append the collected content to all_contents
    all_contents.append(fic_content)

def process_fanfic(driver, fanfic_url, fandom_text, all_titles, all_authors, all_fandoms, all_urls, all_kudos,
                   all_summaries, all_contents):
    driver.get(fanfic_url)
    wait_until_loaded(driver)
    # collect first chapter after clicking on fic: //div[@class="chapter"] / //h2[@class="title heading"]
    try:
        get_stuff(all_titles, all_authors, all_kudos, all_summaries, all_fandoms, all_contents)
        # Append the Fandom and Url too
        all_urls.append(fanfic_url)
        print(fandom_text)
        print(fanfic_url)
    except TimeoutException:
        print(f"fic skipped: {driver.current_url}")
        retry_count = 0
        max_retries = 20
        while retry_count < max_retries:
            driver.get(fanfic_url)
            # Check if the page indicates to retry later
            if "retry later" in driver.page_source.lower():
                retry_count += 1
                print(f"Retry attempt {retry_count}/{max_retries}: Fic skipped. Waiting before retry...")
                time.sleep(30)  # Introduce a delay before retrying
            else:
                # Page loaded successfully, break out of the loop
                break
    # Simulate processing time
    processing_time = random.uniform(2, 6)  # Random delay between 2 to 6 seconds
    time.sleep(processing_time)  # Introduce delay before next request

fanfic_urls = [
    "https://archiveofourown.org/works/663904",
    "https://archiveofourown.org/works/4486827",
    "https://archiveofourown.org/works/6870892",
    "https://archiveofourown.org/works/22935289",
    "https://archiveofourown.org/works/6841507",
    "https://archiveofourown.org/works/8472670/chapters/19413469",
    "https://archiveofourown.org/works/6115615",
    "https://archiveofourown.org/works/18077765",
    "https://archiveofourown.org/works/46741408",
    "https://archiveofourown.org/works/19020061/chapters/45169969",
    "https://archiveofourown.org/works/44361940"
]

# Initialize lists to hold the data
all_titles = []
all_authors = []
all_fandoms = []
all_urls = []
all_kudos = []
all_summaries = []
all_contents = []

# Setup WebDriver (make sure the correct WebDriver is installed, e.g., chromedriver for Chrome)
driver = webdriver.Chrome()

# Process each fanfic
for url in fanfic_urls:
    process_fanfic(driver, url, all_titles, all_authors, all_fandoms, all_urls, all_kudos, all_summaries, all_contents)

# Close the WebDriver
driver.quit()

# Save the collected data to a CSV file
df = pd.DataFrame({
    'Title': all_titles,
    'Author': all_authors,
    'Fandom': all_fandoms,
    'Url': all_urls,
    'Kudos': all_kudos,
    'Summary': all_summaries,
    'Content': all_contents
})
df.to_csv('all_csvs/extra_fanfic_titles.csv', index=False)