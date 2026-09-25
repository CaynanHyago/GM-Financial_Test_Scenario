from decimal import Decimal
from typing import TypedDict
from urllib.parse import urljoin

from playwright.sync_api import Page

URL: str = "https://books.toscrape.com/"
RATING_VALUES: dict[str, int] = {
    "One": 1,
    "Two": 2,
    "Three": 3,
    "Four": 4,
    "Five": 5,
}


class BookData(TypedDict):
    url: str
    name: str
    rating: int
    price: Decimal
    in_stock: bool


def scrape_books(page: Page, *, category: str | None, max_books: int) -> list[BookData]:
    """Scrape book data from https://books.toscrape.com/.

    After navigating to the site homepage, scrapes book data following this
    contract:

    - `category` is `None`: scrape all books, following the pagination from
      the homepage without navigating into any category.
    - `category` matches a sidebar category (case-insensitive): scrape only
      that category's books, following its pagination.
    - `category` does not match any sidebar category (or is empty /
      whitespace-only): return an empty list.

    Stops as soon as `max_books` books have been collected and never request
    pages beyond the limit. If `max_books` is less than or equal to zero, an
    empty list is returned.

    Args:
        page: A Playwright page, already created and navigable.
        category: The category to scrape, or `None` to scrape all books.
        max_books: Maximum number of books to scrape.

    Returns:
        A list of the scraped books.
    """
    page.goto(URL)
    if max_books <= 0:
        return []

    # Resolve categories against the sidebar from the initial homepage visit.
    if category is not None:
        wanted = category.strip().casefold()
        category_url: str | None = None
        for link in page.locator(".side_categories ul li ul li a").all():
            if link.inner_text().strip().casefold() == wanted:
                category_url = urljoin(URL, link.get_attribute("href") or "")
                break
        if category_url is None:
            return []
        page.goto(category_url)

    books: list[BookData] = []
    while True:
        for card in page.locator("article.product_pod").all():
            title_link = card.locator("h3 a")
            name = title_link.get_attribute("title") or title_link.inner_text().strip()
            book_url = urljoin(page.url, title_link.get_attribute("href") or "")

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
            normalized_price = "".join(
                character
                for character in price_text
                if character.isdigit() or character == "."
            )
            price = Decimal(normalized_price)
            availability = card.locator(".availability").inner_text().strip()

            books.append(
                {
                    "url": book_url,
                    "name": name,
                    "rating": rating,
                    "price": price,
                    "in_stock": "in stock" in availability.casefold(),
                }
            )
            if len(books) >= max_books:
                return books

        next_link = page.locator("li.next a")
        if next_link.count() == 0:
            return books
        next_url = urljoin(page.url, next_link.get_attribute("href") or "")
        page.goto(next_url)
