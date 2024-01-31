# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from dataclasses import dataclass
from typing import Optional


@dataclass
class GrantItem:
    """
    A class to represent a grant item. Principal datatype of our final grants dataset.
    [Derived from SoOi_2024_grants_dataset](https://docs.google.com/spreadsheets/d/1PEQiOmHq1u5tKnNEvIFJTtG_6eLHbWHJv3_Epce7lcQ/edit#gid=0)

    ...

    Attributes
    ----------
    funder_name : str
        The name of the funder
    funder_ror_id : Optional[str]
        The ROR ID of the funder
    recipient_org_name : str
        The name of the recipient organization
    recipient_org_ror_id : Optional[str]
        The ROR ID of the recipient organization
    OI : str
        The OI of the recipient
    pi_name : Optional[str]
        The name of the principal investigator
    pi_org_affiliation : Optional[str]
        The affiliation of the principal investigator
    grant_start_date : str
        The start date of the grant
    grant_end_date : Optional[str]
        The end date of the grant
    award_amount : str
        The amount of the award
    award_currency : str
        The currency of the award
    award_currency_usd : Optional[str]
        The amount of the award in USD
    source : str
        The source of the information
    grant_description : Optional[str]
        The description or abstract of the grant
    IP_SOLNCAT : Optional[str]
        The Infra Finder solution category of TARGET
    grant_category : Optional[str]
        The activity category of the grant
    comments : Optional[str]
        Any additional comments
    """
    funder_name: str
    funder_ror_id: Optional[str]
    recipient_org_name: str
    recipient_org_ror_id: Optional[str]
    OI: str
    pi_name: Optional[str]
    pi_org_affiliation: Optional[str]
    grant_start_date: str
    grant_end_date: Optional[str]
    award_amount: str
    award_currency: str
    award_currency_usd: Optional[str]
    source: str
    grant_description: Optional[str]
    IP_SOLNCAT: Optional[str]
    grant_category: Optional[str]
    comments: Optional[str]