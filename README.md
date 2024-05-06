State of Open Infrastructure Funding: Scraping Pipeline
===============================================

This is Invest in Open Infrastructure's core data scrapers for the annual State of Open Infrastructure report. It is intended to provide the data on funding, projects, and tools in the open infrastructure space.

The 2024 report, when released at the end of May, will be available [online](https://investinopen.org/state-of-open-infrastructure-2024) and as a [PDF for download](https://doi.org/10.5281/zenodo.10934089).

## Contact

If you have questions or feedback, please get in touch with "Invest in Open Infrastructure <info@investinopen.org>".

## Pipeline Overview

This project is a Python-based ETL pipeline that obtains publically available data from scientific funding organizations, then normalizes their data to a [common schema](oic_scrape/items.py) for analysis. There are two types of pipelines:
1. [Website scrapers](oic_scrape/spiders) that obtain the data from web pages (such as grant catalogs / portals)
2. [Notebook-based scripts](notebook_pipelines) that process data from APIs or file downloads, such as bulk exports of grants

Both types of pipelines share the same [common schema](oic_scrape/items.py) for the data they output, an [attrs](https://www.attrs.org/en/stable/)-style data class that is used to validate the data and ensure that it is consistent across all funders.

The data for each funder is output as [JSON Lines](https://jsonlines.org/) files in the `[data](data)` directory as `<funderid>_<grant_type>.jsonl`. When funder data exceeds 100mb, it is split into multiple files like `sshrc-ca.split00.jsonl`.

Additional details on the structure of the data and code used to produce it can be found in [CONTRIBUTING.md](CONTRIBUTING.md), along with instructions on running the code to update the data yourself.
