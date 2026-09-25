from argparse import ArgumentParser

from playwright.sync_api import sync_playwright

from .scrape_books import scrape_books

CURRENCY_SYMBOL = "\u00a3"


def main() -> None:
    parser = ArgumentParser(
        prog="scrape-books",
        description="Scrapes book data from https://books.toscrape.com/",
    )
    parser.add_argument(
        "--category",
        "-c",
        help="Category of books to scrape. Defaults to scraping books from all categories.",
        type=str,
        default=None,
    )
    parser.add_argument(
        "--max-books",
        "-m",
        help="Maximum number of books to scrape. Defaults to 30.",
        type=int,
        default=30,
    )
    args = parser.parse_args()

    with sync_playwright() as pw:
        browser = pw.chromium.launch(headless=False)
        ctx = browser.new_context()
        page = ctx.new_page()
        books = scrape_books(page, category=args.category, max_books=args.max_books)

    for i, book in enumerate(books, start=1):
        print(
            f"{i}. {book['name']} ({book['rating']} stars, "
            f"{CURRENCY_SYMBOL}{book['price']}, in stock: {book['in_stock']})"
        )
        print(f"   {book['url']}")
    print(f"\nScraped {len(books)} book(s).")


if __name__ == "__main__":
    main()
