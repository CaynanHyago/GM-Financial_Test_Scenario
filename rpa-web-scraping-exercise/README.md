# RPA Web Scraping Exercise

Welcome! This is a short programming exercise for candidates to a **junior RPA
development** position.

You will complete a single function that scrapes book data from
[`https://books.toscrape.com/`](https://books.toscrape.com/). The site is a
deliberately stable demo website built for web scraping exercises. Everything
you need to know is written below:

- [Setup](#setup): how to install and run the project.
- [The task](#the-task): what to implement.
- [Specification](#specification): the exact behaviour your implementation must
  have.
- [Self-verification](#self-verification): how to check your work.
- [Submitting your solution](#submitting-your-solution): how to submit your
  solution.

## Setup

Requirements:

- Python **3.13** or newer.
- [`uv`](https://docs.astral.sh/uv/)

Clone this repository and install the project and its dependencies using `uv`:

```bash
uv sync
```

Install the Chromium browser used by Playwright:

```bash
uv run playwright install chromium
```

You can now run the provided command-line tool:

```bash
uv run scrape-books --category Travel --max-books 5
```

## The task

Open
[`src/rpa_web_scraping_exercise/scrape_books.py`](src/rpa_web_scraping_exercise/scrape_books.py)
and complete the `scrape_books` function. It currently raises
`NotImplementedError`.

The function receives a Playwright `page: Page` object (already created and
navigable), a `category: str | None`, and `max_books: int`. It must return a
`list[BookData]` where each `BookData` describes one book:

```python
class BookData(TypedDict):
    url: str
    name: str
    rating: int
    price: Decimal
    in_stock: bool
```

## Specification

The exact behaviour your `scrape_books` implementation must have:

1. **Starting point.** Navigate to `https://books.toscrape.com/` first.

2. **Data.** For every book you scrape, collect the following fields:
   - `url`: the book's detail page URL, as an **absolute** URL.
   - `name`: the book's title.
   - `rating`: the star-rating displayed on the book (an integer from 1 to 5).
   - `price`: the displayed price as a `Decimal` (strip currency symbols such as
     `£`).
   - `in_stock`: whether the book is listed as in stock (`bool`).

3. **Category filtering.**
   - If `category` is `None`, scrape **all books**, following the pagination on
     the site from the homepage **without navigating into any category**.
   - If `category` is a string that matches one of the categories in the
     **sidebar on the initial homepage navigation** (matching is
     **case-insensitive**), scrape only the books belonging to that category.
   - If `category` does not match any sidebar category: return an **empty
     list**.

   Note: category pages are also paginated. Follow the pagination when needed.

4. **Maximum number of books.**
   - Scrape as many books as possible, but **stop as soon as `max_books` books
     have been collected**. Do not request any additional pages once the limit
     has been reached.
   - If `max_books` is **less than or equal to zero**, return an empty list
     without scraping anything.

5. **Type hints.** Aim at having high type hint coverage. Add type hints to the
   arguments and a return type to every additional function/method you create.

## Self-verification

There is no pre-built test in this repository. The `scrape-books` command-line
tool is your sanity check: run it against the live site while you develop:

```bash
# Scrape books from a category
uv run scrape-books --category Travel --max-books 5

# Scrape across all categories (no category given)
uv run scrape-books --max-books 5

# Unknown categories should produce no output
uv run scrape-books --category "Not A Real Category"
```

Your solution will ultimately be evaluated based on both its code quality and by
an automated test suite (not included here) that exercises the full
specification above. Make sure your implementation is readable, organized, and
matches the specification exactly, since passing a few manual runs on the live
site does not guarantee that it is correct.

## Submitting your solution

When you're done, push your solution to a git host of your preference (e.g.
GitHub) and send us the link.

Good luck!
