# Data

## Data Design

Data obtained by this project is transformed into a [common schema](oic_scrape/items.py) for analysis.

Data used by this project is designed to capture the funding landscape of open infrastructure projects, and does so by capturing grant/awards catalogs from a variety of funders, both public and private. As each funder's organizational data is unique, we do our best to normalize the data into a common format for analysis, while carrying forward as much as we can given the level of disclosure and nuances of each funder.

### Overview: High Level

We aim to capture information about:
- the funding organization
- the specific grant/award (e.g. a unique ID for the award, a URL for the data, and descriptions, amounts, funder programs where available)
- the recipient organization (e.g the research organization, library, university, nonprofit, fiscal sponsor, etc)
- the project or program being funded, where available
- key people involved, where available

Data either crawled by a scrapy crawler, extracted from an API, or downloaded from a bulk export, then transformed so that it fits the overall structure of the project. Many fields are optional, as not all funders provide the same level of detail, however, a user of the data should operate under the assumption that the data they are working with is the most complete reflection of what the funder made available at the time the pipeline was written. In addition to the transformed fields, the pipelines are expected to also store the original data for each record in a separate field called `raw_data` which can be audited or used to extract additional information by future analysts.

The schema itself is versioned, and so all records also capture their schema version at the time of extraction.

### Schema

The schema is defined in [oic_scrape/items.py](oic_scrape/items.py) as an [attrs](https://www.attrs.org/en/stable/)-style data class. This is used to validate the data and ensure that it is consistent across all funders. The linked file contains the most up-to-date version of the schema, but a simplified version is shown below:

```python
@define
class AwardItem:
    """A class to represent a grant/award item.

    Represents the IOI formatted data for their grants dataset. Successor to the GrantItem class.
    Will be serialized into JSONND/jsonlines format for storage.
    Attributes
    ----------
    Each attribute is a Field() object. The description of each field is as follows (types are not):

    Mandatory Fields:

    _crawled_at : datetime
        The date and time the grant was crawled by the IOI extractor. Must be added by the crawler.
    source : str
        The source of the information
    grant_id : str
        The unique identifier of the award.
            Prefixed with `source_name::` and the internal identifier of the award.
            If no public ID is available it will be prefixed with "ioi:<source_name>::"
            and a unique combination of grant attributes.
    funder_org_name : str
        The name of the funder
    recipient_org_name : str
        The name of the recipient organization

    Optional Fields:

    funder_org_ror_id : Optional[str]
        The ROR ID of the funder
    recipient_org_ror_id : Optional[str]
        The ROR ID of the recipient organization
    recipient_org_location: Optional[str]
        Funder's designated location of the grantee / project.
        Provide hierarchical administrative data (e.g. New York City, New York, United States) or a well-formed address.
    pi_name : Optional[str]
        The name of the principal investigator. If multiple PI's, use the first one listed, and include the rest in named_participants.
    named_participants: Optional[List[AwardParticipant]]
        Details, roles, and identifiers of named participants (grantees) associated with the award. Should include the PI, if known.
    grant_year : Optional[int]
        The year of the grant. Fiscal year should be normalized to actual calendar year of issuance, as these can vary across funders.
    grant_duration : Optional[str]
        The length of time the grant is active (if known), in years or months.
    grant_start_date : Optional[date]
        The starting date of the grant (if known)
    grant_end_date : Optional[date]
        The end date of the grant (if known)
    award_amount : Optional[float]
        The amount of the award
    award_currency : Optional[str]
        The currency of the award
    award_amount_usd : Optional[float]
        The amount of the award in USD
    source_url: Optional[str]
        The URL the data was crawled from
    grant_title : Optional[str]
        The title of the grant
    grant_description : Optional[str]
        The description or abstract of the grant
    program_of_funder : Optional[str]
        The funder's program or category of the grant (organization-specific).
        If hierarchical, use a ">" to separate levels (e.g. "Research>Science>Physics")
    comments : Optional[str]
        Any additional comments
    raw_source_data: Optional[str]
        The raw fields obtained from the source, including that not used in the principal schema, in case we need to reference it later.
        Where including a source object blob (e.g. JSON or transformed XML), use the source's naming conventions.
        If you are scraping it from a site, use our own field names and conventions, where it makes sense.
    _award_schema_version: Optional[str]
        The version of the award schema. Communicates to users the version of the schema. Defaults to latest version provided in the package.
        It is best practice to EXPLICITLY set this to communicate to downstream users the expectations they should hold for the data.
    """

class AwardParticipant:
    """Represents a named participant on an award, such as a Principal Investigator.

    Represents the attributes attached to a person named on an award.

    Args:
        full_name (str): The full name of the person.
        is_pi (bool): Whether the person is considered a principal investigator. Defaults to False.
        affiliations (Optional[List[str]], optional): The affiliations of the person. Defaults to None.
            List of affiliations provided for the person. Should be a list if more than one affiliation is provided.
        grant_role (Optional[str], optional): The role of the person on the grant. Defaults to None.
        first_name (Optional[str], optional): The first name of the person (if specified). Defaults to None.
        middle_name (Optional[str], optional): The middle name (or initial) of the person (if specified). Defaults to None.
        last_name (Optional[str], optional): The last name of the person (if specified). Defaults to None.
        suffix (Optional[str], optional): The suffix of the person (if specified). Defaults to None.
        identifiers (Optional[Dict[str, str]], optional): Any identifiers provided for the person. Defaults to None.
            Identifiers provided for this person on the grant such as ORCID, ISNI, email address, Github handle, etc. as well as funder-specific identifiers for the person. Should be provided as key-value pairs.
    """
```

## Data Formats

Data is currently output as jsonlines by the Scrapy-based crawlers and by notebook-based pipelines. This is intended to simplify bulk loading of the data into data warehouses or querying by analysts. It is also intended to be plain-text readable by analysts at this time.

We are considering other formats for the future, such as parquet, but will not be changing the preferred format until the schema is fully bidirectionally compatible between Parquet and Python data models.
