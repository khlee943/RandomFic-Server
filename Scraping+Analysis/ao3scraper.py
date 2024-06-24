from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, StaleElementReferenceException, \
    ElementNotInteractableException, WebDriverException, UnexpectedAlertPresentException, NoSuchWindowException, \
    InvalidSessionIdException
import time
import random
import pandas as pd

# define website we want to parse & path of the chrome driver
website = 'https://archiveofourown.org/media'
path = r'C:\Users\aquak\chromedriver-win64\chromedriver.exe'
service = Service(path)
driver = webdriver.Chrome(service=service)
driver.get(website)


# DOING SCRAPING

# -> CLICKING ON A BUTTON
# XPath Syntax : //tagName[@AttributeName="Value"]
# Example here:
# <a href = "/media/Anime%20*a*%20Manga/fandoms">All Anime & Manga...</a>
# //a[@href="/media/Anime%20*a%20Manga/fandoms"]
# Never mind get full Xpath: /html/body/div[1]/div[1]/div/ul/li[1]/p/a
# or this: //a[contains(text(), "All Anime & Manga")]
# anime_and_manga_button = driver.find_element(By.XPATH, '//a[contains(text(), "All Anime & Manga")]')


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


def get_language_english(driver):
    # Get button / drop-down for languages
    try:
        language_button = WebDriverWait(driver, 100).until(
            EC.element_to_be_clickable((By.XPATH, '//select[@id="work_search_language_id"]'))
        )
        # Use Select class to select for English
        select = Select(language_button)
        select.select_by_value("en")  # Select English

        #Get button / drop-down for search method
        search_type_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.XPATH, '//select[@id="work_search_sort_column"]'))
        )
        #Use Select class to select for Hits
        select = Select(search_type_button)
        select.select_by_value("kudos_count")  # Select Kudos

        # Get submit button and click
        submit_button = driver.find_element(By.XPATH,
                                            '//input[@type="submit" and @name="commit" and @value="Sort and Filter"]')
        submit_button.click()
    except TimeoutException:
        print("out of time")
        pass


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


def filter_fandoms(driver):
    # get all fandoms (as elements) in their li form
    fandom_elements = driver.find_elements(By.XPATH, '//li[a[@class="tag"]]')
    # Initialize an empty list to store filtered links
    filtered_links = []
    for li in fandom_elements:
        # Extract the text content of the `li` element
        text_content = li.text.strip()
        # Check if text_content ends with ')'
        if text_content.endswith(')'):
            # Find the last opening parenthesis '('
            start = text_content.rfind('(') + 1
            # Extract the number within the parentheses
            number_text = text_content[start:-1]  # This excludes the closing parenthesis ')'
            # Check if the extracted text is a digit and convert it to an integer
            if number_text.isdigit() and int(number_text) > 5000:
                # Get the `a` element within this `li` element
                fandom = li.find_element(By.XPATH, './/a[@class="tag"]')
                # Add the link to the list
                print(f"text: {text_content}, number: {number_text}")
                filtered_links.append(fandom.get_attribute("href"))

    return filtered_links


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


def process_category(category_url, all_titles, all_authors, all_fandoms, all_urls, all_kudos, all_summaries,
                     all_contents):
    driver.get(category_url)
    user_policy_check(driver)
    wait_until_loaded(driver)
    # Get fandoms (as links) and run through their links
    fandom_links = filter_fandoms(driver)
    # TEMP: [link.get_attribute("href") for link in driver.find_elements(By.XPATH, '//a[@class="tag"]')]
    for fandom_link in fandom_links:
        print(f"fandom link: {fandom_link}")
        process_fandom(fandom_link, all_titles, all_authors, all_fandoms, all_urls, all_kudos, all_summaries,
                       all_contents)


def process_fandom(fandom_url, all_titles, all_authors, all_fandoms, all_urls, all_kudos, all_summaries, all_contents):
    print("in!")
    driver.get(fandom_url)
    driver.set_page_load_timeout(300)
    user_policy_check(driver)
    get_language_english(driver)
    wait_until_loaded(driver)
    # Get fanfics (as web elements) and run through them
    # //a[starts-with(@href, "/works/") and not(contains(@href, "#")) and not(contains(@href, "/search"))
    # and not(contains(@href, "/chapters/")) and not(contains(@href, "/bookmarks")) and not(contains(@href, "/collections"))]

    try:
        # Get Fandom name
        fandom = WebDriverWait(driver, 40).until(
            EC.presence_of_element_located((By.XPATH, '//a[@class="tag"]'))
        )
        fandom_text = fandom.text

        # Get fandoms (as links) and run through their links
        fanfic_links = [link.get_attribute("href") for link in driver.find_elements(
            By.XPATH,
            '//a[starts-with(@href, "/works/") and not(contains(@href, "#")) '
            'and not(contains(@href, "/search")) and not(contains(@href, "/chapters/")) '
            'and not(contains(@href, "/bookmarks")) '
            'and not(contains(@href, "/collections"))]'
        )]
        print(f"Found {len(fanfic_links)} fanfics")
        for fanfic_link in fanfic_links[:10]:
            process_fanfic(driver, fanfic_link, fandom_text, all_titles, all_authors, all_fandoms, all_urls, all_kudos,
                           all_summaries, all_contents)
    except Exception as e:
        print(f"Exception occurred: {e}")
        print(f"FANDOM skipped: {driver.current_url}")
        retry_count = 0
        max_retries = 10
        while retry_count < max_retries:
            driver.get(fandom_url)
            # Check if the page indicates to retry later
            if "retry later" in driver.page_source.lower():
                retry_count += 1
                print(f"Retry attempt {retry_count}/{max_retries}: Fandom skipped. Waiting before retry...")
                time.sleep(30)  # Introduce a delay before retrying
            else:
                # Page loaded successfully, break out of the loop
                break


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


# MAIN
main_page_url = driver.current_url

# Make a list to store chapter titles
all_titles = []
all_authors = []
all_fandoms = []
all_urls = []
all_kudos = []
all_summaries = []
all_contents = []

# Find the links of all the <a> elements containing the text "All" and representing fandoms
category_links = [link.get_attribute("href") for link in driver.find_elements(By.XPATH,
                                                                              '//a[contains(text(), "All Video") and contains(@href, "/fandoms")]')]
#try:
# Iterate through each category link and click on it
for category_link in category_links:
    print(f"CATEGORY: {category_link}")
    process_category(category_link, all_titles, all_authors, all_fandoms, all_urls, all_kudos, all_summaries,
                     all_contents)
driver.quit()
#except Exception as e:
# print("broad exception caused")
# print(f"BROAD Exception occurred: {e}")

# Create a dictionary with the lists
data = {
    'Title': all_titles,
    'Author': all_authors,
    'Fandom': all_fandoms,
    'Url': all_urls,
    'Kudos': all_kudos,
    'Summary': all_summaries
}

# Print lengths for debugging
for key, value in data.items():
    print(f"{key}: length = {len(value)}")

# the parenthesis is the dataframe, the curly is the dictionary
df = pd.DataFrame({
    'Title': all_titles,
    'Author': all_authors,
    'Fandom': all_fandoms,
    'Url': all_urls,
    'Kudos': all_kudos,
    'Summary': all_summaries,
    'Content': all_contents
})

df.to_csv('all_csvs/fanfic_titles_10.csv', index=False)
