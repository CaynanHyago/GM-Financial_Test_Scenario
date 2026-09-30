# GM-Financial_Test_Scenario

This repository contains a Python RPA and web scraping exercise. The program
visits the demo website [Books to Scrape](https://books.toscrape.com/) and
collects each book's title, URL, rating, price, and availability. You can limit
the number of results and filter them by category.

## How to run

You need [Python 3.13 or newer](https://www.python.org/) and
[`uv`](https://docs.astral.sh/uv/) installed. In a terminal, go to the project
folder and install the dependencies:

```bash
cd rpa-web-scraping-exercise
uv sync
uv run playwright install chromium
```

Run one of these examples to check the program:

```bash
# Up to 5 books in the Travel category
uv run scrape-books --category Travel --max-books 5

# Up to 5 books, without filtering by category
uv run scrape-books --max-books 5

# A category that does not exist should return no books
uv run scrape-books --category "Category that does not exist"
```

Chromium will open while the program runs. Results are displayed in the
terminal. For details about the exercise and its requirements, see the
[project README](rpa-web-scraping-exercise/README.md).
