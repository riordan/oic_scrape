"""
Andrew W. Mellon Foundation
Scrapes from Graphql API rather than website. May be more subject to errors
But it's a very hip site without any server-side rendering so lets just read the api for the site

Assumptions:
- End Date = Date of Award (start date) + Length (e.g. 35 months)
- No PI is listed in their database
"""

import scrapy
import json
from oic_scrape.items import GrantItem
import dateparser
from dateutil.relativedelta import relativedelta
from datetime import datetime

FUNDER_NAME = "Andrew W. Mellon Foundation"
FUNDER_ROR = "https://ror.org/04jsh2530"


class MellonSpider(scrapy.Spider):
    name = 'mellon.org_grants'
    allowed_domains = ['www.mellon.org']
    start_urls = ['https://www.mellon.org/api/graphql']
    graphql_url = 'https://www.mellon.org/api/graphql'
    offset = 0
    limit = 5000

    def start_requests(self):
        # Query to their GraphQL API to get grant IDs (with pagination)
        # Note: subsequent pagination requests are triggered from the parse function
        payload = {
            "operationName": "GrantFilterQuery",
            "variables": {
                "limit": self.limit,
                "offset": self.offset,
                "term": "",
                "sort": "NEWEST",
                "years": [],
                "grantMakingAreas": [],
                "ideas": [],
                "pastProgram": False,
                "amountRanges": [],
                "country": [],
                "state": [],
                "features": []
            },
            "query": """query GrantFilterQuery($term: String!, $limit: Int!, $offset: Int!, $sort: SearchSort, $amountRanges: [FilterRangeInput!], $grantMakingAreas: [String!], $country: [String!], $pastProgram: Boolean, $yearRange: FilterRangeInput, $years: [Int!], $state: [String!], $ideas: [String!], $features: [String!]) {
  grantSearch(
    term: $term
    limit: $limit
    offset: $offset
    sort: $sort
    filter: {pastProgram: $pastProgram, grantMakingAreas: $grantMakingAreas, country: $country, years: $years, yearRange: $yearRange, amountRanges: $amountRanges, state: $state, ideas: $ideas, features: $features}
  ) {
    ...GrantSearchResults
    __typename
  }
}

fragment GrantSearchResults on GrantSearchResultWithTotal {
  entities {
    data {
      title
      id
      country
      state
      __typename
    }
  }
  totalCount
}
"""
        }

        # Send a POST request to the GraphQL API to get IDs
        yield scrapy.Request(
            self.graphql_url,
            method="POST",
            headers={
                'Content-Type': 'application/json',
                'x-api-key': 'undefined'  # Adjust if you have a proper API key
            },
            body=json.dumps(payload),
            callback=self.parse
        )

    def parse(self, response):
        # Parse the JSON response from grantSearch
        data = json.loads(response.text)
        for grant in data['data']['grantSearch']['entities']:
            # For each grant, request its full details
            grant_id = grant['data']['id']

            # Call the GraphQL API for each individual grant
            yield scrapy.Request(
                self.graphql_url,
                method="POST",
                headers={
                    'Content-Type': 'application/json',
                },
                body=json.dumps({
                    "query": """query GrantDetails($grantId: String!) {
                                  grantDetails(grantId: $grantId) {
                                    grant {
                                      amount
                                      areaOfFocus
                                      date
                                      description
                                      durationInMonths
                                      granteeId
                                      granteeName
                                      id
                                      location
                                      programArea
                                      title
                                    }
                                  }
                                }""",
                    "variables": {"grantId": grant_id},
                }),
                callback=self.parse_grant_details
            )

        # Paginate the original base GraphQL Query
                # Update offset and check for more data to fetch
        self.offset += self.limit
        total_count = data['data']['grantSearch']['totalCount']
        if self.offset < total_count:
            # Generate next request with updated offset
            yield from self.start_requests()

    def parse_grant_details(self, response):
      # Attempt to parse the JSON response
      try:
          details = json.loads(response.text)['data']['grantDetails']['grant']
      except (json.JSONDecodeError, KeyError) as e:
          self.logger.error(f"Error parsing JSON response: {e}")
          return

      # Parse the grant start date
      try:
          grant_start_date = dateparser.parse(details['date'])
          # Ensure grant_start_date is not None
          if grant_start_date is None:
              raise ValueError("Failed to parse grant start date.")
      except (ValueError, TypeError) as e:
          self.logger.error(f"Error parsing grant start date: {e}")
          grant_start_date = None
      
      # Calculate the grant end date
      grant_end_date = None
      if grant_start_date:
          try:
              duration_in_months = int(details['durationInMonths'])
              grant_end_date = grant_start_date + relativedelta(months=duration_in_months)
          except (ValueError, TypeError) as e:
              self.logger.error(f"Error calculating grant end date: {e}")

      # Now, prepare the item
      yield GrantItem(
          grant_id=f"mellon:grants::{details['id']}",
          funder_name=FUNDER_NAME,
          funder_ror_id=FUNDER_ROR,
          recipient_org_name=details['granteeName'],
          recipient_location=details['location'],
          # pi_name=None,  # No PI is listed in their database.
          grant_year=grant_start_date.strftime('%Y') if grant_start_date else None,
          grant_duration=f"{details['durationInMonths']} months",
          grant_start_date=grant_start_date.strftime('%Y-%m-%d') if grant_start_date else None,
          grant_end_date=grant_end_date.strftime('%Y-%m-%d') if grant_end_date else None,
          award_amount=str(details['amount']),
          award_currency="USD",  # Adjust if currency information is available
          award_amount_usd=str(details['amount']),
          source="mellon.org",
          source_url=response.url,
          grant_description=details['description'],
          program_of_funder=details['programArea'],
          _crawled_at=datetime.utcnow(),  # Set to current timestamp
          raw_source_data=details,  # Store the raw source data for debugging
      )
