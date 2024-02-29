# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from enum import Enum
from scrapy import Item, Field
import attrs
from attrs import define, validators
from typing import Optional, List, Dict
from datetime import datetime, date


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
    grant_title : Optional[str]
        The title of the grant
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
    raw_source_data = Optional[Dict[str, Any]]
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
    grant_title = Field()
    grant_description = Field()
    program_of_funder = Field()
    IP_SOLNCAT = Field()
    grant_category = Field()
    comments = Field()
    _crawled_at = Field()
    raw_source_data = Field()


@define
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

    full_name: str = attrs.field(validator=validators.instance_of(str))
    is_pi: bool = attrs.field(default=False, validator=validators.instance_of(bool)) # type: ignore

    affiliations: Optional[List[str]] = attrs.field(
        default=None,
        validator=attrs.validators.optional(
            attrs.validators.deep_iterable(
                member_validator=attrs.validators.instance_of(str),
                iterable_validator=attrs.validators.instance_of(list),
            )
        ),
    )
    grant_role: Optional[str] = attrs.field(
        default=None, validator=validators.optional(validators.instance_of(str))
    )
    first_name: Optional[str] = attrs.field(
        default=None, validator=validators.optional(validators.instance_of(str))
    )
    middle_name: Optional[str] = attrs.field(
        default=None, validator=validators.optional(validators.instance_of(str))
    )
    last_name: Optional[str] = attrs.field(
        default=None, validator=validators.optional(validators.instance_of(str))
    )
    suffix: Optional[str] = attrs.field(
        default=None, validator=validators.optional(validators.instance_of(str))
    )
    identifiers: Optional[Dict[str, str]] = attrs.field(
        default=None,
        validator=attrs.validators.optional(attrs.validators.instance_of(dict)),
    )


@define
class AwardItem:
    """A class to represent a grant/award item.

    Represents the IOI formatted data for their grants dataset. Successor to the GrantItem class.
    Will be serialized into JSONND/jsonlines format for storage.
    [Derived from SoOi_2024_grants_dataset](https://docs.google.com/spreadsheets/d/1PEQiOmHq1u5tKnNEvIFJTtG_6eLHbWHJv3_Epce7lcQ/edit#gid=0)

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
    raw_source_data: Optional[Dict[str, Any]]
        The raw fields obtained from the source, including that not used in the principal schema, in case we need to reference it later.
        Where including a source object blob (e.g. JSON or transformed XML), use the source's naming conventions.
        If you are scraping it from a site, use our own field names and conventions, where it makes sense.
    _award_schema_version: Optional[str]
        The version of the award schema. Communicates to users the version of the schema. Defaults to latest version provided in the package.
        It is best practice to EXPLICITLY set this to communicate to downstream users the expectations they should hold for the data.
    """

    # Mandatory Fields
    _crawled_at: datetime = attrs.field(
        validator=validators.instance_of(datetime), alias="_crawled_at"
    )
    source: str = attrs.field(validator=validators.instance_of(str))
    grant_id: str = attrs.field(validator=validators.instance_of(str))
    funder_org_name: str = attrs.field(validator=validators.instance_of(str))
    recipient_org_name: str = attrs.field(validator=validators.instance_of(str))

    # Optional Fields
    funder_org_ror_id: Optional[str] = attrs.field(
        default=None, validator=validators.optional(validators.instance_of(str))
    )
    recipient_org_ror_id: Optional[str] = attrs.field(
        default=None, validator=validators.optional(validators.instance_of(str))
    )
    recipient_org_location: Optional[str] = attrs.field(
        default=None, validator=validators.optional(validators.instance_of(str))
    )
    pi_name: str = attrs.field(
        default=None, validator=validators.optional(validators.instance_of(str))
    )
    named_participants: Optional[List[AwardParticipant]] = attrs.field(
        default=None,
        validator=attrs.validators.optional(
            attrs.validators.deep_iterable(
                member_validator=attrs.validators.instance_of(AwardParticipant),
                iterable_validator=attrs.validators.instance_of(list),
            )
        ),
    )
    grant_year: Optional[int] = attrs.field(
        default=None, validator=validators.optional(validators.instance_of(int))
    )
    grant_duration: Optional[str] = attrs.field(
        default=None, validator=validators.optional(validators.instance_of(str))
    )
    grant_start_date: Optional[date] = attrs.field(
        default=None, validator=validators.optional(validators.instance_of(date))
    )
    grant_end_date: Optional[date] = (
        attrs.field(
            default=None,
            validator=validators.and_(
                [
                    validators.optional(validators.instance_of(date)),
                    validators.ge(grant_start_date),
                ] # type: ignore
            ),
        ),
    )
    award_amount: Optional[float] = attrs.field(
        default=None, validator=validators.optional(validators.instance_of(float))
    )
    award_currency: Optional[str] = attrs.field(
        default=None, validator=validators.optional(validators.instance_of(str))
    )
    award_amount_usd: Optional[float] = attrs.field(
        default=None, validator=validators.optional(validators.instance_of(float))
    )
    source_url: Optional[str] = attrs.field(
        default=None, validator=validators.optional(validators.instance_of(str))
    )
    grant_title: Optional[str] = attrs.field(
        default=None, validator=validators.optional(validators.instance_of(str))
    )
    grant_description: Optional[str] = attrs.field(
        default=None, validator=validators.optional(validators.instance_of(str))
    )
    program_of_funder: Optional[str] = attrs.field(
        default=None, validator=validators.optional(validators.instance_of(str))
    )
    comments: Optional[str] = attrs.field(
        default=None, validator=validators.optional(validators.instance_of(str))
    )
    raw_source_data: Optional[str] = attrs.field(
        default=None,
        validator=validators.optional(validators.instance_of(str)),
    )
    _award_schema_version: str = attrs.field(
        default="0.1.0",
        validator=validators.instance_of(str), # type: ignore
        alias="_award_schema_version",
    )
