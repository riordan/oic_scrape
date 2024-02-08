# Contributing

We welcome all help in contributing and maintaining this effort. This is currently a stub document and will serve as a placeholder for more detailed information in the future.

## Participation & Code of Conduct

This is a collaborative effort, benefiting from the participation of IOI community members, funders, and data users. We welcome their participation!

This project and everyone participating in it is governed by the [Invest in Open Infrastructure Code of Conduct](https://investinopen.org/code-of-conduct/) . By participating, you are expected to uphold this code. Please report unacceptable behavior to emmy at investinopen.org or to kaitlin at investinopen.org.

## How to Contribute

- Submit issues noting problems with existing data (please search for duplicates first)
- Submit issues noting problems with existing scrapers
- Submit ideas for additional data sources to include
- Submit ideas for improving existing data sources

If you are part of a funding organization and would like to improve the quality of your organization's data in the Catalog of Open Infrastructure or have issues with the way it is currently being obtained, please get directly in touch with the project's maintainers (#TODO Set up IOI email for maintainers).

## Development Environment

To contribute code to this project or to run it independently, you'll need to set up a local environment.

The project architecture is:

- Python (3.11+)
- [Poetry](https://python-poetry.org/) _project dependencies and packaging_
    - Scrapy _Crawling framework_
        - scrapy-playwright _extension for working with interactive sites_
        - Chromium _browser for crawling interactive sites_

### Prerequisites

At present that means you'll need to have Python 3.11 or greater installed. Installing an up-to-date version of Python is beyond the scope of this document (let alone multiple Python versions), but two very good options would be using [Pyenv](https://github.com/pyenv/pyenv) or [Homebrew](https://docs.brew.sh/Homebrew-and-Python) (e.g. `brew install python@3.11`).

You will also need to have [Poetry](https://poetry-python.org) installed for managing project dependencies. While I would recommend following the official instructions and [installing with pipx](https://python-poetry.org/docs/#installing-with-pipx), there are also versions that work on various package managers.

You'll know you're ready when you can run:

```bash
$ poetry --version
Poetry (version 1.7.1)
```

### Installing the project

Download the code locally.

We'll now install the project's Python dependencies into a project-specific virtualenvironment using Poetry.

```bash
$ poetry install
```

One side-effect of using Poetry is that any CLI tools installed by the Python dependencies are part of this isolated virtualenvironment. To access these, we invoke them with `poetry run <python_cli_tool>`. We make liberal use of `poetry run scrapy <...>` so it's useful to remember that the tool lives under `poetry run`.

We use [Playwright](https://playwright.dev) so that Scrapy can crawl interactive websites (e.g. no server-side rendering). We need to [install a special version of chromium](https://playwright.dev/python/docs/browsers).

```
$ poetry run playwright install chromium
```

> NOTE: The above should work on Mac OS or Ubuntu > 18.(something) without any issue. If you're using Windows, please just use Ubuntu under [WSL](https://ubuntu.com/wsl). If you're using Arch, you can probably just install [aur:python-playwright](https://aur.archlinux.org/packages/python-playwright) or [this worked for me](https://github.com/microsoft/playwright/issues/2621#issuecomment-931530175) to get the corresponding dependencies right.

## Running Crawls

You can see what scrapers are available with:

```bash
$ poetry run scrapy list
imls.gov_grants
mellon.org_grants
sloan.org_grants
```

You can trigger a crawl with: `poetry run scrapy crawl <scraper_name>`, however it will just output to your terminal.

In this current phase of the project, we are are outputting JSON to `data/<domain_crawltype>.json`.

```bash
$ poetry run scrapy crawl sloan.org_grants -O data/sloan.org_grants.json
```

## Testing

There will eventually be CI-based testing along with data quality testing. For now, the simplest form of test we can do is using Scrapy's built in [Contracts](https://docs.scrapy.org/en/latest/topics/contracts.html) to ensure that the data we're obtaining from the page is (at least) present at the time of testing.

Scrapy tests take the form of docstrings on functions of the spider. They are run with `poetry run scrapy check <spider_name>`. For example:

```bash
$ poetry run scrapy check sloan.org_grants
```
> WARNING: Scrapy's contracts are only usable on "synchronous functions", meaning if you're using an async function for a scrapy-playwright based spider, the contract approach will not work.


