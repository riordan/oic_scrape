# Design Notes

This mess of a document might serve as a scratch-pad for works in progress. Once fully implemented, the core contents here should be moved into more core documentation such as [CONTRIBUTING.md](CONTRIBUTING.md).

## Crawler Schema

Purpose: We will ultimately have > 100 crawlers of different data sources. In addition to technical configuration, there are a number of non-operational details that should be tracked for each crawler, but inform us of the source's capabilities, crawler design decisions, system maturity, and other factors.

Format as either YAML or TOML (need to pick).

To incentivize use of the schema, we should have a CI-integrated script that is the ONLY way to add a new project to the crawler documentation. While there might be some deviations from the schema declaration and the crawler's functionality, it's a reasonable way to ensure that a schema file is declared 

```yaml
filename: 
    crawler:
        parameter_type:
            - NONE
            - Date
            - Calendar year
            - Fiscal Year: (Should be expressed inclusive (e.g. Oct 1 -> Sept 30))
                - MONTH-DAY -> MONTH-DAY *If there's only ever been one kind of fiscal period*
                - MONTH-DAY -> MONTH-DAY
                - START: YYYY-MM-DD
                - END: YYYY-MM-DD (EXCLUSIVE so if end of period is 2019-09-30, then the end date is 2019-10-01)
                - <WHATEVER IDENTIFIER THEY USE FOR THEIR TRANSITION PERIOD>
                - START: YYYY-MM-DD
                - END: YYYY-MM-DD
                - MONTH-DAY -> MONTH-DAY
                - START: YYYY-MM-DD
                - END: # OPTIONAL IF CONTINUING
            earliest_period: (YYYY-MM-DD or YYYY or FY-YYYY)

source:
    update_cadence: (Daily, Weekly, Monthly, Quarterly, Annually, Irregular, Unknown)
    source_type: (HTML, API, Bulk Download (json, xml, csv, parquet, db), PDF)
    data_dictionary:

## Item Schema

[Tracking Issue: #41](https://github.com/riordan/oic_scrape/issues/41)
