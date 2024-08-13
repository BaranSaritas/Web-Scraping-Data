import requests
from bs4 import BeautifulSoup

#cok satanlar
url = "https://www.trendyol.com/cok-satanlar?type=bestSeller&webGenderId=1"
res = requests.get(url)
soup = BeautifulSoup(res.text, 'html.parser')
product_list = []


p = soup.find_all('div', class_='product-listing-container')

for widget_div in p:
    product_cards = widget_div.find_all('div', class_='product-card')
    for product_card in product_cards:
        # Bilgileri saklayacağımız Collection
        product_info = {}

        link = product_card.find('a', href=True)
        if link:
            product_info['href'] = link['href']

        product_description = link.find('p', class_='product-description') if link else None
        if product_description:
            brand = product_description.find('span', class_='product-brand')
            name = product_description.find('span', class_='product-name')
            if brand and name:
                product_info['brand'] = brand.get_text(strip=True)
                product_info['name'] = name.get_text(strip=True)

        rating_score = link.find('span', class_='rating-score') if link else None
        if rating_score:
            product_info['rating_score'] = rating_score.get_text(strip=True)

        rating_count = link.find('span', class_='ratingCount') if link else None
        if rating_count:
            product_info['rating_count'] = rating_count.get_text(strip=True).strip('()')

        price_discounted = link.find('div', class_='prc-box-dscntd') if link else None
        if price_discounted:
            product_info['price_discounted'] = price_discounted.get_text(strip=True)

        product_list.append(product_info)

for product in product_list:
    print(product)
    print('\n')