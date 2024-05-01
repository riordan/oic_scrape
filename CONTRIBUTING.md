# Contributing

At some point we may invite community contributions to this work. This document serves as a placeholder for more detailed information for future, collaborative efforts.

## Participation & Code of Conduct

This project and everyone participating in it is governed by the [Invest in Open Infrastructure Code of Conduct](https://investinopen.org/code-of-conduct/) . By participating, you are expected to uphold this code. Please report unacceptable behavior to emmy at investinopen.org or to kaitlin at investinopen.org.

## Development Environment

To run this independently, you'll need to set up a local environment.

The project architecture is:

- Python (3.11+)
- [Poetry](https://python-poetry.org/) _project dependencies and packaging_
    - Scrapy _Crawling framework_
        - scrapy-playwright _extension for working with interactive sites_
        - Chromium _browser for crawling interactive sites_
    - Jupyter _for file-based pipelines_
    - [Papermill](https://papermill.readthedocs.io/en/latest/) _for running file-based pipelines_

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

In this current phase of the project, we are are outputting [jsonlines](https://jsonlines.org/) to `data/<domain_crawltype>.jsonl`.

```bash
$ poetry run scrapy crawl sloan.org_grants -O data/sloan.org_grants.jsonl
```

## Testing

There will eventually be CI-based testing along with data quality testing. For now, the simplest form of test we can do is using Scrapy's built in [Contracts](https://docs.scrapy.org/en/latest/topics/contracts.html) to ensure that the data we're obtaining from the page is (at least) present at the time of testing.

Scrapy tests take the form of docstrings on functions of the spider. They are run with `poetry run scrapy check <spider_name>`. For example:

```bash
$ poetry run scrapy check sloan.org_grants
```
> WARNING: Scrapy's contracts are only usable on "synchronous functions", meaning if you're using an async function for a scrapy-playwright based spider, the contract approach will not work.

## Running Notebook-based Pipelines

A number of sources (e.g. NEH) provide more complete data on their grantmaking via file downloads than they do via their grant search systems. We use individual Jupyter notebooks to process these files into the same format as the data obtained from the web.

These follow similar conventions to the Scrapy-based crawlers, but are run with `poetry run papermill <notebook> <output_notebook> -p <parameter> <value>`. For example:

```bash
$ poetry run papermill notebook_pipelines/neh_gov.ipynb notebook_pipelines
/notebook_runs/neh_gov-2024-02-13-1128.ipynb
Input Notebook:  notebook_pipelines/neh_gov.ipynb
Output Notebook: notebook_pipelines/notebook_runs/neh_gov-2024-02-13-1128.ipynb
Executing:   0%|                                                                        | 0/14 [00:00<?, ?cell/s]Executing notebook with kernel: python3
Executing: 100%|███████████████████████████████████████████████████████████████| 14/14 [00:14<00:00,  1.07s/cell]
```

## Misc

Things that don't yet have a clear section.

### Paramaterizing Pipelines

It is strongly preferred for pipelines to be parameterized so that they can be focused on a limited subset of data. This helps us to avoid overloading servers by allowing us to not need to re-crawl the whole source, but to instead retrieve only the new or updated data.

At present, parameters are implemented only in papermill-based pipelines, but should be extended to Scrapy-based crawlers as well.

#### Temporal Parameters

##### Date Parameters

Crawlers are most often parameterized by date. This is preferred. Parameters should be named **`START_DATE`** and **`END_DATE`**. They should be in the format **`YYYY-MM-DD`**. **`START_DATE`** should be inclusive and **`END_DATE`** should be exclusive. If **`END_DATE`** is not provided, it should default to the current date.

> **Why should `END_DATE` be exclusive?**
>
> Making the END_DATE exclusive simplifies the logic and ensures that we consistently retrieve the desired set of records without any ambiguity or missing data.
>
> When dealing with dates that include both a date and a time component, it can be challenging to determine what the "last date" should be. To avoid any confusion or potential data inconsistencies, it is often recommended to exclude the current date from the range.
> 
> In the specific scenario mentioned, setting END_DATE to the current date would ensure that when the code runs regularly, it retrieves all the records from the past 24 hours, giving us a complete set of records for each full day. By excluding the current date, we avoid the need for complex date calculations to ensure we don't miss any records from the current day.

##### Year-based Parameters
