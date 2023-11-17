import requests
from bs4 import BeautifulSoup


def extract_product_details(url):
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.find("h1", itemprop="name")
        if title:
            title = title.text.strip()

        author = soup.find("a", class_="adPage__aside__stats__owner__login")
        if author:
            author = author.text.strip()

        try:
            contacts = soup.findAll('dt', string="Contacte: ")
            if contacts:
                for contact in contacts:
                    contacts = contact.find_next('dd').find_next('ul').find_next('li').find('a').get('href')

                contacts = contacts[contacts.find("+"):]
        except:
            contacts = None

        price = soup.find("span", class_="adPage__content__price-feature__prices__price__value")
        if price:
            price = price.text.strip()

        price_currency = soup.find("span", class_="adPage__content__price-feature__prices__price__currency")
        if price_currency:
            price_currency = price_currency.text.strip()

        description = soup.find("div", class_="adPage__content__description grid_18", itemprop="description")
        if description:
            description = description.text.strip()

        features = soup.find_all("li", class_="m-value", itemprop="additionalProperty")
        if features:
            features = [feature.text.strip() for feature in features]

            for i in range(len(features)):
                features[i] = features[i].replace("     ", " = ")
                features[i] = features[i].replace("    ", " = ")
                features[i] = features[i].replace("   ", "")
        else:
            features = None

        region = soup.find("span", class_="adPage__aside__address-feature__text")

        if region:
            region = region.text.strip()

        additional_info = soup.find_all("li", class_="m-no_value", itemprop="additionalProperty")
        if additional_info:
            additional_info = [info.text.strip() for info in additional_info]
        else:
            additional_info = None

    return {
        "url": url,
        "title": title,
        "author": author,
        "contacts": contacts,
        "price": price,
        "price_currency": price_currency,
        "description": description,
        "features": features,
        "region": region,
        "additional_info": additional_info
    }
