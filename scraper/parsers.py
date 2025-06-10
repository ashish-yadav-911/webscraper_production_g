from bs4 import BeautifulSoup
import abc

class Parser(abc.ABC):
    """Abstract Base Class for parsers. Defines the interface."""
    @abc.abstractmethod
    def parse(self, html_content: str) -> list[dict]:
        pass

class BooksToScrapeParser(Parser):
    """A concrete parser for books.toscrape.com."""
    def parse(self, html_content: str) -> list[dict]:
        soup = BeautifulSoup(html_content, 'html.parser')
        items = []
        for article in soup.find_all('article', class_='product_pod'):
            title = article.h3.a['title']
            price_str = article.find('p', class_='price_color').text
            price = float(price_str.replace('£', ''))
            
            # For simplicity, we'll use the title as description for embedding
            description = title 
            
            # The URL is relative, so we form a placeholder
            # A real implementation would join with the base URL
            url = "http://books.toscrape.com/" + article.h3.a['href']
            
            items.append({
                "title": title,
                "price": price,
                "description": description,
                "url": url
            })
        return items

# --- Add other parsers here for different websites ---
# class AmazonParser(Parser):
#     def parse(self, html_content: str) -> list[dict]:
#         # ... logic to parse an Amazon product page
#         pass


# A factory to get the correct parser based on the URL
def get_parser(url: str) -> Parser:
    if "books.toscrape.com" in url:
        return BooksToScrapeParser()
    # elif "amazon.com" in url:
    #     return AmazonParser()
    else:
        raise ValueError(f"No parser available for URL: {url}")