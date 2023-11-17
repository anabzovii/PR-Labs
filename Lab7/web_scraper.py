import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from random import randint
from time import sleep


def find_last_page_number(start_url):
    try:
        response = requests.get(start_url)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, "html.parser")
        page_link = soup.find("li", class_="is-last-page") and soup.find("li", class_="is-last-page").find("a")

        if page_link:
            page_url = page_link.get("href")
            page_number = int(page_url.split("=")[-1])

            return page_number

    except requests.exceptions.RequestException as e:
        print(f"An error occurred: {e}")

    return None


def start_web_scraping(start_url, max_pages=None, visited_pages=1, previous_links=None, unchanged_count=0):
    links = []
    base_url = "https://999.md"
    limit = 2

    if max_pages is None:
        max_pages = find_last_page_number(start_url)
    elif visited_pages > max_pages:
        return links

    print("Max pages:", max_pages)

    start_url_page = f"{start_url}?page={visited_pages}"
    response = requests.get(start_url_page)

    if response.status_code == 200:

        soup = BeautifulSoup(response.text, "html.parser")
        ads = soup.find_all("a", class_="js-item-ad")

        current_links = set()

        for ad in ads:
            href = ad.get("href")
            if href and "/booster/" not in href:
                absolute_url = urljoin(base_url, href)
                if absolute_url not in links:
                    current_links.add(absolute_url)
                    links.append(absolute_url)
                    print("URL:", absolute_url)

        if current_links == previous_links:
            unchanged_count += 1
            if unchanged_count > limit:

                for i in range(limit + 1):
                    print("Page:", visited_pages - i - 1, "was empty page")

                print("Ending the scraping process")
                return links

        print("Page:", visited_pages, "")

        next_page_links = start_web_scraping(start_url, max_pages, visited_pages + 1, current_links, unchanged_count)
        links.extend(next_page_links)

    return links
