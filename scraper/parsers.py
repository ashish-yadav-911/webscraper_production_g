from bs4 import BeautifulSoup
import abc
import re

class Parser(abc.ABC):
    @abc.abstractmethod
    def parse(self, html_content: str, url: str) -> list[dict]:
        pass

# --- SPECIALIZED PARSER 1 ---
class BooksToScrapeParser(Parser):
    # ... (this class remains unchanged) ...
    def parse(self, html_content: str, url_base: str) -> list[dict]:
        soup = BeautifulSoup(html_content, 'html.parser')
        items = []
        for article in soup.find_all('article', class_='product_pod'):
            title = article.h3.a['title']
            price_str = article.find('p', class_='price_color').text
            price = float(price_str.replace('£', ''))
            description = title 
            relative_url = article.h3.a['href'].replace('../../../', '')
            full_url = "http://books.toscrape.com/catalogue/" + relative_url
            image_url = "http://books.toscrape.com/" + article.find('img', class_='thumbnail')['src'].replace('../', '')

            items.append({
                "title": title, "price": price,
                "description": description, "url": full_url, "image_url": image_url
            })
        return items

# --- SPECIALIZED PARSER 2 ---
class AmazonParser(Parser):
    # ... (this class remains unchanged, but we'll add image parsing) ...
    def parse(self, html_content: str, url: str) -> list[dict]:
        soup = BeautifulSoup(html_content, 'html.parser')
        item = {}
        try: item['title'] = soup.find('span', {'id': 'productTitle'}).get_text(strip=True)
        except: item['title'] = "Title not found"
        try:
            price_whole = soup.find('span', class_='a-price-whole').get_text(strip=True).replace(',', '')
            item['price'] = float(price_whole)
        except: item['price'] = None
        try:
            description_div = soup.find('div', {'id': 'feature-bullets'})
            item['description'] = " ".join([b.get_text(strip=True) for b in description_div.find_all('span', class_='a-list-item')])
        except: item['description'] = "Description not found"
        try:
            item['image_url'] = soup.find('div', {'id': 'imgTagWrapperId'}).find('img')['src']
        except: item['image_url'] = None
        item['url'] = url
        return [item]

# --- NEW WOOCOMMERCE PARSER ---
class WooCommerceParser(Parser):
    """
    A specialized parser for WooCommerce sites. It scrapes multiple products from a category page.
    """
    def parse(self, html_content: str, url: str) -> list[dict]:
        soup = BeautifulSoup(html_content, 'html.parser')
        items = []
        # Find all product items on the page. The class name can vary slightly.
        for product in soup.select('li.product, div.product'):
            try:
                title = product.select_one('.woocommerce-loop-product__title, h2.woocommerce-loop-product__title, .product_title').get_text(strip=True)
                product_url = product.select_one('a.woocommerce-LoopProduct-link')['href']
                image_url = product.select_one('img.woocommerce-placeholder, img.wp-post-image')['src']
                
                # Price can be complex (on sale, etc.)
                price_element = product.select_one('span.price bdi')
                if price_element:
                    # Extracts numbers and decimal point only.
                    price_text = re.sub(r'[^\d.]', '', price_element.get_text())
                    price = float(price_text) if price_text else None
                else:
                    price = None

                items.append({
                    "title": title, "price": price,
                    "description": f"WooCommerce product: {title}", "url": product_url,
                    "image_url": image_url
                })
            except (AttributeError, TypeError, IndexError) as e:
                # This product might be structured differently, so we skip it.
                print(f"Skipping a product due to parsing error: {e}")
                continue
        return items

# --- NEW GENERIC PARSER ---
class GenericTextParser(Parser):
    # ... (this class remains unchanged) ...
    def parse(self, html_content: str, url: str) -> list[dict]:
        soup = BeautifulSoup(html_content, 'html.parser')
        item = {}
        try:
            if soup.find('h1'): item['title'] = soup.find('h1').get_text(strip=True)
            elif soup.find('h2'): item['title'] = soup.find('h2').get_text(strip=True)
            else: item['title'] = soup.title.get_text(strip=True)
        except: item['title'] = "No title found"
        for tag in soup(['nav', 'footer', 'header', 'aside', 'script', 'style', 'a', 'button']):
            tag.decompose()
        body_text = soup.body.get_text(separator=' ', strip=True)
        item['description'] = ' '.join(body_text.split())[:2000]
        item['price'], item['image_url'] = None, None
        item['url'] = url
        return [item]


# --- THE FINAL, UPGRADED FOREMAN ---
def get_parser(url: str, html_content: str) -> Parser:
    """
    Checks for specialized parsers first, then heuristics, and finally falls back.
    """
    if "books.toscrape.com" in url:
        print("Using specialized parser: BooksToScrapeParser")
        return BooksToScrapeParser()
    elif "amazon.in" in url:
        print("Using specialized parser: AmazonParser")
        return AmazonParser()
    # --- The smart heuristic for WooCommerce ---
    elif "woocommerce" in html_content.lower():
        print("Using specialized parser: WooCommerceParser")
        return WooCommerceParser()
    else:
        print("No specialized parser found. Using GenericTextParser as a fallback.")
        return GenericTextParser()