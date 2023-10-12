from bs4 import BeautifulSoup
import requests
import json


def getHTML(url):
    response = requests.get(url)
    return response.text


def data_to_JSON(url, json_file):
    html_document = getHTML(url)
    soup = BeautifulSoup(html_document, 'html.parser')
    data = {}
    m_value_elements = soup.find_all('li', class_='m-value')

    for element in m_value_elements:
        key_atr = element.find('span', class_='adPage__content__features__key')
        value_atr = element.find('span', class_='adPage__content__features__value')

        if key_atr and value_atr:
            key = key_atr.text.strip()
            value = value_atr.text.strip()
            data[key] = value
    # Specify the output JSON file name
    with open(json_file, 'w', encoding='utf-8') as json_file:
        # Write the JSON data to the file
        json.dump(data, json_file, indent=4, ensure_ascii=False)


data_to_JSON('https://999.md/ru/76747986', 'products.json')