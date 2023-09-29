from bs4 import BeautifulSoup
import requests
import re

products_links = []


def getHTML(url):
    response = requests.get(url)
    return response.text


def web_scraping(url, max_num_pag):
    html_document = getHTML(url)
    soup = BeautifulSoup(html_document, 'html.parser')
    current_page = soup.find('li', class_='current')
    page_number = current_page.a.text
    if int(page_number) > max_num_pag:
        return "max_num_page is reached"
    else:
        for link in soup.find_all('a', attrs={'href': re.compile("/ro/"), 'class': re.compile("js-item-ad")}):
            products_links.append("https://999.md" + link.get('href'))
        next_page = current_page.find_next('li').find('a') if current_page else None
        if next_page:
            next_page_link = "https://999.md" + next_page['href']
        else:
            print("No next page link found.")
    print('Current page: ' + page_number)
    print(products_links)
    return web_scraping(next_page_link, max_num_pag)

web_scraping('https://999.md/ru/list/transport/cars', 3)