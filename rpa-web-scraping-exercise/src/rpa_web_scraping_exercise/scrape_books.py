import re
from decimal import Decimal, InvalidOperation
from typing import TypedDict
from urllib.parse import urljoin

from playwright.sync_api import Locator, Page

URL: str = "https://books.toscrape.com/"
RATING_VALUES: dict[str, int] = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}
PRICE_PATTERN = re.compile(r"(?<![0-9.])[0-9]+(?:\.[0-9]{1,2})?(?![0-9.])")

class BookData(TypedDict):
    url: str
    name: str
    rating: int
    price: Decimal
    in_stock: bool

class BookScraper:
    
    def __init__(self, page: Page, base_url: str = URL) -> None:
        self._page = page
        self._base_url = base_url

    def scrape(self, *, category: str | None, max_books: int) -> list[BookData]:
        self._page.goto(self._base_url)
        if max_books <= 0:
            return []

        if category is not None:
            category_url = self._find_category_url(category)
            if category_url is None:
                return []
            self._page.goto(category_url)

        books: list[BookData] = []
        while True:
            for card in self._page.locator("article.product_pod").all():
                books.append(self._parse_book_card(card, self._page.url))
                if len(books) >= max_books:
                    return books

            next_page_url = self._get_next_page_url()
            if next_page_url is None:
                return books
            self._page.goto(next_page_url)

    def _find_category_url(self, category: str) -> str | None:
        wanted_category = category.strip().casefold()
        if not wanted_category:
            return None

        category_links = self._page.locator(
            ".side_categories ul li ul li a"
        ).all()
        for link in category_links:
            link_name = link.inner_text().strip().casefold()
            if link_name == wanted_category:
                href = link.get_attribute("href")
                if href:
                    return urljoin(self._base_url, href)
                return None
        return None

    def _get_next_page_url(self) -> str | None:

        next_link = self._page.locator("li.next a")
        if next_link.count() == 0:
            return None

        href = next_link.get_attribute("href")
        if not href:
            return None
        return urljoin(self._page.url, href)

    @staticmethod
    def _parse_book_card(card: Locator, page_url: str) -> BookData:

        title_link = card.locator("h3 a")
        name = title_link.get_attribute("title") or title_link.inner_text().strip()
        href = title_link.get_attribute("href")
        if not href:
            raise ValueError(f"Book {name!r} has no detail-page URL")
        book_url = urljoin(page_url, href)

        rating_classes = card.locator(".star-rating").get_attribute("class") or ""
        rating = next(
            (
                value
                for word, value in RATING_VALUES.items()
                if word in rating_classes.split()
            ),
            None,
        )
        if rating is None:
            raise ValueError(f"Unrecognized book rating: {rating_classes!r}")

        price_text = card.locator(".price_color").inner_text().strip()
        price = BookScraper._parse_price(price_text)
        availability = card.locator(".availability").inner_text().strip()

        return {
            "url": book_url,
            "name": name,
            "rating": rating,
            "price": price,
            "in_stock": "in stock" in availability.casefold(),
        }

    @staticmethod
    def _parse_price(price_text: str) -> Decimal:

        matches = PRICE_PATTERN.findall(price_text)
        if len(matches) != 1:
            raise ValueError(f"Unrecognized book price: {price_text!r}")
        try:
            return Decimal(matches[0])
        except InvalidOperation as exc:
            raise ValueError(f"Unrecognized book price: {price_text!r}") from exc


def scrape_books(page: Page, *, category: str | None, max_books: int) -> list[BookData]:

    return BookScraper(page).scrape(category=category, max_books=max_books)
