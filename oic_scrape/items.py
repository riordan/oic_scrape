# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from enum import Enum
from scrapy import Item, Field


class Ioi_Grant_Category(Enum):
    """
    IOI's Grants Classification scheme from:
    https://docs.google.com/spreadsheets/d/1PEQiOmHq1u5tKnNEvIFJTtG_6eLHbWHJv3_Epce7lcQ/edit#gid=933566905

    ...

    Members
    -------
    Adjacent : str
        Award is not directly to the OI but supports activities adjacent to it in some way.
    Adoption_community : str
        Award supports adoption broadly in the community.
    Adoption_local : str
        Award supports adoption in a single institution.
    Community : str
        Award supports community building initiatives.
    Events_travel : str
        Award supports events and/or travel.
    Operations : str
        Award supports basic operations.
    Research_and_development : str
        Award supports R&D, including software development.
    Strategy_governance_business_planning : str
        Award supports strategic, governance, or business planning.
    Other : str
        Other
    """

    Adjacent = "Adjacent"
    Adoption_community = "Adoption - community"
    Adoption_local = "Adoption - local"
    Community = "Community"
    Events_travel = "Events/travel"
    Operations = "Operations"
    Research_and_development = "Research and development"
    Strategy_governance_business_planning = "Strategy/governance/business planning"
    Other = "Other"

class GrantItem(Item):
    """
    A class to represent a grant item. Principal datatype of our final grants dataset.
    [Derived from SoOi_2024_grants_dataset](https://docs.google.com/spreadsheets/d/1PEQiOmHq1u5tKnNEvIFJTtG_6eLHbWHJv3_Epce7lcQ/edit#gid=0)

    ...

    Attributes
    ----------
    Each attribute is a Field() object. The description of each field is as follows (types are not):

    grant_id : str
        The unique identifier of the grant.
            If no public ID is available it will be prefixed with "ioi:<source_name>::"
            and a unique combination of grant attributes.
    funder_name : str
        The name of the funder
    funder_ror_id : Optional[str]
        The ROR ID of the funder
    recipient_org_name : str
        The name of the recipient organization
    recipient_org_ror_id : Optional[str]
        The ROR ID of the recipient organization
    recipient_location: Optional[str]
        Funder's designated location of the grantee / project. JSON if structured data available, plain text string if only option.
    OI : Optional[str]
        The OI of the recipient
    pi_name : Optional[str]
        The name of the principal investigator
    pi_org_affiliation : Optional[str]
        The affiliation of the principal investigator
    grant_year : str
        The year of the grant. Fiscal year should be normalized to actual calendar year of issuance, as these can vary across funders.
    grant_duration : Optional[str]
        The length of time the grant is active (if known), in years or months
    grant_start_date : Optional[str]
        The starting date of the grant (if known)
    grant_end_date : Optional[str]
        The end date of the grant (if known)
    award_amount : str
        The amount of the award
    award_currency : str
        The currency of the award
    award_amount_usd : Optional[str]
        The amount of the award in USD
    source : str
        The source of the information
    source_url: Optional[str]
        The URL the data was crawled from
    grant_description : Optional[str]
        The description or abstract of the grant
    program_of_funder : Optional[str]
        The funder's program or category of the grant (organization-specific).
        If hierarchical, use a ">" to separate levels (e.g. "Research>Science>Physics")
    IP_SOLNCAT : Optional[str]
        The Infra Finder solution category of TARGET
    grant_category : Optional[Ioi_Grant_Category]
        The activity category of the grant
    comments : Optional[str]
        Any additional comments
    _crawled_at : datetime.datetime
        The date and time the grant was crawled by the IOI extractor. Must be added by the crawler.
    source_data = Optional[Dict[str, Any]]
        The raw fields obtained from the source, including that not used in the principal schema, in case we need to reference it later.
        Where including a source object blob (e.g. JSON or transformed XML), use the source's naming conventions.
        If you are scraping it from a site, use our own field names and conventions, where it makes sense.
    """

    grant_id = Field()
    funder_name = Field()
    funder_ror_id = Field()
    recipient_org_name = Field()
    recipient_org_ror_id = Field()
    recipient_location = Field()
    OI = Field()
    pi_name = Field()
    pi_org_affiliation = Field()
    grant_year = Field()
    grant_duration = Field()
    grant_start_date = Field()
    grant_end_date = Field()
    award_amount = Field()
    award_currency = Field()
    award_amount_usd = Field()
    source = Field()
    source_url = Field()
    grant_description = Field()
    program_of_funder = Field()
    IP_SOLNCAT = Field()
    grant_category = Field()
    comments = Field()
    _crawled_at = Field()
    source_data = Field()
