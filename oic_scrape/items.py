# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass
from typing import Optional
from enum import Enum
from datetime import datetime


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


@dataclass
class GrantItem:
    """
    A class to represent a grant item. Principal datatype of our final grants dataset.
    [Derived from SoOi_2024_grants_dataset](https://docs.google.com/spreadsheets/d/1PEQiOmHq1u5tKnNEvIFJTtG_6eLHbWHJv3_Epce7lcQ/edit#gid=0)

    ...

    Attributes
    ----------
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
    """

    grant_id: str
    funder_name: str = None
    funder_ror_id: Optional[str] = None
    recipient_org_name: str = None
    recipient_org_ror_id: Optional[str] = None
    OI: Optional[str] = None
    pi_name: Optional[str] = None
    pi_org_affiliation: Optional[str] = None
    grant_year: str = None
    grant_duration: Optional[str] = None
    grant_start_date: Optional[str] = None
    grant_end_date: Optional[str] = None
    award_amount: str = None
    award_currency: str = None
    award_amount_usd: Optional[str] = None
    source: str = None
    grant_description: Optional[str] = None
    program_of_funder: Optional[str] = None
    IP_SOLNCAT: Optional[str] = None
    grant_category: Optional[Ioi_Grant_Category] = None
    comments: Optional[str] = None
    _crawled_at: datetime = None