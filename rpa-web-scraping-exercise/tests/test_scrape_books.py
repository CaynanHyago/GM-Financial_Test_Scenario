from decimal import Decimal
import unittest

from rpa_web_scraping_exercise.scrape_books import URL, scrape_books


class FakeLocator:
    def __init__(
        self,
        *,
        text: str = "",
        attributes: dict[str, str] | None = None,
        children: dict[str, "FakeLocator"] | None = None,
        items: list["FakeLocator"] | None = None,
    ) -> None:
        self.text = text
        self.attributes = attributes or {}
        self.children = children or {}
        self.items = items or []

    def all(self) -> list["FakeLocator"]:
        return self.items

    def locator(self, selector: str) -> "FakeLocator":
        return self.children[selector]

    def inner_text(self) -> str:
        return self.text

    def get_attribute(self, name: str) -> str | None:
        return self.attributes.get(name)

    def count(self) -> int:
        return len(self.items)


def make_book(
    title: str,
    href: str,
    rating: str,
    price: str,
    availability: str,
) -> FakeLocator:
    title_link = FakeLocator(text=title, attributes={"href": href, "title": title})
    return FakeLocator(
        children={
            "h3 a": title_link,
            ".star-rating": FakeLocator(attributes={"class": f"star-rating {rating}"}),
            ".price_color": FakeLocator(text=price),
            ".availability": FakeLocator(text=availability),
        }
    )


class FakePage:
    def __init__(self) -> None:
        self.url = "about:blank"
        self.goto_calls: list[str] = []
        self.categories = [
            FakeLocator(
                text="Travel",
                attributes={"href": "catalogue/category/books/travel_2/index.html"},
            ),
        ]
        self.pages: dict[str, tuple[list[FakeLocator], str | None]] = {
            URL: ([make_book("Home Book", "catalogue/home-book_1/index.html", "One", "£12.34", "In stock")], None),
            "https://books.toscrape.com/catalogue/category/books/travel_2/index.html": (
                [make_book("Travel One", "../../travel-one_2/index.html", "Five", "Â£9.99", "In stock")],
                "page-2.html",
            ),
            "https://books.toscrape.com/catalogue/category/books/travel_2/page-2.html": (
                [make_book("Travel Two", "../../travel-two_3/index.html", "Three", "£5.00", "Out of stock")],
                None,
            ),
        }

    def goto(self, url: str) -> None:
        self.url = url
        self.goto_calls.append(url)

    def locator(self, selector: str) -> FakeLocator:
        if selector == ".side_categories ul li ul li a":
            return FakeLocator(items=self.categories)
        if selector == "article.product_pod":
            return FakeLocator(items=self.pages[self.url][0])
        if selector == "li.next a":
            href = self.pages[self.url][1]
            return FakeLocator(
                attributes={"href": href} if href else {},
                items=[FakeLocator(attributes={"href": href})] if href else [],
            )
        raise AssertionError(f"Unexpected selector: {selector}")


class ScrapeBooksTests(unittest.TestCase):
    def test_scrapes_homepage_and_converts_fields(self) -> None:
        page = FakePage()
        books = scrape_books(page, category=None, max_books=5)

        self.assertEqual(len(books), 1)
        self.assertEqual(
            books[0]["url"],
            "https://books.toscrape.com/catalogue/home-book_1/index.html",
        )
        self.assertEqual(books[0]["rating"], 1)
        self.assertEqual(books[0]["price"], Decimal("12.34"))
        self.assertIs(books[0]["in_stock"], True)
        self.assertEqual(page.goto_calls, [URL])

    def test_category_is_case_insensitive_and_follows_pagination(self) -> None:
        page = FakePage()
        books = scrape_books(page, category=" tRaVeL ", max_books=5)

        self.assertEqual([book["name"] for book in books], ["Travel One", "Travel Two"])
        self.assertEqual([book["rating"] for book in books], [5, 3])
        self.assertEqual(
            [book["price"] for book in books],
            [Decimal("9.99"), Decimal("5.00")],
        )
        self.assertEqual([book["in_stock"] for book in books], [True, False])
        self.assertEqual(len(page.goto_calls), 3)

    def test_unknown_category_returns_empty(self) -> None:
        page = FakePage()
        self.assertEqual(scrape_books(page, category="Unknown", max_books=5), [])
        self.assertEqual(page.goto_calls, [URL])

    def test_non_positive_limit_returns_empty(self) -> None:
        for limit in (0, -1):
            with self.subTest(limit=limit):
                page = FakePage()
                self.assertEqual(scrape_books(page, category=None, max_books=limit), [])
                self.assertEqual(page.goto_calls, [URL])

    def test_stops_without_navigating_after_limit_is_reached(self) -> None:
        page = FakePage()
        page.pages[URL] = (
            [
                make_book("First", "first.html", "Two", "£1.00", "In stock"),
                make_book("Second", "second.html", "Four", "£2.00", "In stock"),
            ],
            "page-2.html",
        )

        books = scrape_books(page, category=None, max_books=1)

        self.assertEqual([book["name"] for book in books], ["First"])
        self.assertEqual(page.goto_calls, [URL])

    def test_all_books_follow_homepage_pagination_without_opening_category(self) -> None:
        page = FakePage()
        second_page_url = "https://books.toscrape.com/catalogue/page-2.html"
        page.pages[URL] = (page.pages[URL][0], "catalogue/page-2.html")
        page.pages[second_page_url] = (
            [
                make_book(
                    "Second Page Book",
                    "second-page-book_2/index.html",
                    "Four",
                    "£2.50",
                    "In stock",
                )
            ],
            None,
        )

        books = scrape_books(page, category=None, max_books=5)

        self.assertEqual(
            [book["name"] for book in books],
            ["Home Book", "Second Page Book"],
        )
        self.assertEqual(page.goto_calls, [URL, second_page_url])

    def test_unrecognized_rating_raises_value_error(self) -> None:
        page = FakePage()
        page.pages[URL] = (
            [make_book("Bad Rating", "bad.html", "Unknown", "£1.00", "In stock")],
            None,
        )

        with self.assertRaisesRegex(ValueError, "Unrecognized book rating"):
            scrape_books(page, category=None, max_books=1)


if __name__ == "__main__":
    unittest.main()
