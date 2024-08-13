from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager

class Product:
    def __init__(self, brand, name, category, favorited_count, rating_score, rating_count, price):
        self.brand = brand
        self.name = name
        self.category = category
        self.favorited_count = favorited_count
        self.rating_score = rating_score
        self.rating_count = rating_count
        self.price = price  # Yeni fiyat alanı

    def __repr__(self):
        return (f"Product(brand={self.brand}, name={self.name}, category={self.category}, "
                f"favorited_count={self.favorited_count}, rating_score={self.rating_score}, "
                f"rating_count={self.rating_count}, price={self.price})")

def get_element_text(element, by, value, default=""):
    try:
        return element.find_element(by, value).text
    except:
        return default

def safe_split(text, index=0, delimiter=' '):
    parts = text.split(delimiter)
    return parts[index] if index < len(parts) else ""

chrome_options = Options()
chrome_options.add_argument("--headless")  # Tarayıcıyı arka planda çalıştırır

driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)

products = []

pageCount = 10
try:
    for pageIndex in range(1, pageCount + 1):
        url = f"https://www.trendyol.com/kadin-palto-x-g1-c1130?pi={pageIndex}"
        driver.get(url)

        try:
            product_elements = WebDriverWait(driver, 10).until(
                EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div.product-down'))
            )
        except Exception as e:
            print(f"Error while waiting for elements on page {pageIndex}: {e}")
            continue

        for element in product_elements:
            brand = get_element_text(element, By.CSS_SELECTOR, 'span.prdct-desc-cntnr-ttl')
            name = get_element_text(element, By.CSS_SELECTOR, 'span.prdct-desc-cntnr-name')
            category = get_element_text(element, By.CSS_SELECTOR, 'div.product-desc-sub-text')

            favorited_text = get_element_text(element, By.CSS_SELECTOR, 'span.social-proof-text span.focused-text')
            favorited_count = safe_split(favorited_text, 0)

            rating_score = get_element_text(element, By.CSS_SELECTOR, 'span.rating-score')
            rating_count = get_element_text(element, By.CSS_SELECTOR, 'span.ratingCount').strip('()')

            price = get_element_text(element, By.CSS_SELECTOR, 'div.prc-box-dscntd')

            product = Product(brand, name, category, favorited_count, rating_score, rating_count, price)
            products.append(product)

finally:
    driver.quit()

for product in products:
    print(product)
